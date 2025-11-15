from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 1 week

# Create the main app
app = FastAPI(title="Enterprate OS API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# ============= ENUMS =============

class UserRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class BusinessStatus(str, Enum):
    IDEA = "IDEA"
    FORMATION = "FORMATION"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"

class ProjectType(str, Enum):
    GENESIS = "GENESIS"
    NAVIGATOR = "NAVIGATOR"
    GROWTH = "GROWTH"
    WEBSITE_BUILDER = "WEBSITE_BUILDER"
    OTHER = "OTHER"

class ProjectStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"

class LeadStatus(str, Enum):
    LEAD = "LEAD"
    PROSPECT = "PROSPECT"
    CUSTOMER = "CUSTOMER"
    LOST = "LOST"

# ============= MODELS =============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    passwordHash: Optional[str] = None
    googleId: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Workspace(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    country: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    ownerId: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkspaceCreate(BaseModel):
    name: str
    country: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None

class WorkspaceMembership(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    workspaceId: str
    role: UserRole
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BusinessProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    businessName: Optional[str] = None
    status: BusinessStatus = BusinessStatus.IDEA
    brandTone: Optional[str] = None
    primaryGoal: Optional[str] = None
    targetAudience: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    type: ProjectType
    name: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    config: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    type: ProjectType
    name: str
    config: Optional[Dict[str, Any]] = None

class Website(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    projectId: Optional[str] = None
    name: str
    domain: Optional[str] = None
    published: bool = False
    config: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WebsiteCreate(BaseModel):
    name: str
    domain: Optional[str] = None

class WebsitePage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    websiteId: str
    path: str
    title: str
    content: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WebsitePageCreate(BaseModel):
    path: str
    title: str
    content: Optional[Dict[str, Any]] = None

class Invoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    customerName: str
    amount: float
    currency: str = "USD"
    status: InvoiceStatus = InvoiceStatus.DRAFT
    dueDate: Optional[datetime] = None
    items: Optional[List[Dict[str, Any]]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InvoiceCreate(BaseModel):
    customerName: str
    amount: float
    currency: str = "USD"
    dueDate: Optional[datetime] = None
    items: Optional[List[Dict[str, Any]]] = None

class InvoiceUpdate(BaseModel):
    customerName: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[InvoiceStatus] = None
    dueDate: Optional[datetime] = None

class Lead(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    source: Optional[str] = None
    status: LeadStatus = LeadStatus.LEAD
    notes: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None

class IntelligenceEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    userId: Optional[str] = None
    type: str
    payload: Optional[Dict[str, Any]] = None
    occurredAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IntelligenceEventCreate(BaseModel):
    type: str
    payload: Optional[Dict[str, Any]] = None

# Genesis AI Models
class IdeaScoreRequest(BaseModel):
    idea: str
    targetCustomer: Optional[str] = None

class BusinessBlueprintRequest(BaseModel):
    businessName: str
    industry: str
    targetMarket: str

# ============= AUTH HELPERS =============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {"user_id": user_id, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = decode_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_workspace_id(x_workspace_id: Optional[str] = Header(None)) -> str:
    if not x_workspace_id:
        raise HTTPException(status_code=400, detail="Workspace ID required in X-Workspace-Id header")
    return x_workspace_id

async def verify_workspace_access(workspace_id: str, user: dict) -> bool:
    membership = await db.workspace_memberships.find_one({
        "workspaceId": workspace_id,
        "userId": user["id"]
    })
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to workspace")
    return True

# ============= AUTH ROUTES =============

@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        passwordHash=hash_password(user_data.password)
    )
    
    doc = user.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.users.insert_one(doc)
    
    # Create token
    token = create_token(user.id)
    
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name}
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not user.get('passwordHash'):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user['passwordHash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'])
    
    return {
        "token": token,
        "user": {"id": user['id'], "email": user['email'], "name": user['name']}
    }

@api_router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {"id": user['id'], "email": user['email'], "name": user['name']}

# Google OAuth placeholder - to be implemented with Emergent OAuth
@api_router.get("/auth/google")
async def google_auth():
    return {"message": "Google OAuth integration - to be implemented"}

# ============= WORKSPACE ROUTES =============

@api_router.get("/workspaces")
async def get_workspaces(user: dict = Depends(get_current_user)):
    memberships = await db.workspace_memberships.find({"userId": user['id']}, {"_id": 0}).to_list(100)
    workspace_ids = [m['workspaceId'] for m in memberships]
    
    workspaces = await db.workspaces.find({"id": {"$in": workspace_ids}}, {"_id": 0}).to_list(100)
    
    # Add membership info
    for ws in workspaces:
        membership = next((m for m in memberships if m['workspaceId'] == ws['id']), None)
        ws['role'] = membership['role'] if membership else None
    
    return workspaces

@api_router.post("/workspaces")
async def create_workspace(workspace_data: WorkspaceCreate, user: dict = Depends(get_current_user)):
    # Generate slug from name
    slug = workspace_data.name.lower().replace(' ', '-')
    
    workspace = Workspace(
        name=workspace_data.name,
        slug=slug,
        country=workspace_data.country,
        industry=workspace_data.industry,
        stage=workspace_data.stage,
        ownerId=user['id']
    )
    
    doc = workspace.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.workspaces.insert_one(doc)
    
    # Create membership
    membership = WorkspaceMembership(
        userId=user['id'],
        workspaceId=workspace.id,
        role=UserRole.OWNER
    )
    
    mem_doc = membership.model_dump()
    mem_doc['createdAt'] = mem_doc['createdAt'].isoformat()
    await db.workspace_memberships.insert_one(mem_doc)
    
    # Create business profile
    profile = BusinessProfile(
        workspaceId=workspace.id,
        businessName=workspace_data.name
    )
    
    profile_doc = profile.model_dump()
    profile_doc['createdAt'] = profile_doc['createdAt'].isoformat()
    await db.business_profiles.insert_one(profile_doc)
    
    return workspace.model_dump()

@api_router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str, user: dict = Depends(get_current_user)):
    await verify_workspace_access(workspace_id, user)
    
    workspace = await db.workspaces.find_one({"id": workspace_id}, {"_id": 0})
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Get business profile
    profile = await db.business_profiles.find_one({"workspaceId": workspace_id}, {"_id": 0})
    workspace['businessProfile'] = profile
    
    return workspace

@api_router.patch("/workspaces/{workspace_id}")
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    update_data = {k: v for k, v in workspace_data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    await db.workspaces.update_one({"id": workspace_id}, {"$set": update_data})
    
    workspace = await db.workspaces.find_one({"id": workspace_id}, {"_id": 0})
    return workspace

# ============= PROJECT ROUTES =============

@api_router.get("/workspaces/{workspace_id}/projects")
async def get_projects(workspace_id: str, user: dict = Depends(get_current_user)):
    await verify_workspace_access(workspace_id, user)
    
    projects = await db.projects.find({"workspaceId": workspace_id}, {"_id": 0}).to_list(100)
    return projects

@api_router.post("/workspaces/{workspace_id}/projects")
async def create_project(
    workspace_id: str,
    project_data: ProjectCreate,
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    project = Project(
        workspaceId=workspace_id,
        type=project_data.type,
        name=project_data.name,
        config=project_data.config
    )
    
    doc = project.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.projects.insert_one(doc)
    
    return project.model_dump()

# ============= GENESIS AI ROUTES =============

@api_router.post("/genesis/idea-score")
async def score_idea(
    request: IdeaScoreRequest,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    # Log intelligence event
    event = IntelligenceEvent(
        workspaceId=workspace_id,
        userId=user['id'],
        type="genesis.idea_score",
        payload={"idea": request.idea}
    )
    event_doc = event.model_dump()
    event_doc['occurredAt'] = event_doc['occurredAt'].isoformat()
    await db.intelligence_events.insert_one(event_doc)
    
    # TODO: Implement actual AI scoring logic with LLM
    # For now, return mocked response
    return {
        "success": True,
        "score": 85,
        "analysis": {
            "marketViability": 88,
            "competitionLevel": 72,
            "executionComplexity": 65,
            "revenuePotetial": 90
        },
        "insights": [
            "Strong market demand identified",
            "Moderate competition in the space",
            "Scalable business model potential"
        ],
        "nextSteps": [
            "Conduct customer interviews",
            "Build MVP prototype",
            "Create go-to-market strategy"
        ]
    }

@api_router.post("/genesis/business-blueprint")
async def create_blueprint(
    request: BusinessBlueprintRequest,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    # TODO: Implement actual AI blueprint generation
    return {
        "success": True,
        "blueprint": {
            "businessModel": "SaaS subscription with tiered pricing",
            "targetMarket": request.targetMarket,
            "valueProposition": "AI-powered business operations platform",
            "revenueStreams": ["Monthly subscriptions", "Enterprise contracts"],
            "keyActivities": ["Product development", "Customer support", "Marketing"],
            "keyResources": ["Engineering team", "AI infrastructure", "Customer data"]
        }
    }

# ============= NAVIGATOR ROUTES (Invoicing) =============

@api_router.get("/navigator/invoices")
async def get_invoices(
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    invoices = await db.invoices.find({"workspaceId": workspace_id}, {"_id": 0}).to_list(100)
    return invoices

@api_router.post("/navigator/invoices")
async def create_invoice(
    invoice_data: InvoiceCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    invoice = Invoice(
        workspaceId=workspace_id,
        **invoice_data.model_dump()
    )
    
    doc = invoice.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    if doc['dueDate']:
        doc['dueDate'] = doc['dueDate'].isoformat()
    await db.invoices.insert_one(doc)
    
    # Log event
    event = IntelligenceEvent(
        workspaceId=workspace_id,
        userId=user['id'],
        type="navigator.invoice_created",
        payload={"invoiceId": invoice.id, "amount": invoice.amount}
    )
    event_doc = event.model_dump()
    event_doc['occurredAt'] = event_doc['occurredAt'].isoformat()
    await db.intelligence_events.insert_one(event_doc)
    
    return invoice.model_dump()

@api_router.patch("/navigator/invoices/{invoice_id}")
async def update_invoice(
    invoice_id: str,
    invoice_data: InvoiceUpdate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    update_data = {k: v for k, v in invoice_data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    await db.invoices.update_one(
        {"id": invoice_id, "workspaceId": workspace_id},
        {"$set": update_data}
    )
    
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    return invoice

# ============= GROWTH ROUTES (CRM/Leads) =============

@api_router.get("/growth/leads")
async def get_leads(
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    leads = await db.leads.find({"workspaceId": workspace_id}, {"_id": 0}).to_list(100)
    return leads

@api_router.post("/growth/leads")
async def create_lead(
    lead_data: LeadCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    lead = Lead(
        workspaceId=workspace_id,
        **lead_data.model_dump()
    )
    
    doc = lead.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.leads.insert_one(doc)
    
    # Log event
    event = IntelligenceEvent(
        workspaceId=workspace_id,
        userId=user['id'],
        type="growth.lead_created",
        payload={"leadId": lead.id, "name": lead.name}
    )
    event_doc = event.model_dump()
    event_doc['occurredAt'] = event_doc['occurredAt'].isoformat()
    await db.intelligence_events.insert_one(event_doc)
    
    return lead.model_dump()

@api_router.patch("/growth/leads/{lead_id}")
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    update_data = {k: v for k, v in lead_data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    await db.leads.update_one(
        {"id": lead_id, "workspaceId": workspace_id},
        {"$set": update_data}
    )
    
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    return lead

# ============= WEBSITE BUILDER ROUTES =============

@api_router.get("/websites")
async def get_websites(
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    websites = await db.websites.find({"workspaceId": workspace_id}, {"_id": 0}).to_list(100)
    return websites

@api_router.post("/websites")
async def create_website(
    website_data: WebsiteCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    website = Website(
        workspaceId=workspace_id,
        name=website_data.name,
        domain=website_data.domain,
        config={"theme": "default", "sections": []}
    )
    
    doc = website.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.websites.insert_one(doc)
    
    # Create default home page
    page = WebsitePage(
        websiteId=website.id,
        path="/",
        title="Home",
        content={"sections": []}
    )
    page_doc = page.model_dump()
    page_doc['createdAt'] = page_doc['createdAt'].isoformat()
    await db.website_pages.insert_one(page_doc)
    
    return website.model_dump()

@api_router.get("/websites/{website_id}")
async def get_website(
    website_id: str,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    website = await db.websites.find_one(
        {"id": website_id, "workspaceId": workspace_id},
        {"_id": 0}
    )
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    return website

@api_router.get("/websites/{website_id}/pages")
async def get_website_pages(
    website_id: str,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    pages = await db.website_pages.find({"websiteId": website_id}, {"_id": 0}).to_list(100)
    return pages

@api_router.post("/websites/{website_id}/pages")
async def create_website_page(
    website_id: str,
    page_data: WebsitePageCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    # Verify website exists and belongs to workspace
    website = await db.websites.find_one(
        {"id": website_id, "workspaceId": workspace_id}
    )
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    page = WebsitePage(
        websiteId=website_id,
        **page_data.model_dump()
    )
    
    doc = page.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.website_pages.insert_one(doc)
    
    return page.model_dump()

@api_router.patch("/websites/{website_id}/pages/{page_id}")
async def update_website_page(
    website_id: str,
    page_id: str,
    page_data: WebsitePageCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    update_data = page_data.model_dump()
    
    await db.website_pages.update_one(
        {"id": page_id, "websiteId": website_id},
        {"$set": update_data}
    )
    
    page = await db.website_pages.find_one({"id": page_id}, {"_id": 0})
    return page

# ============= INTELLIGENCE GRAPH ROUTES =============

@api_router.get("/intel/events")
async def get_events(
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user),
    limit: int = 50
):
    await verify_workspace_access(workspace_id, user)
    
    events = await db.intelligence_events.find(
        {"workspaceId": workspace_id},
        {"_id": 0}
    ).sort("occurredAt", -1).limit(limit).to_list(limit)
    
    return events

@api_router.post("/intel/events")
async def create_event(
    event_data: IntelligenceEventCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    await verify_workspace_access(workspace_id, user)
    
    event = IntelligenceEvent(
        workspaceId=workspace_id,
        userId=user['id'],
        type=event_data.type,
        payload=event_data.payload
    )
    
    doc = event.model_dump()
    doc['occurredAt'] = doc['occurredAt'].isoformat()
    await db.intelligence_events.insert_one(doc)
    
    return event.model_dump()

# Include router in main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
