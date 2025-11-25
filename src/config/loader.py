import json
from functools import lru_cache
from pathlib import Path
from pydantic import ValidationError

from ..models.models import AppConfig


@lru_cache(maxsize=1)
def load_intent_rules(path: str = "intent_rules.json") -> AppConfig:
    """
    Loads and validates the intent rules from the specified JSON file.
    The result is cached to avoid repeated file reads.
    
    Args:
        path: Path to the intent_rules.json file. Defaults to "intent_rules.json"
              in the current working directory.
    
    Returns:
        AppConfig: Validated configuration object containing intent rules.
    
    Raises:
        RuntimeError: If the file is not found, invalid, or cannot be decoded.
    """
    try:
        config_path = Path(path)
        if not config_path.is_absolute():
            config_path = Path(__file__).parent.parent.parent / path
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppConfig(**data)
    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found at: {path}")
    except ValidationError as e:
        raise RuntimeError(f"Configuration file is invalid: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Could not decode JSON from file: {path}. Error: {e}")

