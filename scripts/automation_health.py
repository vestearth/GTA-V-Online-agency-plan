"""Watch missing/failed runs and monthly rollover; maintain deduplicated health Issues."""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

try:
    from scripts.content_safety import utc_now, reset_window, week_id
    from scripts.gta_plus_intake import select_monthly
except ModuleNotFoundError:
    from content_safety import utc_now, reset_window, week_id
    from gta_plus_intake import select_monthly


def weekly_health(status, runs, now=None, workflow_state="active"):
    now = now or utc_now()
    start, _ = reset_window((now + dt.timedelta(hours=7)).date())
    # 13:00 UTC collection + three-hour allowance for scheduling/execution delay.
    due = dt.datetime.combine(start, dt.time(16), dt.timezone.utc)
    allowed_week_ids = {week_id(start)}
    problems = []
    if workflow_state != "active":
        problems.append(f"Workflow state: {workflow_state}; enable it in Actions")
    if status.get("state") == "failed":
        problems.append("Latest refresh failed: " + "; ".join(status.get("issues", [])))
    if status.get("state") == "needs_review":
        problems.append("Candidate needs curator review")
    if now < due:
        # Don't auto-close an unresolved alert just because a new Thursday began.
        start -= dt.timedelta(days=7)
        due -= dt.timedelta(days=7)
        allowed_week_ids.add(week_id(start))
    if now >= due:
        relevant = [r for r in runs if r.get("event") == "schedule"
                    and r.get("created_at", "") >= start.isoformat()]
        if not relevant:
            problems.append("No scheduled Weekly Content Refresh run after expected Thursday cadence")
        elif relevant[0].get("conclusion") not in ("success", None):
            problems.append("Scheduled run failed: " + str(relevant[0].get("html_url", "")))
        if status.get("week_id") not in allowed_week_ids or status.get("state") != "published":
            problems.append("Current week not published/reviewed: " + str(status.get("state", "missing status")))
    return problems


def github_request(repo, path, method="GET", body=None):
    token = os.environ["GH_TOKEN"]
    request = urllib.request.Request("https://api.github.com/repos/" + repo + path,
        data=json.dumps(body).encode() if body is not None else None, method=method,
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "GTA-planning-health-monitor"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def reconcile_issue(repo, title, problems):
    # Include closed issues so recurring failures reopen the same tracking issue.
    issues = []
    page = 1
    while True:
        batch = github_request(repo, f"/issues?state=all&per_page=100&page={page}")
        issues.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    matches = [i for i in issues if i.get("title") == title and "pull_request" not in i]
    body = ("Automated health check. Recovery: `docs/automation-recovery.md`.\n\n"
            + "\n".join("- " + p for p in problems))
    if problems:
        if matches:
            if matches[0].get("state") != "open" or matches[0].get("body") != body:
                github_request(repo, f'/issues/{matches[0]["number"]}', "PATCH", {"state": "open", "body": body})
        else:
            github_request(repo, "/issues", "POST", {"title": title, "body": body})
    elif matches and matches[0]["state"] == "open":
        github_request(repo, f'/issues/{matches[0]["number"]}', "PATCH",
                       {"state": "closed", "state_reason": "completed"})


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    root = Path(__file__).resolve().parents[1]
    path = root / "data/refresh_status.json"
    status = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    workflow = github_request(repo, "/actions/workflows/weekly-content-refresh.yml")
    runs = github_request(repo, "/actions/workflows/weekly-content-refresh.yml/runs?per_page=20")["workflow_runs"]
    problems = weekly_health(status, runs, workflow_state=workflow.get("state", "unknown"))
    reconcile_issue(repo, "[automation] Weekly refresh needs attention", problems)
    monthly, state = select_monthly(root / "data")
    reconcile_issue(repo, "[automation] GTA+ monthly intake needs review", [] if monthly else [state])
    print(json.dumps({"weekly": problems, "monthly": state}))


if __name__ == "__main__":
    main()
