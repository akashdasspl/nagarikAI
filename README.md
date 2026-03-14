# NagarikAI Platform

AI-Powered Citizen Service Intelligence Platform for Chhattisgarh e-District Ecosystem

**Team:** blueBox  
**Event:** Hackathon 2026 Chhattisgarh NIC Smart Governance Initiative  
**Track:** AI & ML Track

## Mission

Moving from digitization to intelligent governance

## Overview

NagarikAI addresses critical challenges in the Chhattisgarh e-District portal through three integrated AI-powered subsystems:

1. **Beneficiary Discovery Engine**: Proactively identifies eligible but unenrolled citizens
2. **Grievance Intelligence Layer**: Automates grievance routing using semantic understanding
3. **CSC Operator Assistant**: Provides real-time validation to reduce application rejections

## Project Structure

```
nagarik-ai-platform/
├── backend/          # FastAPI backend service
├── frontend/         # React web interface (coming soon)
├── .kiro/           # Kiro spec files
└── README.md        # This file
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for API documentation.

### Frontend Setup

Coming soon in Task 5.1

## Development Status

This is an MVP implementation for hackathon demonstration. See `.kiro/specs/nagarik-ai-platform/tasks.md` for the complete implementation plan.

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Frontend**: React, TypeScript, Vite (planned)
- **AI/ML**: Hugging Face Transformers, mBERT (planned)
- **Data**: In-memory stores for MVP demo

## License

Developed for Hackathon 2026 Chhattisgarh NIC Smart Governance Initiative
