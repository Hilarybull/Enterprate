"""Comprehensive Validation Report Service with AI-powered analysis"""
import uuid
import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from app.core.database import get_db
from app.schemas.validation_report import (
    ValidationReportCreate,
    ComprehensiveReport,
    AIScores,
    ScoreItem,
    BusinessFit,
    BusinessFitItem,
    OfferTier,
    FrameworkAnalysis,
    FrameworkScore,
    CommunitySignal,
    KeywordData,
    Categorization,
    ReportStatus
)
from app.services.market_data_service import MarketDataService
from app.services.macro_data_service import MacroDataService
from app.services.keyword_intel_service import KeywordIntelService
from app.services.community_intel_service import CommunityIntelService

# Try to import LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class ValidationReportService:
    """Service for comprehensive idea validation reports"""
    
    @staticmethod
    async def create_comprehensive_report(
        workspace_id: str, 
        user_id: str, 
        data: ValidationReportCreate
    ) -> dict:
        """Create a comprehensive IdeaBrowser-style validation report"""
        db = get_db()
        
        # Generate AI-powered comprehensive report
        report = await ValidationReportService._generate_ai_report(data)
        
        # Always use deterministic scoring (AI is for narrative only)
        deterministic_summary = await ValidationReportService._calculate_deterministic_summary(data)
        report["deterministicSummary"] = deterministic_summary
        report["scores"] = ValidationReportService._build_deterministic_score_cards(
            data,
            deterministic_summary
        )
        ValidationReportService._apply_real_world_narrative(report, data, deterministic_summary)
        await ValidationReportService._apply_keyword_intel(report, data)
        await ValidationReportService._apply_community_intel(report, data)
        
        # Create database document
        report_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        doc = {
            "id": report_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": ReportStatus.PENDING.value,
            "ideaInput": data.model_dump() if hasattr(data, 'model_dump') else data.dict(),
            "report": report,
            "createdAt": now,
            "updatedAt": now
        }
        
        # Store in database
        await db.validation_reports.insert_one(doc)
        
        # Update engagement counter
        await ValidationReportService._increment_engagement(workspace_id, user_id)
        
        # Log intelligence event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "validation.report_created",
            "data": {
                "report_id": report_id,
                "idea_name": data.ideaName,
                "idea_type": data.ideaType,
                "overall_score": report["deterministicSummary"]["validationScore"]
            },
            "occurredAt": now
        })
        
        # Return without _id
        doc.pop("_id", None)
        return doc

    @staticmethod
    async def _calculate_deterministic_summary(data: ValidationReportCreate) -> dict:
        """Calculate deterministic baseline metrics for idea validation."""
        price = float(data.priceAmount or 0)
        units = int(data.expectedUnitsPerMonth or 0)
        variable_per_unit = float(data.variableCostPerUnit or 0)
        fixed_monthly = float(data.fixedMonthlyCosts or 0)
        founder_draw = float(data.founderDrawMonthly or 0)
        contractor_costs = float(data.contractorCostsMonthly or 0)
        total_fixed = fixed_monthly + founder_draw + contractor_costs
        customers = int(data.expectedCustomers or 0)
        sales_cycle_days = int(data.salesCycleDays or 0)
        payment_terms_days = int(data.paymentTermsDays or 0)
        cash_buffer = float(data.cashBuffer or 0)
        staff_count = int(data.staffCount or 0)
        capacity_per_staff = float(data.capacityPerStaffPerMonth or 0)

        monthly_revenue = units * price
        monthly_variable_cost = units * variable_per_unit
        monthly_net = monthly_revenue - monthly_variable_cost - total_fixed
        contribution_margin_pct = (
            ((monthly_revenue - monthly_variable_cost) / monthly_revenue) * 100
            if monthly_revenue > 0 else 0
        )

        break_even_revenue = None
        if price > variable_per_unit and price > 0:
            unit_contribution = price - variable_per_unit
            break_even_units = total_fixed / unit_contribution if unit_contribution > 0 else 0
            break_even_revenue = break_even_units * price

        capacity_total = None
        capacity_feasible = None
        capacity_utilization_pct = None
        if capacity_per_staff > 0:
            effective_staff = max(1, staff_count)
            capacity_total = effective_staff * capacity_per_staff
            capacity_feasible = units <= capacity_total
            capacity_utilization_pct = (units / capacity_total) * 100 if capacity_total > 0 else 0

        runway_months = None
        if cash_buffer > 0 and monthly_net < 0:
            runway_months = cash_buffer / abs(monthly_net)

        market_profile = MarketDataService.get_market_profile(
            industry=data.industry,
            sub_industry=data.subIndustry,
            service_type=data.serviceType,
            delivery_model=data.deliveryModel,
            target_market=data.targetMarket,
            target_location=data.targetLocation,
        )
        market_score = int(market_profile.get("marketScore", 50))
        macro_profile = await MacroDataService.get_macro_profile(data.targetLocation)
        macro_score = int(macro_profile.get("score", 50))
        market_factors = market_profile.get("factors", {})
        demand_factor = int(market_factors.get("demand", 50))

        # PDF-style rubric (D1-D7): deterministic, explainable, reproducible.
        # External context is capped to 10% influence.
        def clip(v: float, lo: int = 0, hi: int = 100) -> int:
            return max(lo, min(hi, int(round(v))))

        # D1: Margin strength
        if contribution_margin_pct >= 60:
            d1_margin = 90
        elif contribution_margin_pct >= 45:
            d1_margin = 75
        elif contribution_margin_pct >= 30:
            d1_margin = 60
        elif contribution_margin_pct >= 20:
            d1_margin = 45
        else:
            d1_margin = 25

        # D2: Demand realism
        if units > 0 and customers > 0:
            d2_demand = 70
        elif units > 0:
            d2_demand = 50
        else:
            d2_demand = 30
        d2_demand = clip(d2_demand + (demand_factor - 50) * 0.4)

        # D3: Capacity feasibility
        if capacity_utilization_pct is None:
            d3_capacity = 50
        elif capacity_utilization_pct < 85:
            d3_capacity = 85
        elif capacity_utilization_pct <= 100:
            d3_capacity = 55
        else:
            d3_capacity = 25

        # D4: Fixed cost impact
        fixed_ratio = total_fixed / monthly_revenue if monthly_revenue > 0 else 99
        if fixed_ratio <= 0.30:
            d4_fixed_cost = 85
        elif fixed_ratio <= 0.50:
            d4_fixed_cost = 70
        elif fixed_ratio <= 0.75:
            d4_fixed_cost = 55
        elif fixed_ratio <= 1.00:
            d4_fixed_cost = 40
        else:
            d4_fixed_cost = 25

        # D5: Payment/cashflow friction
        d5_payment = 80
        if payment_terms_days > 60:
            d5_payment -= 30
        elif payment_terms_days > 45:
            d5_payment -= 20
        elif payment_terms_days > 30:
            d5_payment -= 12
        elif payment_terms_days > 14:
            d5_payment -= 6
        if sales_cycle_days > 60:
            d5_payment -= 20
        elif sales_cycle_days > 45:
            d5_payment -= 12
        elif sales_cycle_days > 30:
            d5_payment -= 6
        d5_payment = clip(d5_payment, 10, 95)

        # D6: Diversification/resilience
        channel_count = len(data.goToMarketChannel or [])
        d6_diversification = 30 + min(40, channel_count * 10)
        if customers >= 5:
            d6_diversification += 15
        elif customers >= 2:
            d6_diversification += 8
        else:
            d6_diversification -= 10
        d6_diversification = clip(d6_diversification, 15, 95)

        # D7: Proof strength (MVP proxy from structured completeness)
        proof_fields = [
            data.ideaDescription, data.targetAudience, data.problemSolved, data.howItWorks,
            data.serviceType, data.pricingModel, data.priceAmount, data.expectedUnitsPerMonth, data.expectedCustomers
        ]
        filled = sum(1 for v in proof_fields if v not in (None, "", []))
        d7_proof = clip((filled / max(1, len(proof_fields))) * 100)
        if data.problemFrequency:
            d7_proof = clip(d7_proof + 5)
        if data.urgencyLevel:
            d7_proof = clip(d7_proof + 5)

        dimension_weights = {
            "D1_marginStrength": 0.20,
            "D2_demandRealism": 0.15,
            "D3_capacityFeasibility": 0.20,
            "D4_fixedCostImpact": 0.15,
            "D5_paymentTermsImpact": 0.10,
            "D6_diversificationBenefit": 0.10,
            "D7_proofStrength": 0.10,
        }
        core_score = clip(
            d1_margin * dimension_weights["D1_marginStrength"] +
            d2_demand * dimension_weights["D2_demandRealism"] +
            d3_capacity * dimension_weights["D3_capacityFeasibility"] +
            d4_fixed_cost * dimension_weights["D4_fixedCostImpact"] +
            d5_payment * dimension_weights["D5_paymentTermsImpact"] +
            d6_diversification * dimension_weights["D6_diversificationBenefit"] +
            d7_proof * dimension_weights["D7_proofStrength"]
        )

        # External context influence is capped at 10% as per PDF policy.
        external_context_score = clip(market_score * 0.60 + macro_score * 0.40)
        external_cap_weight = 0.10
        validation_score = clip(core_score * (1 - external_cap_weight) + external_context_score * external_cap_weight)

        flags = []
        if monthly_revenue <= 0:
            flags.append("No projected monthly revenue provided.")
        if contribution_margin_pct < 30:
            flags.append("Low contribution margin. Review pricing or delivery cost.")
        if capacity_feasible is False:
            flags.append("Demand exceeds delivery capacity.")
        if payment_terms_days > 30:
            flags.append("Long payment terms increase cashflow pressure.")
        if sales_cycle_days > 45:
            flags.append("Long sales cycle may slow customer acquisition.")
        if monthly_net < 0:
            flags.append("Baseline monthly model is running at a deficit.")

        reason_codes = []
        if capacity_feasible is False:
            reason_codes.append("CAPACITY_MISMATCH")
        if contribution_margin_pct < 30:
            reason_codes.append("LOW_MARGIN")
        if monthly_net < 0:
            reason_codes.append("NEGATIVE_MONTHLY_NET")
        if payment_terms_days > 30:
            reason_codes.append("LONG_PAYMENT_TERMS")
        if sales_cycle_days > 45:
            reason_codes.append("LONG_SALES_CYCLE")
        if customers <= 1:
            reason_codes.append("CUSTOMER_CONCENTRATION_RISK")
        if d7_proof < 50:
            reason_codes.append("LOW_PROOF_STRENGTH")
        if external_context_score < 40:
            reason_codes.append("WEAK_EXTERNAL_CONTEXT")

        if validation_score >= 85:
            classification = "Highly Robust"
        elif validation_score >= 70:
            classification = "Strong"
        elif validation_score >= 55:
            classification = "Moderate"
        elif validation_score >= 40:
            classification = "Weak"
        else:
            classification = "High Failure Risk"

        recommendations = []
        if contribution_margin_pct < 40:
            recommendations.append("Increase price or reduce variable cost to improve margin.")
        if capacity_feasible is False:
            recommendations.append("Adjust demand assumptions or increase delivery resources.")
        if monthly_net < 0:
            recommendations.append("Cut fixed costs or increase volume before scaling operations.")
        if payment_terms_days > 30:
            recommendations.append("Tighten payment terms (e.g., 14-30 days) to protect cashflow.")
        if customers <= 1:
            recommendations.append("Reduce concentration risk: avoid relying on a single early customer.")
        if capacity_utilization_pct is not None and capacity_utilization_pct > 100:
            recommendations.append("Increase delivery capacity or lower unit demand assumptions before launch.")
        if not recommendations:
            recommendations.append("Baseline looks viable; proceed to registration and execution planning.")

        return {
            "validationScore": validation_score,
            "metrics": {
                "monthlyRevenue": round(monthly_revenue, 2),
                "monthlyVariableCost": round(monthly_variable_cost, 2),
                "monthlyFixedCost": round(total_fixed, 2),
                "monthlyNet": round(monthly_net, 2),
                "contributionMarginPct": round(contribution_margin_pct, 2),
                "breakEvenRevenue": round(break_even_revenue, 2) if break_even_revenue is not None else None,
                "capacityTotalUnits": round(capacity_total, 2) if capacity_total is not None else None,
                "capacityFeasible": capacity_feasible,
                "capacityUtilizationPct": round(capacity_utilization_pct, 2) if capacity_utilization_pct is not None else None,
                "runwayMonths": round(runway_months, 2) if runway_months is not None else None
            },
            "scoreBreakdown": {
                "baseModelScore": core_score,
                "marketScore": market_score,
                "macroScore": macro_score,
                "externalContextScore": external_context_score,
                "blendWeights": {
                    "coreModel": 0.90,
                    "externalContext": 0.10,
                    "externalSplit": {"market": 0.60, "macro": 0.40},
                },
                "dimensionScores": {
                    "D1_marginStrength": d1_margin,
                    "D2_demandRealism": d2_demand,
                    "D3_capacityFeasibility": d3_capacity,
                    "D4_fixedCostImpact": d4_fixed_cost,
                    "D5_paymentTermsImpact": d5_payment,
                    "D6_diversificationBenefit": d6_diversification,
                    "D7_proofStrength": d7_proof,
                },
                "dimensionWeights": dimension_weights,
            },
            "marketContext": market_profile,
            "macroContext": macro_profile,
            "classification": classification,
            "reasonCodes": reason_codes,
            "flags": flags,
            "recommendations": recommendations
        }

    @staticmethod
    def _build_deterministic_score_cards(data: ValidationReportCreate, summary: dict) -> dict:
        """Build 1-10 score cards from deterministic inputs only."""
        validation_score = int(summary.get("validationScore", 0))
        metrics = summary.get("metrics", {})

        margin_pct = float(metrics.get("contributionMarginPct") or 0)
        monthly_net = float(metrics.get("monthlyNet") or 0)
        capacity_feasible = metrics.get("capacityFeasible")
        sales_cycle_days = int(data.salesCycleDays or 0)
        payment_terms_days = int(data.paymentTermsDays or 0)
        urgency = (data.urgencyLevel or "").lower()

        opportunity = max(1, min(10, round(validation_score / 10)))

        problem_raw = 4
        if urgency == "high":
            problem_raw += 3
        elif urgency == "medium":
            problem_raw += 2
        else:
            problem_raw += 1
        if data.problemFrequency in {"daily", "weekly"}:
            problem_raw += 1
        if len(data.problemSolved or "") >= 80:
            problem_raw += 1
        problem = max(1, min(10, problem_raw))

        feasibility_raw = 5
        if margin_pct >= 50:
            feasibility_raw += 2
        elif margin_pct >= 30:
            feasibility_raw += 1
        if monthly_net >= 0:
            feasibility_raw += 2
        if capacity_feasible is False:
            feasibility_raw -= 2
        feasibility = max(1, min(10, feasibility_raw))

        why_now_raw = 5
        if urgency == "high":
            why_now_raw += 2
        elif urgency == "medium":
            why_now_raw += 1
        if sales_cycle_days and sales_cycle_days <= 30:
            why_now_raw += 1
        if payment_terms_days and payment_terms_days <= 30:
            why_now_raw += 1
        why_now = max(1, min(10, why_now_raw))

        def label(v: int) -> str:
            if v >= 8:
                return "Strong"
            if v >= 6:
                return "Good"
            if v >= 4:
                return "Moderate"
            return "Weak"

        return {
            "opportunity": {
                "value": opportunity,
                "label": label(opportunity),
                "description": "Based on margin, profitability, capacity, and demand signals."
            },
            "problem": {
                "value": problem,
                "label": label(problem),
                "description": "Based on urgency, frequency, and problem clarity."
            },
            "feasibility": {
                "value": feasibility,
                "label": label(feasibility),
                "description": "Based on economics, operational capacity, and execution friction."
            },
            "whyNow": {
                "value": why_now,
                "label": label(why_now),
                "description": "Based on urgency and commercial friction inputs."
            }
        }

    @staticmethod
    def _short_text(value: Optional[str], max_len: int = 140) -> str:
        text = (value or "").strip()
        if len(text) <= max_len:
            return text
        return text[: max_len - 1].rstrip() + "..."

    @staticmethod
    def _clean_sentence(value: Optional[str]) -> str:
        text = (value or "").strip()
        while "  " in text:
            text = text.replace("  ", " ")
        text = text.replace("..", ".")
        return text.strip(" .")

    @staticmethod
    def _structured_description(
        idea_description: Optional[str],
        customer_segment: Optional[str],
        target_location: Optional[str],
        target_market: Optional[str],
        problem: Optional[str],
    ) -> str:
        intro = ValidationReportService._clean_sentence(idea_description) or "Business concept"
        segment = ValidationReportService._clean_sentence(customer_segment) or "target customers"
        location = ValidationReportService._clean_sentence(target_location) or "selected location"
        market = ValidationReportService._clean_sentence(target_market) or "selected market"
        clean_problem = ValidationReportService._clean_sentence(problem) or "No clear problem statement provided"
        return (
            f"What you are building: {intro}.\n"
            f"Who it is for: {segment} in {location} ({market}).\n"
            f"Problem being solved: {clean_problem}."
        )

    @staticmethod
    def _currency_from_location(target_location: Optional[str]) -> tuple[str, str]:
        loc = (target_location or "").strip().lower()
        if any(x in loc for x in ["uk", "united kingdom", "england", "scotland", "wales", "northern ireland"]):
            return "GBP", "GBP"
        if any(x in loc for x in ["us", "usa", "united states", "america"]):
            return "USD", "USD"
        if any(x in loc for x in ["euro", "eu", "germany", "france", "italy", "spain", "netherlands", "belgium"]):
            return "EUR", "EUR"
        return "USD", "USD"

    @staticmethod
    def _format_money(amount: float, currency_code: str) -> str:
        return f"{currency_code} {amount:,.0f}"

    @staticmethod
    def _display_source(source: Optional[str]) -> str:
        raw = (source or "fallback").strip().lower().replace("-", "_")
        mapping = {
            "world_bank": "World Bank",
            "fred": "FRED",
            "dataforseo": "DataForSEO",
            "fallback": "Fallback",
        }
        return mapping.get(raw, raw.replace("_", " ").title())

    @staticmethod
    def _display_location(location: Optional[str]) -> str:
        raw = (location or "").strip()
        if not raw:
            return "selected location"
        lowered = raw.lower()
        if lowered in {"uk", "u.k.", "united kingdom"}:
            return "UK"
        if lowered in {"us", "u.s.", "usa", "united states"}:
            return "US"
        return raw

    @staticmethod
    def _build_value_ladder(data: ValidationReportCreate, summary: dict) -> List[dict]:
        metrics = summary.get("metrics", {})
        price_amount = float(data.priceAmount or 0)
        variable_cost = float(data.variableCostPerUnit or 0)
        margin_guard_price = variable_cost * 1.8 if variable_cost > 0 else 0
        unit = (data.deliverableUnit or "month").lower()
        pricing_model = (data.pricingModel or "fixed_job").lower()
        currency_code, _ = ValidationReportService._currency_from_location(data.targetLocation)

        if price_amount <= 0:
            if margin_guard_price > 0:
                price_amount = margin_guard_price
            else:
                price_amount = 49 if pricing_model in {"subscription", "retainer"} else 150

        unit_suffix_map = {
            "hour": "/hour",
            "hours": "/hour",
            "job": "/job",
            "project": "/job",
            "month": "/month",
            "week": "/week",
        }
        unit_suffix = unit_suffix_map.get(unit, "/unit")
        if pricing_model in {"subscription", "retainer"}:
            unit_suffix = "/month"

        package_names = [p.strip() for p in (data.packageTiers or "").replace("|", "/").split("/") if p.strip()]
        frontend_name = package_names[0] if package_names else "Starter Plan"
        core_name = package_names[-1] if len(package_names) > 1 else "Growth Plan"

        service_name = (data.serviceType or "").strip() or (data.ideaName or "Service").strip()
        service_name = ValidationReportService._short_text(service_name, 48)
        how_it_works = ValidationReportService._short_text(
            ValidationReportService._clean_sentence(data.howItWorks), 110
        ) or "A clear delivery process with measurable milestones."

        expected_customers = int(data.expectedCustomers or 0)
        expected_units = int(data.expectedUnitsPerMonth or 0)
        monthly_revenue = float(metrics.get("monthlyRevenue") or 0)
        demand_note = (
            f"Built for about {expected_customers} paying customers and {expected_units} units per month."
            if expected_customers > 0 or expected_units > 0
            else "Sized for early customer validation and repeat demand."
        )

        frontend_price = ValidationReportService._format_money(price_amount, currency_code) + unit_suffix
        core_min = price_amount * 2.0
        core_max = price_amount * 3.5
        if monthly_revenue > 0 and expected_customers > 0:
            avg_revenue_per_customer = monthly_revenue / expected_customers
            core_min = max(core_min, avg_revenue_per_customer * 0.9)
            core_max = max(core_max, avg_revenue_per_customer * 1.6)
        core_price = (
            f"{ValidationReportService._format_money(core_min, currency_code)}-"
            f"{ValidationReportService._format_money(core_max, currency_code)}{unit_suffix}"
        )

        return [
            {
                "tier": "LEAD MAGNET",
                "name": f"{service_name} Readiness Check",
                "price": "Free",
                "description": "Quick diagnostic to identify bottlenecks and define the first measurable improvement.",
            },
            {
                "tier": "FRONTEND",
                "name": frontend_name,
                "price": frontend_price,
                "description": f"Entry package for {service_name.lower()} with focused scope. {demand_note}",
            },
            {
                "tier": "CORE",
                "name": core_name,
                "price": core_price,
                "description": f"Full delivery tier with ongoing support and outcomes tracking. Operating model: {how_it_works}",
            },
        ]

    @staticmethod
    def _compact_audience(text: Optional[str], fallback_segment: Optional[str]) -> str:
        clean = ValidationReportService._clean_sentence(text)
        if not clean:
            return ValidationReportService._clean_sentence(fallback_segment) or "target customers"
        for token in [", who", " who ", ", facing", " facing "]:
            if token in clean:
                clean = clean.split(token)[0].strip(" ,.")
                break
        return ValidationReportService._short_text(clean, 70) or "target customers"

    @staticmethod
    def _compact_problem(text: Optional[str]) -> str:
        clean = ValidationReportService._clean_sentence(text)
        if not clean:
            return "a clear recurring customer pain"
        lower = clean.lower()
        if ", losing " in lower:
            idx = lower.index(", losing ")
            return ValidationReportService._short_text(clean[idx + 2 :], 90)
        if " due to " in lower:
            parts = clean.split(" due to ", 1)
            return ValidationReportService._short_text(parts[0] + " due to " + parts[1], 90)
        return ValidationReportService._short_text(clean, 90)
    @staticmethod
    def _apply_real_world_narrative(report: dict, data: ValidationReportCreate, summary: dict) -> None:
        """Ground narrative sections with market and macro context (non-AI scoring)."""
        market_ctx = summary.get("marketContext", {})
        macro_ctx = summary.get("macroContext", {})
        metrics = summary.get("metrics", {})
        breakdown = summary.get("scoreBreakdown", {})

        factors = market_ctx.get("factors", {})
        demand = int(factors.get("demand", 50))
        competition = int(factors.get("competition", 50))
        cpc = int(factors.get("cpcPressure", 50))
        macro_score = int(macro_ctx.get("score", 50))
        monthly_net = float(metrics.get("monthlyNet") or 0)
        margin_pct = float(metrics.get("contributionMarginPct") or 0)
        capacity_feasible = metrics.get("capacityFeasible")
        market_score = int(breakdown.get("marketScore", 50))

        audience = ValidationReportService._compact_audience(data.targetAudience, data.customerSegment)
        problem = ValidationReportService._compact_problem(data.problemSolved)
        how_it_works = ValidationReportService._clean_sentence(data.howItWorks) or "a simple repeatable delivery flow"
        if len(how_it_works) > 160:
            how_it_works = how_it_works[:160].rsplit(" ", 1)[0].rstrip(",.;: ")
        primary_channel = data.goToMarketChannel[0] if data.goToMarketChannel else "direct outreach"
        service_name = ValidationReportService._clean_sentence(data.serviceType) or "your core service"
        delivery_model = ValidationReportService._clean_sentence(data.deliveryModel) or "delivery"

        macro_label = "supportive" if macro_score >= 60 else "neutral" if macro_score >= 45 else "tight"
        demand_label = "strong" if demand >= 65 else "moderate" if demand >= 45 else "weak"
        competition_label = "high" if competition >= 70 else "moderate" if competition >= 45 else "low"
        cpc_label = "high" if cpc >= 70 else "moderate" if cpc >= 45 else "low"

        # Build a clean, stable structure and avoid duplicated audience/problem blocks.
        report["description"] = ValidationReportService._structured_description(
            data.ideaDescription,
            data.customerSegment,
            data.targetLocation,
            data.targetMarket,
            problem,
        )

        location_label = ValidationReportService._display_location(data.targetLocation)
        source_label = ValidationReportService._display_source(macro_ctx.get('source', 'fallback'))

        report["whyNow"] = (
            f"Timing for {data.industry} in {location_label} is {macro_label}. "
            f"Demand is {demand}/100 with {competition_label} competition, and urgency is {data.urgencyLevel} around {problem}."
        )

        report["proofSignals"] = (
            f"Signals: demand {demand}/100, competition {competition}/100, and acquisition pressure {cpc}/100. "
            f"Macro score is {macro_score}/100 from {source_label}, supporting testing with {audience} in {location_label}."
        )

        report["marketGap"] = (
            f"Existing options in {location_label} still leave {audience} with {problem}. "
            f"With {competition_label} competition and {cpc_label} acquisition costs, clearer {data.deliveryModel} positioning still has room."
        )

        capacity_note = (
            "Current projected demand fits delivery capacity."
            if capacity_feasible is True
            else "Current projected demand exceeds delivery capacity, so either reduce demand assumptions or increase delivery resources."
            if capacity_feasible is False
            else "Capacity fit is unconfirmed due to limited staffing inputs."
        )
        net_note = "profitable" if monthly_net >= 0 else "loss-making"
        margin_target = max(35, min(60, int(round(margin_pct)) if margin_pct > 0 else 40))

        report["executionPlan"] = (
            f"Build a focused MVP for {service_name.lower()} using a {delivery_model.lower()} model and this flow: {how_it_works}. "
            f"Acquire first customers through {primary_channel}, then scale only when conversion is steady and contribution margin stays above {margin_target}% "
            f"(current baseline is {net_note}, margin {round(margin_pct, 1)}%). {capacity_note}"
        )

        # Deterministic business-fit block (always overrides AI/fallback values).
        monthly_revenue = float(metrics.get("monthlyRevenue") or 0)
        monthly_net = float(metrics.get("monthlyNet") or 0)
        sales_cycle_days = int(data.salesCycleDays or 0)
        gtm_channels = len(data.goToMarketChannel or [])

        revenue_indicator = "$$$" if monthly_revenue >= 10000 else "$$" if monthly_revenue >= 3000 else "$"
        if monthly_net < 0 and revenue_indicator == "$$$":
            revenue_indicator = "$$"
        if monthly_net < 0 and revenue_indicator == "$$":
            revenue_indicator = "$"

        exec_difficulty = 6
        if capacity_feasible is True:
            exec_difficulty -= 1
        elif capacity_feasible is False:
            exec_difficulty += 2
        if margin_pct >= 50:
            exec_difficulty -= 1
        elif margin_pct < 25:
            exec_difficulty += 2
        if monthly_net < 0:
            exec_difficulty += 1
        if macro_score < 45:
            exec_difficulty += 1
        exec_difficulty = max(1, min(10, exec_difficulty))

        go_to_market = 5
        if gtm_channels >= 3:
            go_to_market += 2
        elif gtm_channels >= 2:
            go_to_market += 1
        if sales_cycle_days <= 14:
            go_to_market += 2
        elif sales_cycle_days <= 30:
            go_to_market += 1
        elif sales_cycle_days > 60:
            go_to_market -= 1
        if cpc >= 75:
            go_to_market -= 1
        if demand >= 65:
            go_to_market += 1
        go_to_market = max(1, min(10, go_to_market))
        currency_code, _ = ValidationReportService._currency_from_location(data.targetLocation)

        report["businessFit"] = {
            "revenuePotential": {
                "indicator": revenue_indicator,
                "description": (
                    f"Deterministic from projected monthly revenue ({ValidationReportService._format_money(monthly_revenue, currency_code)}) and net "
                    f"position ({'positive' if monthly_net >= 0 else 'negative'})."
                ),
            },
            "executionDifficulty": {
                "score": exec_difficulty,
                "description": (
                    f"Deterministic from margin ({round(margin_pct, 1)}%), capacity fit "
                    f"({capacity_note.lower()}), and macro pressure ({macro_score}/100)."
                ),
            },
            "goToMarket": {
                "score": go_to_market,
                "description": (
                    f"Deterministic from channel count ({gtm_channels}), sales cycle ({sales_cycle_days} days), "
                    f"acquisition pressure ({cpc}/100), and demand ({demand}/100)."
                ),
            },
        }

        # Deterministic value ladder (always overrides AI/fallback values).
        report["offer"] = ValidationReportService._build_value_ladder(data, summary)

        # Keep the structure but anchor framework content to real-world/deterministic metrics
        report["frameworkFit"] = [
            {
                "name": "Value Equation",
                "overallScore": max(1, min(10, round(summary.get("validationScore", 50) / 10))),
                "scores": [
                    {"name": "Dream Outcome", "score": max(1, min(10, round(demand / 10))), "maxScore": 10},
                    {"name": "Perceived Likelihood", "score": 8 if capacity_feasible is True else 5 if capacity_feasible is None else 3, "maxScore": 10},
                    {"name": "Time Delay", "score": max(1, min(10, 10 - min(9, int((data.salesCycleDays or 0) / 10)))), "maxScore": 10},
                    {"name": "Effort & Sacrifice", "score": max(1, min(10, 10 - min(9, int((data.paymentTermsDays or 0) / 10)))), "maxScore": 10},
                ],
            },
            {
                "name": "Market Position",
                "description": (
                    f"Positioned as a {data.deliveryModel} offer in {data.industry} for {data.targetMarket or 'selected'} "
                    f"customers in {data.targetLocation}, with market score {market_score}/100 and competition {competition_label}."
                ),
            },
            {
                "name": "ACP Framework",
                "scores": [
                    {"name": "Audience", "score": max(1, min(10, round(demand / 10))), "maxScore": 10},
                    {"name": "Community", "score": max(1, min(10, round((100 - cpc) / 10))), "maxScore": 10},
                    {"name": "Product", "score": 8 if monthly_net >= 0 else 5, "maxScore": 10},
                ],
            },
        ]

    @staticmethod
    async def _apply_keyword_intel(report: dict, data: ValidationReportCreate) -> None:
        """Overwrite keyword/trend sections with live DataForSEO data when available."""
        keyword_data = await KeywordIntelService.get_top_keywords(data)
        if not keyword_data:
            report["topKeywords"] = [{
                "keyword": "Live keyword data unavailable",
                "volume": "N/A",
                "competition": "N/A",
            }]
            report["trendKeyword"] = "N/A"
            report["trendVolume"] = "N/A"
            report["trendGrowth"] = "N/A"
            report["keywordDataSource"] = "unavailable"
            return

        report["topKeywords"] = keyword_data.get("topKeywords", report.get("topKeywords", []))
        report["trendKeyword"] = keyword_data.get("trendKeyword", report.get("trendKeyword"))
        report["trendVolume"] = keyword_data.get("trendVolume", report.get("trendVolume"))
        if keyword_data.get("trendGrowth") is not None:
            report["trendGrowth"] = keyword_data.get("trendGrowth")
        report["keywordDataSource"] = keyword_data.get("source", "dataforseo")

    @staticmethod
    async def _apply_community_intel(report: dict, data: ValidationReportCreate) -> None:
        """Overwrite community signals with live/unavailable statuses only."""
        community = await CommunityIntelService.get_community_signals(data)
        report["communitySignals"] = community.get("signals", [])
        report["communityDataSource"] = community.get("sourceStatus", {})
    
    @staticmethod
    async def _generate_ai_report(data: ValidationReportCreate) -> dict:
        """Generate comprehensive report using AI"""
        
        # Build prompt for AI
        prompt = f"""You are an expert business analyst. Analyze this business/product idea and generate a comprehensive validation report.

IDEA DETAILS:
- Type: {data.ideaType}
- Name: {data.ideaName}
- Business Type: {data.businessType or 'Not provided'}
- Founder Availability (hrs/week): {data.founderAvailabilityHoursPerWeek if data.founderAvailabilityHoursPerWeek is not None else 'Not provided'}
- Stage: {data.stage or 'idea'}
- Description: {data.ideaDescription}
- Industry: {data.industry} ({data.subIndustry or 'General'})
- Problem Solved: {data.problemSolved}
- Problem Type: {', '.join(data.problemType) if data.problemType else 'Not provided'}
- Problem Frequency: {data.problemFrequency or 'Not provided'}
- Target Audience: {data.targetAudience}
- Customer Segment: {data.customerSegment or 'Not provided'}
- Current Alternatives: {data.currentAlternatives or 'Not provided'}
- Urgency Level: {data.urgencyLevel}
- How It Works: {data.howItWorks}
- Service Type: {data.serviceType or 'Not provided'}
- Delivery Model: {data.deliveryModel}
- Pricing Model: {data.pricingModel or 'Not provided'}
- Price Amount: {data.priceAmount if data.priceAmount is not None else 'Not provided'}
- Deliverable Unit: {data.deliverableUnit or 'Not provided'}
- Package Tiers: {data.packageTiers or 'Not provided'}
- Target Market: {data.targetMarket}
- Target Location: {data.targetLocation}
- Customer Budget: {data.customerBudget}
- Go-To-Market Channels: {', '.join(data.goToMarketChannel)}
- Expected Units/Month: {data.expectedUnitsPerMonth if data.expectedUnitsPerMonth is not None else 'Not provided'}
- Expected Customers: {data.expectedCustomers if data.expectedCustomers is not None else 'Not provided'}
- Sales Cycle (days): {data.salesCycleDays if data.salesCycleDays is not None else 'Not provided'}
- Payment Terms (days): {data.paymentTermsDays if data.paymentTermsDays is not None else 'Not provided'}
- Variable Cost Per Unit: {data.variableCostPerUnit if data.variableCostPerUnit is not None else 'Not provided'}
- Fixed Monthly Costs: {data.fixedMonthlyCosts if data.fixedMonthlyCosts is not None else 'Not provided'}
- Founder Draw Monthly: {data.founderDrawMonthly if data.founderDrawMonthly is not None else 'Not provided'}
- Contractor Costs Monthly: {data.contractorCostsMonthly if data.contractorCostsMonthly is not None else 'Not provided'}
- Staff Count: {data.staffCount if data.staffCount is not None else 'Not provided'}
- Capacity Per Staff/Month: {data.capacityPerStaffPerMonth if data.capacityPerStaffPerMonth is not None else 'Not provided'}
- Cash Buffer: {data.cashBuffer if data.cashBuffer is not None else 'Not provided'}
- Upfront Costs: {data.upfrontCosts if data.upfrontCosts is not None else 'Not provided'}

Generate a JSON response with this EXACT structure (all fields required):
{{
    "title": "A compelling title for the idea",
    "tags": ["3-5 tags like 'Perfect Timing', 'Strong Market', 'High Potential'"],
    "description": "2-3 paragraphs describing the idea's potential, market context, and key opportunities",
    "scores": {{
        "opportunity": {{"value": 1-10, "label": "description", "description": "why this score"}},
        "problem": {{"value": 1-10, "label": "description", "description": "why this score"}},
        "feasibility": {{"value": 1-10, "label": "description", "description": "why this score"}},
        "whyNow": {{"value": 1-10, "label": "description", "description": "why this score"}}
    }},
    "businessFit": {{
        "revenuePotential": {{"indicator": "$" to "$$$", "description": "revenue potential analysis"}},
        "executionDifficulty": {{"score": 1-10, "description": "execution analysis"}},
        "goToMarket": {{"score": 1-10, "description": "GTM analysis"}}
    }},
    "offer": [
        {{"tier": "LEAD MAGNET", "name": "product name", "price": "Free", "description": "what it is"}},
        {{"tier": "FRONTEND", "name": "product name", "price": "$X/month", "description": "what it is"}},
        {{"tier": "CORE", "name": "product name", "price": "$X-Y/month", "description": "what it is"}}
    ],
    "whyNow": "2-3 sentences on why now is the right time",
    "proofSignals": "2-3 sentences on market demand signals",
    "marketGap": "2-3 sentences on the market opportunity",
    "executionPlan": "2-3 sentences on MVP and growth strategy",
    "frameworkFit": [
        {{"name": "Value Equation", "overallScore": 1-10, "scores": [{{"name": "metric", "score": 1-10}}]}},
        {{"name": "Market Position", "description": "analysis"}},
        {{"name": "ACP Framework", "scores": [{{"name": "Audience", "score": 1-10}}, {{"name": "Community", "score": 1-10}}, {{"name": "Product", "score": 1-10}}]}}
    ],
    "categorization": {{
        "type": "SaaS/Service/Marketplace/etc",
        "market": "B2C/B2B/B2G",
        "target": "target segment",
        "trendAnalysis": "trend insights"
    }},
    "communitySignals": [
        {{"platform": "Reddit", "details": "X subreddits - Y members", "score": 1-10}},
        {{"platform": "Facebook", "details": "X groups - Y members", "score": 1-10}},
        {{"platform": "YouTube", "details": "X channels", "score": 1-10}}
    ],
    "topKeywords": [
        {{"keyword": "keyword1", "volume": "X.XK", "competition": "LOW/MEDIUM/HIGH", "growth": "+XX%"}},
        {{"keyword": "keyword2", "volume": "X.XK", "competition": "LOW/MEDIUM/HIGH"}}
    ],
    "trendKeyword": "main keyword",
    "trendVolume": "X.XK",
    "trendGrowth": "+XX%",
    "buildPrompts": ["Ad Creatives", "Brand Package", "Landing Page", "Email Sequence"],
    "suggestedQuestions": [
        "What problem does this solve?",
        "How big is the market opportunity?",
        "What's the competitive landscape?",
        "How hard is it to build?",
        "What's the revenue model?",
        "What are the key risks?"
    ]
}}

Be realistic but constructive. Base scores on the information provided. Return ONLY valid JSON."""

        try:
            if LLM_AVAILABLE:
                llm_key = os.environ.get("LLM_KEY")
                if llm_key:
                    chat = LlmChat(
                        api_key=llm_key,
                        session_id="validation-report"
                    ).with_model("openai", "gpt-4o")
                    response = await chat.send_message(
                        UserMessage(content=prompt)
                    )
                    
                    # Parse JSON from response
                    response_text = response.content if hasattr(response, 'content') else str(response)
                    
                    # Extract JSON from response (handle markdown code blocks)
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0]
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0]
                    
                    report = json.loads(response_text.strip())
                    return report
        except Exception as e:
            print(f"AI report generation failed: {e}")
        
        # Fallback to rule-based generation
        return ValidationReportService._generate_fallback_report(data)
    
    @staticmethod
    def _generate_fallback_report(data: ValidationReportCreate) -> dict:
        """Generate a comprehensive report without AI (fallback)"""
        
        # Calculate scores based on input quality
        problem_len = len(data.problemSolved)
        desc_len = len(data.ideaDescription)
        audience_len = len(data.targetAudience)
        how_len = len(data.howItWorks)
        
        # Opportunity score
        opp_score = min(9, 5 + (desc_len // 50) + (1 if data.urgencyLevel == "high" else 0))
        
        # Problem score
        prob_score = min(9, 4 + (problem_len // 40) + (2 if data.urgencyLevel == "high" else 1 if data.urgencyLevel == "medium" else 0))
        
        # Feasibility score
        easy_models = ["digital", "saas", "mobile app"]
        feas_score = 7 if data.deliveryModel.lower() in easy_models else 5
        feas_score = min(9, feas_score + (how_len // 100))
        
        # Why Now score
        why_now_score = 8 if data.urgencyLevel == "high" else 6 if data.urgencyLevel == "medium" else 4
        why_now_score = min(9, why_now_score + len(data.goToMarketChannel) // 2)
        
        # Revenue indicator
        rev_indicator = "$$$" if data.customerBudget == "high" else "$$" if data.customerBudget == "medium" else "$"
        
        # Execution difficulty
        exec_diff = 5 if data.deliveryModel.lower() in easy_models else 7
        
        # GTM score
        gtm_score = min(9, 5 + len(data.goToMarketChannel))
        
        return {
            "title": data.ideaName,
            "tags": ValidationReportService._generate_tags(data, opp_score, prob_score),
            "description": ValidationReportService._structured_description(
                data.ideaDescription,
                data.customerSegment,
                data.targetLocation,
                data.targetMarket,
                data.problemSolved,
            ),
            "disclaimer": "*Analysis and scores are based on provided information and general market assumptions. Results vary by execution and market conditions.",
            "scores": {
                "opportunity": {
                    "value": opp_score,
                    "label": "Exceptional" if opp_score >= 8 else "Good" if opp_score >= 6 else "Moderate",
                    "description": f"Strong market opportunity in {data.industry}"
                },
                "problem": {
                    "value": prob_score,
                    "label": "High Pain" if prob_score >= 7 else "Moderate Pain" if prob_score >= 5 else "Low Pain",
                    "description": f"Problem urgency is {data.urgencyLevel}"
                },
                "feasibility": {
                    "value": feas_score,
                    "label": "Achievable" if feas_score >= 7 else "Challenging" if feas_score >= 5 else "Difficult",
                    "description": f"{data.deliveryModel} delivery model assessment"
                },
                "whyNow": {
                    "value": why_now_score,
                    "label": "Perfect Timing" if why_now_score >= 8 else "Good Timing" if why_now_score >= 6 else "Timing Concerns",
                    "description": "Market timing analysis"
                }
            },
            "businessFit": {
                "revenuePotential": {
                    "indicator": rev_indicator,
                    "description": f"Target customers have {data.customerBudget} budget capacity"
                },
                "executionDifficulty": {
                    "score": exec_diff,
                    "description": f"Building a {data.deliveryModel} requires moderate technical execution"
                },
                "goToMarket": {
                    "score": gtm_score,
                    "description": f"Planned channels: {', '.join(data.goToMarketChannel[:3])}"
                }
            },
            "offer": [
                {
                    "tier": "LEAD MAGNET",
                    "name": f"{data.ideaName} Calculator",
                    "price": "Free",
                    "description": f"Free tool to estimate value for {data.targetAudience}"
                },
                {
                    "tier": "FRONTEND",
                    "name": f"Basic {data.ideaName}",
                    "price": "$15/month",
                    "description": f"Entry-level offering for individual {data.targetMarket} customers"
                },
                {
                    "tier": "CORE",
                    "name": f"Pro {data.ideaName}",
                    "price": "$30-50/month",
                    "description": "Full-featured solution with premium capabilities"
                }
            ],
            "whyNow": f"Now is an opportune time to launch in the {data.industry} market. With {data.urgencyLevel} urgency around {data.problemSolved[:100]}..., early movers can capture significant market share.",
            "proofSignals": f"Market research indicates strong demand signals in {data.targetLocation}. The {data.targetMarket} segment shows active interest in solutions addressing {data.problemSolved[:80]}...",
            "marketGap": f"Current solutions in {data.industry} don't fully address the needs of {data.targetAudience}. This creates a clear opportunity to differentiate through {data.deliveryModel} delivery.",
            "executionPlan": f"Launch MVP focused on core value: {data.howItWorks[:100]}... Start with {data.goToMarketChannel[0] if data.goToMarketChannel else 'direct'} acquisition, then expand to additional channels.",
            "frameworkFit": [
                {
                    "name": "Value Equation",
                    "overallScore": (opp_score + prob_score) // 2,
                    "scores": [
                        {"name": "Dream Outcome", "score": opp_score, "maxScore": 10},
                        {"name": "Perceived Likelihood", "score": feas_score, "maxScore": 10},
                        {"name": "Time Delay", "score": 7, "maxScore": 10},
                        {"name": "Effort & Sacrifice", "score": 6, "maxScore": 10}
                    ]
                },
                {
                    "name": "Market Position",
                    "description": f"Positioned as a {data.deliveryModel} solution in the {data.industry} space targeting {data.targetMarket} customers."
                },
                {
                    "name": "ACP Framework",
                    "scores": [
                        {"name": "Audience", "score": min(8, 5 + audience_len // 30), "maxScore": 10},
                        {"name": "Community", "score": 6, "maxScore": 10},
                        {"name": "Product", "score": feas_score, "maxScore": 10}
                    ]
                }
            ],
            "categorization": {
                "type": data.deliveryModel.upper() if data.deliveryModel.lower() in ["saas", "service", "marketplace"] else "SaaS",
                "market": data.targetMarket,
                "target": data.targetAudience[:50] if len(data.targetAudience) > 50 else data.targetAudience,
                "trendAnalysis": f"The {data.industry} market in {data.targetLocation} shows promising growth potential for {data.deliveryModel} solutions."
            },
            "communitySignals": [
                {"platform": "Reddit", "details": "Multiple relevant subreddits", "score": 7},
                {"platform": "Facebook", "details": "Active groups in niche", "score": 6},
                {"platform": "YouTube", "details": "Content creators covering topic", "score": 7},
                {"platform": "LinkedIn", "details": "Professional discussions", "score": 6}
            ],
            "topKeywords": [
                {"keyword": f"{data.industry.lower()} {data.deliveryModel.lower()}", "volume": "2.4K", "competition": "MEDIUM", "growth": "+45%"},
                {"keyword": f"{data.ideaName.lower().split()[0]} solution", "volume": "1.8K", "competition": "LOW", "growth": "+32%"},
                {"keyword": f"best {data.industry.lower()} tools", "volume": "5.1K", "competition": "HIGH"}
            ],
            "trendKeyword": f"{data.industry.lower()} {data.deliveryModel.lower()}",
            "trendVolume": "2.4K",
            "trendGrowth": "+45%",
            "buildPrompts": ["Ad Creatives", "Brand Package", "Landing Page", "Email Sequence", "Social Media Strategy"],
            "suggestedQuestions": [
                "What problem does this solve?",
                "How big is the market opportunity?",
                "What's the competitive landscape?",
                "How hard is it to build?",
                "What's the revenue model?",
                "What are the key risks?"
            ]
        }
    
    @staticmethod
    def _generate_tags(data: ValidationReportCreate, opp_score: int, prob_score: int) -> List[str]:
        """Generate relevant tags based on analysis"""
        tags = []
        
        if opp_score >= 8:
            tags.append("High Opportunity")
        if prob_score >= 7:
            tags.append("Strong Problem-Fit")
        if data.urgencyLevel == "high":
            tags.append("Perfect Timing")
        if data.customerBudget == "high":
            tags.append("Premium Market")
        if len(data.goToMarketChannel) >= 3:
            tags.append("Multi-Channel Ready")
        if data.deliveryModel.lower() in ["saas", "subscription"]:
            tags.append("Recurring Revenue")
        if data.targetMarket == "B2B":
            tags.append("B2B Opportunity")
        
        # Ensure at least 3 tags
        default_tags = ["Market Potential", "Growth Opportunity", "Validated Concept"]
        while len(tags) < 3:
            for t in default_tags:
                if t not in tags:
                    tags.append(t)
                    break
        
        return tags[:5]
    
    @staticmethod
    async def _increment_engagement(workspace_id: str, user_id: str):
        """Increment user's validation engagement counter"""
        db = get_db()
        
        await db.user_engagement.update_one(
            {"user_id": user_id, "workspace_id": workspace_id},
            {
                "$inc": {"validation_count": 1},
                "$set": {"last_validation": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )
    
    @staticmethod
    async def get_user_reports(workspace_id: str, user_id: str, limit: int = 50) -> List[dict]:
        """Get all validation reports for a user"""
        db = get_db()
        
        cursor = db.validation_reports.find(
            {"workspace_id": workspace_id, "user_id": user_id},
            {"_id": 0}
        ).sort("createdAt", -1).limit(limit)
        
        reports = await cursor.to_list(length=limit)
        
        # Transform to list items
        items = []
        for r in reports:
            deterministic_score_100 = r.get("report", {}).get("deterministicSummary", {}).get("validationScore")
            if deterministic_score_100 is not None:
                opp_score = max(1, min(10, round(float(deterministic_score_100) / 10)))
            else:
                opp_score = r.get("report", {}).get("scores", {}).get("opportunity", {}).get("value", 5)
            verdict = "PASS" if opp_score >= 7 else "PIVOT" if opp_score >= 5 else "KILL"
            
            items.append({
                "id": r["id"],
                "ideaName": r.get("ideaInput", {}).get("ideaName", "Untitled"),
                "ideaType": r.get("ideaInput", {}).get("ideaType", "business"),
                "status": r.get("status", "pending"),
                "overallScore": opp_score,
                "verdict": verdict,
                "createdAt": r.get("createdAt", "")
            })
        
        return items
    
    @staticmethod
    async def get_report_by_id(report_id: str, workspace_id: str) -> Optional[dict]:
        """Get a specific validation report"""
        db = get_db()
        
        report = await db.validation_reports.find_one(
            {"id": report_id, "workspace_id": workspace_id},
            {"_id": 0}
        )
        
        return report
    
    @staticmethod
    async def update_report_status(
        report_id: str, 
        workspace_id: str, 
        status: ReportStatus
    ) -> Optional[dict]:
        """Update report status (accept/reject)"""
        db = get_db()
        
        result = await db.validation_reports.find_one_and_update(
            {"id": report_id, "workspace_id": workspace_id},
            {
                "$set": {
                    "status": status.value,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            },
            return_document=True
        )
        
        if result:
            result.pop("_id", None)
            
            # Log event
            await db.intelligence_events.insert_one({
                "id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "type": f"validation.report_{status.value}",
                "data": {"report_id": report_id},
                "occurredAt": datetime.now(timezone.utc).isoformat()
            })
        
        return result
    
    @staticmethod
    async def modify_and_regenerate(
        report_id: str,
        workspace_id: str,
        user_id: str,
        new_data: ValidationReportCreate
    ) -> dict:
        """Modify input data and regenerate report"""
        db = get_db()
        
        # Generate new report
        report = await ValidationReportService._generate_ai_report(new_data)
        deterministic_summary = await ValidationReportService._calculate_deterministic_summary(new_data)
        report["deterministicSummary"] = deterministic_summary
        report["scores"] = ValidationReportService._build_deterministic_score_cards(
            new_data,
            deterministic_summary
        )
        ValidationReportService._apply_real_world_narrative(report, new_data, deterministic_summary)
        await ValidationReportService._apply_keyword_intel(report, new_data)
        await ValidationReportService._apply_community_intel(report, new_data)
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Update existing report
        result = await db.validation_reports.find_one_and_update(
            {"id": report_id, "workspace_id": workspace_id},
            {
                "$set": {
                    "ideaInput": new_data.model_dump() if hasattr(new_data, 'model_dump') else new_data.dict(),
                    "report": report,
                    "status": ReportStatus.PENDING.value,
                    "updatedAt": now
                }
            },
            return_document=True
        )
        
        if result:
            result.pop("_id", None)
            
            # Log event
            await db.intelligence_events.insert_one({
                "id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "type": "validation.report_modified",
                "data": {"report_id": report_id},
                "occurredAt": now
            })
        
        return result
    
    @staticmethod
    async def get_engagement_stats(workspace_id: str, user_id: str) -> dict:
        """Get user's engagement statistics"""
        db = get_db()
        
        # Get engagement counter
        engagement = await db.user_engagement.find_one(
            {"user_id": user_id, "workspace_id": workspace_id},
            {"_id": 0}
        )
        
        # Count reports by status
        pipeline = [
            {"$match": {"workspace_id": workspace_id, "user_id": user_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_counts = {}
        async for doc in db.validation_reports.aggregate(pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        return {
            "totalValidations": engagement.get("validation_count", 0) if engagement else 0,
            "acceptedCount": status_counts.get("accepted", 0),
            "rejectedCount": status_counts.get("rejected", 0),
            "pendingCount": status_counts.get("pending", 0)
        }
    
    @staticmethod
    async def delete_report(report_id: str, workspace_id: str) -> bool:
        """Delete a validation report"""
        db = get_db()
        
        result = await db.validation_reports.delete_one(
            {"id": report_id, "workspace_id": workspace_id}
        )
        
        return result.deleted_count > 0









