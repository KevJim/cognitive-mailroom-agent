# Cognitive Mailroom Agent

A FastAPI-based service that processes unstructured text messages to detect user intents, extract relevant entities, and execute corresponding business actions through stored procedures.

## Overview

Cognitive Mailroom Agent is an intelligent message processing system designed to handle unstructured text requests. It automatically:

- **Detects user intents** using keyword-based matching
- **Extracts entities** (order IDs, tax IDs, etc.) from text using regular expressions
- **Orchestrates actions** by executing stored procedures based on detected intents
- **Handles errors** gracefully by logging exceptions for manual review

## Features

- 🎯 **Intent Detection**: Keyword-based intent recognition from unstructured text
- 📝 **Entity Extraction**: Automatic extraction of structured data (order IDs, RFCs, etc.) from text
- ⚙️ **Configurable Rules**: Intent rules defined in JSON configuration file
- 🔄 **Asynchronous Processing**: Background task processing with immediate acknowledgment
- 🗄️ **Database Integration**: Simulated database with stored procedure execution
- 📊 **Error Logging**: Comprehensive exception tracking for failed requests
- 🧪 **Test Coverage**: Comprehensive test suite using pytest

## Project Structure

```
.
├── src/
│   ├── api/              # FastAPI application and endpoints
│   ├── core/             # Business logic (intent detection, entity extraction)
│   ├── config/           # Configuration loader
│   ├── models/           # Pydantic data models
│   └── services/         # External service integrations (DB simulator)
├── tests/                # Test suite
├── specs/                # Project specifications and documentation
├── intent_rules.json     # Intent detection configuration
├── requirements.txt      # Python dependencies
└── main.py              # Application entry point
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Intent rules are defined in `intent_rules.json`. Each rule specifies:

- `intent_id`: Unique identifier for the intent
- `detection_rules`: Keywords and matching criteria
- `extraction_strategy`: Method for extracting entities
- `target_action`: Stored procedure to execute with parameter mapping

Example configuration:

```json
{
  "intent-rules": [
    {
      "intent_id": "INTENT_INVOICE_REQ",
      "detection_rules": {
        "keywords": ["solicito factura", "factura", "xml", "fiscal"],
        "min_match_count": 1
      },
      "extraction_strategy": "regex_simple",
      "target_action": {
        "type": "stored_procedure",
        "name": "sp_finance_process_invoice_request",
        "params_map": {
          "@order_ref": "extracted_order_id",
          "@client_rfc": "extracted_rfc",
          "@request_source": "_meta.channel_id"
        }
      }
    }
  ]
}
```

## Usage

### Running the Server

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints

#### POST `/process-message`

Processes an unstructured text message asynchronously.

**Request Body**:

```json
{
  "channel_id": "email",
  "body": "Solicito factura para el pedido ORD-12345, RFC ABC123456789"
}
```

**Response** (202 Accepted):

```json
{
  "message": "Request accepted and is being processed."
}
```

**How it works**:

1. Request is immediately acknowledged
2. Intent detection runs in background
3. Entities are extracted from the message body
4. Stored procedure is executed with extracted parameters
5. Errors are logged for manual review if processing fails

## Examples

### Invoice Request

```bash
curl -X POST "http://localhost:8000/process-message" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "email",
    "body": "Hola, solicito factura para el pedido ORD-12345. Mi RFC es ABC123456789"
  }'
```

### Urgent Order Cancellation

```bash
curl -X POST "http://localhost:8000/process-message" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "chat",
    "body": "Necesito cancelar urgentemente el pedido ORD-67890. Hay un error en el pedido."
  }'
```

## Testing

Run the test suite:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run tests for a specific file:

```bash
pytest tests/test_api.py
```

## Entity Extraction

The system currently supports extraction of:

- **Order IDs**: Format `ORD-{digits}` (e.g., `ORD-12345`)
- **RFC (Mexican Tax ID)**: Format matching Mexican tax identification pattern
- **Full text body**: Complete message content
- **Channel ID**: Metadata from request

You can extend entity extraction by adding new regex patterns to `ENTITY_REGEX_MAP` in `src/core/entity_extractor.py`.

## Error Handling

When processing fails, the system:

1. Logs the exception with full context
2. Includes the original request
3. Records the detected intent (if any)
4. Stores timestamp for troubleshooting

Exceptions are stored in the database simulator and can be retrieved for manual review.

## Development

### Adding New Intents

1. Add a new intent rule to `intent_rules.json`
2. Define detection keywords and matching criteria
3. Specify the target stored procedure and parameter mapping
4. Add corresponding entity extraction patterns if needed

### Project Phases

This project follows a phased development approach:

- **Phase 1**: Project scaffolding and setup
- **Phase 2**: Core components (models, config loader)
- **Phase 3**: Business logic (intent detection, entity extraction)
- **Phase 4**: Simulated services (database simulator)
- **Phase 5**: API and orchestration
- **Phase 6**: Testing

See the `specs/` directory for detailed specifications.

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server
- **SQLAlchemy**: SQL toolkit and ORM
- **pytest**: Testing framework

## License

[Specify your license here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support information here]
