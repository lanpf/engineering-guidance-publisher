from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .catalog import ProjectLayout

BEGIN_MARKER = "<!-- engineering-standards:begin"
END_MARKER = "<!-- engineering-standards:end -->"


def skills_for_scope(catalog: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    return [skill for skill in catalog["skills"] if skill["scope"] == scope]


def render_reference(title: str, sections: list[dict[str, Any]]) -> str:
    lines = [f"# {title}", ""]
    if len(sections) > 2:
        lines.extend(["## Contents", ""])
        for section in sections:
            anchor = section["title"].lower().replace(" ", "-")
            lines.append(f"- [{section['title']}](#{anchor})")
        lines.append("")
    for section in sections:
        lines.extend([f"## {section['title']}", ""])
        for rule in section["rules"]:
            lines.append(f"- **{rule['id']}** — {rule['text']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_agents(catalog: dict[str, Any]) -> str:
    version = catalog["version"]
    lines = [
        f"<!-- engineering-standards:begin version={version} -->",
        "## Shared engineering guidance",
        "",
    ]
    for rule in catalog["agents"]["rules"]:
        lines.append(f"- **{rule['id']}** — {rule['text']}")
    lines.extend(["", "## Skill routing", ""])
    for skill in skills_for_scope(catalog, "consumer"):
        lines.append(f"- {skill['when']}: use `${skill['name']}`.")
    lines.extend(["", END_MARKER, ""])
    return "\n".join(lines)


def build(layout: ProjectLayout, catalog: dict[str, Any], output: Path) -> Path:
    if output.exists():
        shutil.rmtree(output)
    skills_output = output / "skills"
    skills_output.mkdir(parents=True)

    for skill in catalog["skills"]:
        name = skill["name"]
        source = layout.blueprints / name
        destination = skills_output / name
        shutil.copytree(source, destination)
        references = destination / "references"
        references.mkdir(exist_ok=True)
        for stale in references.glob("*.md"):
            stale.unlink()
        for reference in skill["references"]:
            content = render_reference(reference["title"], reference["sections"])
            (references / reference["file"]).write_text(content, encoding="utf-8")

    (output / "AGENTS.fragment.md").write_text(render_agents(catalog), encoding="utf-8")
    manifest = {
        "name": catalog["name"],
        "source": catalog["source"],
        "version": catalog["version"],
        "skills": [skill["name"] for skill in catalog["skills"]],
        "consumer_skills": [
            skill["name"] for skill in skills_for_scope(catalog, "consumer")
        ],
        "publisher_skills": [
            skill["name"] for skill in skills_for_scope(catalog, "publisher")
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return output


def artifact_digest(output: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        digest.update(path.relative_to(output).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
