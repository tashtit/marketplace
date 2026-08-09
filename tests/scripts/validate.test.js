// Unit tests for scripts/validate.js.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { describe, it } from 'node:test';

import * as validate from '../../scripts/validate.js';
import * as support from './support.js';

describe('parseFrontmatter', () => {
  function parse(t, content) {
    const root = support.tempRoot(t);
    const filePath = path.join(root, 'SKILL.md');
    support.writeText(filePath, content);
    return support.withRoot(validate, root, () => ({
      fields: validate.parseFrontmatter(filePath),
      errors: [...validate.errors],
    }));
  }

  it('parses scalar fields', (t) => {
    const { fields, errors } = parse(
      t,
      '---\nname: alpha\ndescription: A skill.\n---\nBody.\n',
    );
    assert.deepEqual(errors, []);
    assert.deepEqual(fields, { name: 'alpha', description: 'A skill.' });
  });

  it('unquotes double-quoted values', (t) => {
    const { fields, errors } = parse(
      t,
      '---\ndescription: "A \\"quoted\\" value"\n---\n',
    );
    assert.deepEqual(errors, []);
    assert.equal(fields.description, 'A "quoted" value');
  });

  it('rejects a missing opening marker', (t) => {
    const { fields, errors } = parse(t, 'name: alpha\n');
    assert.deepEqual(fields, {});
    assert.match(errors[0], /must begin with a '---'/);
  });

  it('rejects an unclosed block', (t) => {
    const { errors } = parse(t, '---\nname: alpha\n');
    assert.match(errors[0], /never closed/);
  });

  it('rejects a duplicate field', (t) => {
    const { errors } = parse(t, '---\nname: alpha\nname: beta\n---\n');
    assert.match(errors[0], /duplicate frontmatter field/);
  });

  it('rejects a non-scalar line', (t) => {
    const { errors } = parse(t, '---\n- a list item\n---\n');
    assert.match(errors[0], /cannot parse/);
  });
});

describe('parseCatalogTable', () => {
  it('maps rows and skips non-plugin lines', (t) => {
    const root = support.tempRoot(t);
    const filePath = path.join(root, 'README.md');
    support.writeText(
      filePath,
      '| Plugin | Version | Maturity |\n' +
        '| --- | --- | --- |\n' +
        '| [alpha](plugins/alpha/) | 1.0.0 | Experimental |\n' +
        '| [docs](docs/notes.md) | x | y |\n' +
        'Prose outside the table.\n',
    );
    const { listed, errors } = support.withRoot(validate, root, () => ({
      listed: validate.parseCatalogTable(filePath, 'plugins/'),
      errors: [...validate.errors],
    }));
    assert.deepEqual(errors, []);
    assert.deepEqual(
      [...listed.entries()],
      [['alpha', ['1.0.0', 'Experimental']]],
    );
  });

  it('rejects duplicate rows', (t) => {
    const root = support.tempRoot(t);
    const filePath = path.join(root, 'README.md');
    support.writeText(
      filePath,
      '| [alpha](plugins/alpha/) | 1.0.0 | Experimental |\n' +
        '| [alpha](plugins/alpha/) | 1.0.0 | Experimental |\n',
    );
    const errors = support.withRoot(validate, root, () => {
      validate.parseCatalogTable(filePath, 'plugins/');
      return [...validate.errors];
    });
    assert.match(errors[0], /duplicate catalog row/);
  });
});

describe('validateManifestComponents', () => {
  function check(t, manifest, prepare = () => {}) {
    const root = support.tempRoot(t);
    prepare(root);
    return support.withRoot(validate, root, () => {
      validate.validateManifestComponents(
        path.join(root, 'plugin.json'),
        root,
        manifest,
      );
      return [...validate.errors];
    });
  }

  it('accepts existing component paths', (t) => {
    const errors = check(
      t,
      { skills: './skills', agents: ['./agents/a.md'] },
      (root) => {
        support.writeText(path.join(root, 'agents', 'a.md'), 'agent\n');
        support.writeText(path.join(root, 'skills', '.keep'), '');
      },
    );
    assert.deepEqual(errors, []);
  });

  it('rejects a string where an array is required', (t) => {
    const errors = check(t, { agents: './agents/' });
    assert.match(errors[0], /must be a non-empty array of file paths/);
  });

  it('rejects a missing string component path', (t) => {
    const errors = check(t, { skills: './skills' });
    assert.match(errors[0], /does not exist/);
  });

  it('rejects a list entry that is not a file', (t) => {
    const errors = check(t, { commands: ['./missing.md'] });
    assert.match(errors[0], /is not a file/);
  });
});

