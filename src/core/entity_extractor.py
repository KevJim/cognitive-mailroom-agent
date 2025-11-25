import re
from typing import Dict, Optional
from ..models.models import IntentRule

ENTITY_REGEX_MAP = {
    "extracted_order_id": r"\b(ORD-\d+)\b",
    "extracted_rfc": r"\b([A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3})\b"
}


def extract_entities(text: str, rule: IntentRule) -> Dict[str, Optional[str]]:
    """
    Extracts entities from the text based on the target action's parameter map.

    Args:
        text: The unstructured input text.
        rule: The intent rule that was matched.

    Returns:
        A dictionary mapping parameter names (e.g., 'extracted_order_id')
        to the extracted values. Returns None for values that are not found.
    """
    extracted_data = {}
    params_to_find = rule.target_action.params_map.values()

    for entity_name in params_to_find:
        if entity_name == "full_text_body":
            extracted_data[entity_name] = text
            continue
        if entity_name == "_meta.channel_id":
            extracted_data[entity_name] = None
            continue

        regex_pattern = ENTITY_REGEX_MAP.get(entity_name)
        if regex_pattern:
            match = re.search(regex_pattern, text, re.IGNORECASE)
            extracted_data[entity_name] = match.group(1) if match else None
        else:
            extracted_data[entity_name] = None
            
    return extracted_data

