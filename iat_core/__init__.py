"""与 Streamlit UI 无关的 IAT 领域逻辑包。"""

from .block_factory import IATBlockFactory, SeededRandomNumberGenerator
from .models import (
    BlockStats,
    BlockType,
    CleanedSet,
    CleanedTrial,
    ConditionType,
    CustomPreset,
    CustomWordConfig,
    ExportTrial,
    IATBlock,
    IATTrial,
    ScoredTrial,
    ScatterPoint,
    StimulusCategory,
    TrialResponse,
)
from .exporter import ExportBuilder, ExportResult
from .scoring import DataCleaner, IATReport, Stats
from .session import IATSession
from .stimuli import StimulusBank
from .preset_store import CustomPresetStore
from .task_flow import TaskEventOutcome, TaskProgress, block_instruction_text

__all__ = [
    "BlockStats",
    "BlockType",
    "CleanedSet",
    "CleanedTrial",
    "ConditionType",
    "CustomPreset",
    "CustomPresetStore",
    "CustomWordConfig",
    "DataCleaner",
    "ExportBuilder",
    "ExportResult",
    "ExportTrial",
    "IATBlock",
    "IATBlockFactory",
    "IATReport",
    "IATSession",
    "IATTrial",
    "ScoredTrial",
    "ScatterPoint",
    "SeededRandomNumberGenerator",
    "Stats",
    "StimulusBank",
    "StimulusCategory",
    "TrialResponse",
    "TaskProgress",
    "TaskEventOutcome",
    "block_instruction_text",
]
