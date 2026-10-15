import copy
import datetime as dt
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from scripts import content_safety as safety
from scripts import resolve_weekly_update_source as resolver
from scripts import fetch_gtacar_prices as prices
from scripts import generate_dashboard as classic
from scripts import generate_pixel_dashboard as pixel
from scripts.scrape_weekly_update import WeeklyScraper
from scripts.review_weekly_candidate import approve
from scripts.gta_plus_intake import (monthly_issues, select_monthly, combine_weekly_bonuses, claim_before_expiry)
from scripts.player_profile_state import normalize_profile, character_view, cosmetic_available, validate_profile
from scripts.automation_health import weekly_health, reconcile_issue
from tests.safety_fixtures import TODAY, URL, weekly_payload, approved_workspace, monthly_payload

FIXTURES = Path(__file__).parent / 'fixtures'


class SourceIntakeTests(unittest.TestCase):
    def test_normalizes_both_article_layouts_and_excludes_navigation(self):
        for name in ('newswire_article.html', 'newswire_jsonld.html'):
            raw = (FIXTURES / name).read_text(encoding='utf-8')
            record = safety.normalize_article(raw, URL, TODAY)
            self.assertNotIn('Wrong Navigation', record['text'])
            self.assertEqual(record['week_id'], '2026-W41')
            self.assertEqual(len(record['article_sha256']), 64)
            scraper = WeeklyScraper()
            scraper.parse_content(record['text'])
            self.assertFalse(safety.coverage_issues(scraper.data))
            self.assertEqual(scraper.data['weekly_content']['bonuses'][0]['name'], 'Nightclub Sell Missions')

    def test_js_shell_missing_date_and_monthly_article_fail_closed(self):
        raw = (FIXTURES / 'newswire_jsonld.html').read_text(encoding='utf-8')
        for invalid in ('<div id="root"></div><script>loadArticle()</script>',
                        raw.replace('2026-10-08T10:00:00Z', 'unknown'),
                        raw.replace('GTA Online Weekly Bonuses', 'GTA Online GTA+ Monthly Benefits'),
                        raw.replace('2026-10-08', '2026-10-01')):
            with self.assertRaises(ValueError):
                safety.normalize_article(invalid, URL, TODAY)

    def test_invalid_manual_url_rejected_without_network(self):
        for url in ('https://example.test/newswire/article/a/b', URL.replace('https:', 'http:'),
                    'https://www.rockstargames.com/newswire', 'https://www.rockstargames.com.evil.test/newswire/article/a/b'):
            with self.assertRaises(ValueError):
                resolver.resolve_weekly_update_url(direct_url=url)

    def test_online_category_accepts_general_headline_and_monthly_title_still_rejected(self):
        raw = (FIXTURES / 'newswire_jsonld.html').read_text(encoding='utf-8')
        raw = raw.replace('"headline":"GTA Online Weekly Bonuses"', '"articleSection":"GTA Online","headline":"Boost Your Weekly Business Income"')
        result = safety.normalize_article(raw, URL, TODAY)
        self.assertEqual(result['category'], 'GTA Online')
        with self.assertRaises(ValueError):
            safety.normalize_article(raw.replace('Boost Your Weekly Business Income', 'Claim a Free Car with GTA+'), URL, TODAY)

    def test_scheduled_registry_date_matching_and_missing_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict('os.environ', {}, clear=True):
            path = Path(tmp) / 'sources.json'
            record = {'week_id': '2026-W41', 'published_date': '2026-10-08', 'state': 'confirmed',
                      'kind': 'weekly', 'reviewer': 'fixture', 'url': URL}
            path.write_text(json.dumps({'articles': [record]}), encoding='utf-8')
            self.assertEqual(resolver.resolve_weekly_update_url(source_index=path, today=TODAY), URL)
            with self.assertRaisesRegex(ValueError, 'needs_review'):
                resolver.resolve_weekly_update_url(source_index=path, today=dt.date(2026, 10, 15))

    def test_manual_override_wins_over_registry_but_still_requires_article_validation(self):
        with mock.patch.dict('os.environ', {'WEEKLY_UPDATE_URL': URL}):
            self.assertEqual(resolver.resolve_weekly_update_url(), URL)


