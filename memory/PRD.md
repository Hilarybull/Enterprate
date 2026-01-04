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
- **A/B Testing** for campaigns with statistical significance analysis ✅ COMPLETE
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
- **AIDA Framework Implementation**
- **Gemini 2.0 Flash Integration** for AI content generation
- **6 Color Schemes**: Modern, Professional, Creative, Minimal, Warm, Nature
- **15 Languages Supported**: EN, ES, FR, DE, IT, PT, NL, PL, RU, ZH, JA, KO, AR, HI, TR
- **Lead Capture Forms**: Automatically integrated into generated sites
- **Multi-Platform Deployment**: Netlify ✅, Vercel ✅, Railway ✅
- **Refinement System**: Iterate on designs with AI-powered feedback
- **Download Source Code**: Export HTML for self-hosting

### 7. Quick Templates ✅ EXPANDED TO 15
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
- **Education / Online Courses** ✅ NEW - Expert instructors, certifications
- **Legal / Law Firm** ✅ NEW - Multiple practice areas, consultations
- **Events / Wedding Planner** ✅ NEW - Full-service planning, coordination
- **Digital Agency** ✅ NEW - Web design, digital marketing, branding
- **Nonprofit / Charity** ✅ NEW - Donations, volunteer opportunities

### 8. Website Analytics Dashboard ✅ NEW
- **Overview Dashboard**: Total websites, page views, visitors, conversions
- **Per-Website Analytics**: Detailed metrics for each landing page
- **Daily Trend Charts**: Visual page view trends over time
- **Device Breakdown**: Desktop, mobile, tablet distribution
- **Top Referrers**: Traffic source analysis
- **Country Distribution**: Geographic visitor data
- **Recent Leads**: Latest captured leads from forms
- **Real-time Visitors**: Active visitor count (last 5 minutes)
- **Conversion Rate Tracking**: Form submissions / visitors
- **Period Filtering**: 7, 30, 90, 365 day views

### 9. Team Collaboration ✅ COMPLETE
- **5 Role-based Access Levels**:
  - Owner (level 0) - Full access
  - Admin (level 1) - Manage team + content
  - Editor (level 2) - Manage content
  - Viewer (level 3) - View only
  - Guest (level 4) - Limited view
- **Team Member Management**: List, invite, update roles, remove
- **Email Invitations**: Send invites with personal messages
- **Pending Invites Tracking**: View and manage outstanding invitations
- **Activity Feed**: Track all team actions
- **Permission System**: Granular permissions per role

### 10. A/B Testing ✅ COMPLETE
- **Test Types**: Campaign, Landing Page, Email, Social Post, CTA
- **Variant Management**: Create unlimited variants with A/B/C/D support
- **Traffic Split**: Configurable distribution (50/50 default)
- **Goal Metrics**: Conversion rate, Click rate, Engagement, Revenue
- **Statistical Significance**: Automated analysis at 95% confidence
- **Full Lifecycle**: Draft → Running → Paused → Completed
- **Analysis Dashboard**: Visual comparison of variants
- **Winner Selection**: Automatic or manual winner determination

### 11. Campaign Automation ✅ COMPLETE
- **13 Trigger Types**:
  - Lead: created, status_changed, score_threshold
  - Invoice: paid, overdue
  - Campaign: started, ended
  - Website: lead_captured
  - A/B Test: winner
  - Time: scheduled
  - Marketing: new_follower, mention
- **12 Action Types**:
  - Communication: send_email, send_notification
  - Lead: update_status, add_tag
  - Campaign: schedule_post, start, pause
  - Optimization: apply_ab_winner, increase/decrease_budget
  - Integration: webhook, create_task
- **Condition Operators**: equals, not_equals, contains, gt, lt, gte, lte
- **Rule Priority**: Order execution by priority number
- **Execution Logging**: Track all automation runs with results
- **Toggle On/Off**: Enable/disable rules without deletion

## Architecture

### Tech Stack
- **Frontend:** React, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (via motor async driver)
- **AI:** OpenAI GPT-4o, Gemini 2.0 Flash
- **Auth:** JWT + Emergent-managed Google OAuth
- **Email:** SendGrid
- **Deployment:** Netlify, Vercel, Railway

### Frontend Pages (New)
- `/team` - Team Collaboration
- `/ab-testing` - A/B Testing
- `/automation` - Campaign Automation
- `/website-analytics` - Website Analytics Dashboard

### Key Routes
- `/app/backend/app/routes/team.py` - Team collaboration
- `/app/backend/app/routes/ab_testing.py` - A/B testing
- `/app/backend/app/routes/automation.py` - Campaign automation
- `/app/backend/app/routes/website_analytics.py` - Analytics tracking
- `/app/backend/app/routes/ai_websites.py` - AI website builder

## API Endpoints

### Team Collaboration
- `GET /api/team/roles` - Get available roles (public)
- `GET /api/team/members` - List team members
- `POST /api/team/invite` - Invite team member
- `PATCH /api/team/members/{id}/role` - Update member role
- `DELETE /api/team/members/{id}` - Remove member
- `GET /api/team/invites/pending` - Pending invitations
- `GET /api/team/activity` - Activity feed

### A/B Testing
- `GET /api/ab-tests` - List tests
- `POST /api/ab-tests` - Create test
- `POST /api/ab-tests/{id}/start` - Start test
- `POST /api/ab-tests/{id}/pause` - Pause test
- `POST /api/ab-tests/{id}/resume` - Resume test
- `GET /api/ab-tests/{id}/analyze` - Get analysis
- `POST /api/ab-tests/{id}/complete` - Complete test

