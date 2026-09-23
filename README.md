# JARVIS AI Assistant V3

A personal desktop-style AI assistant running locally through a web interface.

## Technology Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: HTML, CSS, Vanilla JavaScript (to be implemented in later phases)
- **AI**: Gemini through OpenAI-compatible API
- **Configuration**: Pydantic Settings

## Project Structure

```
jarvis-assistant-v3/
├── server.py                 # Main entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
├── PROJECT_STATE.md         # Development state tracking
└── app/
    ├── main.py              # FastAPI application setup
    ├── config.py            # Configuration management
    ├── ai/
    │   └── client.py        # Gemini AI client abstraction
    └── routes/
        ├── health.py        # Health check endpoint
        └── chat.py          # Chat endpoint with streaming
```

## Getting Started

### Prerequisites

- Python 3.8+
- Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your Gemini API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your actual GEMINI_API_KEY
   ```

### Running the Application

```bash
python server.py
```

The server will start at http://localhost:8000

## API Endpoints

### Health Check
```
GET /api/health
```
Returns application status and Gemini configuration status.

### Chat
```
POST /api/chat
```
Accepts JSON with `message` field and returns a streaming response from Gemini AI.

Example request:
```json
{
  "message": "Hello, JARVIS!",
  "temperature": 0.7,
  "max_tokens": 150
}
```

Returns a Server-Sent Events stream with chunks of the AI response.

## Development

This is Phase 1 of the JARVIS AI Assistant V3 project. See `PROJECT_STATE.md` for current development status and future phases.

## License

MIT