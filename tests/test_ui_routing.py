from __future__ import annotations

import unittest

from streamlit.testing.v1 import AppTest

from iat_core.session import IATSession
from ui.instruction import INSTRUCTION_TEXT


class RoutingTests(unittest.TestCase):
    @staticmethod
    def _state_value(app: AppTest, key: str) -> object:
        try:
            return app.session_state[key]
        except KeyError:
            return ""

    @staticmethod
    def _complete_countdown(app: AppTest, kind: str) -> AppTest:
        token = app.session_state["countdown_token"]
        self_kind = app.session_state["countdown_kind"]
        assert self_kind == kind
        app.session_state["concept_input"] = RoutingTests._state_value(
            app,
            "concept_text",
        )
        app.session_state["employee_id_input"] = RoutingTests._state_value(
            app,
            "employee_id",
        )
        app.session_state["job_title_input"] = RoutingTests._state_value(
            app,
            "job_title",
        )
        app.session_state["countdown_gate_main"] = {
            "event_id": f"{token}:done",
            "token": token,
            "type": "countdown_complete",
        }
        app.run()
        return app

    def _open_instruction(self) -> AppTest:
        app = AppTest.from_file("app.py").run(timeout=10)
        app.text_input(key="concept_input").set_value("环保").run()
        app.text_input(key="employee_id_input").set_value("A0231").run()
        app.text_input(key="job_title_input").set_value("设备检修").run()
        app.button(key="home_start").click().run()
        self._complete_countdown(app, "start")
        return app

    def test_home_to_instruction_and_back_preserves_concept(self) -> None:
        app = self._open_instruction()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["page"], "instruction")
        self.assertEqual(
            [button.key for button in app.button],
            ["instruction_back", "instruction_confirm"],
        )
        self.assertTrue(
            any(
                INSTRUCTION_TEXT.replace("\n", "<br>") in item.value
                for item in app.markdown
            )
        )

        app.button(key="instruction_back").click().run()
        self.assertEqual(app.session_state["page"], "home")
        self.assertEqual(
            app.text_input(key="concept_input").value,
            "环保",
        )
        self.assertEqual(
            app.text_input(key="employee_id_input").value,
            "A0231",
        )
        self.assertEqual(
            app.text_input(key="job_title_input").value,
            "设备检修",
        )
        self.assertFalse(app.button(key="home_start").disabled)

    def test_confirm_atomically_creates_session_then_routes_to_task(self) -> None:
        app = self._open_instruction()
        self.assertIsNone(app.session_state["session"])

        app.button(key="instruction_confirm").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["page"], "task")
        self.assertIsInstance(app.session_state["session"], IATSession)
        self.assertEqual(app.session_state["session"].concept, "环保")
        self.assertEqual(app.session_state["session"].subject_id, "A0231")
        self.assertEqual(len(app.session_state["session"].blocks), 7)
        self.assertEqual(len(app.get("component_instance")), 1)

    def test_incomplete_task_state_falls_back_to_instruction(self) -> None:
        app = AppTest.from_file("app.py").run(timeout=10)
        app.session_state["concept_text"] = "环保"
        app.session_state["employee_id"] = "A0231"
        app.session_state["job_title"] = "设备检修"
        app.session_state["page"] = "task"
        app.session_state["session"] = None
        app.run()
        self.assertEqual(app.session_state["page"], "instruction")
        self.assertEqual(app.button(key="instruction_confirm").label, "确定")

    def test_incomplete_report_state_never_renders_report(self) -> None:
        app = AppTest.from_file("app.py").run(timeout=10)
        app.session_state["concept_text"] = "环保"
        app.session_state["employee_id"] = "A0231"
        app.session_state["job_title"] = "设备检修"
        app.session_state["page"] = "report"
        app.session_state["session"] = None
        app.run()
        self.assertEqual(app.session_state["page"], "instruction")

    def test_fresh_browser_session_starts_on_home(self) -> None:
        first = self._open_instruction()
        self.assertEqual(first.session_state["page"], "instruction")

        refreshed = AppTest.from_file("app.py").run(timeout=10)
        self.assertEqual(refreshed.session_state["page"], "home")
        self.assertIsNone(refreshed.session_state["session"])


if __name__ == "__main__":
    unittest.main()
