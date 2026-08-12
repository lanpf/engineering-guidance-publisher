---
name: update-engineering-standards
description: Reconcile Git changes in standards/COMMON.md and standards/SERVICE.md with the engineering guidance catalog, generated Skill references, and release metadata. Use after editing either standards document, when adding, changing, moving, or retiring rules, or when preparing a new engineering guidance release.
---

# Update Engineering Standards

Keep the human-authored standards documents and the publishable rule catalog semantically aligned.

## Locate inputs

1. Locate the `engineering-guidance-publisher` repository containing `standards/COMMON.md`, `standards/SERVICE.md`, and `catalog.json`.
2. Treat `COMMON.md` and `SERVICE.md` as the human-authored policy sources and `catalog.json` as the structured publishing source.
3. Read the repository `AGENTS.md` and `README.md` before editing.

## Inspect the change

1. Use Git status and diff from this repository for `standards/COMMON.md` and `standards/SERVICE.md`.
2. Compare against the user-specified base revision; when none is supplied, use the current Git diff against `HEAD`, including staged and unstaged changes.
3. If the documents are not yet tracked or have no usable Git baseline, stop and ask for a base revision or initial commit. Do not infer a historical diff from file timestamps.
4. Classify every semantic change as added, tightened, relaxed, moved, reworded without semantic change, or retired.

## Reconcile the catalog

1. Map each persistent rule to the narrowest matching Skill reference and section.
2. Reuse an existing rule ID only when its semantic identity remains the same. Add a stable new ID for a new constraint.
3. Never reuse a retired ID for another meaning. Remove a rule from the active catalog only when the source documents intentionally retire it.
4. Keep concise catalog text semantically equivalent to the source documents; split independent constraints into separate rules.
5. Update the matching Skill blueprint only when the workflow or reference-routing behavior changes. Do not duplicate detailed rule text in `SKILL.md`.
6. Keep every catalog reference's `<path>#<heading>` source traceable to the standards document that owns it.
7. Increment the semantic version in `catalog.json`, `pyproject.toml`, and `src/engineering_guidance/__init__.py`. Use a patch increment unless the user requests or the compatibility impact requires a larger increment.

## Verify and report

Run from `engineering-guidance-publisher`:

```bash
PYTHONPATH=src python3 -m engineering_guidance validate
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m engineering_guidance build --output dist
```

Validate every generated Skill under `dist/skills` with the available Skill validator. Report:

- source-document changes mapped to rule IDs;
- added, changed, and retired rule IDs;
- version change;
- blueprint changes;
- verification commands and results.
