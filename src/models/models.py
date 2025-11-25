from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict


class ProcessMessageRequest(BaseModel):
    channel_id: str
    body: str


class DetectionRules(BaseModel):
    keywords: List[str]
    min_match_count: int = 1
    priority_flag: Optional[str] = None


class Action(BaseModel):
    type: str
    name: str
    params_map: Dict[str, str]


class IntentRule(BaseModel):
    intent_id: str
    detection_rules: DetectionRules
    extraction_strategy: str
    target_action: Action

    @model_validator(mode='before')
    @classmethod
    def normalize_action_field(cls, data: dict) -> dict:
        """Normalize the action field to handle both 'et_action' and 'target_action' keys."""
        if isinstance(data, dict):
            if 'et_action' in data and 'target_action' not in data:
                data['target_action'] = data.pop('et_action')
            elif 'et_action' in data and 'target_action' in data:
                data.pop('et_action')
        return data


class AppConfig(BaseModel):
    intent_rules: List[IntentRule] = Field(..., alias='intent-rules')
    
    model_config = ConfigDict(populate_by_name=True)


class ManualException(BaseModel):
    timestamp: datetime
    original_request: ProcessMessageRequest
    error_message: str
    intent_id: Optional[str] = None

