"""Thin client around LeetCode's unofficial GraphQL endpoint.

LeetCode has no official public API for a user's own submissions or
submission code. Every community tool (leetcode-query, alfa-leetcode-api,
glsync, leetcode-cli, ...) uses the same approach this module uses: the
website's own GraphQL endpoint (`https://leetcode.com/graphql`), authenticated
with the `LEETCODE_SESSION` + `csrftoken` cookies copied from a logged-in
browser session. There is no supported way to get a user's submitted code
without those cookies — LeetCode does not expose it any other way.

Two categories of query are used:

* Authenticated (require cookies): `submissionList`, `submissionDetails`.
  These are the only source for *your* submission history and code.
* Public (work with or without cookies): `question` (problem content).

If LeetCode changes these fields, calls will fail loudly with a clear error
rather than silently returning wrong data — see `LeetCodeAPIError`.
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from typing import Any, Optional

import requests

from . import config

log = logging.getLogger("lc_sync.api")


class LeetCodeAPIError(RuntimeError):
    """Raised when a GraphQL call fails or returns an unexpected shape."""


class LeetCodeAuthError(LeetCodeAPIError):
    """Raised when authenticated queries are attempted without valid cookies."""


_QUERY_SUBMISSION_LIST = """
query submissionList($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String) {
  submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
    lastKey
    hasNext
    submissions {
      id
      title
      titleSlug
      status
      statusDisplay
      lang
      timestamp
      url
      isPending
      memory
      runtime
    }
  }
}
"""

_QUERY_SUBMISSION_DETAILS = """
query submissionDetails($submissionId: Int!) {
  submissionDetails(submissionId: $submissionId) {
    runtime
    runtimeDisplay
    runtimePercentile
    memory
    memoryDisplay
    memoryPercentile
    code
    lang {
      name
      verboseName
    }
    question {
      questionId
      titleSlug
    }
    statusCode
    timestamp
  }
}
"""

_QUERY_QUESTION_CONTENT = """
query questionContent($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    title
    titleSlug
    content
    difficulty
    topicTags {
      name
      slug
    }
    isPaidOnly
    exampleTestcases
    hints
    similarQuestions
  }
}
"""


@dataclass
class Credentials:
    session: str
    csrf_token: str

    @property
    def is_present(self) -> bool:
        return bool(self.session and self.csrf_token)


class LeetCodeClient:
    def __init__(self, credentials: Optional[Credentials] = None):
        self.credentials = credentials
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Referer": config.BASE_URL,
                "User-Agent": "lc-sync/1.0 (+https://github.com; personal LeetCode archive tool)",
            }
        )
        if credentials and credentials.is_present:
            self._session.cookies.set("LEETCODE_SESSION", credentials.session, domain="leetcode.com")
            self._session.cookies.set("csrftoken", credentials.csrf_token, domain="leetcode.com")
            self._session.headers["x-csrftoken"] = credentials.csrf_token
        self._last_request_at = 0.0

    # -- low level -----------------------------------------------------

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        wait = config.REQUEST_DELAY_SECONDS - elapsed
        if wait > 0:
            time.sleep(wait)

    def _graphql(self, query: str, variables: dict) -> dict:
        self._throttle()
        last_error: Optional[Exception] = None
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                resp = self._session.post(
                    config.GRAPHQL_URL,
                    json={"query": query, "variables": variables},
                    timeout=config.REQUEST_TIMEOUT_SECONDS,
                )
                self._last_request_at = time.monotonic()
                if resp.status_code == 429:
                    raise LeetCodeAPIError("Rate limited by LeetCode (HTTP 429)")
                if resp.status_code in (401, 403):
                    raise LeetCodeAuthError(
                        f"LeetCode rejected the request (HTTP {resp.status_code}). "
                        "LEETCODE_SESSION / LEETCODE_CSRF_TOKEN are likely missing or expired."
                    )
                resp.raise_for_status()
                payload = resp.json()
                if "errors" in payload and payload["errors"]:
                    raise LeetCodeAPIError(f"GraphQL error: {payload['errors']}")
                return payload.get("data") or {}
            except (requests.RequestException, LeetCodeAPIError) as exc:
                last_error = exc
                if isinstance(exc, LeetCodeAuthError):
                    raise
                if attempt < config.MAX_RETRIES:
                    log.warning("Request failed (attempt %d/%d): %s", attempt, config.MAX_RETRIES, exc)
                    time.sleep(config.RETRY_BACKOFF_SECONDS * attempt)
        raise LeetCodeAPIError(f"GraphQL request failed after {config.MAX_RETRIES} attempts: {last_error}")

    # -- authenticated ---------------------------------------------------

    def _require_auth(self) -> None:
        if not (self.credentials and self.credentials.is_present):
            raise LeetCodeAuthError(
                "This operation requires LEETCODE_SESSION and LEETCODE_CSRF_TOKEN. "
                "Set them as environment variables / GitHub Secrets."
            )

    def fetch_submission_page(
        self, offset: int, limit: int = config.SUBMISSIONS_PAGE_SIZE, last_key: Optional[str] = None
    ) -> dict:
        """One page of the authenticated user's full submission history,
        newest first. Returns {'submissions': [...], 'hasNext': bool, 'lastKey': str}.
        """
        self._require_auth()
        data = self._graphql(
            _QUERY_SUBMISSION_LIST,
            {"offset": offset, "limit": limit, "lastKey": last_key, "questionSlug": None},
        )
        block = data.get("submissionList")
        if block is None:
            raise LeetCodeAPIError("submissionList query returned no data — schema may have changed.")
        return block

    def fetch_submission_details(self, submission_id: int) -> Optional[dict]:
        """Full detail (including code) for one submission id.

        Returns None (not raises) when LeetCode has no detail for this id,
        since older/edge-case submissions can legitimately lack detail — we
        must not fabricate code we couldn't retrieve.
        """
        self._require_auth()
        data = self._graphql(_QUERY_SUBMISSION_DETAILS, {"submissionId": submission_id})
        return data.get("submissionDetails")

    # -- public ------------------------------------------------------------

    def fetch_question_content(self, title_slug: str) -> Optional[dict]:
        """Problem statement + metadata for a problem. Works without auth for
        free problems; paid-only problems will come back with content=None,
        which we surface rather than invent.
        """
        data = self._graphql(_QUERY_QUESTION_CONTENT, {"titleSlug": title_slug})
        return data.get("question")
