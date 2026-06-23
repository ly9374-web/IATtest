"""数据清洗、统计量、D 值和报告生成。"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Sequence

from .exporter import ExportBuilder
from .models import (
    BlockStats,
    BlockType,
    CleanedSet,
    CleanedTrial,
    ConditionType,
    IATBlock,
    ScoredTrial,
    ScatterPoint,
    TrialResponse,
)


class Stats:
    @staticmethod
    def mean(values: Sequence[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    @classmethod
    def standard_deviation(cls, values: Sequence[float]) -> float:
        if len(values) <= 1:
            return 0.0
        average = cls.mean(values)
        variance = sum((value - average) ** 2 for value in values) / (
            len(values) - 1
        )
        return math.sqrt(variance)

    @classmethod
    def pooled_standard_deviation(
        cls,
        a: Sequence[float],
        b: Sequence[float],
    ) -> float:
        a_count = len(a)
        b_count = len(b)
        if a_count <= 1 or b_count <= 1:
            return 0.0
        a_variance = cls.standard_deviation(a) ** 2
        b_variance = cls.standard_deviation(b) ** 2
        pooled = (
            (a_count - 1) * a_variance + (b_count - 1) * b_variance
        ) / (a_count + b_count - 2)
        return math.sqrt(pooled)

    @staticmethod
    def accuracy(trials: Sequence[ScoredTrial]) -> float:
        if not trials:
            return 0.0
        correct = sum(1 for trial in trials if trial.is_correct)
        return correct / len(trials)

    @staticmethod
    def error_rate(
        trials: Sequence[ScoredTrial],
        block_type: BlockType,
    ) -> float:
        filtered = [trial for trial in trials if trial.block_type is block_type]
        if not filtered:
            return 0.0
        incorrect = sum(1 for trial in filtered if not trial.is_correct)
        return incorrect / len(filtered)


class DataCleaner:
    @classmethod
    def clean(cls, trials: Sequence[ScoredTrial]) -> CleanedSet:
        compatible_trials = [
            trial
            for trial in trials
            if trial.block_type is BlockType.COMPATIBLE_FORMAL
        ]
        incompatible_trials = [
            trial
            for trial in trials
            if trial.block_type is BlockType.INCOMPATIBLE_FORMAL
        ]

        compatible_cleaned, compatible_stats = cls._clean_block(
            compatible_trials
        )
        incompatible_cleaned, incompatible_stats = cls._clean_block(
            incompatible_trials
        )
        return CleanedSet(
            compatible=compatible_stats,
            incompatible=incompatible_stats,
            all_trials=compatible_cleaned + incompatible_cleaned,
        )

    @staticmethod
    def _clean_block(
        trials: Sequence[ScoredTrial],
    ) -> tuple[list[CleanedTrial], BlockStats]:
        valid_correct_rts = [
            trial.rt_ms
            for trial in trials
            if trial.is_correct and 200 <= trial.rt_ms <= 2000
        ]
        mean_correct = Stats.mean(valid_correct_rts)

        cleaned: list[CleanedTrial] = []
        for trial in trials:
            is_extreme = trial.rt_ms < 200 or trial.rt_ms > 2000
            if is_extreme:
                cleaned_rt_ms = None
            elif trial.is_correct:
                cleaned_rt_ms = trial.rt_ms
            else:
                cleaned_rt_ms = mean_correct + 400

            cleaned.append(
                CleanedTrial(
                    block_type=trial.block_type,
                    stimulus=trial.stimulus,
                    category=trial.category,
                    correct_key=trial.correct_key,
                    first_key=trial.first_key,
                    is_correct=trial.is_correct,
                    rt_ms=trial.rt_ms,
                    is_extreme=is_extreme,
                    is_excluded=is_extreme,
                    cleaned_rt_ms=cleaned_rt_ms,
                )
            )

        return cleaned, BlockStats(
            cleaned_rts=[
                trial.cleaned_rt_ms
                for trial in cleaned
                if trial.cleaned_rt_ms is not None
            ],
            accuracy=Stats.accuracy(trials),
        )


@dataclass(frozen=True, slots=True)
class IATReport:
    interpretation_text: str
    compatible_mean_ms: float
    incompatible_mean_ms: float
    compatible_accuracy: float
    incompatible_accuracy: float
    compatible_first_error_rate: float
    incompatible_first_error_rate: float
    d_score: float
    scatter_points: tuple[ScatterPoint, ...]
    csv_text: str
    json_text: str

    @property
    def compatible_mean_ms_string(self) -> str:
        return f"{self.compatible_mean_ms:.0f} ms"

    @property
    def incompatible_mean_ms_string(self) -> str:
        return f"{self.incompatible_mean_ms:.0f} ms"

    @property
    def compatible_accuracy_string(self) -> str:
        return f"{self.compatible_accuracy * 100:.1f}%"

    @property
    def incompatible_accuracy_string(self) -> str:
        return f"{self.incompatible_accuracy * 100:.1f}%"

    @property
    def d_score_string(self) -> str:
        return f"{self.d_score:.2f}"

    @property
    def compatible_summary_string(self) -> str:
        return (
            f"{self.compatible_mean_ms:.0f} ms / "
            f"{(1 - self.compatible_accuracy) * 100:.1f}%"
        )

    @property
    def incompatible_summary_string(self) -> str:
        return (
            f"{self.incompatible_mean_ms:.0f} ms / "
            f"{(1 - self.incompatible_accuracy) * 100:.1f}%"
        )

    @property
    def compatible_first_error_rate_string(self) -> str:
        return f"{self.compatible_first_error_rate * 100:.1f}%"

    @property
    def incompatible_first_error_rate_string(self) -> str:
        return f"{self.incompatible_first_error_rate * 100:.1f}%"

    @classmethod
    def generate(
        cls,
        subject_id: str,
        concept: str,
        link_positive: str,
        link_negative: str,
        seed: int,
        order_condition: int,
        position_condition: int,
        blocks: Sequence[IATBlock],
        responses: Sequence[TrialResponse],
        *,
        timestamp: str | None = None,
    ) -> IATReport:
        formal_blocks = {
            BlockType.COMPATIBLE_FORMAL,
            BlockType.INCOMPATIBLE_FORMAL,
        }
        scored_trials: list[ScoredTrial] = []

        for block_index, block in enumerate(blocks):
            if block.type not in formal_blocks:
                continue
            for trial_index, trial in enumerate(block.trials):
                response = next(
                    (
                        item
                        for item in responses
                        if item.block_index == block_index
                        and item.trial_index == trial_index
                    ),
                    None,
                )
                if (
                    response is not None
                    and response.first_key is not None
                    and response.rt_ms is not None
                    and response.is_correct is not None
                ):
                    scored_trials.append(
                        ScoredTrial(
                            block_type=block.type,
                            stimulus=trial.stimulus,
                            category=trial.category,
                            correct_key=trial.correct_key,
                            first_key=response.first_key,
                            is_correct=response.is_correct,
                            rt_ms=response.rt_ms,
                        )
                    )

        cleaned = DataCleaner.clean(scored_trials)
        compatible_stats = cleaned.compatible
        incompatible_stats = cleaned.incompatible
        compatible_error_rate = Stats.error_rate(
            scored_trials, BlockType.COMPATIBLE_FORMAL
        )
        incompatible_error_rate = Stats.error_rate(
            scored_trials, BlockType.INCOMPATIBLE_FORMAL
        )
        pooled_sd = Stats.pooled_standard_deviation(
            compatible_stats.cleaned_rts,
            incompatible_stats.cleaned_rts,
        )
        d_score = (
            0.0
            if pooled_sd == 0
            else (
                incompatible_stats.mean - compatible_stats.mean
            )
            / pooled_sd
        )

        if abs(d_score) < 0.15:
            interpretation = f"你对 ‘{concept}’ 的偏好不明显"
        elif d_score > 0:
            interpretation = f"你{link_positive}{concept}"
        else:
            interpretation = f"你{link_negative}{concept}"

        scatter_points = tuple(
            ScatterPoint.create(
                x=trial.rt_ms / 1000.0,
                condition=(
                    ConditionType.COMPATIBLE
                    if trial.block_type is BlockType.COMPATIBLE_FORMAL
                    else ConditionType.INCOMPATIBLE
                ),
            )
            for trial in cleaned.all_trials
        )
        export = ExportBuilder.build(
            subject_id=subject_id,
            concept=concept,
            seed=seed,
            order_condition=order_condition,
            position_condition=position_condition,
            blocks=tuple(blocks),
            trials=cleaned.all_trials,
            timestamp=timestamp,
        )
        return cls(
            interpretation_text=interpretation,
            compatible_mean_ms=compatible_stats.mean,
            incompatible_mean_ms=incompatible_stats.mean,
            compatible_accuracy=compatible_stats.accuracy,
            incompatible_accuracy=incompatible_stats.accuracy,
            compatible_first_error_rate=compatible_error_rate,
            incompatible_first_error_rate=incompatible_error_rate,
            d_score=d_score,
            scatter_points=scatter_points,
            csv_text=export.csv,
            json_text=export.json,
        )
