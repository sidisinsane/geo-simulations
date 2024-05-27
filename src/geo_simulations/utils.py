import io
import json
from typing import Any


def load_json(path: str) -> Any:
    """Load JSON data."""
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise e
    except FileNotFoundError as e:
        raise e