class PublicationTests(unittest.TestCase):
    def test_current_approved_report_set_matches_and_changed_payload_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = approved_workspace(root)
            self.assertEqual(safety.publication_issues(payload, root, TODAY), [])
            payload['weekly_content']['bonuses'][0]['multiplier'] = '99x'
            self.assertTrue(safety.publication_issues(payload, root, TODAY))

    def test_partial_and_stale_candidate_never_overwrites_confirmed_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved_workspace(root)
            target = root / 'data/weekly_planning_2026_w41.json'
            before = target.read_bytes()
            candidate = root / 'data/candidates/weekly_planning_2026_w41.json'
            payload = weekly_payload()
            payload['weekly_content']['discounts'] = []
            candidate.write_text(json.dumps(payload), encoding='utf-8')
            with self.assertRaises(ValueError):
                approve(candidate, root, 'test', TODAY)
            self.assertEqual(target.read_bytes(), before)
            candidate.write_text(json.dumps(weekly_payload()), encoding='utf-8')
            with self.assertRaises(ValueError):
                approve(candidate, root, 'test', dt.date(2026, 10, 15))
            self.assertEqual(target.read_bytes(), before)

    def test_generators_reject_new_header_with_missing_review_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved_workspace(root)
            path = root / 'data/weekly_planning_2026_w41.json'
            payload = json.loads(path.read_text())
            payload.pop('review')
            path.write_text(json.dumps(payload), encoding='utf-8')
            for generator, constant, template in ((classic, 'DEFAULT_DASHBOARD', 'dashboard.html'),
                                                   (pixel, 'DEFAULT_PIXEL_DASHBOARD', 'pixel-dashboard.html')):
                output = root / template
                old = Path(template).read_text(encoding='utf-8')
                output.write_text(old, encoding='utf-8')
                with mock.patch.object(generator, constant, output), mock.patch.object(generator, 'ROOT', root):
                    self.assertEqual(generator.main(['--weekly', str(path), '--output', str(output)]), 1)
                self.assertEqual(output.read_text(encoding='utf-8'), old)

    def test_both_real_generators_render_approved_current_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved_workspace(root)
            path = root / 'data/weekly_planning_2026_w41.json'
            window = (dt.date(2026, 10, 8), dt.date(2026, 10, 15))
            for generator, constant, template in ((classic, 'DEFAULT_DASHBOARD', 'dashboard.html'),
                                                   (pixel, 'DEFAULT_PIXEL_DASHBOARD', 'pixel-dashboard.html')):
                output = root / template
                output.write_text(Path(template).read_text(encoding='utf-8'), encoding='utf-8')
                with (mock.patch.object(generator, constant, output), mock.patch.object(generator, 'ROOT', root),
                      mock.patch.object(classic, 'ROOT', root), mock.patch.object(safety, 'reset_window', return_value=window)):
                    self.assertEqual(generator.main(['--weekly', str(path), '--output', str(output)]), 0)
                result = output.read_text(encoding='utf-8')
                self.assertIn('2026-W41', result)
                self.assertIn('freshness-banner', result)
                self.assertNotIn('Free claim at The Vinewood Car Club', result)

    def test_status_banner_is_idempotent_and_expires_at_runtime(self):
        payload = weekly_payload()
        result = safety.insert_freshness('<body>old plan</body>', payload, 'pending')
        result = safety.insert_freshness(result, payload, 'pending')
        self.assertEqual(result.count('id="freshness-banner"'), 1)
        self.assertIn('Date.now()', result)
        self.assertIn('old plan', result)
        self.assertIn('age ', result)

    def test_retained_status_describes_displayed_week_even_when_newer_payload_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved_workspace(root)
            old = weekly_payload()
            old['week'].update(id='2026-W40', start_date='2026-10-01', end_date='2026-10-08')
            (root / 'data/weekly_planning_2026_w40.json').write_text(json.dumps(old))
            text = '<!-- START: header_meta -->Week 2026-W40<!-- END: header_meta -->'
            displayed = safety.displayed_payload(root, text, 'header_meta')
            self.assertEqual(displayed['week']['id'], '2026-W40')
            self.assertIn('stale', safety.freshness_banner(displayed, today=TODAY))

    def test_future_and_invalid_schema_are_not_approvable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved_workspace(root)
            candidate = root / 'data/candidates/weekly_planning_2026_w41.json'
            payload = weekly_payload()
            payload['player_context'].pop('constraints')
            candidate.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                approve(candidate, root, 'fixture', TODAY)
            payload = weekly_payload()
            payload['provenance']['published_date'] = '2026-10-14'
            candidate.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                approve(candidate, root, 'fixture', dt.date(2026, 10, 9))


