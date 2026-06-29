from __future__ import annotations

from pathlib import Path
import unittest

from components.countdown_gate import CountdownEvent, consume_new_countdown_event


class CountdownComponentTests(unittest.TestCase):
    def test_valid_complete_event_is_accepted(self) -> None:
        event = CountdownEvent.from_value(
            {
                "event_id": "start:1",
                "token": "start",
                "type": "countdown_complete",
            }
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.token, "start")

    def test_duplicate_event_id_is_consumed_once(self) -> None:
        event = CountdownEvent.from_value(
            {
                "event_id": "after_block_4:1",
                "token": "after_block_4",
                "type": "countdown_complete",
            }
        )
        first, last_id = consume_new_countdown_event(event, None)
        duplicate, unchanged_id = consume_new_countdown_event(event, last_id)
        self.assertEqual(first, event)
        self.assertIsNone(duplicate)
        self.assertEqual(unchanged_id, last_id)

    def test_frontend_uses_eight_second_animation(self) -> None:
        html = Path(
            "components/countdown_gate/frontend/index.html"
        ).read_text(encoding="utf-8")
        self.assertIn("duration_seconds ?? 8", html)
        self.assertIn("requestAnimationFrame(animate)", html)
        self.assertIn("conic-gradient", html)
        self.assertIn("countdown_complete", html)


if __name__ == "__main__":
    unittest.main()
