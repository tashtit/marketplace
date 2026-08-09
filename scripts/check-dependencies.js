#!/usr/bin/env node
// Enforce the dependency intake gate without third-party dependencies.
//
// Every externally sourced dependency this repository declares — npm packages
// in a package.json, and GitHub Actions or reusable workflows referenced by
// `uses:` — must have a reviewed record in dependency-registry.json. The
// record is the committed evidence required by docs/dependency-policy.md:
// purpose, alternatives, adoption, provenance, license, source, and who
// approved it when.
//
// Two gates, deliberately asymmetric:
//
// - Adding a dependency is a hard gate. A declared dependency with no record,
//   or a record for a dependency nothing declares, fails the check.
// - Updating a dependency is a soft gate. A recorded version that no longer
//   matches the manifest is a warning, so a version bump is visible in review
//   and cleared by re-recording it, without blocking a security update.
//
// The check reads committed files only. It resolves nothing over the network
// and therefore cannot judge whether the recorded evidence is true; that is
// the reviewer's job.

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

let ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export const REGISTRY_FILE = 'dependency-registry.json';
export const POLICY_FILE = 'docs/dependency-policy.md';

// Mirrors scripts/validate.js: version control, editor state, and installed
// dependencies never carry declared repository content.
const IGNORED_DIRECTORIES = new Set(['.git', '.idea', 'node_modules']);

const MANIFEST_SECTIONS = [
  'dependencies',
  'devDependencies',
  'optionalDependencies',
  'peerDependencies',
];

