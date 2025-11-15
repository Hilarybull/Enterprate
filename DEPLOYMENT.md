# Deployment Guide

This guide provides instructions for deploying Enterprate OS to various hosting platforms.

---

## Prerequisites

Before deploying, ensure you have:

1. A MongoDB database (MongoDB Atlas recommended for production)
2. Environment variables configured
3. A domain name (optional but recommended)
4. Accounts on your chosen hosting platforms

---

## Backend Deployment

### Option 1: Railway (Recommended)

**Railway** is perfect for FastAPI applications.

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Create a new project:**
   ```bash
   cd backend
   railway init
   ```

4. **Set environment variables:**
   ```bash
   railway variables set MONGO_URL="your-mongodb-url"
   railway variables set DB_NAME="enterprate_os"
   railway variables set JWT_SECRET="your-secret-key"
   railway variables set CORS_ORIGINS="https://your-frontend-domain.com"
   railway variables set FRONTEND_URL="https://your-frontend-domain.com"
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

6. **Get your backend URL:**
   ```bash
   railway domain
   ```

### Option 2: Render

1. Go to [Render](https://render.com/) and create a new Web Service
2. Connect your GitHub repository
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`
4. Add environment variables in Render dashboard
5. Deploy!

### Option 3: AWS EC2 / DigitalOcean

1. **Setup server:**
   ```bash
   ssh user@your-server-ip
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3.11 python3-pip nginx -y
   ```

2. **Clone repository:**
   ```bash
   git clone your-repo-url
   cd enterprate-os/backend
   ```

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Setup environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

