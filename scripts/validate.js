#!/usr/bin/env node
// Validate the Tashtit repository without third-party dependencies.

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

let ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

const PLUGIN_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const MARKDOWN_LINK = /!?\[[^\]]*]\(([^)]+)\)/g;
// A step may open with "- uses:" or carry "uses:" on its own line; both forms
// reference an action and both must satisfy the pinning rule.
const ACTION_REFERENCE = /^\s*(?:-\s+)?uses:\s+([^@\s]+)@([^\s#]+)/gm;
const FULL_SHA = /^[0-9a-f]{40}$/;
// A GitHub-authored action may use an exact release tag. A movable major tag
// such as "v7" or a branch name stays forbidden because it is not immutable.
const GITHUB_AUTHORED_OWNERS = ['actions/', 'github/'];
const EXACT_RELEASE_TAG = /^v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/;
const SCENARIO_TYPES = new Set(['positive', 'failure', 'unsafe']);
const SCENARIO_FIELDS = new Set([
  'id',
  'type',
  'platforms',
  'prompt',
  'setup',
  'expected',
  'must_not',
]);
const PLATFORMS = new Set(['claude-code', 'codex', 'cursor', 'github-copilot']);
// Platforms a plugin targets by default when it declares no `platforms` list.
// Cursor is optional research, so it is opt-in rather than a default target.
const CORE_TARGETS = new Set(['claude-code', 'codex', 'github-copilot']);
const MATURITY_LEVELS = ['experimental', 'candidate', 'stable'];
// Experimental makes no behavioral claim, so it needs no recorded results.
const REVIEWED_MATURITY = new Set(
  MATURITY_LEVELS.filter((level) => level !== 'experimental'),
);
const ACCEPTANCE_FIELDS = new Set(['plugin', 'maturity', 'results']);
const RESULT_FIELDS = new Set([
  'scenario',
  'platform',
  'plugin_version',
  'commit',
  'reviewed_on',
  'reviewer',
  'outcome',
]);
const RESULT_OPTIONAL_FIELDS = new Set(['notes']);
const RESULT_OUTCOMES = new Set(['pass', 'fail']);
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;
const SEMVER = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/;
const MATURITY_CLAIM =
  /\b(Experimental|Candidate|Stable)\b\s*[—-]\s*(\d+\.\d+\.\d+(?:[0-9A-Za-z.-]*[0-9A-Za-z])?)/g;
const FRONTMATTER_FIELD = /^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$/;
// The portable Agent Skills convention caps a skill description. A longer one
// risks truncation or rejection by a host, which silently weakens triggering.
const SKILL_DESCRIPTION_LIMIT = 1024;

export const errors = [];

// Directories that never carry repository content: version control and editor
// state, plus installed dependencies. Kept in one place so every traversal
// skips the same paths.
const IGNORED_DIRECTORIES = new Set(['.git', '.idea', 'node_modules']);

// Decodes strictly so binary content is skipped exactly where Python's
// UnicodeDecodeError used to skip it.
const utf8 = new TextDecoder('utf-8', { fatal: true });

export function setRoot(newRoot) {
  const previous = ROOT;
  ROOT = newRoot;
  return previous;
}

function marketplacePaths() {
  return {
    shared: path.join(ROOT, '.claude-plugin', 'marketplace.json'),
    codex: path.join(ROOT, '.agents', 'plugins', 'marketplace.json'),
  };
}

function readText(filePath) {
  return utf8.decode(fs.readFileSync(filePath));
}

function splitLines(text) {
  const lines = text.split(/\r\n|\r|\n/);
  if (lines.length > 0 && lines[lines.length - 1] === '') {
    lines.pop();
  }
  return lines;
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

function isDirectory(filePath) {
  try {
    return fs.statSync(filePath).isDirectory();
  } catch {
    return false;
  }
}

function listDirectory(dirPath) {
  try {
    return fs.readdirSync(dirPath, { withFileTypes: true });
  } catch {
    return [];
  }
}

// Walks without following directory symlinks, mirroring os.walk and
// Path.rglob defaults, and skips ignored directories everywhere.
function* walk(dirPath) {
  for (const entry of listDirectory(dirPath).sort((a, b) =>
    a.name < b.name ? -1 : a.name > b.name ? 1 : 0,
  )) {
    if (IGNORED_DIRECTORIES.has(entry.name)) {
      continue;
    }
    const entryPath = path.join(dirPath, entry.name);
    yield { path: entryPath, entry };
    if (entry.isDirectory()) {
      yield* walk(entryPath);
    }
  }
}

function* walkFiles(startPath) {
  for (const { path: entryPath, entry } of walk(startPath)) {
    if (entry.isFile()) {
      yield entryPath;
    }
  }
}

const isObjectValue = (value) =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const valueType = (value) =>
  Array.isArray(value) ? 'array' : value === null ? 'null' : typeof value;

const sorted = (iterable) => [...iterable].sort();

const difference = (a, b) => [...a].filter((item) => !b.has(item));

const intersection = (a, b) => new Set([...a].filter((item) => b.has(item)));

const symmetricDifference = (a, b) => [
  ...difference(a, b),
  ...difference(b, a),
];

const setEquals = (a, b) => a.size === b.size && [...a].every((x) => b.has(x));

const show = (value) => JSON.stringify(value);

const showList = (values) => JSON.stringify(values);

export function fail(filePath, message) {
  const relative = path.relative(ROOT, filePath);
  const display =
    relative === '' || relative.startsWith('..') || path.isAbsolute(relative)
      ? String(filePath)
      : relative;
  errors.push(`${display}: ${message}`);
}

export function loadJson(filePath) {
  let raw;
  try {
    raw = fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    if (error.code === 'ENOENT') {
      fail(filePath, 'required file is missing');
      return {};
    }
    throw error;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    fail(filePath, `invalid JSON: ${error.message}`);
    return {};
  }
}

function requireObject(filePath, value, context) {
  if (!isObjectValue(value)) {
    fail(filePath, `${context} must be an object`);
    return {};
  }
  return value;
}

function requireText(filePath, value, field) {
  if (typeof value !== 'string' || !value.trim()) {
    fail(filePath, `${field} must be a non-empty string`);
    return '';
  }
  return value;
}

export function pluginPlatforms(entry) {
  // A plugin's declared target platforms, defaulting to core targets.
  const platforms = entry.platforms;
  if (platforms === undefined || platforms === null) {
    return new Set(CORE_TARGETS);
  }
  // validateMarketplaces records the error for a malformed declaration;
  // fall back to the default so validation can continue past it.
  if (!Array.isArray(platforms)) {
    return new Set(CORE_TARGETS);
  }
  return intersection(
    new Set(platforms.filter((item) => typeof item === 'string')),
    PLATFORMS,
  );
}

export function validateMarketplaces() {
  const catalogs = {};

  for (const [platform, marketplacePath] of Object.entries(
    marketplacePaths(),
  )) {
    const data = requireObject(
      marketplacePath,
      loadJson(marketplacePath),
      'marketplace',
    );
    const name = requireText(marketplacePath, data.name, 'name');
    if (name !== 'tashtit') {
      fail(marketplacePath, "name must be 'tashtit'");
    }

    let plugins = data.plugins;
    if (!Array.isArray(plugins)) {
      fail(marketplacePath, 'plugins must be an array');
      plugins = [];
    }

    const entries = new Map();
    plugins.forEach((rawEntry, index) => {
      const entry = requireObject(
        marketplacePath,
        rawEntry,
        `plugins[${index}]`,
      );
      const pluginName = requireText(
        marketplacePath,
        entry.name,
        `plugins[${index}].name`,
      );
      if (pluginName && !PLUGIN_NAME.test(pluginName)) {
        fail(marketplacePath, `invalid plugin name: ${show(pluginName)}`);
      }
      if (entries.has(pluginName)) {
        fail(marketplacePath, `duplicate plugin entry: ${pluginName}`);
      }
      entries.set(pluginName, entry);

      if (platform === 'shared') {
        const expectedSource = `./plugins/${pluginName}`;
        if (entry.source !== expectedSource) {
          fail(
            marketplacePath,
            `${pluginName} source must be ${show(expectedSource)}`,
          );
        }
        const rawPlatforms = entry.platforms;
        if (rawPlatforms !== undefined && rawPlatforms !== null) {
          const values = validateStringList(
            marketplacePath,
            rawPlatforms,
            `${pluginName}.platforms`,
          );
          const unknown = sorted(difference(new Set(values), PLATFORMS));
          if (unknown.length > 0) {
            fail(
              marketplacePath,
              `${pluginName}.platforms has unknown platforms ` +
                `${showList(unknown)}; expected values from ` +
                `${showList(sorted(PLATFORMS))}`,
            );
          }
        }
      } else {
        const source = requireObject(
          marketplacePath,
          entry.source,
          `${pluginName}.source`,
        );
        const sourceMatches =
          Object.keys(source).length === 2 &&
          source.source === 'local' &&
          source.path === `./plugins/${pluginName}`;
        if (!sourceMatches) {
          fail(
            marketplacePath,
            `${pluginName} must use the repository-local source object`,
          );
        }
        const policy = requireObject(
          marketplacePath,
          entry.policy,
          `${pluginName}.policy`,
        );
        if (
          !['NOT_AVAILABLE', 'AVAILABLE', 'INSTALLED_BY_DEFAULT'].includes(
            policy.installation,
          )
        ) {
          fail(
            marketplacePath,
            `${pluginName} has an invalid installation policy`,
          );
        }
        if (!['ON_INSTALL', 'ON_USE'].includes(policy.authentication)) {
          fail(
            marketplacePath,
            `${pluginName} has an invalid authentication policy`,
          );
        }
        requireText(marketplacePath, entry.category, `${pluginName}.category`);
      }
    });

    const names = [...entries.keys()];
    if (names.join('\n') !== sorted(names).join('\n')) {
      fail(marketplacePath, 'plugins must be sorted by name');
    }
    catalogs[platform] = entries;
  }

  const shared = catalogs.shared ?? new Map();
  const codexTargets = new Set(
    [...shared.entries()]
      .filter(([, entry]) => pluginPlatforms(entry).has('codex'))
      .map(([name]) => name),
  );
  const codexNames = new Set((catalogs.codex ?? new Map()).keys());
  if (!setEquals(codexNames, codexTargets)) {
    fail(
      marketplacePaths().codex,
      'plugin set differs from codex-targeted shared plugins: ' +
        showList(sorted(symmetricDifference(codexNames, codexTargets))),
    );
  }

  return catalogs;
}

// Component fields in a Claude Code plugin manifest and the JSON type each
// must have. Claude Code rejects a manifest whose component field has the
// wrong type with a load error such as "agents: Invalid input", which
// silently breaks marketplace installation. `agents` and `commands` are
// arrays of file paths; the rest are string directory or file paths. See the
// plugin manifest schema:
// https://code.claude.com/docs/en/plugins-reference#complete-schema
const MANIFEST_STRING_COMPONENTS = [
  'skills',
  'hooks',
  'mcpServers',
  'outputStyles',
  'lspServers',
];
const MANIFEST_LIST_COMPONENTS = ['commands', 'agents'];

export function validateManifestComponents(manifestPath, pluginDir, manifest) {
  // Enforce Claude Code's component field types and referenced paths.
  //
  // A wrong-typed component field (for example `"agents": "./agents/"` where
  // the schema requires an array) loads cleanly as JSON but is rejected by
  // the host at install time, so it must fail validation here instead.
  for (const field of MANIFEST_STRING_COMPONENTS) {
    if (!(field in manifest)) {
      continue;
    }
    const value = manifest[field];
    if (typeof value !== 'string' || !value.trim()) {
      fail(manifestPath, `${field} must be a non-empty string path`);
      continue;
    }
    if (!fs.existsSync(path.join(pluginDir, value))) {
      fail(manifestPath, `${field} path ${show(value)} does not exist`);
    }
  }

  for (const field of MANIFEST_LIST_COMPONENTS) {
    if (!(field in manifest)) {
      continue;
    }
    const value = manifest[field];
    if (!Array.isArray(value) || value.length === 0) {
      fail(
        manifestPath,
        `${field} must be a non-empty array of file paths, not ` +
          valueType(value),
      );
      continue;
    }
    for (const item of value) {
      if (typeof item !== 'string' || !item.trim()) {
        fail(manifestPath, `${field} entries must be non-empty string paths`);
        continue;
      }
      if (!isFile(path.join(pluginDir, item))) {
        fail(manifestPath, `${field} path ${show(item)} is not a file`);
      }
    }
  }
}

function pluginDirectories() {
  const pluginsRoot = path.join(ROOT, 'plugins');
  return listDirectory(pluginsRoot)
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith('.'))
    .map((entry) => path.join(pluginsRoot, entry.name))
    .sort();
}

export function validatePlugins(shared) {
  const pluginsRoot = path.join(ROOT, 'plugins');
  const pluginDirs = pluginDirectories();
  const catalogNames = new Set(shared.keys());
  const directoryNames = new Set(pluginDirs.map((dir) => path.basename(dir)));

  if (!setEquals(directoryNames, catalogNames)) {
    const missing = sorted(difference(directoryNames, catalogNames));
    const stale = sorted(difference(catalogNames, directoryNames));
    if (missing.length > 0) {
      fail(pluginsRoot, `plugins missing from marketplaces: ${showList(missing)}`);
    }
    if (stale.length > 0) {
      fail(
        pluginsRoot,
        `marketplace entries without plugin directories: ${showList(stale)}`,
      );
    }
  }

  for (const pluginDir of pluginDirs) {
    const name = path.basename(pluginDir);
    if (!PLUGIN_NAME.test(name)) {
      fail(pluginDir, 'directory name must use lowercase kebab-case');
    }

    const manifests = {
      shared: path.join(pluginDir, '.claude-plugin', 'plugin.json'),
    };
    const codexManifest = path.join(pluginDir, '.codex-plugin', 'plugin.json');
    if (pluginPlatforms(shared.get(name) ?? {}).has('codex')) {
      manifests.codex = codexManifest;
    } else if (fs.existsSync(codexManifest) || isSymlink(codexManifest)) {
      fail(
        codexManifest,
        'plugin does not target codex, so its generated .codex-plugin ' +
          'adapter must be absent',
      );
    }

    const redundantManifest = path.join(pluginDir, 'plugin.json');
    if (fs.existsSync(redundantManifest) || isSymlink(redundantManifest)) {
      fail(
        redundantManifest,
        'duplicate manifest is prohibited; no supported host reads it',
      );
    }

    const loaded = {};
    for (const [platform, manifestPath] of Object.entries(manifests)) {
      if (isSymlink(manifestPath)) {
        fail(
          manifestPath,
          'manifest must be a regular file; a symlink becomes plain ' +
            'text when core.symlinks=false and no host can parse it',
        );
      }
      const manifest = requireObject(
        manifestPath,
        loadJson(manifestPath),
        'plugin manifest',
      );
      loaded[platform] = manifest;
      if (manifest.name !== name) {
        fail(manifestPath, `name must match plugin directory ${show(name)}`);
      }
    }

    const sharedEntry = shared.get(name) ?? {};
    const portableVersion = sharedEntry.version;
    const portableDescription = sharedEntry.description;
    for (const [platform, manifest] of Object.entries(loaded)) {
      if (manifest.version !== portableVersion) {
        fail(manifests[platform], 'version differs across provider adapters');
      }
      if (manifest.description !== portableDescription) {
        fail(
          manifests[platform],
          'description differs from the shared marketplace',
        );
      }
      if (manifest.license !== 'Apache-2.0') {
        fail(manifests[platform], "license must be 'Apache-2.0'");
      }
      validateManifestComponents(manifests[platform], pluginDir, manifest);
    }

    const skillFile = path.join(pluginDir, 'skills', name, 'SKILL.md');
    if (!isFile(skillFile)) {
      fail(skillFile, 'canonical skill is missing');
    }
  }
}

export function parseFrontmatter(filePath) {
  // Parse a SKILL.md frontmatter block of single-line key: value fields.
  //
  // The frontmatter is what every supported host loads to decide whether a
  // skill triggers, so it is validated strictly: it must open the file, be
  // closed, and contain only blank lines and single-line scalar fields.
  // Anything more exotic risks parsing differently across hosts.
  const lines = splitLines(readText(filePath));
  if (lines.length === 0 || lines[0].trim() !== '---') {
    fail(filePath, "must begin with a '---' frontmatter block");
    return {};
  }
  const fields = {};
  for (const line of lines.slice(1)) {
    if (line.trim() === '---') {
      return fields;
    }
    if (!line.trim()) {
      continue;
    }
    const match = FRONTMATTER_FIELD.exec(line);
    if (!match) {
      fail(
        filePath,
        "frontmatter must contain only single-line 'key: value' " +
          `fields; cannot parse: ${show(line)}`,
      );
      continue;
    }
    const key = match[1];
    let value = match[2].trim();
    if (value.length >= 2 && value.startsWith('"') && value.endsWith('"')) {
      value = value.slice(1, -1).replaceAll('\\"', '"');
    }
    if (key in fields) {
      fail(filePath, `duplicate frontmatter field ${show(key)}`);
      continue;
    }
    fields[key] = value;
  }
  fail(filePath, "frontmatter block is never closed with '---'");
  return fields;
}

function skillFiles() {
  const found = [];
  for (const pluginDir of pluginDirectories()) {
    const skillsRoot = path.join(pluginDir, 'skills');
    for (const entry of listDirectory(skillsRoot)) {
      if (!entry.isDirectory()) {
        continue;
      }
      const skillFile = path.join(skillsRoot, entry.name, 'SKILL.md');
      if (isFile(skillFile)) {
        found.push(skillFile);
      }
    }
  }
  return found.sort();
}

export function validateSkillFrontmatter() {
  // Validate the trigger surface each host loads for every skill.
  //
  // Hosts select skills from the frontmatter name and description alone and
  // flatten every installed skill into one namespace, so a malformed name, a
  // missing description, or a name collision breaks routing without producing
  // any load error a user would see.
  const seen = new Map();
  for (const skillPath of skillFiles()) {
    const fields = parseFrontmatter(skillPath);
    const name = fields.name ?? '';
    const directoryName = path.basename(path.dirname(skillPath));
    if (!name) {
      fail(skillPath, 'frontmatter must declare a name');
    } else if (name !== directoryName) {
      fail(
        skillPath,
        `frontmatter name ${show(name)} must match the skill directory ` +
          show(directoryName),
      );
    } else if (!PLUGIN_NAME.test(name)) {
      fail(skillPath, 'frontmatter name must use lowercase kebab-case');
    } else if (seen.has(name)) {
      fail(
        skillPath,
        `skill name ${show(name)} is already used by ` +
          `${path.relative(ROOT, seen.get(name))}; hosts flatten installed ` +
          'skills into one namespace',
      );
    } else {
      seen.set(name, skillPath);
    }

    const description = fields.description ?? '';
    if (!description.trim()) {
      fail(skillPath, 'frontmatter must declare a non-empty description');
    } else if (description.length > SKILL_DESCRIPTION_LIMIT) {
      fail(
        skillPath,
        `description is ${description.length} characters, above the ` +
          `${SKILL_DESCRIPTION_LIMIT}-character skill description limit`,
      );
    }
  }
}

export function parseCatalogTable(filePath, prefix) {
  // Map plugin name to its listed version and maturity for each table row.
  const listed = new Map();
  for (const line of splitLines(readText(filePath))) {
    if (!line.trimStart().startsWith('|')) {
      continue;
    }
    const cells = line
      .trim()
      .replace(/^\|+|\|+$/g, '')
      .split('|')
      .map((cell) => cell.trim());
    if (cells.length < 3) {
      continue;
    }
    const targets = [...cells[0].matchAll(MARKDOWN_LINK)].map(
      (match) => match[1],
    );
    if (targets.length !== 1) {
      continue;
    }
    const target = targets[0].trim();
    if (!target.endsWith('/')) {
      continue;
    }
    if (prefix && !target.startsWith(prefix)) {
      continue;
    }
    const name = target
      .slice(prefix.length)
      .replace(/^[./]+/, '')
      .replace(/[./]+$/, '');
    if (!PLUGIN_NAME.test(name)) {
      continue;
    }
    if (listed.has(name)) {
      fail(filePath, `duplicate catalog row for ${name}`);
      continue;
    }
    listed.set(name, [cells[1], cells[2]]);
  }
  return listed;
}

export function validateCatalogTables(shared, maturityByPlugin) {
  // Keep advertised catalogs identical to the canonical marketplace.
  //
  // A published table that disagrees with the marketplace is drift, so it is
  // validated like any other generated-from-canonical artifact.
  const tables = [
    [path.join(ROOT, 'README.md'), 'plugins/'],
    [path.join(ROOT, 'plugins', 'README.md'), ''],
  ];
  for (const [tablePath, prefix] of tables) {
    if (!isFile(tablePath)) {
      fail(tablePath, 'required file is missing');
      continue;
    }

    const listed = parseCatalogTable(tablePath, prefix);
    const expectedNames = new Set(shared.keys());
    const listedNames = new Set(listed.keys());
    const missing = sorted(difference(expectedNames, listedNames));
    const unexpected = sorted(difference(listedNames, expectedNames));
    if (missing.length > 0) {
      fail(tablePath, `catalog table is missing plugins: ${showList(missing)}`);
    }
    if (unexpected.length > 0) {
      fail(
        tablePath,
        `catalog table lists unknown plugins: ${showList(unexpected)}`,
      );
    }

    for (const [name, [version, maturity]] of [...listed.entries()].sort()) {
      const expectedVersion = (shared.get(name) ?? {}).version;
      if (expectedVersion && version !== expectedVersion) {
        fail(
          tablePath,
          `${name} is listed as version ${show(version)} but the ` +
            `marketplace declares ${show(expectedVersion)}`,
        );
      }
      const expectedMaturity = maturityByPlugin.get(name);
      if (expectedMaturity && maturity.toLowerCase() !== expectedMaturity) {
        fail(
          tablePath,
          `${name} is listed as maturity ${show(maturity)} but its ` +
            `acceptance record declares ${show(expectedMaturity)}`,
        );
      }
    }

    const names = [...listed.keys()];
    if (names.join('\n') !== sorted(names).join('\n')) {
      fail(tablePath, 'catalog table rows must be sorted by plugin name');
    }
  }
}

export function validateStringList(filePath, value, field) {
  if (
    !Array.isArray(value) ||
    value.length === 0 ||
    !value.every((item) => typeof item === 'string' && item.trim())
  ) {
    fail(filePath, `${field} must be a non-empty array of non-empty strings`);
    return [];
  }
  return value;
}

export function validateScenarios(shared) {
  // Validate scenario shape and index each plugin's scenario platforms.
  //
  // The returned index is what makes the acceptance gate enforceable: it
  // states exactly which scenario and platform pairs a non-experimental
  // plugin must have recorded results for.
  const index = new Map();
  const seenIds = new Set();
  for (const pluginDir of pluginDirectories()) {
    const pluginName = path.basename(pluginDir);
    const pluginScenarios = new Map();
    index.set(pluginName, pluginScenarios);
    const declaredPlatforms = pluginPlatforms(shared.get(pluginName) ?? {});
    const testsRoot = path.join(ROOT, 'tests', 'plugins', pluginName);
    const reviewPath = path.join(testsRoot, 'REVIEW.md');
    if (!isFile(reviewPath)) {
      fail(reviewPath, 'human review checklist is missing');
    }

    const scenariosDir = path.join(testsRoot, 'scenarios');
    const scenarioPaths = isDirectory(scenariosDir)
      ? listDirectory(scenariosDir)
          .filter((entry) => entry.isFile() && entry.name.endsWith('.json'))
          .map((entry) => path.join(scenariosDir, entry.name))
          .sort()
      : [];
    if (scenarioPaths.length === 0) {
      fail(scenariosDir, 'at least one acceptance scenario is required');
      continue;
    }

    const foundTypes = new Set();
    for (const scenarioPath of scenarioPaths) {
      const scenario = requireObject(
        scenarioPath,
        loadJson(scenarioPath),
        'scenario',
      );
      const unknownFields = sorted(
        difference(new Set(Object.keys(scenario)), SCENARIO_FIELDS),
      );
      if (unknownFields.length > 0) {
        fail(scenarioPath, `unsupported fields: ${showList(unknownFields)}`);
      }
      const missingFields = sorted(
        difference(SCENARIO_FIELDS, new Set(Object.keys(scenario))),
      );
      if (missingFields.length > 0) {
        fail(scenarioPath, `missing fields: ${showList(missingFields)}`);
      }

      const scenarioId = requireText(scenarioPath, scenario.id, 'id');
      if (scenarioId) {
        if (!PLUGIN_NAME.test(scenarioId)) {
          fail(scenarioPath, 'id must use lowercase kebab-case');
        }
        if (seenIds.has(scenarioId)) {
          fail(scenarioPath, `duplicate scenario id: ${scenarioId}`);
        }
        seenIds.add(scenarioId);
      }

      const scenarioType = requireText(scenarioPath, scenario.type, 'type');
      if (!SCENARIO_TYPES.has(scenarioType)) {
        fail(
          scenarioPath,
          `type must be one of ${showList(sorted(SCENARIO_TYPES))}`,
        );
      } else {
        foundTypes.add(scenarioType);
      }

      const platforms = validateStringList(
        scenarioPath,
        scenario.platforms,
        'platforms',
      );
      const unknownPlatforms = sorted(
        difference(new Set(platforms), PLATFORMS),
      );
      if (unknownPlatforms.length > 0) {
        fail(
          scenarioPath,
          `unsupported platforms ${showList(unknownPlatforms)}; ` +
            `expected values from ${showList(sorted(PLATFORMS))}`,
        );
      }
      const knownPlatforms = intersection(new Set(platforms), PLATFORMS);
      const undeclaredPlatforms = sorted(
        difference(knownPlatforms, declaredPlatforms),
      );
      if (undeclaredPlatforms.length > 0) {
        fail(
          scenarioPath,
          `platforms ${showList(undeclaredPlatforms)} are not declared by ` +
            `${pluginName}; expected values from ` +
            showList(sorted(declaredPlatforms)),
        );
      }
      if (scenarioId) {
        pluginScenarios.set(scenarioId, knownPlatforms);
      }

      requireText(scenarioPath, scenario.prompt, 'prompt');
      validateStringList(scenarioPath, scenario.setup, 'setup');
      validateStringList(scenarioPath, scenario.expected, 'expected');
      validateStringList(scenarioPath, scenario.must_not, 'must_not');
    }

    const missingTypes = sorted(difference(SCENARIO_TYPES, foundTypes));
    if (missingTypes.length > 0) {
      fail(
        scenariosDir,
        `missing required scenario types: ${showList(missingTypes)}`,
      );
    }
  }

  return index;
}

export function validateTestDirectories() {
  // Reject test trees for plugins that no longer exist.
  //
  // A deleted or renamed plugin would otherwise leave its acceptance record,
  // scenarios, and review checklist behind forever, silently advertising
  // coverage for something the marketplace no longer ships.
  const testsRoot = path.join(ROOT, 'tests', 'plugins');
  if (!isDirectory(testsRoot)) {
    return;
  }
  const pluginNames = new Set(
    listDirectory(path.join(ROOT, 'plugins'))
      .filter((entry) => entry.isDirectory() && !entry.name.startsWith('.'))
      .map((entry) => entry.name),
  );
  for (const entry of listDirectory(testsRoot).sort((a, b) =>
    a.name < b.name ? -1 : a.name > b.name ? 1 : 0,
  )) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) {
      continue;
    }
    if (!pluginNames.has(entry.name)) {
      fail(
        path.join(testsRoot, entry.name),
        'test directory has no matching plugin under plugins/',
      );
    }
  }
}

