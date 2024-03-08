"""Utility functions."""

import json
from pathlib import Path
from typing import Any


class JsonOpenError(RuntimeError):
    """Raised when there is an error opening a JSON file."""

    pass


def get_json(json_filename: str) -> Any:
    """Get JSON from a file."""
    try:
        file_content = Path(json_filename).read_text(encoding="utf-8")
        return json.loads(file_content)
    except Exception as e:
        raise JsonOpenError(f"Error opening {json_filename}.") from e
