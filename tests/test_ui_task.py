from __future__ import annotations

import json
import unittest

from streamlit.testing.v1 import AppTest


class TaskPageTests(unittest.TestCase):
    @staticmethod
    def _state_value(app: AppTest, key: str) -> object:
        try:
            return app.session_state[key]
        except KeyError:
            return ""

    @staticmethod
    def _complete_countdown(app: AppTest, kind: str) -> None:
        token = app.session_state["countdown_token"]
        self_kind = app.session_state["countdown_kind"]
        assert self_kind == kind
        app.session_state["concept_input"] = TaskPageTests._state_value(
            app,
            "concept_text",
        )
        app.session_state["employee_id_input"] = TaskPageTests._state_value(
            app,
            "employee_id",
        )
        app.session_state["job_title_input"] = TaskPageTests._state_value(
            app,
            "job_title",
        )
        app.session_state["countdown_gate_main"] = {
            "event_id": f"{token}:done",
            "token": token,
            "type": "countdown_complete",
        }
        app.run()

    def _open_task(self) -> AppTest:
        app = AppTest.from_file("app.py").run(timeout=10)
        app.text_input(key="concept_input").set_value("环保").run()
        app.text_input(key="employee_id_input").set_value("A0231").run()
        app.text_input(key="job_title_input").set_value("设备检修").run()
        app.button(key="home_start").click().run()
        self._complete_countdown(app, "start")
        app.button(key="instruction_confirm").click().run()
        return app

    @staticmethod
    def _event(
        *,
        event_id: str,
        event_type: str,
        trial_id: str,
        key: str | None = None,
        correct_key: str | None = None,
        first_key: str | None = None,
        is_correct: bool | None = None,
        rt_ms: float | None,
        reason: str | None = None,
    ) -> dict[str, object]:
        return {
            "version": 1,
            "event_id": event_id,
            "type": event_type,
            "trial_id": trial_id,
            "key": key,
            "correct_key": correct_key,
            "first_key": first_key,
            "is_correct": is_correct,
            "rt_ms": rt_ms,
            "reason": reason or event_type,
            "client_time_ms": 1000.0,
        }

    def _send(self, app: AppTest, event: dict[str, object]) -> None:
        app.session_state["reaction_task_main"] = event
        app.run()

    def test_task_opens_with_block_intro_and_stable_session(self) -> None:
        app = self._open_task()
        session = app.session_state["session"]
        seed = session.seed
        blocks = session.blocks

        self.assertEqual(app.session_state["page"], "task")
        self.assertTrue(app.session_state["task_progress"].show_block_intro)
        self.assertEqual(len(app.get("component_instance")), 1)
        args = json.loads(
            app.get("component_instance")[0].proto.json_args
        )
        self.assertTrue(args["block_intro_open"])
        self.assertEqual(args["block_title"], "Block 1：目标分类练习")
        self.assertEqual(args["block_count"], 8)
        self.assertEqual(args["concept"], "环保")

        self._send(
            app,
            self._event(
                event_id="block-start-1",
                event_type="block_start",
                trial_id="0:0",
                rt_ms=None,
            ),
        )
        self.assertFalse(app.session_state["task_progress"].show_block_intro)
        self.assertEqual(app.session_state["session"].seed, seed)
        self.assertEqual(app.session_state["session"].blocks, blocks)

    def test_correct_component_events_record_and_advance(self) -> None:
        app = self._open_task()
        self._send(
            app,
            self._event(
                event_id="block-start-1",
                event_type="block_start",
                trial_id="0:0",
                rt_ms=None,
            ),
        )
        progress = app.session_state["task_progress"]
        session = app.session_state["session"]
        trial = progress.current_trial(session)

        self._send(
            app,
            self._event(
                event_id="correct-1",
                event_type="trial_complete",
                trial_id="0:0",
                key=trial.correct_key,
                correct_key=trial.correct_key,
                first_key=trial.correct_key,
                is_correct=True,
                rt_ms=333.0,
                reason="first_correct",
            ),
        )
        response = app.session_state["session"].response_for(0, 0)
        assert response is not None
        self.assertTrue(response.is_correct)
        self.assertEqual(response.rt_ms, 333.0)
        self.assertEqual(app.session_state["task_progress"].trial_index, 1)

    def test_first_error_and_correction_preserve_initial_result(self) -> None:
        app = self._open_task()
        self._send(
            app,
            self._event(
                event_id="block-start-1",
                event_type="block_start",
                trial_id="0:0",
                rt_ms=None,
            ),
        )
        progress = app.session_state["task_progress"]
        session = app.session_state["session"]
        trial = progress.current_trial(session)
        wrong = "J" if trial.correct_key == "S" else "S"

        self._send(
            app,
            self._event(
                event_id="error-1",
                event_type="trial_complete",
                trial_id="0:0",
                key=trial.correct_key,
                correct_key=trial.correct_key,
                first_key=wrong,
                is_correct=False,
                rt_ms=275.0,
                reason="correction",
            ),
        )
        self.assertEqual(app.session_state["task_progress"].trial_index, 1)
        response = app.session_state["session"].response_for(0, 0)
        assert response is not None
        self.assertEqual(response.first_key, wrong)
        self.assertFalse(response.is_correct)
        self.assertEqual(response.rt_ms, 275.0)

    def test_skip_moves_through_blocks_and_finally_routes_to_report(self) -> None:
        app = self._open_task()
        for block_index in range(7):
            progress = app.session_state["task_progress"]
            self._send(
                app,
                self._event(
                    event_id=f"block-start-{block_index}",
                    event_type="block_start",
                    trial_id=progress.trial_id,
                    rt_ms=None,
                ),
            )
            progress = app.session_state["task_progress"]
            self._send(
                app,
                self._event(
                    event_id=f"skip-{block_index}",
                    event_type="skip_block",
                    trial_id=progress.trial_id,
                    rt_ms=None,
                ),
            )
            if block_index == 3:
                self.assertEqual(app.session_state["page"], "countdown")
                self.assertEqual(
                    app.session_state["countdown_kind"],
                    "after_block_4",
                )
                self._complete_countdown(app, "after_block_4")
            if block_index == 6:
                break
            self.assertEqual(app.session_state["page"], "task")
            self.assertEqual(
                app.session_state["task_progress"].block_index,
                block_index + 1,
            )
            self.assertTrue(
                app.session_state["task_progress"].show_block_intro
            )

        self.assertEqual(app.session_state["page"], "countdown")
        self.assertEqual(app.session_state["countdown_kind"], "after_block_7")
        self._complete_countdown(app, "after_block_7")
        self.assertEqual(app.session_state["page"], "report")
        self.assertIsNotNone(app.session_state["session"].report)


if __name__ == "__main__":
    unittest.main()
