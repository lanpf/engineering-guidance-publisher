from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from .catalog import ProjectLayout

SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RULE_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
SKILL_REFERENCE = re.compile(r"\$([a-z0-9]+(?:-[a-z0-9]+)*)")


def validate(layout: ProjectLayout, catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    version = catalog.get("version")
    source = catalog.get("source")
    if not isinstance(source, str) or not source.startswith("https://"):
        errors.append("source must be an HTTPS repository URL")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("version must use MAJOR.MINOR.PATCH")
    else:
        pyproject_path = layout.root / "pyproject.toml"
        with pyproject_path.open("rb") as handle:
            project_version = tomllib.load(handle).get("project", {}).get("version")
        if project_version != version:
            errors.append(f"pyproject.toml version {project_version!r} does not match catalog {version!r}")
        init_path = layout.root / "src" / "engineering_guidance" / "__init__.py"
        init_text = init_path.read_text(encoding="utf-8")
        if f'__version__ = "{version}"' not in init_text:
            errors.append("package __version__ does not match catalog version")

    seen_rules: set[str] = set()
    seen_skills: set[str] = set()
    skill_bodies: dict[str, str] = {}

    def check_rule(rule: Any, location: str) -> None:
        if not isinstance(rule, dict):
            errors.append(f"{location}: rule must be an object")
            return
        rule_id = rule.get("id")
        text = rule.get("text")
        if not isinstance(rule_id, str) or not RULE_ID.fullmatch(rule_id):
            errors.append(f"{location}: invalid rule id {rule_id!r}")
        elif rule_id in seen_rules:
            errors.append(f"{location}: duplicate rule id {rule_id}")
        else:
            seen_rules.add(rule_id)
        if not isinstance(text, str) or not text.strip():
            errors.append(f"{location}: rule text is required")

    for index, rule in enumerate(catalog.get("agents", {}).get("rules", [])):
        check_rule(rule, f"agents.rules[{index}]")

    skills = catalog.get("skills")
    if not isinstance(skills, list) or not skills:
        return errors + ["skills must be a non-empty array"]

    for skill_index, skill in enumerate(skills):
        location = f"skills[{skill_index}]"
        name = skill.get("name")
        if not isinstance(name, str) or not SKILL_NAME.fullmatch(name):
            errors.append(f"{location}: invalid skill name {name!r}")
            continue
        if name in seen_skills:
            errors.append(f"{location}: duplicate skill {name}")
        seen_skills.add(name)
        scope = skill.get("scope")
        if scope not in {"consumer", "publisher"}:
            errors.append(f"{location}: scope must be 'consumer' or 'publisher'")
        blueprint = layout.blueprints / name
        skill_md = blueprint / "SKILL.md"
        openai_yaml = blueprint / "agents" / "openai.yaml"
        if not skill_md.is_file():
            errors.append(f"{location}: missing {skill_md.relative_to(layout.root)}")
        else:
            body = skill_md.read_text(encoding="utf-8")
            if not body.startswith("---\n") or f"name: {name}\n" not in body:
                errors.append(f"{location}: SKILL.md frontmatter does not match {name}")
            if len(body.splitlines()) >= 500:
                errors.append(f"{location}: SKILL.md must stay below 500 lines")
            skill_bodies[name] = body
        if not openai_yaml.is_file():
            errors.append(f"{location}: missing agents/openai.yaml")

        files: set[str] = set()
        references = skill.get("references", [])
        for reference_index, reference in enumerate(references):
            ref_location = f"{location}.references[{reference_index}]"
            source_document = reference.get("source")
            if not isinstance(source_document, str) or "#" not in source_document:
                errors.append(f"{ref_location}: source must use <path>#<heading>")
            else:
                source_path_text, heading = source_document.split("#", 1)
                source_path = layout.root / source_path_text
                if not source_path.is_file():
                    errors.append(f"{ref_location}: source document does not exist: {source_path_text}")
                elif not heading.strip():
                    errors.append(f"{ref_location}: source heading is required")
                else:
                    source_text = source_path.read_text(encoding="utf-8")
                    heading_pattern = re.compile(
                        rf"^#{{1,6}}\s+{re.escape(heading.strip())}\s*$", re.MULTILINE
                    )
                    if not heading_pattern.search(source_text):
                        errors.append(
                            f"{ref_location}: source heading not found: {source_document}"
                        )
            filename = reference.get("file")
            if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(".md"):
                errors.append(f"{ref_location}: invalid reference filename {filename!r}")
            elif filename in files:
                errors.append(f"{ref_location}: duplicate reference filename {filename}")
            else:
                files.add(filename)
            for section_index, section in enumerate(reference.get("sections", [])):
                for rule_index, rule in enumerate(section.get("rules", [])):
                    check_rule(rule, f"{ref_location}.sections[{section_index}].rules[{rule_index}]")

    blueprint_names = {path.name for path in layout.blueprints.iterdir() if path.is_dir()}
    extra = blueprint_names - seen_skills
    missing = seen_skills - blueprint_names
    if extra:
        errors.append(f"unregistered skill blueprints: {', '.join(sorted(extra))}")
    if missing:
        errors.append(f"missing skill blueprints: {', '.join(sorted(missing))}")
    for name, body in skill_bodies.items():
        unresolved = set(SKILL_REFERENCE.findall(body)) - seen_skills
        if unresolved:
            errors.append(
                f"skill {name} references unregistered skills: {', '.join(sorted(unresolved))}"
            )
    return errors
