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
        contact_value: Optional[str] = None,
        language: str = "en",
        include_lead_form: bool = True
    ) -> dict:
        """
        Generate a high-converting landing page from business description.
        Uses AIDA framework and AI content generation.
        Supports multi-language and lead capture forms.
        """
        db = get_db()
        
        # Validate language
        if language not in AIWebsiteBuilderService.SUPPORTED_LANGUAGES:
            language = "en"
        
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
            "contactValue": contact_value,
            "language": language,
            "languageInfo": AIWebsiteBuilderService.SUPPORTED_LANGUAGES[language],
            "includeLeadForm": include_lead_form,
            "workspaceId": workspace_id
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
            "language": language,
            "includeLeadForm": include_lead_form,
            "version": 1,
            "versions": [{
                "version": 1,
                "htmlContent": html_content,
                "createdAt": now
            }],
            "deploymentUrl": None,
            "deploymentPlatform": None,
            "platformSiteId": None,
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
        language = context.get("language", "en")
        lang_info = context.get("languageInfo", {"direction": "ltr"})
        include_lead_form = context.get("includeLeadForm", True)
        workspace_id = context.get("workspaceId", "")
        
        # Language-specific text
        texts = AIWebsiteBuilderService._get_language_texts(language)
        
        cta_href = f"mailto:{contact_value}" if contact_method == "email" else f"tel:{contact_value}" if contact_method == "phone" else "#contact"
        cta_text = texts["cta"]
        
        # Lead capture form HTML
        lead_form_html = ""
        if include_lead_form:
            lead_form_html = AIWebsiteBuilderService._generate_lead_form_html(
                workspace_id, company_name, colors, texts
            )
        
        return f'''<!DOCTYPE html>
<html lang="{language}" dir="{lang_info.get('direction', 'ltr')}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - {texts["tagline"]}</title>
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
        .form-loading {{ opacity: 0.7; pointer-events: none; }}
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
                <a href="#features" class="hover:text-gray-300 transition">{texts["features"]}</a>
                <a href="#about" class="hover:text-gray-300 transition">{texts["about"]}</a>
                <a href="#contact" class="hover:text-gray-300 transition">{texts["contact"]}</a>
                <a href="{cta_href}" class="px-6 py-2 rounded-full gradient-primary hover:opacity-90 transition">{cta_text}</a>
            </div>
        </nav>
        <div class="container mx-auto px-6 text-center">
            <h1 class="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
                {texts["hero_title"]}
            </h1>
            <p class="text-xl md:text-2xl text-gray-200 mb-10 max-w-3xl mx-auto">
                {description}
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="#contact" class="px-8 py-4 rounded-full gradient-primary text-white text-lg font-semibold hover:opacity-90 transition shadow-lg">
                    {cta_text} <i class="fas fa-arrow-right ml-2"></i>
                </a>
                <a href="#features" class="px-8 py-4 rounded-full border-2 border-white text-white text-lg font-semibold hover:bg-white hover:text-gray-900 transition">
                    {texts["learn_more"]}
                </a>
            </div>
        </div>
    </section>

    <!-- FEATURES SECTION - INTEREST -->
    <section id="features" class="py-20 bg-gray-50">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl md:text-4xl font-bold text-center mb-4">{texts["why_choose"]}</h2>
            <p class="text-gray-600 text-center mb-16 max-w-2xl mx-auto">{texts["discover_benefits"]}</p>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition">
                    <div class="w-14 h-14 rounded-full gradient-primary flex items-center justify-center mb-6">
                        <i class="fas fa-rocket text-white text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">{texts["fast_results"]}</h3>
                    <p class="text-gray-600">{texts["fast_results_desc"]}</p>
                </div>
                <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition">
                    <div class="w-14 h-14 rounded-full gradient-primary flex items-center justify-center mb-6">
                        <i class="fas fa-shield-alt text-white text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">{texts["trusted"]}</h3>
                    <p class="text-gray-600">{texts["trusted_desc"]}</p>
                </div>
                <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition">
                    <div class="w-14 h-14 rounded-full gradient-primary flex items-center justify-center mb-6">
                        <i class="fas fa-headset text-white text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-4">{texts["support"]}</h3>
                    <p class="text-gray-600">{texts["support_desc"]}</p>
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
                    <div class="text-gray-200">{texts["happy_clients"]}</div>
                </div>
                <div>
                    <div class="text-4xl md:text-5xl font-bold mb-2">98%</div>
                    <div class="text-gray-200">{texts["satisfaction"]}</div>
                </div>
                <div>
                    <div class="text-4xl md:text-5xl font-bold mb-2">10+</div>
                    <div class="text-gray-200">{texts["experience"]}</div>
                </div>
                <div>
                    <div class="text-4xl md:text-5xl font-bold mb-2">24/7</div>
                    <div class="text-gray-200">{texts["support"]}</div>
                </div>
            </div>
        </div>
    </section>

    <!-- TESTIMONIALS SECTION - DESIRE -->
    <section id="testimonials" class="py-20 bg-white">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl md:text-4xl font-bold text-center mb-16">{texts["testimonials"]}</h2>
            <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                <div class="bg-gray-50 p-8 rounded-2xl">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 rounded-full bg-gray-300 mr-4"></div>
                        <div>
                            <div class="font-bold">Sarah Johnson</div>
                            <div class="text-gray-500 text-sm">CEO, TechStart</div>
                        </div>
                    </div>
                    <p class="text-gray-600 italic">"{texts["testimonial_1"].format(company=company_name)}"</p>
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
                    <p class="text-gray-600 italic">"{texts["testimonial_2"]}"</p>
                    <div class="mt-4 text-yellow-400">
                        <i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- CONTACT/LEAD CAPTURE SECTION - ACTION -->
    {lead_form_html}

    <!-- FOOTER -->
    <footer class="py-8 bg-gray-950 text-gray-400">
        <div class="container mx-auto px-6 text-center">
            <p>&copy; {datetime.now().year} {company_name}. {texts["rights"]}</p>
        </div>
    </footer>

    <!-- Lead Form Script -->
    <script>
        const LEAD_API_URL = '{os.environ.get("FRONTEND_URL", "")}/api/websites/lead';
        const WORKSPACE_ID = '{workspace_id}';
        
        async function submitLeadForm(event) {{
            event.preventDefault();
            const form = event.target;
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            form.classList.add('form-loading');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>{texts["submitting"]}';
            
            const formData = {{
                name: form.querySelector('[name="name"]').value,
                email: form.querySelector('[name="email"]').value,
                phone: form.querySelector('[name="phone"]')?.value || '',
                message: form.querySelector('[name="message"]').value,
                workspaceId: WORKSPACE_ID,
                source: 'website_form'
            }};
            
            try {{
                const response = await fetch(LEAD_API_URL, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(formData)
                }});
                
                if (response.ok) {{
                    form.innerHTML = '<div class="text-center py-8"><i class="fas fa-check-circle text-green-500 text-5xl mb-4"></i><h3 class="text-2xl font-bold text-white mb-2">{texts["thank_you"]}</h3><p class="text-gray-300">{texts["will_contact"]}</p></div>';
                }} else {{
                    throw new Error('Submission failed');
                }}
            }} catch (error) {{
                alert('{texts["error_message"]}');
                form.classList.remove('form-loading');
                submitBtn.innerHTML = originalText;
            }}
        }}
    </script>
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
    
    @staticmethod
    def _get_language_texts(language: str) -> dict:
        """Get localized UI texts for the generated website"""
        texts = {
            "en": {
                "tagline": "Transforming Your Business",
                "cta": "Get Started",
                "learn_more": "Learn More",
                "features": "Features",
                "about": "About",
                "contact": "Contact",
                "why_choose": "Why Choose Us",
                "discover_benefits": "Discover the benefits that set us apart from the competition.",
                "fast_results": "Fast Results",
                "fast_results_desc": "See measurable improvements quickly with our streamlined processes.",
                "trusted": "Trusted & Reliable",
                "trusted_desc": "Join thousands of satisfied clients who trust us with their success.",
                "support": "24/7 Support",
                "support_desc": "Our dedicated team is always here when you need assistance.",
                "happy_clients": "Happy Clients",
                "satisfaction": "Satisfaction Rate",
                "experience": "Years Experience",
                "testimonials": "What Our Clients Say",
                "testimonial_1": "Working with {company} has been transformative for our business. Highly recommended!",
                "testimonial_2": "Professional, responsive, and results-driven. The best decision we made.",
                "hero_title": "Transform Your Business Today",
                "rights": "All rights reserved.",
                "contact_us": "Contact Us",
                "get_in_touch": "Get in Touch",
                "ready_start": "Ready to get started? We'd love to hear from you.",
                "name": "Your Name",
                "email": "Email Address",
                "phone": "Phone Number",
                "message": "Your Message",
                "send_message": "Send Message",
                "submitting": "Sending...",
                "thank_you": "Thank You!",
                "will_contact": "We'll be in touch shortly.",
                "error_message": "Something went wrong. Please try again."
            },
            "es": {
                "tagline": "Transformando Tu Negocio",
                "cta": "Comenzar",
                "learn_more": "Más Información",
                "features": "Características",
                "about": "Nosotros",
                "contact": "Contacto",
                "why_choose": "¿Por Qué Elegirnos?",
                "discover_benefits": "Descubre los beneficios que nos diferencian de la competencia.",
                "fast_results": "Resultados Rápidos",
                "fast_results_desc": "Ve mejoras medibles rápidamente con nuestros procesos optimizados.",
                "trusted": "Confiable y Seguro",
                "trusted_desc": "Únete a miles de clientes satisfechos que confían en nosotros.",
                "support": "Soporte 24/7",
                "support_desc": "Nuestro equipo dedicado siempre está aquí cuando necesitas ayuda.",
                "happy_clients": "Clientes Felices",
                "satisfaction": "Tasa de Satisfacción",
                "experience": "Años de Experiencia",
                "testimonials": "Lo Que Dicen Nuestros Clientes",
                "testimonial_1": "Trabajar con {company} ha sido transformador para nuestro negocio. ¡Muy recomendado!",
                "testimonial_2": "Profesional, receptivo y orientado a resultados. La mejor decisión que tomamos.",
                "hero_title": "Transforma Tu Negocio Hoy",
                "rights": "Todos los derechos reservados.",
                "contact_us": "Contáctanos",
                "get_in_touch": "Ponte en Contacto",
                "ready_start": "¿Listo para comenzar? Nos encantaría saber de ti.",
                "name": "Tu Nombre",
                "email": "Correo Electrónico",
                "phone": "Teléfono",
                "message": "Tu Mensaje",
                "send_message": "Enviar Mensaje",
                "submitting": "Enviando...",
                "thank_you": "¡Gracias!",
                "will_contact": "Nos pondremos en contacto pronto.",
                "error_message": "Algo salió mal. Por favor intenta de nuevo."
            },
            "fr": {
                "tagline": "Transformer Votre Entreprise",
                "cta": "Commencer",
                "learn_more": "En Savoir Plus",
                "features": "Fonctionnalités",
                "about": "À Propos",
                "contact": "Contact",
                "why_choose": "Pourquoi Nous Choisir",
                "discover_benefits": "Découvrez les avantages qui nous distinguent de la concurrence.",
                "fast_results": "Résultats Rapides",
                "fast_results_desc": "Constatez des améliorations mesurables rapidement grâce à nos processus optimisés.",
                "trusted": "Fiable et Sûr",
                "trusted_desc": "Rejoignez des milliers de clients satisfaits qui nous font confiance.",
                "support": "Support 24/7",
                "support_desc": "Notre équipe dédiée est toujours là quand vous avez besoin d'aide.",
                "happy_clients": "Clients Satisfaits",
                "satisfaction": "Taux de Satisfaction",
                "experience": "Années d'Expérience",
                "testimonials": "Ce Que Disent Nos Clients",
                "testimonial_1": "Travailler avec {company} a été transformateur pour notre entreprise. Fortement recommandé!",
                "testimonial_2": "Professionnel, réactif et axé sur les résultats. La meilleure décision que nous ayons prise.",
                "hero_title": "Transformez Votre Entreprise Aujourd'hui",
                "rights": "Tous droits réservés.",
                "contact_us": "Contactez-Nous",
                "get_in_touch": "Entrer en Contact",
                "ready_start": "Prêt à commencer? Nous serions ravis de vous entendre.",
                "name": "Votre Nom",
                "email": "Adresse Email",
                "phone": "Téléphone",
                "message": "Votre Message",
                "send_message": "Envoyer le Message",
                "submitting": "Envoi...",
                "thank_you": "Merci!",
                "will_contact": "Nous vous contacterons bientôt.",
                "error_message": "Une erreur s'est produite. Veuillez réessayer."
            },
            "de": {
                "tagline": "Transformieren Sie Ihr Unternehmen",
                "cta": "Loslegen",
                "learn_more": "Mehr Erfahren",
                "features": "Funktionen",
                "about": "Über Uns",
                "contact": "Kontakt",
                "why_choose": "Warum Uns Wählen",
                "discover_benefits": "Entdecken Sie die Vorteile, die uns von der Konkurrenz abheben.",
                "fast_results": "Schnelle Ergebnisse",
                "fast_results_desc": "Sehen Sie schnell messbare Verbesserungen mit unseren optimierten Prozessen.",
                "trusted": "Vertrauenswürdig & Zuverlässig",
                "trusted_desc": "Schließen Sie sich Tausenden zufriedener Kunden an, die uns vertrauen.",
                "support": "24/7 Support",
                "support_desc": "Unser engagiertes Team ist immer für Sie da.",
                "happy_clients": "Zufriedene Kunden",
                "satisfaction": "Zufriedenheitsrate",
                "experience": "Jahre Erfahrung",
                "testimonials": "Was Unsere Kunden Sagen",
                "testimonial_1": "Die Zusammenarbeit mit {company} war transformativ für unser Geschäft. Sehr empfehlenswert!",
                "testimonial_2": "Professionell, reaktionsschnell und ergebnisorientiert. Die beste Entscheidung.",
                "hero_title": "Transformieren Sie Ihr Unternehmen Heute",
                "rights": "Alle Rechte vorbehalten.",
                "contact_us": "Kontaktieren Sie Uns",
                "get_in_touch": "Kontakt Aufnehmen",
                "ready_start": "Bereit loszulegen? Wir freuen uns von Ihnen zu hören.",
                "name": "Ihr Name",
                "email": "E-Mail-Adresse",
                "phone": "Telefonnummer",
                "message": "Ihre Nachricht",
                "send_message": "Nachricht Senden",
                "submitting": "Senden...",
                "thank_you": "Vielen Dank!",
                "will_contact": "Wir melden uns in Kürze.",
                "error_message": "Etwas ist schief gelaufen. Bitte versuchen Sie es erneut."
            }
        }
        # Return English as fallback for unsupported languages
        return texts.get(language, texts["en"])
    
    @staticmethod
    def _generate_lead_form_html(workspace_id: str, company_name: str, colors: dict, texts: dict) -> str:
        """Generate lead capture form HTML section"""
        api_base = os.environ.get("FRONTEND_URL", "")
        
        return f'''
    <section id="contact" class="py-20 bg-gray-900">
        <div class="container mx-auto px-6">
            <div class="max-w-2xl mx-auto text-center mb-12">
                <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">{texts["get_in_touch"]}</h2>
                <p class="text-gray-400">{texts["ready_start"]}</p>
            </div>
            <form id="lead-capture-form" onsubmit="submitLeadForm(event)" class="max-w-lg mx-auto bg-gray-800 p-8 rounded-2xl">
                <div class="space-y-6">
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-300 mb-2">{texts["name"]}</label>
                        <input type="text" name="name" id="name" required
                            class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[{colors['primary']}] focus:border-transparent"
                            placeholder="{texts["name"]}">
                    </div>
                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-300 mb-2">{texts["email"]}</label>
                        <input type="email" name="email" id="email" required
                            class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[{colors['primary']}] focus:border-transparent"
                            placeholder="{texts["email"]}">
                    </div>
                    <div>
                        <label for="phone" class="block text-sm font-medium text-gray-300 mb-2">{texts["phone"]}</label>
                        <input type="tel" name="phone" id="phone"
                            class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[{colors['primary']}] focus:border-transparent"
                            placeholder="{texts["phone"]}">
                    </div>
                    <div>
                        <label for="message" class="block text-sm font-medium text-gray-300 mb-2">{texts["message"]}</label>
                        <textarea name="message" id="message" rows="4" required
                            class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[{colors['primary']}] focus:border-transparent resize-none"
                            placeholder="{texts["message"]}"></textarea>
                    </div>
                    <button type="submit"
                        class="w-full px-6 py-4 rounded-lg gradient-primary text-white font-semibold hover:opacity-90 transition flex items-center justify-center">
                        <span>{texts["send_message"]}</span>
                        <i class="fas fa-paper-plane ml-2"></i>
                    </button>
                </div>
            </form>
        </div>
    </section>'''
    
    @staticmethod
    async def deploy_to_vercel(
        website_id: str,
        workspace_id: str,
        user_id: str,
        project_name: Optional[str] = None
    ) -> dict:
        """Deploy website to Vercel"""
        db = get_db()
        
        website = await db.ai_websites.find_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        html_content = website.get("htmlContent", "")
        
        if not VERCEL_API_KEY or VERCEL_API_KEY.startswith("REPLACE"):
            # Return mock deployment result
            mock_url = f"https://{project_name or 'enterprate-site'}-{uuid.uuid4().hex[:8]}.vercel.app"
            
            await db.ai_websites.update_one(
                {"id": website_id},
                {
                    "$set": {
                        "status": "deployed",
                        "deploymentUrl": mock_url,
                        "deploymentPlatform": "vercel",
                        "deployedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            return {
                "success": True,
                "siteUrl": mock_url,
                "message": "Website deployed successfully (simulated - configure VERCEL_API_KEY for real deployment)",
                "downloadUrl": f"/api/websites/{website_id}/download"
            }
        
        try:
            import base64
            
            async with httpx.AsyncClient() as client:
                # Create deployment using Vercel API v13
                files = [
                    {
                        "file": "index.html",
                        "data": base64.b64encode(html_content.encode()).decode()
                    }
                ]
                
                deploy_response = await client.post(
                    f"{VERCEL_API_BASE}/v13/deployments",
                    headers={
                        "Authorization": f"Bearer {VERCEL_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "name": project_name or f"enterprate-site-{uuid.uuid4().hex[:8]}",
                        "files": files,
                        "projectSettings": {
                            "framework": None
                        }
                    },
                    timeout=60.0
                )
                
                if deploy_response.status_code not in [200, 201]:
                    raise Exception(f"Deployment failed: {deploy_response.text}")
                
                deploy_data = deploy_response.json()
                site_url = f"https://{deploy_data.get('url', '')}"
                
                await db.ai_websites.update_one(
                    {"id": website_id},
                    {
                        "$set": {
                            "status": "deployed",
                            "deploymentUrl": site_url,
                            "deploymentPlatform": "vercel",
                            "vercelDeploymentId": deploy_data.get("id"),
                            "deployedAt": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                return {
                    "success": True,
                    "siteUrl": site_url,
                    "deploymentId": deploy_data.get("id"),
                    "message": "Website deployed to Vercel successfully!",
                    "downloadUrl": f"/api/websites/{website_id}/download"
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Vercel deployment failed: {str(e)}")
    
    @staticmethod
    async def deploy_to_railway(
        website_id: str,
        workspace_id: str,
        user_id: str,
        project_name: Optional[str] = None
    ) -> dict:
        """Deploy website to Railway"""
        db = get_db()
        
        website = await db.ai_websites.find_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        if not RAILWAY_API_KEY or RAILWAY_API_KEY.startswith("REPLACE"):
            # Return mock deployment result
            mock_url = f"https://{project_name or 'enterprate-site'}-{uuid.uuid4().hex[:8]}.up.railway.app"
            
            await db.ai_websites.update_one(
                {"id": website_id},
                {
                    "$set": {
                        "status": "deployed",
                        "deploymentUrl": mock_url,
                        "deploymentPlatform": "railway",
                        "deployedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            return {
                "success": True,
                "siteUrl": mock_url,
                "message": "Website deployed successfully (simulated - configure RAILWAY_API_KEY for real deployment)",
                "downloadUrl": f"/api/websites/{website_id}/download"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                # Railway uses GraphQL API
                graphql_query = """
                mutation deployStaticSite($input: DeployInput!) {
                    deploy(input: $input) {
                        id
                        staticUrl
                    }
                }
                """
                
                response = await client.post(
                    RAILWAY_API_BASE,
                    headers={
                        "Authorization": f"Bearer {RAILWAY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "query": graphql_query,
                        "variables": {
                            "input": {
                                "projectName": project_name or f"enterprate-site-{uuid.uuid4().hex[:8]}"
                            }
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code not in [200, 201]:
                    raise Exception(f"Railway API error: {response.text}")
                
                data = response.json()
                deploy_data = data.get("data", {}).get("deploy", {})
                site_url = deploy_data.get("staticUrl", "")
                
                await db.ai_websites.update_one(
                    {"id": website_id},
                    {
                        "$set": {
                            "status": "deployed",
                            "deploymentUrl": site_url,
                            "deploymentPlatform": "railway",
                            "railwayDeploymentId": deploy_data.get("id"),
                            "deployedAt": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                return {
                    "success": True,
                    "siteUrl": site_url,
                    "message": "Website deployed to Railway successfully!",
                    "downloadUrl": f"/api/websites/{website_id}/download"
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Railway deployment failed: {str(e)}")
    
    @staticmethod
    async def handle_lead_submission(
        workspace_id: str,
        name: str,
        email: str,
        phone: Optional[str] = None,
        message: Optional[str] = None,
        source: str = "website_form"
    ) -> dict:
        """Handle lead form submission from generated websites"""
        db = get_db()
        
        # Create lead record
        lead_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        lead = {
            "id": lead_id,
            "workspace_id": workspace_id,
            "name": name,
            "email": email,
            "phone": phone,
            "message": message,
            "source": source,
            "status": "new",
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.leads.insert_one(lead)
        
        # Try to send email notification
        try:
            from app.services.notification_service import NotificationService
            await NotificationService.notify_new_lead(workspace_id, lead)
        except Exception as e:
            print(f"Failed to send lead notification: {e}")
        
        return {
            "success": True,
            "leadId": lead_id,
            "message": "Thank you for your submission!"
        }
