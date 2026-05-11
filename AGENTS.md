# Codex Pet Agent Notes

This repository is a **Codex custom pet packaging project**, not a standalone desktop app.

## What This Repo Owns

- source pet images under `assets/`
- docs describing pet asset expectations
- scripts that assemble a Codex-compatible pet package

## What This Repo Does Not Own

- no Tauri host app
- no React frontend
- no local dev server workflow
- no desktop window behavior

If a change request assumes this repo is a runnable app, correct that assumption first.

## Important Structure

- `assets/`: source images used to derive pet frames or atlas content
- `docs/asset-spec.md`: notes on required states, naming, and packaging expectations
- `scripts/pet_package.py`: build/install/reinstall core logic
- `scripts/pet.mjs`: npm entrypoint that resolves a usable Python runtime

## Expected Output

The final deliverable for Codex is:

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
├── pet.json
└── spritesheet.webp
```

The spritesheet contract is fixed:

- `1536x1872`
- `8 columns x 9 rows`
- `192x208` per cell
- transparent background
- unused cells fully transparent

## Default Workflow

1. update or replace source art in `assets/`
2. adjust packaging logic if the framing/layout changes
3. run `npm run pet -- build` to produce a package artifact
4. run `npm run pet -- install` or `npm run pet -- reinstall`
5. refresh custom pets from Codex settings

## Common Gotchas

- current source PNGs may not have transparent backgrounds
- a generic sprite packer is not enough by itself; Codex pets require a fixed atlas layout
- if a user asks for animation quality improvements, that usually means changing source frames or atlas composition rather than app code