class PriceEnrichmentTests(unittest.TestCase):
    def test_real_markup_prices_and_non_purchasable_markup(self):
        self.assertEqual(prices.extract_prices_from_html((FIXTURES / 'gtacars_growler_price.html').read_text(),
                                                        'https://gtacars.net/gta5/growler'), (1627000, 1220250))
        with self.assertRaises(prices.NonPurchasableError):
            prices.extract_prices_from_html((FIXTURES / 'gtacars_non_purchasable.html').read_text(), 'https://gtacars.net/gta5/trailers')
        self.assertEqual(prices.classify_catalog_availability('<p>Price: $1</p><a>Can be acquired in Online</a>'), 'purchasable')
        self.assertEqual(prices.classify_catalog_availability('<p>Price: $1</p><p>Removed from websites</p>'), 'limited')
        self.assertEqual(prices.classify_catalog_availability('<p>Cannot be acquired</p>'), 'non_purchasable')

    def test_price_parser_ignores_script_handling_and_trade_only_prices(self):
        for raw in ('<script>Price: $999999</script><div>nMonetaryValue: 150000</div>', '<p>Trade price: $100</p>'):
            with self.assertRaises(ValueError):
                prices.extract_prices_from_html(raw, 'test')

    def test_weekly_scope_partial_failure_and_invalid_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / 'prices.yaml'
            weekly = root / 'weekly.json'
            summary = root / 'summary.json'
            names = ['Pfister Growler', 'Wonderama Arcade', 'Transient Car', 'Historical Trailer']
            catalog.write_text('vehicles:\n' + ''.join(
                f'  - vehicle_name: "{name}"\n    base_price: null\n    trade_price: null\n    source_url: "https://gtacars.net/gta5/{slug}"\n'
                for name, slug in zip(names, ('growler', 'arcade', 'transient', 'trailers'))), encoding='utf-8')
            weekly.write_text(json.dumps({'weekly_content': {'vehicle_opportunities': [{'vehicle_name': n} for n in names[:3]]}}), encoding='utf-8')
            def fetch(slug, user_agent):
                if slug == 'growler':
                    return (1627000, 1220250)
                raise urllib.error.HTTPError('test', 503, 'temporary', {}, None)
            with mock.patch.object(prices, 'fetch_prices', side_effect=fetch) as fetch_mock:
                result = prices.main(['--prices', str(catalog), '--weekly', str(weekly), '--slug-map', str(root / 'slugs.json'),
                                      '--summary', str(summary), '--sleep', '0'])
            self.assertEqual(result, 0)
            self.assertEqual(fetch_mock.call_count, 2)
            status = json.loads(summary.read_text())
            self.assertEqual((status['attempted'], status['succeeded'], status['failed']), (2, 1, 1))
            text = catalog.read_text()
            self.assertIn('base_price: 1627000', text)
            self.assertEqual(text.count('base_price: null'), 3)
            self.assertTrue(any('HTTP 503' in row.get('reason', '') for row in status['results']))