export function validateAcceptanceResults(filePath, scenarios, results) {
  // Validate recorded review results and index passes by scenario platform.
  //
  // Each entry records one reviewed scenario and platform pair. The index
  // maps that pair to the plugin versions it passed on, so the gate can
  // require a pass at the version being published rather than at any version
  // ever reviewed.
  const passes = new Map();
  if (!Array.isArray(results)) {
    fail(filePath, 'results must be an array');
    return passes;
  }

  const seen = new Set();
  results.forEach((entry, position) => {
    const label = `results[${position}]`;
    if (!isObjectValue(entry)) {
      fail(filePath, `${label} must be an object`);
      return;
    }

    const entryFields = new Set(Object.keys(entry));
    const unknown = sorted(
      [...entryFields].filter(
        (field) =>
          !RESULT_FIELDS.has(field) && !RESULT_OPTIONAL_FIELDS.has(field),
      ),
    );
    if (unknown.length > 0) {
      fail(filePath, `${label} has unsupported fields: ${showList(unknown)}`);
    }
    const missing = sorted(difference(RESULT_FIELDS, entryFields));
    if (missing.length > 0) {
      fail(filePath, `${label} is missing fields: ${showList(missing)}`);
      return;
    }

    const {
      scenario,
      platform,
      plugin_version: version,
      commit,
      reviewed_on: reviewedOn,
      outcome,
    } = entry;

    if (!requireText(filePath, entry.reviewer, `${label}.reviewer`)) {
      return;
    }
    if (!scenarios.has(scenario)) {
      fail(filePath, `${label} references unknown scenario ${show(scenario)}`);
      return;
    }
    if (!scenarios.get(scenario).has(platform)) {
      fail(
        filePath,
        `${label} reviews ${show(scenario)} on ${show(platform)}, which the ` +
          'scenario does not claim',
      );
      return;
    }
    if (typeof version !== 'string' || !SEMVER.test(version)) {
      fail(filePath, `${label}.plugin_version must be a semantic version`);
      return;
    }
    if (typeof commit !== 'string' || !FULL_SHA.test(commit)) {
      fail(
        filePath,
        `${label}.commit must be a full lowercase 40-character commit ` +
          'SHA so the reviewed content is unambiguous',
      );
    }
    if (typeof reviewedOn !== 'string' || !ISO_DATE.test(reviewedOn)) {
      fail(filePath, `${label}.reviewed_on must be an ISO 8601 date`);
    }
    if (!RESULT_OUTCOMES.has(outcome)) {
      fail(
        filePath,
        `${label}.outcome must be one of ${showList(sorted(RESULT_OUTCOMES))}`,
      );
      return;
    }

    const key = JSON.stringify([scenario, platform, version]);
    if (seen.has(key)) {
      fail(
        filePath,
        `${label} duplicates the review of ${show(scenario)} on ` +
          `${show(platform)} at version ${version}`,
      );
    }
    seen.add(key);

    if (outcome === 'pass') {
      const passKey = JSON.stringify([scenario, platform]);
      if (!passes.has(passKey)) {
        passes.set(passKey, new Set());
      }
      passes.get(passKey).add(version);
    }
  });

  return passes;
}

