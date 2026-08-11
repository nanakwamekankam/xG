import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

from scapper import fifaindexscrape


class FifaIndexScrapeTests(unittest.TestCase):
    def test_wait_for_manual_challenge_resumes_after_user_confirmation(self):
        class FakePage:
            def __init__(self):
                self.content_calls = 0

            def content(self):
                self.content_calls += 1
                if self.content_calls == 1:
                    return "Performing security verification"
                return "<html><body><a href='/players/1-mesut-ozil/fifa16'>Mesut Özil</a></body></html>"

            def wait_for_timeout(self, *_args, **_kwargs):
                return None

        page = FakePage()

        def fake_input(_prompt):
            return ""

        resolved = fifaindexscrape.wait_for_manual_challenge(
            page,
            prompt=True,
            input_fn=fake_input,
            max_attempts=2,
            delay_seconds=0,
        )

        self.assertTrue(resolved)
        self.assertGreaterEqual(page.content_calls, 2)


if __name__ == "__main__":
    unittest.main()
