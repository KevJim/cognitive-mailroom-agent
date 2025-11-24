import pytest
from src.config.loader import load_intent_rules


def test_load_intent_rules_successfully():
    """Tests that the configuration is loaded and parsed into AppConfig."""
    config = load_intent_rules()
    assert len(config.intent_rules) > 0
    assert config.intent_rules[0].intent_id == "INTENT_INVOICE_REQ"


def test_load_nonexistent_file_raises_error():
    """Tests that a RuntimeError is raised if the file doesn't exist."""
    with pytest.raises(RuntimeError):
        load_intent_rules(path="nonexistent.json")

