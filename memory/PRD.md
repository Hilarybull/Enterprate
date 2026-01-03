# EnterprateAI - Product Requirements Document

## Overview
EnterprateAI is a comprehensive AI Operating System for Business that helps entrepreneurs start, run, and grow their businesses. The platform provides tools for business registration, finance & compliance, growth/marketing, operations, AI assistant, and advanced AI-powered website building.

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
- Tax estimation calculator with auto-fill
- Compliance checklist management
- Invoice creation and management

### 3. Growth & Marketing
- Lead management and CRM
- Marketing campaign management
- **A/B Testing** for campaigns with statistical significance analysis
- Social media content generation
- **All social platforms**: Twitter, LinkedIn, Facebook, Instagram, TikTok, YouTube
- **Proactive Growth Agent** with automated scheduling

### 4. Advanced Analytics Dashboard
- Dashboard overview with KPIs
- Revenue trends analysis
- Lead funnel visualization
- Business report generation (weekly/monthly/quarterly)

### 5. Automated Scheduling Service
- **Platform-specific optimal posting times** for all 6 platforms
- Engagement predictions and recommendations
- Automated action execution
- TikTok & YouTube integration with peak time analysis

### 6. AI Website Builder (NEW)
- **AIDA Framework Implementation**:
  - **A**ttention: High-impact hero section with result-focused headlines
  - **I**nterest: Feature blocks with emotional benefits
  - **D**esire: Social proof, testimonials, trust badges
  - **A**ction: Strategic CTA placements
- **Gemini 2.0 Flash Integration** for AI content generation
- **6 Color Schemes**: Modern, Professional, Creative, Minimal, Warm, Nature
- **Refinement System**: Iterate on designs with feedback
- **Netlify Deployment**: One-click deployment to live URL
- **Download Source Code**: Export HTML for self-hosting

### 7. Real-time Notifications (NEW)
- Scheduled action execution alerts
- Campaign milestones
- A/B test winner announcements
- Website deployment notifications
- Team activity notifications
- Growth agent alerts

### 8. A/B Testing (NEW)
- **Test Types**: Campaign, Landing Page, Email, Social Post, CTA
- **Traffic Split**: Configurable distribution across variants
- **Goal Metrics**: Conversion rate, Click rate, Engagement, Revenue
- **Statistical Significance**: Automated winner determination
- **Full Lifecycle**: Draft → Running → Paused → Completed

### 9. Team Collaboration (NEW)
- **Role-based Access Control**:
  - Owner (full access)
  - Admin (manage team + content)
  - Editor (manage content)
  - Viewer (view only)
  - Guest (limited view)
- **Team Invitations**: Email-based invite system
- **Activity Feed**: Track all team actions
- **Comments System**: Discuss campaigns, leads, tasks
- **Real-time Collaboration**: See team updates instantly

### 10. Business Operations
- Task management
- Agentic Email Sender with human approval
- AI Document Drafting

### 11. AI Assistant (EnterprateAI)
- Multi-mode AI assistant (Advisory, Data-Backed, Presentation)
- Context-locked to business domains

## Architecture

### Tech Stack
- **Frontend:** React, Tailwind CSS, shadcn/ui (mobile-responsive)
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (via motor async driver)
- **AI:** OpenAI GPT-4o, Gemini 2.0 Flash (via Emergent LLM Key)
- **Auth:** JWT + Emergent-managed Google OAuth
- **Email:** SendGrid
- **Deployment:** Netlify (for generated websites)

### New Services Added (Phase 3)
- `/app/backend/app/services/notification_service.py` - Real-time notifications
- `/app/backend/app/services/ab_testing_service.py` - A/B testing with statistics
- `/app/backend/app/services/team_collaboration_service.py` - Team management
- `/app/backend/app/services/ai_website_builder_service.py` - AIDA website builder

### New Routes Added (Phase 3)
- `/app/backend/app/routes/notifications.py` - Notification endpoints
- `/app/backend/app/routes/ab_testing.py` - A/B testing endpoints
- `/app/backend/app/routes/team.py` - Team collaboration endpoints
- `/app/backend/app/routes/ai_websites.py` - Website builder endpoints

## API Endpoints

