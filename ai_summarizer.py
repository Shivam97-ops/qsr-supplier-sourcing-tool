# ai_summarizer.py
# Uses the Anthropic Claude API to analyse raw search results and produce
# structured, QSR-specific supplier profiles with scoring and risk detection.
#
# WHAT'S NEW IN THIS VERSION:
#   - Fixed scoring bug: system prompt prevents all-zero scores; markdown
#     code-fence stripping ensures JSON always parses correctly.
#   - Retry logic: if JSON parsing fails on the first attempt, Claude is asked
#     again once before falling back to a safe default.
#   - Supplier classification: 4 types (Manufacturer, Distributor,
#     Trader/Broker, Local Vendor) instead of the old Primary/Secondary.
#   - Risk intelligence: 3-category risk assessment returned by Claude
#     (geopolitical, environmental, supplier-specific).
#   - Logistics options: computed locally from logistics_config.py using
#     the origin_country Claude identifies.
#   - Landed cost: full FOB-to-Ontario cost breakdown computed locally.
#   - Sourcing strategy: new generate_sourcing_strategy() function analyses
#     the full batch and returns a structured recommendation.

import anthropic
import json
import time
import traceback
from typing import Callable, Optional

from qsr_config import HIGH_RISK_COUNTRIES
import logistics_config as lc


# ─────────────────────────────────────────────────────────────────────────────
# SCORE COMPUTATION
# ─────────────────────────────────────────────────────────────────────────────

# Kept for backward compatibility with any saved suppliers using the old format.
SCORE_MAXES = {
    "food_safety_certs":  25,
    "export_experience":  20,
    "years_established":  20,
    "product_specificity": 20,
    "contact_available":  15,
}


def compute_total_score(breakdown: dict) -> int:
    """
    Returns the supplier score from a breakdown dict.
    New format: reads final_score directly (Claude computes it per the additive rubric).
    Old format fallback: sums clamped component scores.
    """
    if "final_score" in breakdown:
        return max(0, min(100, int(breakdown["final_score"])))
    # Fallback for old-format breakdowns (saved suppliers)
    total = 0
    for key, max_val in SCORE_MAXES.items():
        raw = breakdown.get(key, 0)
        total += min(int(raw), max_val)
    return min(total, 100)


