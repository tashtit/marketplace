// Unit tests for scripts/check-dependencies.js.
//
// The gate is only useful if it keeps failing on the cases it was written
// for, so each test mutates one aspect of a passing fixture and asserts the
// specific outcome: a hard failure for an unrecorded or stale dependency, and
// a non-blocking warning for a version that drifted from its record.

import assert from 'node:assert/strict';
import path from 'node:path';
import { describe, it } from 'node:test';

import * as checkDependencies from '../../scripts/check-dependencies.js';
import * as support from './support.js';

const NPM_RECORD = {
  ecosystem: 'npm',
  name: 'example-linter',
  version: '1.4.2',
  purpose: 'Lint the fixture repository.',
  alternatives: ['Write the rules here, rejected as unnecessary duplication.'],
  adoption: 'Widely depended on; last release checked on 2026-08-09.',
  provenance: 'Registry metadata resolves to the source repository below.',
  license: 'MIT',
  source: 'https://github.com/example/example-linter',
  reviewed_by: '@fixture',
  reviewed_on: '2026-08-09',
};

const ACTION_RECORD = {
  ...NPM_RECORD,
  ecosystem: 'github-actions',
  name: 'example/action',
  version: 'v3.1.0',
  purpose: 'Check out the fixture repository.',
  source: 'https://github.com/example/action',
};

function buildFixture(root, { registry, manifest, workflow } = {}) {
  support.writeJson(path.join(root, 'package.json'), {
    name: 'fixture',
    private: true,
    devDependencies: { 'example-linter': '1.4.2' },
    ...manifest,
  });
  support.writeText(
    path.join(root, '.github', 'workflows', 'ci.yml'),
    workflow ??
      'jobs:\n  test:\n    steps:\n      - uses: example/action@v3.1.0\n',
  );
  if (registry !== null) {
    support.writeJson(path.join(root, checkDependencies.REGISTRY_FILE), {
      dependencies: registry ?? [ACTION_RECORD, NPM_RECORD],
    });
  }
}

function run(t, options) {
  const root = support.tempRoot(t);
  buildFixture(root, options);
  return support.withRoot(checkDependencies, root, () =>
    support.captureOutput(() => checkDependencies.main()),
  );
}

describe('a compliant repository', () => {
  it('passes with every declared dependency recorded', (t) => {
    const { result, stdout } = run(t);
    assert.equal(result, 0);
    assert.match(stdout, /passed \(2 declared dependencies/);
  });

  it('ignores local actions, container steps, and node_modules', (t) => {
    const root = support.tempRoot(t);
    buildFixture(root, {
      workflow:
        'jobs:\n  test:\n    steps:\n' +
        '      - uses: ./.github/actions/local\n' +
        '      - uses: docker://alpine:3.20\n' +
        '      - uses: example/action@v3.1.0\n',
    });
    support.writeJson(
      path.join(root, 'node_modules', 'installed', 'package.json'),
      { name: 'installed', dependencies: { transitive: '1.0.0' } },
    );
    const { result } = support.withRoot(checkDependencies, root, () =>
      support.captureOutput(() => checkDependencies.main()),
    );
    assert.equal(result, 0);
  });

  it('treats a reusable workflow path as its owning repository', (t) => {
    const { result } = run(t, {
      workflow:
        'jobs:\n  test:\n' +
        '    uses: example/action/.github/workflows/build.yml@v3.1.0\n',
    });
    assert.equal(result, 0);
  });
});

describe('the hard gate on new dependencies', () => {
  it('fails when an npm dependency has no record', (t) => {
    const { result, stderr } = run(t, {
      manifest: { dependencies: { 'new-package': '2.0.0' } },
    });
    assert.equal(result, 1);
    assert.match(stderr, /new-package \(npm\).*no reviewed dependency record/s);
  });

  it('fails when an action has no record', (t) => {
    const { result, stderr } = run(t, {
      workflow: 'jobs:\n  test:\n    steps:\n      - uses: other/action@v1\n',
    });
    assert.equal(result, 1);
    assert.match(stderr, /other\/action \(github-actions\)/);
  });

  it('reports every manifest section', (t) => {
    for (const section of [
      'dependencies',
      'devDependencies',
      'optionalDependencies',
      'peerDependencies',
    ]) {
      const { result, stderr } = run(t, {
        manifest: { [section]: { unrecorded: '1.0.0' } },
      });
      assert.equal(result, 1, section);
      assert.match(stderr, /unrecorded \(npm\)/, section);
    }
  });

  it('fails when the registry is missing entirely', (t) => {
    const { result, stderr } = run(t, { registry: null });
    assert.equal(result, 1);
    assert.match(stderr, /dependency registry is missing/);
  });

  it('names the file that declares the dependency', (t) => {
    const { stderr } = run(t, {
      manifest: { dependencies: { 'new-package': '2.0.0' } },
    });
    assert.match(stderr, /package\.json/);
  });
});

describe('the soft gate on updates', () => {
  it('warns without failing when a recorded version drifted', (t) => {
    const { result, stdout } = run(t, {
      manifest: { devDependencies: { 'example-linter': '1.5.0' } },
    });
    assert.equal(result, 0);
    assert.match(stdout, /warning: .*example-linter \(npm\) is recorded at 1\.4\.2/);
    assert.match(stdout, /declares 1\.5\.0/);
    assert.match(stdout, /1 pending update review\)/);
  });

  it('warns when an action reference moved', (t) => {
    const { result, stdout } = run(t, {
      workflow: 'jobs:\n  test:\n    steps:\n      - uses: example/action@v4.0.0\n',
    });
    assert.equal(result, 0);
    assert.match(stdout, /example\/action \(github-actions\) is recorded at v3\.1\.0/);
  });
});

