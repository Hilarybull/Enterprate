# PostgreSQL Migration Guide - Enterprate OS v1.2

## Overview

Enterprate OS has been migrated from MongoDB to PostgreSQL with SQLAlchemy 2.x ORM and Alembic migrations. This document explains the changes, how to set up the database, and how to run the application.

---

## What Changed

### Database Stack
- **Before (v1.0-1.1):** MongoDB with Motor (async MongoDB driver)
- **After (v1.2):** PostgreSQL 15+ with SQLAlchemy 2.x (async) and asyncpg driver

### Key Improvements
1. ✅ **ACID Transactions** - Full transaction support with rollback
2. ✅ **Referential Integrity** - Foreign key constraints ensure data consistency
3. ✅ **Schema Validation** - Type safety at the database level
4. ✅ **Better Joins** - More efficient relational queries
5. ✅ **Migrations** - Alembic for versioned schema changes
6. ✅ **Enterprise Ready** - PostgreSQL is industry standard for production

---

## Database Schema

### Tables Created (10 + 1 migration table)

1. **users** - User accounts
   - Columns: id (UUID), email, name, password_hash, google_id, created_at, updated_at
   - Indexes: email (unique), google_id (unique)

2. **workspaces** - Multi-tenant workspaces
   - Columns: id (UUID), name, slug, country, industry, stage, owner_id (FK), created_at, updated_at
   - Indexes: slug (unique)
   - Foreign Keys: owner_id → users.id

3. **workspace_memberships** - User-workspace relationships
   - Columns: id (UUID), user_id (FK), workspace_id (FK), role (enum), created_at, updated_at
   - Foreign Keys: user_id → users.id, workspace_id → workspaces.id

4. **business_profiles** - Workspace business information
   - Columns: id (UUID), workspace_id (FK unique), business_name, status (enum), brand_tone, primary_goal, target_audience, created_at, updated_at
   - Foreign Keys: workspace_id → workspaces.id

5. **projects** - Workspace projects
   - Columns: id (UUID), workspace_id (FK), type (enum), name, status (enum), config (JSONB), created_at, updated_at
   - Foreign Keys: workspace_id → workspaces.id

6. **websites** - Website builder sites
   - Columns: id (UUID), workspace_id (FK), project_id (FK nullable), name, domain, published (bool), config (JSONB), created_at, updated_at
   - Foreign Keys: workspace_id → workspaces.id, project_id → projects.id

7. **website_pages** - Website pages
   - Columns: id (UUID), website_id (FK), path, title, content (JSONB), created_at, updated_at
   - Foreign Keys: website_id → websites.id

8. **invoices** - Navigator invoices
   - Columns: id (UUID), workspace_id (FK), customer_name, amount (float), currency, status (enum), due_date, items (JSONB), created_at, updated_at
   - Foreign Keys: workspace_id → workspaces.id

9. **leads** - Growth CRM leads
   - Columns: id (UUID), workspace_id (FK), name, email, phone, source, status (enum), notes (text), created_at, updated_at
   - Foreign Keys: workspace_id → workspaces.id

10. **intelligence_events** - Event tracking
    - Columns: id (UUID), workspace_id (FK), user_id (FK nullable), type, payload (JSONB), occurred_at
    - Indexes: type, occurred_at
    - Foreign Keys: workspace_id → workspaces.id, user_id → users.id

11. **alembic_version** - Migration tracking (auto-created)

---

## Setup Instructions

### 1. Install PostgreSQL

**On Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo service postgresql start
```

**On macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**On Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database and User

```bash
# Connect as postgres user
sudo -u postgres psql

# In psql:
CREATE USER enterprate WITH PASSWORD 'your_secure_password';
CREATE DATABASE enterprate_os OWNER enterprate;
GRANT ALL PRIVILEGES ON DATABASE enterprate_os TO enterprate;
\q
```

### 3. Update Environment Variables

Edit `/app/backend/.env`:

```env
# PostgreSQL Database (Required)
DATABASE_URL=postgresql+asyncpg://enterprate:your_secure_password@localhost:5432/enterprate_os

