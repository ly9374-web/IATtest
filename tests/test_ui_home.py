from __future__ import annotations

import unittest

from streamlit.testing.v1 import AppTest

from iat_core.models import CustomPreset


class HomePageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = AppTest.from_file("app.py").run(timeout=10)

    def test_home_components_and_single_submit_flow(self) -> None:
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(
            [(button.label, button.disabled) for button in self.app.button],
            [("开始", False), ("自定义", False)],
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

    def test_custom_dialog_components(self) -> None:
        self.app.button(key="home_custom").click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(
            [area.placeholder for area in self.app.text_area],
            ["正面词汇（输入正面词汇匹配词）", "负面词汇（输入负面词汇匹配词）"],
        )
        self.assertEqual(
            [
                self.app.text_input(key="custom_yy_text").placeholder,
                self.app.text_input(key="custom_zz_text").placeholder,
            ],
            ["yy（正面词汇更快）", "zz（负面词汇更快）"],
        )
        self.assertEqual(
            [
                self.app.button(key="toggle_history").label,
                self.app.button(key="confirm_preset").label,
                self.app.button(key="save_preset").label,
            ],
            ["历史", "确定", "保存"],
        )

    def test_selecting_history_locks_yy_and_zz(self) -> None:
        self.app.session_state["presets"] = [
            CustomPreset(
                id="fixed",
                positive_text="好",
                negative_text="坏",
                yy_text="赞同",
                zz_text="反对",
                updated_at="2026-06-22T00:00:00+00:00",
            )
        ]
        self.app.button(key="home_custom").click().run()
        self.app.button(key="toggle_history").click().run()
        self.app.button(key="select_preset_fixed").click().run()

        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(
            self.app.text_area(key="custom_positive_text").value,
            "好",
        )
        self.assertEqual(
            self.app.text_area(key="custom_negative_text").value,
            "坏",
        )
        self.assertTrue(self.app.text_input(key="custom_yy_text").disabled)
        self.assertTrue(self.app.text_input(key="custom_zz_text").disabled)
        self.assertEqual(
            self.app.text_input(key="custom_yy_text").value,
            "赞同",
        )
        self.assertEqual(
            self.app.text_input(key="custom_zz_text").value,
            "反对",
        )


if __name__ == "__main__":
    unittest.main()
