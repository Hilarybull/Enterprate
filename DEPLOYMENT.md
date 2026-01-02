# EnterprateAI - Deployment Guide

Complete deployment instructions for EnterprateAI on various platforms.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Railway Deployment](#railway-deployment) ⭐ Recommended
3. [Vercel + Railway](#vercel-frontend--railway-backend)
4. [Netlify + Railway](#netlify-frontend--railway-backend)
5. [Docker Compose](#docker-compose-self-hosted)
6. [VPS Deployment](#vps-deployment)
7. [Post-Deployment Steps](#post-deployment-steps)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] **MongoDB Database** (MongoDB Atlas recommended - free tier available)
- [ ] **Emergent LLM Key** (for AI features)
- [ ] **Domain name** (optional but recommended)

### Optional but Recommended:
- [ ] Companies House API key (UK company verification)
- [ ] SendGrid API key (email delivery)
- [ ] Google OAuth credentials (social login)

See **[CONFIGURATION.md](./CONFIGURATION.md)** for how to get all API keys.

---

## Railway Deployment

**Railway** provides the easiest full-stack deployment with automatic SSL.

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub

### Step 2: Deploy MongoDB
1. Click "New Project" → "Provision MongoDB"
2. Or use MongoDB Atlas (recommended for production)

### Step 3: Deploy Backend

1. Click "New" → "GitHub Repo"
2. Select `enterprate/enterprateai`
3. Configure:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Add Environment Variables (Settings → Variables):
```
MONGO_URL=your-mongodb-url
DB_NAME=enterprateai
JWT_SECRET=your-32-char-secret-here
FRONTEND_URL=https://your-frontend.up.railway.app
CORS_ORIGINS=https://your-frontend.up.railway.app
EMERGENT_LLM_KEY=sk-emergent-your-key
COMPANIES_HOUSE_API_KEY=your-ch-key (optional)
SENDGRID_API_KEY=your-sg-key (optional)
SENDGRID_FROM_EMAIL=noreply@yourdomain.com (optional)
```

5. Click Deploy
6. Note your backend URL (e.g., `https://enterprateai-backend.up.railway.app`)

### Step 4: Deploy Frontend

1. In same project, click "New" → "GitHub Repo"
2. Select same repo
3. Configure:
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build`
   - **Start Command**: `npx serve -s build -l $PORT`

4. Add Environment Variables:
```
REACT_APP_BACKEND_URL=https://your-backend.up.railway.app
```

5. Deploy and note your frontend URL

### Step 5: Update CORS
Go back to backend variables and update:
```
FRONTEND_URL=https://your-actual-frontend-url.up.railway.app
CORS_ORIGINS=https://your-actual-frontend-url.up.railway.app
```

### Step 6: Add Custom Domain (Optional)
1. Settings → Domains
2. Add your domain
3. Update DNS records as shown

---

## Vercel (Frontend) + Railway (Backend)

Best for separate scaling and Vercel's edge network for frontend.

### Step 1: Deploy Backend on Railway
Follow Steps 1-3 from [Railway Deployment](#railway-deployment)

### Step 2: Deploy Frontend on Vercel

1. Go to https://vercel.com
2. Click "Import Project" → Select from GitHub
3. Select `enterprate/enterprateai`
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build`
   - **Output Directory**: `build`

5. Add Environment Variable:
```
REACT_APP_BACKEND_URL=https://your-railway-backend.up.railway.app
```

6. Deploy

### Step 3: Update Backend CORS
Update Railway backend variables with Vercel URL:
```
FRONTEND_URL=https://your-app.vercel.app
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

### Step 4: Custom Domain on Vercel
1. Settings → Domains → Add
2. Follow DNS configuration

---

## Netlify (Frontend) + Railway (Backend)

Alternative to Vercel with similar features.

### Step 1: Deploy Backend on Railway
Follow Steps 1-3 from [Railway Deployment](#railway-deployment)

### Step 2: Deploy Frontend on Netlify

1. Go to https://netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect GitHub and select repo
4. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `yarn build`
   - **Publish directory**: `frontend/build`

5. Add Environment Variable (Site settings → Build & deploy → Environment):
```
REACT_APP_BACKEND_URL=https://your-railway-backend.up.railway.app
```

6. Trigger deploy

### Step 3: Add Redirects for React Router
Create `frontend/public/_redirects`:
```
/*    /index.html   200
```

### Step 4: Update Backend CORS
Update Railway backend with Netlify URL.

---

## Docker Compose (Self-Hosted)

For full control on your own server.

### Prerequisites
- Docker & Docker Compose installed
- Server with 2GB+ RAM

### Step 1: Clone Repository
```bash
git clone https://github.com/enterprate/enterprateai.git
cd enterprateai
```

### Step 2: Create Environment File
```bash
cp .env.docker.example .env
```

Edit `.env`:
```env
MONGO_USERNAME=admin
MONGO_PASSWORD=secure-password-here
DB_NAME=enterprateai
JWT_SECRET=your-32-char-secret-here
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
EMERGENT_LLM_KEY=sk-emergent-your-key
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Step 3: Start Services
```bash
docker-compose up -d
```

### Step 4: Verify
```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f

# Test API
curl http://localhost:8001/api/health
```

### Step 5: Production with Nginx + SSL

Add nginx service to `docker-compose.yml` and configure SSL.
See the full docker-compose.yml in the repo.

---

## VPS Deployment

For DigitalOcean, Linode, AWS EC2, etc.

### Step 1: Provision Server
- Ubuntu 22.04 LTS
- Minimum 2GB RAM, 1 vCPU
- Open ports: 22, 80, 443

### Step 2: Initial Setup
```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3.11 python3.11-venv nodejs npm nginx certbot python3-certbot-nginx

# Install yarn
npm install -g yarn
```

### Step 3: Clone Repository
```bash
cd /opt
git clone https://github.com/enterprate/enterprateai.git
cd enterprateai
```

### Step 4: Setup Backend
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
nano .env  # Edit with your values
```

### Step 5: Create Systemd Service
```bash
cat > /etc/systemd/system/enterprateai-backend.service << 'EOF'
[Unit]
Description=EnterprateAI Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/enterprateai/backend
Environment="PATH=/opt/enterprateai/backend/venv/bin"
EnvironmentFile=/opt/enterprateai/backend/.env
ExecStart=/opt/enterprateai/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable enterprateai-backend
systemctl start enterprateai-backend
```

### Step 6: Build Frontend
```bash
cd /opt/enterprateai/frontend
cp .env.example .env
nano .env  # Set REACT_APP_BACKEND_URL=https://api.yourdomain.com

yarn install
yarn build
```

### Step 7: Configure Nginx
```bash
cat > /etc/nginx/sites-available/enterprateai << 'EOF'
# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    root /opt/enterprateai/frontend/build;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

ln -s /etc/nginx/sites-available/enterprateai /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Step 8: SSL Certificate
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Post-Deployment Steps

### 1. Test All Endpoints
```bash
# Health check
curl https://your-backend-url/api/health

# Test registration
curl -X POST https://your-backend-url/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!","name":"Test User"}'
```

### 2. Create First User
Register through the UI or API.

### 3. Configure Monitoring
- **Uptime**: UptimeRobot (free)
- **Errors**: Sentry (free tier)
- **Logs**: Papertrail, Logtail

### 4. Setup Backups
For MongoDB Atlas: Enable automated backups.

For self-hosted:
```bash
# Daily backup cron
0 2 * * * mongodump --uri="$MONGO_URL" --out=/backups/$(date +\%Y\%m\%d)
```

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
journalctl -u enterprateai-backend -f
# or
docker-compose logs backend
```

### CORS Errors
- Ensure `CORS_ORIGINS` exactly matches frontend URL
- No trailing slash
- Include protocol (https://)

### Database Connection Failed
- Check `MONGO_URL` format
- Verify IP whitelist (MongoDB Atlas)
- Test with MongoDB Compass first

### AI Features Not Working
- Verify `EMERGENT_LLM_KEY`
- Check backend logs for errors

### Frontend Can't Reach Backend
- Check `REACT_APP_BACKEND_URL`
- Verify backend is running
- Check nginx/proxy configuration

### 502 Bad Gateway
- Backend crashed - check logs
- Port mismatch in nginx config
- Memory issues - increase server RAM

---

## Environment Variables Reference

### Backend (Required)
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection | `mongodb+srv://...` |
| `DB_NAME` | Database name | `enterprateai` |
| `JWT_SECRET` | Auth secret (32+ chars) | `abc123...` |
| `FRONTEND_URL` | Frontend URL | `https://app.domain.com` |
| `CORS_ORIGINS` | Allowed origins | `https://app.domain.com` |
| `EMERGENT_LLM_KEY` | AI key | `sk-emergent-...` |

### Backend (Optional)
| Variable | Description |
|----------|-------------|
| `COMPANIES_HOUSE_API_KEY` | UK company data |
| `SENDGRID_API_KEY` | Email delivery |
| `SENDGRID_FROM_EMAIL` | Sender email |
| `GOOGLE_CLIENT_ID` | OAuth |
| `GOOGLE_CLIENT_SECRET` | OAuth |

### Frontend
| Variable | Description |
|----------|-------------|
| `REACT_APP_BACKEND_URL` | Backend API URL |

---

## Need Help?

- Check [CONFIGURATION.md](./CONFIGURATION.md) for API key setup
- Check [README.md](./README.md) for API reference
- Open an issue on GitHub
- Email: support@enterprate.com
