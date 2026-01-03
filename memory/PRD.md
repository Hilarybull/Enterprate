# EnterprateAI - Product Requirements Document

## Overview
EnterprateAI is a comprehensive AI Operating System for Business that helps entrepreneurs start, run, and grow their businesses. The platform provides tools for business registration, finance & compliance, growth/marketing, operations, and an AI-powered assistant.

## Core Features

### 1. Business Registration
- Multi-step wizard for UK company registration
- Support for 13+ business entity types
- **Dynamic fee table** with fees from official UK Government sources (API: `/api/company-profile/fees`)
- Companies House integration for name availability checks (requires valid API key)
- Real-time guidance and recommendations

### 2. Finance & Compliance
- Expense tracking and management
- Receipt scanning with AI OCR
- Tax estimation calculator with auto-fill from invoices/expenses
- Compliance checklist management (add, edit, delete items)
- Invoice creation and management (consolidated under `/api/finance/invoices`)

### 3. Growth & Marketing
- Lead management and CRM
- Marketing campaign management (includes Instagram)
- Social media content generation
- AI Post Generator
- **Proactive Growth Agent** - AI-powered business monitoring that:
  - Analyzes business performance metrics (leads, revenue, campaigns)
  - Calculates business health score (0-100)
  - Detects downturns and opportunities with multiple alert types
  - Generates AI-powered growth recommendations
  - Human-in-the-loop approval before executing actions
  - **Automated scheduling at optimal posting times**

### 4. Advanced Analytics Dashboard (NEW)
- **Dashboard Overview**: Revenue, profit, leads, campaigns metrics
- **Revenue Trends**: 7/30/90-day trends with daily breakdown
- **Lead Funnel**: Full funnel visualization (NEW → CONTACTED → QUALIFIED → CONVERTED → LOST)
- **Campaign Performance**: ROI, CTR, conversions by campaign
- **Business Reports**: Weekly, Monthly, Quarterly comprehensive reports with insights and recommendations

### 5. Automated Scheduling Service (NEW)
- **Optimal Posting Times**: Platform-specific scheduling (LinkedIn, Twitter, Facebook, Instagram)
- **Engagement Predictions**: Score-based recommendations for best posting times
- **Automated Execution**: Growth Agent can schedule posts at optimal times
- **Action Management**: View, execute, or cancel scheduled actions

### 6. Business Operations
- Task management
- Agentic Email Sender (AI drafting with human approval)
- AI Document Drafting (quotes, contracts, policies, etc.)

### 7. AI Assistant (EnterprateAI)
- Multi-mode AI assistant (Advisory, Data-Backed, Presentation)
- Context-locked to business domains
- Data-sourcing hierarchy for trust and accuracy

## Architecture

### Tech Stack
- **Frontend:** React, Tailwind CSS, shadcn/ui (mobile-responsive)
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (via motor async driver)
- **AI:** OpenAI GPT-4o via Emergent LLM Key
- **Auth:** JWT + Emergent-managed Google OAuth
- **Email:** SendGrid

### New Services Added
- `/app/backend/app/services/scheduling_service.py` - Automated scheduling with optimal times
- `/app/backend/app/services/advanced_analytics_service.py` - Dashboard and reporting
- `/app/backend/app/routes/scheduling.py` - Scheduling API endpoints
- `/app/backend/app/routes/analytics.py` - Analytics API endpoints

## API Endpoints

### Scheduling (NEW)
- `GET /api/scheduling/optimal-times?platform=instagram&count=5` - Get optimal posting times
- `POST /api/scheduling/actions` - Schedule a growth action
- `GET /api/scheduling/actions` - List scheduled actions
- `POST /api/scheduling/actions/{id}/execute` - Execute an action
- `DELETE /api/scheduling/actions/{id}` - Cancel an action

### Analytics (NEW)
- `GET /api/analytics/dashboard` - Comprehensive dashboard overview
- `GET /api/analytics/revenue-trends?days=30` - Revenue trends
- `GET /api/analytics/lead-funnel` - Lead funnel analytics
- `GET /api/analytics/campaign-performance` - Campaign metrics
- `GET /api/analytics/social?days=30` - Social media analytics
- `GET /api/analytics/report?report_type=monthly` - Generate business report

### Growth Agent
- `GET /api/growth/agent/analyze` - Analyze business performance (includes new alerts)
- `POST /api/growth/agent/recommend` - Generate recommendation (supports: lead_decline, conversion_decline, revenue_decline, no_campaigns, low_engagement, growth_opportunity, instagram_campaign)
- `POST /api/growth/agent/approve` - Approve with automatic scheduling
- `POST /api/growth/agent/reject` - Reject recommendation

### Finance (Consolidated)
- `POST/GET/PATCH /api/finance/invoices` - Invoice management
- `POST/GET/PATCH /api/finance/expenses` - Expense management
- `GET/POST/DELETE /api/finance/compliance` - Compliance management

## What's Been Implemented

### January 2026 - Phase 2
- **Proactive Growth Agent Enhancements**
  - Additional alert types: low_engagement, growth_opportunity, instagram_opportunity
  - Automated scheduling integration with optimal posting times
  - Instagram campaign support
- **Advanced Analytics Dashboard**
  - Dashboard overview with KPIs
  - Revenue trends (7/30/90 days)
  - Lead funnel visualization with conversion rates
  - Business report generation (weekly/monthly/quarterly)
- **Scheduling Service**
  - Platform-specific optimal posting times
  - Engagement score predictions
  - Automated action execution
- **Instagram Integration** as a marketing platform
- **Mobile Responsiveness** - Growth page with 6 responsive tabs
- **API Route Consolidation** - Invoice endpoints under `/api/finance/`
- **Code Cleanup** - Removed obsolete PostgreSQL models

### December 2025 - Phase 1
- Business Operations Module (Tasks, Agentic Email, AI Docs)
- Finance & Compliance (edit/delete compliance, auto-fill tax)
- Enhanced AI Assistant with multi-mode operation
- Project renamed to "EnterprateAI"
- Documentation suite created

## Integrations
- **OpenAI GPT-4o** - AI features (via Emergent LLM Key)
- **Companies House API** - Company verification (requires valid API key)
- **SendGrid** - Email delivery
- **Emergent Google Auth** - OAuth authentication

## Backlog

### P1 - High Priority
- ✅ Proactive Growth Agent Enhancements (Completed)
- ✅ Advanced Analytics Dashboard (Completed)
- ✅ Automated Scheduling (Completed)
- ✅ Instagram Integration (Completed)
- ✅ Mobile Responsiveness (Completed)

### P2 - Medium Priority
- Companies House API key configuration for production
- Real-time notifications for scheduled actions
- Campaign A/B testing features

### P3 - Low Priority
- Additional social platform integrations (TikTok, YouTube)
- Advanced AI content personalization
- Team collaboration features

## Notes
- **Google Sign-in Flow**: The intermediate landing page at `auth.emergentagent.com` is by design (Emergent-managed auth)
- **MongoDB Only**: The application does NOT use PostgreSQL/SQLAlchemy
- **JWT Compatibility**: Supports both 'user_id' and 'sub' claims
- **Growth Agent**: All recommendations require human approval before execution
- **Scheduling**: Posts can be scheduled at optimal times for maximum engagement

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial tests (25 passed)
- `/app/test_reports/iteration_2.json` - New features tests (36 passed)
