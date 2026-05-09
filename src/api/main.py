"""
FastAPI main application for Insurance Claims API.
"""
# Load environment variables from .env file before any other imports
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import customers, claims, cost, adjustors, chatbot, admin, executive
from src.api.database import engine, Base
from src.api.config import settings
from src.api.exceptions import register_exception_handlers
from src.api.utils.logging_config import setup_logging
from src.api.agents.llm.langfuse_wrapper import initialize_langfuse
import logging
import os

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-Powered Auto Insurance Claims API (Prototype)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (permissive for prototype)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(
    customers.router,
    prefix="/api/v1/customers",
    tags=["Customers"]
)
app.include_router(
    claims.router,
    prefix="/api/v1/claims",
    tags=["Claims"]
)
app.include_router(
    cost.router,
    prefix="/api/v1/cost",
    tags=["Cost Estimation"]
)
app.include_router(
    adjustors.router,
    prefix="/api/v1/adjustors",
    tags=["Adjustors"]
)
app.include_router(
    chatbot.router
)
app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)
app.include_router(
    executive.router,
    prefix="/api/v1"
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Insurance Claims API...")

    # Initialize Langfuse tracing if enabled
    initialize_langfuse(settings.config)

    # Check for reseed marker file
    needs_reseed_marker = ".needs_reseed"
    if os.path.exists(needs_reseed_marker):
        logger.warning("=" * 80)
        logger.warning("⚠️  DATABASE NOT SEEDED!")
        logger.warning("⚠️  PLEASE RESEED the database by running: python scripts/seed-data.py")
        logger.warning("=" * 80)

    # Create database tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Insurance Claims API...")

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Insurance Claims API",
        "version": settings.API_VERSION
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.API_VERSION,
        "api_title": settings.API_TITLE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
