# EnterprateAI - Product Requirements Document

## Overview
EnterprateAI is a comprehensive AI Operating System for Business that helps entrepreneurs start, run, and grow their businesses. The platform provides tools for business registration, finance & compliance, growth/marketing, operations, and an AI-powered assistant.

## Core Features

### 1. Business Registration
- Multi-step wizard for UK company registration
- Support for 13+ business entity types
- **Dynamic fee table** with fees from official UK Government sources
- Companies House integration for name availability checks
- Real-time guidance and recommendations

### 2. Finance & Compliance
- Expense tracking and management
- Receipt scanning with AI OCR
- Tax estimation calculator with auto-fill from invoices/expenses
- Compliance checklist management (add, edit, delete items)
- Invoice creation and management (now also available via `/api/finance/invoices`)

### 3. Growth & Marketing
- Lead management and CRM
- Marketing campaign management
- Social media content generation
- AI Post Generator
- **Proactive Growth Agent** - AI-powered business monitoring that:
  - Analyzes business performance metrics (leads, revenue, campaigns)
  - Calculates business health score
  - Detects downturns and opportunities
  - Generates AI-powered growth recommendations
  - Human-in-the-loop approval before executing actions

### 4. Business Operations
- Task management
- Agentic Email Sender (AI drafting with human approval)
- AI Document Drafting (quotes, contracts, policies, etc.)

### 5. AI Assistant (EnterprateAI)
- Multi-mode AI assistant (Advisory, Data-Backed, Presentation)
- Context-locked to business domains
- Data-sourcing hierarchy for trust and accuracy

## Architecture

### Tech Stack
- **Frontend:** React, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (via motor async driver)
- **AI:** OpenAI GPT-4o via Emergent LLM Key
- **Auth:** JWT + Emergent-managed Google OAuth
- **Email:** SendGrid

### Key Files
- `/app/backend/app/services/proactive_growth_service.py` - Growth Agent logic
- `/app/backend/app/services/fees_config_service.py` - Dynamic fees configuration
- `/app/frontend/src/pages/enterprise/Growth.js` - Growth module with Growth Agent UI
- `/app/frontend/src/pages/enterprise/BusinessRegistration.js` - Registration with dynamic fees

## What's Been Implemented

### December 2025
- Business Operations Module refactored with Tasks, Agentic Email, AI Document Drafting
- Finance & Compliance enhanced with edit/delete compliance items, auto-fill tax calculator
- Enhanced AI Assistant with multi-mode operation
- Project renamed to "EnterprateAI"
- Documentation suite created

### January 2026
- **Proactive Growth Agent** - Full implementation
  - Business performance analysis API
  - Health score calculation
  - Alert detection for lead decline, revenue decline, conversion drops
  - AI-powered recommendation generation
  - Human-in-the-loop approval/rejection flow
- **Dynamic Fee Table** - API for official UK registration fees
- **API Route Consolidation** - Invoice endpoints now available under `/api/finance/invoices`
- **Obsolete Code Removal** - Removed unused PostgreSQL/SQLAlchemy models and alembic

## API Endpoints

### Growth Agent
- `GET /api/growth/agent/analyze` - Analyze business performance
- `POST /api/growth/agent/recommend` - Generate growth recommendation
- `POST /api/growth/agent/approve` - Approve and execute recommendation
- `POST /api/growth/agent/reject` - Reject recommendation
- `GET /api/growth/agent/recommendations` - List recommendations

### Finance (Consolidated)
- `POST/GET/PATCH /api/finance/invoices` - Invoice management
- `POST/GET/PATCH /api/finance/expenses` - Expense management
- `GET/POST/DELETE /api/finance/compliance` - Compliance management

### Company Profile
- `GET /api/company-profile/fees` - Get all registration fees
- `GET /api/company-profile/fees/{type}` - Get fee for specific business type

## Backlog

### P1 - High Priority
- ✅ Proactive Growth Agent (Completed)
- ✅ Dynamic Fee Table (Completed)
- ✅ API Route Consolidation (Completed)
- ✅ Remove PostgreSQL code (Completed)

### P2 - Medium Priority
- Google Sign-in flow - Note: The intermediate landing page at auth.emergentagent.com is by design (Emergent-managed auth)
- Additional Growth Agent triggers and actions
- Advanced campaign automation

### P3 - Low Priority
- Performance optimizations
- Additional reporting dashboards
- Mobile responsiveness improvements

## Integrations
- **OpenAI GPT-4o** - AI features (via Emergent LLM Key)
- **Companies House API** - Company verification
- **SendGrid** - Email delivery
- **Emergent Google Auth** - OAuth authentication

## Notes
- The application does NOT use PostgreSQL/SQLAlchemy. All data operations use MongoDB.
- JWT tokens support both `user_id` and `sub` claims for compatibility with different auth methods.
- Growth Agent recommendations require human approval before execution.
