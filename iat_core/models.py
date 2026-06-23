"""与 UI 无关的核心 IAT 数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import random
import uuid


@dataclass(slots=True)
class CustomPreset:
    """对应 Swift ``CustomPreset`` 的可持久化预设。"""

    id: str
    positive_text: str
    negative_text: str
    yy_text: str
    zz_text: str
    updated_at: str

    @classmethod
    def create(
        cls,
        *,
        positive_text: str,
        negative_text: str,
        yy_text: str,
        zz_text: str,
    ) -> CustomPreset:
        return cls(
            id=str(uuid.uuid4()),
            positive_text=positive_text,
            negative_text=negative_text,
            yy_text=yy_text,
            zz_text=zz_text,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    @property
    def display_name(self) -> str:
        left = self.yy_text.strip()
        right = self.zz_text.strip()
        if not left and not right:
            return "未命名"
        return f"{left or 'yy'}/{right or 'zz'}"


@dataclass(frozen=True, slots=True)
class CustomWordConfig:
    """用户提供的正负刺激词和报告解释用语。"""

    positives: tuple[str, ...]
    negatives: tuple[str, ...]
    yy_text: str
    zz_text: str

    def __init__(
        self,
        positives: tuple[str, ...] | list[str],
        negatives: tuple[str, ...] | list[str],
        yy_text: str,
        zz_text: str,
    ) -> None:
        object.__setattr__(self, "positives", tuple(positives))
        object.__setattr__(self, "negatives", tuple(negatives))
        object.__setattr__(self, "yy_text", yy_text)
        object.__setattr__(self, "zz_text", zz_text)


class BlockType(str, Enum):
    TARGET_PRACTICE = "targetPractice"
    ATTRIBUTE_PRACTICE = "attributePractice"
    COMPATIBLE_PRACTICE = "compatiblePractice"
    COMPATIBLE_FORMAL = "compatibleFormal"
    TARGET_SWAP_PRACTICE = "targetSwapPractice"
    INCOMPATIBLE_PRACTICE = "incompatiblePractice"
    INCOMPATIBLE_FORMAL = "incompatibleFormal"


class StimulusCategory(str, Enum):
    TARGET = "target"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"


@dataclass(frozen=True, slots=True)
class IATTrial:
    stimulus: str
    category: StimulusCategory
    correct_key: str


@dataclass(frozen=True, slots=True)
class IATBlock:
    id: int
    title: str
    left_label: str
    right_label: str
    type: BlockType
    trials: tuple[IATTrial, ...]

    def __init__(
        self,
        id: int,
        title: str,
        left_label: str,
        right_label: str,
        type: BlockType,
        trials: tuple[IATTrial, ...] | list[IATTrial],
    ) -> None:
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "left_label", left_label)
        object.__setattr__(self, "right_label", right_label)
        object.__setattr__(self, "type", type)
        object.__setattr__(self, "trials", tuple(trials))


@dataclass(slots=True)
class TrialResponse:
    block_index: int
    trial_index: int
    first_key: str | None = None
    is_correct: bool | None = None
    rt_ms: float | None = None


@dataclass(frozen=True, slots=True)
class ScoredTrial:
    block_type: BlockType
    stimulus: str
    category: StimulusCategory
    correct_key: str
    first_key: str
    is_correct: bool
    rt_ms: float


@dataclass(frozen=True, slots=True)
class CleanedTrial:
    block_type: BlockType
    stimulus: str
    category: StimulusCategory
    correct_key: str
    first_key: str
    is_correct: bool
    rt_ms: float
    is_extreme: bool
    is_excluded: bool
    cleaned_rt_ms: float | None


class ConditionType(str, Enum):
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True, slots=True)
class ScatterPoint:
    x: float
    condition: ConditionType
    jitter: float

    @classmethod
    def create(cls, x: float, condition: ConditionType) -> ScatterPoint:
        return cls(
            x=x,
            condition=condition,
            jitter=random.uniform(-0.5, 0.5),
        )


@dataclass(frozen=True, slots=True)
class BlockStats:
    cleaned_rts: tuple[float, ...]
    accuracy: float

    def __init__(
        self,
        cleaned_rts: tuple[float, ...] | list[float],
        accuracy: float,
    ) -> None:
        object.__setattr__(self, "cleaned_rts", tuple(cleaned_rts))
        object.__setattr__(self, "accuracy", accuracy)

    @property
    def mean(self) -> float:
        # 局部导入避免 models 与 scoring 的模块级循环依赖。
        from .scoring import Stats

        return Stats.mean(self.cleaned_rts)


@dataclass(frozen=True, slots=True)
class CleanedSet:
    compatible: BlockStats
    incompatible: BlockStats
    all_trials: tuple[CleanedTrial, ...]

    def __init__(
        self,
        compatible: BlockStats,
        incompatible: BlockStats,
        all_trials: tuple[CleanedTrial, ...] | list[CleanedTrial],
    ) -> None:
        object.__setattr__(self, "compatible", compatible)
        object.__setattr__(self, "incompatible", incompatible)
        object.__setattr__(self, "all_trials", tuple(all_trials))


@dataclass(frozen=True, slots=True)
class ExportTrial:
    subject_id: str
    timestamp: str
    seed: int
    order_condition: int
    position_condition: int
    block_id: int
    block_type: str
    stimulus: str
    category: str
    correct_key: str
    first_key: str
    is_correct: bool
    rt_ms: int
    is_extreme: bool
    is_excluded: bool
