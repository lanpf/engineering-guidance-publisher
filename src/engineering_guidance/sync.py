from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .catalog import ProjectLayout
from .render import BEGIN_MARKER, END_MARKER, artifact_digest, render_artifact, skills_for_scope
from .transaction import publish, recover, writer_lock
from .validation import SKILL_NAME

LOCK_PATH = Path(".engineering-standards/standards.lock.json")
PUBLISHER_LOCK_PATH = Path(".engineering-guidance/publisher-skills.lock.json")


class SyncConflict(RuntimeError):
    pass


def update_agents(current: str, fragment: str) -> str:
    begin = current.find(BEGIN_MARKER)
    end = current.find(END_MARKER)
    if current.count(BEGIN_MARKER) > 1 or current.count(END_MARKER) > 1:
        raise SyncConflict("AGENTS.md contains duplicate managed block markers")
    if (begin == -1) != (end == -1):
        raise SyncConflict("AGENTS.md contains an incomplete managed block")
    if begin != -1 and end < begin:
        raise SyncConflict("AGENTS.md managed block markers are out of order")
    if begin == -1:
        if current and not current.endswith("\n"):
            current += "\n"
        if current and not current.endswith("\n\n"):
            current += "\n"
        return current + fragment
    end += len(END_MARKER)
    return current[:begin] + fragment.rstrip() + current[end:]


def _install(layout: ProjectLayout, catalog: dict[str, Any], target: Path,
             scope: str, lock_file: Path, force: bool) -> dict[str, Any]:
    target = target.resolve()
    if not target.is_dir():
        raise SyncConflict(f"target is not a directory: {target}")
    skills_root = Path(".agents/skills")
    skills_path = target / skills_root
    lock_path = target / lock_file
    pending = lock_path.with_suffix(".pending")
    managed = [skill["name"] for skill in skills_for_scope(catalog, scope)]

    def allowed(path: Path) -> bool:
        if path == lock_file or (scope == "consumer" and path == Path("AGENTS.md")):
            return True
        return path.parent == skills_root and SKILL_NAME.fullmatch(path.name) is not None

    with writer_lock(target):
        if lock_path.parent.resolve() != lock_path.parent or skills_path.resolve() != skills_path:
            raise SyncConflict("managed directories must reside in the target project")
        recover(target, pending, allowed)
        if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
            raise SyncConflict(f"expected a regular lock file: {lock_path}")
        previous = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.is_file() else {}
        names = previous.get("managed_skills", []) if isinstance(previous, dict) else None
        if not isinstance(names, list) or not all(isinstance(n, str) and SKILL_NAME.fullmatch(n) for n in names):
            raise SyncConflict(f"invalid managed skill names in {lock_path}")
        added = set(managed) - set(names)
        collisions = sorted(n for n in added if os.path.lexists(target / skills_root / n))
        if collisions and not force:
            raise SyncConflict("unmanaged skills already exist: " + ", ".join(collisions) + "; use --force to adopt them")

        with tempfile.TemporaryDirectory(dir=target) as temporary:
            work = Path(temporary)
            artifact = work / "artifact"
            render_artifact(layout, catalog, artifact)
            lock = {
                "name": catalog["name"],
                "source": catalog["source"],
                "version": catalog["version"],
                "artifact_sha256": artifact_digest(artifact),
                "managed_skills": managed,
            }
            changes: dict[Path, Path | None] = {
                skills_root / name: artifact / "skills" / name for name in managed
            }
            for n in sorted(set(names) - set(managed)):
                changes[skills_root / n] = None
            if scope == "consumer":
                agents = target / "AGENTS.md"
                if agents.is_symlink() or (agents.exists() and not agents.is_file()):
                    raise SyncConflict(f"expected a regular file: {agents}")
                current = agents.read_bytes().decode() if agents.is_file() else ""
                fragment = (artifact / "AGENTS.fragment.md").read_text(encoding="utf-8")
                staged = work / "AGENTS.md"
                staged.write_bytes(update_agents(current, fragment).encode())
                if agents.exists():
                    staged.chmod(agents.stat().st_mode)
                changes[Path("AGENTS.md")] = staged
            staged_lock = work / "lock.json"
            staged_lock.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changes[lock_file] = staged_lock
            publish(target, pending, changes, allowed)
            return lock


def synchronize(layout: ProjectLayout, catalog: dict[str, Any], target: Path,
                *, force: bool = False) -> dict[str, Any]:
    return _install(layout, catalog, target, "consumer", LOCK_PATH, force)


def install_publisher_skills(layout: ProjectLayout, catalog: dict[str, Any],
                             *, force: bool = False) -> dict[str, Any]:
    return _install(layout, catalog, layout.root, "publisher", PUBLISHER_LOCK_PATH, force)
