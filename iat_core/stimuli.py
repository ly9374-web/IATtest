"""刺激词库及自定义词的回退规则。"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    DEFAULT_NEGATIVE_WORDS,
    DEFAULT_POSITIVE_WORDS,
    NEUTRAL_WORDS,
)
from .models import CustomWordConfig


@dataclass(frozen=True, slots=True)
class StimulusBank:
    concept: str
    positives: tuple[str, ...]
    negatives: tuple[str, ...]
    neutrals: tuple[str, ...] = NEUTRAL_WORDS

    @classmethod
    def create(
        cls,
        concept: str,
        custom_config: CustomWordConfig | None = None,
    ) -> StimulusBank:
        positives = (
            custom_config.positives
            if custom_config is not None and custom_config.positives
            else DEFAULT_POSITIVE_WORDS
        )
        negatives = (
            custom_config.negatives
            if custom_config is not None and custom_config.negatives
            else DEFAULT_NEGATIVE_WORDS
        )
        return cls(
            concept=concept,
            positives=tuple(positives),
            negatives=tuple(negatives),
        )

