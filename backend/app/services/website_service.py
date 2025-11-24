"""Website builder service"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.website import Website, WebsitePage
from app.schemas.website import WebsiteCreate, WebsitePageCreate

class WebsiteService:
    """Service for website builder features"""
    
    @staticmethod
    async def get_websites(db: AsyncSession, workspace_id: str) -> list:
        """Get all websites for a workspace"""
        workspace_uuid = UUID(workspace_id)
        
        stmt = select(Website).where(Website.workspace_id == workspace_uuid)
        result = await db.execute(stmt)
        websites = result.scalars().all()
        
        return [
            {
                "id": str(ws.id),
                "workspaceId": str(ws.workspace_id),
                "projectId": str(ws.project_id) if ws.project_id else None,
                "name": ws.name,
                "domain": ws.domain,
                "published": ws.published,
                "config": ws.config,
                "createdAt": ws.created_at.isoformat()
            }
            for ws in websites
        ]
    
    @staticmethod
    async def create_website(db: AsyncSession, website_data: WebsiteCreate, workspace_id: str) -> dict:
        """Create a new website"""
        workspace_uuid = UUID(workspace_id)
        
        website = Website(
            workspace_id=workspace_uuid,
            name=website_data.name,
            domain=website_data.domain,
            config={"theme": "default", "sections": []}
        )
        
        db.add(website)
        await db.flush()
        
        # Create default home page
        page = WebsitePage(
            website_id=website.id,
            path="/",
            title="Home",
            content={"sections": []}
        )
        db.add(page)
        await db.flush()
        
        return {
            "id": str(website.id),
            "workspaceId": str(website.workspace_id),
            "projectId": str(website.project_id) if website.project_id else None,
            "name": website.name,
            "domain": website.domain,
            "published": website.published,
            "config": website.config,
            "createdAt": website.created_at.isoformat()
        }
    
    @staticmethod
    async def get_website(db: AsyncSession, website_id: str, workspace_id: str) -> dict:
        """Get website by ID"""
        website_uuid = UUID(website_id)
        workspace_uuid = UUID(workspace_id)
        
        stmt = select(Website).where(
            Website.id == website_uuid,
            Website.workspace_id == workspace_uuid
        )
        result = await db.execute(stmt)
        website = result.scalar_one_or_none()
        
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        return {
            "id": str(website.id),
            "workspaceId": str(website.workspace_id),
            "projectId": str(website.project_id) if website.project_id else None,
            "name": website.name,
            "domain": website.domain,
            "published": website.published,
            "config": website.config,
            "createdAt": website.created_at.isoformat()
        }
    
    @staticmethod
    async def get_website_pages(db: AsyncSession, website_id: str) -> list:
        """Get all pages for a website"""
        website_uuid = UUID(website_id)
        
        stmt = select(WebsitePage).where(WebsitePage.website_id == website_uuid)
        result = await db.execute(stmt)
        pages = result.scalars().all()
        
        return [
            {
                "id": str(page.id),
                "websiteId": str(page.website_id),
                "path": page.path,
                "title": page.title,
                "content": page.content,
                "createdAt": page.created_at.isoformat()
            }
            for page in pages
        ]
    
    @staticmethod
    async def create_website_page(db: AsyncSession, website_id: str, page_data: WebsitePageCreate, workspace_id: str) -> dict:
        """Create a new website page"""
        website_uuid = UUID(website_id)
        workspace_uuid = UUID(workspace_id)
        
        # Verify website exists and belongs to workspace
        stmt = select(Website).where(
            Website.id == website_uuid,
            Website.workspace_id == workspace_uuid
        )
        result = await db.execute(stmt)
        website = result.scalar_one_or_none()
        
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        page = WebsitePage(
            website_id=website_uuid,
            path=page_data.path,
            title=page_data.title,
            content=page_data.content
        )
        
        db.add(page)
        await db.flush()
        
        return {
            "id": str(page.id),
            "websiteId": str(page.website_id),
            "path": page.path,
            "title": page.title,
            "content": page.content,
            "createdAt": page.created_at.isoformat()
        }
    
    @staticmethod
    async def update_website_page(db: AsyncSession, page_id: str, website_id: str, page_data: WebsitePageCreate) -> dict:
        """Update a website page"""
        page_uuid = UUID(page_id)
        website_uuid = UUID(website_id)
        
        stmt = select(WebsitePage).where(
            WebsitePage.id == page_uuid,
            WebsitePage.website_id == website_uuid
        )
        result = await db.execute(stmt)
        page = result.scalar_one_or_none()
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        # Update fields
        page.path = page_data.path
        page.title = page_data.title
        page.content = page_data.content
        
        await db.flush()
        
        return {
            "id": str(page.id),
            "websiteId": str(page.website_id),
            "path": page.path,
            "title": page.title,
            "content": page.content,
            "createdAt": page.created_at.isoformat()
        }