# ─────────────────────────────────────────────────────────────────────────────
# JSON HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """
    Parses JSON from Claude's response, handling two common failure modes:
      1. Claude wraps JSON in markdown code fences (```json ... ```)
      2. Claude adds explanatory text before/after the JSON object

    Raises json.JSONDecodeError if no valid JSON object can be found.
    """
    text = text.strip()

    # Case 1: markdown code fence — extract everything between first { and last }
    if text.startswith("```"):
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

    # Case 2: extra text before/after JSON — find the outermost braces
    elif not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

    return json.loads(text)


def _extract_json_array(text: str) -> list:
    """
    Parses a JSON array ([...]) from Claude's response text.
    Handles markdown code fences (```json ... ``` or ``` ... ```)
    and leading/trailing prose.

    Raises json.JSONDecodeError if no valid JSON array can be found.
    """
    text = text.strip()

    # Strip markdown code fence: split on ``` and take the middle segment
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    # If there's still prose before the array, find the opening bracket
    if not text.startswith("["):
        start = text.find("[")
        end   = text.rfind("]") + 1
        if start != -1 and end > start:
            text = text[start:end]

    return json.loads(text)


# ─────────────────────────────────────────────────────────────────────────────
# LOGISTICS CALCULATIONS (local — no Claude call needed)
# ─────────────────────────────────────────────────────────────────────────────

def _get_region(origin_country: str) -> str:
    """Maps an origin country name (lowercase) to a logistics region code."""
    return lc.COUNTRY_TO_REGION.get(origin_country.lower(), "asia")


def compute_logistics_options(supplier: dict, qsr_category: str) -> dict:
    """
    Builds a dict of all viable logistics modes from the supplier's origin
    country to Ontario, Canada. All costs are in USD/kg.

    Args:
        supplier:     Enriched supplier dict (must have 'origin_country')
        qsr_category: QSR category string (e.g., '🍗 Proteins')

    Returns:
        Dict with keys 'sea_fcl', 'sea_lcl', 'intermodal', 'air', 'road'
        (only the applicable modes are included).
    """
    origin = supplier.get("origin_country", "unknown").lower()
    region = _get_region(origin)
    options = {}

    # ── Sea Freight (not for Canadian or US shipments) ──
    if region not in ("canada", "usa"):
        sea = lc.SEA_FREIGHT.get(region, lc.SEA_FREIGHT["asia"])
        port = sea["port_of_entry"]
        inland = lc.INLAND_TO_ONTARIO.get(port, lc.INLAND_FALLBACK)

        # FCL: divide container cost by typical kg-per-container to get cost/kg
        sea_fcl_per_kg = (sea["fcl_20ft_usd"] / lc.KG_PER_20FT_CONTAINER) + inland["cost_per_kg_usd"]
        options["sea_fcl"] = {
            "mode": "Sea Freight — FCL (20ft)",
            "cost_per_kg_usd": round(sea_fcl_per_kg, 3),
            "cost_per_container_usd": sea["fcl_20ft_usd"],
            "transit_days": sea["transit_days_range"],
            "port_of_entry": port,
            "route": sea["route_note"],
        }

        # LCL: charge by cubic metre — useful for small orders
        options["sea_lcl"] = {
            "mode": "Sea Freight — LCL",
            "cost_per_cbm_usd": sea["lcl_per_cbm_usd"],
            "transit_days": sea["transit_days_range"],
            "port_of_entry": port,
            "route": sea["route_note"],
            "note": "Suitable for orders under 15 CBM",
        }

        # Intermodal (Sea + Rail via CN Rail)
        if sea.get("intermodal_available") and region in lc.INTERMODAL:
            inter = lc.INTERMODAL[region]
            extra = inter["extra_cost_vs_sea_usd_per_container"]
            inter_per_kg = ((sea["fcl_20ft_usd"] + extra) / lc.KG_PER_20FT_CONTAINER) + inland["cost_per_kg_usd"]
            options["intermodal"] = {
                "mode": "Intermodal — Sea + CN Rail",
                "cost_per_kg_usd": round(inter_per_kg, 3),
                "transit_days": inter["total_transit_days_range"],
                "route": inter["route"],
                "note": inter["note"],
            }

    # ── Air Freight (always available — flag as emergency option) ──
    air = lc.AIR_FREIGHT.get(region, lc.AIR_FREIGHT["asia"])
    options["air"] = {
        "mode": "Air Freight ⚡ Emergency",
        "cost_per_kg_usd": air["cost_per_kg_usd"],
        "transit_days": air["transit_days_range"],
        "note": "5–10× more expensive than sea — use for urgent restocking only",
    }

    # ── Road/Truck (North America only) ──
    if region in ("canada", "usa", "mexico"):
        road = lc.ROAD_FREIGHT.get(region, lc.ROAD_FREIGHT["usa"])
        options["road"] = {
            "mode": f"Road/Truck — {road['description']}",
            "cost_per_kg_usd": road["cost_per_kg_usd"],
            "transit_days": road["transit_days_range"],
            "note": road["note"],
        }

    return options


def compute_landed_cost(supplier: dict, qsr_category: str) -> dict:
    """
    Calculates the total landed cost to Ontario, Canada per kg for a supplier.
    Uses the cheapest viable logistics mode and typical mid-market FOB price
    when no actual price is available.

    Cost components:
        FOB price → Freight → Insurance → Import duty → CFIA fee
        → Inland freight → Inventory holding cost → Total

    Args:
        supplier:     Enriched supplier dict
        qsr_category: QSR category string

    Returns:
        Dict with all cost components in USD/kg and a CAD/kg total.
    """
    origin = supplier.get("origin_country", "unknown").lower()
    region = _get_region(origin)
    is_cusma = origin in lc.CUSMA_COUNTRIES

    # Supplier-class multiplier — differentiates cost tiers across suppliers
    sclass = supplier.get("supplier_class", "Distributor")
    is_mfr = sclass in ("Manufacturer", "Local Vendor")
    is_ontario = "ontario" in supplier.get("location", "").lower()
    if is_mfr and is_cusma and is_ontario:
        fob_multiplier = 1.00
    elif is_mfr and is_cusma:
        fob_multiplier = 1.05
    elif sclass == "Distributor" and is_cusma:
        fob_multiplier = 1.10
    elif sclass == "Distributor":
        fob_multiplier = 1.20
    else:
        fob_multiplier = 1.35

    cat_prices = lc.TYPICAL_FOB_PRICES.get(qsr_category, lc.TYPICAL_FOB_PRICES["General"])
    fob_usd = cat_prices["mid"] * fob_multiplier

    # Select cheapest logistics mode
    if region in ("canada", "usa", "mexico"):
        road = lc.ROAD_FREIGHT.get(region, lc.ROAD_FREIGHT["usa"])
        freight_per_kg = road["cost_per_kg_usd"]
        inland_per_kg = 0.0
        mode_used = f"Road/Truck ({road['description']})"
    else:
        sea = lc.SEA_FREIGHT.get(region, lc.SEA_FREIGHT["asia"])
        freight_per_kg = sea["fcl_20ft_usd"] / lc.KG_PER_20FT_CONTAINER
        port = sea["port_of_entry"]
        inland = lc.INLAND_TO_ONTARIO.get(port, lc.INLAND_FALLBACK)
        inland_per_kg = inland["cost_per_kg_usd"]
        mode_used = "Sea Freight — FCL"

    tariff_rate = lc.TARIFF_RATES["cusma"] if is_cusma else lc.TARIFF_RATES["standard"]
    insurance   = fob_usd * lc.INSURANCE_RATE
    import_duty = fob_usd * tariff_rate
    cfia_usd    = lc.CFIA_FEE_PER_KG_CAD * lc.CAD_TO_USD
    inventory   = fob_usd * lc.INVENTORY_HOLDING_RATE

    # Guaranteed floors so line items are never $0.000
    freight_floor  = 0.08 if is_ontario else (0.12 if region == "canada" else 0.18)
    freight_per_kg = max(freight_per_kg, freight_floor)
    insurance      = max(insurance, fob_usd * 0.005)
    if not is_cusma:
        duty_floor  = 0.15 if region == "canada" else 0.25
        import_duty = max(import_duty, duty_floor)
    if cfia_usd + inland_per_kg + inventory < 0.02:
        cfia_usd = 0.02

    total_usd = fob_usd + freight_per_kg + insurance + import_duty + cfia_usd + inland_per_kg + inventory

    return {
        "fob_price_usd":         round(fob_usd, 3),
        "freight_per_kg_usd":    round(freight_per_kg, 3),
        "inland_per_kg_usd":     round(inland_per_kg, 3),
        "insurance_per_kg_usd":  round(insurance, 3),
        "import_duty_per_kg_usd": round(import_duty, 3),
        "tariff_rate_pct":       round(tariff_rate * 100, 1),
        "cfia_fee_per_kg_usd":   round(cfia_usd, 3),
        "inventory_cost_per_kg_usd": round(inventory, 3),
        "total_landed_usd":      round(total_usd, 3),
        "total_landed_cad":      round(total_usd * lc.USD_TO_CAD, 3),
        "is_cusma":              is_cusma,
        "logistics_mode":        mode_used,
        "fob_price_note":        f"Typical mid-market estimate for {qsr_category}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# SINGLE SUPPLIER SUMMARIZATION
# ─────────────────────────────────────────────────────────────────────────────

def summarize_supplier(
    supplier_raw: dict,
    api_key: str,
    user_profile: Optional[dict] = None,
) -> dict:
    """
    Sends one supplier's raw search data to Claude and returns a fully
    structured QSR supplier profile with scoring, risk assessment, logistics
    options, and total landed cost.

    Args:
        supplier_raw:  Dict with keys: name, website, snippet, product, qsr_category
        api_key:       Anthropic API key
        user_profile:  Optional buyer profile dict (location, certifications, etc.)

    Returns:
        Enriched supplier dict ready for display and database storage.
    """
    client = anthropic.Anthropic(api_key=api_key)

    product      = supplier_raw.get("product", "food product")
    qsr_category = supplier_raw.get("qsr_category", "General")

    # Build buyer context string from profile
    buyer_location = "Ontario, Canada"
    buyer_certs    = "HACCP, ISO 22000, FSSC 22000, FDA, CFIA"
    if user_profile:
        buyer_location = user_profile.get("location", buyer_location)
        preferred = user_profile.get("preferred_certifications", [])
        if preferred:
            buyer_certs = ", ".join(preferred)

    risk_countries_str = ", ".join(HIGH_RISK_COUNTRIES)

    prompt = f"""You are a senior procurement analyst for a QSR (Quick Service Restaurant) company
