from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv

from .routers import auth, ideas
from .database import engine, Base

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="AI Innovation Idea Incubator",
    description="""
    AI-powered platform for refining and scoring business ideas using Gemini 2.5 Pro.
    
    ## Features
    - JWT Authentication with role-based access
    - Complete CRUD operations for innovation ideas
    - Text, enum, boolean, and calculated fields
    - Advanced filtering, pagination, and search
    - AI-powered idea refinement and feasibility scoring
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = [
    "https://deploment-git-main-kunals-projects-6bb44ad3.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(ideas.router, prefix="/ideas", tags=["ideas"])

@app.get("/")
async def root():
    return {
        "message": "AI Innovation Idea Incubator API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-innovation-incubator"}
