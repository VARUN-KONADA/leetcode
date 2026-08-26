#!/usr/bin/env python3
"""LeetCode -> GitHub repository sync.

Usage:
    python sync.py                 # incremental sync (only new submissions)
    python sync.py --full          # full resync: re-walk entire submission history
    python sync.py --dry-run       # show what would happen, write nothing
    python sync.py --limit 5       # cap how many *new* submissions are processed (testing)
    python sync.py -v              # verbose logging

Required environment variables (see README.md "Required GitHub Secrets"):
    LEETCODE_SESSION       — the `LEETCODE_SESSION` cookie value from a
                              logged-in leetcode.com browser session
    LEETCODE_CSRF_TOKEN    — the `csrftoken` cookie value, same session

This script only ever ADDS or UPDATES files under problems/ and data/, plus
README.md and assets/activity.svg. It never deletes anything, and never
overwrites the personal section of a problem's README. It is safe to run
repeatedly (idempotent) and safe to interrupt (each write is atomic).
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone

from lc_sync import config, docgen, readme_gen, stats as stats_mod, storage, streak, svg
from lc_sync.api import Credentials, LeetCodeAPIError, LeetCodeAuthError, LeetCodeClient

log = logging.getLogger("lc_sync")


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )


def _credentials_from_env() -> Credentials:
    return Credentials(
        session=os.environ.get("LEETCODE_SESSION", ""),
        csrf_token=os.environ.get("LEETCODE_CSRF_TOKEN", ""),
    )


class SyncSummary:
    def __init__(self):
        self.synced = 0   # new problems created
        self.updated = 0  # existing problems that got a new submission
        self.skipped = 0  # submissions already known, or non-actionable
        self.failed = 0
        self.failures: list[str] = []

    def report(self) -> str:
        lines = [
            "",
            "===== Sync summary =====",
            f"New problems created : {self.synced}",
            f"Problems updated     : {self.updated}",
            f"Submissions skipped  : {self.skipped}",
            f"Failures             : {self.failed}",
        ]
        if self.failures:
            lines.append("Failure details:")
            lines.extend(f"  - {f}" for f in self.failures)
        return "\n".join(lines)


def _normalize_submission(raw: dict) -> dict:
    return {
        "id": str(raw["id"]),
        "titleSlug": raw["titleSlug"],
        "title": raw.get("title"),
        "status": raw.get("statusDisplay") or "Unknown",
        "lang": raw.get("lang"),
        "timestamp": int(raw["timestamp"]),
        "runtime": raw.get("runtime") or None,
        "memory": raw.get("memory") or None,
    }


def _fetch_new_submissions(client: LeetCodeClient, index: dict, full: bool, limit: int | None) -> list[dict]:
    """Page through submissionList newest-first, returning normalized
    submissions not already present in index, newest first.

    Incremental mode stops as soon as it sees a submission id already in the
    index (everything older is guaranteed already synced). Full mode walks
    every page up to the safety cap, still skipping known ids.
    """
    known_ids = set(index.get("submissions", {}).keys())
    collected: list[dict] = []
    offset = 0
    last_key = None
    pages = 0

    while pages < config.MAX_SUBMISSION_PAGES:
        pages += 1
        page = client.fetch_submission_page(offset=offset, limit=config.SUBMISSIONS_PAGE_SIZE, last_key=last_key)
        raw_subs = page.get("submissions") or []
        if not raw_subs:
            break

        hit_known = False
        for raw in raw_subs:
            sub = _normalize_submission(raw)
            if sub["id"] in known_ids:
                hit_known = True
                if not full:
                    break
                continue
            collected.append(sub)
            if limit and len(collected) >= limit:
                return collected

        if hit_known and not full:
            break
        if not page.get("hasNext"):
            break
        offset += config.SUBMISSIONS_PAGE_SIZE
        last_key = page.get("lastKey")

    return collected


def _get_or_fetch_question(client: LeetCodeClient, meta: dict | None, slug: str) -> dict:
    """Returns a dict with question fields; reuses meta.json's cached copy
    when we already have it (problem statements don't change), otherwise
    fetches fresh. Never fabricates data on failure — records the reason.
    """
    if meta and meta.get("content_fetched"):
        return meta

    result = {
        "number": (meta or {}).get("number", "0000"),
        "title": (meta or {}).get("title", slug),
        "slug": slug,
        "url": f"{config.BASE_URL}/problems/{slug}/",
        "difficulty": (meta or {}).get("difficulty"),
        "topics": (meta or {}).get("topics", []),
        "content_markdown": (meta or {}).get("content_markdown"),
        "content_unavailable_reason": (meta or {}).get("content_unavailable_reason"),
        "content_fetched": False,
    }
    try:
        q = client.fetch_question_content(slug)
    except LeetCodeAPIError as exc:
        log.warning("Could not fetch problem content for %s: %s", slug, exc)
        result["content_unavailable_reason"] = "fetch-failed"
        return result

    if not q:
        result["content_unavailable_reason"] = "not-found"
        return result

    from lc_sync.htmlmd import html_to_markdown

    if q.get("isPaidOnly") and not q.get("content"):
        result["content_unavailable_reason"] = "paid-only"
    else:
        result["content_markdown"] = html_to_markdown(q.get("content") or "")
        result["content_unavailable_reason"] = None
        result["content_fetched"] = True

    result["number"] = q.get("questionFrontendId") or result["number"]
    result["title"] = q.get("title") or result["title"]
    result["difficulty"] = q.get("difficulty") or result["difficulty"]
    result["topics"] = [t["name"] for t in (q.get("topicTags") or [])]
    return result


def _process_submission(
    client: LeetCodeClient,
    sub: dict,
    dry_run: bool,
    summary: SyncSummary,
) -> bool:
    """Handles one new submission end-to-end. Returns True if it was
    successfully synced (or found to already be synced) — i.e. it is safe
    to record in index.json so it is never re-fetched. Returns False on
    failure, so the submission is retried on the next run instead of being
    silently dropped.
    """
    slug = sub["titleSlug"]
    try:
        # Find an existing problem dir for this slug, if any (number may
        # not be known yet, so search by suffix).
        existing_path = None
        existing_meta = None
        if config.PROBLEMS_DIR.exists():
            for entry in config.PROBLEMS_DIR.iterdir():
                if entry.is_dir() and entry.name.endswith(f"-{slug}"):
                    existing_path = entry
                    existing_meta = storage.load_problem_meta(entry)
                    break

        question = _get_or_fetch_question(client, existing_meta, slug)
        problem_path = storage.problem_dir(question["number"], slug)

        # If the directory name changes because we now know the real
        # number (e.g. it was created as 0000-slug on a transient failure),
        # migrate it rather than duplicating.
        if existing_path and existing_path != problem_path and not dry_run:
            if not problem_path.exists():
                existing_path.rename(problem_path)
            else:
                problem_path = existing_path  # avoid clobbering; keep old name

        meta = existing_meta or {
            "number": question["number"],
            "slug": slug,
            "title": question["title"],
            "url": question["url"],
            "difficulty": question.get("difficulty"),
            "topics": question.get("topics", []),
            "content_markdown": question.get("content_markdown"),
            "content_unavailable_reason": question.get("content_unavailable_reason"),
            "content_fetched": question.get("content_fetched", False),
            "submissions": [],
        }
        # Keep metadata fresh if we fetched it this run. content_fetched and
        # content_unavailable_reason are always overwritten (they must be
        # able to flip back to success); the rest only overwrite when we
        # actually have a value, so a failed fetch never blanks out data we
        # already had cached from an earlier successful sync.
        meta["content_fetched"] = question.get("content_fetched", meta.get("content_fetched", False))
        meta["content_unavailable_reason"] = question.get("content_unavailable_reason")
        for key in ("title", "url", "difficulty", "topics", "content_markdown", "number"):
            value = question.get(key)
            if value not in (None, []):
                meta[key] = value

        already_ids = {s["id"] for s in meta["submissions"]}
        is_new_problem = existing_path is None

        if sub["id"] in already_ids:
            summary.skipped += 1
            return True

        # Fetch full submission detail (code) — best effort, never fabricated.
        code = None
        try:
            detail = client.fetch_submission_details(int(sub["id"]))
            if detail and detail.get("code"):
                code = detail["code"]
                if not sub.get("runtime") and detail.get("runtimeDisplay"):
                    sub["runtime"] = detail["runtimeDisplay"]
                if not sub.get("memory") and detail.get("memoryDisplay"):
                    sub["memory"] = detail["memoryDisplay"]
        except LeetCodeAuthError:
            raise
        except LeetCodeAPIError as exc:
            log.warning("Could not fetch code for submission %s (%s): %s", sub["id"], slug, exc)

        sub_record = {
            "id": sub["id"],
            "timestamp": sub["timestamp"],
            "status": sub["status"],
            "lang": sub["lang"],
            "runtime": sub.get("runtime"),
            "memory": sub.get("memory"),
            "code_saved": bool(code),
        }
        meta["submissions"].append(sub_record)
        meta["last_synced_at"] = datetime.now(tz=timezone.utc).isoformat()

        if dry_run:
            log.info("[dry-run] would sync submission %s for %s (%s)", sub["id"], slug, sub["status"])
            return True

        problem_path.mkdir(parents=True, exist_ok=True)
        lang_name, ext = config.language_display_and_ext(sub["lang"])
        if code:
            storage.save_submission_snapshot(problem_path, sub["id"], sub["timestamp"], sub["status"], code, ext)
            latest = max(meta["submissions"], key=lambda s: s["timestamp"])
            if latest["id"] == sub["id"]:
                storage.save_solution_file(problem_path, code, ext)

        storage.save_problem_meta(problem_path, meta)
        docgen.write_problem_readme(problem_path, meta)

        if is_new_problem:
            summary.synced += 1
        else:
            summary.updated += 1
        return True

    except LeetCodeAuthError:
        raise
    except Exception as exc:  # noqa: BLE001 - one bad problem must not kill the run
        log.error("Failed to sync submission %s (%s): %s", sub.get("id"), slug, exc)
        summary.failed += 1
        summary.failures.append(f"submission {sub.get('id')} ({slug}): {exc}")
        return False


def regenerate_dashboard(index: dict, dry_run: bool) -> None:
    problem_metas = list(storage.iter_problem_meta())
    computed_stats = stats_mod.compute_stats(index, problem_metas)
    timestamps = [s["timestamp"] for s in index.get("submissions", {}).values()]
    streaks = streak.compute_streaks(timestamps)

    chart_relpath = None
    if computed_stats["month_counts"]:
        svg_content = svg.monthly_activity_svg(computed_stats["month_counts"])
        chart_relpath = "assets/activity.svg"
        if not dry_run:
            storage.save_activity_svg(svg_content)

    existing_readme = config.README_PATH.read_text(encoding="utf-8") if config.README_PATH.exists() else None
    new_readme = readme_gen.render_root_readme(existing_readme, computed_stats, streaks, chart_relpath)

    if dry_run:
        log.info("[dry-run] would rewrite README.md dashboard")
    else:
        storage.save_root_readme(new_readme)

    log.info(
        "Dashboard: %d unique solved / %d submissions / streak %d (longest %d)",
        computed_stats["unique_problems_solved"],
        computed_stats["total_submissions"],
        streaks["current_streak"],
        streaks["longest_streak"],
    )


def run(args: argparse.Namespace) -> int:
    _setup_logging(args.verbose)
    os.chdir(config.REPO_ROOT)

    creds = _credentials_from_env()
    if not creds.is_present:
        log.error(
            "LEETCODE_SESSION and LEETCODE_CSRF_TOKEN must be set as environment variables. "
            "See README.md for how to obtain them."
        )
        return 2

    client = LeetCodeClient(creds)
    index = storage.load_index()
    summary = SyncSummary()

    try:
        new_submissions = _fetch_new_submissions(client, index, full=args.full, limit=args.limit)
    except LeetCodeAuthError as exc:
        log.error(str(exc))
        return 2
    except LeetCodeAPIError as exc:
        log.error("Could not reach LeetCode: %s", exc)
        return 1

    # Oldest first, so submission history and "latest" tracking build up
    # in chronological order even when many submissions land in one run.
    new_submissions.sort(key=lambda s: s["timestamp"])
    log.info("Found %d new submission(s) to sync.", len(new_submissions))

    max_ts_seen = index.get("last_synced_timestamp", 0)
    any_success = False
    for sub in new_submissions:
        try:
            ok = _process_submission(client, sub, args.dry_run, summary)
        except LeetCodeAuthError as exc:
            log.error(str(exc))
            return 2
        if not ok:
            # Leave it out of index.json entirely so it is retried next run
            # instead of being silently lost.
            continue
        any_success = True
        if not args.dry_run:
            index.setdefault("submissions", {})[sub["id"]] = {
                "problem_slug": sub["titleSlug"],
                "timestamp": sub["timestamp"],
                "status": sub["status"],
                "lang": sub["lang"],
            }
            max_ts_seen = max(max_ts_seen, sub["timestamp"])

    if not args.dry_run and any_success:
        index["last_synced_timestamp"] = max_ts_seen
        storage.save_index(index)

    regenerate_dashboard(index, args.dry_run)

    print(summary.report())
    return 0 if summary.failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync LeetCode submissions into this repository.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen; write nothing.")
    parser.add_argument("--full", action="store_true", help="Walk entire submission history, not just new items.")
    parser.add_argument("--limit", type=int, default=None, help="Cap the number of new submissions processed (testing).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging.")
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
