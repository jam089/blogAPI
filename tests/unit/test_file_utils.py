import json
from pathlib import Path

from core.utils.file_utils import json_read


def test_json_read_returns_list_of_dicts(tmp_path: Path) -> None:
    data = [{"a": "1"}, {"b": "2"}]
    file_path = tmp_path / "data.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    result = json_read(file_path)

    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert result == data


def test_json_read_empty_list(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.json"
    file_path.write_text("[]", encoding="utf-8")

    result = json_read(file_path)

    assert result == []
