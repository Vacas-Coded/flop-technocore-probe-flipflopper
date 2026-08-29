import importlib.util
import pathlib
import unittest

WATCH_PATH = pathlib.Path('/root/.hermes/scripts/flipflopper_watch.py')
spec = importlib.util.spec_from_file_location('flipwatch', WATCH_PATH)
assert spec is not None and spec.loader is not None
flipwatch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flipwatch)


class ReconcileFetchErrorStateTests(unittest.TestCase):
    def test_first_transient_failure_is_suppressed_until_it_repeats(self):
        state = {'errors': {}, 'error_tracker': {}}

        first = flipwatch.reconcile_fetch_error_state(
            state=state,
            source={'id': 'technocore_auth', 'url': 'https://technocore.chat/auth.md', 'note': 'Technocore auth docs'},
            status=503,
            now='2026-08-29 23:00:00 UTC',
        )
        self.assertTrue(first['suppressed'])
        self.assertEqual(first['tracker']['consecutive_failures'], 1)
        self.assertEqual(first['current_error'], None)
        self.assertEqual(first['new_error_line'], None)

        second = flipwatch.reconcile_fetch_error_state(
            state=state,
            source={'id': 'technocore_auth', 'url': 'https://technocore.chat/auth.md', 'note': 'Technocore auth docs'},
            status=503,
            now='2026-08-29 23:02:00 UTC',
        )
        self.assertFalse(second['suppressed'])
        self.assertEqual(second['tracker']['consecutive_failures'], 2)
        self.assertEqual(second['current_error']['status'], 503)
        self.assertIn('HTTP 503', second['new_error_line'])

    def test_success_resolves_persistent_error_and_clears_tracker(self):
        state = {
            'errors': {
                'technocore_auth': {
                    'status': 503,
                    'url': 'https://technocore.chat/auth.md',
                    'note': 'Technocore auth docs',
                    'last_seen_at': '2026-08-29 23:02:00 UTC',
                }
            },
            'error_tracker': {
                'technocore_auth': {
                    'status': 503,
                    'consecutive_failures': 2,
                    'first_failed_at': '2026-08-29 23:00:00 UTC',
                    'last_seen_at': '2026-08-29 23:02:00 UTC',
                    'transient': True,
                }
            },
        }

        outcome = flipwatch.reconcile_fetch_success(
            state=state,
            source_id='technocore_auth',
        )
        self.assertEqual(outcome['resolved_error_line'], '- technocore_auth: recovered from HTTP 503')
        self.assertNotIn('technocore_auth', state['error_tracker'])


if __name__ == '__main__':
    unittest.main()
