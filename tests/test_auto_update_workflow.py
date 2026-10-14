import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from scripts import run_weekly_content_refresh as refresh
from scripts import content_safety
from tests.safety_fixtures import approved_workspace, weekly_payload, URL


class AutoUpdateWorkflowScheduleTests(unittest.TestCase):
    def test_price_workflow_is_manual_and_uses_shared_writer_queue(self):
        workflow = Path('.github/workflows/auto-update-vehicle-prices.yml').read_text(encoding='utf-8')
        self.assertNotIn('schedule:', workflow)
        self.assertNotIn('  push:', workflow)
        self.assertIn('gta-data-producer-${{ github.ref }}', workflow)
        self.assertNotIn('--fail-on-skipped', workflow)

    def test_readme_documents_matching_automation_time(self):
        readme = Path('README.md').read_text(encoding='utf-8')
        self.assertIn('03:00 UTC / 10:00 Bangkok', readme)

    def test_commit_does_not_replay_stale_results_on_newer_remote(self):
        for filename in ('weekly-content-refresh.yml', 'auto-update-vehicle-prices.yml'):
            text = (Path('.github/workflows') / filename).read_text(encoding='utf-8')
            self.assertNotIn('git pull --rebase', text)
            self.assertIn('cancel-in-progress: false', text)


class WeeklyContentRefreshDashboardTests(unittest.TestCase):
    def run_refresh(self, root, approved=False, changed=False, publish=False, fail_price=False, fail_pixel=False):
        if approved:
            approved_workspace(root)
        (root / 'data/candidates').mkdir(parents=True, exist_ok=True)
        (root / 'reports').mkdir(exist_ok=True)
        commands = []
        candidate = root / 'data/candidates/weekly_planning_2026_w41.json'

        def run(command, *, allow_failure=False):
            commands.append(command)
            script = command[1]
            if script.endswith('scrape_weekly_update.py'):
                payload = weekly_payload()
                if changed:
                    payload['provenance']['article_sha256'] = 'b' * 64
                candidate.write_text(json.dumps(payload), encoding='utf-8')
            if script.endswith('fetch_gtacar_prices.py') and fail_price:
                return 1
            if '--output' in command:
                if fail_pixel and script.endswith('generate_pixel_dashboard.py'):
                    import subprocess
                    raise subprocess.CalledProcessError(1, command)
                Path(command[command.index('--output') + 1]).write_text('generated current dashboard', encoding='utf-8')
            return 0

        window = (__import__('datetime').date(2026, 10, 8), __import__('datetime').date(2026, 10, 15))
        with (mock.patch.object(refresh, 'ROOT', root),
              mock.patch.object(refresh, 'current_week_id', return_value='2026-W41'),
              mock.patch.object(content_safety, 'reset_window', return_value=window),
              mock.patch.object(refresh, 'resolve_weekly_update_url', return_value=URL),
              mock.patch.object(refresh, 'run_step', side_effect=run)):
            result = refresh.main(['--publish-reviewed'] if publish else [])
        return result, commands, json.loads((root / 'data/refresh_status.json').read_text())

    def test_missing_master_plan_saves_candidate_and_explicit_review_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, commands, status = self.run_refresh(Path(tmp))
            self.assertEqual(result, 0)
            self.assertEqual(status['state'], 'needs_review')
            self.assertFalse(status['published'])
            self.assertFalse(any('generate_dashboard.py' in c[1] for c in commands))
            self.assertTrue((Path(tmp) / status['candidate']).exists())
            self.assertFalse(list((Path(tmp) / 'reports').glob('*.md')))

    def test_approved_same_week_generates_both_dashboards_and_safe_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result, commands, status = self.run_refresh(root, approved=True)
            self.assertEqual(result, 0)
            self.assertEqual(status['state'], 'published')
            self.assertEqual(len([c for c in commands if '--output' in c]), 2)
            self.assertTrue((root / 'pixel-dashboard.html').exists())
            result, _, status = self.run_refresh(root)
            self.assertEqual(status['state'], 'published')

    def test_source_change_withholds_publication_and_preserves_approved_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved_workspace(root)
            canonical = root / 'data/weekly_planning_2026_w41.json'
            before = canonical.read_bytes()
            _, _, status = self.run_refresh(root, changed=True)
            self.assertEqual(status['state'], 'needs_review')
            self.assertEqual(before, canonical.read_bytes())

    def test_price_source_failure_does_not_block_valid_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, _, status = self.run_refresh(Path(tmp), approved=True, fail_price=True)
            self.assertEqual(result, 0)
            self.assertTrue(status['published'])
            self.assertEqual(status['price_exit_code'], 1)

    def test_report_tampering_or_wrong_week_rejects_explicit_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved_workspace(root)
            report = root / 'reports/weekly_master_plan_2026_w41.md'
            report.write_text('# Wrong report - 2026-W40\n', encoding='utf-8')
            result, _, status = self.run_refresh(root, publish=True)
            self.assertEqual(result, 1)
            self.assertFalse(status['published'])

    def test_second_generator_failure_never_replaces_first_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved_workspace(root)
            for name in ('dashboard.html', 'pixel-dashboard.html'):
                (root / name).write_text('<body>old header and recommendations</body>', encoding='utf-8')
            result, _, status = self.run_refresh(root, fail_pixel=True)
            self.assertEqual(result, 1)
            self.assertIn('old header and recommendations', (root / 'dashboard.html').read_text(encoding='utf-8'))

    def test_workflow_commits_candidates_status_and_only_canonical_report_names(self):
        text = Path('.github/workflows/weekly-content-refresh.yml').read_text(encoding='utf-8')
        self.assertIn('git add -A data', text)
        self.assertIn('reports/weekly_master_plan_*.md', text)
        self.assertIn('reports/event_master_plan_*.md', text)
        self.assertNotIn('reports/weekly_report_', text)


if __name__ == '__main__':
    unittest.main()