export function validateAcceptance(shared, scenarioIndex) {
  // Enforce the maturity gate against recorded behavioral review results.
  //
  // Scenarios describe required behavior but nothing executes them, so a
  // maturity claim above experimental is only credible when a human or
  // evaluation runner has recorded a passing result for every scenario and
  // platform pair at the published version.
  const maturityByPlugin = new Map();
  for (const name of sorted(scenarioIndex.keys())) {
    const acceptancePath = path.join(
      ROOT,
      'tests',
      'plugins',
      name,
      'acceptance.json',
    );
    if (!isFile(acceptancePath)) {
      fail(acceptancePath, 'acceptance record is missing');
      continue;
    }

    const record = requireObject(
      acceptancePath,
      loadJson(acceptancePath),
      'acceptance record',
    );
    const recordFields = new Set(Object.keys(record));
    const unknown = sorted(difference(recordFields, ACCEPTANCE_FIELDS));
    if (unknown.length > 0) {
      fail(acceptancePath, `unsupported fields: ${showList(unknown)}`);
    }
    const missing = sorted(difference(ACCEPTANCE_FIELDS, recordFields));
    if (missing.length > 0) {
      fail(acceptancePath, `missing fields: ${showList(missing)}`);
    }

    if (record.plugin !== name) {
      fail(acceptancePath, `plugin must be ${show(name)}`);
    }

    const maturity = record.maturity;
    if (!MATURITY_LEVELS.includes(maturity)) {
      fail(
        acceptancePath,
        `maturity must be one of ${showList(MATURITY_LEVELS)}`,
      );
      continue;
    }
    maturityByPlugin.set(name, maturity);

    const scenarios = scenarioIndex.get(name) ?? new Map();
    const passes = validateAcceptanceResults(
      acceptancePath,
      scenarios,
      record.results,
    );
    if (!REVIEWED_MATURITY.has(maturity)) {
      continue;
    }

    const version = (shared.get(name) ?? {}).version;
    if (typeof version !== 'string') {
      continue;
    }

    const unreviewed = sorted(
      [...scenarios.entries()].flatMap(([scenario, platforms]) =>
        sorted(platforms)
          .filter(
            (platform) =>
              !(
                passes.get(JSON.stringify([scenario, platform])) ?? new Set()
              ).has(version),
          )
          .map((platform) => `${scenario} on ${platform}`),
      ),
    );
    if (unreviewed.length > 0) {
      fail(
        acceptancePath,
        `maturity ${show(maturity)} requires a recorded pass at version ` +
          `${version} for every scenario and platform; missing: ` +
          showList(unreviewed),
      );
    }
  }

  return maturityByPlugin;
}

