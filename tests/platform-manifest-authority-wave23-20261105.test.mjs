// Source-owned workflow structure assertions, not FPGA/guest execution evidence.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const workflow = readFileSync(new URL('../.github/workflows/platform-member-governance.yml', import.meta.url), 'utf8');

test('governance checkout uses only exact PR SHA with nonpersistent credentials', () => {
  assert.match(workflow, /ref:\s*\$\{\{ github\.event\.pull_request\.head\.sha \|\| github\.sha \}\}/);
  assert.match(workflow, /EXPECTED_HEAD:\s*\$\{\{ github\.event\.pull_request\.head\.sha \|\| github\.sha \}\}/);
  assert.match(workflow, /test "\$\(git rev-parse HEAD\)" = "\$EXPECTED_HEAD"/);
  assert.match(workflow, /persist-credentials:\s*false/);
});

test('runner dependencies are pinned to immutable 40-hex actions and read-only token', () => {
  const actions = [...workflow.matchAll(/uses:\s*(actions\/[\w-]+)@([^\s]+)/g)];
  assert.equal(actions.length, 2);
  assert.deepEqual(actions.map(x => x[1]), ['actions/checkout', 'actions/setup-node']);
  for (const [, , revision] of actions) assert.match(revision, /^[0-9a-f]{40}$/);
  assert.match(workflow, /permissions:\s*\n\s+contents:\s*read/);
  assert.doesNotMatch(workflow, /pull_request_target|permissions:\s*write-all|contents:\s*write|secrets\./);
});

test('workflow explicitly runs metadata governance, without release claims', () => {
  assert.match(workflow, /node --test tests\/platform-member-governance\.test\.mjs/);
  assert.match(workflow, /name: source-platform-member-governance \(metadata only\)/);
  assert.doesNotMatch(workflow, /\b(?:release|publish|deploy|upload-artifact)\s*:/);
});
