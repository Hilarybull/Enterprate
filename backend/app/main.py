"""Main FastAPI application"""
import logging
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.routes import (
    auth, workspaces, projects, genesis, navigator, growth, websites, 
    intel, chat, password_reset, validation_reports,
    blueprint, finance, operations, marketing, company_profile,
    scheduling, analytics, notifications, ab_testing, team, ai_websites,
    automation, website_analytics, websocket, domains, catalogue, documents
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="EnterprateAI API", version="2.0.0")

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
api_router.include_router(company_profile.router)
api_router.include_router(scheduling.router)
api_router.include_router(analytics.router)
api_router.include_router(notifications.router)
api_router.include_router(ab_testing.router)
api_router.include_router(team.router)
api_router.include_router(ai_websites.router)
api_router.include_router(automation.router)
api_router.include_router(website_analytics.router)
api_router.include_router(websocket.router)
api_router.include_router(domains.router)

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
