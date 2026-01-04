# EnterprateAI - Product Requirements Document

## Overview
EnterprateAI is a comprehensive AI Operating System for Business that helps entrepreneurs start, run, and grow their businesses. The platform provides tools for business registration, finance & compliance, growth/marketing, operations, AI assistant, and advanced AI-powered website building.

## Core Features

### 1. Business Registration
- Multi-step wizard for UK company registration
- Support for 13+ business entity types
- **Dynamic fee table** with fees from official UK Government sources
- Companies House integration for name availability checks ✅ WORKING
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

### 6. AI Website Builder ✅ COMPLETE
- **AIDA Framework Implementation**:
  - **A**ttention: High-impact hero section with result-focused headlines
  - **I**nterest: Feature blocks with emotional benefits
  - **D**esire: Social proof, testimonials, trust badges
  - **A**ction: Strategic CTA placements
- **Gemini 2.0 Flash Integration** for AI content generation
- **6 Color Schemes**: Modern, Professional, Creative, Minimal, Warm, Nature
- **15 Languages Supported**: EN, ES, FR, DE, IT, PT, NL, PL, RU, ZH, JA, KO, AR, HI, TR
- **Lead Capture Forms**: Automatically integrated into generated sites
- **Multi-Platform Deployment**: Netlify ✅, Vercel ✅, Railway ✅
- **Refinement System**: Iterate on designs with AI-powered feedback
- **Download Source Code**: Export HTML for self-hosting

### 7. Quick Templates ✅ NEW
- **10 Industry-Specific Templates**:
  - **SaaS / Tech Startup** - Cloud-based solutions, AI analytics
  - **Restaurant / Cafe** - Farm-to-table, reservations
  - **Portfolio / Freelancer** - Showcase work, client testimonials
  - **Salon / Spa** - Beauty services, online booking
  - **Beauty / Cosmetics** - Product showcase, cruelty-free
  - **Online Store / E-commerce** - Product catalog, secure checkout
  - **Consulting Services** - Professional services, expertise
  - **Fitness / Gym** - Membership, class schedules
  - **Real Estate** - Property listings, virtual tours
  - **Healthcare / Medical** - Appointments, services
- Each template includes:
  - Optimized business description
  - Recommended color scheme
  - Industry-specific features
  - Custom CTA text
  - Hero image suggestion

### 8. Real-time Notifications
- Scheduled action execution alerts
- Campaign milestones
- A/B test winner announcements
- Website deployment notifications
- Team activity notifications
- Growth agent alerts

### 9. A/B Testing
- **Test Types**: Campaign, Landing Page, Email, Social Post, CTA
- **Traffic Split**: Configurable distribution across variants
- **Goal Metrics**: Conversion rate, Click rate, Engagement, Revenue
- **Statistical Significance**: Automated winner determination
- **Full Lifecycle**: Draft → Running → Paused → Completed

### 10. Team Collaboration
- **Role-based Access Control**:
  - Owner (full access)
  - Admin (manage team + content)
  - Editor (manage content)
  - Viewer (view only)
  - Guest (limited view)
- **Team Invitations**: Email-based invite system
- **Activity Feed**: Track all team actions
- **Comments System**: Discuss campaigns, leads, tasks

## Architecture

### Tech Stack
- **Frontend:** React, Tailwind CSS, shadcn/ui (mobile-responsive)
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (via motor async driver)
- **AI:** OpenAI GPT-4o, Gemini 2.0 Flash
- **Auth:** JWT + Emergent-managed Google OAuth
- **Email:** SendGrid
- **Deployment:** Netlify, Vercel, Railway (for generated websites)

### Key Services
- `/app/backend/app/services/ai_website_builder_service.py` - AIDA website builder with templates
- `/app/backend/app/services/notification_service.py` - Real-time notifications
- `/app/backend/app/services/ab_testing_service.py` - A/B testing with statistics
- `/app/backend/app/services/team_collaboration_service.py` - Team management

### Key Routes
- `/app/backend/app/routes/ai_websites.py` - Website builder endpoints (prefix: `/api/ai-websites`)
- `/app/backend/app/routes/company_profile.py` - Companies House integration

## API Endpoints

