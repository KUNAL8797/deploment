# AI Innovation Idea Incubator - Setup Guide

## Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Git

## Backend Setup
1. Navigate to backend directory: `cd backend`
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment variables in `.env`
6. Run the server: `uvicorn app.main:app --reload`

## Frontend Setup
1. Navigate to frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Configure environment variables in `.env`
4. Run the development server: `npm start`

## Testing the Setup
- Backend API: http://localhost:8000/docs
- Frontend App: http://localhost:3000
- Health Check: http://localhost:8000/health