### Notifications (NEW)
- `GET /api/notifications` - Get user notifications
- `GET /api/notifications/unread-count` - Get unread count
- `POST /api/notifications/{id}/read` - Mark as read
- `POST /api/notifications/read-all` - Mark all as read

### A/B Testing (NEW)
- `POST /api/ab-tests` - Create A/B test
- `GET /api/ab-tests` - List tests
- `POST /api/ab-tests/{id}/start` - Start test
- `POST /api/ab-tests/{id}/pause` - Pause test
- `GET /api/ab-tests/{id}/analyze` - Analyze results
- `POST /api/ab-tests/{id}/complete` - Complete test

### Team Collaboration (NEW)
- `GET /api/team/members` - Get team members
- `POST /api/team/invite` - Invite member
- `PATCH /api/team/members/{id}/role` - Update role
- `GET /api/team/activity` - Activity feed
- `POST /api/team/comments` - Add comment
- `GET /api/team/roles` - Available roles

### AI Website Builder (NEW)
- `POST /api/websites/generate` - Generate website from description
- `GET /api/websites` - List websites
- `POST /api/websites/{id}/refine` - Refine with feedback
- `POST /api/websites/{id}/deploy` - Deploy to Netlify
- `GET /api/websites/{id}/download` - Download source code
- `GET /api/websites/color-schemes/list` - Get color schemes

### Scheduling (Updated)
- `GET /api/scheduling/optimal-times?platform=tiktok` - TikTok optimal times
- `GET /api/scheduling/optimal-times?platform=youtube` - YouTube optimal times

## What's Been Implemented

### January 2026 - Phase 3 (Current)
- **Real-time Notifications**: Event-based notification system for all user actions
- **A/B Testing**: Complete testing framework with statistical analysis
- **Team Collaboration**: Full team management with roles, invites, comments
- **AI Website Builder**: AIDA framework website generation with Gemini AI
- **TikTok & YouTube Integration**: Optimal posting times for video platforms

### January 2026 - Phase 2
- Proactive Growth Agent with additional triggers
- Advanced Analytics Dashboard
- Instagram Integration
- Automated Scheduling Service

### December 2025 - Phase 1
- Business Operations Module
- Finance & Compliance enhancements
- Enhanced AI Assistant
- Initial documentation

## Integrations

### Active Integrations
- **OpenAI GPT-4o** - AI features (via Emergent LLM Key)
- **Gemini 2.0 Flash** - Website content generation (via Emergent LLM Key)
- **Companies House API** - Company verification
- **SendGrid** - Email delivery
- **Emergent Google Auth** - OAuth authentication

### Simulated Integrations (Configure Keys for Production)
- **Netlify API** - Website deployment (NETLIFY_API_KEY required)

## Environment Variables

### Required
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `EMERGENT_LLM_KEY` - Universal key for AI services
- `SENDGRID_API_KEY` - Email delivery

### Optional
- `COMPANIES_HOUSE_API_KEY` - UK company verification
- `NETLIFY_API_KEY` - Website deployment
- `GEMINI_API_KEY` - Direct Gemini access (falls back to EMERGENT_LLM_KEY)

## Backlog

### Completed ✅
- ✅ Proactive Growth Agent
- ✅ Advanced Analytics Dashboard
- ✅ Automated Scheduling
- ✅ Instagram, TikTok, YouTube Integration
- ✅ Mobile Responsiveness
- ✅ Real-time Notifications
- ✅ A/B Testing
- ✅ Team Collaboration
- ✅ AI Website Builder

### Future Enhancements (P2/P3)
- Real-time websocket notifications
- Advanced campaign automation rules
- Multi-language website generation
- More deployment targets (Vercel, Railway)
- Enhanced team permissions granularity

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial tests (25 passed)
- `/app/test_reports/iteration_2.json` - Phase 2 tests (36 passed)
- `/app/test_reports/iteration_3.json` - Phase 3 tests (45 passed)

**Total: 106 tests, 100% pass rate**

## Notes
- **Google Sign-in**: Intermediate page at `auth.emergentagent.com` is by design
- **MongoDB Only**: Application does NOT use PostgreSQL/SQLAlchemy
- **JWT Compatibility**: Supports both 'user_id' and 'sub' claims
- **Growth Agent**: Requires human approval before executing actions
- **Website Builder**: Uses Gemini AI with template fallback
- **Netlify Deployment**: Returns simulated URL if API key not configured
