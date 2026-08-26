"""A small, dependency-free HTML -> Markdown converter.

LeetCode's `question.content` field is a fairly small, consistent subset of
HTML (p, b/strong, i/em, u, code, pre, ul/ol/li, sup/sub, br, img, table).
Pulling in a full HTML parsing library (BeautifulSoup, html2text, ...) for
this one field would violate the "minimal dependencies" requirement, so this
converter is built on Python's built-in `html.parser`.

It is intentionally conservative: unknown tags are ignored (their text is
kept, structure is dropped) rather than guessed at, and it never invents
content. Images are replaced with a short placeholder + note, since we do
not download/embed external images (see README "Known limitations").
"""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser


class _Converter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self._list_stack: list[str] = []  # 'ul' or 'ol'
        self._ol_counters: list[int] = []
        self._pre_depth = 0
        self._skip_depth = 0  # inside <style>/<script>
        self._had_image = False

    # -- helpers ---------------------------------------------------------
    def _write(self, text: str) -> None:
        if self._skip_depth:
            return
        self.out.append(text)

    # -- HTMLParser hooks --------------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self._skip_depth += 1
            return
        if tag == "p":
            self._write("\n\n")
        elif tag in ("strong", "b"):
            self._write("**")
        elif tag in ("em", "i"):
            self._write("*")
        elif tag == "code":
            self._write("`")
        elif tag == "pre":
            self._pre_depth += 1
            self._write("\n\n```\n")
        elif tag == "ul":
            self._list_stack.append("ul")
        elif tag == "ol":
            self._list_stack.append("ol")
            self._ol_counters.append(0)
        elif tag == "li":
            depth = max(len(self._list_stack) - 1, 0)
            indent = "  " * depth
            if self._list_stack and self._list_stack[-1] == "ol":
                self._ol_counters[-1] += 1
                self._write(f"\n{indent}{self._ol_counters[-1]}. ")
            else:
                self._write(f"\n{indent}- ")
        elif tag == "br":
            self._write("\n")
        elif tag == "sup":
            self._write("^")
        elif tag == "sub":
            self._write("_")
        elif tag == "img":
            self._had_image = True
            self._write("\n\n*[image omitted — view on LeetCode]*\n\n")
        elif tag in ("table", "tr", "td", "th"):
            # Tables in problem statements are rare; fall back to plain text
            # with cell separators rather than reconstructing a markdown table.
            if tag in ("td", "th"):
                self._write(" | ")
            elif tag == "tr":
                self._write("\n")

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._skip_depth = max(self._skip_depth - 1, 0)
            return
        if tag in ("strong", "b"):
            self._write("**")
        elif tag in ("em", "i"):
            self._write("*")
        elif tag == "code":
            self._write("`")
        elif tag == "pre":
            self._pre_depth = max(self._pre_depth - 1, 0)
            self._write("\n```\n\n")
        elif tag in ("ul", "ol"):
            if self._list_stack:
                self._list_stack.pop()
            if tag == "ol" and self._ol_counters:
                self._ol_counters.pop()
            self._write("\n")

    def handle_data(self, data):
        if self._pre_depth:
            self._write(data)
        else:
            self._write(data)


def html_to_markdown(raw_html: str) -> str:
    """Convert a LeetCode problem-statement HTML fragment to Markdown."""
    if not raw_html:
        return ""
    conv = _Converter()
    conv.feed(raw_html)
    conv.close()
    text = "".join(conv.out)
    text = html.unescape(text)
    # Collapse excessive blank lines produced by nested tags.
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
