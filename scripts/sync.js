#!/usr/bin/env node
// Generate Tashtit's Codex adapters from their canonical sources.
//
// Codex requires two files that cannot live at the shared Claude/Copilot
// paths:
//
// - `.agents/plugins/marketplace.json`, whose catalog schema differs;
// - `.codex-plugin/plugin.json` per plugin, whose content matches the shared
//   manifest but whose location is fixed by the host.
//
// Both are generated here and drift-checked by `make validate`. Repository
// symlinks are deliberately not used: Git materializes them as plain text
// files when `core.symlinks=false`, which is the default whenever a checkout
// cannot create symlinks, and a host would then read the link target instead
// of JSON.

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

let ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

const SHARED_MANIFEST_DIR = '.claude-plugin';
const CODEX_MANIFEST_DIR = '.codex-plugin';
const DISPLAY_NAME = 'Tashtit';
const PLUGIN_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const PLATFORMS = new Set(['claude-code', 'codex', 'cursor', 'github-copilot']);
// Platforms a plugin targets by default when it declares no `platforms` list.
// Cursor is optional research, so it is opt-in rather than a default target.
const CORE_TARGETS = new Set(['claude-code', 'codex', 'github-copilot']);
const SEMVER =
  /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/;
const REQUIRED_MANIFEST_FIELDS = ['name', 'version', 'description', 'skills'];

// Raised when a canonical source cannot be trusted for generation.
export class SyncError extends Error {}

export function setRoot(newRoot) {
  const previous = ROOT;
  ROOT = newRoot;
  return previous;
}

const sharedMarketplacePath = () =>
  path.join(ROOT, '.claude-plugin', 'marketplace.json');
const codexMarketplacePath = () =>
  path.join(ROOT, '.agents', 'plugins', 'marketplace.json');
const pluginsRoot = () => path.join(ROOT, 'plugins');

function relative(filePath) {
  const rel = path.relative(ROOT, filePath);
  return rel === '' || rel.startsWith('..') || path.isAbsolute(rel)
    ? String(filePath)
    : rel;
}

const isObjectValue = (value) =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

function requireObject(value, field) {
  if (!isObjectValue(value)) {
    throw new SyncError(`${field} must be an object`);
  }
  return value;
}

function requireText(value, field) {
  if (typeof value !== 'string' || !value.trim()) {
    throw new SyncError(`${field} must be a non-empty string`);
  }
  return value;
}

function readJson(filePath) {
  let raw;
  try {
    raw = fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    if (error.code === 'ENOENT') {
      throw new SyncError(`missing canonical source: ${relative(filePath)}`);
    }
    throw error;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new SyncError(`${relative(filePath)}: invalid JSON: ${error.message}`);
  }
}

export function loadSharedMarketplace() {
  const marketplace = requireObject(
    readJson(sharedMarketplacePath()),
    'marketplace',
  );
  if (requireText(marketplace.name, 'name') !== 'tashtit') {
    throw new SyncError("name must be 'tashtit'");
  }
  const owner = requireObject(marketplace.owner, 'owner');
  requireText(owner.name, 'owner.name');
  const metadata = requireObject(marketplace.metadata, 'metadata');
  requireText(metadata.description, 'metadata.description');
  if (!SEMVER.test(requireText(metadata.version, 'metadata.version'))) {
    throw new SyncError('metadata.version must use Semantic Versioning');
  }

  const plugins = marketplace.plugins;
  if (!Array.isArray(plugins)) {
    throw new SyncError('plugins must be an array');
  }

  const names = [];
  plugins.forEach((rawPlugin, index) => {
    const plugin = requireObject(rawPlugin, `plugins[${index}]`);
    const prefix = `plugins[${index}]`;
    const name = requireText(plugin.name, `${prefix}.name`);
    if (!PLUGIN_NAME.test(name)) {
      throw new SyncError(`${prefix}.name must use lowercase kebab-case`);
    }
    names.push(name);
    if (plugin.source !== `./plugins/${name}`) {
      throw new SyncError(`${prefix}.source must be './plugins/${name}'`);
    }
    requireText(plugin.description, `${prefix}.description`);
    if (!SEMVER.test(requireText(plugin.version, `${prefix}.version`))) {
      throw new SyncError(`${prefix}.version must use Semantic Versioning`);
    }
    if (plugin.license !== 'Apache-2.0') {
      throw new SyncError(`${prefix}.license must be 'Apache-2.0'`);
    }
    requireText(plugin.category, `${prefix}.category`);
    const platforms = plugin.platforms;
    if (platforms !== undefined && platforms !== null) {
      if (
        !Array.isArray(platforms) ||
        platforms.length === 0 ||
        platforms.some((item) => typeof item !== 'string')
      ) {
        throw new SyncError(
          `${prefix}.platforms must be a non-empty array of strings`,
        );
      }
      const unknown = platforms
        .filter((item) => !PLATFORMS.has(item))
        .sort();
      if (unknown.length > 0) {
        throw new SyncError(
          `${prefix}.platforms has unknown platforms ${JSON.stringify(unknown)}`,
        );
      }
    }
  });

  if (names.join('\n') !== [...names].sort().join('\n')) {
    throw new SyncError('plugins must be sorted by name');
  }
  if (names.length !== new Set(names).size) {
    throw new SyncError('plugin names must be unique');
  }
  return marketplace;
}