// A step may open with "- uses:" or carry "uses:" on its own line; both forms
// reference an external action and both need a record.
const ACTION_REFERENCE = /^\s*(?:-\s+)?uses:\s+([^@\s]+)@([^\s#]+)/gm;
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

export const ECOSYSTEMS = new Set(['npm', 'github-actions']);

// Each field answers one check of the intake gate. Dropping one turns the
// record back into an assertion that the dependency was reviewed.
const RECORD_FIELDS = new Set([
  'ecosystem',
  'name',
  'version',
  'purpose',
  'alternatives',
  'adoption',
  'provenance',
  'license',
  'source',
  'reviewed_by',
  'reviewed_on',
]);
const LIST_FIELDS = new Set(['alternatives']);

export const errors = [];
export const warnings = [];

const utf8 = new TextDecoder('utf-8', { fatal: true });

export function setRoot(newRoot) {
  const previous = ROOT;
  ROOT = newRoot;
  return previous;
}

function display(filePath) {
  const relative = path.relative(ROOT, filePath);
  return relative === '' ||
    relative.startsWith('..') ||
    path.isAbsolute(relative)
    ? String(filePath)
    : relative;
}

function fail(filePath, message) {
  errors.push(`${display(filePath)}: ${message}`);
}

function warn(filePath, message) {
  warnings.push(`${display(filePath)}: ${message}`);
}

function readText(filePath) {
  return utf8.decode(fs.readFileSync(filePath));
}

const isObjectValue = (value) =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const sorted = (values) => [...values].sort();

// A dependency's identity across manifests and records.
const key = (ecosystem, name) => `${ecosystem} ${name}`;

function* walkFiles(dirPath) {
  let entries;
  try {
    entries = fs.readdirSync(dirPath, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries.sort((a, b) =>
    a.name < b.name ? -1 : a.name > b.name ? 1 : 0,
  )) {
    if (IGNORED_DIRECTORIES.has(entry.name)) {
      continue;
    }
    const entryPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      yield* walkFiles(entryPath);
    } else if (entry.isFile() && !entry.isSymbolicLink()) {
      yield entryPath;
    }
  }
}

function record(declared, ecosystem, name, version, source) {
  // Index one declaration site. A dependency declared more than once keeps
  // every declared version, so a partial update cannot hide behind a match.
  const id = key(ecosystem, name);
  if (!declared.has(id)) {
    declared.set(id, { ecosystem, name, versions: new Map() });
  }
  const versions = declared.get(id).versions;
  if (!versions.has(version)) {
    versions.set(version, []);
  }
  versions.get(version).push(display(source));
}

export function collectNpmDependencies(declared) {
  for (const filePath of walkFiles(ROOT)) {
    if (path.basename(filePath) !== 'package.json') {
      continue;
    }
    let manifest;
    try {
      manifest = JSON.parse(readText(filePath));
    } catch (error) {
      fail(filePath, `invalid JSON: ${error.message}`);
      continue;
    }
    if (!isObjectValue(manifest)) {
      continue;
    }
    for (const section of MANIFEST_SECTIONS) {
      const entries = manifest[section];
      if (!isObjectValue(entries)) {
        continue;
      }
      for (const [name, version] of Object.entries(entries)) {
        if (typeof version !== 'string') {
          fail(filePath, `${section}.${name} must declare a string version`);
          continue;
        }
        record(declared, 'npm', name, version, filePath);
      }
    }
  }
}

export function collectActionDependencies(declared) {
  const roots = [
    path.join(ROOT, '.github', 'workflows'),
    path.join(ROOT, '.github', 'actions'),
  ];
  for (const start of roots) {
    for (const filePath of walkFiles(start)) {
      if (!/\.ya?ml$/.test(filePath)) {
        continue;
      }
      let content;
      try {
        content = readText(filePath);
      } catch {
        continue;
      }
      for (const [, reference, version] of content.matchAll(
        ACTION_REFERENCE,
      )) {
        // A local action or a container image is not an external repository
        // dependency reviewed under this gate.
        if (reference.startsWith('./') || reference.startsWith('docker://')) {
          continue;
        }
        // The trust unit is the repository that publishes the action, not the
        // subdirectory or reusable workflow path inside it.
        const name = reference.split('/').slice(0, 2).join('/');
        record(declared, 'github-actions', name, version, filePath);
      }
    }
  }
}

export function collectDeclared() {
  const declared = new Map();
  collectNpmDependencies(declared);
  collectActionDependencies(declared);
  return declared;
}

function validateRecord(registryPath, entry, position) {
  // Validate one record's shape and return its identity, or null when the
  // record is too malformed to match against a manifest.
  const label = `dependencies[${position}]`;
  if (!isObjectValue(entry)) {
    fail(registryPath, `${label} must be an object`);
    return null;
  }

  const fields = new Set(Object.keys(entry));
  const unknown = sorted([...fields].filter((f) => !RECORD_FIELDS.has(f)));
  if (unknown.length > 0) {
    fail(registryPath, `${label} has unsupported fields: ${unknown.join(', ')}`);
  }
  const missing = sorted([...RECORD_FIELDS].filter((f) => !fields.has(f)));
  if (missing.length > 0) {
    fail(registryPath, `${label} is missing fields: ${missing.join(', ')}`);
    return null;
  }

  for (const field of RECORD_FIELDS) {
    const value = entry[field];
    if (LIST_FIELDS.has(field)) {
      if (
        !Array.isArray(value) ||
        value.length === 0 ||
        !value.every((item) => typeof item === 'string' && item.trim())
      ) {
        fail(
          registryPath,
          `${label}.${field} must be a non-empty array of non-empty strings`,
        );
      }
      continue;
    }
    if (typeof value !== 'string' || !value.trim()) {
      fail(registryPath, `${label}.${field} must be a non-empty string`);
    }
  }

  if (!ECOSYSTEMS.has(entry.ecosystem)) {
    fail(
      registryPath,
      `${label}.ecosystem must be one of ${sorted(ECOSYSTEMS).join(', ')}`,
    );
    return null;
  }
  if (typeof entry.source !== 'string' || !entry.source.startsWith('https://')) {
    fail(registryPath, `${label}.source must be an https URL of the source repository`);
  }
  if (typeof entry.reviewed_on !== 'string' || !ISO_DATE.test(entry.reviewed_on)) {
    fail(registryPath, `${label}.reviewed_on must be an ISO 8601 date`);
  }
  if (typeof entry.name !== 'string' || !entry.name.trim()) {
    return null;
  }
  if (typeof entry.version !== 'string' || !entry.version.trim()) {
    return null;
  }
  return entry;
}

export function loadRegistry() {
  // Parse and shape-check the registry, returning records by identity.
  const registryPath = path.join(ROOT, REGISTRY_FILE);
  const records = new Map();
  let raw;
  try {
    raw = readText(registryPath);
  } catch (error) {
    if (error.code === 'ENOENT') {
      fail(
        registryPath,
        'dependency registry is missing; every declared dependency needs a ' +
          `reviewed record (see ${POLICY_FILE})`,
      );
      return records;
    }
    throw error;
  }

  let data;
  try {
    data = JSON.parse(raw);
  } catch (error) {
    fail(registryPath, `invalid JSON: ${error.message}`);
    return records;
  }
  if (!isObjectValue(data) || !Array.isArray(data.dependencies)) {
    fail(registryPath, 'registry must be an object with a dependencies array');
    return records;
  }

  const order = [];
  data.dependencies.forEach((entry, position) => {
    const valid = validateRecord(registryPath, entry, position);
    if (!valid) {
      return;
    }
    const id = key(valid.ecosystem, valid.name);
    order.push(id);
    if (records.has(id)) {
      fail(registryPath, `duplicate record for ${id}`);
      return;
    }
    records.set(id, valid);
  });

  if (order.join('\n') !== sorted(order).join('\n')) {
    fail(registryPath, 'records must be sorted by ecosystem then name');
  }
  return records;
}

export function compare(declared, records) {
  const registryPath = path.join(ROOT, REGISTRY_FILE);

  for (const [id, entry] of [...declared.entries()].sort()) {
    const sites = sorted(
      new Set([...entry.versions.values()].flat()),
    ).join(', ');
    const found = records.get(id);
    if (!found) {
      fail(
        registryPath,
        `${entry.name} (${entry.ecosystem}) is declared in ${sites} with no ` +
          `reviewed dependency record; add one before the dependency lands ` +
          `(see ${POLICY_FILE})`,
      );
      continue;
    }
    if (!entry.versions.has(found.version)) {
      const declaredVersions = sorted(entry.versions.keys()).join(', ');
      warn(
        registryPath,
        `${entry.name} (${entry.ecosystem}) is recorded at ${found.version} ` +
          `but ${sites} declares ${declaredVersions}; review the change and ` +
          'update the record in the same pull request',
      );
    }
  }

  for (const id of sorted(records.keys())) {
    if (!declared.has(id)) {
      const entry = records.get(id);
      fail(
        registryPath,
        `${entry.name} (${entry.ecosystem}) has a record but is not declared ` +
          'by any manifest or workflow; remove the stale record',
      );
    }
  }
}

export function main() {
  errors.splice(0);
  warnings.splice(0);

  const declared = collectDeclared();
  const records = loadRegistry();
  compare(declared, records);

  for (const warning of warnings) {
    process.stdout.write(`warning: ${warning}\n`);
  }

  if (errors.length > 0) {
    process.stderr.write('Tashtit dependency check failed:\n');
    for (const error of errors) {
      process.stderr.write(`- ${error}\n`);
    }
    process.stderr.write(
      `\nAdding a dependency is a blocking gate. Record the evidence in ` +
        `${REGISTRY_FILE} as described in ${POLICY_FILE}.\n`,
    );
    return 1;
  }

  const pending =
    warnings.length === 1 ? '1 pending update review' : `${warnings.length} pending update reviews`;
  process.stdout.write(
    `Tashtit dependency check passed (${declared.size} declared ` +
      `dependencies, ${pending}).\n`,
  );
  return 0;
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href
) {
  process.exit(main());
}