export function validateMaturityClaims(shared, maturityByPlugin) {
  // Keep each plugin's advertised maturity and version aligned.
  for (const [name, maturity] of [...maturityByPlugin.entries()].sort()) {
    const readmePath = path.join(ROOT, 'plugins', name, 'README.md');
    if (!isFile(readmePath)) {
      continue;
    }
    const claims = [...readText(readmePath).matchAll(MATURITY_CLAIM)];
    if (claims.length === 0) {
      fail(
        readmePath,
        'must state maturity and version as ' +
          "'<Experimental|Candidate|Stable> — <version>'",
      );
      continue;
    }
    const publishedVersion = (shared.get(name) ?? {}).version;
    for (const [, level, version] of claims) {
      if (level.toLowerCase() !== maturity) {
        fail(
          readmePath,
          `advertises maturity ${show(level)} but the acceptance record ` +
            `declares ${show(maturity)}`,
        );
      }
      if (typeof publishedVersion === 'string' && version !== publishedVersion) {
        fail(
          readmePath,
          `advertises version ${version} but the published version ` +
            `is ${publishedVersion}`,
        );
      }
    }
  }
}

export function validateJsonFiles() {
  for (const filePath of walkFiles(ROOT)) {
    if (!filePath.endsWith('.json')) {
      continue;
    }
    const data = loadJson(filePath);
    let raw;
    try {
      raw = readText(filePath);
    } catch {
      continue;
    }
    const nonEmpty = Array.isArray(data)
      ? data.length > 0
      : isObjectValue(data) && Object.keys(data).length > 0;
    if (nonEmpty && !raw.trim().includes('\n')) {
      fail(
        filePath,
        'JSON must be pretty-printed across multiple lines, not ' +
          'collapsed onto a single line',
      );
    }
  }
}

