"""Website builder service"""
from fastapi import HTTPException
from app.core.database import get_database
from app.schemas.website import Website, WebsiteCreate, WebsitePage, WebsitePageCreate

class WebsiteService:
    """Service for website builder features"""
    
    @staticmethod
    async def get_websites(workspace_id: str) -> list:
        """Get all websites for a workspace"""
        db = get_database()
        websites = await db.websites.find({"workspaceId": workspace_id}, {"_id": 0}).to_list(100)
        return websites
    
    @staticmethod
    async def create_website(website_data: WebsiteCreate, workspace_id: str) -> dict:
        """Create a new website"""
        db = get_database()
        
        website = Website(
            workspaceId=workspace_id,
            name=website_data.name,
            domain=website_data.domain,
            config={"theme": "default", "sections": []}
        )
        
        doc = website.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        await db.websites.insert_one(doc)
        
        # Create default home page
        page = WebsitePage(
            websiteId=website.id,
            path="/",
            title="Home",
            content={"sections": []}
        )
        page_doc = page.model_dump()
        page_doc['createdAt'] = page_doc['createdAt'].isoformat()
        await db.website_pages.insert_one(page_doc)
        
        return website.model_dump()
    
    @staticmethod
    async def get_website(website_id: str, workspace_id: str) -> dict:
        """Get website by ID"""
        db = get_database()
        
        website = await db.websites.find_one(
            {"id": website_id, "workspaceId": workspace_id},
            {"_id": 0}
        )
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        return website
    
    @staticmethod
    async def get_website_pages(website_id: str) -> list:
        """Get all pages for a website"""
        db = get_database()
        pages = await db.website_pages.find({"websiteId": website_id}, {"_id": 0}).to_list(100)
        return pages
    
    @staticmethod
    async def create_website_page(website_id: str, page_data: WebsitePageCreate, workspace_id: str) -> dict:
        """Create a new website page"""
        db = get_database()
        
        # Verify website exists and belongs to workspace
        website = await db.websites.find_one(
            {"id": website_id, "workspaceId": workspace_id}
        )
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        page = WebsitePage(
            websiteId=website_id,
            **page_data.model_dump()
        )
        
        doc = page.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        await db.website_pages.insert_one(doc)
        
        return page.model_dump()
    
    @staticmethod
    async def update_website_page(page_id: str, website_id: str, page_data: WebsitePageCreate) -> dict:
        """Update a website page"""
        db = get_database()
        
        update_data = page_data.model_dump()
        
        await db.website_pages.update_one(
            {"id": page_id, "websiteId": website_id},
            {"$set": update_data}
        )
        
        page = await db.website_pages.find_one({"id": page_id}, {"_id": 0})
        return page