export function targetsCodex(entry) {
  // Whether a plugin gets a generated Codex adapter.
  //
  // A plugin targets every core platform unless it declares a narrower
  // `platforms` list. Codex is the only platform with a separately generated
  // adapter, so omitting it from `platforms` suppresses that adapter while
  // the shared Claude/Copilot manifest is unaffected.
  const platforms = entry.platforms;
  if (platforms === undefined || platforms === null) {
    return CORE_TARGETS.has('codex');
  }
  return platforms.includes('codex');
}

export function buildCodexMarketplace(marketplace) {
  // Translate the shared entries to Codex's incompatible catalog schema.
  const plugins = [];
  for (const plugin of marketplace.plugins) {
    if (!targetsCodex(plugin)) {
      continue;
    }
    plugins.push({
      name: plugin.name,
      source: {
        source: 'local',
        path: `./plugins/${plugin.name}`,
      },
      policy: {
        installation: 'AVAILABLE',
        authentication: 'ON_INSTALL',
      },
      category: plugin.category,
    });
  }
  return {
    name: marketplace.name,
    interface: { displayName: DISPLAY_NAME },
    plugins,
  };
}

function pluginDirectories() {
  let entries;
  try {
    entries = fs.readdirSync(pluginsRoot(), { withFileTypes: true });
  } catch {
    throw new SyncError(`missing plugins directory: ${relative(pluginsRoot())}`);
  }
  return entries
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith('.'))
    .map((entry) => path.join(pluginsRoot(), entry.name))
    .sort();
}

export function loadSharedManifest(manifestPath, pluginName) {
  // Return the canonical manifest text once Codex's requirements hold.
  //
  // Codex accepts the shared manifest schema, so the generated file is a byte
  // copy. Validate here rather than emitting an adapter a host cannot load.
  const manifest = requireObject(
    readJson(manifestPath),
    `${relative(manifestPath)} manifest`,
  );
  if (manifest.name !== pluginName) {
    throw new SyncError(
      `${relative(manifestPath)}: name must be ${JSON.stringify(pluginName)}`,
    );
  }
  for (const field of REQUIRED_MANIFEST_FIELDS) {
    requireText(manifest[field], `${relative(manifestPath)}.${field}`);
  }
  if (!SEMVER.test(manifest.version)) {
    throw new SyncError(
      `${relative(manifestPath)}: version must use Semantic Versioning`,
    );
  }
  if (!manifest.skills.startsWith('./')) {
    throw new SyncError(
      `${relative(manifestPath)}: skills path must start with './'`,
    );
  }
  return fs.readFileSync(manifestPath, 'utf8');
}

export function render(value) {
  return JSON.stringify(value, null, 2) + '\n';
}

export function collectArtifacts() {
  // Pair every generated path with the content its canonical source implies.
  //
  // Also returns the generated adapters that must no longer exist, so that a
  // plugin dropping codex from its platforms is remediated by `make sync`
  // instead of leaving an adapter that only `make validate` complains about.
  const marketplace = loadSharedMarketplace();
  const codexTargets = new Set(
    marketplace.plugins
      .filter((plugin) => targetsCodex(plugin))
      .map((plugin) => plugin.name),
  );
  const artifacts = [
    [codexMarketplacePath(), render(buildCodexMarketplace(marketplace))],
  ];
  const obsolete = [];
  for (const pluginDir of pluginDirectories()) {
    const adapter = path.join(pluginDir, CODEX_MANIFEST_DIR, 'plugin.json');
    if (!codexTargets.has(path.basename(pluginDir))) {
      if (isFile(adapter) || isSymlink(adapter)) {
        obsolete.push(adapter);
      }
      continue;
    }
    const sharedManifest = path.join(
      pluginDir,
      SHARED_MANIFEST_DIR,
      'plugin.json',
    );
    artifacts.push([
      adapter,
      loadSharedManifest(sharedManifest, path.basename(pluginDir)),
    ]);
  }
  return { artifacts, obsolete };
}

