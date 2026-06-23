"""Swift 基线兼容的随机数生成器和七个 IAT Block 工厂。"""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence
from dataclasses import dataclass
from typing import TypeVar

from .constants import LEFT_KEY, RIGHT_KEY
from .models import BlockType, IATBlock, IATTrial, StimulusCategory
from .stimuli import StimulusBank

_T = TypeVar("_T")
_UINT64_MASK = (1 << 64) - 1


@dataclass(slots=True)
class SeededRandomNumberGenerator:
    """复刻 Swift 源码中的 UInt64 线性同余生成器。

    ``next`` 的乘法和加法按 UInt64 溢出。bounded sampling 使用与
    Swift 标准库一致的 64×64 位乘积高位算法，并以向前
    Fisher-Yates 洗牌供领域工厂使用。
    """

    state: int

    def __init__(self, seed: int) -> None:
        self.state = (
            0x1234567890ABCDEF if seed == 0 else seed & _UINT64_MASK
        )

    def next(self) -> int:
        self.state = (
            2862933555777941757 * self.state + 3037000493
        ) & _UINT64_MASK
        return self.state

    def random_below(self, upper_bound: int) -> int:
        if upper_bound <= 0:
            raise ValueError("upper_bound must be positive")
        if upper_bound > 1 << 64:
            raise ValueError("upper_bound must fit in UInt64")

        # Swift 标准库使用 multiply-high/Lemire bounded sampling。
        # 低 64 位落入拒绝区时继续取样，高 64 位作为最终索引。
        threshold = ((1 << 64) - upper_bound) % upper_bound
        while True:
            value = self.next()
            product = value * upper_bound
            low = product & _UINT64_MASK
            high = product >> 64
            if low >= upper_bound or low >= threshold:
                return high

    def random_bool(self) -> bool:
        # Swift Bool.random(using:) 使用随机 UInt64 的最低位。
        return bool(self.next() & 1)

    def choice(self, values: Sequence[_T]) -> _T:
        if not values:
            raise IndexError("cannot choose from an empty sequence")
        return values[self.random_below(len(values))]

    def shuffle(self, values: MutableSequence[_T]) -> None:
        """原地执行向前 Fisher-Yates 洗牌。"""
        for index in range(0, len(values) - 1):
            swap_index = index + self.random_below(len(values) - index)
            if swap_index != index:
                values[index], values[swap_index] = (
                    values[swap_index],
                    values[index],
                )


