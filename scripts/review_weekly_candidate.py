#!/usr/bin/env python3
"""Explicit human/assistant handoff after canonical planning and completeness QA."""
import argparse
import hashlib
import json
from pathlib import Path

try:
    from scripts.content_safety import source_issues, report_paths, payload_digest, publication_issues, utc_now, write_json
except ModuleNotFoundError:
    from content_safety import source_issues, report_paths, payload_digest, publication_issues, utc_now, write_json

ROOT = Path(__file__).resolve().parents[1]


def approve(candidate, root, reviewer, today=None):
    payload = json.loads(candidate.read_text(encoding="utf-8"))
    payload["content_quality"] = "confirmed"
    issues = source_issues(payload, today)
    if not reviewer.strip():
        issues.append("Reviewer is required")
    if issues:
        raise ValueError("; ".join(issues))
    identifier = payload["week"]["id"]
    hashes = {}
    for path in report_paths(root, identifier):
        if not path.exists():
            raise ValueError(f"Missing canonical report: {path.name}")
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    master = report_paths(root, identifier)[0].read_text(encoding="utf-8")
    for heading in ("## What to Play", "## What to Buy", "## What to Ignore", "## Action Queue"):
        if heading not in master:
            raise ValueError(f"Missing master plan section: {heading}")
    payload["review"] = {"state": "approved", "reviewer": reviewer, "reviewed_at": utc_now().isoformat(),
                         "payload_sha256": payload_digest(payload), "report_sha256": hashes}
    issues = publication_issues(payload, root, today)
    if issues:
        raise ValueError("; ".join(issues))
    target = root / "data" / f"weekly_planning_{identifier.replace('-', '_').lower()}.json"
    write_json(target, payload)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--reviewer", required=True)
    args = parser.parse_args()
    try:
        print(approve(args.candidate, ROOT, args.reviewer))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Review rejected: {exc}\n")


if __name__ == "__main__":
    main()
