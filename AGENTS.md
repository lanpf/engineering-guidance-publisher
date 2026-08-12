# Repository Guidance

This repository publishes shared engineering guidance as generated Skills and managed agent instructions.

## Source ownership

- `standards/COMMON.md` and `standards/SERVICE.md` are the human-authored policy sources. `catalog.json` is their structured publishing representation and is the direct source of versions, persistent rule IDs, Skill routing, and generated detailed rule text.
- `blueprints/skills/*/SKILL.md` owns workflow instructions and progressive reference routing only.
- `blueprints/skills/*/agents/openai.yaml` owns Skill UI metadata.
- `dist/` is generated and must never be edited by hand or committed.
- Do not duplicate detailed rules in this file or in Skill blueprints.

## Change rules

- Keep every rule ID stable after publication. Never reuse an ID for a different meaning.
- Add a new rule ID for a new constraint. Preserve removed IDs in release history rather than reassigning them.
- Keep Skill names stable unless a migration explicitly handles the rename.
- Declare every Skill as `consumer` or `publisher`; consumer synchronization must never install publisher-only maintenance Skills.
- Every catalog reference declares a `source` in `<document>#<heading>` form and must remain traceable to an existing heading in `standards/COMMON.md` or `standards/SERVICE.md`.
- Increment the semantic version in `catalog.json`, `pyproject.toml`, and `src/engineering_guidance/__init__.py` for every published change.
- Published Git tags are immutable.

## Verification

Run from the repository root:

```bash
PYTHONPATH=src python3 -m engineering_guidance validate
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m engineering_guidance build --output dist
PYTHONPATH=src python3 -m engineering_guidance install-publisher-skills
```

Validate every generated Skill with the Skill validator before release.
