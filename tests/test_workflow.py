from __future__ import annotations

import copy
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engineering_guidance.catalog import ProjectLayout, load_catalog, project_root
from engineering_guidance.render import artifact_digest, build
from engineering_guidance.sync import (
    LOCK_PATH,
    PUBLISHER_LOCK_PATH,
    SyncConflict,
    install_publisher_skills,
    synchronize,
    update_agents,
)
from engineering_guidance.validation import validate


class EngineeringGuidancePublisherTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.layout = ProjectLayout(project_root())
        cls.catalog = load_catalog(cls.layout.catalog)

    def test_catalog_and_blueprints_are_valid(self) -> None:
        self.assertEqual([], validate(self.layout, self.catalog))

    def test_every_blueprint_skill_reference_is_registered(self) -> None:
        registered = {skill["name"] for skill in self.catalog["skills"]}
        pattern = re.compile(r"\$([a-z0-9]+(?:-[a-z0-9]+)*)")
        for skill in self.catalog["skills"]:
            skill_md = self.layout.blueprints / skill["name"] / "SKILL.md"
            referenced = set(pattern.findall(skill_md.read_text(encoding="utf-8")))
            self.assertEqual(
                set(),
                referenced - registered,
                f"{skill['name']} references unregistered skills",
            )

    def test_every_reference_is_traceable_to_a_standards_heading(self) -> None:
        for skill in self.catalog["skills"]:
            for reference in skill["references"]:
                sources = [reference["source"]]
                sources.extend(
                    section["source"]
                    for section in reference["sections"]
                    if "source" in section
                )
                for source_document in sources:
                    source_path, heading = source_document.split("#", 1)
                    source = self.layout.root / source_path
                    self.assertTrue(source.is_file())
                    self.assertRegex(
                        source.read_text(encoding="utf-8"),
                        rf"(?m)^#{{1,6}}\s+{re.escape(heading)}\s*$",
                    )

    def test_every_rule_has_a_valid_classification(self) -> None:
        rules = list(self.catalog["agents"]["rules"])
        rules.extend(
            rule
            for skill in self.catalog["skills"]
            for reference in skill["references"]
            for section in reference["sections"]
            for rule in section["rules"]
        )
        self.assertTrue(rules)
        self.assertTrue(all(rule["enforcement"] in {"required", "default", "advisory"} for rule in rules))
        self.assertTrue(all(rule["priority"] in {"baseline", "topic"} for rule in rules))
        self.assertTrue(any(rule["priority"] == "baseline" for rule in rules))
        self.assertTrue(any(rule["priority"] == "topic" for rule in rules))

    def test_every_standard_uses_the_best_practice_filename_prefix(self) -> None:
        standards = sorted((self.layout.root / "standards").rglob("*.md"))
        self.assertTrue(standards)
        self.assertTrue(
            all(path.name.startswith("bp_") or path.name == "README.md" for path in standards)
        )
        for skill in self.catalog["skills"]:
            for reference in skill["references"]:
                source_path, _ = reference["source"].split("#", 1)
                self.assertTrue(Path(source_path).name.startswith("bp_"))

    def test_standard_bullets_are_not_declared_in_multiple_documents(self) -> None:
        owners: dict[str, Path] = {}
        classification = re.compile(r"^- \*\*(强制|默认|建议) · (基础|主题)\*\*：")
        for standard in sorted((self.layout.root / "standards").rglob("bp_*.md")):
            for line in standard.read_text(encoding="utf-8").splitlines():
                rule = line.strip()
                if not rule.startswith("- "):
                    continue
                self.assertRegex(rule, classification, f"unclassified standard bullet in {standard}")
                rule = classification.sub("- ", rule).partition(" <!-- ")[0]
                self.assertNotIn(
                    rule,
                    owners,
                    f"duplicate standard bullet in {owners.get(rule)} and {standard}",
                )
                owners[rule] = standard

    def test_build_is_deterministic_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = build(self.layout, self.catalog, Path(temporary) / "first")
            second = build(self.layout, self.catalog, Path(temporary) / "second")
            self.assertEqual(artifact_digest(first), artifact_digest(second))
            for skill in self.catalog["skills"]:
                skill_root = first / "skills" / skill["name"]
                self.assertTrue((skill_root / "SKILL.md").is_file())
                self.assertTrue((skill_root / "agents" / "openai.yaml").is_file())
                for reference in skill["references"]:
                    content = (skill_root / "references" / reference["file"]).read_text(encoding="utf-8")
                    self.assertIn(reference["title"], content)
                    for section in reference["sections"]:
                        for rule in section["rules"]:
                            tag = f"**[{rule['enforcement'].upper()}][{rule['priority'].upper()}]**"
                            self.assertIn(tag, content)
            manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(
                ["update-standards", "sync-standards"],
                manifest["publisher_skills"],
            )

    def test_agents_update_preserves_project_content(self) -> None:
        current = "# Project\n\nKeep this rule.\n"
        fragment = "<!-- engineering-standards:begin version=1.0.0 -->\nmanaged\n<!-- engineering-standards:end -->\n"
        first = update_agents(current, fragment)
        self.assertIn("Keep this rule.", first)
        replacement = fragment.replace("managed", "updated")
        second = update_agents(first, replacement)
        self.assertIn("Keep this rule.", second)
        self.assertIn("updated", second)
        self.assertNotIn("\nmanaged\n", second)

    def test_sync_writes_lock_agents_and_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "consumer"
            target.mkdir()
            (target / "AGENTS.md").write_text("# Consumer\n\nLocal rule.\n", encoding="utf-8")
            lock = synchronize(self.layout, self.catalog, target)
            persisted = json.loads((target / LOCK_PATH).read_text(encoding="utf-8"))
            self.assertEqual(lock, persisted)
            self.assertEqual(self.catalog["version"], persisted["version"])
            self.assertIn("Local rule.", (target / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertNotIn(
                "update-standards",
                (target / "AGENTS.md").read_text(encoding="utf-8"),
            )
            for name in persisted["managed_skills"]:
                self.assertTrue((target / ".agents" / "skills" / name / "SKILL.md").is_file())
            self.assertNotIn("update-standards", persisted["managed_skills"])
            self.assertFalse(
                (target / ".agents" / "skills" / "update-standards").exists()
            )

    def test_install_publisher_skills_installs_only_publisher_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "publisher"
            root.mkdir()
            layout = ProjectLayout(root)
            layout.blueprints.parent.mkdir(parents=True)
            for skill in self.catalog["skills"]:
                source = self.layout.blueprints / skill["name"]
                destination = layout.blueprints / skill["name"]
                shutil.copytree(source, destination)
            (root / "catalog.json").write_text(
                json.dumps(self.catalog, ensure_ascii=False), encoding="utf-8"
            )
            lock = install_publisher_skills(layout, self.catalog)

            persisted = json.loads((root / PUBLISHER_LOCK_PATH).read_text(encoding="utf-8"))
            self.assertEqual(lock, persisted)
            self.assertEqual(
                ["update-standards", "sync-standards"],
                persisted["managed_skills"],
            )
            self.assertFalse((root / ".agents" / "skills" / "develop-service").exists())

    def test_sync_refuses_to_adopt_unmanaged_skill_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "consumer"
            collision = target / ".agents" / "skills" / self.catalog["skills"][0]["name"]
            collision.mkdir(parents=True)
            with self.assertRaises(SyncConflict):
                synchronize(self.layout, self.catalog, target)

            self.assertFalse((target / "AGENTS.md").exists())
            self.assertFalse((target / LOCK_PATH).exists())

    def test_upgrade_preserves_newly_colliding_skill_until_explicit_adoption(self) -> None:
        old = copy.deepcopy(self.catalog)
        old["skills"] = [s for s in old["skills"] if s["name"] != "refactor-service"]
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            synchronize(self.layout, old, target)
            local = target / ".agents/skills/refactor-service/local.md"
            local.parent.mkdir()
            local.write_text("user-owned")
            before = artifact_digest(target)
            with self.assertRaises(SyncConflict):
                synchronize(self.layout, self.catalog, target)
            self.assertEqual(before, artifact_digest(target))
            synchronize(self.layout, self.catalog, target, force=True)
            self.assertFalse(local.exists())
            self.assertTrue((local.parent / "SKILL.md").is_file())

    def test_sync_rolls_back_when_final_lock_write_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary).resolve()
            synchronize(self.layout, self.catalog, target)
            before = artifact_digest(target)
            newer = copy.deepcopy(self.catalog)
            newer["version"] = "9.9.9"
            newer["skills"] = [s for s in newer["skills"] if s["name"] != "refactor-service"]
            replace = os.replace

            def fail_lock(source, destination):
                if Path(destination) == target / LOCK_PATH and Path(source).parent.name == "new":
                    raise OSError("injected lock write failure")
                return replace(source, destination)

            with patch("engineering_guidance.transaction.os.replace", side_effect=fail_lock):
                with self.assertRaisesRegex(OSError, "injected"):
                    synchronize(self.layout, newer, target)
            self.assertEqual(before, artifact_digest(target))
            synchronize(self.layout, newer, target)
            self.assertFalse((target / ".agents/skills/refactor-service").exists())

    def test_retry_recovers_an_interrupted_upgrade_before_conflict_checks(self) -> None:
        old = copy.deepcopy(self.catalog)
        old["skills"] = [s for s in old["skills"] if s["name"] != "refactor-service"]
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            synchronize(self.layout, old, target)
            replace = os.replace

            def interrupt(source, destination):
                if Path(destination).name == "AGENTS.md" and Path(source).parent.name == "new":
                    raise KeyboardInterrupt()
                return replace(source, destination)

            # Simulate process death by leaving the on-disk journal for the next caller.
            with patch("engineering_guidance.transaction.os.replace", side_effect=interrupt), \
                    patch("engineering_guidance.transaction.recover"):
                with self.assertRaises(KeyboardInterrupt):
                    synchronize(self.layout, self.catalog, target)
            synchronize(self.layout, self.catalog, target)
            self.assertIn("refactor-service", json.loads((target / LOCK_PATH).read_text())["managed_skills"])
            self.assertEqual(1, (target / "AGENTS.md").read_text().count("engineering-standards:begin"))

    def test_build_preserves_unknown_modified_and_source_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            output.mkdir()
            local = output / "local.txt"
            local.write_text("keep")
            with self.assertRaises(ValueError):
                build(self.layout, self.catalog, output)
            self.assertEqual("keep", local.read_text())
            local.unlink()
            build(self.layout, self.catalog, output)
            build(self.layout, self.catalog, output)
            local = output / "skills/develop-service/SKILL.md"
            local.write_text("my edits")
            with self.assertRaises(ValueError):
                build(self.layout, self.catalog, output)
            self.assertEqual("my edits", local.read_text())
            for protected in (self.layout.root, self.layout.root / "standards" / "new-directory"):
                with self.assertRaises(ValueError):
                    build(self.layout, self.catalog, protected)

    def test_build_render_failure_preserves_previous_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "dist"
            build(self.layout, self.catalog, output)
            before = artifact_digest(output)
            with patch("engineering_guidance.render.render_reference", side_effect=OSError("render failed")):
                with self.assertRaises(OSError):
                    build(self.layout, self.catalog, output)
            self.assertEqual(before, artifact_digest(output))

    def test_validate_detects_source_grade_priority_and_coverage_drift(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        rules = catalog["skills"][0]["references"][0]["sections"][0]["rules"]
        rules[0]["enforcement"] = "advisory"
        rules[1]["priority"] = "topic"
        missing = rules.pop()["id"]
        errors = "\n".join(validate(self.layout, catalog))
        self.assertIn(f"{rules[0]['id']} differs from BP source", errors)
        self.assertIn(f"{rules[1]['id']} differs from BP source", errors)
        self.assertIn(f"{missing}: BP rule missing", errors)


if __name__ == "__main__":
    unittest.main()
