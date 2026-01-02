# EnterprateAI

<p align="center">
  <img src="https://customer-assets.emergentagent.com/job_saas-dashboard-20/artifacts/aems110l_Enterprate%20Logo.png" alt="EnterprateAI" width="200"/>
</p>

<p align="center">
  <strong>The Complete AI-Powered Business Operating System</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#deployment">Deployment</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#configuration">Configuration</a>
</p>

---

## 🎯 Overview

EnterprateAI is a comprehensive AI-powered business management platform designed for UK businesses. It provides intelligent automation for company formation, operations management, financial tracking, compliance, and growth marketing.

## ✨ Features

### 🚀 Genesis AI (Business Formation)
- **Idea Validation** - AI-powered business idea analysis and market research
- **Company Registration** - UK Companies House integration for company verification
- **Business Planning** - Automated business plan and blueprint generation
- **Entity Selection** - Smart guidance on UK company types (Ltd, LLP, PLC, etc.)

### 🧭 Navigator AI (Operations & Finance)
- **Invoice Management** - Create, track, and manage invoices
- **Expense Tracking** - AI receipt scanning with automatic categorization
- **Tax Estimation** - UK tax calculator with auto-population from financial data
- **Compliance Checklist** - HMRC, Companies House, and GDPR compliance tracking
- **Task Management** - Business operations task tracking

### 📈 Growth AI (Marketing & Sales)
- **AI Content Generator** - Social media posts for LinkedIn, Twitter, Facebook
- **Lead Management** - Track and nurture business leads
- **Campaign Management** - Marketing campaign tracking and analytics
- **Performance Dashboard** - Business growth analytics

### 🤖 AI Assistant (Multi-Mode Intelligence)
- **Advisory Mode** - General business guidance and best practices
- **Data-Backed Mode** - Verified Companies House data lookups
- **Presentation Mode** - Structured reports for stakeholders
- **Context-Locked** - Only provides business-relevant responses

### 📄 AI Document Drafting
- Business Documents (Quotes, Contracts, Proposals, Invoices)
- Compliance Documents (Privacy Policy, T&Cs, Cookie Notice, Refund Policy)
- HR Policies (Employee Handbook, Remote Work, Leave, Code of Conduct)
- CRM Templates (Welcome Emails, Follow-ups, Thank You Notes)

### 🎨 Branding & Website Tools
- Branding Wizard with AI logo concepts
- Website Content Generator for all pages
- SEO content generation

### 🔐 Authentication
- Email/Password with JWT
- Google OAuth integration
- Workspace-based multi-tenancy

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Tailwind CSS, shadcn/ui, Lucide Icons |
| **Backend** | FastAPI (Python 3.11+), Pydantic |
| **Database** | MongoDB (Atlas recommended) |
| **AI** | OpenAI GPT-4o via Emergent LLM |
| **Email** | SendGrid |
| **Company Data** | UK Companies House API |

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ & Yarn
- Python 3.11+
- MongoDB database
- Required API keys (see [Configuration](#configuration))

### Local Development

```bash
# Clone the repository
git clone https://github.com/enterprate/enterprateai.git
cd enterprateai

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend Setup (new terminal)
cd frontend
yarn install
cp .env.example .env
# Edit .env with your backend URL
yarn start
```

---

## 📦 Deployment

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for complete deployment instructions.

### Quick Deploy Options

| Platform | Best For | Guide |
|----------|----------|-------|
| **Railway** | Full-stack, easy setup | [Deploy →](#railway-deployment) |
| **Vercel + Railway** | Separate scaling | [Deploy →](#vercel--railway) |
| **Docker Compose** | Self-hosted | [Deploy →](#docker-deployment) |
| **VPS** | Full control | [Deploy →](#vps-deployment) |

---

## 🔌 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/google/init` | Init Google OAuth |

### Workspaces
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workspaces` | List workspaces |
| POST | `/api/workspaces` | Create workspace |
| GET | `/api/workspaces/{id}` | Get workspace |

### Company Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/company-profile` | Get profile |
| POST | `/api/company-profile` | Update profile |
| POST | `/api/company-profile/check-name` | Check name availability |
| POST | `/api/company-profile/confirm-registration` | Confirm with Companies House |
| POST | `/api/company-profile/generate-branding` | AI branding |
| POST | `/api/company-profile/generate-website-content` | AI website content |

### Finance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/navigator/invoices` | Invoice management |
| GET/POST | `/api/finance/expenses` | Expense tracking |
| POST | `/api/finance/scan-receipt` | AI receipt scanning |
| POST | `/api/finance/estimate-tax` | Tax calculation |
| GET/POST | `/api/finance/compliance` | Compliance checklist |

### Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/operations/tasks` | Task management |
| POST | `/api/operations/generate-email` | AI email drafting |
| GET/POST | `/api/operations/email-templates` | Email templates |

### Marketing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/growth/leads` | Lead management |
| GET/POST | `/api/marketing/campaigns` | Campaigns |
| POST | `/api/marketing/social-posts/generate` | AI post generation |

### AI Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message to AI |
| GET | `/api/chat/modes` | Get operating modes |
| GET | `/api/chat/history/{session}` | Chat history |

### Business Blueprint
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/blueprint` | Blueprint management |
| POST | `/api/blueprint/generate-document` | AI document generation |

---

## ⚙️ Configuration

See **[CONFIGURATION.md](./CONFIGURATION.md)** for detailed setup of all API keys and integrations.

### Required Environment Variables

```env
# Database (Required)
MONGO_URL=mongodb+srv://...
DB_NAME=enterprateai

# Security (Required)
JWT_SECRET=your-32-char-secret
FRONTEND_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com

# AI (Required)
EMERGENT_LLM_KEY=sk-emergent-...
```

### Optional Integrations
- Companies House API (UK company verification)
- SendGrid (Email delivery)
- Google OAuth (Social login)
- Social Media APIs (Posting automation)

---

## 📁 Project Structure

```
enterprateai/
├── backend/
│   ├── app/
│   │   ├── core/           # Security, database
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── schemas/        # Pydantic models
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── context/        # State management
│   │   └── App.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── DEPLOYMENT.md
├── CONFIGURATION.md
└── README.md
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
yarn test
```

---

## 🔄 Development Continuation

This project can be continued:
1. **On Emergent Platform** - Continue in the same workspace
2. **In VS Code/Cursor** - Clone from GitHub, install dependencies
3. **By Any Developer** - Follow setup guide in this README

---

## 📄 License

Proprietary - © Enterprate Ltd

---

## 📞 Support

- **Email**: support@enterprate.com
- **Issues**: [GitHub Issues](https://github.com/enterprate/enterprateai/issues)

---

<p align="center">Built with ❤️ by Enterprate</p>
