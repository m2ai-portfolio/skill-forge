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
//   node scripts/open-intake-pr.mjs --skill <name> [--title "..."] [--body-file path]
//   node scripts/open-intake-pr.mjs --graduation-check
//
// Allowed staged paths: skills/<name>/** (new files only), registry.yaml,
// data/intake/*.processed.md, data/last_check.txt. Anything else = exit 2.
// Existing forge/<name> branch or open PR = exit 3 (kills the MAI-7 duplicate race).
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

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OWNER = 'm2ai-st-metro';
const NAME = 'skill-forge';
const LEDGER = resolve(REPO, 'data/forge-cycle-ledger.json');
const GRADUATION_BAR = 7;

const args = process.argv.slice(2);
const opt = (f) => (args.includes(f) ? args[args.indexOf(f) + 1] : null);
const die = (code, msg) => { console.error(msg); process.exit(code); };

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