class MonthlyLifecycleTests(unittest.TestCase):
    def test_expired_unknown_and_conflicting_periods_supply_no_current_claims(self):
        payload = monthly_payload()
        self.assertTrue(monthly_issues(payload, TODAY))
        self.assertEqual(claim_before_expiry(payload, TODAY), [])
        self.assertNotIn('Ocelot Stromberg', classic.render_gta_plus_benefits(payload, {}, TODAY))
        self.assertNotIn('Ocelot Stromberg', pixel.render_pixel_gta_plus(payload, TODAY))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for month in ('06', '07'):
                (root / f'gta_plus_monthly_2026_{month}.json').write_text(json.dumps(payload))
            selected, state = select_monthly(root, dt.date(2026, 6, 12))
            self.assertEqual(selected, {})
            self.assertIn('overlapping', state)

    def test_no_unrelated_or_undocumented_multiplier_product(self):
        payload = monthly_payload()
        weekly = weekly_payload()
        weekly['week'].update(id='2026-W24', start_date='2026-06-11', end_date='2026-06-18')
        weekly['weekly_content']['bonuses'][0]['name'] = "G's Caches"
        day = dt.date(2026, 6, 12)
        row = combine_weekly_bonuses(weekly, payload, day)[0]
        self.assertEqual(row['member'], '5x')
        self.assertNotEqual(row['member'], '10x')
        bonus = payload['monthly_benefits']['member_bonuses'][0]
        bonus['weekly_overlay'] = {'review_state': 'confirmed', 'source_urls': [URL], 'week_id': '2026-W24',
                                  'weekly_multiplier': '2x', 'member_multiplier': '5x', 'reward_type': 'GTA$ & RP', 'effective_multiplier': 10}
        payload['review']['payload_sha256'] = safety.payload_digest(payload)
        self.assertEqual(combine_weekly_bonuses(weekly, payload, day)[0]['member'], '10x')
        bonus['weekly_overlay']['week_id'] = '2026-W40'
        payload['review']['payload_sha256'] = safety.payload_digest(payload)
        self.assertEqual(combine_weekly_bonuses(weekly, payload, day)[0]['member'], '5x')

    def test_key_benefit_source_and_claim_method_validation(self):
        payload = monthly_payload()
        self.assertFalse(monthly_issues(payload, dt.date(2026, 6, 12)))
        claims = claim_before_expiry(payload, dt.date(2026, 6, 12))
        self.assertEqual(claims[0]['claim_method'], 'vinewood_car_club')
        payload['monthly_benefits']['claimable_vehicles'][0]['source_urls'] = []
        self.assertTrue(monthly_issues(payload, dt.date(2026, 6, 12)))

    def test_edited_monthly_perk_cannot_keep_confirmed_review(self):
        payload = monthly_payload()
        payload['monthly_benefits']['member_bonuses'][0]['multiplier'] = '100x'
        self.assertTrue(monthly_issues(payload, dt.date(2026, 6, 12)))
        self.assertEqual(claim_before_expiry(payload, dt.date(2026, 6, 12)), [])

    def test_period_rollover_and_filename_order_do_not_select_future_perks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = monthly_payload()
            new = monthly_payload()
            new['membership_period'].update(start_date='2026-07-14', end_date='2026-08-10')
            new['review']['payload_sha256'] = safety.payload_digest(new)
            (root / 'gta_plus_monthly_2026_06.json').write_text(json.dumps(old), encoding='utf-8')
            (root / 'gta_plus_monthly_2026_07.json').write_text(json.dumps(new), encoding='utf-8')
            selected, _ = select_monthly(root, dt.date(2026, 7, 13))
            self.assertEqual(selected['membership_period']['start_date'], '2026-06-11')
            selected, _ = select_monthly(root, dt.date(2026, 7, 14))
            self.assertEqual(selected['membership_period']['start_date'], '2026-07-14')

    def test_period_covering_only_part_of_week_has_no_blanket_member_multiplier(self):
        payload = monthly_payload()
        weekly = weekly_payload()
        weekly['week'].update(start_date='2026-07-09', end_date='2026-07-16')
        weekly['weekly_content']['bonuses'][0]['name'] = "G's Caches"
        row = combine_weekly_bonuses(weekly, payload, dt.date(2026, 7, 12))[0]
        self.assertEqual(row['member'], 'unknown')


