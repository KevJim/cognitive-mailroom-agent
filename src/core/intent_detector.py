from typing import Optional
from ..models.models import AppConfig, IntentRule


def detect_intent(text: str, config: AppConfig) -> Optional[IntentRule]:
    """
    Detects the user's intent by matching keywords from the text against
    the loaded intent rules.

    Args:
        text: The unstructured input text.
        config: The application configuration containing all intent rules.

    Returns:
        The first matching IntentRule, or None if no intent is detected.
    """
    lower_text = text.lower()
    
    for rule in config.intent_rules:
        match_count = 0
        for keyword in rule.detection_rules.keywords:
            if keyword.lower() in lower_text:
                match_count += 1
        
        if match_count >= rule.detection_rules.min_match_count:
            return rule
            
    return None

