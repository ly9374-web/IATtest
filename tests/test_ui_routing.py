from __future__ import annotations

import unittest

from streamlit.testing.v1 import AppTest

from iat_core.session import IATSession
from ui.instruction import INSTRUCTION_TEXT


class RoutingTests(unittest.TestCase):
    def _open_instruction(self) -> AppTest:
        app = AppTest.from_file("app.py").run(timeout=10)
        app.text_input(key="concept_input").set_value("环保").run()
        app.button(key="home_start").click().run()
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
        self.assertFalse(app.button(key="home_start").disabled)

    def test_confirm_atomically_creates_session_then_routes_to_task(self) -> None:
        app = self._open_instruction()
        self.assertIsNone(app.session_state["session"])

        app.button(key="instruction_confirm").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["page"], "task")
        self.assertIsInstance(app.session_state["session"], IATSession)
        self.assertEqual(app.session_state["session"].concept, "环保")
        self.assertEqual(len(app.session_state["session"].blocks), 7)
        self.assertEqual(len(app.get("component_instance")), 1)

    def test_incomplete_task_state_falls_back_to_instruction(self) -> None:
        app = AppTest.from_file("app.py").run(timeout=10)
        app.session_state["concept_text"] = "环保"
        app.session_state["page"] = "task"
        app.session_state["session"] = None
        app.run()
        self.assertEqual(app.session_state["page"], "instruction")
        self.assertEqual(app.button(key="instruction_confirm").label, "确定")

    def test_incomplete_report_state_never_renders_report(self) -> None:
        app = AppTest.from_file("app.py").run(timeout=10)
        app.session_state["concept_text"] = "环保"
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
