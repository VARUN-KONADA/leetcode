"""Tests for lc_sync.

Runs fully offline: FakeLeetCodeClient stands in for the real API so these
tests never touch the network, and each test works in its own temp
directory so they never touch the real repository's problems/ or data/.

Run with:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lc_sync import config, docgen, stats as stats_mod, storage, streak, htmlmd  # noqa: E402


class FakeLeetCodeClient:
    """Stands in for lc_sync.api.LeetCodeClient. Serves canned data instead
    of calling leetcode.com, so tests are deterministic and offline.
    """

    def __init__(self, submissions: list[dict], questions: dict[str, dict], details: dict[str, dict]):
        # submissions: newest-first list of raw submissionList-shaped dicts
        self._submissions = submissions
        self._questions = questions  # slug -> question dict
        self._details = details      # submission id (str) -> submissionDetails dict

    def fetch_submission_page(self, offset, limit, last_key=None):
        page = self._submissions[offset: offset + limit]
        return {
            "submissions": page,
            "hasNext": offset + limit < len(self._submissions),
            "lastKey": None,
        }

    def fetch_submission_details(self, submission_id: int):
        return self._details.get(str(submission_id))

    def fetch_question_content(self, title_slug: str):
        return self._questions.get(title_slug)


def _sub(id_, slug, title, status, lang, ts, runtime=None, memory=None):
    return {
        "id": id_,
        "title": title,
        "titleSlug": slug,
        "status": 10 if status == "Accepted" else 11,
        "statusDisplay": status,
        "lang": lang,
        "timestamp": ts,
        "url": f"/submissions/detail/{id_}/",
        "isPending": "Not Pending",
        "memory": memory,
        "runtime": runtime,
    }


def _question(slug, number, title, difficulty, topics, content="<p>Statement.</p>", paid=False):
    return {
        "questionId": str(number),
        "questionFrontendId": str(number),
        "title": title,
        "titleSlug": slug,
        "content": None if paid else content,
        "difficulty": difficulty,
        "topicTags": [{"name": t, "slug": t.lower().replace(" ", "-")} for t in topics],
        "isPaidOnly": paid,
        "exampleTestcases": "",
        "hints": [],
        "similarQuestions": "[]",
    }


class TestLanguageMap(unittest.TestCase):
    def test_known_language(self):
        name, ext = config.language_display_and_ext("python3")
        self.assertEqual((name, ext), ("Python3", "py"))

    def test_unknown_language_degrades_gracefully(self):
        name, ext = config.language_display_and_ext("some-future-lang")
        self.assertEqual(name, "some-future-lang")
        self.assertEqual(ext, "txt")


class TestHtmlToMarkdown(unittest.TestCase):
    def test_basic_conversion_no_hallucination(self):
        html = "<p>Given an array <code>nums</code>.</p><ul><li>1 &lt;= n</li></ul>"
        md = htmlmd.html_to_markdown(html)
        self.assertIn("Given an array `nums`.", md)
        self.assertIn("- 1 <= n", md)

    def test_image_is_marked_not_fabricated(self):
        html = "<p>See diagram:</p><img src='x.png'/>"
        md = htmlmd.html_to_markdown(html)
        self.assertIn("image omitted", md)

    def test_empty_input(self):
        self.assertEqual(htmlmd.html_to_markdown(""), "")


class TestStreak(unittest.TestCase):
    TZ = ZoneInfo(config.LOCAL_TIMEZONE)

    def _ts(self, d: date) -> int:
        return int(datetime(d.year, d.month, d.day, 12, 0, tzinfo=self.TZ).timestamp())

    def test_no_submissions(self):
        result = streak.compute_streaks([])
        self.assertEqual(result, {"current_streak": 0, "longest_streak": 0, "active_days": 0})

    def test_consecutive_days_current_and_longest(self):
        today = date(2026, 8, 26)
        days = [today - timedelta(days=i) for i in (0, 1, 2)]  # 3-day streak ending today
        timestamps = [self._ts(d) for d in days]
        result = streak.compute_streaks(timestamps, today=today)
        self.assertEqual(result["current_streak"], 3)
        self.assertEqual(result["longest_streak"], 3)

    def test_streak_broken_by_gap(self):
        today = date(2026, 8, 26)
        days = [today - timedelta(days=5), today - timedelta(days=4), today - timedelta(days=1), today]
        timestamps = [self._ts(d) for d in days]
        result = streak.compute_streaks(timestamps, today=today)
        # today + yesterday = current streak of 2; the two-day run five days
        # ago is the longest (2), tied — longest should be 2 either way.
        self.assertEqual(result["current_streak"], 2)
        self.assertEqual(result["longest_streak"], 2)

    def test_streak_ends_if_last_active_more_than_a_day_ago(self):
        today = date(2026, 8, 26)
        days = [today - timedelta(days=10), today - timedelta(days=9)]
        timestamps = [self._ts(d) for d in days]
        result = streak.compute_streaks(timestamps, today=today)
        self.assertEqual(result["current_streak"], 0)
        self.assertEqual(result["longest_streak"], 2)

    def test_multiple_submissions_same_day_count_once(self):
        today = date(2026, 8, 26)
        ts_morning = self._ts(today)
        ts_evening = ts_morning + 3600 * 8
        result = streak.compute_streaks([ts_morning, ts_evening], today=today)
        self.assertEqual(result["active_days"], 1)
        self.assertEqual(result["current_streak"], 1)


class TestDocgenPersonalContentPreservation(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _meta(self, **overrides):
        base = {
            "number": "1",
            "slug": "two-sum",
            "title": "Two Sum",
            "url": "https://leetcode.com/problems/two-sum/",
            "difficulty": "Easy",
            "topics": ["Array", "Hash Table"],
            "content_markdown": "Given an array...",
            "content_unavailable_reason": None,
            "submissions": [
                {"id": "1", "timestamp": 1000, "status": "Wrong Answer", "lang": "python3",
                 "runtime": None, "memory": None, "code_saved": True},
                {"id": "2", "timestamp": 2000, "status": "Accepted", "lang": "python3",
                 "runtime": "52 ms", "memory": "16.4 MB", "code_saved": True},
            ],
        }
        base.update(overrides)
        return base

    def test_first_generation_creates_template_personal_section(self):
        content = docgen.render_problem_readme(self._meta(), existing_content=None)
        self.assertIn(config.AUTO_START, content)
        self.assertIn(config.PERSONAL_START, content)
        self.assertIn("My Approach", content)

    def test_personal_content_survives_regeneration(self):
        first = docgen.render_problem_readme(self._meta(), existing_content=None)
        edited = first.replace(
            "_How I personally solved it — write this yourself._",
            "I used a hash map to store complements. Learned to watch for duplicate values.",
        )
        # Simulate a new submission changing the AUTO block on next sync.
        new_meta = self._meta()
        new_meta["submissions"].append(
            {"id": "3", "timestamp": 3000, "status": "Accepted", "lang": "java",
             "runtime": "3 ms", "memory": "40 MB", "code_saved": True}
        )
        regenerated = docgen.render_problem_readme(new_meta, existing_content=edited)
        self.assertIn("I used a hash map to store complements.", regenerated)
        self.assertIn("java" if False else "Java", regenerated)  # AUTO block picked up the new submission

    def test_latest_submission_identified(self):
        content = docgen.render_problem_readme(self._meta(), existing_content=None)
        self.assertIn("Latest submission:", content)
        self.assertIn("✅ Accepted", content)

    def test_no_duplicate_history_rows_for_two_submissions(self):
        content = docgen.render_problem_readme(self._meta(), existing_content=None)
        self.assertEqual(content.count("52 ms"), 1)


class TestStatsUniqueVsTotal(unittest.TestCase):
    def test_two_sum_three_submissions_one_unique(self):
        """The exact example from the spec: Wrong, Wrong, Accepted =>
        unique problems solved = 1, total submissions = 3, accepted = 1."""
        index = {
            "last_synced_timestamp": 3000,
            "submissions": {
                "1": {"problem_slug": "two-sum", "timestamp": 1000, "status": "Wrong Answer", "lang": "python3"},
                "2": {"problem_slug": "two-sum", "timestamp": 2000, "status": "Wrong Answer", "lang": "python3"},
                "3": {"problem_slug": "two-sum", "timestamp": 3000, "status": "Accepted", "lang": "python3"},
            },
        }
        problem_metas = [
            {
                "number": "1", "slug": "two-sum", "title": "Two Sum", "difficulty": "Easy",
                "topics": ["Array", "Hash Table"],
                "submissions": [
                    {"id": "1", "timestamp": 1000, "status": "Wrong Answer", "lang": "python3"},
                    {"id": "2", "timestamp": 2000, "status": "Wrong Answer", "lang": "python3"},
                    {"id": "3", "timestamp": 3000, "status": "Accepted", "lang": "python3"},
                ],
            }
        ]
        result = stats_mod.compute_stats(index, problem_metas, today=date(2026, 1, 1))
        self.assertEqual(result["unique_problems_solved"], 1)
        self.assertEqual(result["total_submissions"], 3)
        self.assertEqual(result["accepted_submissions"], 1)
        self.assertEqual(result["failed_submissions"], 2)

    def test_difficulty_and_topic_breakdown(self):
        index = {"submissions": {
            "1": {"problem_slug": "two-sum", "timestamp": 1000, "status": "Accepted", "lang": "python3"},
            "2": {"problem_slug": "valid-parens", "timestamp": 1500, "status": "Accepted", "lang": "cpp"},
        }}
        metas = [
            {"number": "1", "slug": "two-sum", "title": "Two Sum", "difficulty": "Easy",
             "topics": ["Array"], "submissions": [{"id": "1", "timestamp": 1000, "status": "Accepted", "lang": "python3"}]},
            {"number": "20", "slug": "valid-parens", "title": "Valid Parentheses", "difficulty": "Easy",
             "topics": ["Stack"], "submissions": [{"id": "2", "timestamp": 1500, "status": "Accepted", "lang": "cpp"}]},
        ]
        result = stats_mod.compute_stats(index, metas, today=date(2026, 1, 1))
        self.assertEqual(result["difficulty_counts"], {"Easy": 2})
        self.assertEqual(result["language_counts"], {"Python3": 1, "C++": 1})


class TestDedupIdempotency(unittest.TestCase):
    """Verifies index.json based dedup: syncing the same submission twice
    must not create a second history entry."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self._orig_paths = (config.REPO_ROOT, config.DATA_DIR, config.PROBLEMS_DIR, config.INDEX_PATH, config.README_PATH, config.ASSETS_DIR, config.ACTIVITY_SVG_PATH)
        config.REPO_ROOT = self.tmp
        config.DATA_DIR = self.tmp / "data"
        config.PROBLEMS_DIR = self.tmp / "problems"
        config.INDEX_PATH = config.DATA_DIR / "index.json"
        config.README_PATH = self.tmp / "README.md"
        config.ASSETS_DIR = self.tmp / "assets"
        config.ACTIVITY_SVG_PATH = config.ASSETS_DIR / "activity.svg"

    def tearDown(self):
        (config.REPO_ROOT, config.DATA_DIR, config.PROBLEMS_DIR, config.INDEX_PATH, config.README_PATH, config.ASSETS_DIR, config.ACTIVITY_SVG_PATH) = self._orig_paths

    def test_saving_index_twice_is_idempotent(self):
        index = storage.load_index()
        index["submissions"]["100"] = {"problem_slug": "two-sum", "timestamp": 1, "status": "Accepted", "lang": "python3"}
        storage.save_index(index)

        reloaded = storage.load_index()
        self.assertIn("100", reloaded["submissions"])
        self.assertEqual(len(reloaded["submissions"]), 1)

        # "Re-sync": same id again should not duplicate.
        reloaded["submissions"]["100"] = {"problem_slug": "two-sum", "timestamp": 1, "status": "Accepted", "lang": "python3"}
        storage.save_index(reloaded)
        final = storage.load_index()
        self.assertEqual(len(final["submissions"]), 1)

    def test_problem_meta_round_trip(self):
        path = storage.problem_dir("1", "two-sum")
        meta = {"number": "1", "slug": "two-sum", "submissions": []}
        storage.save_problem_meta(path, meta)
        loaded = storage.load_problem_meta(path)
        self.assertEqual(loaded["slug"], "two-sum")


