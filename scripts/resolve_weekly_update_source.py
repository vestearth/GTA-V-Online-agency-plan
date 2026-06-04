#!/usr/bin/env python3
"""Resolve the Rockstar Newswire article URL for weekly content refreshes."""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


DEFAULT_NEWSWIRE_URL = "https://www.rockstargames.com/newswire"
DEFAULT_ENV_VAR = "WEEKLY_UPDATE_URL"
ROCKSTAR_ORIGIN = "https://www.rockstargames.com"


class NewswireAnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[tuple[str, str]] = []
        self._active_href: str | None = None
        self._active_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._active_href = href
            self._active_text = []

    def handle_data(self, data: str) -> None:
        if self._active_href:
            self._active_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._active_href:
            self.anchors.append((self._active_href, " ".join(self._active_text)))
            self._active_href = None
            self._active_text = []


def normalize_article_url(href: str) -> str:
    href = html.unescape(href.strip())
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return urllib.parse.urljoin(ROCKSTAR_ORIGIN, href)


def _visible_text(fragment: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _candidate_score(url: str, context: str) -> int:
    lowered = f"{url} {context}".lower()
    if "gta online" not in lowered and "gta-online" not in lowered:
        return -100

    score = 10
    for keyword in ("bonus", "bonuses", "rewards", "weekly", "event", "discount", "income"):
        if keyword in lowered:
            score += 2
    if "gta+" in lowered or "gta plus" in lowered:
        score -= 20
    if "red dead" in lowered or "grand theft auto vi" in lowered:
        score -= 20
    return score


def discover_latest_gta_online_article(html_text: str) -> str:
    """Return the best GTA Online Newswire article URL found in HTML markup."""
    candidates: list[tuple[int, int, str]] = []
    parser = NewswireAnchorParser()
    parser.feed(html_text)

    for index, (href, anchor_text) in enumerate(parser.anchors):
        url = normalize_article_url(href)
        parsed_path = urllib.parse.urlparse(url).path
        if "/newswire/article/" not in parsed_path:
            continue
        context = _visible_text(anchor_text)
        score = _candidate_score(url, context)
        if score >= 0:
            candidates.append((score, -index, url))

    if not candidates:
        raise ValueError("No GTA Online Newswire article links found")

    candidates.sort(reverse=True)
    return candidates[0][2]


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def resolve_weekly_update_url(
    direct_url: str | None = None,
    env_var: str = DEFAULT_ENV_VAR,
    newswire_url: str = DEFAULT_NEWSWIRE_URL,
    html_file: Path | None = None,
) -> str:
    if direct_url:
        return direct_url

    env_url = os.environ.get(env_var, "").strip()
    if env_url:
        return env_url

    html_text = html_file.read_text(encoding="utf-8") if html_file else fetch_text(newswire_url)
    return discover_latest_gta_online_article(html_text)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve the weekly GTA Online Newswire URL.")
    parser.add_argument("--url", help="Explicit Newswire article URL.")
    parser.add_argument("--env-var", default=DEFAULT_ENV_VAR, help="Environment variable fallback name.")
    parser.add_argument("--newswire-url", default=DEFAULT_NEWSWIRE_URL, help="Newswire listing URL for discovery.")
    parser.add_argument("--html-file", type=Path, help="Read Newswire markup from a local file for testing.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        print(
            resolve_weekly_update_url(
                direct_url=args.url,
                env_var=args.env_var,
                newswire_url=args.newswire_url,
                html_file=args.html_file,
            )
        )
    except (OSError, urllib.error.URLError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
