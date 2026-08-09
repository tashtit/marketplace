// Unit tests for scripts/scan-secrets.js.
//
// Every synthetic credential below is assembled by concatenation so that
// this file, which the scanner itself scans on every `npm run validate`, never
// contains a contiguous string matching any rule.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { describe, it } from 'node:test';

import * as scanSecrets from '../../scripts/scan-secrets.js';
import * as support from './support.js';

const FAKE_SECRETS = {
  'AWS access key id': 'AKIA' + '0123456789ABCDEF',
  'GitHub token': 'ghp' + '_' + 'a'.repeat(36),
  'GitHub fine-grained token': 'github' + '_pat_' + 'a'.repeat(60),
  'Google API key': 'AIza' + '0'.repeat(35),
  'Slack token': 'xoxb' + '-' + '0'.repeat(12),
  'Stripe live key': 'sk' + '_live_' + 'a'.repeat(24),
  'npm token': 'npm' + '_' + 'a'.repeat(36),
  'private key block': '-----BEGIN RSA' + ' PRIVATE' + ' KEY-----',
  'OpenAI key': 'sk-' + 'a'.repeat(20) + 'T3Blb' + 'kFJ' + 'a'.repeat(20),
};

function scan(t, content, fileName = 'fixture.txt') {
  const root = support.tempRoot(t);
  const filePath = path.join(root, fileName);
  support.writeText(filePath, content);
  return support.withRoot(scanSecrets, root, () => {
    scanSecrets.scanFile(filePath);
    return [...scanSecrets.findings];
  });
}

describe('scanFile rules', () => {
  it('matches each synthetic credential with its label', (t) => {
    for (const [label, value] of Object.entries(FAKE_SECRETS)) {
      const findings = scan(t, `token = ${value}\n`);
      assert.equal(findings.length, 1, `${label}: ${JSON.stringify(findings)}`);
      assert.ok(
        findings[0].includes(`possible ${label}`),
        `${label}: ${findings[0]}`,
      );
    }
  });

  it('never echoes the matched value', (t) => {
    const value = FAKE_SECRETS['AWS access key id'];
    const findings = scan(t, `token = ${value}\n`);
    assert.ok(!findings[0].includes(value));
  });

  it('includes the path and line number', (t) => {
    const value = FAKE_SECRETS['GitHub token'];
    const findings = scan(t, `line one\ntoken = ${value}\n`);
    assert.match(findings[0], /fixture\.txt:2:/);
  });
});

describe('scanFile non-findings', () => {
  it('ignores workflow secret references', (t) => {
    assert.deepEqual(scan(t, 'password: ${{ secrets.NPM_TOKEN }}\n'), []);
  });

  it('ignores prose about credentials', (t) => {
    assert.deepEqual(
      scan(t, 'Store the API key in your secret manager.\n'),
      [],
    );
  });

  it('skips a line with the allowlist pragma', (t) => {
    const value = FAKE_SECRETS['AWS access key id'];
    const marker = scanSecrets.ALLOWLIST_MARKER;
    assert.deepEqual(scan(t, `${value}  # ${marker}\n`), []);
  });

  it('skips oversized files', (t) => {
    const value = FAKE_SECRETS['AWS access key id'];
    const padding = 'a'.repeat(scanSecrets.MAX_BYTES);
    assert.deepEqual(scan(t, `${padding}\ntoken = ${value}\n`), []);
  });

  it('skips undecodable files', (t) => {
    const root = support.tempRoot(t);
    const filePath = path.join(root, 'binary.bin');
    // Invalid UTF-8 bytes force the strict decoder to reject the file.
    fs.writeFileSync(filePath, Buffer.from([0x00, 0xff, 0xfe, 0x80, 0x80]));
    const findings = support.withRoot(scanSecrets, root, () => {
      scanSecrets.scanFile(filePath);
      return [...scanSecrets.findings];
    });
    assert.deepEqual(findings, []);
  });
});

describe('main', () => {
  function runMain(root) {
    return support.withRoot(scanSecrets, root, () =>
      support.captureOutput(() => scanSecrets.main()),
    );
  }

  it('passes on a clean tree', (t) => {
    const root = support.tempRoot(t);
    support.writeText(path.join(root, 'README.md'), 'No credentials here.\n');
    const { result, stdout } = runMain(root);
    assert.equal(result, 0);
    assert.match(stdout, /passed/);
  });

  it('fails with a located finding for a planted credential', (t) => {
    const root = support.tempRoot(t);
    const value = FAKE_SECRETS['Slack token'];
    support.writeText(
      path.join(root, 'config', 'app.yml'),
      `slack: ${value}\n`,
    );
    const { result, stderr } = runMain(root);
    assert.equal(result, 1);
    assert.match(stderr, /config\/app\.yml:1: possible Slack token/);
    assert.ok(!stderr.includes(value));
  });

  it('does not scan ignored directories', (t) => {
    const root = support.tempRoot(t);
    const value = FAKE_SECRETS['GitHub token'];
    support.writeText(
      path.join(root, 'node_modules', 'dep', 'index.js'),
      `${value}\n`,
    );
    const { result } = runMain(root);
    assert.equal(result, 0);
  });
});