export function validateActionPins() {
  // Enforce the pinning rule documented in github-actions-standards.
  //
  // Any remote action may use a full commit SHA. An action published by
  // GitHub itself may instead use an exact release tag, which this repository
  // accepts because CI holds no secrets, write permissions, or deployment
  // authority.
  const workflows = path.join(ROOT, '.github', 'workflows');
  const workflowPaths = listDirectory(workflows)
    .filter(
      (entry) =>
        entry.isFile() &&
        (entry.name.endsWith('.yml') || entry.name.endsWith('.yaml')),
    )
    .map((entry) => path.join(workflows, entry.name))
    .sort();
  for (const workflowPath of workflowPaths) {
    const content = readText(workflowPath);
    for (const [, action, reference] of content.matchAll(ACTION_REFERENCE)) {
      if (FULL_SHA.test(reference)) {
        continue;
      }
      if (action.startsWith('./') || action.startsWith('docker://')) {
        continue;
      }
      const githubAuthored = GITHUB_AUTHORED_OWNERS.some((owner) =>
        action.startsWith(owner),
      );
      if (githubAuthored && EXACT_RELEASE_TAG.test(reference)) {
        continue;
      }
      if (githubAuthored) {
        fail(
          workflowPath,
          `${action} must use a full 40-character commit SHA or an ` +
            `exact release tag such as v1.2.3, not ${show(reference)}`,
        );
      } else {
        fail(
          workflowPath,
          `${action} must be pinned to a full 40-character commit SHA`,
        );
      }
    }
  }
}

