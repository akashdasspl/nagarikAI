# NagarikAI Platform - Backend

FastAPI backend for the NagarikAI Platform MVP.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /api/health` - Detailed health check with data store counts

## Development

The application uses in-memory data stores (Python dictionaries) for the MVP demo. Data will be lost when the server restarts.
