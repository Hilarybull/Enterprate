# Enterprate OS - Deployment Guide

This guide covers multiple deployment options for Enterprate OS.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Deployment Options](#deployment-options)
   - [Docker Compose](#docker-compose-recommended)
   - [Railway](#railway)
   - [Vercel + Railway](#vercel-frontend--railway-backend)
   - [AWS/GCP/Azure](#cloud-providers)
   - [VPS/Dedicated Server](#vps-deployment)
4. [Post-Deployment](#post-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Domain name (optional but recommended)
- SSL certificate (provided by most platforms)
- MongoDB database (Atlas recommended for production)
- API Keys:
  - Emergent LLM Key (for AI features)
  - Companies House API Key (for UK company data)
  - SendGrid API Key (for email)
  - Google OAuth credentials (for social login)

---

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# ============================================
# REQUIRED - Core Configuration
# ============================================
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=enterprate_prod
JWT_SECRET=your-super-secure-jwt-secret-min-32-chars
FRONTEND_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# ============================================
# REQUIRED - AI Integration
# ============================================
EMERGENT_LLM_KEY=sk-emergent-your-key-here

# ============================================
# OPTIONAL - Companies House (UK Company Data)
# ============================================
# Get from: https://developer.company-information.service.gov.uk/
COMPANIES_HOUSE_API_KEY=your-companies-house-api-key

# ============================================
# OPTIONAL - Email (SendGrid)
# ============================================
# Get from: https://sendgrid.com/
SENDGRID_API_KEY=SG.your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@your-domain.com

# ============================================
# OPTIONAL - Google OAuth
# ============================================
# Get from: https://console.cloud.google.com/
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# ============================================
# OPTIONAL - Social Media Integrations
# ============================================
# Twitter/X API
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=
TWITTER_BEARER_TOKEN=

# Facebook/Instagram
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
FACEBOOK_PAGE_ACCESS_TOKEN=
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=

# LinkedIn
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=

# YouTube
YOUTUBE_API_KEY=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# Backend API URL (no trailing slash)
REACT_APP_BACKEND_URL=https://api.your-domain.com

# Optional: Disable health checks in production
ENABLE_HEALTH_CHECK=false
```

---

## Deployment Options

### Docker Compose (Recommended)

The easiest way to deploy the full stack.

#### 1. Create docker-compose.yml

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6
    restart: always
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    networks:
      - enterprate-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/
      - DB_NAME=enterprate
      - JWT_SECRET=${JWT_SECRET}
      - FRONTEND_URL=${FRONTEND_URL}
      - CORS_ORIGINS=${CORS_ORIGINS}
      - EMERGENT_LLM_KEY=${EMERGENT_LLM_KEY}
      - COMPANIES_HOUSE_API_KEY=${COMPANIES_HOUSE_API_KEY}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - SENDGRID_FROM_EMAIL=${SENDGRID_FROM_EMAIL}
    depends_on:
      - mongodb
    networks:
      - enterprate-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL}
    restart: always
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - enterprate-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - enterprate-network

volumes:
  mongodb_data:

networks:
  enterprate-network:
    driver: bridge
```

#### 2. Create Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### 3. Create Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app

ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 4. Deploy

```bash
# Create .env file with your variables
cp .env.example .env
# Edit .env with your production values

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

### Railway

Railway provides easy deployment with automatic SSL.

#### Backend Deployment

1. Create a new project on [Railway](https://railway.app)
2. Add a MongoDB database service
3. Connect your GitHub repository
4. Set the root directory to `backend`
5. Add environment variables (see above)
6. Railway will auto-detect Python and deploy

#### Frontend Deployment

1. Add another service in the same project
2. Set root directory to `frontend`
3. Set build command: `yarn build`
4. Set start command: `yarn start`
5. Add `REACT_APP_BACKEND_URL` pointing to your backend URL

---

### Vercel (Frontend) + Railway (Backend)

Best for separate scaling of frontend and backend.

#### Backend on Railway

1. Deploy backend to Railway (see above)
2. Note the generated URL (e.g., `https://enterprate-backend.up.railway.app`)

#### Frontend on Vercel

1. Import project from GitHub on [Vercel](https://vercel.com)
2. Set root directory to `frontend`
3. Add environment variable:
   ```
   REACT_APP_BACKEND_URL=https://enterprate-backend.up.railway.app
   ```
4. Deploy

---

### Cloud Providers (AWS/GCP/Azure)

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 enterprate-backend

# Create environment
eb create production

# Set environment variables
eb setenv MONGO_URL=... JWT_SECRET=... EMERGENT_LLM_KEY=...

# Deploy
eb deploy
```

#### Google Cloud Run

```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/enterprate-backend

# Deploy
gcloud run deploy enterprate-backend \
  --image gcr.io/PROJECT_ID/enterprate-backend \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars MONGO_URL=...,JWT_SECRET=...
```

---

### VPS Deployment

For deployment on a VPS (DigitalOcean, Linode, etc.):

```bash
# SSH into your server
ssh user@your-server-ip

# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv nodejs npm nginx certbot

# Clone repository
git clone https://github.com/enterprate/enterprateai.git
cd enterprateai

# Setup backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values

# Setup systemd service for backend
sudo cat > /etc/systemd/system/enterprate-backend.service << EOF
[Unit]
Description=Enterprate Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/user/enterprateai/backend
EnvironmentFile=/home/user/enterprateai/backend/.env
ExecStart=/home/user/enterprateai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable enterprate-backend
sudo systemctl start enterprate-backend

# Setup frontend
cd ../frontend
npm install -g yarn
yarn install
yarn build

# Configure Nginx
sudo cat > /etc/nginx/sites-available/enterprate << EOF
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Frontend
    location / {
        root /home/user/enterprateai/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/enterprate /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL Certificate
sudo certbot --nginx -d your-domain.com
```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check backend health
curl https://your-domain.com/api/health

# Check frontend loads
curl https://your-domain.com
```

### 2. Create Admin User

Register through the UI or use the API:

```bash
curl -X POST https://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "SecurePassword123!", "name": "Admin"}'
```

### 3. Configure Monitoring

Recommended monitoring tools:
- **Uptime**: UptimeRobot, Pingdom
- **Logs**: Papertrail, Logtail
- **Errors**: Sentry
- **Metrics**: Datadog, New Relic

### 4. Setup Backups

For MongoDB Atlas, enable automated backups. For self-hosted:

```bash
# Daily backup script
mongodump --uri="$MONGO_URL" --out=/backups/$(date +%Y%m%d)
```

---

## Troubleshooting

### Common Issues

#### CORS Errors

Ensure `CORS_ORIGINS` includes your frontend URL (with protocol, no trailing slash):
```env
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

#### MongoDB Connection Failed

- Check MongoDB URL format
- Ensure IP whitelist includes server IP (for Atlas)
- Verify credentials

#### AI Features Not Working

- Verify `EMERGENT_LLM_KEY` is set correctly
- Check backend logs for errors

#### Frontend Can't Reach Backend

- Verify `REACT_APP_BACKEND_URL` is correct
- Check if backend is running: `curl https://api.your-domain.com/api/health`
- Check Nginx/proxy configuration

### Logs

```bash
# Docker
docker-compose logs -f backend
docker-compose logs -f frontend

# Systemd
journalctl -u enterprate-backend -f

# Railway
# View in Railway dashboard
```

---

## Security Checklist

- [ ] Use strong, unique `JWT_SECRET`
- [ ] Enable HTTPS only
- [ ] Set strict CORS origins
- [ ] Use environment variables (never commit secrets)
- [ ] Enable MongoDB authentication
- [ ] Regular security updates
- [ ] Rate limiting on API
- [ ] Input validation
- [ ] Regular backups

---

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Search [GitHub Issues](https://github.com/enterprate/enterprateai/issues)
3. Contact support@enterprate.com