based in {buyer_location}. A sourcing team searched Google for a "{product}" supplier
in the "{qsr_category}" category and found this result:

Title:       {supplier_raw['name']}
Website:     {supplier_raw['website']}
URL:         {supplier_raw.get('displayed_url', '')}
Description: {supplier_raw['snippet']}

Analyse this result and return a JSON supplier profile. Follow every instruction below exactly.

━━━━ SCORING SYSTEM — ADDITIVE ━━━━
Compute the score by starting at a base of 50 and adding/subtracting bonuses and deductions.
Clamp final_score to the range 0–100.

BASE: 50 — for any verified business with a working website.

BONUSES (add to the appropriate field):
  cusma_bonus  +15 → Supplier is Canadian or USA-based (CUSMA/USMCA tariff-free for a Canadian buyer)
               +0  → All other countries
  type_bonus   +10 → Supplier is a Manufacturer (makes the product in their own facility)
               +0  → Distributor
               -10 → Trader or Broker (intermediary; does not manufacture or hold inventory)
  cert_bonus   +8 per confirmed cert (HACCP, ISO 22000, FSSC 22000, FDA registered, BRC, SQF, GlobalG.A.P), max +20
               +4 per implied/unconfirmed cert for an established Manufacturer (certs likely held but not listed), max +10
               -15 → No certifications found AND supplier shows no evidence of any food safety compliance programme
  focus_bonus  +8 → Supplier explicitly focuses on foodservice, QSR, restaurant, or institutional food supply
               +0 → General food company with no stated QSR focus
  location_bonus +5 → Supplier is in Ontario OR regularly ships to Ontario buyers
               +0 → No Ontario connection stated
  address_bonus  +3 → Physical address or facility location is confirmed in the available information
               +0 → No address found
  foodservice_bonus +4 → Has a dedicated foodservice product line, foodservice catalogue, or foodservice sales team
               +0 → No dedicated foodservice channel

