import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';

const repoRoot = process.cwd();

function pythonCandidates() {
  const home = process.env.HOME || '';
  return [
    process.env.CODEX_PYTHON,
    path.join(home, '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'),
    'python3',
    'python'
  ].filter(Boolean);
}

function canRunPython(candidate) {
  if (candidate.includes('/') && !existsSync(candidate)) {
    return false;
  }

  const result = spawnSync(
    candidate,
    ['-c', 'import PIL; import sys; sys.stdout.write(PIL.__version__)'],
    { stdio: 'ignore', env: process.env }
  );
  return result.status === 0;
}

function resolvePython() {
  for (const candidate of pythonCandidates()) {
    if (canRunPython(candidate)) {
      return candidate;
    }
  }

  throw new Error(
    'No usable Python with Pillow found. Set CODEX_PYTHON or install Pillow into your python3 environment.'
  );
}

const action = process.argv[2] || 'reinstall';
const extraArgs = process.argv.slice(3);
const allowed = new Set(['build', 'install', 'reinstall']);
if (!allowed.has(action)) {
  console.error(`Unknown action: ${action}`);
  console.error('Use one of: build, install, reinstall');
  process.exit(1);
}

const python = resolvePython();
const result = spawnSync(
  python,
  ['scripts/pet_package.py', action, ...extraArgs],
  {
    cwd: repoRoot,
    stdio: 'inherit',
    env: process.env
  }
);

process.exit(result.status ?? 1);
