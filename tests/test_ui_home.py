from __future__ import annotations

import unittest

from streamlit.testing.v1 import AppTest


class HomePageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = AppTest.from_file("app.py").run(timeout=10)

    def test_home_components_and_single_submit_flow(self) -> None:
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(
            [(button.label, button.disabled) for button in self.app.button],
            [("开始", False)],
        )
        self.assertEqual(
            self.app.text_input(key="concept_input").placeholder,
            "输入测试目标（例如：环保）",
        )

        self.app.button(key="home_start").click().run()
        self.assertEqual(self.app.session_state["page"], "home")

        self.app.text_input(key="concept_input").set_value("环保")
        self.app.button(key="home_start").click().run()
        self.assertEqual(self.app.session_state["page"], "instruction")
        self.assertEqual(self.app.session_state["concept_text"], "环保")


if __name__ == "__main__":
    unittest.main()