### Campaign Automation
- `GET /api/automation/triggers` - Available triggers
- `GET /api/automation/actions` - Available actions
- `GET /api/automation/operators` - Condition operators
- `GET /api/automation/rules` - List rules
- `POST /api/automation/rules` - Create rule
- `PATCH /api/automation/rules/{id}` - Update rule
- `DELETE /api/automation/rules/{id}` - Delete rule
- `GET /api/automation/logs` - Execution logs

### Website Analytics
- `GET /api/website-analytics/overview` - All websites overview
- `GET /api/website-analytics/website/{id}` - Single website details
- `GET /api/website-analytics/website/{id}/realtime` - Real-time visitors
- `POST /api/website-analytics/track/pageview` - Track page view (public)
- `POST /api/website-analytics/track/conversion` - Track conversion (public)

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial tests (25 passed)
- `/app/test_reports/iteration_2.json` - Phase 2 tests (36 passed)
- `/app/test_reports/iteration_3.json` - Phase 3 tests (45 passed)
- `/app/test_reports/iteration_4.json` - AI Website Builder (32 passed)
- `/app/test_reports/iteration_5.json` - Quick Templates + Fixes (23 passed)
- `/app/test_reports/iteration_6.json` - Enterprise Features (39 passed)

**Total: 200 tests, 100% pass rate**

## Environment Variables

### Required
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `EMERGENT_LLM_KEY` - Universal key for AI services
- `SENDGRID_API_KEY` - Email delivery

### Deployment Keys (Configured)
- `COMPANIES_HOUSE_API_KEY` - UK company verification ✅
- `GEMINI_API_KEY` - Gemini AI for website generation ✅
- `NETLIFY_API_KEY` - Netlify deployment ✅
- `VERCEL_API_KEY` - Vercel deployment ✅
- `RAILWAY_API_KEY` - Railway deployment ✅

## Backlog

### Completed ✅
- ✅ AI Website Builder with AIDA Framework
- ✅ Multi-language website generation (15 languages)
- ✅ Lead capture forms
- ✅ Netlify/Vercel/Railway deployment
- ✅ Quick Templates (expanded to 15)
- ✅ Team Collaboration with roles
- ✅ A/B Testing with analysis
- ✅ Campaign Automation with triggers/actions
- ✅ Website Analytics dashboard
- ✅ Companies House API integration
- ✅ Fixed Netlify deployment (text/html)
- ✅ **WebSocket Real-Time Notifications** - Live WebSocket connection with status indicator
- ✅ **Custom Domain Support** - Generic DNS verification flow for any provider
- ✅ **Notification Center** - Real-time notification popover in header

### Future Enhancements (P2/P3)
- More template categories
- Advanced team permission granularity
- Multi-variant testing (A/B/C/D/n)
- Lead integration with Growth/CRM module (partially implemented)

## Database Collections

### website_analytics
```javascript
{
  id: String (UUID),
  websiteId: String,
  workspace_id: String,
  visitorId: String,
  eventType: String (page_view|conversion),
  pagePath: String,
  referrer: String,
  deviceType: String,
  country: String,
  timestamp: ISODate
}
```

### automation_rules
```javascript
{
  id: String (UUID),
  workspace_id: String,
  name: String,
  description: String,
  trigger: Object,
  conditions: Array,
  actions: Array,
  isActive: Boolean,
  priority: Number,
  executionCount: Number,
  lastExecuted: ISODate,
  createdAt: ISODate
}
```

## Verified Deployments
- https://innovatetech-ai.netlify.app - SaaS template (text/html ✅)
- https://techflow-solutions.netlify.app - Tech startup

## Notes
- **Google Sign-in**: Intermediate page at `auth.emergentagent.com` is by design
- **MongoDB Only**: Application does NOT use PostgreSQL/SQLAlchemy
- **All APIs Working**: Team, A/B Testing, Automation, Analytics, WebSocket, Custom Domains verified
- **All Frontend UIs**: Team, A/B Testing, Automation, Analytics, Custom Domains pages complete
- **Real-Time Notifications**: WebSocket connection established on login, shows "Live" status

## New Features (Iteration 7)

### 12. WebSocket Real-Time Notifications ✅
- **Connection Management**: Auto-connect on login, reconnect on disconnect
- **Notification Categories**: lead, website, ab_test, automation, team, scheduling
- **Toast Notifications**: Automatic toast display based on notification category
- **Status Indicator**: "Live" status in header when WebSocket connected

### 13. Custom Domain Management ✅
- **Generic DNS Verification**: Works with any DNS provider
- **CNAME/A Record Support**: Provides instructions for both record types
- **Verification Flow**: Check DNS propagation with single click
- **SSL Status Tracking**: Automatic SSL provisioning after verification
- **Per-Website Domains**: Each deployed website can have custom domains

### 14. Notification Center UI ✅
- **Header Integration**: Bell icon in enterprise header
- **Connection Status**: Shows "Live" or "Offline" indicator
- **Notification List**: Scrollable list of recent notifications
- **Category Icons**: Visual icons for different notification types
- **Mark as Read**: Individual or bulk mark as read
- **Clear All**: Remove all notifications

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial tests (25 passed)
- `/app/test_reports/iteration_2.json` - Phase 2 tests (36 passed)
- `/app/test_reports/iteration_3.json` - Phase 3 tests (45 passed)
- `/app/test_reports/iteration_4.json` - AI Website Builder (32 passed)
- `/app/test_reports/iteration_5.json` - Quick Templates + Fixes (23 passed)
- `/app/test_reports/iteration_6.json` - Enterprise Features (39 passed)
- `/app/test_reports/iteration_7.json` - WebSocket & Custom Domains (27 passed)

**Total: 227 tests, 100% pass rate**