export function validateRetiredBranding() {
  const retiredName = 'open' + 'rigor';
  for (const { path: entryPath, entry } of walk(ROOT)) {
    if (!entry.isFile() || entry.isSymbolicLink()) {
      continue;
    }
    let content;
    try {
      content = readText(entryPath);
    } catch {
      continue;
    }
    if (content.toLowerCase().includes(retiredName)) {
      fail(entryPath, 'contains the retired project name');
    }
  }
}

export function validateLinks() {
  for (const { path: entryPath, entry } of walk(ROOT)) {
    if (!entry.isSymbolicLink()) {
      continue;
    }
    if (path.isAbsolute(fs.readlinkSync(entryPath))) {
      fail(entryPath, 'link target must be repository-relative');
    }
    let resolved;
    try {
      resolved = fs.realpathSync(entryPath);
    } catch {
      fail(entryPath, 'link target does not exist');
      continue;
    }
    const relative = path.relative(ROOT, resolved);
    if (relative.startsWith('..') || path.isAbsolute(relative)) {
      fail(entryPath, 'link target escapes the repository');
    }
  }

  const redundantMarketplace = path.join(
    ROOT,
    '.github',
    'plugin',
    'marketplace.json',
  );
  if (fs.existsSync(redundantMarketplace) && !isSymlink(redundantMarketplace)) {
    fail(
      redundantMarketplace,
      'duplicate marketplace is prohibited; Copilot reuses .claude-plugin',
    );
  }
}