# Other settings remain the same
CORS_ORIGINS=*
JWT_SECRET=your-secret-key
EMERGENT_LLM_KEY=sk-emergent-xxxxx
# ...
```

**Important Notes:**
- Use `postgresql+asyncpg://` prefix for async SQLAlchemy
- Replace `your_secure_password` with your actual password
- For production, use strong passwords and secure connection strings

### 4. Install Python Dependencies

```bash
cd /app/backend
pip install -r requirements.txt
```

**New dependencies added:**
- `sqlalchemy==2.0.36` - ORM
- `asyncpg==0.30.0` - Async PostgreSQL driver
- `alembic==1.14.0` - Database migrations
- `psycopg2-binary==2.9.10` - PostgreSQL adapter (for migrations)

### 5. Run Alembic Migrations

```bash
cd /app/backend

# Check current migration status
alembic current

# Run all pending migrations
alembic upgrade head

# Verify tables were created
psql -U enterprate -d enterprate_os -c "\dt"
```

**Expected output:**
```
                  List of relations
 Schema |         Name          | Type  |   Owner    
--------+-----------------------+-------+------------
 public | alembic_version       | table | enterprate
 public | business_profiles     | table | enterprate
 public | intelligence_events   | table | enterprate
 public | invoices              | table | enterprate
 public | leads                 | table | enterprate
 public | projects              | table | enterprate
 public | users                 | table | enterprate
 public | website_pages         | table | enterprate
 public | websites              | table | enterprate
 public | workspace_memberships | table | enterprate
 public | workspaces            | table | enterprate
(11 rows)
```

### 6. Run the Application

```bash
cd /app/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Expected startup log:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Connected to PostgreSQL
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

---

## Migration Status

### ✅ Completed

1. **Database Schema**
   - ✅ All 10 tables created with proper types
   - ✅ Foreign key constraints
   - ✅ Indexes for performance
   - ✅ JSONB columns for flexible data (config, payload, content, items)
   - ✅ Enums for status fields (UserRole, BusinessStatus, ProjectType, etc.)
   - ✅ UUID primary keys
   - ✅ Timestamps (created_at, updated_at)

2. **Core Infrastructure**
   - ✅ SQLAlchemy models in `app/models/`
   - ✅ Async engine and session management in `core/database.py`
   - ✅ Updated configuration in `core/config.py`
   - ✅ Alembic setup and initial migration
   - ✅ Updated requirements.txt

3. **Documentation**
   - ✅ Migration guide (this document)
   - ✅ Setup instructions
   - ✅ Schema documentation

### 🚧 In Progress / TODO

1. **Service Layer Migration** 
   - Services need to be updated from Motor/MongoDB to SQLAlchemy
   - Replace `db.collection.find_one()` with SQLAlchemy queries
   - Replace `db.collection.insert_one()` with `session.add()` and `session.commit()`
   - Update all CRUD operations

2. **Testing**
   - Test all API endpoints with PostgreSQL
   - Verify data consistency
   - Performance testing

---

## Alembic Commands Reference

### Common Commands

```bash
# Create a new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current migration version
alembic current

# View migration history
alembic history

# Rollback all migrations (use with caution!)
alembic downgrade base
```

### Creating Manual Migrations

If autogenerate doesn't detect changes:

```bash
alembic revision -m "Add index to user email"
```

Then edit the generated file in `alembic/versions/` to add your changes.

---

## Data Migration from MongoDB

If you have existing data in MongoDB that needs to be migrated:

### Option 1: Export/Import (Recommended for small datasets)

```bash
# 1. Export from MongoDB
mongoexport --db=enterprate_os --collection=users --out=users.json

# 2. Transform JSON to match PostgreSQL schema (custom script needed)

