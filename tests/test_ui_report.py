from __future__ import annotations

import json
import unittest

from streamlit.testing.v1 import AppTest

from iat_core import ConditionType, IATReport, IATSession, ScatterPoint
from ui.charts import build_scatter_svg
from ui.report import d_score_display_text


def fixed_report(d_score: float = 0.40) -> IATReport:
    return IATReport(
        interpretation_text="你喜欢环保",
        compatible_mean_ms=600,
        incompatible_mean_ms=1000,
        compatible_accuracy=0.75,
        incompatible_accuracy=0.5,
        compatible_first_error_rate=0.25,
        incompatible_first_error_rate=0.5,
        d_score=d_score,
        scatter_points=(
            ScatterPoint(0.5, ConditionType.COMPATIBLE, -0.25),
            ScatterPoint(0.7, ConditionType.COMPATIBLE, 0.25),
            ScatterPoint(0.9, ConditionType.INCOMPATIBLE, -0.5),
            ScatterPoint(1.1, ConditionType.INCOMPATIBLE, 0.5),
        ),
        csv_text=(
            "subjectId,timestamp,seed,orderCondition,positionCondition,"
            "blockId,blockType,stimulus,category,correctKey,firstKey,"
            "isCorrect,rtMs,isExtreme,isExcluded\n"
            "subject,2026-06-22T00:00:00Z,7,1,2,4,"
            "compatibleFormal,词,正,S,S,true,500,false,false"
        ),
        json_text=json.dumps(
            [
                {
                    "subjectId": "subject",
                    "timestamp": "2026-06-22T00:00:00Z",
                    "seed": 7,
                    "orderCondition": 1,
                    "positionCondition": 2,
                    "blockId": 4,
                    "blockType": "compatibleFormal",
                    "stimulus": "词",
                    "category": "正",
                    "correctKey": "S",
                    "firstKey": "S",
                    "isCorrect": True,
                    "rtMs": 500,
                    "isExtreme": False,
                    "isExcluded": False,
                }
            ],
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )


class ReportPresentationTests(unittest.TestCase):
    def test_precise_d_score_thresholds(self) -> None:
        cases = [
            (0.14, "|D|：0.14 (无明显偏好)"),
            (0.15, "|D|：0.15 (轻微偏好)"),
            (-0.34, "|D|：0.34 (轻微偏好)"),
            (0.35, "|D|：0.35 (中等偏好)"),
            (-0.64, "|D|：0.64 (中等偏好)"),
            (0.65, "|D|：0.65 (强偏好)"),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(
                    d_score_display_text(fixed_report(value), True),
                    expected,
                )
        self.assertEqual(
            d_score_display_text(fixed_report(-0.4), False),
            "-0.40",
        )

    def test_scatter_svg_keeps_two_rows_colors_and_point_count(self) -> None:
        svg = build_scatter_svg(fixed_report().scatter_points)
        self.assertIn('data-point-count="4"', svg)
        self.assertEqual(svg.count("<circle"), 4)
        self.assertEqual(svg.count('fill="#22a447"'), 2)
        self.assertEqual(svg.count('fill="#ff3b30"'), 2)
        self.assertIn('d="M 32 216 H 792 M 32 8 V 216"', svg)

    def test_report_page_order_values_and_export_payloads(self) -> None:
        app = AppTest.from_file("app.py").run(timeout=10)
        session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=7,
            subject_id="subject",
        )
        session.report = fixed_report()
        app.session_state["concept_text"] = "环保"
        app.session_state["session"] = session
        app.session_state["page"] = "report"
        app.run()

        self.assertEqual(len(app.exception), 0)
        markdown = [item.value for item in app.markdown]
        title_positions = [
            next(
                index
                for index, value in enumerate(markdown)
                if f">{title}<" in value
            )
            for title in ("结果解释", "统计数据", "散点图", "导出")
        ]
        self.assertEqual(title_positions, sorted(title_positions))
        joined = "\n".join(markdown)
        self.assertIn("你喜欢环保", joined)
        self.assertIn("兼容正式首此眼动错误概率：25.0%", joined)
        self.assertIn("不兼容正式首此眼动错误概率：50.0%", joined)
        self.assertIn("600 ms / 25.0%", joined)
        self.assertIn("1000 ms / 50.0%", joined)
        self.assertIn("|D|：0.40 (中等偏好)", joined)

        components = app.get("component_instance")
        self.assertEqual(len(components), 1)
        args = json.loads(components[0].proto.json_args)
        self.assertEqual(args["csv_text"], fixed_report().csv_text)
        self.assertEqual(args["json_text"], fixed_report().json_text)

        iframe_nodes = app.get("iframe")
        self.assertEqual(len(iframe_nodes), 1)
        self.assertIn(
            "data-point-count%3D%224%22",
            iframe_nodes[0].proto.src,
        )

        self.assertEqual(app.button(key="report_retest").label, "重新测试")

    def test_retest_returns_home_and_preserves_saved_presets(self) -> None:
        app = AppTest.from_file("app.py").run(timeout=10)
        session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=7,
            subject_id="subject",
        )
        session.report = fixed_report()
        presets = list(app.session_state["presets"])
        app.session_state["concept_text"] = "环保"
        app.session_state["concept_input"] = "环保"
        app.session_state["session"] = session
        app.session_state["page"] = "report"
        app.run()

        app.button(key="report_retest").click().run()

        self.assertEqual(app.session_state["page"], "home")
        self.assertEqual(app.session_state["concept_text"], "")
        self.assertIsNone(app.session_state["session"])
        self.assertIsNone(app.session_state["task_progress"])
        self.assertEqual(app.session_state["presets"], presets)
        self.assertEqual(app.text_input(key="concept_input").value, "")


if __name__ == "__main__":
    unittest.main()
