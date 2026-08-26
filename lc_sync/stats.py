"""Computes every number the README dashboard needs.

Two data sources, deliberately kept distinct:

* ``index['submissions']`` — the flat, global submission log (every
  submission id ever synced). This is the source of truth for
  total/accepted/failed submission counts, since it is never lossy.
* per-problem ``meta.json`` records — the source of truth for difficulty
  and topic tags, since those live on the problem, not the submission.

"Unique problems solved" = distinct problems with >=1 Accepted submission.
This is deliberately different from "problems attempted", to satisfy the
explicit requirement to never conflate unique problems with total
submissions.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import config


def _local_date(timestamp: int) -> date:
    return datetime.fromtimestamp(timestamp, tz=ZoneInfo(config.LOCAL_TIMEZONE)).date()


def _first_accepted(meta: dict) -> dict | None:
    accepted = [s for s in meta.get("submissions", []) if s.get("status") == "Accepted"]
    if not accepted:
        return None
    return min(accepted, key=lambda s: s["timestamp"])


def _latest_submission(meta: dict) -> dict | None:
    subs = meta.get("submissions", [])
    if not subs:
        return None
    return max(subs, key=lambda s: s["timestamp"])


def compute_stats(index: dict, problem_metas: list[dict], today: date | None = None) -> dict:
    if today is None:
        today = datetime.now(tz=ZoneInfo(config.LOCAL_TIMEZONE)).date()

    submissions = index.get("submissions", {})
    total_submissions = len(submissions)
    accepted_submissions = sum(1 for s in submissions.values() if s.get("status") == "Accepted")
    failed_submissions = total_submissions - accepted_submissions

    solved_problems = []
    attempted_problems = 0
    difficulty_counter: Counter = Counter()
    topic_counter: Counter = Counter()
    language_counter: Counter = Counter()
    month_counter: Counter = Counter()
    year_counter: Counter = Counter()

    week_start = today - timedelta(days=today.weekday())  # Monday
    weekly_count = 0
    monthly_count = 0
    yearly_count = 0

    recent: list[dict] = []

    for meta in problem_metas:
        if meta.get("submissions"):
            attempted_problems += 1
        first_acc = _first_accepted(meta)
        latest = _latest_submission(meta)
        if latest:
            recent.append(
                {
                    "title": meta.get("title") or meta.get("slug"),
                    "number": meta.get("number"),
                    "slug": meta.get("slug"),
                    "difficulty": meta.get("difficulty") or "Unknown",
                    "lang": latest.get("lang"),
                    "status": latest.get("status"),
                    "timestamp": latest["timestamp"],
                }
            )
        if not first_acc:
            continue
        solved_problems.append(meta)
        difficulty_counter[meta.get("difficulty") or "Unknown"] += 1
        for topic in meta.get("topics") or []:
            topic_counter[topic] += 1
        lang_name, _ = config.language_display_and_ext(first_acc["lang"])
        language_counter[lang_name] += 1

        d = _local_date(first_acc["timestamp"])
        month_counter[d.strftime("%Y-%m")] += 1
        year_counter[d.strftime("%Y")] += 1
        if d >= week_start:
            weekly_count += 1
        if d.year == today.year and d.month == today.month:
            monthly_count += 1
        if d.year == today.year:
            yearly_count += 1

    recent.sort(key=lambda r: r["timestamp"], reverse=True)

    unique_solved = len(solved_problems)

    def pct(n: int, total: int) -> float:
        return round(100.0 * n / total, 1) if total else 0.0

    return {
        "unique_problems_solved": unique_solved,
        "unique_problems_attempted": attempted_problems,
        "total_submissions": total_submissions,
        "accepted_submissions": accepted_submissions,
        "failed_submissions": failed_submissions,
        "difficulty_counts": dict(difficulty_counter),
        "difficulty_percent": {k: pct(v, unique_solved) for k, v in difficulty_counter.items()},
        "language_counts": dict(language_counter),
        "language_percent": {k: pct(v, unique_solved) for k, v in language_counter.items()},
        "topic_counts": dict(topic_counter.most_common()),
        "month_counts": dict(sorted(month_counter.items())),
        "year_counts": dict(sorted(year_counter.items())),
        "weekly_solved": weekly_count,
        "monthly_solved": monthly_count,
        "yearly_solved": yearly_count,
        "recent": recent[:15],
    }
