"""Current / longest daily streak, computed from submission timestamps.

A day "counts" if at least one submission (any status — this mirrors
LeetCode's own submission calendar, which credits activity, not just
acceptance) happened on that local calendar day. Multiple submissions on the
same day only count once. Dates are bucketed in LC_SYNC_TIMEZONE
(default Asia/Kolkata), not UTC and not the machine's local time, so streaks
match what the person actually experienced.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import config


def _local_date(timestamp: int) -> date:
    tz = ZoneInfo(config.LOCAL_TIMEZONE)
    return datetime.fromtimestamp(timestamp, tz=tz).date()


def unique_active_days(timestamps: list[int]) -> list[date]:
    days = sorted({_local_date(ts) for ts in timestamps})
    return days


def compute_streaks(timestamps: list[int], today: date | None = None) -> dict:
    """Returns {'current_streak': int, 'longest_streak': int, 'active_days': int}."""
    days = unique_active_days(timestamps)
    if not days:
        return {"current_streak": 0, "longest_streak": 0, "active_days": 0}

    if today is None:
        today = datetime.now(tz=ZoneInfo(config.LOCAL_TIMEZONE)).date()

    # Longest streak: scan the sorted unique days for consecutive runs.
    longest = 1
    run = 1
    for prev, curr in zip(days, days[1:]):
        if curr - prev == timedelta(days=1):
            run += 1
        else:
            longest = max(longest, run)
            run = 1
    longest = max(longest, run)

    # Current streak: walk backwards from the most recent active day, but
    # only if that day is today or yesterday (otherwise the streak is broken).
    last_active = days[-1]
    if today - last_active > timedelta(days=1):
        current = 0
    else:
        current = 1
        day_set = set(days)
        cursor = last_active
        while (cursor - timedelta(days=1)) in day_set:
            current += 1
            cursor -= timedelta(days=1)

    return {"current_streak": current, "longest_streak": longest, "active_days": len(days)}