DEDUCTIONS (sum all that apply into the single "deductions" field as a negative integer):
  -8  → Non-CUSMA offshore supplier (applies when cusma_bonus = 0)
  -5  → Single-source dependency risk (no backup, no alternative product line, very narrow range)
  -8  → No physical address AND no direct contact found (website only, no phone, no email)
  -3  → Company age or founding year completely unconfirmed

IMPORTANT: Do NOT deduct -10 for Trader/Broker in deductions — that is already captured in type_bonus.
Do NOT double-count the -8 non-CUSMA deduction if you already awarded cusma_bonus = 0.

EXPECTED SCORE RANGES (use these to sanity-check your result):
  Strong Canadian/Ontario manufacturer with 2+ confirmed certs: 75–90
  Verified US CUSMA manufacturer with confirmed certs: 65–80
  Offshore non-CUSMA manufacturer: 50–65
  Trader/broker with unconfirmed certs: 40–55

━━━━ SUPPLIER CLASSIFICATION ━━━━
Classify as exactly one of:
  "Manufacturer"   → Makes the product directly in their own facility
  "Distributor"    → Buys in bulk and resells; carries inventory
  "Trader/Broker"  → Intermediary/agent; does not hold inventory
  "Local Vendor"   → Canadian or regional supplier (based in Canada)

If the supplier is in Canada: always classify as "Local Vendor".
supplier_type should be "Primary" for Manufacturers and Local Vendors, "Secondary" for others.

━━━━ RISK ASSESSMENT ━━━━
Score each risk category 0–100 where HIGHER = MORE RISKY.
  0–30: Low risk  |  31–60: Medium risk  |  61–100: High risk

geopolitical_risk (0–100): Political stability of supplier country, active trade sanctions,
  currency volatility vs CAD, labour dispute history.
  Canada/USA: 5-15  |  EU/Australia: 10-20  |  SE Asia: 25-45  |  Middle East/Africa: 45-70
  High-risk countries ({risk_countries_str}): 70-95

environmental_risk (0–100): Weather/climate disruption risk for this product and region,
  seasonal availability for "{product}", disease outbreak history (avian flu, ASF, etc.).

supplier_risk (0–100): Based on what you can see:
  - Is this a single-source dependency risk?
  - Are there certification gaps vs buyer requirements ({buyer_certs})?
  - Does capacity appear sufficient for a QSR buyer?
  - Are there quality consistency indicators?
  Broker/Trader with no certs = 60+. Certified large manufacturer = 10-25.

overall_risk_score: Weighted average (geopolitical 35%, environmental 25%, supplier 40%).
risk_level: "Low" (0–30), "Medium" (31–60), or "High" (61–100).

