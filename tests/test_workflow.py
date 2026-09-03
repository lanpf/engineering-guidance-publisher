from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

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
                source_path, heading = reference["source"].split("#", 1)
                source = self.layout.root / source_path
                self.assertTrue(source.is_file())
                self.assertIn(heading, source.read_text(encoding="utf-8"))

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
        for standard in sorted((self.layout.root / "standards").rglob("bp_*.md")):
            for line in standard.read_text(encoding="utf-8").splitlines():
                rule = line.strip()
                if not rule.startswith("- "):
                    continue
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

if __name__ == "__main__":
    unittest.main()
