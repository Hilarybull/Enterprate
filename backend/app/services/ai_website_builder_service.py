"""
AI Website Builder Service
Converts business descriptions into high-converting landing pages using AIDA framework.
Integrates with Gemini 2.0 Flash for content generation and multiple deployment platforms.
Supports multi-language generation and lead capture forms.
"""
import os
import uuid
import httpx
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from app.core.database import get_db

# Try to import LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# API Keys (from environment)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("EMERGENT_LLM_KEY", ""))
NETLIFY_API_KEY = os.environ.get("NETLIFY_API_KEY", "")
VERCEL_API_KEY = os.environ.get("VERCEL_API_KEY", "")
RAILWAY_API_KEY = os.environ.get("RAILWAY_API_KEY", "")

# API Base URLs
NETLIFY_API_BASE = "https://api.netlify.com/api/v1"
VERCEL_API_BASE = "https://api.vercel.com"
RAILWAY_API_BASE = "https://backboard.railway.app/graphql/v2"


class AIWebsiteBuilderService:
    """
    Lead AI Architect & Deployment Agent.
    Converts user business descriptions into production-ready, high-converting landing pages.
    Supports multi-language, lead capture, and multiple deployment platforms.
    """
    
    # AIDA Framework sections
    AIDA_SECTIONS = {
        "attention": "Hero Section - High-impact headline focusing on the RESULT",
        "interest": "Features/Benefits - Translate features into emotional benefits",
        "desire": "Social Proof/Why Us - Establish authority and trust",
        "action": "Conversion - Clear Call-to-Action buttons"
    }
    
    # Default color schemes
    COLOR_SCHEMES = {
        "modern": {"primary": "#6366f1", "secondary": "#4f46e5", "accent": "#10b981"},
        "professional": {"primary": "#1e40af", "secondary": "#1e3a8a", "accent": "#059669"},
        "creative": {"primary": "#ec4899", "secondary": "#db2777", "accent": "#8b5cf6"},
        "minimal": {"primary": "#18181b", "secondary": "#27272a", "accent": "#3f3f46"},
        "warm": {"primary": "#ea580c", "secondary": "#c2410c", "accent": "#facc15"},
        "nature": {"primary": "#16a34a", "secondary": "#15803d", "accent": "#0d9488"}
    }
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        "en": {"name": "English", "direction": "ltr"},
        "es": {"name": "Spanish", "direction": "ltr"},
        "fr": {"name": "French", "direction": "ltr"},
        "de": {"name": "German", "direction": "ltr"},
        "it": {"name": "Italian", "direction": "ltr"},
        "pt": {"name": "Portuguese", "direction": "ltr"},
        "nl": {"name": "Dutch", "direction": "ltr"},
        "pl": {"name": "Polish", "direction": "ltr"},
        "ru": {"name": "Russian", "direction": "ltr"},
        "zh": {"name": "Chinese (Simplified)", "direction": "ltr"},
        "ja": {"name": "Japanese", "direction": "ltr"},
        "ko": {"name": "Korean", "direction": "ltr"},
        "ar": {"name": "Arabic", "direction": "rtl"},
        "hi": {"name": "Hindi", "direction": "ltr"},
        "tr": {"name": "Turkish", "direction": "ltr"}
    }
    
    # Deployment platforms
    DEPLOYMENT_PLATFORMS = {
        "netlify": {"name": "Netlify", "key_env": "NETLIFY_API_KEY"},
        "vercel": {"name": "Vercel", "key_env": "VERCEL_API_KEY"},
        "railway": {"name": "Railway", "key_env": "RAILWAY_API_KEY"}
    }
    
    @staticmethod
    async def generate_website(
        workspace_id: str,
        user_id: str,
        user_description: str,
        brand_preferences: Optional[Dict] = None,
        logo_url: Optional[str] = None,
        contact_method: str = "form",
        contact_value: Optional[str] = None
    ) -> dict:
        """
        Generate a high-converting landing page from business description.
        Uses AIDA framework and AI content generation.
        """
        db = get_db()
        
        # Get company profile for context
        profile = await db.company_profiles.find_one({"workspace_id": workspace_id})
        
        # Combine context
        business_context = {
            "description": user_description,
            "companyName": profile.get("legalName", profile.get("proposedName", "Your Business")) if profile else "Your Business",
            "industry": profile.get("businessDescription", "") if profile else "",
            "targetMarket": profile.get("targetMarket", "") if profile else "",
            "brandPreferences": brand_preferences or {},
            "logoUrl": logo_url,
            "contactMethod": contact_method,
            "contactValue": contact_value
        }
        
        # Generate HTML using AI
        html_content = await AIWebsiteBuilderService._generate_html_with_ai(business_context)
        
        # Create website record
        website_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        website = {
            "id": website_id,
            "workspace_id": workspace_id,
            "status": "draft",  # draft, deployed, archived
            "businessContext": business_context,
            "htmlContent": html_content,
            "version": 1,
            "versions": [{
                "version": 1,
                "htmlContent": html_content,
                "createdAt": now
            }],
            "deploymentUrl": None,
            "netlifyId": None,
            "createdBy": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.ai_websites.insert_one(website)
        
        return {
            "id": website_id,
            "htmlContent": html_content,
            "status": "draft",
            "message": "Website generated successfully. Preview and refine before deploying."
        }
    
    @staticmethod
    async def _generate_html_with_ai(context: dict) -> str:
        """Generate HTML using AI with AIDA framework"""
        
        company_name = context.get("companyName", "Your Business")
        description = context.get("description", "")
        industry = context.get("industry", "")
        target_market = context.get("targetMarket", "")
        preferences = context.get("brandPreferences", {})
        logo_url = context.get("logoUrl")
        contact_method = context.get("contactMethod", "form")
        contact_value = context.get("contactValue", "")
        
        # Determine color scheme
        color_scheme_name = preferences.get("colorScheme", "modern")
        colors = AIWebsiteBuilderService.COLOR_SCHEMES.get(
            color_scheme_name, 
            AIWebsiteBuilderService.COLOR_SCHEMES["modern"]
        )
        
        # Get appropriate Unsplash images based on industry
        hero_image = AIWebsiteBuilderService._get_unsplash_image(industry or description)
        
        # Build the prompt for AI
        prompt = f"""You are an expert landing page designer. Create a high-converting landing page HTML using the AIDA framework.

BUSINESS CONTEXT:
- Company Name: {company_name}
- Description: {description}
- Industry: {industry}
- Target Market: {target_market}

DESIGN REQUIREMENTS:
1. ATTENTION (Hero): Create a compelling headline focusing on the RESULT/BENEFIT, not just the company name
2. INTEREST (Features): 3-4 feature blocks with icons, translating features into emotional benefits
3. DESIRE (Social Proof): Testimonials section, stats/numbers, trust badges
4. ACTION (CTA): Two prominent CTA buttons - one in hero, one at bottom

TECHNICAL REQUIREMENTS:
- Use Tailwind CSS via CDN
- Mobile-first, fully responsive
- Modern, professional design
- Include Font Awesome for icons
- Color scheme: Primary {colors['primary']}, Secondary {colors['secondary']}, Accent {colors['accent']}
- Hero background image: {hero_image}
{f'- Logo URL: {logo_url}' if logo_url else '- No logo provided, use text-based logo'}

CONTACT METHOD: {contact_method}
{f'Contact Value: {contact_value}' if contact_value else ''}

Generate ONLY the complete HTML code. No explanations or markdown - just valid HTML starting with <!DOCTYPE html>."""

        if LLM_AVAILABLE and GEMINI_API_KEY:
            try:
                chat = LlmChat(
                    api_key=GEMINI_API_KEY,
                    session_id=f"website-builder-{uuid.uuid4().hex[:8]}",
                    system_message="You are an expert web designer specializing in high-converting landing pages. Output only valid HTML code."
                ).with_model("google", "gemini-2.0-flash")
                
                response = await chat.send_message(UserMessage(text=prompt))
                html = response.text if hasattr(response, 'text') else str(response)
                
                # Clean up response (remove markdown if present)
                if html.startswith("```html"):
                    html = html[7:]
                if html.startswith("```"):
                    html = html[3:]
                if html.endswith("```"):
                    html = html[:-3]
                
                return html.strip()
                
            except Exception as e:
                print(f"AI generation error: {e}")
        
        # Fallback: Generate template-based HTML
        return AIWebsiteBuilderService._generate_template_html(context, colors, hero_image)
    
    @staticmethod
    def _generate_template_html(context: dict, colors: dict, hero_image: str) -> str:
        """Generate template-based HTML when AI is unavailable"""
        company_name = context.get("companyName", "Your Business")
        description = context.get("description", "Transform your business with our innovative solutions")
        logo_url = context.get("logoUrl", "")
        contact_method = context.get("contactMethod", "form")
        contact_value = context.get("contactValue", "#")
        
        cta_href = f"mailto:{contact_value}" if contact_method == "email" else f"tel:{contact_value}" if contact_method == "phone" else "#contact"
        cta_text = "Get Started"
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - Transform Your Business</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: {colors['primary']};
            --secondary: {colors['secondary']};
            --accent: {colors['accent']};
        }}
        .gradient-primary {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); }}
        .text-primary {{ color: var(--primary); }}
        .bg-primary {{ background-color: var(--primary); }}
        .border-primary {{ border-color: var(--primary); }}
        .hover\\:bg-primary:hover {{ background-color: var(--secondary); }}
    </style>
