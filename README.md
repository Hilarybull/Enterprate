# Enterprate OS

**An AI Operating System for Businesses**

Enterprate OS is a production-ready SaaS platform that provides businesses with AI-powered tools for operations, growth, and strategic planning. Built with modern technologies and designed for scalability.

---

## Overview

Enterprate OS is a comprehensive business management platform featuring:

- **Multi-tenant workspaces** - Each workspace represents one business with multiple team members
- **Three AI-powered domains:**
  - **Genesis AI** - Transform ideas into validated business concepts
  - **Navigator AI** - Manage operations, invoicing, and financial workflows
  - **Growth AI** - CRM, lead management, and customer acquisition
- **Website Builder** - Drag-and-drop website creation tool
- **Intelligence Graph** - Event logging and business intelligence system

---

## Technology Stack

### Backend
- **FastAPI** (Python) - Modern, fast web framework
- **MongoDB** - NoSQL database for flexible data modeling
- **JWT Authentication** - Secure token-based authentication
- **Emergent LLM Integration** - AI capabilities via universal API key

### Frontend
- **React 19** - Modern UI library
- **React Router v7** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible component library
- **Axios** - HTTP client for API requests
- **Sonner** - Toast notifications

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ with Yarn
- MongoDB running locally or connection string

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd enterprate-os
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   yarn install
   cp .env.example .env
   # Edit .env with your backend URL
   ```

### Running Locally

1. **Start MongoDB:**
   ```bash
   # Make sure MongoDB is running on mongodb://localhost:27017
   ```

2. **Start Backend:**
   ```bash
   cd backend
   uvicorn server:app --reload --host 0.0.0.0 --port 8001
   ```

3. **Start Frontend:**
   ```bash
   cd frontend
   yarn start
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001/api
   - API Documentation: http://localhost:8001/docs

---

## Environment Variables

