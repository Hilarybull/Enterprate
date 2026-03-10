# Validation Dashboard Explainer

This document explains, in plain language, how each section on the Validation dashboard is produced today.

## 1) Overall Validation Score (/100)

Source:
- `backend/app/services/validation_report_service.py`
- Method: `_calculate_deterministic_summary`

The score is deterministic (not AI-scored).

Formula:
- `CoreScore` is computed from 7 dimensions (D1-D7) with fixed weights.
- `ExternalContextScore = 0.60 * MarketScore + 0.40 * MacroScore`
- External influence is capped at 10%.
- `ValidationScore = 0.90 * CoreScore + 0.10 * ExternalContextScore`
- Final score is clamped to `0..100`.

## 2) Dimension Scores (D1-D7)

Dimension weights:
- D1 Margin Strength: `20%`
- D2 Demand Realism: `15%`
- D3 Capacity Feasibility: `20%`
- D4 Fixed Cost Impact: `15%`
- D5 Payment Terms Impact: `10%`
- D6 Diversification Benefit: `10%`
- D7 Proof Strength: `10%`

How each dimension is determined:
- D1: from contribution margin bands.
- D2: from units/customers presence plus market demand adjustment.
- D3: from capacity utilization (under/near/over capacity).
- D4: from fixed-cost-to-revenue ratio.
- D5: from payment terms and sales cycle penalties.
- D6: from channel count and customer concentration.
- D7: from proof/completeness fields in the submitted form.

UI behavior:
- The dashboard shows dimension name + score.
- "Why this value" text is dynamic by score band (strong/moderate/weak).

## 3) Deterministic Baseline Model Cards

These come from your form inputs.

- Monthly Revenue: `expectedUnitsPerMonth * priceAmount`
- Monthly Variable Cost: `expectedUnitsPerMonth * variableCostPerUnit`
- Monthly Fixed Cost: `fixedMonthlyCosts + founderDrawMonthly + contractorCostsMonthly`
- Monthly Net: `MonthlyRevenue - MonthlyVariableCost - MonthlyFixedCost`
- Contribution Margin %: `((Revenue - VariableCost) / Revenue) * 100` (or 0 if revenue is 0)
- Break-even Revenue: derived when `priceAmount > variableCostPerUnit`
- Capacity Feasible: compares expected units to total monthly capacity
- Runway (months): `cashBuffer / abs(monthlyNet)` when monthly net is negative

## 4) Market Score

Source:
- `backend/app/services/market_data_service.py`
- Method: `get_market_profile`

Current behavior:
- Uses deterministic baseline tables (industry, delivery model, market type, location) + rule adjustments.
- Optional override file via `MARKET_DATA_OVERRIDES_FILE`.

Formula:
- `MarketScore = 0.40*demand + 0.25*(100-competition) + 0.20*(100-cpcPressure) + 0.15*macro`

Note:
- This is still baseline-rules driven unless override data is provided.

## 5) Macro Score

Source:
- `backend/app/services/macro_data_service.py`
- Method: `get_macro_profile`

Location policy:
- US -> FRED API
- Non-US country -> World Bank API
- Failure/missing key -> fallback defaults

Normalization:
- GDP growth: higher is better
- Inflation: lower is better
- Unemployment: lower is better
- Policy rate: lower is better

Formula:
- `MacroScore = 0.30*GDP + 0.30*Inflation + 0.25*Unemployment + 0.15*PolicyRate`

## 6) Validation Score Cards (0-10)

Source:
- `validation_report_service.py`
- Method: `_build_deterministic_score_cards`

Cards:
- Opportunity: derived from overall validation score
- Problem: urgency + frequency + problem clarity logic
- Feasibility: economics + capacity + execution friction
- Why Now: urgency + commercial timing friction

UI:
- Explanations/formulas are shown through `i` tooltips.

## 7) Business Fit

Source:
- `validation_report_service.py`
- Method: `_apply_real_world_narrative`

Metrics:
- Revenue Potential (`$`, `$$`, `$$$`) from projected monthly revenue and net sign
- Execution Difficulty (1-10) from margin, capacity fit, net, macro pressure
- Go-To-Market (1-10) from channels, sales cycle, CPC pressure, demand

## 8) Value Ladder

Source:
- `validation_report_service.py`
- Method: `_build_value_ladder`

Built deterministically from:
- pricing model, unit, base price, variable cost, expected customers/units, monthly revenue, location currency.

Produces 3 tiers:
- Lead Magnet
- Frontend
- Core

## 9) Narrative Blocks

Source:
- `validation_report_service.py`
- Method: `_apply_real_world_narrative`

Generated fields:
- Why Now
- Proof & Signals
- Market Gap
- Execution Plan

Current formatting improvements:
- Source labels are humanized (`world_bank` -> `World Bank`).
- Location formatting is normalized (`uk` -> `UK`, `us` -> `US`).
- Execution plan wording was rewritten to avoid clipped/awkward text.

## 10) Keyword Trend and Top Keywords

Source:
- `backend/app/services/keyword_intel_service.py`

Data source:
- DataForSEO API (with `DATAFORSEO_LOGIN` + `DATAFORSEO_PASSWORD`)

Difference:
- Keyword Trend: primary keyword snapshot (volume + growth)
- Top Keywords: additional high-signal keyword list

## 11) Community Signals

Source:
- `backend/app/services/community_intel_service.py`

Possible live sources:
- Reddit
- YouTube (if key set)
- Facebook (if token set)
- LinkedIn proxy via Bing search API (if key set)

Unavailable sources are shown as unavailable/low score rather than fabricated values.

## 12) Decision Simulation

Scope:
- Monthly simulation (not yearly).

What it does:
- Applies predefined scenario changes to monthly revenue/cost/capacity assumptions.
- Shows monthly net impact per scenario.

Formula shown in UI tooltip:
- `Monthly Net = Monthly Revenue - Monthly Variable Costs - Monthly Fixed Costs` (after scenario adjustment)

## 13) Proof Strength Simulation (Dashboard UX)

UI behavior:
- User can set Proof Level and Proof Count.
- Dashboard previews:
  - projected proof score
  - estimated validation score impact

Important:
- This is a preview simulation on the dashboard, not a persisted write-back to database unless explicit save logic is added.

## 14) Why a field can show unavailable/N-A

Common reasons:
- Missing required numeric inputs
- Missing API keys
- API quota/rate limit
- API timeout/fetch failure

This is intentional so the system does not hallucinate data.

## 15) Required/Useful Environment Keys

- `FRED_API_KEY`
- `DATAFORSEO_LOGIN`
- `DATAFORSEO_PASSWORD`
- `YOUTUBE_API_KEY` (optional)
- `FACEBOOK_GRAPH_TOKEN` (optional)
- `BING_SEARCH_API_KEY` (optional)
- `CLAUDE_API_KEY` (optional for chat/suggestions, not deterministic scoring)
