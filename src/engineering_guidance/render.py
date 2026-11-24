from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .catalog import ProjectLayout
from .transaction import publish, recover, writer_lock

BEGIN_MARKER = "<!-- engineering-standards:begin"
END_MARKER = "<!-- engineering-standards:end -->"


def render_rule(rule: dict[str, Any]) -> str:
    enforcement = rule["enforcement"].upper()
    priority = rule["priority"].upper()
    return f"- **{rule['id']}** **[{enforcement}][{priority}]** — {rule['text']}"


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
            lines.append(render_rule(rule))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_agents(catalog: dict[str, Any]) -> str:
    version = catalog["version"]
    lines = [
        f"<!-- engineering-standards:begin version={version} -->",
        "## Shared engineering guidance",
        "",
        "Rule markers: [REQUIRED] is release-blocking, [DEFAULT] applies unless a concrete "
        "deviation reason is recorded, [ADVISORY] is optional guidance; [BASELINE] rules are "
        "preloaded for every change, [TOPIC] rules apply when the affected capability matches.",
        "",
    ]
    for rule in catalog["agents"]["rules"]:
        lines.append(render_rule(rule))
    lines.extend(["", "## Skill routing", ""])
    for skill in skills_for_scope(catalog, "consumer"):
        lines.append(f"- {skill['when']}: use `${skill['name']}`.")
    lines.extend(["", END_MARKER, ""])
    return "\n".join(lines)


def _inventory(output: Path) -> dict[str, str]:
    files = {}
    for item in sorted(output.rglob("*")):
        if item.is_symlink():
            raise ValueError(f"unexpected symlink in build output: {item}")
        if item == output / "manifest.json":
            continue
        name = item.relative_to(output).as_posix()
        files[name] = "directory" if item.is_dir() else hashlib.sha256(item.read_bytes()).hexdigest()
    return files


def _check_output(layout: ProjectLayout, catalog: dict[str, Any], output: Path) -> None:
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise ValueError(f"output must be a directory: {output}")
    if not output.exists() or not any(output.iterdir()):
        return
    manifest_path = output / "manifest.json"
    message = f"output contains unknown or modified content: {output}"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError(message)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or any(manifest.get(k) != catalog[k] for k in ("name", "source")):
        raise ValueError(message)
    inventory = _inventory(output)
    if "files" in manifest:
        if manifest["files"] != inventory:
            raise ValueError(message)
        return
    if not _matches_legacy_lock(layout, output, manifest.get("version")):
        raise ValueError(message)


def _matches_legacy_lock(layout: ProjectLayout, output: Path, version: str) -> bool:
    # Before inventories, the publisher lock recorded the full artifact digest.
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        return False
    lock = Path(".engineering-guidance/publisher-skills.lock.json")
    digest = artifact_digest(output)
    current = layout.root / lock
    if current.is_file() and json.loads(current.read_text(encoding="utf-8")).get("artifact_sha256") == digest:
        return True
    try:
        saved = subprocess.check_output(
            ["git", "show", f"{version}:{lock.as_posix()}"],
            cwd=layout.root, stderr=subprocess.DEVNULL,
        )
        return json.loads(saved).get("artifact_sha256") == digest
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return False


def build(layout: ProjectLayout, catalog: dict[str, Any], output: Path) -> Path:
    if output.is_symlink():
        raise ValueError(f"output must not be a symlink: {output}")
    output = output.resolve()
    root = layout.root.resolve()
    protected = {"src", "standards", "blueprints", "tests", "releases"}
    if root.is_relative_to(output):
        raise ValueError(f"output contains publisher sources: {output}")
    if output.is_relative_to(root):
        first = output.relative_to(root).parts[0]
        if first in protected or first.startswith("."):
            raise ValueError(f"output is inside a publisher source directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    pending = output.with_name(f".{output.name}.engineering-guidance-pending")
    relative = Path(output.name)

    def allowed(path: Path) -> bool:
        return path == relative

    with writer_lock(output):
        recover(output.parent, pending, allowed)
        _check_output(layout, catalog, output)
        with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
            staged = Path(temporary) / "artifact"
            render_artifact(layout, catalog, staged)
            publish(output.parent, pending, {relative: staged}, allowed)
    return output


def render_artifact(layout: ProjectLayout, catalog: dict[str, Any], output: Path) -> None:
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
    manifest["files"] = _inventory(output)
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def artifact_digest(output: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        digest.update(path.relative_to(output).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
