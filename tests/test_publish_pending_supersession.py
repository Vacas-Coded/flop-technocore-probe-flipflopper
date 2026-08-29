import importlib.util
import json
import pathlib
import tempfile
import unittest

MODULE_PATH = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/publish_update_bundle.py')
spec = importlib.util.spec_from_file_location('publish_update_bundle', MODULE_PATH)
assert spec is not None and spec.loader is not None
publish_update_bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish_update_bundle)


class PendingPublicationSupersessionTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmpdir.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir(parents=True, exist_ok=True)
        self.docs = self.repo / 'docs' / 'project-updates'
        self.docs.mkdir(parents=True, exist_ok=True)
        self.log_dir = self.root / 'logs'
        self.state_path = self.root / 'publish_state.json'

        setattr(publish_update_bundle, 'REPO', self.repo)
        setattr(publish_update_bundle, 'LOG_DIR', self.log_dir)
        setattr(publish_update_bundle, 'STATE_PATH', self.state_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_update(self, name: str, title: str, source_id: str, date_utc: str):
        path = self.docs / name
        path.write_text(
            '\n'.join([
                f'# {title}',
                '',
                f'- date_utc: {date_utc}',
                f'- source_id: {source_id}',
                '- source_url: https://example.com/source',
                '',
                '## Summary',
                'Example summary.',
                '',
                '## Why it matters',
                'Example why.',
                '',
                '## Verified',
                '- Verified once.',
                '',
                '## Still uncertain',
                '- One uncertainty.',
                '',
                '## Evidence',
                '- /tmp/evidence.txt',
                '',
            ])
        )
        return path

    def test_newer_pending_item_supersedes_older_item_for_same_source_and_event(self):
        state = publish_update_bundle.default_state()
        older = self._write_update(
            '20260829T221230Z_cooldown-aware-pending-publication-queue-added.md',
            'Cooldown-aware pending publication queue added',
            'watcher_publication_stack',
            '2026-08-29T22:12:30+00:00',
        )
        newer = self._write_update(
            '20260829T224218Z_autonomous-retry-for-cooldown-blocked-publications-added.md',
            'Autonomous retry for cooldown-blocked publications added',
            'watcher_publication_stack',
            '2026-08-29T22:42:18+00:00',
        )
        guardrails = {
            'blockers': ['room_cooldown_active', 'same_event_cooldown_active'],
            'details': {
                'cooldown_minutes': 195,
                'same_event_cooldown_minutes': 195,
                'cooldown_allows_at': '2026-08-29T23:42:16+00:00',
                'same_event_allows_at': '2026-08-29T23:42:16+00:00',
            },
        }

        publish_update_bundle.upsert_pending_publication(
            state,
            room='technocore',
            event_type='docs_change',
            update_path=older,
            score={'total_score': 100, 'recommendation': 'autopublish', 'components': {'airdrop_leverage': 15}},
            guardrails=guardrails,
            log_path=self.log_dir / 'older.json',
        )
        publish_update_bundle.upsert_pending_publication(
            state,
            room='technocore',
            event_type='docs_change',
            update_path=newer,
            score={'total_score': 100, 'recommendation': 'autopublish', 'components': {'airdrop_leverage': 13}},
            guardrails=guardrails,
            log_path=self.log_dir / 'newer.json',
        )

        pending = state['pending_publications']
        self.assertEqual(len(pending), 1)
        only_item = next(iter(pending.values()))
        self.assertEqual(only_item['update_path'], str(newer))
        self.assertEqual(only_item['source_id'], 'watcher_publication_stack')

    def test_distinct_sources_are_kept_separately(self):
        state = publish_update_bundle.default_state()
        a = self._write_update(
            '20260829T224218Z_autonomous-retry-for-cooldown-blocked-publications-added.md',
            'Autonomous retry for cooldown-blocked publications added',
            'watcher_publication_stack',
            '2026-08-29T22:42:18+00:00',
        )
        b = self._write_update(
            '20260829T231205Z_transient-fetch-error-damping-added-to-flipflopper-watcher.md',
            'Transient fetch-error damping added to FlipFlopper watcher',
            'watcher_resilience',
            '2026-08-29T23:12:05+00:00',
        )
        guardrails = {
            'blockers': ['room_cooldown_active'],
            'details': {'cooldown_allows_at': '2026-08-29T23:42:16+00:00', 'cooldown_minutes': 195},
        }

        publish_update_bundle.upsert_pending_publication(
            state,
            room='technocore',
            event_type='docs_change',
            update_path=a,
            score={'total_score': 100, 'recommendation': 'autopublish', 'components': {'airdrop_leverage': 13}},
            guardrails=guardrails,
            log_path=self.log_dir / 'a.json',
        )
        publish_update_bundle.upsert_pending_publication(
            state,
            room='technocore',
            event_type='docs_change',
            update_path=b,
            score={'total_score': 100, 'recommendation': 'autopublish', 'components': {'airdrop_leverage': 15}},
            guardrails=guardrails,
            log_path=self.log_dir / 'b.json',
        )

        self.assertEqual(len(state['pending_publications']), 2)

    def test_load_state_canonicalizes_legacy_pending_duplicates(self):
        older = self._write_update(
            '20260829T221230Z_cooldown-aware-pending-publication-queue-added.md',
            'Cooldown-aware pending publication queue added',
            'watcher_publication_stack',
            '2026-08-29T22:12:30+00:00',
        )
        newer = self._write_update(
            '20260829T224218Z_autonomous-retry-for-cooldown-blocked-publications-added.md',
            'Autonomous retry for cooldown-blocked publications added',
            'watcher_publication_stack',
            '2026-08-29T22:42:18+00:00',
        )
        self.state_path.write_text(json.dumps({
            'posts': [],
            'by_update': {},
            'by_message_hash': {},
            'last_success_by_room': {},
            'last_success_by_room_and_event': {},
            'last_attempt_by_update': {},
            'last_attempt_by_message_hash': {},
            'pending_publications': {
                f'technocore::{older}': {
                    'room': 'technocore',
                    'event_type': 'docs_change',
                    'update_path': str(older),
                    'queued_at': '2026-08-29T22:12:38+00:00',
                    'updated_at': '2026-08-29T22:12:38+00:00',
                    'eligible_at': '2026-08-29T23:42:16+00:00',
                    'score': 100,
                },
                f'technocore::{newer}': {
                    'room': 'technocore',
                    'event_type': 'docs_change',
                    'update_path': str(newer),
                    'queued_at': '2026-08-29T22:42:27+00:00',
                    'updated_at': '2026-08-29T22:42:27+00:00',
                    'eligible_at': '2026-08-29T23:42:16+00:00',
                    'score': 100,
                },
            },
        }, indent=2))

        state = publish_update_bundle.load_state()

        self.assertEqual(len(state['pending_publications']), 1)
        only_item = next(iter(state['pending_publications'].values()))
        self.assertEqual(only_item['update_path'], str(newer))
        self.assertEqual(only_item['source_id'], 'watcher_publication_stack')

        persisted = json.loads(self.state_path.read_text())
        self.assertEqual(len(persisted['pending_publications']), 1)
        persisted_only_item = next(iter(persisted['pending_publications'].values()))
        self.assertEqual(persisted_only_item['update_path'], str(newer))


if __name__ == '__main__':
    unittest.main()
