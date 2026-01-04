"""Custom Domain Service for deployed websites"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict
from app.core.database import get_db
import httpx
import os

# Netlify API
NETLIFY_API_KEY = os.environ.get("NETLIFY_API_KEY", "")
NETLIFY_API_BASE = "https://api.netlify.com/api/v1"

# Vercel API
VERCEL_API_KEY = os.environ.get("VERCEL_API_KEY", "")
VERCEL_API_BASE = "https://api.vercel.com"


class CustomDomainService:
    """Service for managing custom domains for deployed websites"""
    
    @staticmethod
    async def add_custom_domain(
        website_id: str,
        workspace_id: str,
        domain: str,
        user_id: str
    ) -> dict:
        """Add a custom domain to a website"""
        db = get_db()
        
        # Get website
        website = await db.ai_websites.find_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        
        if not website:
            return {"success": False, "error": "Website not found"}
        
        if website.get("status") != "deployed":
            return {"success": False, "error": "Website must be deployed first"}
        
        # Clean domain
        domain = domain.lower().strip()
        if domain.startswith("http://"):
            domain = domain[7:]
        if domain.startswith("https://"):
            domain = domain[8:]
        if domain.startswith("www."):
            domain = domain[4:]
        domain = domain.rstrip("/")
        
        # Validate domain format
        if not CustomDomainService._is_valid_domain(domain):
            return {"success": False, "error": "Invalid domain format"}
        
        # Check if domain is already in use
        existing = await db.custom_domains.find_one({"domain": domain})
        if existing:
            return {"success": False, "error": "Domain is already in use"}
        
        # Get deployment platform
        platform = website.get("deploymentPlatform", "netlify")
        platform_site_id = website.get("netlifyId") or website.get("vercelProjectId")
        
        # Add domain to platform
        dns_records = []
        verification_status = "pending"
        
        if platform == "netlify" and platform_site_id and NETLIFY_API_KEY:
            result = await CustomDomainService._add_netlify_domain(platform_site_id, domain)
            if result.get("success"):
                dns_records = result.get("dns_records", [])
                verification_status = "pending_dns"
        elif platform == "vercel" and VERCEL_API_KEY:
            result = await CustomDomainService._add_vercel_domain(website.get("vercelProjectId"), domain)
            if result.get("success"):
                dns_records = result.get("dns_records", [])
                verification_status = "pending_dns"
        else:
            # For platforms without API, provide manual instructions
            dns_records = [
                {"type": "CNAME", "name": domain, "value": website.get("deploymentUrl", "").replace("https://", "").replace("http://", "")},
                {"type": "A", "name": domain, "value": "75.2.60.5"}  # Netlify's load balancer
            ]
            verification_status = "pending_dns"
        
        # Create domain record
        domain_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        domain_record = {
            "id": domain_id,
            "websiteId": website_id,
            "workspace_id": workspace_id,
            "domain": domain,
            "platform": platform,
            "status": verification_status,
            "sslStatus": "pending",
            "dnsRecords": dns_records,
            "createdBy": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.custom_domains.insert_one(domain_record)
        
        # Update website
        await db.ai_websites.update_one(
            {"id": website_id},
            {
                "$set": {
                    "customDomain": domain,
                    "customDomainStatus": verification_status,
                    "updatedAt": now
                }
            }
        )
        
        return {
            "success": True,
            "domainId": domain_id,
            "domain": domain,
            "status": verification_status,
            "dnsRecords": dns_records,
            "message": "Domain added. Please configure DNS records."
        }
    
    @staticmethod
    async def verify_domain(
        domain_id: str,
        workspace_id: str
    ) -> dict:
        """Verify DNS configuration for a custom domain"""
        db = get_db()
        
        domain_record = await db.custom_domains.find_one({
            "id": domain_id,
            "workspace_id": workspace_id
        })
        
        if not domain_record:
            return {"success": False, "error": "Domain not found"}
        
        domain = domain_record.get("domain")
        
        # Check DNS resolution
        import socket
        try:
            # Try to resolve the domain
            socket.gethostbyname(domain)
            dns_verified = True
        except socket.gaierror:
            dns_verified = False
        
        # Update status
        now = datetime.now(timezone.utc).isoformat()
        new_status = "active" if dns_verified else "pending_dns"
        ssl_status = "active" if dns_verified else "pending"
        
        await db.custom_domains.update_one(
            {"id": domain_id},
            {
                "$set": {
                    "status": new_status,
                    "sslStatus": ssl_status,
                    "lastVerified": now,
                    "updatedAt": now
                }
            }
        )
        
        # Update website
        await db.ai_websites.update_one(
            {"id": domain_record.get("websiteId")},
            {
                "$set": {
                    "customDomainStatus": new_status,
                    "updatedAt": now
                }
            }
        )
        
        return {
            "success": True,
            "domain": domain,
            "status": new_status,
            "dnsVerified": dns_verified,
            "sslStatus": ssl_status,
            "message": "Domain verified successfully!" if dns_verified else "DNS not yet propagated. Please wait and try again."
        }
    
    @staticmethod
    async def remove_domain(
        domain_id: str,
        workspace_id: str
    ) -> dict:
        """Remove a custom domain"""
        db = get_db()
        
        domain_record = await db.custom_domains.find_one({
            "id": domain_id,
            "workspace_id": workspace_id
        })
        
        if not domain_record:
            return {"success": False, "error": "Domain not found"}
        
        # Remove from platform if possible
        platform = domain_record.get("platform")
        if platform == "netlify" and NETLIFY_API_KEY:
            # Netlify domain removal would go here
            pass
        
        # Delete domain record
        await db.custom_domains.delete_one({"id": domain_id})
        
        # Update website
        await db.ai_websites.update_one(
            {"id": domain_record.get("websiteId")},
            {
                "$unset": {"customDomain": "", "customDomainStatus": ""},
                "$set": {"updatedAt": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return {
            "success": True,
            "message": "Domain removed successfully"
        }
    
    @staticmethod
    async def get_domain(domain_id: str, workspace_id: str) -> Optional[dict]:
        """Get domain details"""
        db = get_db()
        domain = await db.custom_domains.find_one({
            "id": domain_id,
            "workspace_id": workspace_id
        })
        if domain:
            domain.pop("_id", None)
        return domain
    
    @staticmethod
    async def get_website_domains(website_id: str, workspace_id: str) -> List[dict]:
        """Get all domains for a website"""
        db = get_db()
        domains = await db.custom_domains.find({
            "websiteId": website_id,
            "workspace_id": workspace_id
        }).to_list(length=10)
        return [{k: v for k, v in d.items() if k != "_id"} for d in domains]
    
    @staticmethod
    def _is_valid_domain(domain: str) -> bool:
        """Validate domain format"""
        import re
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    @staticmethod
    async def _add_netlify_domain(site_id: str, domain: str) -> dict:
        """Add domain to Netlify site"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{NETLIFY_API_BASE}/sites/{site_id}/domains",
                    headers={
                        "Authorization": f"Bearer {NETLIFY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={"hostname": domain},
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {
                        "success": True,
                        "dns_records": [
                            {"type": "CNAME", "name": domain, "value": f"{site_id}.netlify.app"}
                        ]
                    }
                else:
                    return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _add_vercel_domain(project_id: str, domain: str) -> dict:
        """Add domain to Vercel project"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{VERCEL_API_BASE}/v10/projects/{project_id}/domains",
                    headers={
                        "Authorization": f"Bearer {VERCEL_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={"name": domain},
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {
                        "success": True,
                        "dns_records": [
                            {"type": "A", "name": domain, "value": "76.76.21.21"},
                            {"type": "CNAME", "name": f"www.{domain}", "value": "cname.vercel-dns.com"}
                        ]
                    }
                else:
                    return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