describe('validateAcceptanceResults', () => {
  const SCENARIOS = new Map([['alpha-positive-case', new Set(['claude-code'])]]);

  function entry(overrides = {}) {
    return {
      scenario: 'alpha-positive-case',
      platform: 'claude-code',
      plugin_version: '1.0.0',
      commit: '0'.repeat(40),
      reviewed_on: '2026-01-01',
      reviewer: 'reviewer',
      outcome: 'pass',
      ...overrides,
    };
  }

  function check(t, results) {
    const root = support.tempRoot(t);
    return support.withRoot(validate, root, () => ({
      passes: validate.validateAcceptanceResults(
        path.join(root, 'acceptance.json'),
        SCENARIOS,
        results,
      ),
      errors: [...validate.errors],
    }));
  }

  it('indexes passing reviews by version', (t) => {
    const { passes, errors } = check(t, [entry()]);
    assert.deepEqual(errors, []);
    const key = JSON.stringify(['alpha-positive-case', 'claude-code']);
    assert.deepEqual([...passes.keys()], [key]);
    assert.deepEqual([...passes.get(key)], ['1.0.0']);
  });

  it('rejects non-array results', (t) => {
    const { passes, errors } = check(t, 'not-a-list');
    assert.equal(passes.size, 0);
    assert.match(errors[0], /results must be an array/);
  });

  it('rejects an unknown scenario', (t) => {
    const { errors } = check(t, [entry({ scenario: 'alpha-unknown' })]);
    assert.match(errors[0], /unknown scenario/);
  });

  it('rejects a platform the scenario does not claim', (t) => {
    const { errors } = check(t, [entry({ platform: 'codex' })]);
    assert.match(errors[0], /does not claim/);
  });

  it('rejects a short commit', (t) => {
    const { errors } = check(t, [entry({ commit: 'abc123' })]);
    assert.match(errors[0], /40-character commit/);
  });

  it('rejects a duplicate review', (t) => {
    const { errors } = check(t, [entry(), entry()]);
    assert.match(errors[0], /duplicates the review/);
  });

  it('does not index a failing review as a pass', (t) => {
    const { passes, errors } = check(t, [entry({ outcome: 'fail' })]);
    assert.deepEqual(errors, []);
    assert.equal(passes.size, 0);
  });
});

describe('validateActionPins', () => {
  function pinErrors(t, stepLines) {
    const root = support.tempRoot(t);
    support.writeText(
      path.join(root, '.github', 'workflows', 'ci.yml'),
      'jobs:\n  build:\n    steps:\n' + stepLines,
    );
    return support.withRoot(validate, root, () => {
      validate.validateActionPins();
      return [...validate.errors];
    });
  }

  it('accepts a full SHA and an exact GitHub tag in both step forms', (t) => {
    const errors = pinErrors(
      t,
      `      - uses: third/party@${'0'.repeat(40)}\n` +
        '      - name: Checkout\n' +
        '        uses: actions/checkout@v7.0.1\n',
    );
    assert.deepEqual(errors, []);
  });

  it('rejects a movable major tag on a GitHub action', (t) => {
    const errors = pinErrors(t, '      - uses: actions/cache@v7\n');
    assert.equal(errors.length, 1);
    assert.match(errors[0], /exact release tag/);
  });

  it('rejects a release tag on a third-party action', (t) => {
    const errors = pinErrors(t, '      - uses: third/party@v1.2.3\n');
    assert.equal(errors.length, 1);
    assert.match(errors[0], /full 40-character commit SHA/);
  });

  it('rejects a branch reference', (t) => {
    const errors = pinErrors(t, '      - uses: actions/checkout@main\n');
    assert.equal(errors.length, 1);
  });
});

