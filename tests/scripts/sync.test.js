// Unit tests for scripts/sync.js.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { describe, it } from 'node:test';

import * as sync from '../../scripts/sync.js';
import * as support from './support.js';

describe('targetsCodex', () => {
  it('defaults to codex when platforms are omitted', () => {
    assert.equal(sync.targetsCodex({ name: 'alpha' }), true);
  });

  it('respects an explicit platform list', () => {
    assert.equal(sync.targetsCodex({ platforms: ['codex'] }), true);
    assert.equal(sync.targetsCodex({ platforms: ['claude-code'] }), false);
  });
});

describe('buildCodexMarketplace', () => {
  it('translates entries and drops non-codex plugins', () => {
    const marketplace = {
      name: 'tashtit',
      plugins: [
        { name: 'alpha', category: 'testing' },
        { name: 'beta', category: 'testing', platforms: ['claude-code'] },
      ],
    };
    const built = sync.buildCodexMarketplace(marketplace);
    assert.equal(built.name, 'tashtit');
    assert.deepEqual(built.interface, { displayName: 'Tashtit' });
    assert.deepEqual(built.plugins, [
      {
        name: 'alpha',
        source: { source: 'local', path: './plugins/alpha' },
        policy: { installation: 'AVAILABLE', authentication: 'ON_INSTALL' },
        category: 'testing',
      },
    ]);
  });

  it('renders pretty-printed JSON with a trailing newline', () => {
    assert.equal(sync.render({ a: 1 }), '{\n  "a": 1\n}\n');
  });
});

describe('loadSharedMarketplace', () => {
  function setUp(t) {
    const root = support.tempRoot(t);
    support.buildRepo(root, ['alpha', 'beta']);
    return root;
  }

  it('accepts the fixture marketplace', (t) => {
    const root = setUp(t);
    const marketplace = support.withRoot(sync, root, () =>
      sync.loadSharedMarketplace(),
    );
    assert.deepEqual(
      marketplace.plugins.map((plugin) => plugin.name),
      ['alpha', 'beta'],
    );
  });

  it('rejects unsorted plugins', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => data.plugins.reverse() && data,
    );
    support.withRoot(sync, root, () => {
      assert.throws(() => sync.loadSharedMarketplace(), /sorted by name/);
    });
  });

  it('rejects a non-semver version', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => {
        data.plugins[0].version = '1.0';
        return data;
      },
    );
    support.withRoot(sync, root, () => {
      assert.throws(() => sync.loadSharedMarketplace(), /Semantic Versioning/);
    });
  });

  it('rejects an unknown platform', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => {
        data.plugins[0].platforms = ['mystery'];
        return data;
      },
    );
    support.withRoot(sync, root, () => {
      assert.throws(() => sync.loadSharedMarketplace(), /unknown platforms/);
    });
  });
});

describe('loadSharedManifest', () => {
  function manifest(overrides = {}) {
    return {
      name: 'alpha',
      version: '1.0.0',
      description: 'Fixture plugin alpha.',
      skills: './skills',
      ...overrides,
    };
  }

  function load(t, value) {
    const root = support.tempRoot(t);
    const filePath = path.join(root, 'plugin.json');
    support.writeJson(filePath, value);
    return support.withRoot(sync, root, () =>
      sync.loadSharedManifest(filePath, 'alpha'),
    );
  }

  it('returns the manifest text verbatim', (t) => {
    const content = load(t, manifest());
    assert.equal(content, JSON.stringify(manifest(), null, 2) + '\n');
  });

  it('rejects a name mismatch', (t) => {
    assert.throws(() => load(t, manifest({ name: 'beta' })), /name must be/);
  });

  it('rejects a missing required field', (t) => {
    const value = manifest();
    delete value.skills;
    assert.throws(() => load(t, value), /skills/);
  });

  it('rejects a skills path without a leading dot-slash', (t) => {
    assert.throws(
      () => load(t, manifest({ skills: 'skills' })),
      /start with '\.\/'/,
    );
  });
});

