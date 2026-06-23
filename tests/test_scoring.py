from __future__ import annotations

import json
import math
import unittest

from iat_core import (
    BlockType,
    DataCleaner,
    ExportBuilder,
    IATBlock,
    IATReport,
    IATSession,
    IATTrial,
    ScoredTrial,
    Stats,
    StimulusCategory,
    TrialResponse,
)


def scored(
    *,
    block_type: BlockType = BlockType.COMPATIBLE_FORMAL,
    rt_ms: float,
    is_correct: bool,
) -> ScoredTrial:
    return ScoredTrial(
        block_type=block_type,
        stimulus="词",
        category=StimulusCategory.POSITIVE,
        correct_key="S",
        first_key="S" if is_correct else "J",
        is_correct=is_correct,
        rt_ms=rt_ms,
    )


def block(
    *,
    block_id: int,
    block_type: BlockType,
    rts_count: int,
) -> IATBlock:
    return IATBlock(
        id=block_id,
        title=f"Block {block_id}",
        left_label="左",
        right_label="右",
        type=block_type,
        trials=[
            IATTrial(
                stimulus=f"词{index}",
                category=StimulusCategory.POSITIVE,
                correct_key="S",
            )
            for index in range(rts_count)
        ],
    )


class StatsTests(unittest.TestCase):
    def test_empty_and_single_value_statistics(self) -> None:
        self.assertEqual(Stats.mean([]), 0)
        self.assertEqual(Stats.standard_deviation([]), 0)
        self.assertEqual(Stats.standard_deviation([500]), 0)
        self.assertEqual(Stats.pooled_standard_deviation([], []), 0)
        self.assertEqual(Stats.accuracy([]), 0)
        self.assertEqual(
            Stats.error_rate([], BlockType.COMPATIBLE_FORMAL),
            0,
        )

    def test_sample_and_pooled_standard_deviation(self) -> None:
        self.assertAlmostEqual(
            Stats.standard_deviation([500, 700]),
            math.sqrt(20_000),
        )
        self.assertAlmostEqual(
            Stats.pooled_standard_deviation([500, 700], [900, 1100]),
            math.sqrt(20_000),
        )


class DataCleanerTests(unittest.TestCase):
    def test_error_uses_condition_correct_mean_plus_400(self) -> None:
        cleaned = DataCleaner.clean(
            [
                scored(rt_ms=600, is_correct=True),
                scored(rt_ms=800, is_correct=True),
                scored(rt_ms=700, is_correct=False),
            ]
        )
        self.assertEqual(
            cleaned.compatible.cleaned_rts,
            (600, 800, 1100),
        )
        self.assertAlmostEqual(cleaned.compatible.accuracy, 2 / 3)
        self.assertEqual(cleaned.all_trials[2].cleaned_rt_ms, 1100)

    def test_error_without_valid_correct_trial_uses_400(self) -> None:
        cleaned = DataCleaner.clean(
            [scored(rt_ms=750, is_correct=False)]
        )
        self.assertEqual(cleaned.compatible.cleaned_rts, (400,))

    def test_extreme_thresholds_are_strict_and_excluded(self) -> None:
        cleaned = DataCleaner.clean(
            [
                scored(rt_ms=199, is_correct=True),
                scored(rt_ms=200, is_correct=True),
                scored(rt_ms=2000, is_correct=True),
                scored(rt_ms=2001, is_correct=False),
            ]
        )
        trials = cleaned.all_trials
        self.assertTrue(trials[0].is_extreme)
        self.assertIsNone(trials[0].cleaned_rt_ms)
        self.assertFalse(trials[1].is_extreme)
        self.assertEqual(trials[1].cleaned_rt_ms, 200)
        self.assertFalse(trials[2].is_extreme)
        self.assertEqual(trials[2].cleaned_rt_ms, 2000)
        self.assertTrue(trials[3].is_extreme)
        self.assertTrue(trials[3].is_excluded)
        self.assertIsNone(trials[3].cleaned_rt_ms)

    def test_non_formal_trials_are_ignored(self) -> None:
        cleaned = DataCleaner.clean(
            [
                scored(
                    block_type=BlockType.COMPATIBLE_PRACTICE,
                    rt_ms=500,
                    is_correct=True,
                ),
                scored(
                    block_type=BlockType.TARGET_PRACTICE,
                    rt_ms=600,
                    is_correct=True,
                ),
            ]
        )
        self.assertEqual(cleaned.all_trials, ())
        self.assertEqual(cleaned.compatible.mean, 0)
        self.assertEqual(cleaned.incompatible.mean, 0)


