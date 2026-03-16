"""Business Blueprint service with AI generation"""
import uuid
import os
import re
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.blueprint import (
    BlueprintCreate, BlueprintUpdate, BlueprintSectionType,
    SWOTAnalysis, FinancialProjection
)

# Try to import LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class BlueprintService:
    """Service for Business Blueprint generation"""

    TEMPLATE_VERSIONS: Dict[str, str] = {
        "business_plan": "template_v2",
    }

    @staticmethod
    def _normalize_business_name(name: str) -> str:
        return " ".join(str(name or "").strip().lower().split())
    
    SECTION_PROMPTS = {
        "executive_summary": """Generate a professional executive summary for a business plan.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Target Market: {target_market}
            Business Model: {business_model}
            
            Include: mission statement, value proposition, key success factors, and funding requirements.
            Keep it concise (300-400 words) and compelling for investors.""",
        
        "market_analysis": """Generate a comprehensive market analysis section.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Target Market: {target_market}
            
            Include: market size, growth trends, target customer segments, and market dynamics.
            Provide specific insights relevant to the industry.""",
        
        "products_services": """Generate a products and services section.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Business Model: {business_model}
            
            Include: core offerings, features and benefits, pricing strategy, and competitive advantages.""",
        
        "marketing_strategy": """Generate a marketing strategy section.
            Business: {business_name}
            Industry: {industry}
            Target Market: {target_market}
            Business Model: {business_model}
            
            Include: positioning, marketing channels, customer acquisition strategy, and brand messaging.""",
        
        "operations_plan": """Generate an operations plan section.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Business Model: {business_model}
            
            Include: operational workflow, key processes, resource requirements, and technology needs.""",
        
        "financial_projections": """Generate a financial projections narrative.
            Business: {business_name}
            Industry: {industry}
            Business Model: {business_model}
            Funding Goal: {funding_goal}
            
            Include: revenue model, cost structure, break-even analysis, and 3-year projection summary.""",
        
        "competitive_analysis": """Generate a competitive analysis section.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Target Market: {target_market}
            
            Include: key competitors, competitive landscape, differentiation strategy, and market positioning."""
    }

    DOCUMENT_LABELS: Dict[str, str] = {
        "business_plan": "Business Plan",
        "client_proposal": "Client Proposal",
        "sales_letter": "Sales Letter",
        "sales_quotation": "Sales Quotation",
        "cashflow_analysis": "Cashflow Analysis",
        "financial_projection": "Financial Projection",
    }

    DOCUMENT_REQUIREMENTS: Dict[str, List[Dict[str, str]]] = {
        "business_plan": [
            {"key": "businessName", "label": "Business name", "source": "state_or_input"},
            {"key": "problemSolved", "label": "Problem statement", "source": "state_or_input"},
            {"key": "customerSegment", "label": "Customer segment", "source": "state_or_input"},
            {"key": "serviceType", "label": "Service offer", "source": "state_or_input"},
            {"key": "priceAmount", "label": "Pricing amount", "source": "state_or_input"},
            {"key": "expectedUnitsPerMonth", "label": "Units per month", "source": "state_or_input"},
            {"key": "fixedMonthlyCosts", "label": "Fixed monthly costs", "source": "state_or_input"},
            {"key": "projectionYears", "label": "Projection years", "source": "input"},
            {"key": "growthRateAnnualPct", "label": "Annual growth assumption (%)", "source": "input"},
        ],
        "client_proposal": [
            {"key": "prospectName", "label": "Prospect name", "source": "input"},
            {"key": "serviceType", "label": "Service selected", "source": "state_or_input"},
            {"key": "deliverables", "label": "Deliverables", "source": "input"},
            {"key": "deliveryTimelineDays", "label": "Timeline (days)", "source": "input"},
            {"key": "priceAmount", "label": "Pricing", "source": "state_or_input"},
            {"key": "paymentTermsDays", "label": "Payment terms", "source": "state_or_input"},
        ],
        "sales_letter": [
            {"key": "targetRecipientType", "label": "Target recipient type", "source": "input"},
            {"key": "serviceType", "label": "Selected service", "source": "state_or_input"},
            {"key": "tonePreference", "label": "Tone preference", "source": "input"},
        ],
        "sales_quotation": [
            {"key": "clientName", "label": "Client name", "source": "input"},
            {"key": "servicePackage", "label": "Service package", "source": "input"},
            {"key": "validityDays", "label": "Validity period (days)", "source": "input"},
            {"key": "paymentSchedule", "label": "Payment schedule", "source": "input"},
            {"key": "priceAmount", "label": "Pricing", "source": "state_or_input"},
        ],
        "cashflow_analysis": [
            {"key": "analysisMonths", "label": "Analysis horizon (months)", "source": "input"},
            {"key": "expectedUnitsPerMonth", "label": "Units per month", "source": "state_or_input"},
            {"key": "priceAmount", "label": "Unit price", "source": "state_or_input"},
            {"key": "variableCostPerUnit", "label": "Variable cost per unit", "source": "state_or_input"},
            {"key": "fixedMonthlyCosts", "label": "Fixed monthly costs", "source": "state_or_input"},
        ],
        "financial_projection": [
            {"key": "projectionYears", "label": "Projection years", "source": "input"},
            {"key": "growthRateAnnualPct", "label": "Annual growth assumption (%)", "source": "input"},
            {"key": "costInflationAnnualPct", "label": "Cost inflation assumption (%)", "source": "input"},
            {"key": "expectedUnitsPerMonth", "label": "Units per month", "source": "state_or_input"},
            {"key": "priceAmount", "label": "Unit price", "source": "state_or_input"},
            {"key": "variableCostPerUnit", "label": "Variable cost per unit", "source": "state_or_input"},
            {"key": "fixedMonthlyCosts", "label": "Fixed monthly costs", "source": "state_or_input"},
        ],
    }

    DEFAULT_DOCUMENT_INPUTS: Dict[str, Dict[str, Any]] = {
        "business_plan": {
            "projectionYears": 3,
            "growthRateAnnualPct": 8,
        },
        "cashflow_analysis": {
            "analysisMonths": 12,
        },
        "financial_projection": {
            "projectionYears": 3,
            "growthRateAnnualPct": 8,
            "costInflationAnnualPct": 4,
        },
        "client_proposal": {
            "deliveryTimelineDays": 14,
        },
        "sales_letter": {
            "targetRecipientType": "customer",
            "tonePreference": "professional",
        },
        "sales_quotation": {
            "validityDays": 30,
            "paymentSchedule": "50% upfront, 50% on delivery",
        },
    }

    @staticmethod
    def _suggest_missing_inputs(state: dict, document_type: str, missing_fields: List[dict], existing_inputs: dict) -> dict:
        """
        Suggest values for input-only missing fields using existing validated state + safe defaults.
        This keeps deterministic generation while reducing unnecessary manual typing.
        """
        suggestions: Dict[str, Any] = {}

        defaults = BlueprintService.DEFAULT_DOCUMENT_INPUTS.get(document_type, {})
        for field in missing_fields or []:
            key = field.get("key")
            source = field.get("source")
            if not key or source not in ["input", "state_or_input"]:
                continue
            if BlueprintService._value_exists(existing_inputs.get(key)):
                continue
            if key in defaults:
                suggestions[key] = defaults[key]

        # Document-specific heuristics from state
        if document_type == "client_proposal":
            if not BlueprintService._value_exists(existing_inputs.get("deliverables")):
                service_type = (state.get("serviceModel", {}) or {}).get("serviceType")
                how_it_works = (state.get("serviceModel", {}) or {}).get("howItWorks")
                if BlueprintService._value_exists(service_type):
                    deliverables = [
                        f"- {service_type}: delivery as agreed",
                        "- Weekly progress update",
                        "- Handover + next-steps checklist",
                    ]
                    if BlueprintService._value_exists(how_it_works):
                        deliverables.insert(1, f"- Implementation approach: {how_it_works}")
                    suggestions["deliverables"] = "\n".join(deliverables)
        if document_type == "sales_quotation":
            if not BlueprintService._value_exists(existing_inputs.get("servicePackage")):
                service_type = (state.get("serviceModel", {}) or {}).get("serviceType")
                if BlueprintService._value_exists(service_type):
                    suggestions["servicePackage"] = str(service_type)
        if document_type == "sales_letter":
            if not BlueprintService._value_exists(existing_inputs.get("targetRecipientType")):
                audience = (state.get("customerSegment", {}) or {}).get("audience") or (state.get("customerSegment", {}) or {}).get("segment")
                if BlueprintService._value_exists(audience):
                    suggestions["targetRecipientType"] = str(audience)

        return suggestions
    
    @staticmethod
    async def create_blueprint(workspace_id: str, user_id: str, data: BlueprintCreate) -> dict:
        """Create a new business blueprint"""
        db = get_db()

        normalized_name = BlueprintService._normalize_business_name(data.businessName)
        if not normalized_name:
            raise HTTPException(status_code=422, detail="Business name is required")

        existing = await db.blueprints.find_one(
            {"workspace_id": workspace_id, "businessNameNormalized": normalized_name},
            {"_id": 0},
        )
        if not existing:
            escaped = re.escape(str(data.businessName or "").strip())
            existing = await db.blueprints.find_one(
                {"workspace_id": workspace_id, "businessName": {"$regex": f"^{escaped}$", "$options": "i"}},
                {"_id": 0},
            )
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "A blueprint with this business name already exists in this workspace",
                    "existingBlueprintId": existing.get("id"),
                },
            )
        
        blueprint_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        blueprint = {
            "id": blueprint_id,
            "workspace_id": workspace_id,
            "businessName": data.businessName,
            "businessNameNormalized": normalized_name,
            "industry": data.industry,
            "description": data.description,
            "targetMarket": data.targetMarket,
            "businessModel": data.businessModel,
            "fundingGoal": data.fundingGoal,
            "status": "draft",
            "sections": [],
            "swotAnalysis": None,
            "financialProjections": [],
            "created_by": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.blueprints.insert_one(blueprint)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "blueprint.created",
            "data": {"blueprint_id": blueprint_id, "business_name": data.businessName},
            "occurredAt": now
        })
        
        return {k: v for k, v in blueprint.items() if k != '_id'}
    
    @staticmethod
    async def get_blueprints(workspace_id: str) -> List[dict]:
        """Get all blueprints for a workspace"""
        db = get_db()
        
        blueprints = await db.blueprints.find(
            {"workspace_id": workspace_id}
        ).sort("createdAt", -1).to_list(length=100)
        
        return [{k: v for k, v in bp.items() if k != '_id'} for bp in blueprints]
    
    @staticmethod
    async def get_blueprint(blueprint_id: str, workspace_id: str) -> dict:
        """Get a specific blueprint"""
        db = get_db()
        
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        return {k: v for k, v in blueprint.items() if k != '_id'}
    
    @staticmethod
    async def generate_section(workspace_id: str, blueprint_id: str, section_type: str) -> dict:
        """Generate a specific section using AI"""
        db = get_db()
        
        # Get blueprint
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        # Generate content
        content = await BlueprintService._generate_with_ai(
            section_type,
            blueprint
        )
        
        # Create section
        section = {
            "sectionType": section_type,
            "title": BlueprintService._get_section_title(section_type),
            "content": content,
            "generatedAt": datetime.now(timezone.utc).isoformat()
        }
        
        # Update blueprint
        existing_sections = blueprint.get("sections", [])
        # Remove existing section of same type
        existing_sections = [s for s in existing_sections if s.get("sectionType") != section_type]
        existing_sections.append(section)
        
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {
                "$set": {
                    "sections": existing_sections,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return section
    
    @staticmethod
    async def generate_swot(workspace_id: str, blueprint_id: str) -> dict:
        """Generate SWOT analysis using AI"""
        db = get_db()
        
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        # Generate SWOT with AI
        swot = await BlueprintService._generate_swot_with_ai(blueprint)
        
        # Update blueprint
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {
                "$set": {
                    "swotAnalysis": swot,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return swot
    
    @staticmethod
    async def generate_financials(workspace_id: str, blueprint_id: str) -> List[dict]:
        """Generate financial projections"""
        db = get_db()
        
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        # Generate projections (simplified model)
        projections = BlueprintService._generate_financial_projections(
            blueprint.get("fundingGoal", 100000),
            blueprint.get("businessModel", "subscription")
        )
        
        # Update blueprint
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {
                "$set": {
                    "financialProjections": projections,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return projections
    
    @staticmethod
    async def generate_full_blueprint(workspace_id: str, blueprint_id: str) -> dict:
        """Generate all sections at once"""
        sections_to_generate = [
            "executive_summary",
            "market_analysis",
            "products_services",
            "marketing_strategy",
            "operations_plan",
            "financial_projections",
            "competitive_analysis"
        ]
        
        for section_type in sections_to_generate:
            await BlueprintService.generate_section(workspace_id, blueprint_id, section_type)
        
        # Generate SWOT
        await BlueprintService.generate_swot(workspace_id, blueprint_id)
        
        # Generate financials
        await BlueprintService.generate_financials(workspace_id, blueprint_id)
        
        # Update status
        db = get_db()
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {"$set": {"status": "complete", "updatedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        return await BlueprintService.get_blueprint(blueprint_id, workspace_id)
    
    @staticmethod
    async def update_blueprint(blueprint_id: str, workspace_id: str, data: BlueprintUpdate) -> dict:
        """Update a blueprint"""
        db = get_db()
        
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        update_data = data.model_dump(exclude_unset=True)

        if "businessName" in update_data:
            normalized_name = BlueprintService._normalize_business_name(update_data.get("businessName"))
            if not normalized_name:
                raise HTTPException(status_code=422, detail="Business name is required")

            existing = await db.blueprints.find_one(
                {
                    "workspace_id": workspace_id,
                    "businessNameNormalized": normalized_name,
                    "id": {"$ne": blueprint_id},
                },
                {"_id": 0},
            )
            if not existing:
                escaped = re.escape(str(update_data.get("businessName") or "").strip())
                existing = await db.blueprints.find_one(
                    {
                        "workspace_id": workspace_id,
                        "businessName": {"$regex": f"^{escaped}$", "$options": "i"},
                        "id": {"$ne": blueprint_id},
                    },
                    {"_id": 0},
                )
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "message": "A blueprint with this business name already exists in this workspace",
                        "existingBlueprintId": existing.get("id"),
                    },
                )

            update_data["businessNameNormalized"] = normalized_name
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
        
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {"$set": update_data}
        )
        
        return await BlueprintService.get_blueprint(blueprint_id, workspace_id)
    
    @staticmethod
    async def delete_blueprint(blueprint_id: str, workspace_id: str) -> bool:
        """Delete a blueprint"""
        db = get_db()
        
        result = await db.blueprints.delete_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        return result.deleted_count > 0
    
    # Module 2: Structured workflow endpoints
    @staticmethod
    async def get_eligibility(workspace_id: str, business_id: Optional[str] = None) -> dict:
        state = await BlueprintService._get_business_state(workspace_id, business_id)
        available = []
        partial = []
        missing = []
        for doc_type in BlueprintService.DOCUMENT_REQUIREMENTS.keys():
            readiness = await BlueprintService._evaluate_readiness(workspace_id, state, doc_type)
            if readiness["ready"]:
                available.append(readiness)
            elif readiness["completionPercent"] > 0:
                partial.append(readiness)
            else:
                missing.append(readiness)
        return {
            "businessId": state["businessId"],
            "available": available,
            "partial": partial,
            "missing": missing,
        }

    @staticmethod
    async def get_document_readiness(workspace_id: str, document_type: str, business_id: Optional[str] = None) -> dict:
        state = await BlueprintService._get_business_state(workspace_id, business_id)
        return await BlueprintService._evaluate_readiness(workspace_id, state, document_type)

    @staticmethod
    async def save_document_inputs(
        workspace_id: str,
        user_id: str,
        document_type: str,
        inputs: dict,
        provenance: Optional[dict] = None,
        business_id: Optional[str] = None,
    ) -> dict:
        db = get_db()
        state = await BlueprintService._get_business_state(workspace_id, business_id)
        now = datetime.now(timezone.utc).isoformat()
        existing = await db.blueprint_document_inputs.find_one({
            "workspace_id": workspace_id,
            "business_id": state["businessId"],
            "document_type": document_type,
        })
        payload = {
            "workspace_id": workspace_id,
            "business_id": state["businessId"],
            "document_type": document_type,
            "inputs": inputs or {},
            "provenance": provenance or {},
            "updated_by": user_id,
            "updated_at": now,
        }
        if existing:
            await db.blueprint_document_inputs.update_one({"id": existing["id"]}, {"$set": payload})
            entry_id = existing["id"]
        else:
            entry_id = str(uuid.uuid4())
            payload.update({
                "id": entry_id,
                "created_by": user_id,
                "created_at": now,
            })
            await db.blueprint_document_inputs.insert_one(payload)

        readiness = await BlueprintService._evaluate_readiness(workspace_id, state, document_type)
        return {
            "id": entry_id,
            "businessId": state["businessId"],
            "documentType": document_type,
            "inputs": inputs or {},
            "readiness": readiness,
        }

    @staticmethod
    async def generate_module2_document(
        workspace_id: str,
        user_id: str,
        document_type: str,
        business_id: Optional[str] = None,
        regenerate: bool = False,
    ) -> dict:
        db = get_db()
        template_version = BlueprintService.TEMPLATE_VERSIONS.get(document_type, "template_v1")
        state = await BlueprintService._get_business_state(workspace_id, business_id)
        readiness = await BlueprintService._evaluate_readiness(workspace_id, state, document_type)
        if not readiness["ready"]:
            doc_inputs = await BlueprintService._get_effective_document_inputs(workspace_id, state["businessId"], document_type)
            suggested_inputs = BlueprintService._suggest_missing_inputs(
                state=state,
                document_type=document_type,
                missing_fields=readiness.get("missingFields", []),
                existing_inputs=doc_inputs,
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"{BlueprintService.DOCUMENT_LABELS.get(document_type, document_type)} is not ready",
                    "missingFields": readiness.get("missingFields", []),
                    "suggestedInputs": suggested_inputs,
                },
            )

        doc_inputs = await BlueprintService._get_effective_document_inputs(workspace_id, state["businessId"], document_type)
        hydrated_state = BlueprintService._hydrate_state_from_document_context(state, doc_inputs)
        blueprint_data = BlueprintService._assemble_blueprint_data_object(hydrated_state, doc_inputs)
        financial_summary = BlueprintService._run_financial_engine(document_type, blueprint_data)
        sections = BlueprintService._build_template_sections(document_type, blueprint_data, financial_summary)
        sections = await BlueprintService._rewrite_sections_for_tone(document_type, sections, blueprint_data)
        validation = BlueprintService._validate_document_integrity(document_type, sections, blueprint_data, financial_summary)
        if not validation["ok"]:
            raise HTTPException(status_code=422, detail={"message": "Document validation failed", "errors": validation["errors"]})

        rendered_html = BlueprintService._render_document_html(
            title=BlueprintService.DOCUMENT_LABELS.get(document_type, document_type.replace("_", " ").title()),
            sections=sections,
        )
        now = datetime.now(timezone.utc).isoformat()

        existing = await db.blueprint_documents.find_one({
            "workspace_id": workspace_id,
            "business_id": state["businessId"],
            "document_type": document_type,
        })
        version_entry = {
            "version": 1,
            "createdAt": now,
            "sourceStateVersion": state["sourceStateVersion"],
            "templateVersion": template_version,
            "llmGenerationVersion": "llm_rewrite_v1",
        }

        if existing:
            versions = existing.get("versions", [])
            next_version = (versions[-1]["version"] if versions else 0) + 1
            version_entry["version"] = next_version
            await db.blueprint_documents.update_one(
                {"id": existing["id"]},
                {
                    "$set": {
                        "title": BlueprintService.DOCUMENT_LABELS.get(document_type, document_type),
                        "status": "draft",
                        "renderedHtml": rendered_html,
                        "sections": sections,
                        "sourceStateVersion": state["sourceStateVersion"],
                        "templateVersion": template_version,
                        "llmGenerationVersion": "llm_rewrite_v1",
                        "sourceData": blueprint_data,
                        "financialSummary": financial_summary,
                        "updatedAt": now,
                    },
                    "$push": {"versions": version_entry},
                },
            )
            document_id = existing["id"]
        else:
            document_id = str(uuid.uuid4())
            await db.blueprint_documents.insert_one({
                "id": document_id,
                "workspace_id": workspace_id,
                "business_id": state["businessId"],
                "document_type": document_type,
                "title": BlueprintService.DOCUMENT_LABELS.get(document_type, document_type),
                "status": "draft",
                "renderedHtml": rendered_html,
                "sections": sections,
                "sourceStateVersion": state["sourceStateVersion"],
                "templateVersion": template_version,
                "llmGenerationVersion": "llm_rewrite_v1",
                "sourceData": blueprint_data,
                "financialSummary": financial_summary,
                "versions": [version_entry],
                "createdBy": user_id,
                "createdAt": now,
                "updatedAt": now,
            })

        doc = await db.blueprint_documents.find_one({"id": document_id}, {"_id": 0})
        return BlueprintService._normalize_document_response(doc)

    @staticmethod
    async def get_document(workspace_id: str, document_id: str) -> dict:
        db = get_db()
        doc = await db.blueprint_documents.find_one(
            {"id": document_id, "workspace_id": workspace_id},
            {"_id": 0},
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Blueprint document not found")
        return BlueprintService._normalize_document_response(doc)

    @staticmethod
    async def update_document_section(
        workspace_id: str,
        user_id: str,
        document_id: str,
        section_id: str,
        content: str,
    ) -> dict:
        db = get_db()
        doc = await db.blueprint_documents.find_one(
            {"id": document_id, "workspace_id": workspace_id},
            {"_id": 0},
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Blueprint document not found")
        sections = doc.get("sections", [])
        updated = False
        for section in sections:
            if section.get("id") == section_id:
                section["content"] = content
                updated = True
                break
        if not updated:
            raise HTTPException(status_code=404, detail="Section not found")
        now = datetime.now(timezone.utc).isoformat()
        versions = doc.get("versions", [])
        next_version = (versions[-1]["version"] if versions else 0) + 1
        version_entry = {
            "version": next_version,
            "createdAt": now,
            "sourceStateVersion": doc.get("sourceStateVersion", "state_v1"),
            "templateVersion": doc.get("templateVersion", "template_v1"),
            "llmGenerationVersion": "manual_edit_v1",
        }
        await db.blueprint_documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "sections": sections,
                    "renderedHtml": BlueprintService._render_document_html(doc.get("title", "Document"), sections),
                    "updatedAt": now,
                    "updatedBy": user_id,
                },
                "$push": {"versions": version_entry},
            },
        )
        updated_doc = await db.blueprint_documents.find_one({"id": document_id}, {"_id": 0})
        return BlueprintService._normalize_document_response(updated_doc)

    @staticmethod
    async def regenerate_document_section(workspace_id: str, document_id: str, section_id: str) -> dict:
        db = get_db()
        doc = await db.blueprint_documents.find_one(
            {"id": document_id, "workspace_id": workspace_id},
            {"_id": 0},
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Blueprint document not found")
        source_data = doc.get("sourceData") or {}
        financial_summary = doc.get("financialSummary") or {}
        regenerated_sections = BlueprintService._build_template_sections(
            doc.get("document_type"),
            source_data,
            financial_summary,
        )
        updated_section = None
        for section in regenerated_sections:
            if section.get("id") == section_id:
                updated_section = section
                break
        if not updated_section:
            raise HTTPException(status_code=404, detail="Section not found")
        sections = doc.get("sections", [])
        for idx, existing in enumerate(sections):
            if existing.get("id") == section_id:
                sections[idx] = updated_section
                break
        now = datetime.now(timezone.utc).isoformat()
        versions = doc.get("versions", [])
        next_version = (versions[-1]["version"] if versions else 0) + 1
        version_entry = {
            "version": next_version,
            "createdAt": now,
            "sourceStateVersion": doc.get("sourceStateVersion", "state_v1"),
            "templateVersion": doc.get("templateVersion", "template_v1"),
            "llmGenerationVersion": "section_regen_v1",
        }
        await db.blueprint_documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "sections": sections,
                    "renderedHtml": BlueprintService._render_document_html(doc.get("title", "Document"), sections),
                    "updatedAt": now,
                },
                "$push": {"versions": version_entry},
            },
        )
        updated_doc = await db.blueprint_documents.find_one({"id": document_id}, {"_id": 0})
        return BlueprintService._normalize_document_response(updated_doc)

    @staticmethod
    async def duplicate_document(workspace_id: str, user_id: str, document_id: str) -> dict:
        db = get_db()
        source = await db.blueprint_documents.find_one(
            {"id": document_id, "workspace_id": workspace_id},
            {"_id": 0},
        )
        if not source:
            raise HTTPException(status_code=404, detail="Blueprint document not found")
        now = datetime.now(timezone.utc).isoformat()
        duplicate_id = str(uuid.uuid4())
        source["id"] = duplicate_id
        source["title"] = f'{source.get("title", "Document")} (Copy)'
        source["createdBy"] = user_id
        source["createdAt"] = now
        source["updatedAt"] = now
        source["versions"] = [{
            "version": 1,
            "createdAt": now,
            "sourceStateVersion": source.get("sourceStateVersion", "state_v1"),
            "templateVersion": source.get("templateVersion", "template_v1"),
            "llmGenerationVersion": source.get("llmGenerationVersion", "llm_rewrite_v1"),
        }]
        await db.blueprint_documents.insert_one(source)
        return BlueprintService._normalize_document_response(source)

    @staticmethod
    async def export_document(workspace_id: str, document_id: str, export_format: str) -> dict:
        doc = await BlueprintService.get_document(workspace_id, document_id)
        if export_format.lower() == "html":
            return {"format": "html", "content": doc.get("renderedHtml", "")}
        if export_format.lower() == "text":
            lines = [doc.get("title", "")]
            for section in doc.get("sections", []):
                lines.append("")
                lines.append(section.get("title", ""))
                lines.append(section.get("content", ""))
            return {"format": "text", "content": "\n".join(lines)}
        raise HTTPException(status_code=400, detail="Unsupported export format")

    # Helper methods
    @staticmethod
    async def _get_business_state(workspace_id: str, business_id: Optional[str] = None) -> dict:
        db = get_db()
        report = None
        if business_id:
            report = await db.validation_reports.find_one(
                {"workspace_id": workspace_id, "id": business_id},
                {"_id": 0},
            )
        if not report:
            report = await db.validation_reports.find_one(
                {"workspace_id": workspace_id, "status": "accepted"},
                {"_id": 0},
                sort=[("updatedAt", -1), ("createdAt", -1)],
            )
        if not report:
            report = await db.validation_reports.find_one(
                {"workspace_id": workspace_id},
                {"_id": 0},
                sort=[("updatedAt", -1), ("createdAt", -1)],
            )
        if not report:
            raise HTTPException(status_code=404, detail="No idea validation record found for this workspace")

        idea_input = report.get("ideaInput", {}) or {}
        company_profile = await db.company_profiles.find_one({"workspaceId": workspace_id}, {"_id": 0})
        business_name = (
            idea_input.get("businessName")
            or idea_input.get("ideaName")
            or (company_profile or {}).get("legalName")
            or "Untitled Business"
        )
        return {
            "businessId": report.get("id"),
            "sourceStateVersion": report.get("updatedAt") or report.get("createdAt") or datetime.now(timezone.utc).isoformat(),
            "businessProfile": {
                "businessName": business_name,
                "description": idea_input.get("whatYouAreBuilding") or idea_input.get("ideaDescription"),
                "industry": idea_input.get("industry"),
                "location": idea_input.get("targetLocation"),
                "targetMarket": idea_input.get("targetMarket"),
            },
            "customerSegment": {
                "customerSegment": idea_input.get("customerSegment"),
                "segment": idea_input.get("customerSegment"),
                "audience": idea_input.get("targetAudience"),
                "problemSolved": idea_input.get("problemSolved"),
                "urgency": idea_input.get("urgencyLevel"),
            },
            "serviceModel": {
                "serviceType": idea_input.get("serviceType"),
                "howItWorks": idea_input.get("howItWorks"),
                "deliveryModel": idea_input.get("deliveryModel"),
            },
            "pricingModel": {
                "pricingModel": idea_input.get("pricingModel"),
                "priceAmount": idea_input.get("priceAmount"),
                "paymentTermsDays": idea_input.get("paymentTermsDays"),
                "deliverableUnit": idea_input.get("deliverableUnit"),
            },
            "costStructure": {
                "variableCostPerUnit": idea_input.get("variableCostPerUnit"),
                "fixedMonthlyCosts": idea_input.get("fixedMonthlyCosts"),
                "founderDrawMonthly": idea_input.get("founderDrawMonthly"),
                "contractorCostsMonthly": idea_input.get("contractorCostsMonthly"),
            },
            "baselineMetrics": {
                "expectedUnitsPerMonth": idea_input.get("expectedUnitsPerMonth"),
                "expectedCustomers": idea_input.get("expectedCustomers"),
                "salesCycleDays": idea_input.get("salesCycleDays"),
                "staffCount": idea_input.get("staffCount"),
                "capacityPerStaffPerMonth": idea_input.get("capacityPerStaffPerMonth"),
            },
            "scenarioResults": report.get("report", {}).get("decisionSimulation") or {},
            "companyProfile": company_profile or {},
        }

    @staticmethod
    async def _get_document_inputs(workspace_id: str, business_id: str, document_type: str) -> dict:
        db = get_db()
        entry = await db.blueprint_document_inputs.find_one(
            {
                "workspace_id": workspace_id,
                "business_id": business_id,
                "document_type": document_type,
            },
            {"_id": 0},
        )
        return (entry or {}).get("inputs", {}) or {}

    @staticmethod
    def _apply_document_input_defaults(document_type: str, inputs: Optional[dict]) -> dict:
        """
        Merge safe defaults for a given document type without overwriting user-provided values.
        Treat empty strings as missing so defaults can apply.
        """
        base = dict(BlueprintService.DEFAULT_DOCUMENT_INPUTS.get(document_type, {}) or {})
        incoming = inputs or {}
        for key, value in incoming.items():
            if BlueprintService._value_exists(value):
                base[key] = value
        return base

    @staticmethod
    async def _get_effective_document_inputs(workspace_id: str, business_id: str, document_type: str) -> dict:
        stored = await BlueprintService._get_document_inputs(workspace_id, business_id, document_type)
        return BlueprintService._apply_document_input_defaults(document_type, stored)

    @staticmethod
    async def _evaluate_readiness(workspace_id: str, state: dict, document_type: str) -> dict:
        requirements = BlueprintService.DOCUMENT_REQUIREMENTS.get(document_type, [])
        doc_inputs = await BlueprintService._get_effective_document_inputs(workspace_id, state["businessId"], document_type)

        def get_value(key: str, source: str):
            if source == "input":
                return doc_inputs.get(key)
            if source == "state_or_input":
                state_value = BlueprintService._extract_from_state(state, key)
                return state_value if state_value not in [None, "", []] else doc_inputs.get(key)
            return BlueprintService._extract_from_state(state, key)

        missing_fields = []
        filled = 0
        for requirement in requirements:
            value = get_value(requirement["key"], requirement["source"])
            if BlueprintService._value_exists(value):
                filled += 1
            else:
                missing_fields.append(requirement)
        completion = int((filled / len(requirements)) * 100) if requirements else 100
        return {
            "documentType": document_type,
            "label": BlueprintService.DOCUMENT_LABELS.get(document_type, document_type),
            "ready": len(missing_fields) == 0,
            "missingFields": missing_fields,
            "completionPercent": completion,
        }

    @staticmethod
    def _extract_from_state(state: dict, key: str) -> Any:
        maps = [
            state.get("businessProfile", {}),
            state.get("customerSegment", {}),
            state.get("serviceModel", {}),
            state.get("pricingModel", {}),
            state.get("costStructure", {}),
            state.get("baselineMetrics", {}),
            state.get("scenarioResults", {}),
            state.get("companyProfile", {}),
        ]
        for obj in maps:
            if key in obj and obj[key] not in [None, ""]:
                return obj[key]
        return None

    @staticmethod
    def _value_exists(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() != ""
        if isinstance(value, list):
            return len(value) > 0
        return True

    @staticmethod
    def _hydrate_state_from_document_context(state: dict, document_context: dict) -> dict:
        """
        Allow module2 document inputs to satisfy generation even when upstream modules
        (business registration / idea validation) haven't provided a field yet.
        This does NOT overwrite existing state values.
        """
        hydrated = dict(state or {})
        ctx = document_context or {}
        mapping = {
            "businessName": ("businessProfile", "businessName"),
            "problemSolved": ("businessProfile", "problemSolved"),
            "customerSegment": ("customerSegment", "customerSegment"),
            "serviceType": ("serviceModel", "serviceType"),
            "priceAmount": ("pricingModel", "priceAmount"),
            "expectedUnitsPerMonth": ("baselineMetrics", "expectedUnitsPerMonth"),
            "fixedMonthlyCosts": ("costStructure", "fixedMonthlyCosts"),
            "variableCostPerUnit": ("costStructure", "variableCostPerUnit"),
            "paymentTermsDays": ("pricingModel", "paymentTermsDays"),
        }

        for ctx_key, (state_section, state_key) in mapping.items():
            value = ctx.get(ctx_key)
            if not BlueprintService._value_exists(value):
                continue
            section_obj = dict(hydrated.get(state_section, {}) or {})
            if BlueprintService._value_exists(section_obj.get(state_key)):
                continue
            section_obj[state_key] = value
            hydrated[state_section] = section_obj

        return hydrated

    @staticmethod
    def _assemble_blueprint_data_object(state: dict, document_context: dict) -> dict:
        return {
            "business_profile": state.get("businessProfile", {}),
            "customer_segment": state.get("customerSegment", {}),
            "service_model": state.get("serviceModel", {}),
            "pricing_model": state.get("pricingModel", {}),
            "cost_structure": state.get("costStructure", {}),
            "baseline_metrics": state.get("baselineMetrics", {}),
            "scenario_results": state.get("scenarioResults", {}),
            "company_profile": state.get("companyProfile", {}),
            "document_context": document_context or {},
        }

    @staticmethod
    def _get_section_title(section_type: str) -> str:
        titles = {
            "executive_summary": "Executive Summary",
            "market_analysis": "Market Analysis",
            "products_services": "Products & Services",
            "marketing_strategy": "Marketing Strategy",
            "operations_plan": "Operations Plan",
            "financial_projections": "Financial Projections",
            "competitive_analysis": "Competitive Analysis",
            "swot_analysis": "SWOT Analysis"
        }
        return titles.get(section_type, section_type.replace("_", " ").title())

    @staticmethod
    def _run_financial_engine(document_type: str, data: dict) -> dict:
        requires_financials = document_type in {
            "business_plan",
            "cashflow_analysis",
            "financial_projection",
        }
        if not requires_financials:
            return {}

        pricing = data.get("pricing_model", {})
        costs = data.get("cost_structure", {})
        baseline = data.get("baseline_metrics", {})
        doc_ctx = data.get("document_context", {})

        price = BlueprintService._to_float(pricing.get("priceAmount"))
        units = BlueprintService._to_float(baseline.get("expectedUnitsPerMonth"))
        variable = BlueprintService._to_float(costs.get("variableCostPerUnit"))
        fixed = (
            BlueprintService._to_float(costs.get("fixedMonthlyCosts"))
            + BlueprintService._to_float(costs.get("founderDrawMonthly"))
            + BlueprintService._to_float(costs.get("contractorCostsMonthly"))
        )
        projection_years = int(BlueprintService._to_float(doc_ctx.get("projectionYears"), default=1))
        projection_years = projection_years if projection_years in [1, 2, 3, 5] else 1
        analysis_months = int(BlueprintService._to_float(doc_ctx.get("analysisMonths"), default=12))
        analysis_months = max(1, min(60, analysis_months))
        growth_annual_pct = BlueprintService._to_float(doc_ctx.get("growthRateAnnualPct"), default=8)
        inflation_annual_pct = BlueprintService._to_float(doc_ctx.get("costInflationAnnualPct"), default=4)
        monthly_growth = ((1 + (growth_annual_pct / 100)) ** (1 / 12)) - 1
        monthly_inflation = ((1 + (inflation_annual_pct / 100)) ** (1 / 12)) - 1

        monthly_rows = []
        cash_position = 0.0
        for month in range(1, analysis_months + 1):
            growth_factor = (1 + monthly_growth) ** (month - 1)
            inflation_factor = (1 + monthly_inflation) ** (month - 1)
            monthly_revenue = price * units * growth_factor
            monthly_variable = variable * units * inflation_factor
            monthly_fixed = fixed * inflation_factor
            monthly_net = monthly_revenue - monthly_variable - monthly_fixed
            cash_position += monthly_net
            monthly_rows.append({
                "month": month,
                "revenue": round(monthly_revenue, 2),
                "variableCosts": round(monthly_variable, 2),
                "fixedCosts": round(monthly_fixed, 2),
                "netCashflow": round(monthly_net, 2),
                "cashPosition": round(cash_position, 2),
            })

        annual_projection = []
        for year in range(1, projection_years + 1):
            months = monthly_rows[(year - 1) * 12: year * 12]
            if not months:
                break
            rev = sum(m["revenue"] for m in months)
            var_cost = sum(m["variableCosts"] for m in months)
            fix_cost = sum(m["fixedCosts"] for m in months)
            annual_projection.append({
                "year": year,
                "revenue": round(rev, 2),
                "totalCosts": round(var_cost + fix_cost, 2),
                "netIncome": round(rev - var_cost - fix_cost, 2),
            })

        monthly_revenue_base = price * units
        monthly_variable_base = variable * units
        monthly_net_base = monthly_revenue_base - monthly_variable_base - fixed
        break_even_revenue = fixed / (1 - (variable / price)) if price > variable and price > 0 else None
        return {
            "inputs": {
                "priceAmount": price,
                "unitsPerMonth": units,
                "variableCostPerUnit": variable,
                "fixedMonthlyCosts": fixed,
                "projectionYears": projection_years,
                "analysisMonths": analysis_months,
                "growthRateAnnualPct": growth_annual_pct,
                "costInflationAnnualPct": inflation_annual_pct,
            },
            "base": {
                "monthlyRevenue": round(monthly_revenue_base, 2),
                "monthlyVariableCosts": round(monthly_variable_base, 2),
                "monthlyNet": round(monthly_net_base, 2),
                "breakEvenRevenue": round(break_even_revenue, 2) if break_even_revenue is not None else None,
            },
            "monthlyRows": monthly_rows,
            "annualProjection": annual_projection,
        }

    @staticmethod
    def _build_template_sections(document_type: str, data: dict, financial: dict) -> List[dict]:
        bp = data.get("business_profile", {})
        cs = data.get("customer_segment", {})
        sm = data.get("service_model", {})
        pm = data.get("pricing_model", {})
        cp = data.get("company_profile", {})
        ctx = data.get("document_context", {})
        currency = BlueprintService._currency_symbol(bp.get("location"))

        if document_type == "business_plan":
            official = (cp.get("officialProfile") or {}) if isinstance(cp, dict) else {}
            operating = (cp.get("operatingProfile") or {}) if isinstance(cp, dict) else {}
            derived = (cp.get("derivedProfile") or {}) if isinstance(cp, dict) else {}
            registration_data = (cp.get("registrationData") or {}) if isinstance(cp, dict) else {}

            entity_type = (cp.get("entityType") if isinstance(cp, dict) else None) or "Not specified"
            company_number = official.get("companyNumber") or registration_data.get("companyNumber") or "Not specified"
            vat_number = registration_data.get("vatNumber") or registration_data.get("vat_number") or "Not specified"

            business_name = bp.get("businessName", "Business")
            location = bp.get("location") or operating.get("tradingAddress") or "Not specified"
            industry = operating.get("industry") or bp.get("industry") or "Not specified"

            funding_goal = cp.get("fundingGoal") if isinstance(cp, dict) else None
            funding_text = (
                f"The request: {BlueprintService._money(funding_goal, currency)} (state how it will be used)."
                if BlueprintService._value_exists(funding_goal)
                else "The request: If seeking funding, state the amount required and how it will be used."
            )

            mission_sentence = (
                derived.get("elevatorPitch")
                or derived.get("tagline")
                or f"{business_name} helps {cs.get('audience') or cs.get('segment') or 'customers'} by delivering {sm.get('serviceType') or 'a solution'}."
            )

            hook_sentence = (
                f"Why this wins: a focused offer, clear delivery model ({sm.get('deliveryModel') or 'Not specified'}), and disciplined unit economics."
            )

            pricing_sentence = (
                f"Pricing strategy: {BlueprintService._money(pm.get('priceAmount'), currency)} per {pm.get('deliverableUnit') or 'unit'} "
                f"({pm.get('pricingModel') or 'pricing model not specified'}). VAT: {('TBD' if vat_number == 'Not specified' else 'consider VAT implications')}."
            )

            financial_plan_parts = [
                "Sales forecast (12–36 months):",
                BlueprintService._projection_text(financial, currency),
                "Cash flow statement (monthly):",
                BlueprintService._cashflow_text(financial, currency),
            ]
            break_even = (financial or {}).get("base", {}).get("breakEvenRevenue")
            if break_even is not None:
                financial_plan_parts.append(
                    f"Break-even analysis: estimated break-even revenue per month is {BlueprintService._money(break_even, currency)}."
                )
            financial_plan_text = "\n".join([p for p in financial_plan_parts if str(p).strip()])

            sections = [
                ("executive_summary", "Executive Summary", "\n".join([
                    f"The mission: {mission_sentence}",
                    f"The hook: {hook_sentence}",
                    funding_text,
                ])),
                ("business_overview", "Business Overview", "\n".join([
                    f"Legal structure: {entity_type}.",
                    f"Registration: Companies House number: {company_number}. VAT number: {vat_number}.",
                    f"Location: {location}.",
                    f"Industry: {industry}.",
                ])),
                ("market_analysis", "Market Analysis", "\n".join([
                    "UK lenders love data. Show the gap in the market with evidence.",
                    f"Target audience: {cs.get('audience') or 'Not specified'} (segment: {cs.get('segment') or 'Not specified'}).",
                    "Competitor analysis: identify local and national competitors and quantify your differentiation.",
                    "Market trends: include UK-specific trends impacting demand/costs (e.g., regulation, consumer behaviour, supply chain shifts).",
                ])),
                ("products_services", "Products and Services", "\n".join([
                    f"The problem: {cs.get('problemSolved') or 'Not specified'}.",
                    f"The solution: {sm.get('serviceType') or 'Not specified'} delivered via {sm.get('deliveryModel') or 'Not specified'}.",
                    f"Detail: {sm.get('howItWorks') or 'Not specified'}.",
                    pricing_sentence,
                ])),
                ("sales_marketing", "Sales and Marketing", "\n".join([
                    f"Branding: {business_name} (tone: {derived.get('tone') or 'Not specified'}).",
                    f"Channels: {operating.get('website') or 'Website not specified'}; outbound, referrals, partnerships, and relevant marketplaces where applicable.",
                    "Marketing strategy: combine local SEO, content, targeted ads, and networking; track conversion rate, CAC, and retention.",
                ])),
                ("operational_plan", "Operational Plan", "\n".join([
                    "Suppliers: list key suppliers and whether they are UK-based or international.",
                    "Technology: list core tools (e.g., accounting tools like Xero/FreeAgent, CRM, invoicing, analytics).",
                    "Insurance: confirm appropriate coverage (e.g., Public Liability, Professional Indemnity).",
                ])),
                ("management_personnel", "Management and Personnel", "\n".join([
                    "The team: summarise the founder(s) and relevant experience that supports execution.",
                    "Hiring: define when to use contractors vs PAYE employees (note IR35 considerations for contractors).",
                ])),
                ("financial_plan", "Financial Plan", financial_plan_text),
                ("risk_analysis", "Risk Analysis", "\n".join([
                    "Market risks; financial risks; operational risks; regulatory risks.",
                    "Mitigation: monitor monthly cashflow, maintain pipeline coverage, and adjust pricing/capacity based on variance.",
                ])),
                ("growth_strategy", "Growth Strategy", "\n".join([
                    "Market expansion plans; product development roadmap; strategic partnerships; technology adoption; hiring and operational expansion.",
                ])),
                ("conclusion", "Conclusion", "Summary and next steps to persuade stakeholders to support the plan."),
            ]
        elif document_type == "client_proposal":
            sections = [
                ("proposal_intro", "Proposal Summary", (
                    f'Prepared for {ctx.get("prospectName", "the client")}: {sm.get("serviceType", "service")} for {cs.get("segment", "target customers")} in {bp.get("location", "target location")}.'
                )),
                ("scope_deliverables", "Scope and Deliverables", ctx.get("deliverables", "Deliverables to be finalized with client requirements.")),
                ("timeline", "Timeline", f'Estimated delivery timeline: {ctx.get("deliveryTimelineDays", "N/A")} days.'),
                ("commercials", "Commercials", (
                    f'Price: {BlueprintService._money(pm.get("priceAmount"), currency)} ({pm.get("pricingModel", "pricing model")}); '
                    f'payment terms: {pm.get("paymentTermsDays") or ctx.get("paymentTermsDays") or "N/A"} days.'
                )),
                ("next_steps", "Next Steps", "Confirm scope, sign agreement, and schedule kickoff."),
            ]
        elif document_type == "sales_letter":
            sections = [
                ("opening", "Opening", (
                    f'To {ctx.get("targetRecipientType", "target customers")}: {bp.get("businessName", "we")} helps you solve {cs.get("problemSolved", "a recurring operational issue")}.'
                )),
                ("offer", "Offer", (
                    f'Offer: {sm.get("serviceType", "service")} delivered as {sm.get("deliveryModel", "delivery model")} with clear service outcomes.'
                )),
                ("cta", "Call to Action", "Reply to book a short discovery call and confirm fit."),
            ]
        elif document_type == "sales_quotation":
            sections = [
                ("recipient", "Recipient", f'Client: {ctx.get("clientName", "N/A")}'),
                ("quotation_details", "Quotation Details", (
                    f'Service package: {ctx.get("servicePackage", sm.get("serviceType", "N/A"))}; '
                    f'validity: {ctx.get("validityDays", "N/A")} days; payment schedule: {ctx.get("paymentSchedule", "N/A")}.'
                )),
                ("pricing", "Pricing", (
                    f'Quoted price: {BlueprintService._money(pm.get("priceAmount"), currency)} per {pm.get("deliverableUnit", "unit")} '
                    f'({pm.get("pricingModel", "pricing model")}).'
                )),
                ("terms", "Terms", f'Payment terms: {pm.get("paymentTermsDays") or ctx.get("paymentTermsDays") or "N/A"} days.'),
            ]
        elif document_type == "cashflow_analysis":
            sections = [
                ("summary", "Cashflow Summary", BlueprintService._cashflow_text(financial, currency)),
                ("monthly", "Monthly Inflow and Outflow", BlueprintService._monthly_table_text(financial, currency, rows=6)),
                ("liquidity", "Liquidity Commentary", BlueprintService._liquidity_text(financial, currency)),
            ]
        elif document_type == "financial_projection":
            sections = [
                ("assumptions", "Projection Assumptions", (
                    f'Projection years: {financial.get("inputs", {}).get("projectionYears", 1)}; growth: '
                    f'{financial.get("inputs", {}).get("growthRateAnnualPct", 0)}% annually; cost inflation: '
                    f'{financial.get("inputs", {}).get("costInflationAnnualPct", 0)}% annually.'
                )),
                ("yearly_projection", "Year by Year Projection", BlueprintService._projection_text(financial, currency)),
                ("interpretation", "Interpretation", "Review annual net income trend and adjust pricing, volume, or cost assumptions before scaling."),
            ]
        else:
            sections = [("document", "Document", "Template not configured.")]

        return [{"id": sid, "title": title, "content": content, "editable": True} for sid, title, content in sections]

    @staticmethod
    async def _rewrite_sections_for_tone(document_type: str, sections: List[dict], data: dict) -> List[dict]:
        cleaned = []
        for section in sections:
            text = str(section.get("content", "")).strip()
            text = " ".join(text.split())
            cleaned.append({**section, "content": text})
        return cleaned

    @staticmethod
    def _validate_document_integrity(document_type: str, sections: List[dict], data: dict, financial: dict) -> dict:
        errors = []
        if not sections:
            errors.append("No sections generated.")
        for section in sections:
            if not str(section.get("content", "")).strip():
                errors.append(f'Empty section: {section.get("title", "unknown")}')
        if document_type in ["business_plan", "cashflow_analysis", "financial_projection"]:
            if not financial or not financial.get("base"):
                errors.append("Financial engine output missing.")
        return {"ok": len(errors) == 0, "errors": errors}

    @staticmethod
    def _render_document_html(title: str, sections: List[dict]) -> str:
        body_parts = []
        for section in sections:
            body_parts.append(
                f'<section data-section-id="{section.get("id")}"><h3>{section.get("title")}</h3><p>{section.get("content")}</p></section>'
            )
        return f"<article><h1>{title}</h1>{''.join(body_parts)}</article>"

    @staticmethod
    def _normalize_document_response(doc: dict) -> dict:
        if not doc:
            return {}
        return {
            "id": doc.get("id"),
            "workspaceId": doc.get("workspace_id"),
            "businessId": doc.get("business_id"),
            "documentType": doc.get("document_type"),
            "title": doc.get("title"),
            "status": doc.get("status", "draft"),
            "renderedHtml": doc.get("renderedHtml", ""),
            "sections": doc.get("sections", []),
            "sourceStateVersion": doc.get("sourceStateVersion", ""),
            "templateVersion": doc.get("templateVersion", "template_v1"),
            "llmGenerationVersion": doc.get("llmGenerationVersion", "llm_rewrite_v1"),
            "versions": doc.get("versions", []),
            "createdBy": doc.get("createdBy"),
            "createdAt": doc.get("createdAt"),
            "updatedAt": doc.get("updatedAt"),
        }

    @staticmethod
    def _currency_symbol(location: Optional[str]) -> str:
        loc = (location or "").strip().lower()
        if loc in ["us", "usa", "united states"]:
            return "$"
        return "GBP"

    @staticmethod
    def _money(value: Any, currency: str) -> str:
        number = BlueprintService._to_float(value)
        symbol = "£" if currency == "GBP" else "$"
        return f"{symbol}{number:,.2f}"

    @staticmethod
    def _to_float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or value == "":
                return float(default)
            return float(value)
        except Exception:
            return float(default)

    @staticmethod
    def _cashflow_text(financial: dict, currency: str) -> str:
        if not financial:
            return "Cashflow summary unavailable."
        base = financial.get("base", {})
        break_even = base.get("breakEvenRevenue")
        break_even_text = BlueprintService._money(break_even, currency) if break_even is not None else "not reachable with current inputs"
        return (
            f'Monthly revenue is {BlueprintService._money(base.get("monthlyRevenue"), currency)}, '
            f'variable costs are {BlueprintService._money(base.get("monthlyVariableCosts"), currency)}, '
            f'and monthly net is {BlueprintService._money(base.get("monthlyNet"), currency)}. '
            f'Break-even revenue is {break_even_text}.'
        )

    @staticmethod
    def _projection_text(financial: dict, currency: str) -> str:
        rows = financial.get("annualProjection", []) if financial else []
        if not rows:
            return "Projection unavailable."
        parts = []
        for row in rows:
            parts.append(
                f'Year {row.get("year")}: revenue {BlueprintService._money(row.get("revenue"), currency)}, '
                f'costs {BlueprintService._money(row.get("totalCosts"), currency)}, '
                f'net {BlueprintService._money(row.get("netIncome"), currency)}.'
            )
        return " ".join(parts)

    @staticmethod
    def _monthly_table_text(financial: dict, currency: str, rows: int = 6) -> str:
        monthly = financial.get("monthlyRows", []) if financial else []
        if not monthly:
            return "No monthly rows available."
        parts = []
        for row in monthly[:rows]:
            outflow = (row.get("variableCosts", 0) or 0) + (row.get("fixedCosts", 0) or 0)
            parts.append(
                f'M{row.get("month")}: rev {BlueprintService._money(row.get("revenue"), currency)}, '
                f'outflow {BlueprintService._money(outflow, currency)}, '
                f'net {BlueprintService._money(row.get("netCashflow"), currency)}.'
            )
        return " ".join(parts)

    @staticmethod
    def _liquidity_text(financial: dict, currency: str) -> str:
        monthly = financial.get("monthlyRows", []) if financial else []
        deficits = [row for row in monthly if row.get("netCashflow", 0) < 0]
        if not monthly:
            return "Liquidity signal unavailable."
        if not deficits:
            last_cash = monthly[-1].get("cashPosition", 0)
            return f'No deficit months in this horizon. Ending cash position is {BlueprintService._money(last_cash, currency)}.'
        first_deficit = deficits[0]
        return (
            f'Cash deficits appear from month {first_deficit.get("month")}. '
            f'Consider pricing, volume, or cost adjustments to avoid negative operating cashflow.'
        )

    @staticmethod
    async def _generate_with_ai(section_type: str, blueprint: dict) -> str:
        """Generate section content with AI"""
        if not LLM_AVAILABLE:
            return BlueprintService._get_fallback_content(section_type, blueprint)
        
        try:
            prompt_template = BlueprintService.SECTION_PROMPTS.get(section_type, "")
            prompt = prompt_template.format(
                business_name=blueprint.get("businessName", "the business"),
                industry=blueprint.get("industry", "general"),
                description=blueprint.get("description", "a new business"),
                target_market=blueprint.get("targetMarket", "general market"),
                business_model=blueprint.get("businessModel", "traditional"),
                funding_goal=blueprint.get("fundingGoal", 100000)
            )
            
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return BlueprintService._get_fallback_content(section_type, blueprint)
            
            chat = LlmChat(
                api_key=llm_key,
                session_id=f"blueprint-{section_type}",
                system_message="You are a professional business consultant creating business plan sections. Write clear, professional, and actionable content."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            # Handle both string response and object response
            return response if isinstance(response, str) else (response.text if hasattr(response, 'text') else str(response))
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return BlueprintService._get_fallback_content(section_type, blueprint)
    
    @staticmethod
    async def _generate_swot_with_ai(blueprint: dict) -> dict:
        """Generate SWOT analysis with AI"""
        if not LLM_AVAILABLE:
            return BlueprintService._get_fallback_swot(blueprint)
        
        try:
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return BlueprintService._get_fallback_swot(blueprint)
            
            prompt = f"""Generate a SWOT analysis for this business:
            Business: {blueprint.get('businessName')}
            Industry: {blueprint.get('industry')}
            Description: {blueprint.get('description')}
            Target Market: {blueprint.get('targetMarket')}
            
            Return exactly 4-5 items for each category.
            Format as JSON with keys: strengths, weaknesses, opportunities, threats
            Each value should be an array of strings."""
            
            chat = LlmChat(
                api_key=llm_key,
                session_id="blueprint-swot",
                system_message="You are a business analyst. Return only valid JSON."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            # Try to parse JSON from response - handle both string and object response
            import json
            try:
                # Extract JSON from response
                text = response if isinstance(response, str) else (response.text if hasattr(response, 'text') else str(response))
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                
                swot_data = json.loads(text.strip())
                return {
                    "strengths": swot_data.get("strengths", [])[:5],
                    "weaknesses": swot_data.get("weaknesses", [])[:5],
                    "opportunities": swot_data.get("opportunities", [])[:5],
                    "threats": swot_data.get("threats", [])[:5]
                }
            except Exception:
                return BlueprintService._get_fallback_swot(blueprint)
                
        except Exception as e:
            print(f"SWOT AI error: {e}")
            return BlueprintService._get_fallback_swot(blueprint)
    
    @staticmethod
    def _get_fallback_content(section_type: str, blueprint: dict) -> str:
        """Fallback content when AI is unavailable"""
        business_name = blueprint.get("businessName", "Your Business")
        industry = blueprint.get("industry", "your industry")
        
        fallbacks = {
            "executive_summary": f"""{business_name} is a innovative venture in the {industry} industry. Our mission is to deliver exceptional value to our customers through innovative solutions and outstanding service. With a focus on sustainable growth and customer satisfaction, we aim to establish ourselves as a market leader within the next 3-5 years.

Key highlights include:
- Strong value proposition addressing real market needs
- Experienced leadership team with industry expertise
- Scalable business model with multiple revenue streams
- Clear path to profitability and sustainable growth""",
            
            "market_analysis": f"""The {industry} market presents significant opportunities for growth. Our analysis indicates:

**Market Size & Growth**: The market continues to expand with strong fundamentals.

**Target Customer Segments**:
- Primary: Core customer base with immediate needs
- Secondary: Adjacent markets with growth potential

**Market Trends**:
- Digital transformation driving adoption
- Increasing demand for quality solutions
- Growing awareness of value-based services

**Key Success Factors**:
- Customer-centric approach
- Continuous innovation
- Strong brand positioning""",
            
            "products_services": f"""{business_name} offers a comprehensive suite of products and services:

**Core Offerings**:
- Primary product/service line
- Supporting services
- Premium tier options

**Key Features**:
- User-friendly design
- Scalable solutions
- Integration capabilities

**Competitive Advantages**:
- Superior quality
- Competitive pricing
- Excellent customer support""",
            
            "marketing_strategy": f"""Our marketing strategy focuses on building brand awareness and driving customer acquisition:

**Positioning**: Premium quality at competitive prices in the {industry} space.

**Marketing Channels**:
- Digital marketing (SEO, content, social media)
- Strategic partnerships
- Direct outreach and networking
- Referral programs

**Customer Acquisition Strategy**:
- Content marketing to establish thought leadership
- Targeted advertising campaigns
- Conversion optimization

**Brand Messaging**:
- Clear value proposition
- Trust and credibility building
- Customer success stories""",
            
            "operations_plan": """Our operations are designed for efficiency and scalability:

**Core Processes**:
- Service delivery workflow
- Quality assurance
- Customer support

**Technology Infrastructure**:
- Modern tech stack
- Scalable cloud infrastructure
- Security and compliance

**Resource Requirements**:
- Team structure and roles
- Key partnerships
- Vendor relationships

**Key Metrics**:
- Operational efficiency KPIs
- Quality metrics
- Customer satisfaction scores""",
            
            "financial_projections": f"""Financial projections for {business_name}:

**Revenue Model**:
- Multiple revenue streams
- Recurring revenue opportunities
- Upsell and cross-sell potential

**Cost Structure**:
- Fixed costs: Infrastructure, team, overhead
- Variable costs: Customer acquisition, delivery

**Break-even Analysis**:
- Projected break-even within 18-24 months
- Path to profitability clearly defined

**3-Year Projection Summary**:
- Year 1: Foundation building, initial revenue
- Year 2: Growth acceleration, market expansion
- Year 3: Scale and profitability""",
            
            "competitive_analysis": f"""Competitive landscape analysis for the {industry} market:

**Direct Competitors**:
- Established players with market share
- New entrants with innovative approaches

**Competitive Positioning**:
- Our unique differentiators
- Value proposition comparison
- Pricing strategy

**Market Share Opportunity**:
- Addressable market segments
- Growth potential

**Defensive Strategy**:
- Barriers to entry
- Customer retention focus
- Continuous innovation"""
        }
        
        return fallbacks.get(section_type, "Content for this section.")
    
    @staticmethod
    def _get_fallback_swot(blueprint: dict) -> dict:
        """Fallback SWOT when AI unavailable"""
        return {
            "strengths": [
                "Innovative approach to market needs",
                "Strong founding team expertise",
                "Scalable business model",
                "Clear value proposition"
            ],
            "weaknesses": [
                "Limited brand recognition initially",
                "Resource constraints as startup",
                "Need to build customer base",
                "Dependent on key team members"
            ],
            "opportunities": [
                "Growing market demand",
                "Digital transformation trends",
                "Partnership opportunities",
                "Geographic expansion potential"
            ],
            "threats": [
                "Competitive pressure",
                "Market volatility",
                "Regulatory changes",
                "Economic uncertainty"
            ]
        }
    
    @staticmethod
    def _generate_financial_projections(funding_goal: float, business_model: str) -> List[dict]:
        """Generate financial projections"""
        base_revenue = funding_goal * 0.3  # 30% of funding as first year revenue target
        
        projections = []
        for year in range(1, 4):
            growth_rate = 0.3 + (year * 0.15)  # 45%, 60%, 75% growth
            revenue = base_revenue * (1 + growth_rate) ** year
            expenses = revenue * (0.85 - (year * 0.1))  # Decreasing expense ratio
            
            projections.append({
                "year": year,
                "revenue": round(revenue, 2),
                "expenses": round(expenses, 2),
                "netIncome": round(revenue - expenses, 2),
                "growthRate": round(growth_rate * 100, 1)
            })
        
        return projections
    
    @staticmethod
    async def generate_document(data: dict) -> dict:
        """Generate business document using AI"""
        document_type = data.get("documentType", "quote")
        company_name = data.get("companyName", "Company")
        industry = data.get("industry", "")
        description = data.get("description", "")
        
        if not LLM_AVAILABLE:
            return {"content": BlueprintService._get_fallback_document(document_type, company_name)}
        
        try:
            # Professional preamble for all documents
            base_context = f"""You are a professional document drafting expert with expertise in UK business law and industry best practices.

COMPANY CONTEXT:
- Company Name: {company_name}
- Industry: {industry or 'General Business Services'}
- Description: {description or 'Professional services provider'}

CRITICAL REQUIREMENTS:
1. Write in perfect British English with correct grammar, spelling, and punctuation
2. Follow UK legal standards and industry best practices
3. Make it specific to the company - use the company name throughout, NOT generic placeholders
4. Structure with clear headings and professional formatting
5. Include relevant dates formatted as DD/MM/YYYY
6. Be comprehensive yet concise
7. Ensure legal validity where applicable

"""
            
            doc_prompts = {
                "quote": base_context + """Create a professional quotation/estimate document.

REQUIRED SECTIONS:
1. Company letterhead with full contact details
2. Quote reference number and date
3. Client information section
4. Detailed itemised pricing table with columns: Item, Description, Quantity, Unit Price (£), Total (£)
5. Subtotal, VAT (20%), and Grand Total
6. Validity period (typically 30 days)
7. Payment terms
8. Terms and conditions summary
9. Acceptance signature block

Make it look professional and ready to send to clients.""",
                
                "simple_contract": base_context + """Create a legally sound service agreement contract.

REQUIRED SECTIONS:
1. Agreement header with parties' details
2. Recitals (background/whereas clauses)
3. Definitions
4. Scope of Services
5. Fees and Payment Terms
6. Term and Termination
7. Confidentiality
8. Intellectual Property
9. Limitation of Liability
10. General Provisions (Force Majeure, Notices, Governing Law - England and Wales)
11. Signature blocks for both parties

Ensure it is enforceable under UK law.""",
                
                "proposal": base_context + """Create a compelling business proposal.

REQUIRED SECTIONS:
1. Cover page with company branding
2. Executive Summary
3. Understanding of Client Needs
4. Proposed Solution/Approach
5. Methodology and Timeline
6. Team/Resources
7. Investment Summary (pricing)
8. Why Choose Us (differentiators)
9. Case Studies/Testimonials (placeholder)
10. Next Steps and Call to Action
11. Terms and Conditions Summary

Make it persuasive and professional.""",
                
                "invoice_template": base_context + """Create a professional invoice template.

REQUIRED ELEMENTS:
1. Company logo/letterhead area
2. "INVOICE" header
3. Invoice number, date, and due date
4. Company VAT number (placeholder)
5. Bill To section
6. Itemised services/products table
7. Subtotal, VAT breakdown, Total Due
8. Payment methods and bank details section
9. Payment terms
10. Thank you note

Format for easy customisation.""",
                
                "privacy_policy": base_context + """Create a comprehensive GDPR and UK Data Protection Act 2018 compliant privacy policy.

REQUIRED SECTIONS:
1. Introduction and company identification
2. What information we collect
3. How we collect your information
4. How we use your information (legal bases)
5. Data sharing and third parties
6. International transfers
7. Data retention
8. Your rights under GDPR (access, rectification, erasure, portability, objection)
9. Cookies (brief, link to cookie policy)
10. Security measures
11. Children's privacy
12. Changes to this policy
13. Contact details and Data Protection Officer
14. Right to complain to ICO

Ensure full legal compliance.""",
                
                "cookie_notice": base_context + """Create a PECR and GDPR compliant cookie policy.

REQUIRED SECTIONS:
1. What are cookies
2. Types of cookies we use:
   - Strictly necessary
   - Performance/Analytics
   - Functionality
   - Targeting/Advertising
3. Specific cookies table (name, purpose, duration, type)
4. Third-party cookies
5. How to manage cookies (browser settings)
6. Consent management
7. Changes to policy
8. Contact information

Include practical guidance for users.""",
                
                "terms_conditions": base_context + """Create comprehensive terms and conditions.

REQUIRED SECTIONS:
1. Introduction and acceptance
2. Definitions
3. Services description
4. Account registration (if applicable)
5. Pricing and payment
6. Cancellation and refunds
7. User obligations
8. Intellectual property
9. Disclaimer and limitation of liability
10. Indemnification
11. Termination
12. Dispute resolution
13. Governing law (England and Wales)
14. Changes to terms
15. Contact information
16. Severability

Ensure enforceability under UK consumer law.""",
                
                "refund_policy": base_context + """Create a clear refund and returns policy compliant with UK Consumer Rights Act 2015.

REQUIRED SECTIONS:
1. Policy overview
2. Eligibility for refunds
3. Statutory rights (14-day cooling-off period for online sales)
4. How to request a refund
5. Refund process and timeline
6. Refund methods
7. Non-refundable items/services
8. Partial refunds
9. Exchanges
10. Faulty goods/services
11. Contact information

Be clear and customer-friendly while protecting the business.""",
                
                "employee_handbook": base_context + """Create a professional employee handbook.

REQUIRED SECTIONS:
1. Welcome message from leadership
2. Company overview, mission, and values
3. Employment policies
   - Equal opportunities
   - Recruitment and probation
   - Working hours and flexible working
4. Code of conduct
5. Leave policies (annual, sick, parental)
6. Benefits summary
7. Performance management
8. Disciplinary and grievance procedures
9. Health and safety
10. Data protection and confidentiality
11. IT and social media policy
12. Termination of employment
13. Acknowledgment form

Comply with UK employment law.""",
                
                "remote_work_policy": base_context + """Create a comprehensive remote/hybrid working policy.

REQUIRED SECTIONS:
1. Policy purpose and scope
2. Eligibility criteria
3. Application process
4. Working arrangements (hours, availability)
5. Workspace requirements
6. Equipment and expenses
7. Health and safety (DSE assessments)
8. Data security and confidentiality
9. Communication expectations
10. Performance management
11. Team collaboration
12. Return to office provisions
13. Policy review

Reflect modern working practices.""",
                
                "leave_policy": base_context + """Create a UK-compliant leave policy.

REQUIRED SECTIONS:
1. Annual leave entitlement (minimum 28 days including bank holidays)
2. Leave year and carry-over
3. Booking process
4. Sick leave and SSP
5. Maternity leave (52 weeks statutory)
6. Paternity leave (2 weeks statutory)
7. Shared parental leave
8. Adoption leave
9. Parental bereavement leave
10. Compassionate leave
11. Jury service
12. Time off for dependants
13. Unpaid leave

Ensure statutory compliance.""",
                
                "code_of_conduct": base_context + """Create a professional code of conduct.

REQUIRED SECTIONS:
1. Introduction and purpose
2. Core values and principles
3. Professional behaviour expectations
4. Equality, diversity, and inclusion
5. Anti-harassment and bullying
6. Conflicts of interest
7. Gifts and hospitality
8. Confidentiality
9. Use of company resources
10. Social media guidelines
11. Reporting concerns (whistleblowing)
12. Consequences of violations
13. Acknowledgment

Set clear expectations for all employees.""",
                
                "welcome_email": base_context + """Create a warm, professional welcome email template for new clients.

INCLUDE:
1. Personalised greeting
2. Expression of appreciation
3. Brief reminder of what they've signed up for
4. What to expect next (clear next steps)
5. Key contact information
6. Helpful resources or links
7. Invitation to reach out with questions
8. Professional sign-off

Make the client feel valued and informed.""",
                
                "follow_up_email": base_context + """Create a professional sales follow-up email template.

INCLUDE:
1. Personalised opening referencing previous interaction
2. Value reminder (what problem you solve)
3. Specific benefit or case study mention
4. Gentle handling of potential objections
5. Clear, specific call-to-action
6. Easy response mechanism
7. Professional sign-off
8. P.S. with added value or urgency

Be persuasive without being pushy.""",
                
                "thank_you_note": base_context + """Create a sincere client thank you note template.

INCLUDE:
1. Genuine expression of gratitude
2. Specific mention of what you're thanking them for
3. Recognition of the relationship value
4. Brief mention of positive outcomes or impact
5. Forward-looking statement
6. Offer of continued support
7. Warm, professional close

Make it personal and memorable.""",
                
                "meeting_agenda": base_context + """Create a professional meeting agenda template.

INCLUDE:
1. Meeting header (title, date, time, location/link)
2. Attendees list
3. Meeting objective
4. Agenda items with:
   - Topic
   - Presenter/Lead
   - Time allocation
5. Discussion points
6. Action items section
7. Next steps
8. Next meeting date placeholder
9. Notes section

Keep it structured and actionable."""
            }
            
            prompt = doc_prompts.get(document_type, base_context + f"Create a professional {document_type} document.")
            
            chat = LlmChat(
                api_key=os.environ.get("EMERGENT_LLM_KEY", ""),
                session_id=f"doc-gen-{document_type}",
                system_message="You are a professional document drafting expert. Create comprehensive, legally compliant business documents following UK standards. Use proper British English."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            text = response if isinstance(response, str) else (response.text if hasattr(response, 'text') else str(response))
            
            return {"content": text.strip()}
            
        except Exception as e:
            print(f"Document generation error: {e}")
            return {"content": BlueprintService._get_fallback_document(document_type, company_name)}
    
    @staticmethod
    def _get_fallback_document(document_type: str, company_name: str) -> str:
        """Fallback documents when AI is unavailable"""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        templates = {
            "quote": f"""QUOTATION

{company_name}
Date: {date_str}
Quote #: [Number]
Valid Until: [Date]

TO:
[Client Name]
[Client Address]

DESCRIPTION OF SERVICES:

| Item | Description | Quantity | Unit Price | Total |
|------|-------------|----------|------------|-------|
| 1    | [Service]   | 1        | £0.00      | £0.00 |

Subtotal: £0.00
VAT (20%): £0.00
TOTAL: £0.00

Terms: Payment due within 30 days

Accepted by: _______________ Date: ___________""",

            "privacy_policy": f"""PRIVACY POLICY

Last Updated: {date_str}

{company_name} ("we", "us", or "our") is committed to protecting your privacy.

1. INFORMATION WE COLLECT
We collect information you provide directly to us.

2. HOW WE USE YOUR INFORMATION
We use the information to provide and improve our services.

3. INFORMATION SHARING
We do not sell or rent your personal information.

4. DATA SECURITY
We implement appropriate security measures.

5. YOUR RIGHTS
You have the right to access, correct, or delete your data.

6. CONTACT US
For questions, please contact us at: [email]""",

            "simple_contract": f"""SERVICE AGREEMENT

This Agreement is entered into on {date_str}

BETWEEN:
{company_name} ("Provider")
AND:
[Client Name] ("Client")

1. SERVICES
The Provider agrees to provide [describe services].

2. PAYMENT TERMS
[Payment details]

3. TERM
This agreement begins on [date] and continues until [date/completion].

4. TERMINATION
Either party may terminate with [X] days written notice.

5. CONFIDENTIALITY
Both parties agree to keep confidential information private.

SIGNATURES:

Provider: _______________ Date: ___________
Client: _______________ Date: ___________""",

            "welcome_email": f"""Subject: Welcome to {company_name}!

Dear [Client Name],

We're delighted to welcome you to {company_name}!

Thank you for choosing us. We're committed to providing you with exceptional service.

What happens next:
• [Step 1]
• [Step 2]
• [Step 3]

If you have any questions, don't hesitate to reach out.

Best regards,
The {company_name} Team"""
        }
        
        return templates.get(document_type, f"[{document_type.replace('_', ' ').title()} Template for {company_name}]")
