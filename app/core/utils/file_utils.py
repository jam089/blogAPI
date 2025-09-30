import json
from pathlib import Path


def json_read(file_path: Path) -> list[dict[str, str]]:
    with file_path.open("r", encoding="utf-8") as f:
        data: list[dict[str, str]] = json.load(f)
    return data