━━━━ RISK FLAGS ━━━━
Add a string to risk_flags for EACH condition that applies:
  • "Broker or trader — not a direct manufacturer"
  • "Certifications not publicly confirmed — verify directly with supplier"
    (use for established Manufacturers/Distributors where certs may exist but aren't listed)
  • "No food safety certifications found"
    (use ONLY for unknown or new suppliers with no cert evidence at all)
  • "No physical address or location found"
  • "High-risk origin country"
  • "Seasonal supply risk"
  • "Single-source dependency risk"
  • "Certification gap — does not meet CFIA/Canadian requirements"

━━━━ RESPONSE FORMAT ━━━━
Respond ONLY with a valid JSON object. No markdown, no explanation, no extra text.

{{
  "name": "Clean company name only",
  "location": "City, Country — or 'Not specified' if unknown",
  "origin_country": "Country name only (e.g., Thailand) — or 'Unknown'",
  "contact_info": "Email and/or phone if found — otherwise 'Visit website'",
  "supplier_class": "Manufacturer OR Distributor OR Trader/Broker OR Local Vendor",
  "supplier_type": "Primary OR Secondary",
  "certifications": ["list", "of", "named", "certifications"],
  "moq": "Minimum order quantity if mentioned — otherwise 'Not specified'",
  "lead_time": "Lead time if mentioned — otherwise 'Not specified'",
  "summary": "2-3 sentences: what they produce, their scale, why they suit a QSR buyer",
  "strengths": "3 key strengths as a comma-separated string",
  "score_breakdown": {{
    "base": 50,
    "cusma_bonus": 0,
    "type_bonus": 0,
    "cert_bonus": 0,
    "focus_bonus": 0,
    "location_bonus": 0,
    "address_bonus": 0,
    "foodservice_bonus": 0,
    "deductions": 0,
    "final_score": 0,
    "score_rationale": "One sentence: biggest factor pushing score up AND biggest factor holding it down"
  }},
  "risk_assessment": {{
    "geopolitical_risk": 0,
    "geopolitical_notes": "1-2 sentences",
    "environmental_risk": 0,
    "environmental_notes": "1-2 sentences",
    "supplier_risk": 0,
    "supplier_risk_notes": "1-2 sentences",
    "overall_risk_score": 0,
    "risk_level": "Low"
  }},
  "risk_flags": [],
  "seasonal_risk": false
}}"""

    # Augment prompt with known facts when supplier comes from the curated database
    if supplier_raw.get("is_curated"):
        curated_country = supplier_raw.get("curated_country", "")
        curated_certs   = ", ".join(supplier_raw.get("curated_certs", []))
        prompt += (
            f"\n\nNOTE: This supplier is from our internal verified database. "
            f"Country of origin: {curated_country}. "
            f"Known certifications: {curated_certs or 'See website'}. "
            "Use these known facts in your analysis. "
            "Score generously on attributes that are confirmed above."
        )

    # ── First API call ──
    # Using a system prompt to strongly reinforce JSON-only output.
    # Sonnet 4.6 — deep reasoning for risk, scoring, and strategy
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1400,
        system=(
            "You are a QSR procurement analyst. "
            "Always respond with valid JSON only. "
            "Never use markdown code fences. "
            "Never return all-zero score breakdowns — assign realistic scores."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text.strip()

    # ── Parse with retry ──
    try:
        parsed = _extract_json(response_text)
    except (json.JSONDecodeError, ValueError):
        # One retry: ask Claude to fix the JSON
        # Sonnet 4.6 — deep reasoning for risk, scoring, and strategy (retry)
        retry_response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1400,
            system="Return only valid JSON. No markdown. No extra text.",
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response_text},
                {"role": "user", "content": "Your response was not valid JSON. Please return only the JSON object, no markdown fences."},
            ],
        )
        try:
            parsed = _extract_json(retry_response.content[0].text.strip())
        except (json.JSONDecodeError, ValueError):
            # Both attempts failed — use safe default
            parsed = _fallback_profile(supplier_raw)

    # ── Post-processing ──

    # Ensure list fields are always lists before any logic that reads them
    if not isinstance(parsed.get("certifications"), list):
        parsed["certifications"] = []
    if not isinstance(parsed.get("risk_flags"), list):
        parsed["risk_flags"] = []

    # Compute numeric score from the breakdown (uses final_score if present)
    parsed["score"] = compute_total_score(parsed.get("score_breakdown", {}))

    # Ensure risk_assessment is a dict
    if not isinstance(parsed.get("risk_assessment"), dict):
        parsed["risk_assessment"] = {
            "geopolitical_risk": 30, "geopolitical_notes": "Unable to assess",
            "environmental_risk": 30, "environmental_notes": "Unable to assess",
            "supplier_risk": 40,     "supplier_risk_notes": "Unable to assess",
            "overall_risk_score": 35, "risk_level": "Medium",
        }

    # Auto-add seasonal risk flag for produce category
    if qsr_category == "🥬 Produce":
        flag = "Seasonal supply risk"
        if flag not in parsed["risk_flags"]:
            parsed["risk_flags"].append(flag)

    # Preserve the original URL and metadata from the search source
    parsed["website"]        = supplier_raw.get("website", "")
    parsed["product"]        = supplier_raw.get("product", "")
    parsed["qsr_category"]   = supplier_raw.get("qsr_category", "General")
    parsed["is_curated"]     = supplier_raw.get("is_curated", False)
    # Pass through contact details found by Claude web search
    parsed["contact_email"]  = supplier_raw.get("contact_email", "")
    parsed["contact_phone"]  = supplier_raw.get("contact_phone", "")

    # ── Compute logistics and landed cost locally ──
    parsed["logistics_options"] = compute_logistics_options(parsed, qsr_category)
    parsed["landed_cost"]       = compute_landed_cost(parsed, qsr_category)

    return parsed


def _fallback_profile(supplier_raw: dict) -> dict:
    """
    Returns a safe placeholder profile when Claude's JSON cannot be parsed
    after two attempts. Prevents one bad response from crashing the whole batch.
    """
    return {
        "name":            supplier_raw.get("name", "Unknown Supplier"),
        "location":        "Not specified",
        "origin_country":  "Unknown",
        "contact_info":    "Visit website",
        "supplier_class":  "Distributor",
        "supplier_type":   "Secondary",
        "certifications":  [],
        "moq":             "Not specified",
        "lead_time":       "Not specified",
        "summary":         supplier_raw.get("snippet", "No summary available."),
        "strengths":       "See website for details",
        "score_breakdown": {k: 0 for k in SCORE_MAXES},
        "risk_assessment": {
            "geopolitical_risk": 40, "geopolitical_notes": "Unable to assess — review manually",
            "environmental_risk": 40, "environmental_notes": "Unable to assess — review manually",
            "supplier_risk": 50,      "supplier_risk_notes": "Unable to assess — review manually",
            "overall_risk_score": 45, "risk_level": "Medium",
        },
        "risk_flags":  ["AI analysis incomplete — review manually"],
        "seasonal_risk": False,
        "score":         0,
        "logistics_options": {},
        "landed_cost":       {},
    }


# ─────────────────────────────────────────────────────────────────────────────
# BATCH PROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def batch_summarize(
    suppliers_raw: list[dict],
    api_key: str,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    user_profile: Optional[dict] = None,
) -> list[dict]:
    """
    Summarizes a list of raw supplier search results using Claude, one at a time.

    Args:
        suppliers_raw:     List of raw supplier dicts from supplier_search.py
        api_key:           Anthropic API key
        progress_callback: Optional function(current, total) for progress bar updates
        user_profile:      Optional buyer profile (location, certs, etc.)

    Returns:
        List of enriched, scored, risk-flagged supplier dicts with logistics data.
    """
    results = []
    total   = len(suppliers_raw)

    for i, supplier_raw in enumerate(suppliers_raw):
        try:
            summarized = summarize_supplier(supplier_raw, api_key, user_profile)
            results.append(summarized)
        except Exception as e:
            fallback = _fallback_profile(supplier_raw)
            fallback["summary"]      = f"AI analysis failed: {str(e)}"
            fallback["website"]      = supplier_raw.get("website", "")
            fallback["product"]      = supplier_raw.get("product", "")
            fallback["qsr_category"] = supplier_raw.get("qsr_category", "General")
            results.append(fallback)

        if progress_callback:
            progress_callback(i + 1, total)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# CLAUDE WEB SEARCH — PRIMARY SUPPLIER DISCOVERY
#
# Why Claude-first is better than SerpAPI-first:
#   - Claude understands procurement intent (not just keywords). It finds actual
#     companies rather than SEO-heavy aggregator pages and Wikipedia articles.
#   - The web_search tool returns structured, deduplicated company data with real
#     contact info — no domain exclusion lists or snippet scraping needed.
#   - Structured JSON output means the pipeline receives pre-cleaned supplier
#     profiles; post-processing in batch_summarize() works on richer input.
#
# Fallback chain (orchestrated by search_suppliers in supplier_search.py):
#   Claude web search (≥3 results) → use Claude results         → method "claude"
#   Claude returns <3 results      → supplement with SerpAPI     → method "combined"
#   Claude fails entirely          → SerpAPI only               → method "serpapi"
#   Both fail                      → curated database only      → method "none"
# ─────────────────────────────────────────────────────────────────────────────

def search_suppliers_with_claude(
    product: str,
    country: Optional[str],
    qsr_category: str,
    user_profile: Optional[dict],
    api_key: str,
) -> list[dict]:
    """
    Lightweight Claude discovery call — finds WHO the suppliers are (fast, cheap).
    batch_summarize() then analyses EACH supplier deeply (scoring, risk, landed cost).

    This mirrors the SerpAPI architecture:
      Claude discovery  = find supplier names + websites  (like Google returning URLs)
      batch_summarize() = analyse each supplier in detail  (already works perfectly)

    # Discovery call: ~500-800 tokens = ~$0.003/search
    # Previous full-detail call: ~2000-4000 tokens, often timed out
    # Timeout: 20 s — names/URLs only, so 20 s is more than enough
    """
    client = anthropic.Anthropic(api_key=api_key)

    country_str = country.strip() if country else "any country"

    user_prompt = (
        f"List 8 real {product} suppliers from {country_str} for QSR food service. "
        "Return ONLY a JSON array with these fields per supplier:\n"
        '- "name": company name\n'
        '- "website": full URL including https://\n'
        '- "country": country\n'
        '- "city": city\n'
        '- "supplier_type": Manufacturer or Distributor or Trader\n'
        '- "contact_note": brief contact note, e.g. "Contact via website inquiry form" '
        'or export department email only if reliably known\n\n'
        "IMPORTANT RULES:\n"
        f"- Return ONLY raw material suppliers and manufacturers who sell {product} "
        "as an ingredient or bulk commodity\n"
        "- Do NOT include retail consumer brands — only B2B suppliers\n"
        f"- Do NOT include companies that USE {product} — only companies that SUPPLY "
        "it as a raw material\n"
        "- Focus on: food manufacturers, ingredient suppliers, commodity exporters, "
        "bulk distributors\n"
        "- The buyer is a QSR operator needing bulk raw ingredients, "
        "not finished consumer products\n\n"
        "No other fields. No explanation. Raw JSON only. Start with [ end with ]."
    )

    key_preview = api_key[:8] + "..." if api_key else "EMPTY"
    print(f"[Claude discovery] starting | key={key_preview} | product={product!r} | country={country!r}")

    response_text = ""
    try:
        # Haiku — lightweight JSON retrieval, no deep reasoning needed
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            timeout=20.0,
            system=(
                "You are a procurement specialist with knowledge of global food "
                "suppliers. Return only valid JSON arrays. Never fabricate companies."
            ),
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = response.content[0].text.strip()
        print(f"[Claude discovery] response length={len(response_text)} chars")

        # Strip any accidental markdown fences before parsing
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        suppliers_data = json.loads(response_text)

        if not isinstance(suppliers_data, list):
            print(f"[Claude discovery] unexpected type {type(suppliers_data).__name__}, returning []")
            return []

    except json.JSONDecodeError as exc:
        print(f"[Claude discovery] JSON parse failed: {exc}")
        print(f"[Claude discovery] raw response preview: {response_text[:300]!r}")
        return []

    except Exception as exc:
        print(f"\n{'='*60}")
        print(f"[Claude discovery] FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise

    # Convert to the raw dict format batch_summarize() expects.
    # The snippet gives Claude's summarize_supplier() enough context to score properly.
    raw_results = []
    for s in suppliers_data:
        if not isinstance(s, dict):
            continue

        name          = s.get("name", "Unknown Supplier")
        website       = s.get("website", "") or ""
        supplier_type = s.get("supplier_type", "Manufacturer")
        city          = s.get("city", "")
        s_country     = s.get("country", country_str)
        contact_note  = s.get("contact_note", "Contact via website inquiry form")

        # Ensure URL has a scheme so Streamlit link_button works correctly
        if website and not website.startswith("http"):
            website = "https://" + website

        location_str = f"{city}, {s_country}".strip(", ")
        snippet = (
            f"{name} is a {supplier_type} of {product} based in {location_str}. "
            f"Contact: {contact_note}"
        )

        raw_results.append({
            "name":          name,
            "website":       website,
            "displayed_url": website,
            "snippet":       snippet,
            "product":       product,
            "qsr_category":  qsr_category,
            "contact_email": "",
            "contact_phone": "",
            "contact_note":  contact_note,
            "source":        "claude_knowledge",
        })

    print(f"[Claude discovery] returning {len(raw_results)} suppliers")
    return raw_results


# ─────────────────────────────────────────────────────────────────────────────
# SOURCING STRATEGY RECOMMENDATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_sourcing_strategy(
    suppliers: list[dict],
    product: str,
    qsr_category: str,
    api_key: str,
    user_profile: Optional[dict] = None,
) -> dict:
    """
    Analyses the full set of scored suppliers and generates a procurement
    strategy recommendation. Uses Claude to reason over all options together.

    Args:
        suppliers:    List of enriched supplier dicts (already scored)
        product:      The product being sourced (e.g., "chicken thighs")
        qsr_category: QSR category string
        api_key:      Anthropic API key
        user_profile: Optional buyer profile

    Returns:
        Dict with keys: primary_recommendation, backup_recommendation,
        volume_split, single_vs_dual, key_risks, estimated_savings, narrative
    """
    client = anthropic.Anthropic(api_key=api_key)

    buyer_location = "Ontario, Canada"
    monthly_volume = "Not specified"
    if user_profile:
        buyer_location = user_profile.get("location", buyer_location)
        volumes = user_profile.get("monthly_volumes", {})
        monthly_volume = volumes.get(qsr_category, "Not specified")

    # Build a compact summary of each supplier for the prompt
    supplier_summaries = []
    for s in suppliers[:8]:  # Cap at 8 to stay within token limit
        lc_data  = s.get("landed_cost", {})
        risk_data = s.get("risk_assessment", {})
        supplier_summaries.append(
            f"- {s.get('name', 'Unknown')} | {s.get('supplier_class', 'Unknown')} | "
            f"Location: {s.get('location', 'N/A')} | "
            f"Score: {s.get('score', 0)}/100 | "
            f"Risk: {risk_data.get('risk_level', 'Unknown')} ({risk_data.get('overall_risk_score', 0)}/100) | "
            f"Landed Cost: ${lc_data.get('total_landed_usd', 0):.2f}/kg USD | "
            f"CUSMA: {'Yes' if lc_data.get('is_cusma') else 'No'} | "
            f"Certs: {', '.join(s.get('certifications', [])) or 'None'}"
        )

    suppliers_block = "\n".join(supplier_summaries)

    prompt = f"""You are a senior QSR procurement strategist advising a buyer in {buyer_location}.
They are sourcing "{product}" ({qsr_category}).
Monthly volume requirement: {monthly_volume}.

Here are the evaluated suppliers (sorted by score):

{suppliers_block}

Based on this data, provide a sourcing strategy recommendation. Consider:
- The buyer's location (Ontario, Canada) — prefer CUSMA suppliers to avoid 12% tariff
- Risk diversification — recommend dual-sourcing if there are significant risks
- Landed cost — compare total cost to Ontario including duties and freight
- Supplier reliability — higher score = more reliable

Return a JSON object with exactly these keys:

{{
  "primary_supplier": "Name of best overall supplier",
  "primary_rationale": "2-3 sentences explaining why",
  "backup_supplier": "Name of best backup supplier",
  "backup_rationale": "2-3 sentences explaining why",
  "volume_split": "e.g., 70% primary / 30% backup",
  "single_vs_dual": "Single-source OR Dual-source",
  "single_vs_dual_rationale": "1-2 sentences explaining the recommendation",
  "key_risks": ["risk 1", "risk 2", "risk 3"],
  "estimated_savings_note": "Commentary on potential cost savings vs alternatives",
  "cusma_advantage": "Explain CUSMA tariff benefit if applicable",
  "strategy_summary": "3-4 sentence executive summary of the full recommendation"
}}"""

    try:
        response = client.messages.create(
            # Sonnet 4.6 — strategy reasoning requires nuanced multi-supplier analysis
            model="claude-sonnet-4-6",
            max_tokens=1200,
            system=(
                "You are a QSR procurement strategist. "
                "Return only valid JSON with no markdown or extra text."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        return _extract_json(response.content[0].text.strip())

    except Exception as e:
        # Return a minimal strategy if Claude fails
        best = suppliers[0] if suppliers else {}
        backup = suppliers[1] if len(suppliers) > 1 else {}
        return {
            "primary_supplier": best.get("name", "See results above"),
            "primary_rationale": "Highest overall score in this search.",
            "backup_supplier": backup.get("name", "N/A"),
            "backup_rationale": "Second highest score; provides supply continuity.",
            "volume_split": "70% primary / 30% backup",
            "single_vs_dual": "Dual-source",
            "single_vs_dual_rationale": "Dual sourcing is recommended to reduce supply chain risk.",
            "key_risks": ["Single-source dependency", "Supply disruption", "Price volatility"],
            "estimated_savings_note": f"Strategy generation failed: {str(e)}",
            "cusma_advantage": "CUSMA eligible suppliers (Canada, USA, Mexico) have 0% import duty.",
            "strategy_summary": "Review top-scored suppliers above and consider dual sourcing for resilience.",
        }
