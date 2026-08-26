"""Central configuration and constants for lc_sync.

Nothing in here talks to the network. It only defines paths, limits and the
LeetCode language -> file-extension mapping, so every other module has one
place to look things up.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to the repository root; sync.py sets cwd to the repo root)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
PROBLEMS_DIR = REPO_ROOT / "problems"
INDEX_PATH = DATA_DIR / "index.json"
README_PATH = REPO_ROOT / "README.md"
ASSETS_DIR = REPO_ROOT / "assets"
ACTIVITY_SVG_PATH = ASSETS_DIR / "activity.svg"

# ---------------------------------------------------------------------------
# LeetCode endpoints
# ---------------------------------------------------------------------------
GRAPHQL_URL = "https://leetcode.com/graphql"
BASE_URL = "https://leetcode.com"

# ---------------------------------------------------------------------------
# Networking / rate limiting
# ---------------------------------------------------------------------------
# LeetCode has no documented public rate limit for the unofficial GraphQL
# endpoint. Community tools (leetcode-query, alfa-leetcode-api, glsync, etc.)
# converge on ~1 request/second as a safe, unobtrusive default. We stay well
# under that.
REQUEST_DELAY_SECONDS = float(os.environ.get("LC_SYNC_REQUEST_DELAY", "1.2"))
REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 3

# How many submissions to request per page when paging submissionList.
SUBMISSIONS_PAGE_SIZE = 20

# Safety valve: even a --full resync stops after this many pages, so a bug
# can't spin forever against LeetCode's servers.
MAX_SUBMISSION_PAGES = 500

# ---------------------------------------------------------------------------
# Timezone used for streaks / daily / weekly / monthly bucketing
# ---------------------------------------------------------------------------
LOCAL_TIMEZONE = os.environ.get("LC_SYNC_TIMEZONE", "Asia/Kolkata")

# ---------------------------------------------------------------------------
# Content markers used to separate generated content from hand-written notes
# ---------------------------------------------------------------------------
AUTO_START = "<!-- LC-SYNC:AUTO-GENERATED:START — do not edit below, it is overwritten on every sync -->"
AUTO_END = "<!-- LC-SYNC:AUTO-GENERATED:END -->"
PERSONAL_START = "<!-- LC-SYNC:PERSONAL:START — write freely below, this section is never touched by sync -->"
PERSONAL_END = "<!-- LC-SYNC:PERSONAL:END -->"

README_AUTO_START = "<!-- LC-SYNC:README-AUTO:START -->"
README_AUTO_END = "<!-- LC-SYNC:README-AUTO:END -->"

# ---------------------------------------------------------------------------
# LeetCode "lang" slug -> (display name, file extension)
# Values come from LeetCode's own submission-language slugs.
# ---------------------------------------------------------------------------
LANGUAGE_MAP = {
    "python": ("Python", "py"),
    "python3": ("Python3", "py"),
    "pythondata": ("Pandas", "py"),
    "c": ("C", "c"),
    "cpp": ("C++", "cpp"),
    "csharp": ("C#", "cs"),
    "java": ("Java", "java"),
    "javascript": ("JavaScript", "js"),
    "typescript": ("TypeScript", "ts"),
    "php": ("PHP", "php"),
    "swift": ("Swift", "swift"),
    "kotlin": ("Kotlin", "kt"),
    "dart": ("Dart", "dart"),
    "golang": ("Go", "go"),
    "ruby": ("Ruby", "rb"),
    "scala": ("Scala", "scala"),
    "rust": ("Rust", "rs"),
    "racket": ("Racket", "rkt"),
    "erlang": ("Erlang", "erl"),
    "elixir": ("Elixir", "ex"),
    "mysql": ("MySQL", "sql"),
    "mssql": ("MS SQL Server", "sql"),
    "oraclesql": ("Oracle SQL", "sql"),
    "postgresql": ("PostgreSQL", "sql"),
    "bash": ("Bash", "sh"),
}


def language_display_and_ext(lang_slug: str) -> tuple[str, str]:
    """Return (display name, extension) for a LeetCode language slug.

    Unknown/new languages degrade gracefully instead of crashing: we keep the
    raw slug as the display name and use '.txt' so nothing is lost, and the
    caller can see from the name that it wasn't a recognized language.
    """
    return LANGUAGE_MAP.get(lang_slug, (lang_slug, "txt"))


DIFFICULTY_ORDER = ["Easy", "Medium", "Hard"]
