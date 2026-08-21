#!/usr/bin/env node
// open-intake-pr.mjs: the ONLY sanctioned PR path for the skill-forge intake lane.
//
// STANDS ALONE: ~/bin/gh-app-token.mjs (the existing counterpart considered) only mints
// tokens; nothing else stages-validates, branches, pushes, and opens forge intake PRs.
// It lives in the repo (not ~/.claude/crons), so no G4 glue-budget impact.
//
// owner: Matthew (HIL merge gate until graduation)
// sink:  a DRAFT PR on github.com/m2ai-st-metro/skill-forge + data/forge-cycle-ledger.json
// kill:  exits non-zero on any allowlist violation (2) or duplicate branch/PR (3);
//        no retries, no loops; the nightly routine escalates on failure.
//
// Usage:
//   node scripts/open-intake-pr.mjs --skill <name> [--title "..."] [--body-file path] [--validate-only]
//   node scripts/open-intake-pr.mjs --tool-issue --name <kebab> --source-url <url> --summary-file <path>
//                                   [--title "..."] [--hooks "a; b; c"] [--project-id <uuid>] [--dry-run]
//   node scripts/open-intake-pr.mjs --graduation-check
//
// Allowed staged paths: skills/<name>/** (new files only), registry.yaml,
// data/intake/*.processed.md, data/last_check.txt. Anything else = exit 2.
// Existing forge/<name> branch or open PR = exit 3 (kills the MAI-7 duplicate race).
//
// CLASSIFICATION GATE (MAI-206). Every intake candidate is classified technique | tool | other
// BEFORE anything is drafted (rule: ~/.claude/rules/tool-skill-subagent-triage.md). Only a
// `technique` becomes a skill. The staged skills/<name>/skill-registry.yaml MUST carry
// `classification: technique`; a missing value or tool/other = exit 2, no branch, no PR.
// A `tool` (PR #112, subscription-sdk-bridge, was a tool force-fit into a SKILL.md) exits the
// intake through `--tool-issue`: a Paperclip evaluation issue (Pattern-4 discovery exit)
// carrying the source URL, a one-paragraph summary, and relevance hooks. The intake file
// records `**Classification:** tool` + `**Routing:** CARD — MAI-nnn` per idea, enforced by
// scripts/mark_intake_processed.py, so every classification is grep-able after the fact.
//
// HIL graduation: PRs open as DRAFT until data/forge-cycle-ledger.json cleanCycles >= 7.
// POST-GRADUATION FLIP: change `draft: !graduated` below to `draft: false` semantics is
// already automatic once cleanCycles >= 7; the remaining one-line decision is enabling
// auto-merge in the review routine. KNOWN CONSTRAINT: the GitHub App cannot approve its
// own PRs, so post-graduation auto-merge still needs a second reviewer identity or
// Matthew's review to satisfy branch protection (require 1 approving review).
//
// The App token is minted per run via ~/bin/gh-app-token.mjs --owner m2ai-st-metro
// --repo skill-forge, held in memory, used in an ephemeral push URL, and never logged
// or written to disk/git config.

import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';

const args = process.argv.slice(2);
const opt = (f) => (args.includes(f) ? args[args.indexOf(f) + 1] : null);
const die = (code, msg) => { console.error(msg); process.exit(code); };

// --repo exists so the gate can be exercised against a fixture repo (tests/test_open_intake_pr.py);
// production runs never pass it and resolve to the checkout this script lives in.
const REPO = opt('--repo') ? resolve(opt('--repo')) : resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OWNER = 'm2ai-st-metro';
const NAME = 'skill-forge';
const LEDGER = resolve(REPO, 'data/forge-cycle-ledger.json');
const GRADUATION_BAR = 7;

const CLASSIFICATIONS = ['technique', 'tool', 'other'];

const git = (...a) => {
  const r = spawnSync('git', ['-C', REPO, ...a], { encoding: 'utf8' });
  if (r.status !== 0) die(1, `git ${a[0]} failed: ${r.stderr.trim()}`);
  return r.stdout.trim();
};