class IATBlockFactory:
    @classmethod
    def make_blocks(
        cls,
        stimuli: StimulusBank,
        order_condition: int,
        position_condition: int,
        rng: SeededRandomNumberGenerator,
    ) -> tuple[IATBlock, ...]:
        # 与 Swift 基线一致：order_condition 目前只被保存，不改变顺序。
        del order_condition
        target_left_first = position_condition == 1

        block_1 = cls._make_target_practice(
            stimuli, target_left=target_left_first, rng=rng
        )
        block_2 = cls._make_attribute_practice(stimuli, rng=rng)
        target_negative_blocks = (
            cls._make_combined_practice(
                stimuli,
                target_left=target_left_first,
                target_with_positive=False,
                rng=rng,
            ),
            cls._make_combined_formal(
                stimuli,
                target_left=target_left_first,
                target_with_positive=False,
                rng=rng,
            ),
        )
        target_swap = cls._make_target_swap_practice(
            stimuli, target_left=not target_left_first, rng=rng
        )
        target_positive_blocks = (
            cls._make_combined_practice(
                stimuli,
                target_left=not target_left_first,
                target_with_positive=True,
                rng=rng,
            ),
            cls._make_combined_formal(
                stimuli,
                target_left=not target_left_first,
                target_with_positive=True,
                rng=rng,
            ),
        )
        return (
            block_1,
            block_2,
            *target_negative_blocks,
            target_swap,
            *target_positive_blocks,
        )

    @classmethod
    def _make_target_practice(
        cls,
        stimuli: StimulusBank,
        target_left: bool,
        rng: SeededRandomNumberGenerator,
    ) -> IATBlock:
        # target_left 在 Swift 中传入但未影响当前标签/映射，原样保留。
        del target_left
        trials = cls._make_trials(
            stimuli=stimuli,
            counts=(
                (StimulusCategory.TARGET, 4),
                (StimulusCategory.NEUTRAL, 4),
            ),
            left_categories={StimulusCategory.NEUTRAL},
            rng=rng,
            avoid_repeat=False,
        )
        return IATBlock(
            id=1,
            title="Block 1：目标分类练习",
            left_label="其他",
            right_label=stimuli.concept,
            type=BlockType.TARGET_PRACTICE,
            trials=trials,
        )

    @classmethod
    def _make_attribute_practice(
        cls,
        stimuli: StimulusBank,
        rng: SeededRandomNumberGenerator,
    ) -> IATBlock:
        trials = cls._make_trials(
            stimuli=stimuli,
            counts=(
                (StimulusCategory.POSITIVE, 4),
                (StimulusCategory.NEGATIVE, 4),
            ),
            left_categories={StimulusCategory.POSITIVE},
            rng=rng,
            avoid_repeat=False,
        )
        return IATBlock(
            id=2,
            title="Block 2：属性分类练习",
            left_label="正面",
            right_label="负面",
            type=BlockType.ATTRIBUTE_PRACTICE,
            trials=trials,
        )

    @classmethod
    def _make_combined_practice(
        cls,
        stimuli: StimulusBank,
        target_left: bool,
        target_with_positive: bool,
        rng: SeededRandomNumberGenerator,
    ) -> IATBlock:
        del target_left
        if target_with_positive:
            left_label = f"{stimuli.concept} + 正面"
            right_label = "其他 + 负面"
            left_categories = {
                StimulusCategory.TARGET,
                StimulusCategory.POSITIVE,
            }
        else:
            left_label = "其他 + 正面"
            right_label = f"{stimuli.concept} + 负面"
            left_categories = {
                StimulusCategory.NEUTRAL,
                StimulusCategory.POSITIVE,
            }

        trials = cls._make_trials(
            stimuli=stimuli,
            counts=(
                (StimulusCategory.TARGET, 3),
                (StimulusCategory.NEUTRAL, 3),
                (StimulusCategory.POSITIVE, 2),
                (StimulusCategory.NEGATIVE, 2),
            ),
            left_categories=left_categories,
            rng=rng,
            avoid_repeat=True,
        )
        return IATBlock(
            id=6 if target_with_positive else 3,
            title=(
                "Block 6：兼容联合练习"
                if target_with_positive
                else "Block 3：不兼容联合练习"
            ),
            left_label=left_label,
            right_label=right_label,
            type=(
                BlockType.COMPATIBLE_PRACTICE
                if target_with_positive
                else BlockType.INCOMPATIBLE_PRACTICE
            ),
            trials=trials,
        )

    @classmethod
    def _make_combined_formal(
        cls,
        stimuli: StimulusBank,
        target_left: bool,
        target_with_positive: bool,
        rng: SeededRandomNumberGenerator,
    ) -> IATBlock:
        del target_left
        if target_with_positive:
            left_label = f"{stimuli.concept} + 正面"
            right_label = "其他 + 负面"
            left_categories = {
                StimulusCategory.TARGET,
                StimulusCategory.POSITIVE,
            }
        else:
            left_label = "其他 + 正面"
            right_label = f"{stimuli.concept} + 负面"
            left_categories = {
                StimulusCategory.NEUTRAL,
                StimulusCategory.POSITIVE,
            }

        trials = cls._make_trials(
            stimuli=stimuli,
            counts=(
                (StimulusCategory.TARGET, 4),
                (StimulusCategory.NEUTRAL, 4),
                (StimulusCategory.POSITIVE, 4),
                (StimulusCategory.NEGATIVE, 3),
            ),
            left_categories=left_categories,
            rng=rng,
            avoid_repeat=True,
        )
        return IATBlock(
            id=7 if target_with_positive else 4,
            title=(
                "Block 7：兼容联合正式"
                if target_with_positive
                else "Block 4：不兼容联合正式"
            ),
            left_label=left_label,
            right_label=right_label,
            type=(
                BlockType.COMPATIBLE_FORMAL
                if target_with_positive
                else BlockType.INCOMPATIBLE_FORMAL
            ),
            trials=trials,
        )

    @classmethod
    def _make_target_swap_practice(
        cls,
        stimuli: StimulusBank,
        target_left: bool,
        rng: SeededRandomNumberGenerator,
    ) -> IATBlock:
        del target_left
        trials = cls._make_trials(
            stimuli=stimuli,
            counts=(
                (StimulusCategory.TARGET, 5),
                (StimulusCategory.NEUTRAL, 5),
            ),
            left_categories={StimulusCategory.TARGET},
            rng=rng,
            avoid_repeat=False,
        )
        return IATBlock(
            id=5,
            title="Block 5：目标换位练习",
            left_label=stimuli.concept,
            right_label="其他",
            type=BlockType.TARGET_SWAP_PRACTICE,
            trials=trials,
        )

    @classmethod
    def _make_trials(
        cls,
        stimuli: StimulusBank,
        counts: tuple[tuple[StimulusCategory, int], ...],
        left_categories: set[StimulusCategory],
        rng: SeededRandomNumberGenerator,
        avoid_repeat: bool,
    ) -> tuple[IATTrial, ...]:
        trials: list[IATTrial] = []
        for category, count in counts:
            for _ in range(count):
                stimulus = cls._pick_stimulus(stimuli, category, rng)
                correct_key = (
                    LEFT_KEY if category in left_categories else RIGHT_KEY
                )
                trials.append(
                    IATTrial(
                        stimulus=stimulus,
                        category=category,
                        correct_key=correct_key,
                    )
                )

        rng.shuffle(trials)
        if avoid_repeat:
            return cls._shuffle_avoiding_consecutive_same_stimulus(
                trials, rng
            )
        return tuple(trials)

    @classmethod
    def _shuffle_avoiding_consecutive_same_stimulus(
        cls,
        trials: Sequence[IATTrial],
        rng: SeededRandomNumberGenerator,
    ) -> tuple[IATTrial, ...]:
        result = list(trials)
        for _ in range(20):
            rng.shuffle(result)
            if not cls._has_consecutive_repeat(result):
                return tuple(result)

            for index in range(1, len(result)):
                if result[index].stimulus != result[index - 1].stimulus:
                    continue
                current = result[index].stimulus
                previous = result[index - 1].stimulus
                for candidate in range(index + 1, len(result)):
                    next_stimulus = (
                        result[candidate + 1].stimulus
                        if candidate + 1 < len(result)
                        else ""
                    )
                    if (
                        result[candidate].stimulus != current
                        and result[candidate].stimulus != previous
                        and next_stimulus != current
                    ):
                        result[index], result[candidate] = (
                            result[candidate],
                            result[index],
                        )
                        break

            if not cls._has_consecutive_repeat(result):
                return tuple(result)
        return tuple(result)

    @staticmethod
    def _has_consecutive_repeat(trials: Sequence[IATTrial]) -> bool:
        return any(
            trials[index].stimulus == trials[index - 1].stimulus
            for index in range(1, len(trials))
        )

    @staticmethod
    def _pick_stimulus(
        stimuli: StimulusBank,
        category: StimulusCategory,
        rng: SeededRandomNumberGenerator,
    ) -> str:
        if category is StimulusCategory.TARGET:
            return stimuli.concept
        if category is StimulusCategory.NEUTRAL:
            return rng.choice(stimuli.neutrals)
        if category is StimulusCategory.POSITIVE:
            return rng.choice(stimuli.positives)
        return rng.choice(stimuli.negatives)
