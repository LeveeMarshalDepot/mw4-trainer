# Contributing to mw4-trainer

Thanks for wanting to help out with the MW4 trainer. A few ground rules so PRs land smoothly.

## Scope
This repo is the **Call of Duty: Modern Warfare 4 Trainer** — a Windows desktop trainer with overlay, ESP, aimbot, recoil control and memory-patch jobs. Keep PRs inside that scope.

## Dev setup
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.app
```

## Branch naming
- `feat/esp-<feature>` for ESP work
- `feat/aimbot-<feature>` for aim assist work
- `fix/offset-<build>` when the game patch shifts offsets
- `chore/<thing>` for housekeeping

## Offsets & signatures
Any new offsets must go through `src/offsets/resolver.py` and be verified against the currently supported game build. Do not hardcode raw addresses in handlers or processors — everything flows through the resolver pipeline.

## Style
- Python 3.11, type hints everywhere, `ruff` + `black` defaults.
- No blocking calls on the overlay thread — push work onto the job queue.
- Every new processor needs a stub test under `tests/`.

## Reporting issues
Attach `logs/trainer.log` and, if it's a crash, the dump from `dumps/`. Never paste raw offset tables from protected builds.