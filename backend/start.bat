@echo off
echo Starting NagarikAI Platform Backend...
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
