# TASK-002: Bootstrap repository context

## Metadata
- **Phase**: 0
- **Status**: DONE
- **Assigned To**: main
- **Started**: 2026-05-23T18:20:05Z
- **Completed**: 2026-05-23T18:20:40Z
- **Duration**: 0m
- **Depends On**: [TASK-001]
- **Blocks**: none

## Description
Reads source-of-truth guidance files required by the CLAUDE analysis prompt: root `AGENTS.md` (if present), root `CLAUDE.md` (if present), and any service-local `CLAUDE.md` files (if present). Also inventories existing documentation under `docs/` (if present). If files are missing, records explicit evidence of absence.

## Acceptance Criteria
- [ ] `.zeuz/analysis/bootstrap-context.md` exists
- [ ] Evidence-based notes include whether `AGENTS.md` and `CLAUDE.md` exist or are missing
- [ ] Absence of `docs/` is recorded if `docs/` directory does not exist

## Notes
Bootstrapping only captured evidence about guidance/document directories; deeper command/runtime inventory is deferred to Phase 1.

## Checklist
- [ ] Find `AGENTS.md` and `CLAUDE.md`
- [ ] Check for `docs/` directory and existing docs
- [ ] Write `.zeuz/analysis/bootstrap-context.md`

## Output
- `.zeuz/analysis/bootstrap-context.md`

## Test Requirements
- N/A (documentation-only bootstrap)