class ReportTests(unittest.TestCase):
    def test_generated_pairings_make_target_positive_the_compatible_condition(
        self,
    ) -> None:
        session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=20260622,
            subject_id="semantic-check",
        )
        compatible_index = next(
            index
            for index, item in enumerate(session.blocks)
            if item.type == BlockType.COMPATIBLE_FORMAL
        )
        incompatible_index = next(
            index
            for index, item in enumerate(session.blocks)
            if item.type == BlockType.INCOMPATIBLE_FORMAL
        )
        compatible = session.blocks[compatible_index]
        incompatible = session.blocks[incompatible_index]

        self.assertEqual(compatible.id, 7)
        self.assertIn("环保", compatible.left_label)
        self.assertIn("正面词汇", compatible.left_label)
        self.assertEqual(incompatible.id, 4)
        self.assertIn("环保", incompatible.right_label)
        self.assertIn("负面词汇", incompatible.right_label)

        for trial_index, trial in enumerate(compatible.trials):
            session.record_response(
                compatible_index,
                trial_index,
                trial.correct_key,
                True,
                450 + trial_index * 10,
            )
        for trial_index, trial in enumerate(incompatible.trials):
            session.record_response(
                incompatible_index,
                trial_index,
                trial.correct_key,
                True,
                850 + trial_index * 10,
            )

        session.finalize()
        report = session.report
        assert report is not None
        self.assertLess(
            report.compatible_mean_ms,
            report.incompatible_mean_ms,
        )
        self.assertGreater(report.d_score, 0)
        self.assertEqual(report.interpretation_text, "你喜欢环保")

    def test_empty_report_preserves_zero_behavior_and_text(self) -> None:
        report = IATReport.generate(
            subject_id="empty",
            concept="环保",
            link_positive="喜欢",
            link_negative="不喜欢",
            seed=1,
            order_condition=1,
            position_condition=1,
            blocks=[],
            responses=[],
            timestamp="2026-06-22T00:00:00Z",
        )
        self.assertEqual(report.compatible_mean_ms, 0)
        self.assertEqual(report.incompatible_mean_ms, 0)
        self.assertEqual(report.compatible_accuracy, 0)
        self.assertEqual(report.incompatible_accuracy, 0)
        self.assertEqual(report.d_score, 0)
        self.assertEqual(report.interpretation_text, "你对 ‘环保’ 的偏好不明显")
        self.assertEqual(report.compatible_summary_string, "0 ms / 100.0%")
        self.assertEqual(report.scatter_points, ())
        self.assertEqual(report.csv_text, ExportBuilder.CSV_HEADER)
        self.assertEqual(report.json_text, "[]")

    def test_report_uses_only_formal_blocks_and_current_d_formula(self) -> None:
        blocks = [
            block(
                block_id=2,
                block_type=BlockType.ATTRIBUTE_PRACTICE,
                rts_count=1,
            ),
            block(
                block_id=4,
                block_type=BlockType.COMPATIBLE_FORMAL,
                rts_count=2,
            ),
            block(
                block_id=7,
                block_type=BlockType.INCOMPATIBLE_FORMAL,
                rts_count=2,
            ),
        ]
        responses = [
            TrialResponse(0, 0, "S", True, 50),
            TrialResponse(1, 0, "S", True, 500),
            TrialResponse(1, 1, "S", True, 700),
            TrialResponse(2, 0, "S", True, 900),
            TrialResponse(2, 1, "S", True, 1100),
        ]
        report = IATReport.generate(
            subject_id="subject",
            concept="环保",
            link_positive="喜欢",
            link_negative="不喜欢",
            seed=7,
            order_condition=1,
            position_condition=2,
            blocks=blocks,
            responses=responses,
            timestamp="2026-06-22T00:00:00Z",
        )
        self.assertEqual(report.compatible_mean_ms, 600)
        self.assertEqual(report.incompatible_mean_ms, 1000)
        self.assertAlmostEqual(report.d_score, math.sqrt(8))
        self.assertEqual(report.interpretation_text, "你喜欢环保")
        self.assertEqual(len(report.scatter_points), 4)
        self.assertNotIn(",50,", report.csv_text)
        self.assertEqual(len(json.loads(report.json_text)), 4)

    def test_zero_standard_deviation_forces_zero_d_score(self) -> None:
        blocks = [
            block(
                block_id=4,
                block_type=BlockType.COMPATIBLE_FORMAL,
                rts_count=2,
            ),
            block(
                block_id=7,
                block_type=BlockType.INCOMPATIBLE_FORMAL,
                rts_count=2,
            ),
        ]
        responses = [
            TrialResponse(0, 0, "S", True, 500),
            TrialResponse(0, 1, "S", True, 500),
            TrialResponse(1, 0, "S", True, 900),
            TrialResponse(1, 1, "S", True, 900),
        ]
        report = IATReport.generate(
            subject_id="subject",
            concept="环保",
            link_positive="喜欢",
            link_negative="不喜欢",
            seed=7,
            order_condition=1,
            position_condition=1,
            blocks=blocks,
            responses=responses,
        )
        self.assertEqual(report.d_score, 0)
        self.assertEqual(report.interpretation_text, "你对 ‘环保’ 的偏好不明显")

    def test_first_error_rate_uses_original_first_key_correctness(self) -> None:
        blocks = [
            block(
                block_id=4,
                block_type=BlockType.COMPATIBLE_FORMAL,
                rts_count=2,
            ),
            block(
                block_id=7,
                block_type=BlockType.INCOMPATIBLE_FORMAL,
                rts_count=2,
            ),
        ]
        responses = [
            TrialResponse(0, 0, "J", False, 500),
            TrialResponse(0, 1, "S", True, 600),
            TrialResponse(1, 0, "S", True, 700),
            TrialResponse(1, 1, "J", False, 800),
        ]
        report = IATReport.generate(
            subject_id="subject",
            concept="环保",
            link_positive="喜欢",
            link_negative="不喜欢",
            seed=7,
            order_condition=1,
            position_condition=1,
            blocks=blocks,
            responses=responses,
        )
        self.assertEqual(report.compatible_first_error_rate, 0.5)
        self.assertEqual(report.incompatible_first_error_rate, 0.5)
        self.assertEqual(report.compatible_accuracy, 0.5)
        self.assertEqual(report.incompatible_accuracy, 0.5)

    def test_session_finalize_attaches_report(self) -> None:
        session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=20260622,
            subject_id="fixed",
        )
        session.finalize()
        self.assertIsInstance(session.report, IATReport)


