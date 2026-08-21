"""Fixture tests for scripts/open-intake-pr.mjs, the sanctioned intake exit (MAI-206).

The script is node; these tests drive it as a subprocess against (a) a throwaway git
repo with a staged skills/<name>/ tree, to exercise the allowlist + classification
gate that runs BEFORE any token mint or network call, and (b) a local stub of the
Paperclip API, to exercise the `--tool-issue` exit end to end without touching the
real board.

Why: PR #112 (subscription-sdk-bridge) was a TOOL force-fit into a SKILL.md because
nothing in the intake path asked "technique or tool?". These pin the answer:
a tool-classified candidate produces a Paperclip issue and no forge/<skill> branch.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "open-intake-pr.mjs"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")

SIDECAR = """name: {name}
version: "1.0.0"
status: draft
created: "2026-08-21"
classification: {classification}
source:
  type: youtube
  url: "https://example.com/v"
  author: "Someone"
  date: "2026-08-20"
taxonomy:
  domain: developer-tooling
  complexity: beginner
"""


def run(*argv: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["node", str(SCRIPT), *argv], capture_output=True, text=True,
                          env={**dict(__import__("os").environ), **(env or {})}, timeout=60)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A git repo with one commit on main; tests stage a skill dir on top."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@example.com"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "t"], check=True)
    (tmp_path / "README.md").write_text("x\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    return tmp_path


def stage_skill(repo: Path, name: str, classification: str | None) -> None:
    d = repo / "skills" / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\nbody\n")
    sidecar = SIDECAR.format(name=name, classification=classification or "")
    if classification is None:
        sidecar = sidecar.replace("classification: \n", "")
    (d / "skill-registry.yaml").write_text(sidecar)
    subprocess.run(["git", "-C", str(repo), "add", "skills"], check=True)


def branches(repo: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(repo), "branch", "--format=%(refname:short)"],
                         capture_output=True, text=True, check=True).stdout
    return out.split()


class TestClassificationGate:
    def test_a_technique_passes_the_gate(self, repo):
        stage_skill(repo, "good-skill", "technique")
        r = run("--skill", "good-skill", "--repo", str(repo), "--validate-only")
        assert r.returncode == 0, r.stderr
        assert "passes the allowlist and classification gate" in r.stdout

    @pytest.mark.parametrize("classification", ["tool", "other"])
    def test_a_non_technique_is_refused_with_no_branch(self, repo, classification):
        stage_skill(repo, "some-tool", classification)
        r = run("--skill", "some-tool", "--repo", str(repo))
        assert r.returncode == 2
        assert f'classification "{classification}" does not become a skill' in r.stderr
        assert "--tool-issue --name some-tool" in r.stderr, "the refusal must point at the tool exit"
        assert branches(repo) == ["main"], "no forge/<skill> branch may be created"

    def test_a_missing_classification_is_refused(self, repo):
        stage_skill(repo, "unclassified", None)
        r = run("--skill", "unclassified", "--repo", str(repo))
        assert r.returncode == 2
        assert "no classification field" in r.stderr
        assert branches(repo) == ["main"]

    def test_an_unknown_classification_is_refused(self, repo):
        stage_skill(repo, "weird", "gadget")
        r = run("--skill", "weird", "--repo", str(repo))
        assert r.returncode == 2
        assert 'classification "gadget" is not one of technique | tool | other' in r.stderr

    def test_allowlist_still_runs_first(self, repo):
        stage_skill(repo, "good-skill", "technique")
        (repo / "src.py").write_text("print(1)\n")
        subprocess.run(["git", "-C", str(repo), "add", "src.py"], check=True)
        r = run("--skill", "good-skill", "--repo", str(repo), "--validate-only")
        assert r.returncode == 2
        assert "outside the intake allowlist" in r.stderr


class _StubPaperclip(BaseHTTPRequestHandler):
    """Records every request; answers the three calls --tool-issue makes."""
    requests: list[tuple[str, str, dict]] = []
    existing: list[dict] = []

    def log_message(self, *_):  # silence
        pass

    def _send(self, code: int, body) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.requests.append(("GET", self.path, {}))
        if self.path.endswith("/issues"):
            return self._send(200, self.existing)
        if "/api/issues/" in self.path:
            return self._send(200, {"id": "iss-1", "identifier": "MAI-999", "status": "todo"})
        self._send(404, {})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        self.requests.append(("POST", self.path, body))
        self._send(201, {"id": "iss-1", "identifier": "MAI-999", "status": "todo"})


@pytest.fixture
def stub():
    _StubPaperclip.requests = []
    _StubPaperclip.existing = []
    srv = HTTPServer(("127.0.0.1", 0), _StubPaperclip)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{srv.server_address[1]}", _StubPaperclip
    finally:
        srv.shutdown()


@pytest.fixture
def summary(tmp_path: Path) -> Path:
    p = tmp_path / "summary.txt"
    p.write_text("An SDK bridge that wraps subscription billing APIs behind one client; "
                 "install it, point it at your provider, and it handles the webhook loop.")
    return p


class TestToolIssueExit:
    def test_files_one_paperclip_issue_and_prints_its_identifier(self, stub, summary, repo):
        url, h = stub
        r = run("--tool-issue", "--name", "subscription-sdk-bridge",
                "--source-url", "https://www.youtube.com/watch?v=abc",
                "--summary-file", str(summary), "--hooks", "billing for M2AI clients; replaces hand-rolled webhooks",
                "--repo", str(repo),
                env={"PAPERCLIP_API_URL": url, "PAPERCLIP_BOARD_TOKEN": "t", "PAPERCLIP_COMPANY_ID": "co"})
        assert r.returncode == 0, r.stderr
        assert r.stdout.startswith("created MAI-999"), r.stdout
        posts = [req for req in h.requests if req[0] == "POST"]
        assert len(posts) == 1, "exactly one issue per intent"
        body = posts[0][2]
        assert posts[0][1] == "/api/companies/co/issues"
        assert body["title"] == "Evaluate tool: subscription-sdk-bridge"
        assert body["status"] == "todo" and "assigneeAgentId" not in body, "captures land unassigned"
        assert "classification: tool" in body["description"]
        assert "https://www.youtube.com/watch?v=abc" in body["description"]
        assert "SDK bridge" in body["description"]
        assert "- billing for M2AI clients" in body["description"]
        assert "- replaces hand-rolled webhooks" in body["description"]
        assert body["idempotencyKey"] == "forge-tool-issue:subscription-sdk-bridge"
        assert branches(repo) == ["main"], "a tool exit never creates a forge/<skill> branch"

    def test_an_existing_open_issue_is_referenced_not_duplicated(self, stub, summary):
        url, h = stub
        h.existing = [{"id": "old", "identifier": "MAI-500", "title": "Evaluate tool: some-tool", "status": "todo"}]
        r = run("--tool-issue", "--name", "some-tool", "--source-url", "https://x.y/z",
                "--summary-file", str(summary),
                env={"PAPERCLIP_API_URL": url, "PAPERCLIP_BOARD_TOKEN": "t", "PAPERCLIP_COMPANY_ID": "co"})
        assert r.returncode == 0, r.stderr
        assert r.stdout.startswith("existing MAI-500")
        assert not [req for req in h.requests if req[0] == "POST"]

    def test_a_closed_issue_with_the_same_title_does_not_block_a_new_one(self, stub, summary):
        url, h = stub
        h.existing = [{"id": "old", "identifier": "MAI-500", "title": "Evaluate tool: some-tool", "status": "done"}]
        r = run("--tool-issue", "--name", "some-tool", "--source-url", "https://x.y/z",
                "--summary-file", str(summary),
                env={"PAPERCLIP_API_URL": url, "PAPERCLIP_BOARD_TOKEN": "t", "PAPERCLIP_COMPANY_ID": "co"})
        assert r.returncode == 0, r.stderr
        assert r.stdout.startswith("created MAI-999")

    def test_dry_run_makes_no_request(self, stub, summary):
        url, h = stub
        r = run("--tool-issue", "--name", "some-tool", "--source-url", "https://x.y/z",
                "--summary-file", str(summary), "--dry-run",
                env={"PAPERCLIP_API_URL": url, "PAPERCLIP_BOARD_TOKEN": "t"})
        assert r.returncode == 0, r.stderr
        assert "DRY-RUN --tool-issue" in r.stdout and "classification: tool" in r.stdout
        assert h.requests == []

    @pytest.mark.parametrize("argv, msg", [
        (["--tool-issue", "--source-url", "https://x.y/z"], "--name"),
        (["--tool-issue", "--name", "t", "--source-url", "notaurl"], "--source-url"),
        (["--tool-issue", "--name", "t", "--source-url", "https://x.y/z"], "--summary-file"),
    ])
    def test_required_arguments_are_enforced_before_any_request(self, stub, argv, msg):
        url, h = stub
        r = run(*argv, env={"PAPERCLIP_API_URL": url, "PAPERCLIP_BOARD_TOKEN": "t"})
        assert r.returncode == 2
        assert msg in r.stderr
        assert h.requests == []

    def test_a_thin_summary_is_refused(self, stub, tmp_path):
        url, h = stub
        p = tmp_path / "s.txt"
        p.write_text("too short")
        r = run("--tool-issue", "--name", "t", "--source-url", "https://x.y/z", "--summary-file", str(p),
                env={"PAPERCLIP_API_URL": url, "PAPERCLIP_BOARD_TOKEN": "t"})
        assert r.returncode == 2 and "real paragraph" in r.stderr