### AI Website Builder
- `POST /api/ai-websites/generate` - Generate website from description
- `GET /api/ai-websites` - List all websites
- `GET /api/ai-websites/{id}` - Get website details
- `POST /api/ai-websites/{id}/refine` - Refine with feedback
- `POST /api/ai-websites/{id}/deploy` - Deploy to Netlify/Vercel/Railway
- `GET /api/ai-websites/{id}/download` - Download HTML source
- `GET /api/ai-websites/color-schemes/list` - Get color schemes
- `GET /api/ai-websites/languages/list` - Get supported languages
- `GET /api/ai-websites/platforms/list` - Get deployment platforms
- `GET /api/ai-websites/templates/list` - Get 10 quick templates ✅ NEW
- `GET /api/ai-websites/templates/{id}` - Get specific template ✅ NEW
- `POST /api/ai-websites/lead` - Handle lead form submission

### Companies House
- `POST /api/company-profile/check-name` - Check name availability ✅ WORKING

## What's Been Implemented

### January 2026 - Phase 5 (Current Session)
- ✅ **Quick Templates Feature**: 10 industry-specific templates
- ✅ **Netlify Deployment Fix**: Now serves text/html correctly
- ✅ **Companies House API**: Verified working with real API key
- ✅ **23 new tests**: All passing (100% pass rate)

### January 2026 - Phase 4
- ✅ **AI Website Builder Complete**: Backend service + Frontend UI
- ✅ **Multi-language support**: 15 languages
- ✅ **Lead capture forms**: Auto-integrated
- ✅ **32 tests passing**

### Earlier Phases
- Real-time Notifications
- A/B Testing
- Team Collaboration
- Proactive Growth Agent
- Advanced Analytics Dashboard

## Environment Variables

### Required
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `EMERGENT_LLM_KEY` - Universal key for AI services
- `SENDGRID_API_KEY` - Email delivery

### Deployment Keys (Configured)
- `COMPANIES_HOUSE_API_KEY` - UK company verification ✅ WORKING
- `GEMINI_API_KEY` - Gemini AI for website generation
- `NETLIFY_API_KEY` - Netlify deployment ✅ WORKING
- `VERCEL_API_KEY` - Vercel deployment ✅ WORKING
- `RAILWAY_API_KEY` - Railway deployment

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial tests (25 passed)
- `/app/test_reports/iteration_2.json` - Phase 2 tests (36 passed)
- `/app/test_reports/iteration_3.json` - Phase 3 tests (45 passed)
- `/app/test_reports/iteration_4.json` - AI Website Builder (32 passed)
- `/app/test_reports/iteration_5.json` - Quick Templates + Fixes (23 passed)

**Total: 161 tests, 100% pass rate**

## Backlog

### Completed ✅
- ✅ Proactive Growth Agent
- ✅ Advanced Analytics Dashboard
- ✅ Automated Scheduling
- ✅ Instagram, TikTok, YouTube Integration
- ✅ Real-time Notifications
- ✅ A/B Testing
- ✅ Team Collaboration
- ✅ AI Website Builder with AIDA Framework
- ✅ Multi-language website generation
- ✅ Lead capture forms
- ✅ Netlify/Vercel/Railway deployment
- ✅ Quick Templates (10 industries)
- ✅ Companies House API integration

### Upcoming (P1)
- Frontend UIs for Team Collaboration
- Frontend UIs for A/B Testing
- Frontend UIs for Campaign Automation
- WebSocket real-time notifications

### Future Enhancements (P2/P3)
- Advanced campaign automation rules
- Enhanced team permissions granularity
- Custom domain support for deployed sites
- More template categories

## Verified Deployments
- https://innovatetech-ai.netlify.app - SaaS template (text/html ✅)
- https://techflow-solutions.netlify.app - Tech startup

## Notes
- **Google Sign-in**: Intermediate page at `auth.emergentagent.com` is by design
- **MongoDB Only**: Application does NOT use PostgreSQL/SQLAlchemy
- **Deployment Keys**: All platform keys (Netlify, Vercel, Railway, Gemini, Companies House) are configured and working
- **Template Selection**: Templates tab loads first by default in Website Builder