export function removeObsolete(adapterPath, check) {
  // Remove one adapter whose plugin no longer targets codex.
  if (check) {
    process.stderr.write(
      `${relative(adapterPath)}: plugin no longer targets codex, so its ` +
        'generated adapter must be removed\n',
    );
    return false;
  }
  fs.unlinkSync(adapterPath);
  try {
    fs.rmdirSync(path.dirname(adapterPath));
  } catch {
    // The directory holds files this script does not generate; validation
    // will report them if they are a problem.
  }
  process.stdout.write(`removed ${relative(adapterPath)}\n`);
  return true;
}

function splitKeepingNewlines(text) {
  return text.split(/(?<=\n)/);
}

// Minimal unified-style diff: trims the common prefix and suffix and prints
// the differing middle. Enough to show which generated lines drifted.
function writeDiff(actual, expected, fromFile, toFile) {
  const actualLines = splitKeepingNewlines(actual);
  const expectedLines = splitKeepingNewlines(expected);

  let start = 0;
  while (
    start < actualLines.length &&
    start < expectedLines.length &&
    actualLines[start] === expectedLines[start]
  ) {
    start += 1;
  }
  let actualEnd = actualLines.length;
  let expectedEnd = expectedLines.length;
  while (
    actualEnd > start &&
    expectedEnd > start &&
    actualLines[actualEnd - 1] === expectedLines[expectedEnd - 1]
  ) {
    actualEnd -= 1;
    expectedEnd -= 1;
  }

  const ensureNewline = (line) => (line.endsWith('\n') ? line : `${line}\n`);
  process.stderr.write(`--- ${fromFile}\n`);
  process.stderr.write(`+++ ${toFile}\n`);
  for (const line of actualLines.slice(start, actualEnd)) {
    process.stderr.write(ensureNewline(`-${line.replace(/\n$/, '')}`));
  }
  for (const line of expectedLines.slice(start, expectedEnd)) {
    process.stderr.write(ensureNewline(`+${line.replace(/\n$/, '')}`));
  }
}

function isSymlink(filePath) {
  try {
    return fs.lstatSync(filePath).isSymbolicLink();
  } catch {
    return false;
  }
}

function isFile(filePath) {
  try {
    return fs.statSync(filePath).isFile();
  } catch {
    return false;
  }
}

export function syncArtifact(artifactPath, expected, check) {
  // Write or verify one generated file, replacing any symlink in place.
  const linked = isSymlink(artifactPath);
  const actual = isFile(artifactPath)
    ? fs.readFileSync(artifactPath, 'utf8')
    : '';
  if (!linked && actual === expected) {
    return true;
  }

  if (check) {
    if (linked) {
      process.stderr.write(
        `${relative(artifactPath)}: must be a generated regular file, not a ` +
          'symlink; symlinks become plain text when core.symlinks=false\n',
      );
      return false;
    }
    writeDiff(
      actual,
      expected,
      relative(artifactPath),
      `${relative(artifactPath)} (generated)`,
    );
    return false;
  }

  if (linked) {
    fs.unlinkSync(artifactPath);
  }
  fs.mkdirSync(path.dirname(artifactPath), { recursive: true });
  fs.writeFileSync(artifactPath, expected);
  process.stdout.write(`updated ${relative(artifactPath)}\n`);
  return true;
}

export function main() {
  const check = process.argv.includes('--check');

  let collected;
  try {
    collected = collectArtifacts();
  } catch (error) {
    if (error instanceof SyncError) {
      process.stderr.write(
        `canonical source validation failed: ${error.message}\n`,
      );
      return 1;
    }
    throw error;
  }

  const { artifacts, obsolete } = collected;
  const stale = artifacts.filter(
    ([artifactPath, expected]) => !syncArtifact(artifactPath, expected, check),
  );
  stale.push(
    ...obsolete.filter((adapterPath) => !removeObsolete(adapterPath, check)),
  );
  if (stale.length > 0) {
    process.stderr.write(
      'Generated Codex adapters are stale; run `make sync` and include ' +
        'the result\n',
    );
    return 1;
  }
  if (check) {
    process.stdout.write(
      `Generated Codex adapters are synchronized (${artifacts.length} files).\n`,
    );
  }
  return 0;
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href
) {
  process.exit(main());
}