class PlayerProfileTests(unittest.TestCase):
    def test_legacy_profile_and_character_garages_do_not_merge(self):
        legacy = {'owned_assets': {'vehicles': ['Main Car']}, 'bankroll': {'cash_on_hand': 1}}
        self.assertEqual(character_view(legacy)['owned_assets']['vehicles'], ['Main Car'])
        profile = normalize_profile(legacy)
        profile['characters']['secondary'] = {'owned_assets': {'vehicles': ['Secondary Car']}}
        self.assertEqual(character_view(profile, 'secondary')['owned_assets']['vehicles'], ['Secondary Car'])
        with self.assertRaises(ValueError):
            character_view(profile, 'wrong')

    def test_repository_observation_is_specific_not_general_unlock_rule(self):
        profile = json.loads(Path('data/player_profile.json').read_text(encoding='utf-8'))
        self.assertFalse(validate_profile(profile))
        record = cosmetic_available(profile, 'Orange Shade Camo', 'secondary')
        self.assertEqual(record['state'], 'observed_available')
        self.assertFalse(record['buy_duplicate_for_unlock'])
        self.assertEqual(record['unlock_method'], 'unknown')
        self.assertEqual(cosmetic_available(profile, 'Other GTA+ livery', 'secondary')['state'], 'unknown')
        self.assertNotIn('Galaxy Super Yacht', character_view(profile, 'secondary')['owned_assets']['properties'])
        profile['active_character'] = 'secondary'
        self.assertFalse(validate_profile(profile))

    def test_contradictory_notes_and_aliases_caught(self):
        profile = {'owned_assets': {'properties': ['Galaxy Super Yacht'], 'notes': 'Missing only Yacht.'}}
        self.assertTrue(validate_profile(profile))
        current = json.loads(Path('data/player_profile.json').read_text(encoding='utf-8'))
        current['owned_assets']['vehicles'].append('Wrong alias car')
        self.assertTrue(validate_profile(current))


class HealthMonitoringTests(unittest.TestCase):
    def test_intentionally_manual_weekly_intake_does_not_alert(self):
        self.assertFalse(weekly_health(
            {'state': 'failed', 'issues': ['Missing reviewed source']}, [],
            workflow_state='disabled_manually', schedule_enabled=False))

    def test_missing_schedule_disabled_failure_and_recovery(self):
        now = dt.datetime(2026, 10, 15, 17, tzinfo=dt.timezone.utc)
        self.assertTrue(weekly_health({}, [], now, 'disabled_inactivity'))
        run = {'event': 'schedule', 'created_at': '2026-10-15T03:00:00Z', 'conclusion': 'failure', 'html_url': 'test'}
        self.assertTrue(weekly_health({}, [run], now))
        run['conclusion'] = 'success'
        status = {'week_id': '2026-W42', 'state': 'published'}
        self.assertFalse(weekly_health(status, [run], now))
        self.assertTrue(weekly_health({**status, 'state': 'needs_review'}, [run], now))
        self.assertFalse(weekly_health(status, [run], now.replace(hour=13)))
        previous_status = {'week_id': '2026-W41', 'state': 'published'}
        previous_run = {'event': 'schedule', 'created_at': '2026-10-08T03:00:00Z', 'conclusion': 'success'}
        self.assertFalse(weekly_health(previous_status, [previous_run], now.replace(hour=5)))
        self.assertTrue(weekly_health(previous_status, [previous_run], now.replace(hour=6)))

    def test_alert_reopens_deduplicated_issue_and_closes_only_on_recovery(self):
        with mock.patch('scripts.automation_health.github_request') as request:
            request.return_value = [{'number': 30, 'title': 'health', 'state': 'closed'}]
            reconcile_issue('owner/repo', 'health', ['missing run'])
            self.assertEqual(request.call_args.args[3]['state'], 'open')
            request.return_value = [{'number': 30, 'title': 'health', 'state': 'open'}]
            reconcile_issue('owner/repo', 'health', [])
            self.assertEqual(request.call_args.args[3]['state'], 'closed')

    def test_unchanged_health_issue_stays_quiet(self):
        body = 'Automated health check. Recovery: `docs/automation-recovery.md`.\n\n- missing run'
        with mock.patch('scripts.automation_health.github_request') as request:
            request.return_value = [{'number': 30, 'title': 'health', 'state': 'open', 'body': body}]
            reconcile_issue('owner/repo', 'health', ['missing run'])
            self.assertEqual(request.call_count, 1)


if __name__ == '__main__':
    unittest.main()
