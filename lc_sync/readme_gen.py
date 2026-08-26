"""Builds the root README.md — the LeetCode dashboard.

Like problem READMEs, the dashboard content lives inside
README_AUTO_START/END markers. Anything the person adds outside those
markers (e.g. a personal intro at the top, links at the bottom) survives
every sync untouched.
"""

from __future__ import annotations

import re
from datetime import datetime, date
from zoneinfo import ZoneInfo

from . import config

_AUTO_RE = re.compile(
    re.escape(config.README_AUTO_START) + r".*?" + re.escape(config.README_AUTO_END),
    re.DOTALL,
)

_DEFAULT_HEADER = "# My LeetCode Journey\n\nAn automatically maintained archive of my LeetCode solutions, synced from my submissions.\n"


def _bar(pct: float, width: int = 20) -> str:
    filled = round(width * pct / 100)
    return "█" * filled + "░" * (width - filled)


def _difficulty_section(stats: dict) -> str:
    lines = ["### Difficulty", "", "| Difficulty | Solved | % | |", "| --- | --- | --- | --- |"]
    for diff in config.DIFFICULTY_ORDER:
        n = stats["difficulty_counts"].get(diff, 0)
        p = stats["difficulty_percent"].get(diff, 0.0)
        lines.append(f"| {diff} | {n} | {p}% | `{_bar(p)}` |")
    return "\n".join(lines)


def _language_section(stats: dict) -> str:
    if not stats["language_counts"]:
        return "### Languages\n\n_No solved problems synced yet._"
    lines = ["### Languages", "", "| Language | Solved | % |", "| --- | --- | --- |"]
    for lang, n in sorted(stats["language_counts"].items(), key=lambda kv: -kv[1]):
        p = stats["language_percent"].get(lang, 0.0)
        lines.append(f"| {lang} | {n} | {p}% |")
    return "\n".join(lines)


def _topics_section(stats: dict, top_n: int = 12) -> str:
    if not stats["topic_counts"]:
        return "### Topics\n\n_No topic data synced yet._"
    items = list(stats["topic_counts"].items())[:top_n]
    lines = ["### Topics", ""]
    lines.append(", ".join(f"{name} ({n})" for name, n in items))
    return "\n".join(lines)


def _recent_section(stats: dict) -> str:
    if not stats["recent"]:
        return "### Recent Problems\n\n_No submissions synced yet._"
    lines = ["### Recent Problems", "", "| Problem | Difficulty | Language | Status | Date |", "| --- | --- | --- | --- | --- |"]
    for r in stats["recent"][:10]:
        lang_name, _ = config.language_display_and_ext(r["lang"]) if r["lang"] else ("—", "")
        d = datetime.fromtimestamp(r["timestamp"], tz=ZoneInfo(config.LOCAL_TIMEZONE))
        slug = r.get("slug")
        num = r.get("number")
        link = f"problems/{str(num).zfill(4) if str(num).isdigit() else num}-{slug}/"
        title_link = f"[{r['title']}]({link})" if slug else r["title"]
        lines.append(
            f"| {title_link} | {r['difficulty']} | {lang_name} | {r['status']} | {d.strftime('%b %d, %Y')} |"
        )
    return "\n".join(lines)


def build_auto_block(stats: dict, streaks: dict, chart_svg_relpath: str | None) -> str:
    now = datetime.now(tz=ZoneInfo(config.LOCAL_TIMEZONE))
    lines = [config.README_AUTO_START, ""]
    lines.append("## 📊 LeetCode Dashboard")
    lines.append("")
    lines.append(f"_Last synced: {now.strftime('%Y-%m-%d %H:%M %Z')}_")
    lines.append("")
    lines.append("### Overall Progress")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("| --- | --- |")
    lines.append(f"| Unique problems solved | **{stats['unique_problems_solved']}** |")
    lines.append(f"| Total submissions | {stats['total_submissions']} |")
    lines.append(f"| Accepted submissions | {stats['accepted_submissions']} |")
    lines.append(f"| Failed submissions | {stats['failed_submissions']} |")
    lines.append("")
    lines.append(_difficulty_section(stats))
    lines.append("")
    lines.append(_language_section(stats))
    lines.append("")
    lines.append("### Streak")
    lines.append("")
    lines.append(f"🔥 **Current streak:** {streaks['current_streak']} day(s)  ")
    lines.append(f"🏆 **Longest streak:** {streaks['longest_streak']} day(s)")
    lines.append("")
    lines.append(_recent_section(stats))
    lines.append("")
    lines.append("### Weekly / Monthly / Yearly Progress")
    lines.append("")
    lines.append(f"- This week: **{stats['weekly_solved']}** unique problem(s) solved")
    lines.append(f"- This month: **{stats['monthly_solved']}** unique problem(s) solved")
    lines.append(f"- This year: **{stats['yearly_solved']}** unique problem(s) solved")
    lines.append("")
    if chart_svg_relpath:
        lines.append("### Monthly Activity")
        lines.append("")
        lines.append(f"![Monthly activity]({chart_svg_relpath})")
        lines.append("")
    lines.append(_topics_section(stats))
    lines.append("")
    lines.append(config.README_AUTO_END)
    return "\n".join(lines)


def render_root_readme(existing_content: str | None, stats: dict, streaks: dict, chart_svg_relpath: str | None) -> str:
    auto_block = build_auto_block(stats, streaks, chart_svg_relpath)
    if existing_content and _AUTO_RE.search(existing_content):
        return _AUTO_RE.sub(lambda _m: auto_block, existing_content)
    if existing_content:
        return existing_content.rstrip() + "\n\n" + auto_block + "\n"
    return _DEFAULT_HEADER + "\n" + auto_block + "\n"
