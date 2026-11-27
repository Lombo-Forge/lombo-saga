# AGENTS.md

Notes for an AI coding agent (or a person) working in this repo. `CLAUDE.md` pulls this file in.


## What this is

LomboSaga keeps Kavita collections for book series filled, from rules you write. It is a small Python 3.12 program, standard library only (add a
dependency only when it clearly earns its place).

**Skeleton:** `core.py`, the client and the settings are still the template's example. Read
`docs/architecture.md` ("What it will do") before writing code.

## Layout

| Path | What |
|---|---|
| `src/lombo_saga/core.py` | The decisions. Pure functions: no network, disk or clock. Change the rules here. |
| `src/lombo_saga/jellyfin.py` | The Jellyfin client. Add calls here. |
| `src/lombo_saga/cli.py` | `doctor`, `plan`, `run`. The only place that does I/O and prints. |
| `src/lombo_saga/config.py` | Settings from `LOMBO_SAGA_*` environment variables. |
| `src/lombo_saga/notify.py` | Webhook alerts. |
| `tests/` | pytest, with a fake Jellyfin and webhook in `conftest.py`. |
| `scripts/leak-check.sh` | Fails when private or personal strings appear. CI runs it. |
| `docs/` | One topic per file, each with a `## Contents` list. |

## Rules

- **Keep `core.py` pure.** If a rule needs data, pass it in. That is what makes it testable.
- **Safe by default.** `DRY_RUN` defaults to true. `plan` must never change anything.
- **A new setting** goes in `config.py` (validated, message names the variable), `.env.example`
  (one comment line), and `compose.example.yaml` if it needs passing through.
- **Fail with a message, not a traceback.** Wrap outside calls; the loop survives one bad round.
- **Never put private details in the repo:** real hostnames, IPs, webhook URLs, API keys, local
  paths. Use `jellyfin.example.com`, `/mnt/media`, `changeme`. `scripts/leak-check.sh` enforces it;
  patterns live in `scripts/leak-patterns.txt`.
- Plain language in docs and messages. Call a PC used for encoding a "main PC with a discrete
  graphics card". Never call anything "official" or imply the Jellyfin project made it.
- The Lombo look (every icon has the Lombo L) is in `docs/branding.md`.

## Test

```sh
pip install -e '.[dev]'
pre-commit install            # once: runs the checks below before every commit
pre-commit run --all-files    # ruff lint + format, strict mypy, file hygiene, leak check
pytest -q --cov               # tests with coverage (the gate is `fail_under` in pyproject.toml)
```

These are the same checks CI runs (one config: `.pre-commit-config.yaml` and `pyproject.toml`), so what passes
locally passes there. The tooling is the same in every Lombo-Forge repo: ruff for lint and format, strict mypy,
pytest. Do not loosen a rule to make a change pass; fix the code, or say why in a comment next to a narrow `noqa`.

Without Python installed: `docker run --rm -v "$PWD:/w" -w /w python:3.12-slim sh -c "pip install -q -e '.[dev]' && pytest -q"`.
Tests use a fake server; before claiming a Jellyfin behaviour works, check it against a throwaway
Jellyfin container, never someone's real server.

## Working efficiently

- Optional tools that live in your own profile, not in this repo. Skip any you do not have.
- Graphify: build the code-only graph with `graphify update .` (never `/graphify .`, which costs tokens) and run
  `graphify query "<question>"` before grepping. `graphify-out/` is generated and gitignored; INFERRED edges are guesses.
- Ponytail: the smallest change that fully solves the task. Keep diffs small and focused.

## Skills (`.claude/skills/`)

- `install-into-my-stack`: help a user put the app into their setup and run `doctor`.
- `troubleshoot`: read `doctor` output and logs.
- `adapt`: change the rules, thresholds or settings safely.
