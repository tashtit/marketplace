// Shared fixtures for the repository script test suite.
//
// `buildRepo` writes a minimal repository tree that `scripts/validate.js`
// accepts and `scripts/sync.js --check` reports as synchronized. Each test
// mutates one aspect of that tree and asserts on the specific failure the
// mutation causes, so a validator check that silently stops firing breaks a
// test instead of shipping.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';

export const PLUGIN_VERSION = '1.0.0';

export function tempRoot(t) {
  // realpathSync matters: macOS temp directories live behind a /var symlink,
  // and the scripts compare resolved paths against their root.
  const dir = fs.realpathSync(
    fs.mkdtempSync(path.join(os.tmpdir(), 'tashtit-fixture-')),
  );
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

export function writeText(filePath, content) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content);
}

export function writeJson(filePath, value) {
  // Serialize exactly like scripts/sync.js renders generated artifacts.
  writeText(filePath, JSON.stringify(value, null, 2) + '\n');
}

export function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

export function mutateJson(filePath, mutate) {
  const value = readJson(filePath);
  writeJson(filePath, mutate(value) ?? value);
}

export function pluginDescription(name) {
  return `Fixture plugin ${name}.`;
}

export function scenario(plugin, kind) {
  return {
    id: `${plugin}-${kind}-case`,
    type: kind,
    platforms: ['claude-code'],
    prompt: `Exercise the ${kind} path of ${plugin}.`,
    setup: ['A repository prepared for the scenario.'],
    expected: ['The documented behavior is observed.'],
    must_not: ['No credential material appears in output.'],
  };
}

function catalogTable(names, prefix) {
  const rows = [...names]
    .sort()
    .map(
      (name) =>
        `| [${name}](${prefix}${name}/) | ${PLUGIN_VERSION} | Experimental |`,
    )
    .join('\n');
  return `| Plugin | Version | Maturity |\n| --- | --- | --- |\n${rows}\n`;
}

export function buildRepo(root, plugins = ['alpha']) {
  // Write a minimal repository tree that passes validation and sync.
  const names = [...plugins].sort();

  writeJson(path.join(root, '.claude-plugin', 'marketplace.json'), {
    name: 'tashtit',
    owner: { name: 'Fixture Maintainers' },
    metadata: {
      description: 'Fixture marketplace for script tests.',
      version: '0.1.0',
    },
    plugins: names.map((name) => ({
      name,
      source: `./plugins/${name}`,
      description: pluginDescription(name),
      version: PLUGIN_VERSION,
      license: 'Apache-2.0',
      category: 'testing',
    })),
  });

  // The exact content scripts/sync.js is expected to generate; writing it
  // here makes `sync --check` on the clean fixture assert the generator.
  writeJson(path.join(root, '.agents', 'plugins', 'marketplace.json'), {
    name: 'tashtit',
    interface: { displayName: 'Tashtit' },
    plugins: names.map((name) => ({
      name,
      source: { source: 'local', path: `./plugins/${name}` },
      policy: { installation: 'AVAILABLE', authentication: 'ON_INSTALL' },
      category: 'testing',
    })),
  });

  for (const name of names) {
    const pluginDir = path.join(root, 'plugins', name);
    const manifest = {
      name,
      version: PLUGIN_VERSION,
      description: pluginDescription(name),
      license: 'Apache-2.0',
      skills: './skills',
    };
    writeJson(path.join(pluginDir, '.claude-plugin', 'plugin.json'), manifest);
    writeJson(path.join(pluginDir, '.codex-plugin', 'plugin.json'), manifest);
    writeText(
      path.join(pluginDir, 'skills', name, 'SKILL.md'),
      '---\n' +
        `name: ${name}\n` +
        `description: Fixture skill for ${name}.\n` +
        '---\n' +
        '\n' +
        'Use this fixture skill to exercise the validator.\n',
    );

    const testsDir = path.join(root, 'tests', 'plugins', name);
    writeText(
      path.join(testsDir, 'REVIEW.md'),
      `# Review checklist for ${name}\n\nReviewed for fixture use.\n`,
    );
    writeJson(path.join(testsDir, 'acceptance.json'), {
      plugin: name,
      maturity: 'experimental',
      results: [],
    });
    for (const kind of ['positive', 'failure', 'unsafe']) {
      writeJson(
        path.join(testsDir, 'scenarios', `${kind}-case.json`),
        scenario(name, kind),
      );
    }
  }

  writeText(
    path.join(root, 'README.md'),
    '# Fixture marketplace\n\n' + catalogTable(names, 'plugins/'),
  );
  writeText(
    path.join(root, 'plugins', 'README.md'),
    '# Fixture plugins\n\n' + catalogTable(names, ''),
  );
}

export function withRoot(module, root, fn) {
  // Point a script module at a fixture tree and reset its recorded state.
  const previous = module.setRoot(root);
  module.errors?.splice(0);
  module.findings?.splice(0);
  module.warnings?.splice(0);
  try {
    return fn();
  } finally {
    module.setRoot(previous);
    module.errors?.splice(0);
    module.findings?.splice(0);
    module.warnings?.splice(0);
  }
}

export function captureOutput(fn) {
  let stdout = '';
  let stderr = '';
  const originalStdout = process.stdout.write;
  const originalStderr = process.stderr.write;
  process.stdout.write = (chunk) => {
    stdout += chunk;
    return true;
  };
  process.stderr.write = (chunk) => {
    stderr += chunk;
    return true;
  };
  try {
    const result = fn();
    return { result, stdout, stderr };
  } finally {
    process.stdout.write = originalStdout;
    process.stderr.write = originalStderr;
  }
}
