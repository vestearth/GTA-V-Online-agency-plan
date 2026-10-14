"""Shared intake and publication contracts. No network or assistant orchestration."""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def reset_window(today=None):
    today = today or (utc_now() + dt.timedelta(hours=7)).date()
    start = today - dt.timedelta(days=(today.weekday() - 3) % 7)
    return start, start + dt.timedelta(days=7)


def week_id(start):
    year, week, _ = start.isocalendar()
    return f"{year}-W{week:02d}"


def validate_newswire_url(url):
    if not isinstance(url, str):
        raise ValueError("Expected an HTTPS Rockstar Newswire article URL string")
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.hostname != "www.rockstargames.com"
            or parsed.username or parsed.password or parsed.port
            or not re.fullmatch(r"/newswire/article/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/?", parsed.path)):
        raise ValueError("Expected an HTTPS Rockstar Newswire article URL")
    return url


class ArticleParser(HTMLParser):
    """Read visible article blocks, publication metadata and JSON-LD Article bodies."""
    blocks = {"p", "li", "h1", "h2", "h3", "h4", "div", "br", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.article_parts = []
        self.in_article = 0
        self.skip = 0
        self.json_script = False
        self.script_parts = []
        self.records = []
        self.meta = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.meta[attrs.get("property", attrs.get("name", ""))] = attrs.get("content", "")
        if tag in {"script", "style", "nav", "header", "footer"}:
            self.skip += 1
        if tag == "script":
            self.json_script = attrs.get("type") == "application/ld+json"
            self.script_parts = []
        if tag == "article":
            self.in_article += 1
        if tag in self.blocks and not self.skip:
            self.parts.append("\n")
            if self.in_article:
                self.article_parts.append("\n")

    def handle_data(self, data):
        if self.json_script:
            self.script_parts.append(data)
        elif not self.skip:
            self.parts.append(data)
            if self.in_article:
                self.article_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.json_script:
            try:
                self.records.append(json.loads("".join(self.script_parts)))
            except ValueError:
                pass
            self.json_script = False
        if tag in {"script", "style", "nav", "header", "footer"}:
            self.skip = max(0, self.skip - 1)
        if tag in self.blocks and not self.skip:
            self.parts.append("\n")
            if self.in_article:
                self.article_parts.append("\n")
        if tag == "article":
            self.in_article = max(0, self.in_article - 1)


def _articles(value):
    if isinstance(value, list):
        for item in value:
            yield from _articles(item)
    elif isinstance(value, dict):
        kind = value.get("@type", [])
        kind = [kind] if isinstance(kind, str) else kind
        if any(k in {"Article", "NewsArticle", "BlogPosting"} for k in kind):
            yield value
        yield from _articles(value.get("@graph", []))


def normalize_article(raw, url, today=None):
    validate_newswire_url(url)
    parser = ArticleParser()
    parser.feed(raw)
    records = list(_articles(parser.records))
    # Multiple article objects are ambiguous; don't guess the right one.
    if len(records) > 1:
        raise ValueError("Multiple article records; needs_review")
    record = records[0] if records else {}
    title = record.get("headline") or parser.meta.get("og:title", "")
    category = record.get("articleSection") or parser.meta.get("article:section", "")
    published = record.get("datePublished") or parser.meta.get("article:published_time", "")
    try:
        published_date = dt.date.fromisoformat(str(published)[:10])
    except ValueError as exc:
        raise ValueError("Missing publication date; needs_review (possibly JS-only page)") from exc
    lowered = title.casefold()
    categories = category if isinstance(category, list) else [category]
    is_online = "gta online" in lowered or any(str(c).casefold() in {"gta online", "grand theft auto online"} for c in categories)
    if (not is_online or any(k in lowered for k in ("gta+", "gta plus", "red dead"))):
        raise ValueError("Source is not a general GTA Online weekly article")
    start, end = reset_window(today)
    if not start <= published_date < end:
        raise ValueError(f"Stale/incorrect-week source: {published_date}; expected {start}..{end}")
    if published_date > (today or (utc_now() + dt.timedelta(hours=7)).date()):
        raise ValueError("Future/pre-live source cannot be treated as current confirmed content")
    body = record.get("articleBody")
    if body:
        body_parser = ArticleParser()
        body_parser.feed(str(body))
        parts = body_parser.parts
    else:
        parts = parser.article_parts
    text = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in "".join(parts).splitlines())
    text = re.sub(r"\n+", "\n", text).strip()
    if len(text) < 100:
        raise ValueError("Missing article body; needs_review (possibly JS-only page)")
    return {"url": url, "title": title, "category": category, "published_date": published_date.isoformat(),
            "fetched_at": utc_now().isoformat(), "article_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "text": text, "week_id": week_id(start)}


def coverage_issues(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("weekly_content"), dict):
        return ["Invalid weekly payload/content object"]
    content = payload.get("weekly_content", {})
    issues = []
    for group in ("bonuses", "discounts", "vehicle_opportunities"):
        if not isinstance(content.get(group), list) or not content[group]:
            issues.append(f"Missing critical coverage: {group}")
    return issues


def schema_issues(payload):
    """Deterministic subset of validate_weekly_schema_lightweight's canonical contract."""
    if not isinstance(payload, dict):
        return ["Invalid payload object"]
    issues = []
    for key, value in (("schema_version", "2.0"), ("schema_mode", "weekly_planning")):
        if payload.get(key) != value:
            issues.append(f"Invalid {key}; expected {value}")
    for path in ("week.id", "week.label", "week.start_date", "week.end_date",
                 "player_context.owned_assets.properties", "player_context.constraints.hours_available",
                 "weekly_content.discounts"):
        current = payload
        for key in path.split("."):
            current = current.get(key) if isinstance(current, dict) else None
        if current is None:
            issues.append(f"Missing critical schema path: {path}")
    content = payload.get("weekly_content", {})
    if isinstance(content, dict):
        if not isinstance(content.get("events", content.get("featured_activities")), list):
            issues.append("Missing events/featured_activities list")
        for tier in content.get("discounts", []) if isinstance(content.get("discounts"), list) else []:
            if (not isinstance(tier, dict) or type(tier.get("tier_percent")) is not int
                    or not 0 <= tier["tier_percent"] <= 100 or not isinstance(tier.get("items"), list)
                    or not tier["items"] or not all(isinstance(x, str) and x.strip() for x in tier["items"])):
                issues.append("Invalid discount tier/items")
    return issues


def payload_digest(payload):
    content = {k: v for k, v in payload.items() if k != "review"}
    return hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def report_paths(root, identifier):
    suffix = identifier.replace("-", "_").lower()
    return [root / "reports" / name for name in (
        f"weekly_master_plan_{suffix}.md", f"weekly_master_plan_{suffix}_income_scenarios.md",
        f"event_master_plan_{suffix}.md")]


def source_issues(payload, today=None):
    issues = schema_issues(payload) + coverage_issues(payload)
    if not isinstance(payload, dict):
        return issues
    start, end = reset_window(today)
    week = payload.get("week", {})
    if not isinstance(week, dict):
        return issues + ["Invalid week object"]
    if (week.get("id") != week_id(start) or week.get("start_date") != start.isoformat()
            or week.get("end_date") != end.isoformat()):
        issues.append("Week ID/date window does not match current reset")
    source = payload.get("provenance", {})
    if not isinstance(source, dict):
        return issues + ["Invalid provenance object"]
    try:
        validate_newswire_url(source.get("url", ""))
        published = dt.date.fromisoformat(source.get("published_date", ""))
        if not start <= published < end:
            issues.append("Source date is outside current reset window")
        if published > (today or (utc_now() + dt.timedelta(hours=7)).date()):
            issues.append("Future/pre-live source date")
    except ValueError:
        issues.append("Missing/invalid source provenance")
    if not re.fullmatch(r"[a-f0-9]{64}", str(source.get("article_sha256", ""))) or not source.get("title"):
        issues.append("Missing source title/article hash")
    title = str(source.get("title", "")).casefold()
    categories = source.get("category", [])
    categories = categories if isinstance(categories, list) else [categories]
    is_online = "gta online" in title or any(str(c).casefold() in {"gta online", "grand theft auto online"} for c in categories)
    if not is_online or "gta+" in title or "gta plus" in title:
        issues.append("Source is not a general weekly article")
    if payload.get("content_quality") != "confirmed":
        issues.append("Content is not confirmed")
    return issues


def publication_issues(payload, root, today=None):
    issues = source_issues(payload, today)
    if not isinstance(payload, dict):
        return issues
    review = payload.get("review", {})
    if not isinstance(review, dict):
        return issues + ["Invalid review object"]
    if (review.get("state") != "approved" or not review.get("reviewer")
            or review.get("payload_sha256") != payload_digest(payload)):
        issues.append("Missing approval or payload changed since review")
    identifier = payload.get("week", {}).get("id", "")
    if not isinstance(identifier, str) or not re.fullmatch(r"\d{4}-W\d{2}", identifier):
        return issues + ["Invalid week identifier"]
    for path in report_paths(root, identifier):
        if not path.exists():
            issues.append(f"Missing report: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        heading = text.splitlines()[0] if text.splitlines() else ""
        match = re.search(r"\b\d{4}-W\d{2}\b", heading)
        if not match or match.group() != identifier:
            issues.append(f"Report week mismatch: {path.name}")
        if review.get("report_sha256", {}).get(path.name) != hashlib.sha256(path.read_bytes()).hexdigest():
            issues.append(f"Report changed/unapproved: {path.name}")
    return issues


def displayed_payload(root, html_text, marker):
    """Status must describe the displayed header, not a newer unrendered payload."""
    block = re.search(r"<!-- START: " + re.escape(marker) + r" -->(.*?)<!-- END: " + re.escape(marker) + r" -->", html_text, re.S)
    identifier = re.search(r"\b\d{4}-W\d{2}\b", block[1]) if block else None
    if not identifier:
        return {}
    identifier = identifier.group()
    path = root / "data" / f"weekly_planning_{identifier.replace('-', '_').lower()}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    return {"week": {"id": identifier}, "content_quality": "needs_review"}


def freshness_banner(payload, reason="", today=None):
    start, end = reset_window(today)
    week = payload.get("week", {})
    stale = week.get("id") != week_id(start)
    state = "stale" if stale else payload.get("content_quality", "needs_review")
    reviewed = payload.get("review", {}).get("state") == "approved"
    source = payload.get("provenance", {})
    try:
        dated = dt.date.fromisoformat(source.get("published_date", week.get("start_date", "")))
        age = ((today or (utc_now() + dt.timedelta(hours=7)).date()) - dated).days
    except ValueError:
        age = "unknown"
    text = (f"{state} · {week.get('id', 'unknown')} · source {source.get('published_date', 'unknown')}"
            f" · age {age} days · ends {week.get('end_date', 'unknown')} · review {'approved' if reviewed else 'pending'}")
    if reason:
        text += f" · {reason}"
    try:
        source_url = validate_newswire_url(source.get("url"))
        link = f' · <a href="{html.escape(source_url, quote=True)}" style="color:#fff">Newswire source</a>'
    except ValueError:
        link = ""
    # Runtime expiry is necessary for static hosting when no scheduled run happens.
    return ('<!-- START: freshness_banner -->\n'
            f'<aside id="freshness-banner" role="status" data-expires="{html.escape(str(week.get("end_date", "")))}" '
            'style="padding:16px;background:#422;color:#fff;border:2px solid #f99;font-weight:bold">'
            f'{html.escape(text)} / โปรดตรวจสอบวันที่ข้อมูลและสถานะรีวิว{link}</aside>\n'
            '<script>(()=>{const update=()=>{const b=document.getElementById("freshness-banner");'
            'const end=Date.parse(b.dataset.expires+"T00:00:00+07:00");'
            'if((!Number.isFinite(end)||Date.now()>=end)&&!b.dataset.stale){b.prepend("STALE / ข้อมูลหมดอายุ · ");b.dataset.stale="true";}'
            'document.querySelectorAll("[data-gta-plus-until]").forEach(p=>{'
            'if(Date.now()>=Date.parse(p.dataset.gtaPlusUntil)){p.textContent="GTA+ STALE / สิทธิ์หมดอายุ โปรดรอข้อมูลรอบใหม่";}});};'
            'if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",update);}else{update();}'
            'setInterval(update,60000);})();</script>\n<!-- END: freshness_banner -->')


def insert_freshness(html_text, payload, reason=""):
    banner = freshness_banner(payload, reason)
    pattern = r"<!-- START: freshness_banner -->.*?<!-- END: freshness_banner -->"
    if re.search(pattern, html_text, re.S):
        return re.sub(pattern, lambda _: banner, html_text, flags=re.S)
    return re.sub(r"(<body\b[^>]*>)", lambda m: m[1] + "\n" + banner, html_text, count=1)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)
