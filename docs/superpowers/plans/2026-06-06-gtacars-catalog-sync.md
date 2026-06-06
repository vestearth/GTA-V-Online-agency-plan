# GTACars Catalog Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a sitemap-based GTACars catalog sync to keep vehicle slugs and prices complete.

**Architecture:** Create a standard-library script that reads GTACars `sitemap.xml`, filters public `/gta5/<slug>` vehicle pages, fetches them with a configurable delay, parses vehicle name and prices, and merges records into `vehicle_gtacars_slugs.json` plus `vehicle_prices.yaml`. The command supports `--dry-run` and `--limit` for safe review before writing.

**Tech Stack:** Python standard library, `unittest`, existing YAML-like text editing helpers.

---

### Task 1: Parser And Sitemap Helpers

**Files:**
- Create: `scripts/sync_gtacars_catalog.py`
- Modify: `tests/test_update_vehicle_prices.py`

- [ ] Add tests for sitemap URL filtering and page HTML parsing.
- [ ] Implement `extract_vehicle_urls_from_sitemap` and `extract_vehicle_record_from_html`.
- [ ] Run focused parser tests.

### Task 2: Reference Merge Helpers

**Files:**
- Modify: `scripts/sync_gtacars_catalog.py`
- Modify: `tests/test_update_vehicle_prices.py`

- [ ] Add tests for slug-map updates and price-reference merge behavior.
- [ ] Implement `build_slug_updates` and `apply_price_records`.
- [ ] Run focused merge tests.

### Task 3: CLI

**Files:**
- Modify: `scripts/sync_gtacars_catalog.py`

- [ ] Add CLI flags: `--dry-run`, `--limit`, `--sleep`, `--sitemap-url`, `--prices`, `--slug-map`.
- [ ] Ensure fetched URLs are public `/gta5/<slug>` pages only.
- [ ] Run live `--dry-run --limit 5`.
- [ ] Run `python -m unittest tests.test_update_vehicle_prices -v`.
