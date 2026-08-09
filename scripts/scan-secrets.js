#!/usr/bin/env node
// Scan the repository for committed secrets without third-party dependencies.
//
// The scanner is deliberately conservative. Tashtit documentation discusses
// tokens, secret names, and workflow expressions constantly, so only patterns
// that identify real key *material* are reported. A reference such as
// `${{ secrets.NPM_TOKEN }}` or prose about an API key is never a finding.
//
// Add `pragma: allowlist secret` on the same line to accept a deliberate
// fixture.

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

let ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// Mirrors scripts/validate.js: version control, editor state, and installed
// dependencies never carry repository content.
const IGNORED_DIRECTORIES = new Set(['.git', '.idea', 'node_modules']);
export const ALLOWLIST_MARKER = 'pragma: allowlist secret';
export const MAX_BYTES = 2_000_000;

// Each rule matches issued credential material, not a name or a reference.
const RULES = [
  ['private key block', /-----BEGIN(?: [A-Z0-9]+)* PRIVATE KEY-----/],
  ['AWS access key id', /\b(?:AKIA|ASIA)[0-9A-Z]{16}\b/],
  ['GitHub token', /\bgh[pousr]_[A-Za-z0-9]{36,}\b/],
  ['GitHub fine-grained token', /\bgithub_pat_[A-Za-z0-9_]{60,}\b/],
  ['Google API key', /\bAIza[0-9A-Za-z_-]{35}\b/],
  ['Slack token', /\bxox[abprs]-[0-9A-Za-z-]{10,}\b/],
  ['Stripe live key', /\bsk_live_[0-9A-Za-z]{24,}\b/],
  ['npm token', /\bnpm_[A-Za-z0-9]{36}\b/],
  ['PyPI token', /\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}\b/],
  ['OpenAI key', /\bsk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}\b/],
];

export const findings = [];

// Decodes strictly so binary content is skipped rather than scanned as
// replacement characters.
const utf8 = new TextDecoder('utf-8', { fatal: true });

export function setRoot(newRoot) {
  const previous = ROOT;
  ROOT = newRoot;
  return previous;
}

function report(filePath, lineNumber, label) {
  // Record a finding without echoing the matched secret value.
  const relative = path.relative(ROOT, filePath);
  const display =
    relative === '' || relative.startsWith('..') || path.isAbsolute(relative)
      ? String(filePath)
      : relative;
  findings.push(`${display}:${lineNumber}: possible ${label}`);
}

function splitLines(text) {
  const lines = text.split(/\r\n|\r|\n/);
  if (lines.length > 0 && lines[lines.length - 1] === '') {
    lines.pop();
  }
  return lines;
}

export function scanFile(filePath) {
  let content;
  try {
    if (fs.statSync(filePath).size > MAX_BYTES) {
      return;
    }
    content = utf8.decode(fs.readFileSync(filePath));
  } catch {
    return;
  }

  splitLines(content).forEach((line, index) => {
    if (line.includes(ALLOWLIST_MARKER)) {
      return;
    }
    for (const [label, pattern] of RULES) {
      if (pattern.test(line)) {
        report(filePath, index + 1, label);
      }
    }
  });
}

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

export function main() {
  for (const filePath of walkFiles(ROOT)) {
    scanFile(filePath);
  }

  if (findings.length > 0) {
    process.stderr.write('Tashtit secret scan failed:\n');
    for (const finding of findings) {
      process.stderr.write(`- ${finding}\n`);
    }
    process.stderr.write(
      '\nRotate any real credential before removing it from history. ' +
        `Append '${ALLOWLIST_MARKER}' to accept a deliberate fixture.\n`,
    );
    return 1;
  }

  process.stdout.write('Tashtit secret scan passed (no credential material found).\n');
  return 0;
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href
) {
  process.exit(main());
}
