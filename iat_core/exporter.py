"""保持 Swift 基线字段和字符串行为的 CSV/JSON 导出。"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import NamedTuple

from .models import (
    BlockType,
    CleanedTrial,
    ExportTrial,
    IATBlock,
    StimulusCategory,
)


class ExportResult(NamedTuple):
    csv: str
    json: str


class ExportBuilder:
    CSV_HEADER = (
        "subjectId,timestamp,seed,orderCondition,positionCondition,"
        "blockId,blockType,stimulus,category,correctKey,firstKey,"
        "isCorrect,rtMs,isExtreme,isExcluded"
    )

    @classmethod
    def build(
        cls,
        subject_id: str,
        concept: str,
        seed: int,
        order_condition: int,
        position_condition: int,
        blocks: tuple[IATBlock, ...] | list[IATBlock],
        trials: tuple[CleanedTrial, ...] | list[CleanedTrial],
        *,
        timestamp: str | None = None,
    ) -> ExportResult:
        """生成与 Swift 字段一致的 CSV 和 JSON。

        ``timestamp`` 是测试注入点；正常调用时使用 UTC ISO-8601 秒精度。
        CSV 刻意保持 Swift 当前的直接逗号拼接行为，不增加字段转义。
        """
        resolved_timestamp = timestamp or cls._current_timestamp()
        csv_lines = [cls.CSV_HEADER]
        json_trials: list[ExportTrial] = []

        for trial in trials:
            block_id = cls._block_id_for_type(blocks, trial.block_type)
            category = cls._category_string(trial.category, concept)
            csv_lines.append(
                ",".join(
                    (
                        subject_id,
                        resolved_timestamp,
                        str(seed),
                        str(order_condition),
                        str(position_condition),
                        str(block_id),
                        trial.block_type.value,
                        trial.stimulus,
                        category,
                        trial.correct_key,
                        trial.first_key,
                        cls._swift_bool(trial.is_correct),
                        format(trial.rt_ms, ".0f"),
                        cls._swift_bool(trial.is_extreme),
                        cls._swift_bool(trial.is_excluded),
                    )
                )
            )
            json_trials.append(
                ExportTrial(
                    subject_id=subject_id,
                    timestamp=resolved_timestamp,
                    seed=seed,
                    order_condition=order_condition,
                    position_condition=position_condition,
                    block_id=block_id,
                    block_type=trial.block_type.value,
                    stimulus=trial.stimulus,
                    category=category,
                    correct_key=trial.correct_key,
                    first_key=trial.first_key,
                    is_correct=trial.is_correct,
                    rt_ms=int(trial.rt_ms),
                    is_extreme=trial.is_extreme,
                    is_excluded=trial.is_excluded,
                )
            )

        json_payload = [
            {
                "subjectId": item.subject_id,
                "timestamp": item.timestamp,
                "seed": item.seed,
                "orderCondition": item.order_condition,
                "positionCondition": item.position_condition,
                "blockId": item.block_id,
                "blockType": item.block_type,
                "stimulus": item.stimulus,
                "category": item.category,
                "correctKey": item.correct_key,
                "firstKey": item.first_key,
                "isCorrect": item.is_correct,
                "rtMs": item.rt_ms,
                "isExtreme": item.is_extreme,
                "isExcluded": item.is_excluded,
            }
            for item in json_trials
        ]
        return ExportResult(
            csv="\n".join(csv_lines),
            json=json.dumps(
                json_payload,
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        )

    @staticmethod
    def _current_timestamp() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _block_id_for_type(
        blocks: tuple[IATBlock, ...] | list[IATBlock],
        block_type: BlockType,
    ) -> int:
        match = next((block for block in blocks if block.type is block_type), None)
        return match.id if match is not None else 0

    @staticmethod
    def _category_string(
        category: StimulusCategory,
        concept: str,
    ) -> str:
        if category is StimulusCategory.TARGET:
            return concept
        if category is StimulusCategory.NEUTRAL:
            return "中性词汇"
        if category is StimulusCategory.POSITIVE:
            return "正"
        return "负"

    @staticmethod
    def _swift_bool(value: bool) -> str:
        return "true" if value else "false"
