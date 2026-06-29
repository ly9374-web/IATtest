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

    def test_report_page_renders_safety_layout_and_iat_values(self) -> None:
        app = AppTest.from_file("app.py").run(timeout=10)
        session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=7,
            subject_id="subject",
        )
        session.report = fixed_report()
        app.session_state["concept_text"] = "环保"
        app.session_state["employee_id"] = "A0231"
        app.session_state["job_title"] = "设备检修"
        app.session_state["session"] = session
        app.session_state["page"] = "report"
        app.run()

        self.assertEqual(len(app.exception), 0)
        markdown = [item.value for item in app.markdown]
        joined = "\n".join(markdown)
        expected_order = [
            "作业人员心理安全辅助评估报告",
            "综合风险提示",
            "核心数据概览",
            "散点图",
            "负面表情",
            "维度详情分析",
        ]
        positions = [joined.index(text) for text in expected_order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("员工编号", joined)
        self.assertIn("A0231", joined)
        self.assertIn("岗位", joined)
        self.assertIn("设备检修", joined)
        self.assertIn("D_work: 0.40", joined)
        self.assertIn("环保与负面词汇反应时变长（40%）", joined)
        self.assertIn("对环保正面态度显著度：中", joined)
        self.assertIn("心率变异性（HRV）", joined)
        self.assertIn("职业倦怠风险", joined)
        self.assertIn('data-point-count="4"', joined)

        self.assertEqual(len(app.get("component_instance")), 0)
        self.assertEqual(len(app.get("iframe")), 0)

        self.assertEqual(app.button(key="report_retest").label, "重新测试")

    def test_retest_returns_home(self) -> None:
        app = AppTest.from_file("app.py").run(timeout=10)
        session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=7,
            subject_id="subject",
        )
        session.report = fixed_report()
        app.session_state["concept_text"] = "环保"
        app.session_state["concept_input"] = "环保"
        app.session_state["employee_id"] = "A0231"
        app.session_state["employee_id_input"] = "A0231"
        app.session_state["job_title"] = "设备检修"
        app.session_state["job_title_input"] = "设备检修"
        app.session_state["session"] = session
        app.session_state["page"] = "report"
        app.run()

        app.button(key="report_retest").click().run()

        self.assertEqual(app.session_state["page"], "home")
        self.assertEqual(app.session_state["concept_text"], "")
        self.assertEqual(app.session_state["employee_id"], "")
        self.assertEqual(app.session_state["job_title"], "")
        self.assertIsNone(app.session_state["session"])
        self.assertIsNone(app.session_state["task_progress"])
        self.assertEqual(app.text_input(key="concept_input").value, "")
        self.assertEqual(app.text_input(key="employee_id_input").value, "")
        self.assertEqual(app.text_input(key="job_title_input").value, "")


if __name__ == "__main__":
    unittest.main()
