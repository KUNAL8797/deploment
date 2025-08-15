from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from .routers import auth, ideas
from .database import engine, Base

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Innovation Idea Incubator",
    description="""
    AI-powered platform for refining and scoring business ideas using Gemini 2.5 Pro.
    
    ## Features
    - JWT Authentication with role-based access
    - Complete CRUD operations for innovation ideas
    - Text, enum, boolean, and calculated fields
    - Advanced filtering, pagination, and search
    - AI-powered idea refinement (coming in Step 4)
    """,
    version="1.0.0",
    docs_url="/docs"
)

# CORS configuration
origins = [
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
        "features": ["authentication", "ideas-crud", "pagination", "filtering"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-innovation-incubator"}