describe('registry hygiene', () => {
  it('fails on a record nothing declares', (t) => {
    const { result, stderr } = run(t, {
      registry: [
        ACTION_RECORD,
        NPM_RECORD,
        { ...NPM_RECORD, name: 'removed-package' },
      ],
    });
    assert.equal(result, 1);
    assert.match(stderr, /removed-package.*remove the stale record/s);
  });

  it('fails on a missing field', (t) => {
    const { reviewed_by: _omitted, ...incomplete } = NPM_RECORD;
    const { result, stderr } = run(t, {
      registry: [ACTION_RECORD, incomplete],
    });
    assert.equal(result, 1);
    assert.match(stderr, /is missing fields: reviewed_by/);
  });

  it('fails on an unsupported field', (t) => {
    const { result, stderr } = run(t, {
      registry: [ACTION_RECORD, { ...NPM_RECORD, approved: true }],
    });
    assert.equal(result, 1);
    assert.match(stderr, /unsupported fields: approved/);
  });

  it('fails on an unknown ecosystem', (t) => {
    const { result, stderr } = run(t, {
      registry: [ACTION_RECORD, NPM_RECORD, { ...NPM_RECORD, ecosystem: 'cargo' }],
    });
    assert.equal(result, 1);
    assert.match(stderr, /ecosystem must be one of/);
  });

  it('fails on an empty alternatives list', (t) => {
    const { result, stderr } = run(t, {
      registry: [ACTION_RECORD, { ...NPM_RECORD, alternatives: [] }],
    });
    assert.equal(result, 1);
    assert.match(stderr, /alternatives must be a non-empty array/);
  });

  it('fails on a non-https source', (t) => {
    const { result, stderr } = run(t, {
      registry: [ACTION_RECORD, { ...NPM_RECORD, source: 'example.com' }],
    });
    assert.equal(result, 1);
    assert.match(stderr, /source must be an https URL/);
  });

  it('fails on a malformed review date', (t) => {
    const { result, stderr } = run(t, {
      registry: [ACTION_RECORD, { ...NPM_RECORD, reviewed_on: 'August 2026' }],
    });
    assert.equal(result, 1);
    assert.match(stderr, /reviewed_on must be an ISO 8601 date/);
  });

  it('fails on unsorted records', (t) => {
    const { result, stderr } = run(t, {
      registry: [NPM_RECORD, ACTION_RECORD],
    });
    assert.equal(result, 1);
    assert.match(stderr, /must be sorted by ecosystem then name/);
  });

  it('fails on a duplicate record', (t) => {
    const { result, stderr } = run(t, {
      registry: [ACTION_RECORD, NPM_RECORD, NPM_RECORD],
    });
    assert.equal(result, 1);
    assert.match(stderr, /duplicate record for npm example-linter/);
  });

  it('fails on an invalid registry document', (t) => {
    const root = support.tempRoot(t);
    buildFixture(root, { registry: null });
    support.writeText(
      path.join(root, checkDependencies.REGISTRY_FILE),
      '{ "dependencies": [\n',
    );
    const { result, stderr } = support.withRoot(checkDependencies, root, () =>
      support.captureOutput(() => checkDependencies.main()),
    );
    assert.equal(result, 1);
    assert.match(stderr, /invalid JSON/);
  });
});
