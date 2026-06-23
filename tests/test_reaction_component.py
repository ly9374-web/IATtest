from __future__ import annotations

from pathlib import Path
import unittest

from components.reaction_task import ReactionEvent, consume_new_event


def event_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "version": 1,
        "event_id": "instance:0:0:1",
        "type": "trial_complete",
        "trial_id": "0:0",
        "key": "s",
        "correct_key": "J",
        "first_key": "s",
        "is_correct": False,
        "rt_ms": 432.18,
        "reason": "first_incorrect",
        "client_time_ms": 12345.67,
    }
    payload.update(overrides)
    return payload


class ReactionEventTests(unittest.TestCase):
    def test_valid_event_is_normalized(self) -> None:
        event = ReactionEvent.from_value(event_payload())
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.key, "S")
        self.assertEqual(event.correct_key, "J")
        self.assertEqual(event.rt_ms, 432.18)

    def test_invalid_protocol_values_are_rejected(self) -> None:
        self.assertIsNone(ReactionEvent.from_value(None))
        self.assertIsNone(
            ReactionEvent.from_value(event_payload(version=2))
        )
        self.assertIsNone(
            ReactionEvent.from_value(event_payload(key="K"))
        )
        self.assertIsNone(
            ReactionEvent.from_value(event_payload(rt_ms=None))
        )
        self.assertIsNone(
            ReactionEvent.from_value(event_payload(is_correct="false"))
        )
        self.assertIsNone(
            ReactionEvent.from_value(event_payload(rt_ms=-1))
        )

    def test_control_event_has_no_reaction_fields(self) -> None:
        event = ReactionEvent.from_value(
            event_payload(
                type="block_start",
                key=None,
                correct_key=None,
                first_key=None,
                is_correct=None,
                rt_ms=None,
                reason="block_start",
            )
        )
        self.assertIsNotNone(event)

    def test_duplicate_event_id_is_consumed_once(self) -> None:
        event = ReactionEvent.from_value(event_payload())
        first, last_id = consume_new_event(event, None)
        duplicate, unchanged_id = consume_new_event(event, last_id)
        self.assertEqual(first, event)
        self.assertEqual(last_id, event.event_id)
        self.assertIsNone(duplicate)
        self.assertEqual(unchanged_id, last_id)


class ReactionLayoutTests(unittest.TestCase):
    def test_overlay_and_skip_share_the_responsive_task_surface(self) -> None:
        html = (
            Path("components/reaction_task/frontend/index.html")
            .read_text(encoding="utf-8")
        )
        self.assertIn('<main id="surface"', html)
        self.assertIn('<button id="skip-block"', html)
        self.assertIn('<div id="block-intro">', html)
        self.assertIn("inset: 0;", html)
        self.assertIn("align-items: center;", html)
        self.assertIn("justify-content: center;", html)
        self.assertIn("right: 24px;", html)
        self.assertIn("bottom: 24px;", html)
        self.assertIn("viewportHeight - 84", html)
        self.assertIn('event.key === "Enter"', html)

    def test_default_scheduler_wraps_native_set_timeout(self) -> None:
        source = (
            Path("components/reaction_task/frontend/reaction_state.mjs")
            .read_text(encoding="utf-8")
        )
        self.assertIn(
            "schedule = (callback, delay) => setTimeout(callback, delay)",
            source,
        )


if __name__ == "__main__":
    unittest.main()