class TestFullSyncRun(unittest.TestCase):
    """End-to-end test of sync.py's core logic against the FakeLeetCodeClient,
    covering: submission detection, language detection, solution saving,
    duplicate detection, and multi-submission history — all in one temp repo.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self._orig = (config.REPO_ROOT, config.DATA_DIR, config.PROBLEMS_DIR, config.INDEX_PATH,
                      config.README_PATH, config.ASSETS_DIR, config.ACTIVITY_SVG_PATH)
        config.REPO_ROOT = self.tmp
        config.DATA_DIR = self.tmp / "data"
        config.PROBLEMS_DIR = self.tmp / "problems"
        config.INDEX_PATH = config.DATA_DIR / "index.json"
        config.README_PATH = self.tmp / "README.md"
        config.ASSETS_DIR = self.tmp / "assets"
        config.ACTIVITY_SVG_PATH = config.ASSETS_DIR / "activity.svg"

        sys.path.insert(0, str(ROOT))
        import importlib
        global sync
        import sync as sync  # type: ignore
        importlib.reload(sync)
        self.sync = sync

    def tearDown(self):
        (config.REPO_ROOT, config.DATA_DIR, config.PROBLEMS_DIR, config.INDEX_PATH,
         config.README_PATH, config.ASSETS_DIR, config.ACTIVITY_SVG_PATH) = self._orig

    def test_two_sum_wrong_wrong_accepted_then_rerun_is_idempotent(self):
        submissions = [  # newest first, as LeetCode returns them
            _sub("3", "two-sum", "Two Sum", "Accepted", "python3", 3000, runtime="52 ms", memory="16.4 MB"),
            _sub("2", "two-sum", "Two Sum", "Wrong Answer", "python3", 2000),
            _sub("1", "two-sum", "Two Sum", "Wrong Answer", "python3", 1000),
        ]
        questions = {"two-sum": _question("two-sum", 1, "Two Sum", "Easy", ["Array", "Hash Table"])}
        details = {
            "1": {"code": "class Solution: pass  # wrong v1", "runtimeDisplay": None, "memoryDisplay": None},
            "2": {"code": "class Solution: pass  # wrong v2", "runtimeDisplay": None, "memoryDisplay": None},
            "3": {"code": "class Solution:\n    def twoSum(self, nums, target):\n        return [0, 1]",
                  "runtimeDisplay": "52 ms", "memoryDisplay": "16.4 MB"},
        }
        client = FakeLeetCodeClient(submissions, questions, details)

        index = storage.load_index()
        new_subs = self.sync._fetch_new_submissions(client, index, full=False, limit=None)
        self.assertEqual(len(new_subs), 3)
        new_subs.sort(key=lambda s: s["timestamp"])

        summary = self.sync.SyncSummary()
        for s in new_subs:
            ok = self.sync._process_submission(client, s, dry_run=False, summary=summary)
            self.assertTrue(ok)
            index["submissions"][s["id"]] = {"problem_slug": s["titleSlug"], "timestamp": s["timestamp"],
                                              "status": s["status"], "lang": s["lang"]}
        storage.save_index(index)

        # -- assertions after first run --
        problem_path = storage.problem_dir("1", "two-sum")
        self.assertTrue((problem_path / "solution.py").exists())
        solution_code = (problem_path / "solution.py").read_text()
        self.assertIn("return [0, 1]", solution_code)  # latest (Accepted) is the mirrored solution

        meta = storage.load_problem_meta(problem_path)
        self.assertEqual(len(meta["submissions"]), 3)  # full history kept
        self.assertEqual(summary.synced, 1)  # one new problem
        self.assertEqual(summary.updated, 2)  # two more submissions to the same problem

        submission_files = sorted((problem_path / "submissions").glob("*.py"))
        self.assertEqual(len(submission_files), 3)  # no history lost

        # -- second run: nothing new should happen (idempotency) --
        index2 = storage.load_index()
        new_subs_2 = self.sync._fetch_new_submissions(client, index2, full=False, limit=None)
        self.assertEqual(len(new_subs_2), 0)

        meta_after = storage.load_problem_meta(problem_path)
        self.assertEqual(len(meta_after["submissions"]), 3)  # still 3, not 6

    def test_readme_dashboard_generation(self):
        submissions = [_sub("1", "two-sum", "Two Sum", "Accepted", "python3", 1000)]
        questions = {"two-sum": _question("two-sum", 1, "Two Sum", "Easy", ["Array"])}
        details = {"1": {"code": "print(1)", "runtimeDisplay": "1 ms", "memoryDisplay": "10 MB"}}
        client = FakeLeetCodeClient(submissions, questions, details)

        index = storage.load_index()
        new_subs = self.sync._fetch_new_submissions(client, index, full=False, limit=None)
        summary = self.sync.SyncSummary()
        for s in new_subs:
            self.sync._process_submission(client, s, dry_run=False, summary=summary)
            index["submissions"][s["id"]] = {"problem_slug": s["titleSlug"], "timestamp": s["timestamp"],
                                              "status": s["status"], "lang": s["lang"]}
        storage.save_index(index)
        self.sync.regenerate_dashboard(index, dry_run=False)

        self.assertTrue(config.README_PATH.exists())
        readme = config.README_PATH.read_text()
        self.assertIn("Unique problems solved", readme)
        self.assertIn("**1**", readme)


if __name__ == "__main__":
    unittest.main()
