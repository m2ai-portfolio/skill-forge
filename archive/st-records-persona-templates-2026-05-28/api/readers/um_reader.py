"""Read ideas from the Ultra Magnus caught_ideas.db SQLite database.

Read-only — never writes to the database. Handles cases where pipeline
columns may not yet exist (schema added on first MCP server run).
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from api.models.responses import IdeaDetail, IdeaSummary

DEFAULT_DB_PATH = Path.home() / "incoming" / "caught_ideas.db"


class UMReader:
    """Reads idea data from Ultra Magnus SQLite database."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._has_pipeline_columns: bool | None = None

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    def _check_pipeline_columns(self, conn: sqlite3.Connection) -> bool:
        """Check if pipeline columns exist (added by UM MCP _ensure_schema)."""
        if self._has_pipeline_columns is not None:
            return self._has_pipeline_columns
        cursor = conn.execute("PRAGMA table_info(caught_ideas)")
        columns = {row["name"] for row in cursor.fetchall()}
        self._has_pipeline_columns = "stage" in columns
        return self._has_pipeline_columns

    def _parse_tags(self, raw: str | None) -> list[str]:
        if not raw:
            return []
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

    def _parse_json(self, raw: str | None) -> dict | None:
        if not raw:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

    def _parse_datetime(self, raw: str | None) -> datetime | None:
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw)
        except ValueError:
            return None

    def _extract_score(self, eval_result: dict | None) -> float | None:
        if not eval_result:
            return None
        scores = eval_result.get("scores")
        if scores and isinstance(scores, dict):
            return scores.get("overall_score")
        return None

    def _extract_recommendation(self, eval_result: dict | None) -> str | None:
        if not eval_result:
            return None
        return eval_result.get("recommendation")

    def available(self) -> bool:
        """Check if the database file exists and is readable."""
        return self.db_path.exists() and self.db_path.is_file()

    def list_ideas(
        self,
        stage: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[IdeaSummary]:
        if not self.available():
            return []
        conn = self._connect()
        try:
            has_pipeline = self._check_pipeline_columns(conn)

            if has_pipeline:
                query = "SELECT id, title, stage, status, caught_at, tags, evaluation_result FROM caught_ideas"
            else:
                query = "SELECT id, title, status, caught_at, tags FROM caught_ideas"

            conditions: list[str] = []
            params: list = []

            if stage and has_pipeline:
                conditions.append("stage = ?")
                params.append(stage)
            if status:
                conditions.append("status = ?")
                params.append(status)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY caught_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            results = []
            for row in rows:
                eval_result = self._parse_json(row["evaluation_result"]) if has_pipeline else None
                caught_at = self._parse_datetime(row["caught_at"])
                if caught_at is None:
                    caught_at = datetime.now()
                results.append(
                    IdeaSummary(
                        id=row["id"],
                        title=row["title"],
                        stage=row["stage"] if has_pipeline and row["stage"] else "captured",
                        status=row["status"] or "pending",
                        overall_score=self._extract_score(eval_result),
                        recommendation=self._extract_recommendation(eval_result),
                        caught_at=caught_at,
                        tags=self._parse_tags(row["tags"]),
                    )
                )
            return results
        finally:
            conn.close()

    def get_idea(self, idea_id: int) -> IdeaDetail | None:
        if not self.available():
            return None
        conn = self._connect()
        try:
            has_pipeline = self._check_pipeline_columns(conn)

            if has_pipeline:
                query = "SELECT * FROM caught_ideas WHERE id = ?"
            else:
                query = "SELECT id, title, raw_content, tags, source_context, caught_at, status FROM caught_ideas WHERE id = ?"

            row = conn.execute(query, (idea_id,)).fetchone()
            if row is None:
                return None

            eval_result = self._parse_json(row["evaluation_result"]) if has_pipeline else None
            caught_at = self._parse_datetime(row["caught_at"])
            if caught_at is None:
                caught_at = datetime.now()

            row_keys = row.keys()

            return IdeaDetail(
                id=row["id"],
                title=row["title"],
                stage=row["stage"] if has_pipeline and "stage" in row_keys and row["stage"] else "captured",
                status=row["status"] or "pending",
                overall_score=self._extract_score(eval_result),
                recommendation=self._extract_recommendation(eval_result),
                caught_at=caught_at,
                tags=self._parse_tags(row["tags"]),
                raw_content=row["raw_content"],
                source_context=row["source_context"] if "source_context" in row_keys else None,
                enrichment_result=self._parse_json(row["enrichment_result"]) if has_pipeline else None,
                evaluation_result=eval_result,
                scaffolding_result=self._parse_json(row["scaffolding_result"]) if has_pipeline else None,
                build_result=self._parse_json(row["build_result"]) if has_pipeline else None,
                review_decision=row["review_decision"] if has_pipeline else None,
                review_notes=row["review_notes"] if has_pipeline else None,
                github_url=row["github_url"] if has_pipeline else None,
                completed_at=self._parse_datetime(row["completed_at"]) if has_pipeline else None,
            )
        finally:
            conn.close()

    def count_by_stage(self) -> dict[str, int]:
        """Count ideas grouped by stage."""
        if not self.available():
            return {}
        conn = self._connect()
        try:
            has_pipeline = self._check_pipeline_columns(conn)
            if not has_pipeline:
                row = conn.execute("SELECT COUNT(*) as cnt FROM caught_ideas").fetchone()
                return {"captured": row["cnt"]}
            rows = conn.execute(
                "SELECT COALESCE(stage, 'captured') as stage, COUNT(*) as cnt "
                "FROM caught_ideas GROUP BY stage"
            ).fetchall()
            return {row["stage"]: row["cnt"] for row in rows}
        finally:
            conn.close()
