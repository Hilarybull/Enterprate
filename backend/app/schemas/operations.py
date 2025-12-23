"""Operations schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskCreate(BaseModel):
    """Create task"""
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    dueDate: Optional[str] = None
    assignee: Optional[str] = None
    projectId: Optional[str] = None
    tags: List[str] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    dueDate: Optional[str] = None
    assignee: Optional[str] = None

class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    dueDate: Optional[str] = None
    assignee: Optional[str] = None
    projectId: Optional[str] = None
    tags: List[str] = []
    createdAt: str
    completedAt: Optional[str] = None

# Email Automation (SendGrid - Mocked)
class EmailTemplateCreate(BaseModel):
    """Create email template"""
    name: str
    subject: str
    bodyHtml: str
    bodyText: Optional[str] = None
    category: str = "general"  # general, marketing, transactional, notification

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    bodyHtml: Optional[str] = None
    category: Optional[str] = None

class EmailTemplateResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    subject: str
    bodyHtml: str
    bodyText: Optional[str] = None
    category: str
    createdAt: str

class EmailSendRequest(BaseModel):
    """Send email request"""
    templateId: Optional[str] = None
    to: List[str]
    subject: Optional[str] = None
    bodyHtml: Optional[str] = None
    variables: dict = {}  # Template variables for substitution

class EmailSendResponse(BaseModel):
    """Email send response"""
    success: bool
    messageId: Optional[str] = None
    message: str
    mock: bool = True  # Indicates this is mocked

class EmailLogResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    to: List[str]
    subject: str
    status: str  # sent, failed, pending
    sentAt: str
    templateId: Optional[str] = None

# Document Management
class DocumentCreate(BaseModel):
    """Create document"""
    name: str
    type: str  # pdf, doc, spreadsheet, presentation, other
    description: Optional[str] = None
    fileUrl: Optional[str] = None
    content: Optional[str] = None
    category: str = "general"
    tags: List[str] = []

class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    type: str
    description: Optional[str] = None
    fileUrl: Optional[str] = None
    category: str
    tags: List[str] = []
    createdAt: str
    updatedAt: Optional[str] = None

# Workflow Templates
class WorkflowStep(BaseModel):
    """Single workflow step"""
    id: str
    title: str
    description: Optional[str] = None
    order: int
    action: Optional[str] = None  # email, task, notification
    config: dict = {}

class WorkflowTemplateCreate(BaseModel):
    """Create workflow template"""
    name: str
    description: Optional[str] = None
    category: str = "general"
    steps: List[WorkflowStep] = []
    trigger: Optional[str] = None  # manual, scheduled, event

class WorkflowTemplateResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    description: Optional[str] = None
    category: str
    steps: List[WorkflowStep] = []
    trigger: Optional[str] = None
    createdAt: str
    isActive: bool = True