# 3. Import to PostgreSQL using COPY or INSERT statements
```

### Option 2: Write a Migration Script

Create `backend/scripts/migrate_mongo_to_postgres.py`:

```python
# Pseudocode
from motor import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Workspace, etc.

async def migrate_users():
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
    mongo_db = mongo_client["enterprate_os"]
    
    # Connect to PostgreSQL
    async with AsyncSessionLocal() as session:
        # Fetch all users from MongoDB
        users = await mongo_db.users.find({}).to_list(None)
        
        # Insert into PostgreSQL
        for user_data in users:
            user = User(
                id=UUID(user_data["id"]),
                email=user_data["email"],
                # ... map other fields
            )
            session.add(user)
        
        await session.commit()
```

### Option 3: Manual SQL Import

For complex migrations, write SQL scripts that PostgreSQL can execute.

---

## Troubleshooting

### Connection Refused

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Start PostgreSQL if not running
sudo service postgresql start
```

### Authentication Failed

**Error:** `password authentication failed for user "enterprate"`

**Solution:**
```bash
# Reset password
sudo -u postgres psql
ALTER USER enterprate WITH PASSWORD 'new_password';
\q

# Update DATABASE_URL in .env with new password
```

### Permission Denied

**Error:** `permission denied for schema public`

**Solution:**
```bash
sudo -u postgres psql -d enterprate_os
GRANT ALL PRIVILEGES ON DATABASE enterprate_os TO enterprate;
GRANT ALL PRIVILEGES ON SCHEMA public TO enterprate;
\q
```

### Migration Conflicts

**Error:** `Alembic detects conflicts`

**Solution:**
```bash
# Check current state
alembic current

# If stuck, stamp the database with current version
alembic stamp head

# Or rollback and reapply
alembic downgrade -1
alembic upgrade head
```

---

## Performance Considerations

### Indexes

All performance-critical columns have indexes:
- `users.email` (unique index for login)
- `users.google_id` (unique index for OAuth)
- `workspaces.slug` (unique index for URL routing)
- `intelligence_events.type` (for filtering by event type)
- `intelligence_events.occurred_at` (for time-based queries)

### Connection Pooling

For production, configure connection pooling in `core/database.py`:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Number of connections to maintain
    max_overflow=40,  # Allow up to 60 total connections
    pool_pre_ping=True,  # Verify connections before use
)
```

### JSONB Performance

For queries on JSONB columns, add GIN indexes:

```sql
CREATE INDEX idx_projects_config ON projects USING GIN (config);
CREATE INDEX idx_intelligence_events_payload ON intelligence_events USING GIN (payload);
```

---

## Production Deployment

### Environment Variables

```env
# Production Database URL (with connection pooling)
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/enterprate_os?pool_size=20&max_overflow=40

# Enable SSL for production
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/enterprate_os?ssl=require
```

### Database Backup

```bash
# Backup
pg_dump -U enterprate -d enterprate_os -F c -f backup.dump

# Restore
pg_restore -U enterprate -d enterprate_os backup.dump
```

### Monitoring

Monitor PostgreSQL performance:
```sql
# Active connections
SELECT count(*) FROM pg_stat_activity;

# Slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

---

## API Contract Preservation

**All 24 API endpoints remain unchanged:**
- Same request/response shapes
- Same validation rules
- Same business logic
- Same error handling

**Only the data layer changed:**
- MongoDB → PostgreSQL
- Motor → SQLAlchemy
- Document queries → ORM queries

---

## Next Steps

1. **Update Service Layer** - Migrate all services from MongoDB to SQLAlchemy
2. **Integration Testing** - Test all endpoints thoroughly
3. **Data Migration** - If migrating from existing MongoDB instance
4. **Performance Tuning** - Add indexes, optimize queries
5. **Documentation** - Update API docs with any schema changes

---

**Version:** 1.2.0  
**Status:** 🚧 Schema Complete, Services Migration In Progress  
**Date:** November 24, 2025
