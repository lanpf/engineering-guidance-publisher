---
name: update-engineering-standards
description: Reconcile Git changes in Markdown standards documents with the engineering guidance catalog, generated Skill references, and release metadata. Use after editing files under standards/, when adding, changing, moving, or retiring rules, or when preparing a standards release.
---

# Update Engineering Standards

Keep the human-authored standards documents and the publishable rule catalog semantically aligned.

## Locate inputs

1. Locate the `engineering-guidance-publisher` repository containing `standards/` and `catalog.json`.
2. Treat every Markdown file under `standards/` as a human-authored policy source and `catalog.json` as the structured publishing source.
3. Read the repository `AGENTS.md` and `README.md` before editing.
4. Record the initial Git status so a later commit can exclude unrelated pre-existing changes.

## Inspect the change

1. Discover every Markdown file recursively under `standards/`, then use Git status and diff for that complete file set.
2. Compare against the user-specified base revision when one is supplied.
3. Without a user-specified base, select the baseline automatically:
   - If any standards Markdown file has staged or unstaged changes, compare the working tree against `HEAD`, including staged changes.
   - Otherwise, find the most recent commit that modified any standards Markdown file and compare that commit against its first parent. Report the selected commit range before reconciling.
4. If the Markdown files are not yet tracked, no matching commit exists, or the selected commit has no parent, stop and ask for a base revision or initial commit. Do not infer a historical diff from file timestamps.
5. Classify every semantic change as added, tightened, relaxed, moved, reworded without semantic change, or retired.

## Reconcile the catalog

1. Map each persistent rule to the narrowest matching Skill reference and section.
2. Reuse an existing rule ID only when its semantic identity remains the same. Add a stable new ID for a new constraint.
3. Never reuse a retired ID for another meaning. Remove a rule from the active catalog only when the source documents intentionally retire it.
4. Keep concise catalog text semantically equivalent to the source documents; split independent constraints into separate rules.
5. Update the matching Skill blueprint only when the workflow or reference-routing behavior changes. Do not duplicate detailed rule text in `SKILL.md`.
6. Keep every catalog reference's `<path>#<heading>` source traceable to the standards document that owns it.
7. Increment the semantic version in `catalog.json`, `pyproject.toml`, and `src/engineering_guidance/__init__.py`. Use a patch increment unless the user requests or the compatibility impact requires a larger increment.

## Track consumer changes

Before pushing, compare the selected baseline and the updated `catalog.json`. For every Skill whose `scope` is `consumer`, record whether its catalog entry or references changed. For each changed consumer Skill, list added, changed, and retired rule IDs; also record reference, routing, or metadata changes that do not alter a rule. Preserve this consumer change list for the post-push report.

Classify each consumer change as either synchronization-only or code-conformance-affecting. Treat changes exclusively to `refactor-java-service` itself, including its workflow, routing, or metadata, as synchronization-only. Treat changes to rules or references of every other consumer Skill as code-conformance-affecting unless the change is explicitly documented as non-semantic.

## Verify and report

Run from `engineering-guidance-publisher`:

```bash
PYTHONPATH=src python3 -m engineering_guidance validate
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m engineering_guidance build --output dist
PYTHONPATH=src python3 -m engineering_guidance install-publisher-skills
```

Validate every generated Skill under `dist/skills` with the available Skill validator. Report:

- source-document changes mapped to rule IDs;
- added, changed, and retired rule IDs;
- version change;
- blueprint changes;
- consumer/publisher Skill scope changes;
- verification commands and results.

## Commit and push

After every required verification succeeds, review the Git status and diff, stage only changes made by this workflow, including the managed publisher Skill and its lock file, commit them with an accurate message, and push the current branch to its configured upstream without asking for confirmation. If no upstream is configured, ask the user for the remote and branch instead of choosing one. Report the commit and push results.

## Synchronize after push

After a successful push, inspect the preserved consumer change list. If no consumer Skill changed, report that no consumer synchronization is required and do not ask for project names. Otherwise, first list every changed consumer Skill and its added, changed, and retired rules, including any non-rule reference, routing, or metadata changes. Then ask the user for one or more consumer project directory names to synchronize. Accept a comma-separated, whitespace-separated, or newline-separated list; validate every entry as a single directory name, remove duplicates while preserving the user-supplied order, and ask again if any entry is invalid. This synchronization prompt applies to every consumer change, including synchronization-only changes to `refactor-java-service`.

Invoke `$sync-engineering-standards` separately for each validated project and follow its complete validation, synchronization, and consumer-verification workflow. If one synchronization fails, report the failed project and stop before beginning any remaining projects until the user gives direction. Do not infer project names or start synchronization when the push did not succeed.

## Plan and apply consumer refactors

After each consumer project synchronizes successfully, inspect the preserved consumer change list. If it contains only synchronization-only changes, report that no project code refactor plan is needed and do not inspect or modify consumer-project code.

Otherwise, use only code-conformance-affecting changes to analyze that project without modifying it. Read the project guidance and the changed consumer Skills, inspect the affected code and tests, and produce a project-specific refactor plan. For every planned item, state the consumer Skill, changed rule IDs, affected files or modules, intended code change, and project verification command. Exclude consumer rules that do not apply to the project and state why.

Present all project plans together and ask for explicit confirmation before changing any consumer-project code. Do not modify, stage, commit, or push a consumer project while preparing the plan.

After explicit confirmation, apply only the confirmed project plans. Preserve unrelated pre-existing changes, run the planned verification commands, and report their results. When a project has code changes and verification succeeds, stage only the refactor changes made by this workflow and create one accurate Git commit in that project. Do not push consumer-project commits unless the user separately asks. If a project is not a Git repository, has no applicable refactor, has verification failures, or has unrelated changes that cannot be safely excluded, do not commit it; report the reason and continue only when it is safe to do so.