class ExportBuilderTests(unittest.TestCase):
    def test_csv_and_json_fields_match_swift_baseline(self) -> None:
        blocks = [
            block(
                block_id=4,
                block_type=BlockType.COMPATIBLE_FORMAL,
                rts_count=1,
            )
        ]
        cleaned = DataCleaner.clean(
            [scored(rt_ms=612.9, is_correct=False)]
        )
        result = ExportBuilder.build(
            subject_id="subject",
            concept="环保",
            seed=42,
            order_condition=1,
            position_condition=2,
            blocks=blocks,
            trials=cleaned.all_trials,
            timestamp="2026-06-22T00:00:00Z",
        )
        rows = result.csv.splitlines()
        self.assertEqual(rows[0], ExportBuilder.CSV_HEADER)
        self.assertEqual(
            rows[1],
            (
                "subject,2026-06-22T00:00:00Z,42,1,2,4,"
                "compatibleFormal,词,正,S,J,false,613,false,false"
            ),
        )

        payload = json.loads(result.json)
        self.assertEqual(
            list(payload[0]),
            [
                "subjectId",
                "timestamp",
                "seed",
                "orderCondition",
                "positionCondition",
                "blockId",
                "blockType",
                "stimulus",
                "category",
                "correctKey",
                "firstKey",
                "isCorrect",
                "rtMs",
                "isExtreme",
                "isExcluded",
            ],
        )
        self.assertEqual(payload[0]["rtMs"], 612)
        self.assertFalse(payload[0]["isCorrect"])


if __name__ == "__main__":
    unittest.main()
