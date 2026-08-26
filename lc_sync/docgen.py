"""Builds problems/<num>-<slug>/README.md.

The file always has exactly two regions, each wrapped in HTML-comment
markers (see config.AUTO_START/END and PERSONAL_START/END):

  AUTO block      — fully regenerated every sync from meta.json. Never hand-edit.
  PERSONAL block  — written once with a template, then left completely alone
                     by every future sync. This is where "My Approach",
                     "Complexity", "My Notes" and "What I Learned" live.

Regeneration works by re-reading the existing file (if any), extracting the
PERSONAL block byte-for-byte, and reassembling AUTO(new) + PERSONAL(old).
If no file exists yet, PERSONAL gets a starter template.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import config, storage

_PERSONAL_TEMPLATE = f"""{config.PERSONAL_START}

### My Approach

_How I personally solved it — write this yourself._

### Complexity

- Time complexity:
- Space complexity:

### My Notes

_Mistakes made, edge cases missed, anything worth remembering._

### What I Learned

_Anything useful for next time._

{config.PERSONAL_END}
"""

_PERSONAL_RE = re.compile(
    re.escape(config.PERSONAL_START) + r".*?" + re.escape(config.PERSONAL_END),
    re.DOTALL,
)


def _extract_existing_personal_block(existing_content: str | None) -> str:
    if not existing_content:
        return _PERSONAL_TEMPLATE.strip()
    match = _PERSONAL_RE.search(existing_content)
    if match:
        return match.group(0)
    # File existed but somehow lost its markers (e.g. hand-edited away) —
    # never discard the person's writing: keep everything after the AUTO
    # block, wrapped fresh, rather than silently dropping it.
    auto_end_idx = existing_content.find(config.AUTO_END)
    if auto_end_idx != -1:
        trailing = existing_content[auto_end_idx + len(config.AUTO_END):].strip()
        if trailing:
            return f"{config.PERSONAL_START}\n\n{trailing}\n\n{config.PERSONAL_END}\n"
    return _PERSONAL_TEMPLATE.strip()


def _status_badge(status: str) -> str:
    return {
        "Accepted": "✅ Accepted",
        "Wrong Answer": "❌ Wrong Answer",
        "Time Limit Exceeded": "⏱️ Time Limit Exceeded",
        "Runtime Error": "💥 Runtime Error",
        "Memory Limit Exceeded": "💾 Memory Limit Exceeded",
        "Compile Error": "🛠️ Compile Error",
    }.get(status, status)


def _submission_table(submissions: list[dict]) -> str:
    if not submissions:
        return "_No submissions synced yet._"
    rows = [
        "| Date | Status | Language | Runtime | Memory | Code |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for sub in sorted(submissions, key=lambda s: s["timestamp"], reverse=True):
        from datetime import datetime, timezone

        date_str = datetime.fromtimestamp(sub["timestamp"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lang_name, ext = config.language_display_and_ext(sub["lang"])
        code_link = "—"
        if sub.get("code_saved"):
            fname = f"submissions/{sub['timestamp']}_{sub['status'].replace(' ', '-')}_{sub['id']}.{ext}"
            code_link = f"[view]({fname})"
        rows.append(
            f"| {date_str} | {_status_badge(sub['status'])} | {lang_name} | "
            f"{sub.get('runtime') or '—'} | {sub.get('memory') or '—'} | {code_link} |"
        )
    return "\n".join(rows)


def _latest_submission(submissions: list[dict]) -> dict | None:
    if not submissions:
        return None
    return max(submissions, key=lambda s: s["timestamp"])


def build_auto_block(meta: dict) -> str:
    difficulty = meta.get("difficulty") or "Unknown"
    topics = meta.get("topics") or []
    submissions = meta.get("submissions") or []
    latest = _latest_submission(submissions)

    lines = [config.AUTO_START, ""]
    lines.append(f"# {meta.get('number', '?')}. {meta.get('title', meta.get('slug', 'Unknown Problem'))}")
    lines.append("")
    lines.append(
        f"**Difficulty:** {difficulty}  |  **LeetCode:** [{meta.get('slug')}]({meta.get('url')})"
    )
    if topics:
        lines.append(f"**Topics:** {', '.join(topics)}")
    lines.append("")

    if latest:
        lang_name, ext = config.language_display_and_ext(latest["lang"])
        lines.append(f"**Latest submission:** {_status_badge(latest['status'])} in {lang_name} "
                      f"— see [`solution.{ext}`](solution.{ext})")
        lines.append("")

    lines.append("## Problem Statement")
    lines.append("")
    if meta.get("content_markdown"):
        lines.append(meta["content_markdown"])
    elif meta.get("content_unavailable_reason") == "paid-only":
        lines.append(
            "_This problem is LeetCode Premium (paid-only content). The statement could not be "
            f"retrieved; see it on LeetCode: {meta.get('url')}_"
        )
    else:
        lines.append(
            f"_Problem statement could not be reliably retrieved. See it on LeetCode: {meta.get('url')}_"
        )
    lines.append("")

    lines.append("## Submission History")
    lines.append("")
    lines.append(_submission_table(submissions))
    lines.append("")
    lines.append(config.AUTO_END)
    return "\n".join(lines)


def render_problem_readme(meta: dict, existing_content: str | None) -> str:
    auto_block = build_auto_block(meta)
    personal_block = _extract_existing_personal_block(existing_content)
    return f"{auto_block}\n\n{personal_block}\n"


def write_problem_readme(problem_path: Path, meta: dict) -> None:
    existing = storage.read_readme(problem_path)
    content = render_problem_readme(meta, existing)
    storage.save_readme(problem_path, content)
