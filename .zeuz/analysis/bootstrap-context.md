# Bootstrap Context

Generated: 2026-05-23T18:20:30Z

## Source-of-truth guidance files

- `AGENTS.md`: **Not found**.
  - Evidence: `find . -maxdepth 4 -name AGENTS.md` returned no results.
- Root `CLAUDE.md`: **Not found**.
  - Evidence: `ls -la CLAUDE.md` reports `No such file or directory`.
- Service-local `CLAUDE.md` files: **Not found**.
  - Evidence: `find . -maxdepth 6 -name CLAUDE.md` returned no results.

## Documentation directory (`docs/`)
- `docs/` directory: **Not found**.
  - Evidence: `ls -la docs` reports `No such file or directory`.

## Repository boundaries (top-level)
Based on the directory layout in the current working directory:
- `Apps/`: application components (contains multiple subprojects; exact boundaries require deeper discovery later).
- `Framework/`: shared framework/runtime code.
- `Projects/`: project definitions/configuration.
- `Drivers/`: driver/integration layer code.
- `Installer/`: install/bootstrap scripts.
- `server/`: server-side entrypoints.
- `reporting/`: reporting artifacts.
- `tests/`: test suite.
- `node_cli.py`: top-level Python CLI entrypoint candidate.

## Canonical commands (best-effort evidence from filesystem)
No root-level build/test scripts were confirmed yet (Phase 1 will inventory config files like `pyproject.toml`, etc.). For now, only these were observed:
- `pyproject.toml` exists at repo root (`./pyproject.toml`).
- `node_cli.py` exists at repo root (`./node_cli.py`).
- `tests/` directory exists (`./tests`).

## Security/auth constraints
Not determinable from Phase 0 bootstrap alone; subsequent phases will inspect auth/config and any secret-handling patterns.
