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
  <a href="#api-documentation">API Docs</a> •
  <a href="#license">License</a>
</p>

---

## Overview

EnterprateAI is a comprehensive business management platform that helps entrepreneurs and businesses manage every aspect of their operations through AI-powered automation. From company formation to growth marketing, EnterprateAI provides intelligent assistance at every step.

## Features

### 🚀 Genesis AI (Business Formation)
- **Idea Validation** - AI-powered business idea analysis
- **Company Registration** - UK Companies House integration
- **Business Planning** - Automated business plan generation
- **Entity Selection** - Smart guidance on company types

### 🧭 Navigator AI (Operations & Finance)
- **Invoice Management** - Create and track invoices
- **Expense Tracking** - Receipt scanning with AI
- **Tax Estimation** - UK tax calculator
- **Compliance Checklist** - Stay compliant with regulations
- **Task Management** - Organize business operations

### 📈 Growth AI (Marketing & Sales)
- **AI Post Generator** - Social media content creation
- **Lead Management** - Track and nurture leads
- **Campaign Management** - Marketing campaign tracking
- **Analytics Dashboard** - Performance insights

### 🤖 AI Assistant
- **Three Operating Modes:**
  - Advisory Mode - General business guidance
  - Data-Backed Mode - Verified Companies House data
  - Presentation Mode - Structured stakeholder reports
- **Context-Aware** - Maps responses to business domains
- **Non-Hallucinating** - Only provides verified information

### 📄 AI Document Drafting
- Business Documents (Quotes, Contracts, Proposals)
- Compliance Documents (Privacy Policy, T&Cs, Cookie Notice)
- HR Policies (Employee Handbook, Remote Work Policy)
- CRM Templates (Welcome Emails, Follow-ups)

### 🔐 Authentication
- Email/Password authentication
- Google OAuth (Emergent-managed)
- JWT-based session management

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.11+) |
| Database | MongoDB |
| AI | OpenAI GPT-4o (via Emergent LLM Key) |
| Email | SendGrid |
| Company Data | Companies House API |

## Quick Start

### Prerequisites

- Node.js 18+ and Yarn
- Python 3.11+
- MongoDB instance
- Required API keys (see Environment Variables)

### Local Development

```bash
# Clone the repository
git clone https://github.com/enterprate/enterprateai.git
cd enterprateai

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend setup (new terminal)
cd frontend
yarn install
cp .env.example .env
# Edit .env with your backend URL
yarn start
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy Options

#### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

#### Vercel (Frontend) + Railway (Backend)
1. Deploy backend to Railway with MongoDB addon
2. Deploy frontend to Vercel with `REACT_APP_BACKEND_URL`

#### Docker
```bash
docker-compose up -d
```

## Environment Variables

### Backend (Required)

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGO_URL` | MongoDB connection string | ✅ |
| `DB_NAME` | Database name | ✅ |
| `JWT_SECRET` | JWT signing secret | ✅ |
| `EMERGENT_LLM_KEY` | AI integration key | ✅ |
| `FRONTEND_URL` | Frontend URL for CORS | ✅ |
| `CORS_ORIGINS` | Allowed CORS origins | ✅ |

### Backend (Optional)

| Variable | Description |
|----------|-------------|
| `COMPANIES_HOUSE_API_KEY` | UK Companies House API |
| `SENDGRID_API_KEY` | Email delivery |
| `SENDGRID_FROM_EMAIL` | Sender email address |
| `GOOGLE_CLIENT_ID` | Google OAuth |
| `GOOGLE_CLIENT_SECRET` | Google OAuth |

### Frontend

| Variable | Description | Required |
|----------|-------------|----------|
| `REACT_APP_BACKEND_URL` | Backend API URL | ✅ |

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Key API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/register` | User registration |
| `POST /api/auth/login` | User authentication |
| `GET /api/company-profile` | Get company profile |
| `POST /api/chat` | AI Assistant |
| `POST /api/finance/invoices` | Create invoice |
| `POST /api/marketing/social-posts/generate` | Generate social post |
| `POST /api/blueprint/generate-document` | Generate document |

## Project Structure

```
enterprateai/
├── backend/
│   ├── app/
│   │   ├── core/           # Security, database config
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── schemas/        # Pydantic models
│   │   └── main.py         # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context providers
│   │   └── App.js          # Main app component
│   └── package.json
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software owned by Enterprate Ltd.

## Support

- **Documentation**: [docs.enterprate.com](https://docs.enterprate.com)
- **Email**: support@enterprate.com
- **Issues**: [GitHub Issues](https://github.com/enterprate/enterprateai/issues)

---

<p align="center">Built with ❤️ by Enterprate</p>
