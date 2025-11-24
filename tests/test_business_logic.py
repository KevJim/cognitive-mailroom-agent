import pytest
from src.core.intent_detector import detect_intent
from src.core.entity_extractor import extract_entities
from src.config.loader import load_intent_rules


@pytest.fixture(scope="module")
def config():
    return load_intent_rules()


def test_detect_invoice_intent(config):
    """Tests happy path for detecting an invoice request."""
    text = "Hola, solicito factura para la orden ORD-123"
    intent = detect_intent(text, config)
    assert intent is not None
    assert intent.intent_id == "INTENT_INVOICE_REQ"


def test_extract_invoice_entities(config):
    """Tests happy path for extracting invoice entities."""
    text = "Factura para la orden ORD-999 con RFC XEXX010101000"
    rule = detect_intent(text, config)
    entities = extract_entities(text, rule)
    assert entities["extracted_order_id"] == "ORD-999"
    assert entities["extracted_rfc"] == "XEXX010101000"


def test_extract_entities_missing_rfc(config):
    """Tests that a missing entity is returned as None."""
    text = "Necesito la factura de mi orden ORD-555"
    rule = detect_intent(text, config)
    entities = extract_entities(text, rule)
    assert entities["extracted_order_id"] == "ORD-555"
    assert entities["extracted_rfc"] is None