export function validateMarkdownLinks() {
  for (const filePath of walkFiles(ROOT)) {
    if (!filePath.endsWith('.md')) {
      continue;
    }
    const content = readText(filePath);
    for (const [, rawTarget] of content.matchAll(MARKDOWN_LINK)) {
      const trimmed = rawTarget.trim();
      if (!trimmed) {
        fail(filePath, 'markdown link target is blank');
        continue;
      }
      const target = trimmed.split(/\s+/)[0].replace(/^[<>]+|[<>]+$/g, '');
      if (
        !target ||
        target.startsWith('#') ||
        target.startsWith('http://') ||
        target.startsWith('https://') ||
        target.startsWith('mailto:')
      ) {
        continue;
      }
      let relativeTarget = target.split('#')[0];
      try {
        relativeTarget = decodeURIComponent(relativeTarget);
      } catch {
        // Keep the raw target when percent-decoding fails.
      }
      const resolved = path.resolve(path.dirname(filePath), relativeTarget);
      const relative = path.relative(ROOT, resolved);
      if (relative.startsWith('..') || path.isAbsolute(relative)) {
        fail(filePath, `local link escapes repository: ${target}`);
        continue;
      }
      if (!fs.existsSync(resolved)) {
        fail(filePath, `broken local link: ${target}`);
      }
    }
  }
}

export function main() {
  const catalogs = validateMarketplaces();
  const shared = catalogs.shared ?? new Map();
  validatePlugins(shared);
  validateSkillFrontmatter();
  const scenarioIndex = validateScenarios(shared);
  validateTestDirectories();
  const maturityByPlugin = validateAcceptance(shared, scenarioIndex);
  validateMaturityClaims(shared, maturityByPlugin);
  validateCatalogTables(shared, maturityByPlugin);
  validateJsonFiles();
  validateActionPins();
  validateRetiredBranding();
  validateLinks();
  validateMarkdownLinks();

  if (errors.length > 0) {
    process.stderr.write('Tashtit validation failed:\n');
    for (const error of errors) {
      process.stderr.write(`- ${error}\n`);
    }
    return 1;
  }

  process.stdout.write(
    `Tashtit validation passed (${shared.size} shared marketplace entries).\n`,
  );
  return 0;
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href
) {
  process.exit(main());
}