const loadLedger = () => {
  if (!existsSync(LEDGER)) return { cleanCycles: 0, lastCycle: null, history: [] };
  return JSON.parse(readFileSync(LEDGER, 'utf8'));
};

if (args.includes('--graduation-check')) {
  const l = loadLedger();
  console.log(`cleanCycles: ${l.cleanCycles}`);
  process.exit(l.cleanCycles >= GRADUATION_BAR ? 0 : 1);
}

// ---------------------------------------------------------------------------------------------
// --tool-issue: the tool-classified exit. No SKILL.md, no forge/<name> branch, no PR. Files ONE
// Paperclip evaluation issue (unassigned, per capture convention) and prints its identifier so
// the intake file can record `**Routing:** CARD — MAI-nnn`. One side effect per intent: an
// existing open issue with the same title is referenced, never duplicated.
// ---------------------------------------------------------------------------------------------
if (args.includes('--tool-issue')) {
  const name = opt('--name');
  if (!name || !/^[a-z0-9][a-z0-9-]*$/.test(name)) die(2, 'usage: --tool-issue --name <kebab-name> required');
  const sourceUrl = opt('--source-url');
  if (!sourceUrl || !/^https?:\/\//.test(sourceUrl)) die(2, 'usage: --source-url <http(s) url> required');
  const summaryFile = opt('--summary-file');
  if (!summaryFile || !existsSync(summaryFile)) die(2, 'usage: --summary-file <path> required (one-paragraph summary of the tool)');
  const summary = readFileSync(summaryFile, 'utf8').trim();
  if (summary.length < 40) die(2, 'summary must be a real paragraph (>= 40 chars)');
  const hooks = (opt('--hooks') || '').split(';').map((h) => h.trim()).filter(Boolean);

  const env = process.env;
  const API = env.PAPERCLIP_API_URL || 'http://127.0.0.1:3151';
  const TOKEN = env.PAPERCLIP_BOARD_TOKEN;
  const COMPANY = env.PAPERCLIP_COMPANY_ID || '3e5c2e63-53bf-4ace-9456-3306e5e67091';
  // Default: the `build` project, where evaluation work is routed by the daily routing pass.
  const PROJECT = opt('--project-id') || env.FORGE_TOOL_ISSUE_PROJECT_ID || '14e1a6ae-36df-4881-a14e-8a643c69c741';
  if (!TOKEN) die(1, 'PAPERCLIP_BOARD_TOKEN not in env (set -a; source ~/.env.shared; set +a)');

  const title = (opt('--title') || `Evaluate tool: ${name}`).slice(0, 200);
  const description = [
    `classification: tool`,
    `source: forge intake (tool-vs-technique gate, scripts/open-intake-pr.mjs --tool-issue)`,
    `source_url: ${sourceUrl}`,
    `candidate: ${name}`,
    ``,
    `owner: Matthew (evaluation decision)`,
    `sink: comment on this issue with adopt / trial / no-go and the reason`,
    `kill: one evaluation pass; close with the decision recorded`,
    ``,
    `## Summary`,
    summary,
    ``,
    `## Relevance hooks`,
    ...(hooks.length ? hooks.map((h) => `- ${h}`) : ['- (none recorded by the scan; add before evaluating)']),
    ``,
    `## Why this is an issue and not a skill`,
    `The forge intake classified this candidate as a TOOL (a thing to install or call), not a TECHNIQUE`,
    `(a procedure to distill into a SKILL.md). Tools do not become skills (tool-skill-subagent triage).`,
    `This is the Pattern-4 discovery exit: the intake file records \`**Routing:** CARD — <this issue>\`.`,
  ].join('\n');

  const pc = async (path, opts = {}) => {
    const r = await fetch(`${API}${path}`, {
      ...opts,
      headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', ...opts.headers },
    });
    const body = await r.json().catch(() => ({}));
    return { ok: r.ok, status: r.status, body };
  };
  const norm = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

  if (args.includes('--dry-run')) {
    console.log(`DRY-RUN --tool-issue\ntitle: ${title}\nproject: ${PROJECT}\n---\n${description}`);
    process.exit(0);
  }

  // Duplicate guard: same normalized title, not closed = reference it.
  const existing = await pc(`/api/companies/${COMPANY}/issues`);
  if (!existing.ok) die(1, `could not list issues for the duplicate guard: ${existing.status}`);
  const list = Array.isArray(existing.body) ? existing.body : (existing.body.issues || existing.body.items || []);
  const dupe = list.find((i) => norm(i.title || '') === norm(title) && !['done', 'cancelled', 'canceled'].includes(i.status));
  if (dupe) {
    console.log(`existing ${dupe.identifier} ${API.replace('127.0.0.1', '10.0.0.46')}/issues/${dupe.id}`);
    process.exit(0);
  }

  const created = await pc(`/api/companies/${COMPANY}/issues`, {
    method: 'POST',
    body: JSON.stringify({
      title, description, projectId: PROJECT, status: 'todo', priority: 'medium',
      idempotencyKey: `forge-tool-issue:${name}`,
    }),
  });
  if (!created.ok) die(1, `issue creation failed ${created.status}: ${JSON.stringify(created.body).slice(0, 500)}`);
  // Read-back: a write that cannot be read back is treated as lost (MAI-144 convention).
  const back = await pc(`/api/issues/${created.body.id}`);
  if (!back.ok || !back.body.identifier) die(1, `READ-BACK FAILED for ${created.body.id}; treat this capture as LOST`);
  console.log(`created ${back.body.identifier} ${API.replace('127.0.0.1', '10.0.0.46')}/issues/${back.body.id}`);
  process.exit(0);
}

const skill = opt('--skill');
if (!skill || !/^[a-z0-9][a-z0-9-]*$/.test(skill)) die(2, 'usage: --skill <kebab-name> required');
const branch = `forge/${skill}`;

// 1. Validate the staged change set against the allowlist.
const staged = git('diff', '--cached', '--name-status', '-z').split('\0').filter(Boolean);
const entries = [];
for (let i = 0; i < staged.length; i += 2) entries.push({ status: staged[i][0], path: staged[i + 1] });
if (entries.length === 0) die(2, 'nothing staged');

const bad = [];
const skillDirs = new Set();
for (const { status, path } of entries) {
  if (path === 'registry.yaml' || path === 'data/last_check.txt') continue;
  if (/^data\/intake\/[^/]+\.processed\.md$/.test(path)) continue;
  const m = path.match(/^skills\/([^/]+)\//);
  if (m) {
    skillDirs.add(m[1]);
    if (status !== 'A') bad.push(`${path} (skill files must be new, got status ${status})`);
    continue;
  }
  bad.push(path);
}
if (skillDirs.size > 1) die(2, `more than one skills/<dir> staged: ${[...skillDirs].join(', ')}`);
if (skillDirs.size === 1 && !skillDirs.has(skill)) die(2, `staged skill dir "${[...skillDirs][0]}" does not match --skill ${skill}`);
if (bad.length) die(2, `staged paths outside the intake allowlist:\n  ${bad.join('\n  ')}`);

// 1b. Classification gate: the staged sidecar must say `classification: technique`.
if (skillDirs.size === 1) {
  const sidecarPath = `skills/${skill}/skill-registry.yaml`;
  if (!entries.some((e) => e.path === sidecarPath)) die(2, `${sidecarPath} must be staged (carries the classification field)`);
  const sidecar = git('show', `:${sidecarPath}`);
  const m = sidecar.match(/^classification:\s*["']?([a-z]+)["']?\s*$/m);
  if (!m) die(2, `${sidecarPath} has no classification field; add \`classification: technique\` (only techniques become skills; tools exit via --tool-issue)`);
  if (!CLASSIFICATIONS.includes(m[1])) die(2, `${sidecarPath}: classification "${m[1]}" is not one of ${CLASSIFICATIONS.join(' | ')}`);
  if (m[1] !== 'technique') die(2, `${sidecarPath}: classification "${m[1]}" does not become a skill. Unstage skills/${skill}/ and run:\n  node scripts/open-intake-pr.mjs --tool-issue --name ${skill} --source-url <url> --summary-file <path> [--hooks "a; b"]`);
}
if (args.includes('--validate-only')) { console.log(`validate-only: staged set for ${skill} passes the allowlist and classification gate`); process.exit(0); }

// 2. Mint a repo-scoped App token (stdout only, never logged).
const mint = spawnSync('node', [resolve(homedir(), 'bin/gh-app-token.mjs'), '--owner', OWNER, '--repo', NAME], { encoding: 'utf8' });
if (mint.status !== 0) die(1, `token mint failed: ${mint.stderr.trim()}`);
const token = mint.stdout.trim();
if (!token) die(1, 'token mint returned empty stdout');

const api = async (path, opts = {}) => {
  const r = await fetch(`https://api.github.com${path}`, {
    ...opts,
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', ...opts.headers },
  });
  const body = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, body };
};

// 3. Duplicate guards: existing remote branch or open PR = refuse.
const br = await api(`/repos/${OWNER}/${NAME}/branches/${encodeURIComponent(branch)}`);
if (br.ok) die(3, `branch ${branch} already exists on origin; refusing (duplicate race guard)`);
const prs = await api(`/repos/${OWNER}/${NAME}/pulls?state=open&head=${OWNER}:${encodeURIComponent(branch)}`);
if (prs.ok && prs.body.length > 0) die(3, `open PR already exists for ${branch}: ${prs.body[0].html_url}`);

// 4. Branch from origin/main, commit staged paths, push with the ephemeral token URL.
git('fetch', 'origin', 'main');
const startBranch = git('rev-parse', '--abbrev-ref', 'HEAD');
git('checkout', '-b', branch, 'origin/main');
try {
  git('commit', '-m', `forge(intake): add skill ${skill}\n\nOpened by scripts/open-intake-pr.mjs (sanctioned forge intake lane).`);
  const pushUrl = `https://x-access-token:${token}@github.com/${OWNER}/${NAME}.git`;
  const push = spawnSync('git', ['-C', REPO, 'push', pushUrl, `${branch}:${branch}`], { encoding: 'utf8' });
  if (push.status !== 0) die(1, `push failed: ${push.stderr.replace(token, '***')}`);
} finally {
  spawnSync('git', ['-C', REPO, 'checkout', startBranch], { encoding: 'utf8' });
}

// 5. Open the PR (DRAFT until graduation).
const ledger = loadLedger();
const graduated = ledger.cleanCycles >= GRADUATION_BAR;
const bodyFile = opt('--body-file');
const pr = await api(`/repos/${OWNER}/${NAME}/pulls`, {
  method: 'POST',
  body: JSON.stringify({
    title: opt('--title') || `forge(intake): ${skill}`,
    head: branch,
    base: 'main',
    draft: !graduated,
    body: bodyFile ? readFileSync(bodyFile, 'utf8') : `Automated forge intake PR for \`${skill}\`.\n\nOpened via \`scripts/open-intake-pr.mjs\` (allowlist-validated). ${graduated ? 'Lane is GRADUATED.' : `HIL gate active: draft until ${GRADUATION_BAR} clean cycles (currently ${ledger.cleanCycles}).`}`,
  }),
});
if (!pr.ok) die(1, `PR creation failed ${pr.status}: ${JSON.stringify(pr.body).slice(0, 500)}`);

// 6. Ledger: append this cycle record (cleanCycles is advanced by the review routine, not here).
const record = { ts: new Date().toISOString(), skill, pr: pr.body.html_url, draft: !graduated };
ledger.lastCycle = record;
ledger.history.push(record);
writeFileSync(LEDGER, JSON.stringify(ledger, null, 2) + '\n');

console.log(pr.body.html_url);
