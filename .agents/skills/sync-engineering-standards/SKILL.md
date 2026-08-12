---
name: sync-engineering-standards
description: Validate, build, and synchronize the current engineering standards into one named project in the cloud workspace. Use when installing or upgrading generated AGENTS.md guidance and managed Skills for a project; the request must provide the project name.
---

# Sync Engineering Standards

Synchronize the publisher's current catalog into exactly one consumer project.

## Resolve the target

1. Require one project name from the user, for example `user-auth` or `user-person`.
2. Accept only a single directory name, not a path: reject `/`, `..`, `~`, glob characters, or an absolute path.
3. Locate the cloud workspace root containing both `engineering-guidance-publisher` and the named project.
4. Resolve the target as `<cloud-root>/<project-name>` and confirm that it is an existing directory.
5. Read the publisher's `AGENTS.md` and `README.md`, the target `AGENTS.md` when present, and the target's existing `.engineering-standards/standards.lock.json` when present.

## Validate and synchronize

Run from `engineering-guidance-publisher`:

```bash
PYTHONPATH=src python3 -m engineering_guidance validate
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m engineering_guidance build --output dist
PYTHONPATH=src python3 -m engineering_guidance sync --target ../<project-name>
```

Do not use `--force` unless the user explicitly authorizes adopting colliding unmanaged Skill directories. Do not sync multiple projects from one invocation.
Synchronize only Skills whose catalog scope is `consumer`; never install publisher maintenance Skills into the target project.

## Verify the consumer

1. Confirm the managed block in the target `AGENTS.md` reports the current catalog version.
2. Confirm `.engineering-standards/standards.lock.json` contains the same version and all catalog-managed Skills.
3. Confirm project-specific content outside the managed `AGENTS.md` block remains unchanged.
4. Report the project name, previous and current versions, installed Skill names, and verification results.
