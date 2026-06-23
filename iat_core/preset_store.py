"""用 JSON 文件替代 Swift UserDefaults 的自定义预设存储。"""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import tempfile

from .models import CustomPreset

DEFAULT_PRESET_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "custom_presets.json"
)


class CustomPresetStore:
    def __init__(self, path: Path | str = DEFAULT_PRESET_PATH) -> None:
        self.path = Path(path)

    def load(self) -> list[CustomPreset]:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                return []
            return [
                CustomPreset(
                    id=str(item["id"]),
                    positive_text=str(item["positive_text"]),
                    negative_text=str(item["negative_text"]),
                    yy_text=str(item["yy_text"]),
                    zz_text=str(item["zz_text"]),
                    updated_at=str(item["updated_at"]),
                )
                for item in payload
                if isinstance(item, dict)
            ]
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            return []

    def save(self, presets: list[CustomPreset]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(
            [asdict(preset) for preset in presets],
            ensure_ascii=False,
            indent=2,
        )
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            temporary_path = Path(handle.name)
        temporary_path.replace(self.path)
