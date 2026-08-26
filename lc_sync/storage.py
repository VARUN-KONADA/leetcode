"""All filesystem I/O lives here.

Two kinds of state on disk:

1. ``data/index.json`` — the master, machine-only log of every submission
   ever synced (id -> lightweight record). This is what makes sync
   idempotent and incremental: a submission id in here is never processed
   again, and the newest timestamp in here is the incremental cursor.

2. ``problems/<num>-<slug>/`` — the human-facing, generated artifact for
   each unique problem: the solution file(s), a README (auto + personal
   sections), and a meta.json with the full structured record for that one
   problem (statement, examples, constraints, topics, submission history).

index.json is the source of truth for "has this been synced". The
problems/ tree is derived from it and is safe to regenerate.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterator

from . import config


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _atomic_write_json(path: Path, data: Any) -> None:
    _atomic_write_text(path, json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------
# index.json
# ---------------------------------------------------------------------------

def load_index() -> dict:
    if not config.INDEX_PATH.exists():
        return {"last_synced_timestamp": 0, "submissions": {}}
    with open(config.INDEX_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("last_synced_timestamp", 0)
    data.setdefault("submissions", {})
    return data


def save_index(index: dict) -> None:
    _atomic_write_json(config.INDEX_PATH, index)


# ---------------------------------------------------------------------------
# problems/<num>-<slug>/
# ---------------------------------------------------------------------------

def problem_dir(number: str, slug: str) -> Path:
    safe_number = str(number).zfill(4) if str(number).isdigit() else str(number)
    return config.PROBLEMS_DIR / f"{safe_number}-{slug}"


def load_problem_meta(path: Path) -> dict | None:
    meta_path = path / "meta.json"
    if not meta_path.exists():
        return None
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_problem_meta(path: Path, meta: dict) -> None:
    _atomic_write_json(path / "meta.json", meta)


def save_solution_file(path: Path, code: str, ext: str) -> Path:
    solution_path = path / f"solution.{ext}"
    _atomic_write_text(solution_path, code.rstrip("\n") + "\n")
    return solution_path


def save_submission_snapshot(path: Path, submission_id: str, timestamp: int, status: str, code: str, ext: str) -> Path:
    """Preserve one submission's exact code, so history is never lost even
    though only the latest submission is mirrored as solution.<ext>.
    """
    snap_dir = path / "submissions"
    safe_status = status.replace(" ", "-")
    snap_path = snap_dir / f"{timestamp}_{safe_status}_{submission_id}.{ext}"
    if not snap_path.exists():
        _atomic_write_text(snap_path, code.rstrip("\n") + "\n")
    return snap_path


def save_readme(path: Path, content: str) -> None:
    _atomic_write_text(path / "README.md", content)


def read_readme(path: Path) -> str | None:
    readme_path = path / "README.md"
    if not readme_path.exists():
        return None
    return readme_path.read_text(encoding="utf-8")


def iter_problem_meta() -> Iterator[dict]:
    """Yield every problem's meta.json content, for stats/streak/README generation."""
    if not config.PROBLEMS_DIR.exists():
        return
    for entry in sorted(config.PROBLEMS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        meta = load_problem_meta(entry)
        if meta:
            yield meta


def save_root_readme(content: str) -> None:
    _atomic_write_text(config.README_PATH, content)


def save_activity_svg(svg: str) -> None:
    _atomic_write_text(config.ACTIVITY_SVG_PATH, svg)