### Backend (.env)

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=enterprate_os
CORS_ORIGINS=*
JWT_SECRET=your-secret-key-change-in-production
EMERGENT_LLM_KEY=sk-emergent-xxxxx
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env)

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## Project Structure

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Backend environment variables
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.js       # Main layout with sidebar
│   │   │   └── ui/             # shadcn/ui components
│   │   ├── context/
│   │   │   ├── AuthContext.js  # Authentication state
│   │   │   └── WorkspaceContext.js  # Workspace management
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── Dashboard.js
│   │   │   ├── Genesis.js
│   │   │   ├── Navigator.js
│   │   │   ├── Growth.js
│   │   │   ├── WebsiteBuilder.js
│   │   │   ├── WebsiteEditor.js
│   │   │   └── Settings.js
│   │   ├── App.js
│   │   └── App.css
│   ├── package.json
│   └── .env
│
└── README.md
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/me` - Get current user
- `GET /api/auth/google` - Google OAuth (placeholder)

### Workspaces
- `GET /api/workspaces` - List user's workspaces
- `POST /api/workspaces` - Create workspace
- `GET /api/workspaces/:id` - Get workspace details
- `PATCH /api/workspaces/:id` - Update workspace

### Projects
- `GET /api/workspaces/:id/projects` - List projects
- `POST /api/workspaces/:id/projects` - Create project

### Genesis AI
- `POST /api/genesis/idea-score` - Score business idea
- `POST /api/genesis/business-blueprint` - Generate business blueprint

### Navigator (Invoicing)
- `GET /api/navigator/invoices` - List invoices
- `POST /api/navigator/invoices` - Create invoice
- `PATCH /api/navigator/invoices/:id` - Update invoice

### Growth (CRM)
- `GET /api/growth/leads` - List leads
- `POST /api/growth/leads` - Create lead
- `PATCH /api/growth/leads/:id` - Update lead

### Website Builder
- `GET /api/websites` - List websites
- `POST /api/websites` - Create website
- `GET /api/websites/:id` - Get website
- `GET /api/websites/:id/pages` - List pages
- `POST /api/websites/:id/pages` - Create page
- `PATCH /api/websites/:id/pages/:pageId` - Update page

### Intelligence Graph
- `GET /api/intel/events` - List events
- `POST /api/intel/events` - Log event

---

## Database Schema

### Collections

**users**
- id, email, passwordHash, googleId, name, createdAt

**workspaces**
- id, name, slug, country, industry, stage, ownerId, createdAt

**workspace_memberships**
- id, userId, workspaceId, role, createdAt

**business_profiles**
- id, workspaceId, businessName, status, brandTone, primaryGoal, targetAudience, createdAt

**projects**
- id, workspaceId, type, name, status, config, createdAt

**websites**
- id, workspaceId, projectId, name, domain, published, config, createdAt

**website_pages**
- id, websiteId, path, title, content, createdAt

**invoices**
- id, workspaceId, customerName, amount, currency, status, dueDate, items, createdAt

**leads**
- id, workspaceId, name, email, phone, source, status, notes, createdAt

**intelligence_events**
- id, workspaceId, userId, type, payload, occurredAt

---

## Features

### ✅ Implemented

- Multi-tenant workspace system
- User authentication (email/password + Google OAuth placeholder)
- Workspace management and switching
- Dashboard with overview cards and activity feed
- Genesis AI idea validation wizard (mocked responses)
- Navigator invoicing system with CRUD operations
- Growth CRM with lead management
- Website builder with drag-and-drop editor
- Page management for websites
- Intelligence event logging
- Settings page for workspace configuration
- Responsive design with mobile sidebar
- Modern UI with shadcn/ui components

### 🚧 Future Enhancements

- **AI Integration**: Connect Genesis, Navigator, and Growth AI to actual LLM APIs
- **Google OAuth**: Complete Google authentication implementation
- **Advanced Website Builder**: More components, templates, and publishing
- **Analytics Dashboard**: Business intelligence and reporting
- **Team Management**: Invite members, role-based access control
- **Integrations**: Connect to third-party services
- **Export/Import**: Data portability features
- **Real-time Collaboration**: WebSocket support for live updates

---

## Development Notes

### AI Placeholder Responses

Currently, Genesis AI, Navigator AI, and Growth AI return mocked responses. The infrastructure is ready for integration with:
- OpenAI GPT-4o via Emergent LLM key
- Custom AI models
- Third-party AI services

### Authentication

- JWT tokens stored in localStorage
- Tokens expire after 7 days
- Password hashing using bcrypt
- Workspace context passed via `X-Workspace-Id` header

### Website Builder

The website builder supports:
- Multiple pages per website
- Component types: Heading, Text, Image, Section
- Drag-and-drop interface (visual indicators)
- Save/publish workflow

---

## Testing

### Manual Testing Flow

1. **Register**: Create a new account
2. **Create Workspace**: Set up your first workspace
3. **Dashboard**: View overview and statistics
4. **Genesis AI**: Test idea validation
5. **Navigator**: Create and manage invoices
6. **Growth**: Add and track leads
7. **Website Builder**: Create a website with pages
8. **Settings**: Update workspace information

### API Testing

```bash
# Register
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"password123"}'

# Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Create Workspace (use token from login)
curl -X POST http://localhost:8001/api/workspaces \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Company"}'
```

---

## Deployment

### Backend

The backend can be deployed to:
- Railway
- Render
- AWS/GCP/Azure
- Any platform supporting Python/FastAPI

**Requirements:**
- Python 3.11+
- MongoDB connection
- Environment variables configured

### Frontend

The frontend can be deployed to:
- Vercel (recommended)
- Netlify
- AWS Amplify
- Any static hosting service

**Build command:**
```bash
yarn build
```

**Environment:**
Set `REACT_APP_BACKEND_URL` to your backend URL

---

## Contributing

This is a v1 MVP scaffold. Contributions are welcome!

### Areas for Contribution

1. **AI Integration**: Implement actual LLM calls
2. **OAuth Completion**: Finish Google OAuth flow
3. **Testing**: Add unit and integration tests
4. **Documentation**: API documentation, tutorials
5. **UI/UX**: Improvements and new features
6. **Performance**: Optimization and caching

---

## License

MIT License - feel free to use this project as a foundation for your own SaaS application.

---

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Icons from [Lucide](https://lucide.dev/)
- Developed on [Emergent](https://emergent.sh/)

---

**Version:** 1.0.0 (MVP Scaffold)  
**Status:** Production-ready foundation, AI features mocked  
**Last Updated:** January 2025
