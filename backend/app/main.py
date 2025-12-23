"""Main FastAPI application"""
import logging
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.routes import (
    auth, workspaces, projects, genesis, navigator, growth, websites, 
    intel, chat, password_reset, validation_reports,
    blueprint, finance, operations, marketing
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Enterprate OS API", version="1.0.0")

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(projects.router)
api_router.include_router(genesis.router)
api_router.include_router(navigator.router)
api_router.include_router(growth.router)
api_router.include_router(websites.router)
api_router.include_router(intel.router)
api_router.include_router(chat.router)
api_router.include_router(password_reset.router)
api_router.include_router(validation_reports.router)
api_router.include_router(blueprint.router)
api_router.include_router(finance.router)
api_router.include_router(operations.router)
api_router.include_router(marketing.router)

# Include API router in main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.CORS_ORIGINS.split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_db_client():
    """Initialize MongoDB connection on startup"""
    await init_db()
    logger.info("Connected to MongoDB")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    await close_db()
    logger.info("Closed MongoDB connection")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
