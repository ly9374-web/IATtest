"""刺激词库。"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    DEFAULT_NEGATIVE_WORDS,
    DEFAULT_POSITIVE_WORDS,
    NEUTRAL_WORDS,
)


@dataclass(frozen=True, slots=True)
class StimulusBank:
    concept: str
    positives: tuple[str, ...]
    negatives: tuple[str, ...]
    neutrals: tuple[str, ...] = NEUTRAL_WORDS

    @classmethod
    def create(cls, concept: str) -> StimulusBank:
        return cls(
            concept=concept,
            positives=DEFAULT_POSITIVE_WORDS,
            negatives=DEFAULT_NEGATIVE_WORDS,
        )
