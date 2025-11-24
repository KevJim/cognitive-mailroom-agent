from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from datetime import datetime

from ..models.models import ProcessMessageRequest, AppConfig, ManualException
from ..config.loader import load_intent_rules
from ..core.intent_detector import detect_intent
from ..core.entity_extractor import extract_entities
from ..services.db_simulator import db_simulator

# --- Application Setup ---
app = FastAPI(title="Cognitive Mailroom Agent")
config: AppConfig = None

@app.on_event("startup")
def startup_event():
    """Load configuration on application startup."""
    global config
    config = load_intent_rules()

# --- Orchestration Logic ---
def process_message_task(request: ProcessMessageRequest):
    """
    The main orchestration logic that runs in the background.
    """
    global config
    intent = None
    try:
        # 1. Detect Intent
        intent = detect_intent(request.body, config)
        if not intent:
            raise ValueError("No matching intent found for the request.")

        # 2. Extract Entities
        extracted_data = extract_entities(request.body, intent)
        
        # 3. Map Parameters for Stored Procedure
        sp_params = {}
        for sp_param, entity_key in intent.target_action.params_map.items():
            if entity_key == "_meta.channel_id":
                sp_params[sp_param] = request.channel_id
            else:
                sp_params[sp_param] = extracted_data.get(entity_key)

        # 4. Execute Stored Procedure (Simulated)
        db_simulator.execute_sp(
            sp_name=intent.target_action.name,
            params=sp_params
        )

    except Exception as e:
        # 5. Handle and Log Exceptions
        exception_details = ManualException(
            timestamp=datetime.now(),
            original_request=request,
            error_message=str(e),
            intent_id=intent.intent_id if intent else None,
        )
        db_simulator.log_exception(exception_details)

# --- API Endpoint ---
@app.post("/process-message", status_code=status.HTTP_202_ACCEPTED)
async def process_message(request: ProcessMessageRequest, background_tasks: BackgroundTasks):
    """
    Receives an unstructured text message, acknowledges it immediately,
    and processes it in the background.
    """
    background_tasks.add_task(process_message_task, request)
    return {"message": "Request accepted and is being processed."}

