# Security Policy

## Supported builds
The trainer targets the currently supported **Modern Warfare 4** PC build on Steam/Battle.net. Offset tables for older builds live under `offsets/legacy/` and are not guaranteed to work.

## Reporting a vulnerability
If you find something that could get users banned unexpectedly, or a memory-safety bug in the injector path, open a private security advisory on this repo. Do **not** open a public issue for anything that could be weaponized before a patch lands.

## Threat model
- The trainer runs in user-mode only. No kernel drivers, no ring0.
- All memory reads/writes go through `pymem` handles opened with the minimum rights required.
- Overlay rendering never touches the game process directly; it draws in a separate transparent window.
- Config files are parsed with `tomllib` (strict) — no `eval`, no `exec` on user input.

## What this is not
This is an educational / hobbyist community project for offline and private-match testing. Running it in competitive matchmaking is against the game's ToS and will likely get your account banned. Use at your own risk.