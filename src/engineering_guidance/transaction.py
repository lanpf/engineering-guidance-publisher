"""Serialize cooperating publishers and recover interrupted multi-path replacements."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator


@contextmanager
def writer_lock(target: Path) -> Iterator[None]:
    key = hashlib.sha256(os.fsencode(target.resolve())).hexdigest()
    lock = Path(tempfile.gettempdir()) / f"engineering-guidance-{key}.lock"
    with lock.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def recover(root: Path, pending: Path, allowed: Callable[[Path], bool]) -> None:
    """Undo a pending transaction. Each rename can safely be retried."""
    if not pending.exists():
        return
    if pending.is_symlink():
        raise ValueError(f"unexpected transaction symlink: {pending}")
    record = json.loads((pending / "paths.json").read_text(encoding="utf-8"))
    if record.get("format") != "engineering-guidance-transaction-1":
        raise ValueError(f"unrecognized transaction: {pending}")
    paths = record["paths"]
    for row in paths:
        relative = Path(row["path"])
        if not allowed(relative) or (root / relative).parent.resolve() != (root / relative).parent:
            raise ValueError(f"invalid transaction destination: {relative}")
    for index in reversed(range(len(paths))):
        row = paths[index]
        destination = root / row["path"]
        backup = pending / "old" / str(index)
        staged = pending / "new" / str(index)
        if backup.exists() or backup.is_symlink():
            if destination.exists() or destination.is_symlink():
                os.replace(destination, staged)
            os.replace(backup, destination)
        elif not row["existed"] and not staged.exists() and destination.exists():
            os.replace(destination, staged)
    discard(pending)


def discard(pending: Path) -> None:
    # Unlink the recovery journal from its well-known name before removing files.
    with tempfile.TemporaryDirectory(dir=pending.parent) as garbage:
        os.replace(pending, Path(garbage) / "completed")


def publish(root: Path, pending: Path, changes: dict[Path, Path | None],
            allowed: Callable[[Path], bool]) -> None:
    """Call under writer_lock, after recover. Sources must be on the target filesystem."""
    pending.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=pending.parent) as temporary:
        work = Path(temporary) / "transaction"
        (work / "new").mkdir(parents=True)
        (work / "old").mkdir()
        rows = []
        for index, (relative, source) in enumerate(changes.items()):
            destination = root / relative
            if not allowed(relative) or destination.parent.resolve() != destination.parent:
                raise ValueError(f"invalid transaction destination: {relative}")
            rows.append({"path": str(relative), "existed": os.path.lexists(destination)})
            if source is not None:
                os.replace(source, work / "new" / str(index))
        record = {"format": "engineering-guidance-transaction-1", "paths": rows}
        (work / "paths.json").write_text(json.dumps(record), encoding="utf-8")
        os.replace(work, pending)

    try:
        for index, (relative, source) in enumerate(changes.items()):
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if rows[index]["existed"]:
                os.replace(destination, pending / "old" / str(index))
            if source is not None:
                os.replace(pending / "new" / str(index), destination)
    except BaseException:
        recover(root, pending, allowed)
        raise
    discard(pending)
