"""Enum definitions"""
from enum import Enum

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
