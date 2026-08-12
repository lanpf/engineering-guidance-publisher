from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .render import BEGIN_MARKER, END_MARKER, artifact_digest, build, skills_for_scope
from .catalog import ProjectLayout

LOCK_PATH = Path(".engineering-standards/standards.lock.json")
PUBLISHER_LOCK_PATH = Path(".engineering-guidance/publisher-skills.lock.json")


class SyncConflict(RuntimeError):
    pass


def replace_managed_skills(
    artifact: Path,
    target: Path,
    managed_skills: list[str],
    previous_skills: list[str],
    *,
    force: bool,
) -> None:
    skills_root = target / ".agents" / "skills"
    if not previous_skills and not force:
        collisions = [name for name in managed_skills if (skills_root / name).exists()]
        if collisions:
            raise SyncConflict(
                "unmanaged skill directories already exist: "
                + ", ".join(collisions)
                + "; use --force to adopt them"
            )

    skills_root.mkdir(parents=True, exist_ok=True)
    for name in managed_skills:
        source = artifact / "skills" / name
        destination = skills_root / name
        staged = skills_root / f".{name}.staged"
        if staged.exists():
            shutil.rmtree(staged)
        shutil.copytree(source, staged)
        if destination.exists():
            shutil.rmtree(destination)
        os.replace(staged, destination)

    for name in set(previous_skills) - set(managed_skills):
        destination = skills_root / name
        if destination.is_dir():
            shutil.rmtree(destination)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def update_agents(current: str, fragment: str) -> str:
    begin = current.find(BEGIN_MARKER)
    end = current.find(END_MARKER)
    if (begin == -1) != (end == -1):
        raise SyncConflict("AGENTS.md contains an incomplete managed block")
    if begin != -1 and end < begin:
        raise SyncConflict("AGENTS.md managed block markers are out of order")
    if begin == -1:
        prefix = current.rstrip()
        return (prefix + "\n\n" if prefix else "") + fragment
    end += len(END_MARKER)
    return current[:begin] + fragment.rstrip() + current[end:]


def synchronize(
    layout: ProjectLayout,
    catalog: dict[str, Any],
    target: Path,
    *,
    force: bool = False,
) -> dict[str, Any]:
    target = target.resolve()
    if not target.is_dir():
        raise SyncConflict(f"target is not a directory: {target}")

    lock_path = target / LOCK_PATH
    previous = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.is_file() else None
    managed_skills = [skill["name"] for skill in skills_for_scope(catalog, "consumer")]

    with tempfile.TemporaryDirectory(prefix="engineering-guidance-") as temporary:
        artifact = build(layout, catalog, Path(temporary) / "dist")
        digest = artifact_digest(artifact)
        agents_path = target / "AGENTS.md"
        current_agents = agents_path.read_text(encoding="utf-8") if agents_path.is_file() else ""
        fragment = (artifact / "AGENTS.fragment.md").read_text(encoding="utf-8")
        atomic_write(agents_path, update_agents(current_agents, fragment))

        replace_managed_skills(
            artifact,
            target,
            managed_skills,
            previous.get("managed_skills", []) if previous else [],
            force=force,
        )

        lock = {
            "name": catalog["name"],
            "source": catalog["source"],
            "version": catalog["version"],
            "artifact_sha256": digest,
            "managed_skills": managed_skills,
        }
        atomic_write(lock_path, json.dumps(lock, ensure_ascii=False, indent=2) + "\n")
        return lock


def install_publisher_skills(
    layout: ProjectLayout,
    catalog: dict[str, Any],
    *,
    force: bool = False,
) -> dict[str, Any]:
    target = layout.root.resolve()
    lock_path = target / PUBLISHER_LOCK_PATH
    previous = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.is_file() else None
    managed_skills = [skill["name"] for skill in skills_for_scope(catalog, "publisher")]

    with tempfile.TemporaryDirectory(prefix="engineering-guidance-") as temporary:
        artifact = build(layout, catalog, Path(temporary) / "dist")
        digest = artifact_digest(artifact)
        replace_managed_skills(
            artifact,
            target,
            managed_skills,
            previous.get("managed_skills", []) if previous else [],
            force=force,
        )
        lock = {
            "name": catalog["name"],
            "source": catalog["source"],
            "version": catalog["version"],
            "artifact_sha256": digest,
            "managed_skills": managed_skills,
        }
        atomic_write(lock_path, json.dumps(lock, ensure_ascii=False, indent=2) + "\n")
        return lock