describe('main against a fixture repository', () => {
  function setUp(t) {
    const root = support.tempRoot(t);
    support.buildRepo(root, ['alpha', 'beta']);
    return root;
  }

  function runMain(root) {
    return support.withRoot(validate, root, () =>
      support.captureOutput(() => validate.main()),
    );
  }

  it('passes on a clean fixture', (t) => {
    const root = setUp(t);
    const { result, stderr } = runMain(root);
    assert.equal(result, 0, stderr);
  });

  it('fails on an unsorted marketplace', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => data.plugins.reverse() && data,
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /plugins must be sorted by name/);
  });

  it('fails on catalog version drift', (t) => {
    const root = setUp(t);
    const readme = path.join(root, 'README.md');
    const content = fs.readFileSync(readme, 'utf8');
    support.writeText(
      readme,
      content.replace(
        '| [alpha](plugins/alpha/) | 1.0.0 |',
        '| [alpha](plugins/alpha/) | 2.0.0 |',
      ),
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /listed as version "2\.0\.0"/);
  });

  it('fails on a missing scenario type', (t) => {
    const root = setUp(t);
    fs.unlinkSync(
      path.join(
        root,
        'tests',
        'plugins',
        'alpha',
        'scenarios',
        'unsafe-case.json',
      ),
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /missing required scenario types/);
    assert.match(stderr, /unsafe/);
  });

  it('fails on collapsed JSON', (t) => {
    const root = setUp(t);
    support.writeText(
      path.join(root, 'tests', 'plugins', 'alpha', 'acceptance.json'),
      '{"plugin": "alpha", "maturity": "experimental", "results": []}\n',
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /pretty-printed/);
  });

  it('fails on manifest version drift', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, 'plugins', 'alpha', '.claude-plugin', 'plugin.json'),
      (data) => {
        data.version = '9.9.9';
        return data;
      },
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /version differs across provider adapters/);
  });

  it('fails on an overlong skill description', (t) => {
    const root = setUp(t);
    support.writeText(
      path.join(root, 'plugins', 'alpha', 'skills', 'tashtit-alpha', 'SKILL.md'),
      '---\nname: tashtit-alpha\ndescription: ' +
        'x'.repeat(1100) +
        '\n---\n\nBody.\n',
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /skill description limit/);
  });

  it('fails on a duplicate skill name', (t) => {
    const root = setUp(t);
    support.writeText(
      path.join(root, 'plugins', 'beta', 'skills', 'tashtit-beta', 'SKILL.md'),
      '---\nname: tashtit-alpha\ndescription: Duplicate of alpha.\n---\n\nBody.\n',
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /must match the skill directory/);
  });

  it('fails on a skill name without the tashtit- prefix', (t) => {
    const root = setUp(t);
    support.writeText(
      path.join(root, 'plugins', 'alpha', 'skills', 'extra', 'SKILL.md'),
      '---\nname: extra\ndescription: Unprefixed fixture skill.\n---\n\nBody.\n',
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /must carry the 'tashtit-' provenance prefix/);
  });

  it('fails on a broken markdown link', (t) => {
    const root = setUp(t);
    support.writeText(
      path.join(root, 'docs.md'),
      'See [missing](missing/file.md).\n',
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /broken local link/);
  });

  it('fails on a blank markdown link target', (t) => {
    const root = setUp(t);
    support.writeText(path.join(root, 'docs.md'), 'See [blank]( ).\n');
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /markdown link target is blank/);
  });

  it('fails on an orphaned test directory', (t) => {
    const root = setUp(t);
    support.writeText(
      path.join(root, 'tests', 'plugins', 'gamma', 'REVIEW.md'),
      '# Review checklist for a plugin that no longer exists\n',
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /test directory has no matching plugin/);
  });

  it('survives a non-list platforms declaration', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => {
        data.plugins[0].platforms = 'claude-code';
        return data;
      },
    );
    // The malformed declaration is an error, not a crash that discards
    // every other diagnostic.
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /platforms must be a non-empty array/);
  });
});

