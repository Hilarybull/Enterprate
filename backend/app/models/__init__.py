"""
MongoDB Data Models (Schema Documentation)

This file documents the MongoDB collection schemas used by EnterprateAI.
The application uses MongoDB via motor (async driver) with schema validation
handled through Pydantic models in /app/backend/app/schemas/.

Collections:
-----------
- users: User accounts (email, name, google auth, etc.)
- workspaces: Business workspaces 
- user_sessions: Authentication sessions
- company_profiles: Company registration data
- blueprints: Business blueprints
- invoices: Financial invoices
- expenses: Business expenses
- leads: Sales leads
- campaigns: Marketing campaigns
- social_posts: Social media content
- compliance_items: Compliance checklist items
- chat_sessions: AI assistant chat history
- growth_recommendations: Proactive growth agent suggestions
- intelligence_events: Business intelligence events log

Note: This application does NOT use SQLAlchemy or PostgreSQL.
All data operations are performed via MongoDB using motor async driver.
"""

# This file exists for documentation purposes only.
# Actual data validation is handled via Pydantic schemas.
