from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import ProjectLayout, load_catalog, project_root
from .render import artifact_digest, build
from .sync import SyncConflict, install_publisher_skills, synchronize
from .validation import validate


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(prog="engineering-guidance")
    subcommands = command.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate", help="validate catalog and Skill blueprints")
    build_parser = subcommands.add_parser("build", help="build a publishable artifact")
    build_parser.add_argument("--output", type=Path, default=Path("dist"))
    sync_parser = subcommands.add_parser("sync", help="synchronize guidance into a consumer repository")
    sync_parser.add_argument("--target", type=Path, required=True)
    sync_parser.add_argument("--force", action="store_true", help="adopt colliding managed Skill directories")
    install_parser = subcommands.add_parser(
        "install-publisher-skills", help="install publisher-only Skills into this repository"
    )
    install_parser.add_argument(
        "--force", action="store_true", help="adopt colliding unmanaged Skill directories"
    )
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = project_root()
    layout = ProjectLayout(root)
    catalog = load_catalog(layout.catalog)
    errors = validate(layout, catalog)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 2

    if args.command == "validate":
        print(f"valid engineering guidance {catalog['version']}")
        return 0
    if args.command == "build":
        output = build(layout, catalog, args.output.resolve())
        print(json.dumps({"output": str(output), "sha256": artifact_digest(output)}, indent=2))
        return 0
    if args.command == "sync":
        try:
            lock = synchronize(layout, catalog, args.target, force=args.force)
        except SyncConflict as error:
            print(f"error: {error}", file=sys.stderr)
            return 3
        print(json.dumps(lock, ensure_ascii=False, indent=2))
        return 0
    if args.command == "install-publisher-skills":
        try:
            lock = install_publisher_skills(layout, catalog, force=args.force)
        except SyncConflict as error:
            print(f"error: {error}", file=sys.stderr)
            return 3
        print(json.dumps(lock, ensure_ascii=False, indent=2))
        return 0
    return 1
