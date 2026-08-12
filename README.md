# Engineering Guidance Publisher

This repository turns versioned engineering standards into deterministic Skills and managed guidance for coding agents. `standards/COMMON.md` and `standards/SERVICE.md` are the human-authored policy sources; `catalog.json` is their structured publishing representation and the direct source of generated `AGENTS.md` guidance and Skill references.

## Commands

```bash
python3 -m engineering_guidance validate
python3 -m engineering_guidance build
python3 -m engineering_guidance install-publisher-skills
python3 -m engineering_guidance sync --target ../user-auth
python3 -m unittest discover -s tests
```

The generated `$update-engineering-standards` Skill reconciles Git changes in
`standards/COMMON.md` and `standards/SERVICE.md` with the catalog. The generated
`$sync-engineering-standards` Skill accepts a sibling project name and runs the
validated synchronization workflow for that project.

Skills have an explicit publication scope:

- `consumer` Skills are rendered into consumer `AGENTS.md`, installed by `sync`, and recorded in the consumer lock.
- `publisher` Skills are installed only into this repository by `install-publisher-skills`; they are not distributed to business projects.

For local development without installing the package, set `PYTHONPATH=src` before the command.

## Release model

1. Change `standards/COMMON.md` or `standards/SERVICE.md`, then reconcile the semantic changes into `catalog.json`; when workflow behavior changes, also update the matching Skill blueprint.
2. Increment the version in `catalog.json`, `pyproject.toml`, and `src/engineering_guidance/__init__.py`.
3. Run validation, tests, and a clean build.
4. Publish an immutable Git tag matching the catalog version.
5. Consumer repositories synchronize the tagged version and commit the resulting PR.

Generated Skill directories are managed content. Project-specific guidance belongs outside the managed block in the consumer repository's `AGENTS.md`.

For consumer compatibility, synchronization continues to recognize the existing
`engineering-standards` managed-block markers and `.engineering-standards/standards.lock.json`.
These are wire-format identifiers, not the publisher project name.
