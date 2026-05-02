# qsr_config.py
# Central configuration for QSR (Quick Service Restaurant) product categories.
# Keeping this in its own file makes it easy to add new categories later
# without touching any other code.

# ─────────────────────────────────────────────────────────────────────────────
# QSR_CATEGORIES
#
# Each category has:
#   examples        — shown as placeholder text in the product input field
#   extra_terms     — appended to the Google search query to surface
#                     food-grade, certified suppliers instead of generic results
#   cert_focus      — told to Claude so it knows which certs matter most
#   seasonal_risk   — True means supply/price fluctuates by season;
#                     automatically adds a risk flag for produce items
# ─────────────────────────────────────────────────────────────────────────────
QSR_CATEGORIES: dict[str, dict] = {
    "🍗 Proteins": {
        "examples": ["Chicken thighs", "Beef patties", "Fish fillets", "Plant-based protein"],
        "extra_terms": "food grade HACCP FDA approved meat poultry processor manufacturer halal",
        "cert_focus": "HACCP, FDA, ISO 22000, FSSC 22000, Halal",
        "seasonal_risk": False,
    },
    "🥬 Produce": {
        "examples": ["Iceberg lettuce", "Roma tomatoes", "Russet potatoes", "Onions"],
        "extra_terms": "fresh produce supplier food safety GAP certified agricultural exporter wholesale",
        "cert_focus": "GlobalG.A.P, GAP, FDA, USDA Organic",
        "seasonal_risk": True,  # Fresh produce is highly seasonal — always flag this
    },
    "📦 Packaging": {
        "examples": ["Paper cups", "Burger bags", "Sandwich wrappers", "Clamshell boxes"],
        "extra_terms": "food grade packaging FDA food contact material manufacturer BRC certified",
        "cert_focus": "FDA food contact, ISO 9001, BRC, FSC",
        "seasonal_risk": False,
    },
    "🧂 Condiments & Sauces": {
        "examples": ["Ketchup", "Mayonnaise", "Hot sauce", "BBQ sauce", "Mustard"],
        "extra_terms": "food manufacturer sauce condiment FDA HACCP certified bulk B2B supplier OEM",
        "cert_focus": "HACCP, FDA, ISO 22000, FSSC 22000",
        "seasonal_risk": False,
    },
    "🌾 Dry Goods": {
        "examples": ["All-purpose flour", "Palm cooking oil", "Refined sugar", "Table salt"],
        "extra_terms": "bulk food ingredient supplier FDA approved food grade manufacturer wholesale",
        "cert_focus": "FDA, ISO 22000, FSSC 22000, Kosher, Halal",
        "seasonal_risk": False,
    },
    "❄️ Frozen & Cold Chain": {
        "examples": ["Frozen french fries", "Frozen beef patties", "Frozen fish portions"],
        "extra_terms": "frozen food manufacturer cold chain logistics HACCP certified IQF supplier",
        "cert_focus": "HACCP, FDA, ISO 22000, BRC, IFS",
        "seasonal_risk": False,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# HIGH_RISK_COUNTRIES
#
# Countries flagged for elevated food safety due-diligence requirements.
# This list is used in the Claude prompt — it is NOT a blocklist.
# Claude uses it to add a "High-risk origin country" flag when relevant.
# Procurement teams should still investigate and make their own judgment.
# ─────────────────────────────────────────────────────────────────────────────
HIGH_RISK_COUNTRIES: list[str] = [
    "Yemen", "Somalia", "Sudan", "South Sudan", "Libya",
    "North Korea", "Syria", "Venezuela", "Myanmar",
]

# ─────────────────────────────────────────────────────────────────────────────
# SCORE_THRESHOLDS
#
# Used in the UI to assign a label and color to each supplier's score.
# ─────────────────────────────────────────────────────────────────────────────
SCORE_THRESHOLDS = {
    "verified":   {"min": 75, "label": "Verified Supplier",  "color": "#00E096", "bg": "#003D26", "text": "#00E096"},
    "promising":  {"min": 50, "label": "Promising",           "color": "#FFB800", "bg": "#3D2A00", "text": "#FFB800"},
    "caution":    {"min": 0,  "label": "Needs Verification",  "color": "#FF4757", "bg": "#3D0A0F", "text": "#FF4757"},
}


def get_score_tier(score: int) -> dict:
    """
    Returns the threshold config dict for a given score (0-100).
    Example: get_score_tier(80) → {"min":75, "label":"Verified Supplier", "color":"#28a745", ...}
    """
    if score >= SCORE_THRESHOLDS["verified"]["min"]:
        return SCORE_THRESHOLDS["verified"]
    if score >= SCORE_THRESHOLDS["promising"]["min"]:
        return SCORE_THRESHOLDS["promising"]
    return SCORE_THRESHOLDS["caution"]