describe('syncArtifact', () => {
  it('passes check mode for a current file', (t) => {
    const root = support.tempRoot(t);
    const filePath = path.join(root, 'generated.json');
    support.writeText(filePath, 'expected\n');
    assert.equal(sync.syncArtifact(filePath, 'expected\n', true), true);
  });

  it('fails check mode for a stale file with a diff', (t) => {
    const root = support.tempRoot(t);
    const filePath = path.join(root, 'generated.json');
    support.writeText(filePath, 'stale\n');
    const { result, stderr } = support.captureOutput(() =>
      sync.syncArtifact(filePath, 'expected\n', true),
    );
    assert.equal(result, false);
    assert.match(stderr, /-stale/);
    assert.match(stderr, /\+expected/);
  });

  it('creates the expected content in write mode', (t) => {
    const root = support.tempRoot(t);
    const filePath = path.join(root, 'nested', 'generated.json');
    const { result } = support.captureOutput(() =>
      sync.syncArtifact(filePath, 'expected\n', false),
    );
    assert.equal(result, true);
    assert.equal(fs.readFileSync(filePath, 'utf8'), 'expected\n');
  });

  it('fails check mode for a symlink and replaces it in write mode', (t) => {
    const root = support.tempRoot(t);
    const target = path.join(root, 'target.json');
    support.writeText(target, 'expected\n');
    const link = path.join(root, 'generated.json');
    fs.symlinkSync(target, link);

    const checked = support.captureOutput(() =>
      sync.syncArtifact(link, 'expected\n', true),
    );
    assert.equal(checked.result, false);
    assert.match(checked.stderr, /symlink/);

    const written = support.captureOutput(() =>
      sync.syncArtifact(link, 'expected\n', false),
    );
    assert.equal(written.result, true);
    assert.equal(fs.lstatSync(link).isSymbolicLink(), false);
    assert.equal(fs.readFileSync(link, 'utf8'), 'expected\n');
  });
});

describe('main', () => {
  function setUp(t) {
    const root = support.tempRoot(t);
    support.buildRepo(root, ['alpha', 'beta']);
    return root;
  }

  function runMain(root, ...argv) {
    const originalArgv = process.argv;
    process.argv = ['node', 'sync.js', ...argv];
    try {
      return support.withRoot(sync, root, () =>
        support.captureOutput(() => sync.main()),
      );
    } finally {
      process.argv = originalArgv;
    }
  }

  it('passes check mode on a synchronized fixture', (t) => {
    const root = setUp(t);
    const { result, stdout, stderr } = runMain(root, '--check');
    assert.equal(result, 0, stderr);
    // One codex marketplace plus one adapter per plugin.
    assert.match(stdout, /\(3 files\)/);
  });

  it('fails check mode on a stale generated file', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.agents', 'plugins', 'marketplace.json'),
      (data) => {
        data.plugins[0].category = 'drifted';
        return data;
      },
    );
    const { result, stderr } = runMain(root, '--check');
    assert.equal(result, 1);
    assert.match(stderr, /stale/);
  });

  it('regenerates a stale file in write mode', (t) => {
    const root = setUp(t);
    const marketplacePath = path.join(
      root,
      '.agents',
      'plugins',
      'marketplace.json',
    );
    const expected = fs.readFileSync(marketplacePath, 'utf8');
    support.mutateJson(marketplacePath, (data) => {
      data.plugins[0].category = 'drifted';
      return data;
    });
    const { result, stdout } = runMain(root);
    assert.equal(result, 0);
    assert.match(stdout, /updated/);
    assert.equal(fs.readFileSync(marketplacePath, 'utf8'), expected);
  });

  it('fails before generation on an invalid canonical source', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => {
        data.name = 'wrong';
        return data;
      },
    );
    const { result, stderr } = runMain(root, '--check');
    assert.equal(result, 1);
    assert.match(stderr, /canonical source validation failed/);
  });

  it('marks the adapter of a non-codex plugin obsolete', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => {
        data.plugins[1].platforms = ['claude-code'];
        return data;
      },
    );
    const { artifacts, obsolete } = support.withRoot(sync, root, () =>
      sync.collectArtifacts(),
    );
    assert.equal(artifacts.length, 2);
    const betaAdapter = path.join(
      root,
      'plugins',
      'beta',
      '.codex-plugin',
      'plugin.json',
    );
    assert.ok(!artifacts.some(([artifactPath]) => artifactPath === betaAdapter));
    assert.deepEqual(obsolete, [betaAdapter]);
  });

  it('reports an obsolete adapter in check mode', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => {
        data.plugins[1].platforms = ['claude-code'];
        return data;
      },
    );
    const { result, stderr } = runMain(root, '--check');
    assert.equal(result, 1);
    assert.match(stderr, /no longer targets codex/);
  });

  it('removes an obsolete adapter in write mode', (t) => {
    const root = setUp(t);
    support.mutateJson(
      path.join(root, '.claude-plugin', 'marketplace.json'),
      (data) => {
        data.plugins[1].platforms = ['claude-code'];
        return data;
      },
    );
    // Write mode must also regenerate the codex marketplace without beta.
    const { result, stdout } = runMain(root);
    assert.equal(result, 0);
    assert.match(stdout, /removed/);
    const betaAdapter = path.join(
      root,
      'plugins',
      'beta',
      '.codex-plugin',
      'plugin.json',
    );
    assert.equal(fs.existsSync(betaAdapter), false);
    // The emptied .codex-plugin directory is cleaned up too.
    assert.equal(fs.existsSync(path.dirname(betaAdapter)), false);
    // A subsequent check run converges.
    const checked = runMain(root, '--check');
    assert.equal(checked.result, 0, checked.stderr);
  });
});
