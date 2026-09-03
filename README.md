# Engineering Guidance Publisher

This repository turns versioned engineering best practices into deterministic Skills and managed guidance for coding agents. The `standards/bp_*.md` series contains the human-authored policy sources; `catalog.json` is their structured publishing representation and the direct source of generated `AGENTS.md` guidance and Skill references.

## Commands

```bash
python3 -m engineering_guidance validate
python3 -m engineering_guidance build
python3 -m engineering_guidance install-publisher-skills
python3 -m engineering_guidance sync --target ../user-auth
python3 -m unittest discover -s tests
```

The generated `$update-standards` Skill reconciles Git changes in
all Markdown documents under `standards/` with the catalog. The generated
`$sync-standards` Skill accepts a sibling project name and runs the
validated synchronization workflow for that project.

Skills have an explicit publication scope:

- `consumer` Skills are rendered into consumer `AGENTS.md`, installed by `sync`, and recorded in the consumer lock.
- `publisher` Skills are installed only into this repository by `install-publisher-skills`; they are not distributed to business projects.

The 2.1 consumer Skill set separates daily development guidance from phase-specific and capability-specific workflows:

- `develop-service` owns the shared development guidance for dependencies, layering, naming, Java language, common tools, logging, error codes, persistence, distributed IDs, and unit testing.
- `develop-distributed` and `develop-compensation` own distributed lock/message and compensation workflows.
- `test-integration` owns smoke-phase integration testing; during development only unit tests are allowed.
- `refactor-layered-service` coordinates the other consumer Skills and requires plan confirmation before changing consumer code.

Version 2.1 replaces `develop-java-code`, `manage-maven-dependencies`, `develop-layered-service`, `manage-service-error-codes`, `develop-service-persistence`, and `test-service`. A normal synchronization removes those retired managed Skill directories and installs their replacements.

Version 2.2 renames `develop-service-code` to `develop-service`, `develop-distributed-capabilities` to `develop-distributed`, `develop-compensation-workflows` to `develop-compensation`, `update-engineering-standards` to `update-standards`, and `sync-engineering-standards` to `sync-standards`. A normal synchronization or publisher-skill install removes the retired directories and installs the renamed replacements. The same release shortens standards document names: `bp_project_documentation.md` to `bp_docs.md`, `bp_distributed_id.md` to `bp_ids.md`, `bp_distributed_lock.md` to `bp_lock.md`, `bp_distributed_messaging.md` to `bp_messaging.md`, `bp_business_compensation.md` to `bp_compensation.md`, and `bp_integration_testing.md` to `bp_integration.md`.

For local development without installing the package, set `PYTHONPATH=src` before the command.

## Release model

1. Change one or more `standards/bp_*.md` documents, then reconcile semantic changes into `catalog.json`; when workflow behavior changes, also update the matching Skill blueprint.
2. Increment the version in `catalog.json`, `pyproject.toml`, and `src/engineering_guidance/__init__.py`.
3. Run validation, tests, and a clean build.
4. Publish an immutable Git tag matching the catalog version.
5. Consumer repositories synchronize the tagged version and commit the resulting PR.

Generated Skill directories are managed content. Project-specific guidance belongs outside the managed block in the consumer repository's `AGENTS.md`.

For consumer compatibility, synchronization continues to recognize the existing
`engineering-standards` managed-block markers and `.engineering-standards/standards.lock.json`.
These are wire-format identifiers, not the publisher project name.