5. **Setup systemd service:**
   ```bash
   sudo nano /etc/systemd/system/enterprate-backend.service
   ```

   ```ini
   [Unit]
   Description=Enterprate OS Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/backend
   Environment="PATH=/usr/bin"
   ExecStart=/usr/bin/uvicorn server:app --host 0.0.0.0 --port 8001
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start service:**
   ```bash
   sudo systemctl start enterprate-backend
   sudo systemctl enable enterprate-backend
   ```

7. **Setup Nginx reverse proxy:**
   ```bash
   sudo nano /etc/nginx/sites-available/enterprate
   ```

   ```nginx
   server {
       listen 80;
       server_name api.your-domain.com;

       location / {
           proxy_pass http://localhost:8001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/enterprate /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

8. **Setup SSL with Let's Encrypt:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d api.your-domain.com
   ```

---

## Frontend Deployment

### Option 1: Vercel (Recommended)

**Vercel** is optimized for React applications.

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login:**
   ```bash
   vercel login
   ```

3. **Deploy from frontend directory:**
   ```bash
   cd frontend
   vercel
   ```

4. **Set environment variable:**
   - Go to Vercel dashboard
   - Project Settings → Environment Variables
   - Add: `REACT_APP_BACKEND_URL` = `https://your-backend-url.com`

5. **Redeploy:**
   ```bash
   vercel --prod
   ```

### Option 2: Netlify

1. Go to [Netlify](https://netlify.com/) and create a new site
2. Connect your GitHub repository
3. Configure:
   - **Build Command:** `yarn build`
   - **Publish Directory:** `build`
   - **Base Directory:** `frontend`
4. Add environment variables:
   - `REACT_APP_BACKEND_URL` = `https://your-backend-url.com`
5. Deploy!

### Option 3: AWS S3 + CloudFront

1. **Build the application:**
   ```bash
   cd frontend
   REACT_APP_BACKEND_URL=https://your-backend-url.com yarn build
   ```

2. **Create S3 bucket:**
   ```bash
   aws s3 mb s3://enterprate-os-frontend
   ```

3. **Upload build:**
   ```bash
   aws s3 sync build/ s3://enterprate-os-frontend --delete
   ```

4. **Enable static website hosting:**
   - Go to S3 bucket → Properties → Static website hosting
   - Enable and set index.html as index document

5. **Setup CloudFront distribution:**
   - Create distribution pointing to S3 bucket
   - Configure custom domain and SSL certificate

---

## Database Setup

### MongoDB Atlas (Recommended)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user
4. Whitelist IP addresses (or allow all: 0.0.0.0/0)
5. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/`
6. Use this as your `MONGO_URL` environment variable

### Self-Hosted MongoDB

If you prefer to host MongoDB yourself:

```bash
# Install MongoDB
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Create database and user
mongo
> use enterprate_os
> db.createUser({user: "enterprate", pwd: "your-password", roles: ["readWrite"]})

# Connection string
MONGO_URL=mongodb://enterprate:your-password@localhost:27017/enterprate_os
```

---

## Environment Variables

### Backend

```env
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=enterprate_os
CORS_ORIGINS=https://your-frontend-domain.com
JWT_SECRET=use-a-long-random-string-here
EMERGENT_LLM_KEY=sk-emergent-xxxxx
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-secret
FRONTEND_URL=https://your-frontend-domain.com
```

### Frontend

```env
REACT_APP_BACKEND_URL=https://your-backend-domain.com
```

---

## Post-Deployment Checklist

- [ ] Backend is accessible via HTTPS
- [ ] Frontend is accessible via HTTPS
- [ ] Database connection is working
- [ ] CORS is configured correctly
- [ ] Environment variables are set
- [ ] User registration works
- [ ] User login works
- [ ] Workspace creation works
- [ ] All pages load correctly
- [ ] API endpoints respond correctly
- [ ] Toast notifications appear
- [ ] Mobile responsiveness works

---

## Monitoring & Maintenance

### Recommended Tools

1. **Uptime Monitoring:** UptimeRobot, Pingdom
2. **Error Tracking:** Sentry
3. **Analytics:** Google Analytics, Plausible
4. **Logs:** Papertrail, Logtail
5. **Performance:** Lighthouse, WebPageTest

### Backup Strategy

**MongoDB Backups:**
```bash
# Manual backup
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/enterprate_os" --out=/backups/$(date +%Y%m%d)

# Automated backups with Atlas (recommended)
# Enable automated backups in Atlas dashboard
```

### Updates

```bash
# Backend updates
cd backend
git pull
pip install -r requirements.txt
sudo systemctl restart enterprate-backend

# Frontend updates
cd frontend
git pull
yarn install
yarn build
# Then redeploy to Vercel/Netlify
```

---

## Troubleshooting

### Backend Issues

**"Connection refused" errors:**
- Check if backend is running: `sudo systemctl status enterprate-backend`
- Check logs: `sudo journalctl -u enterprate-backend -n 50`

**"Database connection failed":**
- Verify MONGO_URL is correct
- Check if MongoDB is accessible
- Whitelist server IP in MongoDB Atlas

### Frontend Issues

**"API request failed":**
- Verify REACT_APP_BACKEND_URL is correct
- Check CORS settings on backend
- Inspect browser console for errors

**Build failures:**
- Clear cache: `rm -rf node_modules yarn.lock && yarn install`
- Check Node version: `node -v` (should be 18+)

---

## Scaling Considerations

As your application grows:

1. **Database:** Upgrade MongoDB cluster size
2. **Backend:** Add load balancer and multiple instances
3. **Frontend:** CDN is automatically handled by Vercel/Netlify
4. **Caching:** Implement Redis for session management
5. **Queue:** Add job queue for background tasks (Celery, Bull)

---

## Security Best Practices

- ✅ Use HTTPS everywhere
- ✅ Keep JWT_SECRET secure and random
- ✅ Regularly update dependencies
- ✅ Implement rate limiting on API
- ✅ Use strong passwords for database
- ✅ Enable 2FA for hosting platforms
- ✅ Regular security audits
- ✅ Monitor for suspicious activity

---

## Support

For deployment issues, please check:
- GitHub Issues
- Documentation
- Community forums

---

Good luck with your deployment! 🚀
