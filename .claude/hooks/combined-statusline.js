#!/usr/bin/env node
/**
 * combined-statusline.js
 * OMC HUD + GSD statusline 통합 출력
 * 각 스크립트 출력을 " | "로 연결 (빈 출력은 제외)
 */
const { execSync } = require('child_process');
const { readFileSync } = require('fs');
const path = require('path');

// Claude Code가 파이프로 전달한 stdin(JSON)을 OMC HUD에 포워딩
let claudeStdin = '';
try {
  if (!process.stdin.isTTY) {
    claudeStdin = readFileSync(0, 'utf8'); // fd 0 = stdin
  }
} catch (_) {}

const parts = [];

// OMC HUD: stdin 포워딩 필요
try {
  const opts = { timeout: 3000, encoding: 'utf8' };
  if (claudeStdin) opts.input = claudeStdin;
  const out = execSync('node C:/Users/oaiskoo/.claude/hud/omc-hud.mjs', opts).trim();
  if (out) parts.push(out);
} catch (_) {}

// GSD statusline: stdin 불필요
try {
  const out = execSync(`node "${path.join(__dirname, 'gsd-statusline.js')}"`, { timeout: 3000, encoding: 'utf8' }).trim();
  if (out) parts.push(out);
} catch (_) {}

process.stdout.write(parts.join(' | ') + '\n');
