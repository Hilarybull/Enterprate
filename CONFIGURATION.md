# EnterprateAI - Configuration Guide

This document provides comprehensive instructions for configuring all API keys, integrations, and environment variables required to run EnterprateAI.

---

## Table of Contents

1. [Environment Files Overview](#environment-files-overview)
2. [Required Configuration](#required-configuration)
3. [Optional Integrations](#optional-integrations)
4. [Database Setup](#database-setup)
5. [API Keys - How to Get Them](#api-keys---how-to-get-them)
6. [Security Recommendations](#security-recommendations)

---

## Environment Files Overview

EnterprateAI uses two environment files:

| File | Purpose |
|------|--------|
| `backend/.env` | All backend configuration |
| `frontend/.env` | Frontend configuration (just backend URL) |

**⚠️ IMPORTANT:** Never commit `.env` files to Git. Use `.env.example` as templates.

---

## Required Configuration

These are the **minimum required** settings to run EnterprateAI:

### Backend (`backend/.env`)

```env
# ============================
# DATABASE (Required)
# ============================
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=enterprateai

# ============================
# SECURITY (Required)
# ============================
# Generate with: openssl rand -hex 32
JWT_SECRET=your-super-secure-jwt-secret-minimum-32-characters

# Frontend URL for CORS and redirects
FRONTEND_URL=https://your-frontend-domain.com

# Allowed CORS origins (comma-separated, no trailing slash)
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# ============================
# AI INTEGRATION (Required)
# ============================
# Emergent LLM Key for all AI features
EMERGENT_LLM_KEY=sk-emergent-your-key-here
```

### Frontend (`frontend/.env`)

```env
# Backend API URL (no trailing slash)
REACT_APP_BACKEND_URL=https://your-backend-domain.com
```

---

## Optional Integrations

### 1. Companies House API (UK Company Verification)

**What it enables:**
- Company name availability checking
- Company registration verification
- Director and PSC lookups
- Filing status verification
- Data-backed mode in AI Assistant

**How to get:**
1. Go to https://developer.company-information.service.gov.uk/
2. Create an account
3. Register your application
4. Create a "Live" API key

```env
COMPANIES_HOUSE_API_KEY=your-api-key-here
```

**Cost:** Free for up to 600 requests/5 minutes

---

### 2. SendGrid (Email Delivery)

**What it enables:**
- Sending AI-generated emails
- Email templates
- Agentic email with human-in-the-loop

**How to get:**
1. Sign up at https://sendgrid.com/
2. Go to Settings → API Keys
3. Create API Key with "Full Access"
4. Verify your sender identity/domain

```env
SENDGRID_API_KEY=SG.your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@your-verified-domain.com
```

**Cost:** Free tier: 100 emails/day

---

### 3. Google OAuth (Social Login)

**What it enables:**
- "Sign in with Google" button
- Faster user registration

**How to get:**
1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable Google+ API and Google Identity API
4. Go to Credentials → Create Credentials → OAuth client ID
5. Application type: Web application
6. Add authorized redirect URIs:
   - `https://your-backend.com/api/auth/google/callback`

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**Cost:** Free

---

### 4. Social Media APIs (Posting Automation)

#### Twitter/X
```env
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```
**Get from:** https://developer.twitter.com/

#### Facebook/Instagram
```env
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_PAGE_ACCESS_TOKEN=your-page-token
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-business-id
```
**Get from:** https://developers.facebook.com/

#### LinkedIn
```env
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_ACCESS_TOKEN=your-access-token
```
**Get from:** https://www.linkedin.com/developers/

#### YouTube
```env
YOUTUBE_API_KEY=your-api-key
YOUTUBE_CLIENT_ID=your-client-id
YOUTUBE_CLIENT_SECRET=your-client-secret
YOUTUBE_REFRESH_TOKEN=your-refresh-token
```
**Get from:** https://console.cloud.google.com/

---

## Database Setup

### Option 1: MongoDB Atlas (Recommended for Production)

1. **Create Account:** https://www.mongodb.com/cloud/atlas
2. **Create Cluster:** Free tier (M0) is sufficient to start
3. **Create Database User:**
   - Database Access → Add New Database User
   - Authentication: Password
   - Note down username and password
4. **Configure Network Access:**
   - Network Access → Add IP Address
   - For development: "Allow Access from Anywhere" (0.0.0.0/0)
   - For production: Add specific server IPs
5. **Get Connection String:**
   - Clusters → Connect → Connect your application
   - Copy connection string
   - Replace `<password>` with your database user password

```env
MONGO_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=enterprateai
```

### Option 2: Supabase (PostgreSQL Alternative)

**Note:** EnterprateAI is designed for MongoDB. Using Supabase requires code modifications.

1. Create project at https://supabase.com/
2. Get connection string from Project Settings → Database
3. You'll need to modify backend code to use PostgreSQL/SQLAlchemy

### Option 3: Self-Hosted MongoDB

```bash
# Using Docker
docker run -d --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=yourpassword \
  -v mongodb_data:/data/db \
  mongo:6
```

```env
MONGO_URL=mongodb://admin:yourpassword@localhost:27017/
DB_NAME=enterprateai
```

---

## API Keys - How to Get Them

### Quick Reference Table

| Integration | URL | Free Tier | Required For |
|------------|-----|-----------|-------------|
| MongoDB Atlas | mongodb.com/cloud/atlas | 512MB storage | Database |
| Emergent LLM | Emergent Platform | Included | AI features |
| Companies House | developer.company-information.service.gov.uk | 600 req/5min | UK company data |
| SendGrid | sendgrid.com | 100 emails/day | Email sending |
| Google Cloud | console.cloud.google.com | Free | OAuth, YouTube |
| Twitter/X | developer.twitter.com | Limited | Social posting |
| Facebook | developers.facebook.com | Free | Social posting |
| LinkedIn | linkedin.com/developers | Free | Social posting |

---

## Security Recommendations

### JWT Secret
- **Minimum 32 characters**
- Generate securely:
  ```bash
  openssl rand -hex 32
  ```

### Environment Variables
- ✅ Use `.env` files locally
- ✅ Use platform secrets in production (Railway, Vercel)
- ❌ Never commit secrets to Git
- ❌ Never log secrets

### CORS Configuration
- ✅ Specify exact origins in production
- ❌ Don't use `*` wildcard in production

### Database
- ✅ Use strong passwords
- ✅ Restrict IP access in production
- ✅ Enable MongoDB authentication

---

## Troubleshooting

### "AI features not working"
- Check `EMERGENT_LLM_KEY` is set correctly
- Verify key hasn't expired

### "Companies House lookup failing"
- Check `COMPANIES_HOUSE_API_KEY` is valid
- Verify you're not exceeding rate limits (600/5min)

### "Emails not sending"
- Verify SendGrid API key
- Check sender email is verified in SendGrid
- Check SendGrid activity log for errors

### "Google OAuth not working"
- Verify redirect URI matches exactly
- Check client ID and secret
- Ensure APIs are enabled in Google Cloud Console

### "MongoDB connection failed"
- Check connection string format
- Verify IP is whitelisted (Atlas)
- Check username/password
- Test with MongoDB Compass first

---

## Example Complete Configuration

### `backend/.env` (Production)

```env
# Database
MONGO_URL=mongodb+srv://enterprate:SecurePass123@cluster0.abc123.mongodb.net/
DB_NAME=enterprateai_prod

# Security
JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4
FRONTEND_URL=https://app.enterprate.com
CORS_ORIGINS=https://app.enterprate.com,https://www.enterprate.com

# AI (Required)
EMERGENT_LLM_KEY=sk-emergent-bB2Fb4816BeA3B8C22

# UK Company Data
COMPANIES_HOUSE_API_KEY=abc123def456ghi789

# Email
SENDGRID_API_KEY=SG.xxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@enterprate.com

# Google OAuth
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxx
```

### `frontend/.env` (Production)

```env
REACT_APP_BACKEND_URL=https://api.enterprate.com
```

---

For deployment instructions, see **[DEPLOYMENT.md](./DEPLOYMENT.md)**