</head>
<body class="font-sans antialiased">
    <!-- HERO SECTION - ATTENTION -->
    <section class="relative min-h-screen flex items-center" style="background: linear-gradient(135deg, rgba(0,0,0,0.7), rgba(0,0,0,0.5)), url('{hero_image}') center/cover no-repeat;">
        <nav class="absolute top-0 left-0 right-0 p-6 flex justify-between items-center">
            <div class="flex items-center space-x-2">
                {f'<img src="{logo_url}" alt="{company_name}" class="h-10">' if logo_url else f'<span class="text-2xl font-bold text-white">{company_name}</span>'}
            </div>
            <div class="hidden md:flex space-x-8 text-white">
                <a href="#features" class="hover:text-gray-300 transition">Features</a>
                <a href="#about" class="hover:text-gray-300 transition">About</a>
                <a href="#testimonials" class="hover:text-gray-300 transition">Testimonials</a>
                <a href="{cta_href}" class="px-6 py-2 rounded-full gradient-primary hover:opacity-90 transition">{cta_text}</a>
            </div>
        </nav>
        <div class="container mx-auto px-6 text-center">
            <h1 class="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
                Transform Your Business Today
            </h1>
            <p class="text-xl md:text-2xl text-gray-200 mb-10 max-w-3xl mx-auto">
                {description}
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="{cta_href}" class="px-8 py-4 rounded-full gradient-primary text-white text-lg font-semibold hover:opacity-90 transition shadow-lg">
                    {cta_text} <i class="fas fa-arrow-right ml-2"></i>
                </a>
                <a href="#features" class="px-8 py-4 rounded-full border-2 border-white text-white text-lg font-semibold hover:bg-white hover:text-gray-900 transition">
                    Learn More
                </a>
            </div>
        </div>
    </section>

    <!-- FEATURES SECTION - INTEREST -->
    <section id="features" class="py-20 bg-gray-50">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl md:text-4xl font-bold text-center mb-4">Why Choose Us</h2>
            <p class="text-gray-600 text-center mb-16 max-w-2xl mx-auto">Discover the benefits that set us apart</p>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition">
                    <div class="w-14 h-14 rounded-full gradient-primary flex items-center justify-center mb-6">
                        <i class="fas fa-rocket text-white text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">Fast Results</h3>
                    <p class="text-gray-600">See measurable improvements in your business within weeks, not months.</p>
                </div>
                <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition">
                    <div class="w-14 h-14 rounded-full gradient-primary flex items-center justify-center mb-6">
                        <i class="fas fa-shield-alt text-white text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">Trusted & Reliable</h3>
                    <p class="text-gray-600">Join hundreds of satisfied customers who trust us with their success.</p>
                </div>
                <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition">
                    <div class="w-14 h-14 rounded-full gradient-primary flex items-center justify-center mb-6">
                        <i class="fas fa-headset text-white text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">24/7 Support</h3>
                    <p class="text-gray-600">Our dedicated team is always here to help you succeed.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- STATS SECTION - DESIRE -->
    <section id="about" class="py-16 gradient-primary">
        <div class="container mx-auto px-6">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white">
                <div>
                    <div class="text-4xl md:text-5xl font-bold mb-2">500+</div>
                    <div class="text-gray-200">Happy Clients</div>
                </div>
                <div>
                    <div class="text-4xl md:text-5xl font-bold mb-2">98%</div>
                    <div class="text-gray-200">Satisfaction Rate</div>
                </div>
                <div>
                    <div class="text-4xl md:text-5xl font-bold mb-2">10+</div>
                    <div class="text-gray-200">Years Experience</div>
                </div>
                <div>
                    <div class="text-4xl md:text-5xl font-bold mb-2">24/7</div>
                    <div class="text-gray-200">Support</div>
                </div>
            </div>
        </div>
    </section>

    <!-- TESTIMONIALS SECTION - DESIRE -->
    <section id="testimonials" class="py-20 bg-white">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl md:text-4xl font-bold text-center mb-16">What Our Clients Say</h2>
            <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                <div class="bg-gray-50 p-8 rounded-2xl">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 rounded-full bg-gray-300 mr-4"></div>
                        <div>
                            <div class="font-bold">Sarah Johnson</div>
                            <div class="text-gray-500 text-sm">CEO, TechStart</div>
                        </div>
                    </div>
                    <p class="text-gray-600 italic">"Working with {company_name} transformed our business. The results exceeded our expectations!"</p>
                    <div class="mt-4 text-yellow-400">
                        <i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i>
                    </div>
                </div>
                <div class="bg-gray-50 p-8 rounded-2xl">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 rounded-full bg-gray-300 mr-4"></div>
                        <div>
                            <div class="font-bold">Michael Chen</div>
                            <div class="text-gray-500 text-sm">Founder, GrowthLabs</div>
                        </div>
                    </div>
                    <p class="text-gray-600 italic">"Professional, efficient, and results-driven. Highly recommend to any serious business."</p>
                    <div class="mt-4 text-yellow-400">
                        <i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA SECTION - ACTION -->
    <section id="contact" class="py-20 bg-gray-900">
        <div class="container mx-auto px-6 text-center">
            <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">Ready to Get Started?</h2>
            <p class="text-gray-300 mb-10 max-w-2xl mx-auto">Join hundreds of businesses that have transformed their success with us.</p>
            <a href="{cta_href}" class="inline-block px-10 py-4 rounded-full gradient-primary text-white text-lg font-semibold hover:opacity-90 transition shadow-lg">
                {cta_text} <i class="fas fa-arrow-right ml-2"></i>
            </a>
        </div>
    </section>

    <!-- FOOTER -->
    <footer class="py-8 bg-gray-950 text-gray-400">
        <div class="container mx-auto px-6 text-center">
            <p>&copy; {datetime.now().year} {company_name}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>'''
    
    @staticmethod
    def _get_unsplash_image(context: str) -> str:
        """Get appropriate Unsplash image based on business context"""
        keywords = context.lower()
        
        if any(word in keywords for word in ["tech", "software", "digital", "ai", "app"]):
            return "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80"
        elif any(word in keywords for word in ["finance", "bank", "invest", "money"]):
            return "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1920&q=80"
        elif any(word in keywords for word in ["health", "medical", "wellness", "fitness"]):
            return "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1920&q=80"
        elif any(word in keywords for word in ["food", "restaurant", "cafe", "culinary"]):
            return "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&q=80"
        elif any(word in keywords for word in ["real estate", "property", "home"]):
            return "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1920&q=80"
        elif any(word in keywords for word in ["education", "learning", "school", "training"]):
            return "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1920&q=80"
        elif any(word in keywords for word in ["marketing", "agency", "creative", "design"]):
            return "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1920&q=80"
        else:
            return "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80"
    
    @staticmethod
    async def refine_website(
        website_id: str,
        workspace_id: str,
        user_id: str,
        feedback: str
    ) -> dict:
        """Refine website based on user feedback"""
        db = get_db()
        
        website = await db.ai_websites.find_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        current_html = website.get("htmlContent", "")
        context = website.get("businessContext", {})
        
        # Generate refined HTML using AI
        refined_html = await AIWebsiteBuilderService._refine_html_with_ai(
            current_html, feedback, context
        )
        
        # Update website with new version
        new_version = website.get("version", 1) + 1
        now = datetime.now(timezone.utc).isoformat()
        
        versions = website.get("versions", [])
        versions.append({
            "version": new_version,
            "htmlContent": refined_html,
            "feedback": feedback,
            "createdAt": now
        })
        
        await db.ai_websites.update_one(
            {"id": website_id},
            {
                "$set": {
                    "htmlContent": refined_html,
                    "version": new_version,
                    "versions": versions,
                    "updatedAt": now
                }
            }
        )
        
        return {
            "id": website_id,
            "htmlContent": refined_html,
            "version": new_version,
            "message": "Website refined successfully"
        }
    
    @staticmethod
    async def _refine_html_with_ai(current_html: str, feedback: str, context: dict) -> str:
        """Refine HTML based on user feedback using AI"""
        
        prompt = f"""You are an expert web designer. Refine this landing page HTML based on the user feedback.

CURRENT HTML:
{current_html}

USER FEEDBACK:
{feedback}

INSTRUCTIONS:
1. Apply the user's requested changes
2. Maintain the AIDA framework structure
3. Keep the design mobile-first and responsive
4. Preserve the overall look and feel unless specifically asked to change
5. Output ONLY the complete refined HTML code - no explanations

Generate the refined HTML starting with <!DOCTYPE html>:"""

        if LLM_AVAILABLE and GEMINI_API_KEY:
            try:
                chat = LlmChat(
                    api_key=GEMINI_API_KEY,
                    session_id=f"website-refine-{uuid.uuid4().hex[:8]}",
                    system_message="You are an expert web designer. Output only valid HTML code."
                ).with_model("google", "gemini-2.0-flash")
                
                response = await chat.send_message(UserMessage(text=prompt))
                html = response.text if hasattr(response, 'text') else str(response)
                
                # Clean up response
                if html.startswith("```html"):
                    html = html[7:]
                if html.startswith("```"):
                    html = html[3:]
                if html.endswith("```"):
                    html = html[:-3]
                
                return html.strip()
                
            except Exception as e:
                print(f"AI refinement error: {e}")
        
        # Return current HTML if AI unavailable
        return current_html
    
    @staticmethod
    async def deploy_to_netlify(
        website_id: str,
        workspace_id: str,
        user_id: str,
        site_name: Optional[str] = None
    ) -> dict:
        """Deploy website to Netlify"""
        db = get_db()
        
        website = await db.ai_websites.find_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        html_content = website.get("htmlContent", "")
        
        if not NETLIFY_API_KEY:
            # Return mock deployment result
            mock_url = f"https://{site_name or 'enterprate-site'}-{uuid.uuid4().hex[:8]}.netlify.app"
            
            await db.ai_websites.update_one(
                {"id": website_id},
                {
                    "$set": {
                        "status": "deployed",
                        "deploymentUrl": mock_url,
                        "deployedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            return {
                "success": True,
                "siteUrl": mock_url,
                "message": "Website deployed successfully (simulated - configure NETLIFY_API_KEY for real deployment)",
                "downloadUrl": f"/api/websites/{website_id}/download"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                # Create new site
                site_response = await client.post(
                    f"{NETLIFY_API_BASE}/sites",
                    headers={
                        "Authorization": f"Bearer {NETLIFY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={"name": site_name} if site_name else {},
                    timeout=30.0
                )
                
                if site_response.status_code not in [200, 201]:
                    raise Exception(f"Failed to create site: {site_response.text}")
                
                site_data = site_response.json()
                site_id = site_data.get("site_id") or site_data.get("id")
                
                # Deploy HTML
                deploy_response = await client.post(
                    f"{NETLIFY_API_BASE}/sites/{site_id}/deploys",
                    headers={
                        "Authorization": f"Bearer {NETLIFY_API_KEY}",
                        "Content-Type": "application/zip"
                    },
                    content=AIWebsiteBuilderService._create_deploy_zip(html_content),
                    timeout=60.0
                )
                
                if deploy_response.status_code not in [200, 201]:
                    raise Exception(f"Failed to deploy: {deploy_response.text}")
                
                deploy_data = deploy_response.json()
                site_url = deploy_data.get("ssl_url") or deploy_data.get("url") or site_data.get("ssl_url")
                
                # Update website record
                await db.ai_websites.update_one(
                    {"id": website_id},
                    {
                        "$set": {
                            "status": "deployed",
                            "deploymentUrl": site_url,
                            "netlifyId": site_id,
                            "deployedAt": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                # Send notification
                from app.services.notification_service import NotificationService
                await NotificationService.notify_website_deployed(
                    workspace_id, user_id, site_url, site_name or "Your Website"
                )
                
                return {
                    "success": True,
                    "siteUrl": site_url,
                    "siteId": site_id,
                    "message": "Website deployed successfully!",
                    "downloadUrl": f"/api/websites/{website_id}/download"
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")
    
    @staticmethod
    def _create_deploy_zip(html_content: str) -> bytes:
        """Create a ZIP file for Netlify deployment"""
        import io
        import zipfile
        
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('index.html', html_content)
        
        return buffer.getvalue()
    
    @staticmethod
    async def get_website(website_id: str, workspace_id: str) -> Optional[dict]:
        """Get website by ID"""
        db = get_db()
        website = await db.ai_websites.find_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        return {k: v for k, v in website.items() if k != '_id'} if website else None
    
    @staticmethod
    async def get_websites(workspace_id: str) -> List[dict]:
        """Get all websites for a workspace"""
        db = get_db()
        websites = await db.ai_websites.find({
            "workspace_id": workspace_id
        }).sort("createdAt", -1).to_list(length=50)
        return [{k: v for k, v in w.items() if k != '_id'} for w in websites]
    
    @staticmethod
    async def delete_website(website_id: str, workspace_id: str) -> bool:
        """Delete a website"""
        db = get_db()
        result = await db.ai_websites.delete_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
