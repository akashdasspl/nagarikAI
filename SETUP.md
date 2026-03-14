# NagarikAI Platform - Setup Guide

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Node.js 18+ (for frontend, coming soon)

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create and activate virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the server

**Option A: Using startup script**

Windows:
```bash
start.bat
```

Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

**Option B: Direct command**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verify installation

Open your browser and visit:
- API Root: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

You should see the API documentation and be able to test the endpoints.

## Testing the API

### Using curl (Command Line)

**Health Check:**
```bash
curl http://localhost:8000/
```

**Detailed Health Check:**
```bash
curl http://localhost:8000/api/health
```

### Using Browser

Simply navigate to http://localhost:8000/docs to access the interactive Swagger UI where you can test all endpoints.

## Project Structure

```
nagarik-ai-platform/
├── backend/
│   ├── venv/              # Virtual environment (created during setup)
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   ├── start.bat          # Windows startup script
│   ├── start.sh           # Linux/Mac startup script
│   └── README.md          # Backend documentation
├── frontend/
│   └── .gitkeep           # Placeholder (frontend coming in Task 5.1)
├── .kiro/
│   └── specs/             # Kiro specification files
├── README.md              # Project overview
└── SETUP.md               # This file
```

## Next Steps

After completing Task 1.1, the next tasks will:
- Task 1.2: Create mock databases with sample data
- Task 1.3: Create Pydantic data models
- Task 2.x: Implement Beneficiary Discovery Engine
- Task 3.x: Implement Grievance Intelligence Layer
- Task 4.x: Implement CSC Operator Assistant
- Task 5.x: Build React frontend

## Troubleshooting

### Port already in use
If port 8000 is already in use, you can change it:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Virtual environment activation issues
Make sure you're in the `backend` directory when activating the virtual environment.

### Module not found errors
Ensure you've activated the virtual environment and installed all dependencies:
```bash
pip install -r requirements.txt
```

## Development Notes

- The application uses in-memory data stores for the MVP demo
- Data will be reset when the server restarts
- CORS is configured for local development (ports 3000 and 5173)
- Hot reload is enabled - changes to Python files will automatically restart the server
