from __future__ import annotations

import unittest
from collections import Counter

from iat_core import (
    BlockType,
    IATSession,
    SeededRandomNumberGenerator,
    StimulusBank,
    StimulusCategory,
)
from iat_core.constants import (
    DEFAULT_NEGATIVE_WORDS,
    DEFAULT_POSITIVE_WORDS,
    NEUTRAL_WORDS,
)


class SeededRandomNumberGeneratorTests(unittest.TestCase):
    def test_uint64_sequence_is_stable(self) -> None:
        rng = SeededRandomNumberGenerator(42)
        self.assertEqual(
            [rng.next() for _ in range(4)],
            [
                9562744903453244591,
                18278647270788561952,
                10770292229496577741,
                13861437123898332102,
            ],
        )

    def test_zero_seed_uses_swift_fallback(self) -> None:
        zero_seed = SeededRandomNumberGenerator(0)
        fallback_seed = SeededRandomNumberGenerator(0x1234567890ABCDEF)
        self.assertEqual(zero_seed.next(), fallback_seed.next())

    def test_bool_shuffle_and_choice_match_swift_standard_library(self) -> None:
        # 由本机 Apple Swift 6.3.2 对同一生成器和 seed=42 产生的基准。
        rng = SeededRandomNumberGenerator(42)
        self.assertTrue(rng.random_bool())
        self.assertFalse(rng.random_bool())
        values = list(range(8))
        rng.shuffle(values)
        self.assertEqual(values, [4, 6, 2, 0, 1, 7, 5, 3])
        self.assertEqual(rng.choice(values), 4)


class StimulusBankTests(unittest.TestCase):
    def test_defaults_preserve_order_counts_and_duplicates(self) -> None:
        bank = StimulusBank.create("环保")
        self.assertEqual(bank.neutrals, NEUTRAL_WORDS)
        self.assertEqual(bank.positives, DEFAULT_POSITIVE_WORDS)
        self.assertEqual(bank.negatives, DEFAULT_NEGATIVE_WORDS)
        self.assertEqual(len(bank.neutrals), 31)
        self.assertEqual(len(bank.positives), 21)
        self.assertEqual(len(bank.negatives), 22)
        self.assertEqual(bank.positives.count("幸福"), 2)
        self.assertEqual(bank.positives.count("美好"), 2)

class BlockFactoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=20260622,
            subject_id="fixed-subject",
        )

    def test_block_identity_titles_labels_and_counts(self) -> None:
        expected = [
            (
                1,
                "Block 1：目标分类练习",
                "中性词汇",
                "环保",
                BlockType.TARGET_PRACTICE,
                8,
            ),
            (
                2,
                "Block 2：属性分类练习",
                "正面词汇",
                "负面词汇",
                BlockType.ATTRIBUTE_PRACTICE,
                8,
            ),
            (
                3,
                "Block 3：不兼容联合练习",
                "中性词汇 + 正面词汇",
                "环保 + 负面词汇",
                BlockType.INCOMPATIBLE_PRACTICE,
                10,
            ),
            (
                4,
                "Block 4：不兼容联合正式",
                "中性词汇 + 正面词汇",
                "环保 + 负面词汇",
                BlockType.INCOMPATIBLE_FORMAL,
                15,
            ),
            (
                5,
                "Block 5：目标换位练习",
                "环保",
                "中性词汇",
                BlockType.TARGET_SWAP_PRACTICE,
                10,
            ),
            (
                6,
                "Block 6：兼容联合练习",
                "环保 + 正面词汇",
                "中性词汇 + 负面词汇",
                BlockType.COMPATIBLE_PRACTICE,
                10,
            ),
            (
                7,
                "Block 7：兼容联合正式",
                "环保 + 正面词汇",
                "中性词汇 + 负面词汇",
                BlockType.COMPATIBLE_FORMAL,
                15,
            ),
        ]
        actual = [
            (
                block.id,
                block.title,
                block.left_label,
                block.right_label,
                block.type,
                len(block.trials),
            )
            for block in self.session.blocks
        ]
        self.assertEqual(actual, expected)
        self.assertEqual(sum(len(block.trials) for block in self.session.blocks), 76)
        self.assertEqual(len(self.session.responses), 76)

    def test_category_counts_and_key_mappings(self) -> None:
        expected_counts = [
            {"target": 4, "neutral": 4},
            {"positive": 4, "negative": 4},
            {"target": 3, "neutral": 3, "positive": 2, "negative": 2},
            {"target": 4, "neutral": 4, "positive": 4, "negative": 3},
            {"target": 5, "neutral": 5},
            {"target": 3, "neutral": 3, "positive": 2, "negative": 2},
            {"target": 4, "neutral": 4, "positive": 4, "negative": 3},
        ]
        left_categories = [
            {StimulusCategory.NEUTRAL},
            {StimulusCategory.POSITIVE},
            {StimulusCategory.NEUTRAL, StimulusCategory.POSITIVE},
            {StimulusCategory.NEUTRAL, StimulusCategory.POSITIVE},
            {StimulusCategory.TARGET},
            {StimulusCategory.TARGET, StimulusCategory.POSITIVE},
            {StimulusCategory.TARGET, StimulusCategory.POSITIVE},
        ]

        for index, block in enumerate(self.session.blocks):
            with self.subTest(block=block.id):
                counts = Counter(trial.category.value for trial in block.trials)
                self.assertEqual(dict(counts), expected_counts[index])
                for trial in block.trials:
                    expected_key = (
                        "S" if trial.category in left_categories[index] else "J"
                    )
                    self.assertEqual(trial.correct_key, expected_key)

    def test_fixed_seed_reproduces_conditions_and_trials(self) -> None:
        repeated = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=20260622,
            subject_id="another-subject",
        )
        self.assertEqual(
            self.session.order_condition,
            repeated.order_condition,
        )
        self.assertEqual(
            self.session.position_condition,
            repeated.position_condition,
        )
        self.assertEqual(self.session.blocks, repeated.blocks)

    def test_different_seed_changes_generated_trials(self) -> None:
        other = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=20260623,
            subject_id="fixed-subject",
        )
        self.assertNotEqual(self.session.blocks, other.blocks)

    def test_order_and_position_do_not_change_current_fixed_layout(self) -> None:
        # 锁定 Swift 当前“参数存在但布局未使用”的行为，防止迁移时误修复。
        layouts = []
        for position in (1, 2):
            rng = SeededRandomNumberGenerator(100)
            from iat_core import IATBlockFactory

            blocks = IATBlockFactory.make_blocks(
                stimuli=StimulusBank.create("环保"),
                order_condition=2,
                position_condition=position,
                rng=rng,
            )
            layouts.append(
                [
                    (block.id, block.left_label, block.right_label, block.type)
                    for block in blocks
                ]
            )
        self.assertEqual(layouts[0], layouts[1])

    def test_record_response_updates_existing_slot_only(self) -> None:
        self.session.record_response(0, 0, "S", False, 412.5)
        response = self.session.responses[0]
        self.assertEqual(response.first_key, "S")
        self.assertFalse(response.is_correct)
        self.assertEqual(response.rt_ms, 412.5)

        before = len(self.session.responses)
        self.session.record_response(99, 99, "J", True, 100.0)
        self.assertEqual(len(self.session.responses), before)


if __name__ == "__main__":
    unittest.main()
