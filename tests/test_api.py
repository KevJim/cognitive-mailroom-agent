import pytest
from fastapi.testclient import TestClient
from src.api.main import app, startup_event
from src.services.db_simulator import db_simulator

# Ensure config is loaded before creating client
startup_event()
client = TestClient(app)


def test_process_invoice_request_happy_path(mocker):
    """
    Integration Test for Scenario A: Successful invoice request.
    Verifies a 202 response and that the correct SP is 'executed'.
    """
    # Spy on the db_simulator to see if it gets called correctly
    mock_execute_sp = mocker.spy(db_simulator, "execute_sp")

    request_body = {
        "channel_id": "EMAIL_GATEWAY",
        "body": "Hola, solicito factura para la orden ORD-999 con RFC XEXX010101000"
    }
    
    response = client.post("/process-message", json=request_body)
    
    assert response.status_code == 202
    
    # TestClient runs background tasks synchronously after the response,
    # so the background task should have completed by now
    
    # Check that the background task called the simulator with correct info
    mock_execute_sp.assert_called_once()
    call_args = mock_execute_sp.call_args
    assert call_args.kwargs["sp_name"] == "sp_finance_process_invoice_request"
    assert call_args.kwargs["params"]["@order_ref"] == "ORD-999"
    assert call_args.kwargs["params"]["@client_rfc"] == "XEXX010101000"
    assert call_args.kwargs["params"]["@request_source"] == "EMAIL_GATEWAY"


def test_process_request_ambiguity_path(mocker):
    """
    Integration Test for Scenario B: Ambiguous request (missing RFC).
    Verifies a 202 response and that the exception is logged.
    """
    mock_log_exception = mocker.spy(db_simulator, "log_exception")
    
    request_body = {
        "channel_id": "CHAT_BOT",
        "body": "Quiero mi factura de la orden ORD-123, por favor."
    }
    
    response = client.post("/process-message", json=request_body)
    
    assert response.status_code == 202
    
    # TestClient runs background tasks synchronously after the response,
    # so the background task should have completed by now
    
    # The 'execute_sp' should have failed, so check that 'log_exception' was called
    mock_log_exception.assert_called_once()
    call_args = mock_log_exception.call_args[0][0]
    assert call_args.intent_id == "INTENT_INVOICE_REQ"
    assert "Mandatory parameter '@client_rfc' is missing" in call_args.error_message

