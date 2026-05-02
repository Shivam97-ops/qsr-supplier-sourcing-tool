# app.py — QSR Supplier Sourcing Tool: AI-powered supplier discovery, risk scoring, and landed cost analysis for food-service procurement teams.
# Main entry point — run with: streamlit run app.py
#
# Streamlit re-runs this entire script top-to-bottom on every user interaction.
# We use st.session_state (a persistent dict) to preserve data between reruns.
#
# WHAT'S NEW IN THIS VERSION:
#   - User Profile: stored in user_profile.json, shown and editable in sidebar.
#     The profile influences search geo-bias and AI analysis context.
#   - 4-type supplier classification with coloured badges.
#   - Risk Intelligence dashboard (3 categories + overall score).
#   - Logistics Options table (sea/intermodal/air/truck with costs).
#   - Total Landed Cost calculator (7-component breakdown, USD + CAD).
#   - Sourcing Strategy: AI-generated recommendation after search results.
#   - Upgraded comparison panel with all new fields.

import streamlit as st
import os
import json
import pandas as pd

from supplier_search import search_suppliers
from ai_summarizer import batch_summarize, generate_sourcing_strategy
from qsr_config import QSR_CATEGORIES, get_score_tier
from database import (
    init_db, migrate_db,
    save_supplier, get_all_suppliers, delete_supplier,
    supplier_already_saved,
    save_scorecard, get_scorecard_for_supplier, get_all_scorecards,
    parse_json_list, parse_json_dict,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QSR Supplier Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL DARK THEME CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

.stApp { background-color:#0A0E1A !important; font-family:'Inter',sans-serif !important; }
.stApp > header { background-color:#0A0E1A !important; }
.main .block-container { background-color:#0A0E1A !important; }

[data-testid="stSidebar"] { background-color:#060910 !important; }
[data-testid="stSidebar"] * { color:#F0F4FF !important; }

.stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2,
.stMarkdown h3, .stMarkdown h4, .stMarkdown li { color:#F0F4FF !important; }

.stTextInput > div > div > input {
    background-color:#111827 !important; border:1px solid #1E2A3A !important;
    color:#F0F4FF !important; border-radius:6px !important;
}
.stTextInput > div > div > input:focus {
    border-color:#00D4FF !important; box-shadow:0 0 0 2px rgba(0,212,255,0.15) !important;
}
.stTextInput label { color:#8892A4 !important; font-size:0.82rem !important; }

.stSelectbox > div > div { background-color:#111827 !important; border:1px solid #1E2A3A !important; color:#F0F4FF !important; }
.stSelectbox [data-baseweb="select"] > div { background-color:#111827 !important; border-color:#1E2A3A !important; color:#F0F4FF !important; }
.stSelectbox label { color:#8892A4 !important; }

.stButton > button {
    background:linear-gradient(135deg,#00D4FF,#0099CC) !important;
    color:#0A0E1A !important; font-weight:700 !important;
    border:none !important; border-radius:8px !important;
    font-family:'Inter',sans-serif !important;
}
.stButton > button:hover { background:linear-gradient(135deg,#33DDFF,#00AADD) !important; color:#0A0E1A !important; }
.stFormSubmitButton > button {
    background:linear-gradient(135deg,#00D4FF,#0099CC) !important;
    color:#0A0E1A !important; font-weight:700 !important;
    border:none !important; border-radius:8px !important;
    padding:14px !important; font-family:'Inter',sans-serif !important;
}
.stLinkButton a { background:transparent !important; border:1px solid #1E2A3A !important; color:#00D4FF !important; border-radius:6px !important; }

.stTabs [data-baseweb="tab-list"] { background-color:#060910 !important; border-bottom:1px solid #1E2A3A !important; }
.stTabs [data-baseweb="tab"] { background-color:transparent !important; color:#8892A4 !important; font-family:'Inter',sans-serif !important; font-weight:500 !important; }
.stTabs [aria-selected="true"] { background-color:rgba(0,212,255,0.08) !important; color:#00D4FF !important; border-bottom:2px solid #00D4FF !important; }

.streamlit-expanderHeader { background-color:#111827 !important; color:#F0F4FF !important; border:1px solid #1E2A3A !important; border-radius:8px !important; }
.streamlit-expanderContent { background-color:#111827 !important; border:1px solid #1E2A3A !important; border-top:none !important; }

[data-testid="stMetricValue"] { color:#00D4FF !important; font-family:'Inter',sans-serif !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] { color:#8892A4 !important; }
[data-testid="metric-container"] { background-color:#111827 !important; border:1px solid #1E2A3A !important; border-top:2px solid #00D4FF !important; border-radius:8px !important; padding:12px 16px !important; }

.stDataFrame { background-color:#111827 !important; }
.stDataFrame thead tr th { background-color:#1E2A3A !important; color:#8892A4 !important; }
.stDataFrame tbody tr td { background-color:#111827 !important; color:#F0F4FF !important; }

.stProgress > div > div > div > div { background-color:#00D4FF !important; }

[data-testid="stInfo"] { background-color:rgba(0,212,255,0.07) !important; border-left:3px solid #00D4FF !important; color:#F0F4FF !important; }
[data-testid="stWarning"] { background-color:rgba(255,184,0,0.07) !important; border-left:3px solid #FFB800 !important; color:#F0F4FF !important; }
[data-testid="stError"] { background-color:rgba(255,71,87,0.07) !important; border-left:3px solid #FF4757 !important; color:#F0F4FF !important; }
[data-testid="stSuccess"] { background-color:rgba(0,224,150,0.07) !important; border-left:3px solid #00E096 !important; color:#F0F4FF !important; }

div[data-testid="stCaptionContainer"] p { color:#8892A4 !important; }
.stCheckbox label { color:#F0F4FF !important; }
.stSlider label, .stSlider div { color:#F0F4FF !important; }
.stTextArea textarea { background-color:#111827 !important; border:1px solid #1E2A3A !important; color:#F0F4FF !important; border-radius:6px !important; }

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0A0E1A; }
::-webkit-scrollbar-thumb { background:#1E2A3A; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#2a3a5a; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# USER PROFILE  —  persisted in user_profile.json on disk
# ─────────────────────────────────────────────────────────────────────────────
PROFILE_PATH = "user_profile.json"

DEFAULT_PROFILE = {
    "company_name": "My QSR Company",
    "location": "Ontario, Canada",
    "industry": "QSR",
    "sourcing_priority": [
        "1. Local/Canadian suppliers first",
        "2. USA suppliers (CUSMA — 0% tariff)",
        "3. Offshore primary manufacturers",
        "4. Offshore distributors/traders last",
    ],
    "monthly_volumes": {
        "🍗 Proteins":            "10,000 kg",
        "🥬 Produce":             "5,000 kg",
        "📦 Packaging":           "50,000 units",
        "🧂 Condiments & Sauces": "2,000 kg",
        "🌾 Dry Goods":           "8,000 kg",
        "❄️ Frozen & Cold Chain": "15,000 kg",
    },
    "preferred_certifications": ["HACCP", "ISO 22000", "FSSC 22000", "FDA", "CFIA"],
}


def load_user_profile() -> dict:
    """
    Loads the user profile from user_profile.json.
    Creates the file with defaults if it does not exist yet.
    """
    if not os.path.exists(PROFILE_PATH):
        save_user_profile(DEFAULT_PROFILE)
        return DEFAULT_PROFILE.copy()
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_PROFILE.copy()


def save_user_profile(profile: dict):
    """Writes the profile dict to user_profile.json."""
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────────────────────────────────────
init_db()
migrate_db()


# ─────────────────────────────────────────────────────────────────────────────
# REUSABLE INLINE-STYLE CONSTANTS  (dark theme)
# ─────────────────────────────────────────────────────────────────────────────

# Cards
_CARD  = "background:#111827; border:1px solid #1E2A3A; border-radius:12px; padding:20px 24px 16px 24px; margin-bottom:12px; box-shadow:0 4px 24px rgba(0,0,0,0.4);"
_CCARD = "background:#111827; border:1px solid #1E2A3A; border-radius:12px; padding:18px; margin:4px 0;"

# Typography
_NAME      = "font-size:1.15rem; font-weight:700; color:#F0F4FF; margin-bottom:4px; font-family:'Space Grotesk',sans-serif;"
_CNAME     = "font-size:1rem; font-weight:700; color:#F0F4FF; margin-bottom:8px; border-bottom:1px solid #1E2A3A; padding-bottom:8px; font-family:'Space Grotesk',sans-serif;"
_CLABEL    = "font-size:0.72rem; color:#8892A4; text-transform:uppercase; letter-spacing:0.08em; margin-top:10px; margin-bottom:2px;"
_CVALUE    = "font-size:0.88rem; color:#D0D8E8; margin-bottom:2px;"
_MUTED     = "color:#8892A4; font-size:0.85rem;"
_SECTION_H = "font-size:1.4rem; font-weight:700; color:#F0F4FF; border-bottom:2px solid #00D4FF; padding-bottom:8px; margin-bottom:20px; font-family:'Space Grotesk',sans-serif;"

# 4-type supplier class badges
_CLASS_MANUFACTURER = "background:#003D26; color:#00E096; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; margin-right:4px;"
_CLASS_DISTRIBUTOR  = "background:#003040; color:#00D4FF; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; margin-right:4px;"
_CLASS_TRADER       = "background:#3D2A00; color:#FFB800; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; margin-right:4px;"
_CLASS_LOCAL        = "background:#2A003D; color:#C084FC; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; margin-right:4px;"

# Risk level badges
_RISK_HIGH   = "background:#3D0A0F; color:#FF4757; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:700;"
_RISK_MEDIUM = "background:#3D2A00; color:#FFB800; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:700;"
_RISK_LOW    = "background:#003D26; color:#00E096; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:700;"

# CUSMA badge
_CUSMA = "background:#003040; color:#00D4FF; padding:2px 9px; border-radius:20px; font-size:0.78rem; font-weight:600;"

# Curated / verified supplier badge
_CURATED_BADGE = "background:#3B1FA8; color:#C084FC; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; margin-right:4px;"

# Cert and risk-flag pills
_CERT_PILL = "background:#003D26; color:#00E096; padding:2px 9px; border-radius:20px; font-size:0.72rem; font-weight:600; margin-right:4px; display:inline-block; margin-bottom:3px;"
_RISK_PILL = "background:#3D0A0F; color:#FF4757; padding:2px 9px; border-radius:20px; font-size:0.72rem; font-weight:600; margin-right:4px; display:inline-block; margin-bottom:3px;"

# Score bar background
_BAR_BG = "background:#1E2A3A; border-radius:4px; height:6px; width:100%; margin:6px 0 2px 0; overflow:hidden;"


# ═════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def get_class_badge(supplier_class: str) -> str:
    """Returns an HTML badge for the supplier's 4-type classification."""
    icons = {
        "Manufacturer":  "🏭",
        "Distributor":   "🏪",
        "Trader/Broker": "🤝",
        "Local Vendor":  "🍁",
    }
    styles = {
        "Manufacturer":  _CLASS_MANUFACTURER,
        "Distributor":   _CLASS_DISTRIBUTOR,
        "Trader/Broker": _CLASS_TRADER,
        "Local Vendor":  _CLASS_LOCAL,
    }
    icon  = icons.get(supplier_class, "🏢")
    style = styles.get(supplier_class, _CLASS_DISTRIBUTOR)
    return f'<span style="{style}">{icon} {supplier_class}</span>'


def get_risk_badge(risk_level: str, risk_score: int = 0) -> str:
    """Returns an HTML badge coloured by risk level."""
    if risk_level == "High":
        style = _RISK_HIGH
        icon  = "🔴"
    elif risk_level == "Medium":
        style = _RISK_MEDIUM
        icon  = "🟡"
    else:
        style = _RISK_LOW
        icon  = "🟢"
    score_str = f" {risk_score}/100" if risk_score else ""
    return f'<span style="{style}">{icon} {risk_level} Risk{score_str}</span>'


def generate_score_gauge(score: int) -> str:
    """SVG semicircle gauge showing the supplier score 0–100."""
    tier  = get_score_tier(score)
    color = tier["color"]
    label = tier["label"]
    # Semicircle arc r=45 → length = π × 45 ≈ 141.4; fill proportional to score
    arc_len   = 141.4
    fill      = arc_len * score / 100
    gap       = arc_len - fill
    return f"""
    <svg width="110" height="64" viewBox="0 0 110 64" style="display:block;margin:0 auto 4px auto;">
      <path d="M 10 58 A 45 45 0 0 1 100 58" fill="none" stroke="#1E2A3A" stroke-width="9" stroke-linecap="round"/>
      <path d="M 10 58 A 45 45 0 0 1 100 58" fill="none" stroke="{color}" stroke-width="9"
            stroke-linecap="round"
            stroke-dasharray="{fill:.1f} {gap:.1f}"
            stroke-dashoffset="0"/>
      <text x="55" y="54" text-anchor="middle" font-size="17" font-weight="700"
            font-family="Space Grotesk,Inter,sans-serif" fill="{color}">{score}</text>
    </svg>
    <div style="text-align:center; font-size:0.72rem; font-weight:700; color:{color};
                letter-spacing:0.05em; margin-bottom:6px;">{label.upper()}</div>
    """


def render_score_bar(score: int) -> str:
    """Returns HTML for a gradient progress bar + score label."""
    tier  = get_score_tier(score)
    color = tier["color"]
    label = tier["label"]
    return (
        f'<div style="{_BAR_BG}">'
        f'<div style="height:6px; border-radius:4px; width:{score}%; background:linear-gradient(90deg,{color}99,{color});"></div>'
        f'</div>'
        f'<div style="font-size:0.8rem; font-weight:700; color:{color}; margin-bottom:10px;">'
        f'{score}/100 &nbsp;—&nbsp; {label}'
        f'</div>'
    )


def render_cert_badges(certs: list, supplier_class: str = "") -> str:
    """Green pill badges for certifications, or contextual message when none are listed."""
    if certs:
        return " ".join(f'<span style="{_CERT_PILL}">✓ {c}</span>' for c in certs)
    if supplier_class in ("Manufacturer", "Local Vendor"):
        return (
            '<span style="color:#FFB800; font-size:0.78rem; font-style:italic;">'
            '⚠️ Certifications not publicly listed — verify directly with supplier'
            '</span>'
        )
    return '<span style="color:#FF4757; font-size:0.78rem;">❌ No certifications confirmed</span>'


def render_risk_badges(flags: list) -> str:
    """Red pill badges for risk flags."""
    if not flags:
        return '<span style="color:#00E096; font-size:0.78rem;">✓ No risk flags</span>'
    return " ".join(f'<span style="{_RISK_PILL}">⚠ {flag}</span>' for flag in flags)


def render_risk_bar(score: int, label: str, color: str) -> str:
    """Returns an HTML mini-bar for one risk category (higher = worse)."""
    return (
        f'<div style="margin-bottom:8px;">'
        f'<div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:2px;">'
        f'<span style="color:#D0D8E8;">{label}</span>'
        f'<span style="font-weight:700; color:{color};">{score}/100</span>'
        f'</div>'
        f'<div style="background:#1E2A3A; border-radius:6px; height:7px; overflow:hidden;">'
        f'<div style="height:7px; border-radius:6px; width:{score}%; background:linear-gradient(90deg,{color}88,{color});"></div>'
        f'</div>'
        f'</div>'
    )


def _risk_color(score: int) -> str:
    """Returns a hex colour for a risk score (higher score = more risk = redder)."""
    if score >= 61:
        return "#FF4757"
    if score >= 31:
        return "#FFB800"
    return "#00E096"


def render_risk_dashboard(risk: dict):
    """
    Renders the 3-category risk breakdown inside a Streamlit expander.
    Uses st.html for the bar charts and st.columns for layout.
    """
    if not risk:
        st.caption("Risk data not available for this supplier.")
        return

    geo   = risk.get("geopolitical_risk", 0)
    env   = risk.get("environmental_risk", 0)
    sup   = risk.get("supplier_risk", 0)
    overall = risk.get("overall_risk_score", 0)
    level = risk.get("risk_level", "Unknown")

    bars_html = (
        render_risk_bar(geo,     "🌍 Geopolitical & Trade",     _risk_color(geo)) +
        render_risk_bar(env,     "🌱 Environmental & Seasonal",  _risk_color(env)) +
        render_risk_bar(sup,     "🏢 Supplier-Specific",         _risk_color(sup))
    )
    st.html(bars_html)

    col1, col2 = st.columns(2)
    with col1:
        badge = get_risk_badge(level, overall)
        st.html(f'<div style="margin-top:4px; color:#D0D8E8;"><strong>Overall:</strong> {badge}</div>')
    with col2:
        st.html(f'<div style="font-size:0.82rem; color:#8892A4; margin-top:8px;">'
                f'Overall risk score: <strong style="color:#D0D8E8;">{overall}/100</strong>'
                f'</div>')

    notes = [
        ("Geopolitical", risk.get("geopolitical_notes", "")),
        ("Environmental", risk.get("environmental_notes", "")),
        ("Supplier",      risk.get("supplier_risk_notes", "")),
    ]
    for label, note in notes:
        if note:
            st.html(f'<p style="font-size:0.8rem; color:#8892A4; margin:4px 0;">'
                    f'<strong style="color:#D0D8E8;">{label}:</strong> {note}</p>')


def render_logistics_section(logistics: dict, landed: dict):
    """
    Renders the logistics options table and landed cost breakdown
    inside a Streamlit expander.
    """
    if not logistics and not landed:
        st.caption("Logistics data not available for this supplier.")
        return

    # ── Logistics Options Table ──
    if logistics:
        st.markdown("**Available Logistics Modes:**")
        rows = []
        for key, opt in logistics.items():
            mode = opt.get("mode", key)
            days = opt.get("transit_days", ("?", "?"))
            days_str = f"{days[0]}–{days[1]} days" if isinstance(days, tuple) else str(days)

            if "cost_per_kg_usd" in opt:
                cost_str = f"${opt['cost_per_kg_usd']:.3f}/kg"
            elif "cost_per_cbm_usd" in opt:
                cost_str = f"${opt['cost_per_cbm_usd']}/CBM"
            else:
                cost_str = "N/A"

            route = opt.get("route", opt.get("note", ""))
            rows.append({"Mode": mode, "Cost": cost_str, "Transit": days_str, "Route/Note": route})

        if rows:
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

    # ── Landed Cost Breakdown ──
    if landed:
        st.markdown("**Total Landed Cost to Ontario (est.):**")

        is_cusma = landed.get("is_cusma", False)
        tariff   = landed.get("tariff_rate_pct", 12)
        mode     = landed.get("logistics_mode", "Sea Freight")

        if is_cusma:
            st.html(f'<span style="{_CUSMA}">🍁 CUSMA Eligible — 0% Import Duty</span>'
                    f'&nbsp;<span style="{_MUTED}">({mode})</span>')
        else:
            st.html(f'<span style="{_MUTED}">Logistics: {mode} | Duty: {tariff:.0f}%</span>')

        items = [
            ("FOB Price (origin)",          landed.get("fob_price_usd", 0)),
            ("Ocean/Air/Truck Freight",     landed.get("freight_per_kg_usd", 0)),
            ("Insurance (0.5%)",            landed.get("insurance_per_kg_usd", 0)),
            (f"Import Duty ({tariff:.0f}%)", landed.get("import_duty_per_kg_usd", 0)),
            ("CFIA Inspection Fee",         landed.get("cfia_fee_per_kg_usd", 0)),
            ("Inland to Ontario",           landed.get("inland_per_kg_usd", 0)),
            ("Inventory Holding (3.75%)",   landed.get("inventory_cost_per_kg_usd", 0)),
        ]
        total_usd = landed.get("total_landed_usd", 0)
        total_cad = landed.get("total_landed_cad", 0)

        table_rows = "".join(
            f"<tr><td style='padding:3px 8px; font-size:0.82rem; color:#8892A4;'>{lbl}</td>"
            f"<td style='padding:3px 8px; font-size:0.82rem; text-align:right; color:#D0D8E8;'>${val:.3f}/kg</td></tr>"
            for lbl, val in items
        )
        table_html = f"""
        <table style="width:100%; border-collapse:collapse; margin-top:6px;">
            {table_rows}
            <tr style="border-top:2px solid #1E2A3A; background:#0A0E1A;">
                <td style="padding:5px 8px; font-size:0.88rem; font-weight:700; color:#F0F4FF;">Total Landed Cost</td>
                <td style="padding:5px 8px; font-size:0.88rem; font-weight:700; text-align:right; color:#00D4FF;">
                    ${total_usd:.3f}/kg USD<br>
                    <span style="color:#8892A4; font-size:0.8rem;">${total_cad:.3f}/kg CAD</span>
                </td>
            </tr>
        </table>
        <p style="font-size:0.75rem; color:#8892A4; margin-top:4px;">
            * Estimates based on typical mid-market FOB prices. Actual quotes may vary.
        </p>"""
        st.html(table_html)


def render_supplier_card(supplier: dict, index: int, product: str, user_profile: dict = None):
    """
    Renders one supplier result card with:
      - Supplier class badge (4-type colour system)
      - Score bar
      - Certifications + risk flags
      - Risk dashboard (in expander)
      - Logistics & Landed Cost (in expander)
      - Save / Compare / Website buttons

    Args:
        supplier:     Enriched supplier dict from ai_summarizer.py
        index:        Position in results list (for unique widget keys)
        product:      Product searched for (duplicate check on save)
        user_profile: Current user profile dict (optional)
    """
    score  = supplier.get("score", 0)
    sclass = supplier.get("supplier_class", supplier.get("supplier_type", "Distributor"))
    certs  = supplier.get("certifications", [])
    flags  = supplier.get("risk_flags", [])
    risk   = supplier.get("risk_assessment", {})
    logistics = supplier.get("logistics_options", {})
    landed    = supplier.get("landed_cost", {})

    risk_level    = risk.get("risk_level", "Unknown")
    is_cusma      = landed.get("is_cusma", False)
    total_usd     = landed.get("total_landed_usd", 0)
    is_curated   = supplier.get("is_curated", False)
    contact_note = supplier.get("contact_note", "") or supplier.get("contact_info", "")
    contact_line = f'📞 <strong>Contact:</strong> {contact_note or "Visit website"}'

    class_badge   = get_class_badge(sclass)
    risk_badge    = get_risk_badge(risk_level, risk.get("overall_risk_score", 0))
    cusma_html    = f'&nbsp;<span style="{_CUSMA}">🍁 CUSMA</span>' if is_cusma else ""
    cost_html     = (f'&nbsp;<span style="{_MUTED}">Landed: <strong>${total_usd:.2f}/kg USD</strong></span>'
                     if total_usd else "")
    curated_html  = f'<span style="{_CURATED_BADGE}">⭐ Verified Supplier</span>&nbsp;' if is_curated else ""

    tier  = get_score_tier(score)
    accent = tier["color"]

    card_html = f"""
    <div style="background:#111827; border:1px solid #1E2A3A; border-left:3px solid {accent};
                border-radius:12px; padding:20px 24px 14px 24px; margin-bottom:12px;
                box-shadow:0 4px 24px rgba(0,0,0,0.4);">

        <div style="display:flex; align-items:flex-start; gap:20px;">

            <!-- Score gauge column -->
            <div style="min-width:110px; flex-shrink:0; text-align:center;">
                {generate_score_gauge(score)}
            </div>

            <!-- Main content -->
            <div style="flex:1; min-width:0;">
                <div style="{_NAME}">{curated_html}{supplier.get('name', 'Unknown Supplier')}</div>

                <div style="margin-bottom:10px; font-size:0.85rem; display:flex; flex-wrap:wrap; align-items:center; gap:6px;">
                    <span style="color:#8892A4;">📍 {supplier.get('location', 'Not specified')}</span>
                    <span style="color:#1E2A3A;">|</span>
                    {class_badge}{cusma_html}
                    <span style="color:#1E2A3A;">|</span>
                    {risk_badge}
                    {cost_html}
                </div>

                <div style="margin:8px 0 6px 0;">
                    <span style="{_MUTED}">🔬 CERTS &nbsp;</span>
                    {render_cert_badges(certs, sclass)}
                </div>

                <div style="margin-bottom:10px;">
                    <span style="{_MUTED}">⚑ FLAGS &nbsp;</span>
                    {render_risk_badges(flags)}
                </div>

                <p style="color:#D0D8E8; margin-bottom:10px; font-size:0.9rem; line-height:1.55;">
                    {supplier.get('summary', '')}
                </p>

                <div style="display:flex; gap:24px; font-size:0.84rem; color:#8892A4; margin-bottom:8px; flex-wrap:wrap;">
                    <span>📦 <strong style="color:#D0D8E8;">MOQ:</strong> {supplier.get('moq', 'Not specified')}</span>
                    <span>⏱ <strong style="color:#D0D8E8;">Lead Time:</strong> {supplier.get('lead_time', 'Not specified')}</span>
                    <span style="color:#8892A4;">{contact_line}</span>
                </div>

                <div style="{_MUTED}">💪 <strong style="color:#D0D8E8;">Strengths:</strong> {supplier.get('strengths', 'N/A')}</div>
            </div>
        </div>
    </div>"""

    st.html(card_html)

    # ── Expandable detail panels ──
    col_risk, col_logistics = st.columns(2)

    with col_risk:
        with st.expander("⚠️ Risk Intelligence"):
            render_risk_dashboard(risk)

    with col_logistics:
        with st.expander("🚢 Logistics & Landed Cost"):
            render_logistics_section(logistics, landed)

    # ── Action buttons ──
    col_link, col_save, col_compare, _ = st.columns([1, 1, 1, 3])

    with col_link:
        website_url = supplier.get("website", "")
        if website_url and website_url.startswith("http"):
            st.link_button("🌐 Website", website_url)
        else:
            st.caption("No website")

    with col_save:
        save_key = f"save_{index}"
        already_saved = st.session_state.get("save_status", {}).get(save_key, False)
        if already_saved:
            st.success("Saved ✓")
        else:
            if st.button("💾 Save", key=save_key):
                if supplier_already_saved(supplier.get("name", ""), product):
                    st.warning("Already saved.")
                else:
                    save_supplier(supplier)
                    if "save_status" not in st.session_state:
                        st.session_state["save_status"] = {}
                    st.session_state["save_status"][save_key] = True
                    st.rerun()

    with col_compare:
        currently_checked = st.session_state.get(f"compare_{index}", False)
        st.checkbox("⊕ Compare", key=f"compare_{index}", value=currently_checked)

    st.html("<div style='height:4px;'></div>")


def render_comparison_panel(suppliers: list):
    """
    Renders a side-by-side comparison of up to 4 selected suppliers.
    Each card now includes: supplier class badge, CUSMA status,
    total landed cost, risk score, and logistics summary.
    """
    st.markdown("---")
    st.html(f'<div style="{_SECTION_H}">🔄 Side-by-Side Comparison</div>')

    cols = st.columns(len(suppliers))

    for col, sup in zip(cols, suppliers):
        score    = sup.get("score", 0)
        tier     = get_score_tier(score)
        color    = tier["color"]
        label    = tier["label"]
        certs    = sup.get("certifications", [])
        flags    = sup.get("risk_flags", [])
        risk     = sup.get("risk_assessment", {})
        landed   = sup.get("landed_cost", {})
        logistics = sup.get("logistics_options", {})
        sclass   = sup.get("supplier_class", "Distributor")

        risk_level   = risk.get("risk_level", "Unknown")
        overall_risk = risk.get("overall_risk_score", 0)
        is_cusma     = landed.get("is_cusma", False)
        total_usd    = landed.get("total_landed_usd", 0)
        total_cad    = landed.get("total_landed_cad", 0)
        tariff       = landed.get("tariff_rate_pct", 12)

        # Pick the cheapest sea/road mode for the logistics summary
        preferred_mode = "N/A"
        if "road" in logistics:
            preferred_mode = logistics["road"]["mode"]
        elif "sea_fcl" in logistics:
            preferred_mode = logistics["sea_fcl"]["mode"]

        cusma_line = (f'<span style="{_CUSMA}">🍁 CUSMA 0% Duty</span>'
                      if is_cusma else
                      f'<span style="{_MUTED}">Standard Duty: {tariff:.0f}%</span>')

        card_html = f"""
        <div style="background:#111827; border:1px solid #1E2A3A; border-top:2px solid {color};
                    border-radius:12px; padding:18px; margin:4px 0;">

            <div style="{_CNAME}">{sup.get('name', 'Unknown')}</div>

            {generate_score_gauge(score)}

            <div style="{_CLABEL}">SUPPLIER TYPE</div>
            <div style="margin-bottom:6px;">{get_class_badge(sclass)}</div>

            <div style="{_CLABEL}">RISK</div>
            <div style="margin-bottom:6px;">{get_risk_badge(risk_level, overall_risk)}</div>

            <div style="{_CLABEL}">TARIFF STATUS</div>
            <div style="margin-bottom:6px;">{cusma_line}</div>

            <div style="{_CLABEL}">TOTAL LANDED COST</div>
            <div style="font-size:0.9rem; font-weight:700; color:#00D4FF; margin-bottom:2px;">
                ${total_usd:.3f}/kg USD
            </div>
            <div style="font-size:0.8rem; color:#8892A4; margin-bottom:6px;">
                ${total_cad:.3f}/kg CAD
            </div>

            <div style="{_CLABEL}">LOCATION</div>
            <div style="{_CVALUE}">📍 {sup.get('location', 'N/A')}</div>

            <div style="{_CLABEL}">CERTIFICATIONS</div>
            <div style="{_CVALUE}">{render_cert_badges(certs, sclass)}</div>

            <div style="{_CLABEL}">MOQ</div>
            <div style="{_CVALUE}">📦 {sup.get('moq', 'Not specified')}</div>

            <div style="{_CLABEL}">LEAD TIME</div>
            <div style="{_CVALUE}">⏱ {sup.get('lead_time', 'Not specified')}</div>

            <div style="{_CLABEL}">PREFERRED LOGISTICS</div>
            <div style="{_CVALUE}">{preferred_mode}</div>

            <div style="{_CLABEL}">RISK FLAGS</div>
            <div style="{_CVALUE}">{render_risk_badges(flags)}</div>

            <div style="{_CLABEL}">SUMMARY</div>
            <div style="font-size:0.82rem; color:#8892A4; line-height:1.45;">
                {sup.get('summary', 'N/A')}
            </div>

        </div>"""

        with col:
            st.html(card_html)
            if sup.get("website"):
                st.link_button("🌐 Visit Website", sup["website"], use_container_width=True)


def render_sourcing_strategy(strategy: dict):
    """Renders the AI-generated sourcing strategy recommendation."""
    if not strategy:
        return

    st.markdown("---")
    st.html(f'<div style="{_SECTION_H}">🎯 Sourcing Strategy Recommendation</div>')

    # Executive summary box
    summary = strategy.get("strategy_summary", "")
    if summary:
        st.html(f"""
        <div style="background:rgba(0,212,255,0.06); border-left:4px solid #00D4FF; border-radius:8px;
                    padding:16px 20px; margin-bottom:16px;">
            <p style="color:#D0D8E8; font-size:0.95rem; line-height:1.6; margin:0;">
                {summary}
            </p>
        </div>
        """)

    col1, col2 = st.columns(2)

    with col1:
        primary     = strategy.get("primary_supplier", "N/A")
        p_rationale = strategy.get("primary_rationale", "")
        st.html(f"""
        <div style="background:#111827; border:1px solid #1E2A3A; border-left:3px solid #00E096;
                    border-radius:10px; padding:16px; margin-bottom:12px;">
            <div style="font-size:0.72rem; color:#8892A4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">PRIMARY RECOMMENDATION</div>
            <div style="font-size:1.05rem; font-weight:700; color:#00E096; margin-bottom:6px; font-family:'Space Grotesk',sans-serif;">✅ {primary}</div>
            <p style="font-size:0.85rem; color:#D0D8E8; line-height:1.5; margin:0;">{p_rationale}</p>
        </div>
        """)

        backup      = strategy.get("backup_supplier", "N/A")
        b_rationale = strategy.get("backup_rationale", "")
        st.html(f"""
        <div style="background:#111827; border:1px solid #1E2A3A; border-left:3px solid #00D4FF;
                    border-radius:10px; padding:16px; margin-bottom:12px;">
            <div style="font-size:0.72rem; color:#8892A4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">BACKUP RECOMMENDATION</div>
            <div style="font-size:1.05rem; font-weight:700; color:#00D4FF; margin-bottom:6px; font-family:'Space Grotesk',sans-serif;">🔄 {backup}</div>
            <p style="font-size:0.85rem; color:#D0D8E8; line-height:1.5; margin:0;">{b_rationale}</p>
        </div>
        """)

    with col2:
        vol_split    = strategy.get("volume_split", "70% / 30%")
        single_dual  = strategy.get("single_vs_dual", "Dual-source")
        sd_rationale = strategy.get("single_vs_dual_rationale", "")
        cusma_note   = strategy.get("cusma_advantage", "")
        savings_note = strategy.get("estimated_savings_note", "")

        st.html(f"""
        <div style="background:#111827; border:1px solid #1E2A3A; border-radius:10px; padding:16px; margin-bottom:12px;">
            <div style="font-size:0.72rem; color:#8892A4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">STRATEGY</div>
            <div style="font-size:1rem; font-weight:700; color:#F0F4FF; margin-bottom:6px; font-family:'Space Grotesk',sans-serif;">
                {single_dual} — {vol_split}
            </div>
            <p style="font-size:0.85rem; color:#D0D8E8; line-height:1.5; margin:0;">{sd_rationale}</p>
        </div>
        """)

        key_risks = strategy.get("key_risks", [])
        if key_risks:
            risks_html = "".join(f'<li style="font-size:0.85rem; color:#D0D8E8;">{r}</li>' for r in key_risks)
            st.html(f"""
            <div style="background:rgba(255,184,0,0.07); border:1px solid #3D2A00; border-radius:10px; padding:16px;">
                <div style="font-size:0.72rem; color:#FFB800; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:6px;">⚠️ KEY RISKS TO MONITOR</div>
                <ul style="margin:0; padding-left:18px;">{risks_html}</ul>
            </div>
            """)

        if cusma_note:
            st.html(f'<p style="font-size:0.82rem; color:#00D4FF; background:rgba(0,212,255,0.07); border-radius:6px; padding:8px 12px; margin-top:10px;">🍁 {cusma_note}</p>')

        if savings_note:
            st.html(f'<p style="font-size:0.82rem; color:#8892A4; margin-top:6px;">💰 {savings_note}</p>')


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.html("""
    <div style="padding:4px 0 12px 0;">
        <div style="font-size:1.15rem; font-weight:700; color:#F0F4FF;
                    font-family:'Space Grotesk',sans-serif; letter-spacing:0.01em;">
            🏭 QSR Supplier Intelligence
        </div>
        <div style="font-size:0.75rem; color:#8892A4; margin-top:2px; letter-spacing:0.04em;">
            AI-POWERED PROCUREMENT PLATFORM
        </div>
    </div>
    """)
    st.markdown("---")

    # ── API Keys ──
    st.html('<div style="font-size:0.8rem; font-weight:700; color:#8892A4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">⚙️ API Keys</div>')
    anthropic_key = st.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Required — powers Claude AI search and supplier analysis",
    )
    serpapi_key = st.text_input(
        "SerpAPI Key (optional)",
        value=os.getenv("SERPAPI_KEY", ""),
        type="password",
        help="Optional — enhances local supplier discovery via Google Search",
    )
    st.caption("SerpAPI key optional — enhances local supplier discovery")

    if not anthropic_key:
        st.warning("⚠️ Anthropic API key required to search.")
    elif serpapi_key:
        st.success("✅ Ready to search (AI + SerpAPI)")
    else:
        st.info("✅ Ready — Claude AI search active")

    # ── Search method indicator (shown after a search is run) ──
    _method = st.session_state.get("search_method")
    if _method:
        st.markdown("---")
        st.markdown("**Last Search Method:**")
        if _method == "claude":
            st.success("🤖 AI Search")
        elif _method == "serpapi":
            st.info("🔍 Web Search (SerpAPI fallback)")
        elif _method == "combined":
            st.success("🤖+🔍 Combined")

    st.markdown("---")

    # ── User Profile ──
    st.html('<div style="font-size:0.8rem; font-weight:700; color:#8892A4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">🏢 Your Profile</div>')
    profile = load_user_profile()

    st.markdown(f"**📍** {profile.get('location', 'Ontario, Canada')}")
    st.markdown(f"**🏭** Industry: {profile.get('industry', 'QSR')}")

    priority_items = profile.get("sourcing_priority", [])
    if priority_items:
        st.markdown("**Sourcing Priority:**")
        for item in priority_items:
            st.markdown(f"&nbsp;&nbsp;{item}")

    certs = profile.get("preferred_certifications", [])
    if certs:
        st.markdown(f"**Certs:** {', '.join(certs)}")

    # Profile editor
    with st.expander("✏️ Edit Profile"):
        with st.form("profile_form"):
            new_company  = st.text_input("Company Name",   value=profile.get("company_name", ""))
            new_location = st.text_input("Location",       value=profile.get("location", "Ontario, Canada"))
            new_industry = st.text_input("Industry",       value=profile.get("industry", "QSR"))
            new_certs    = st.text_input(
                "Preferred Certifications (comma-separated)",
                value=", ".join(profile.get("preferred_certifications", [])),
            )

            st.markdown("**Monthly Volumes by Category:**")
            vols = profile.get("monthly_volumes", {})
            new_vols = {}
            for cat in QSR_CATEGORIES.keys():
                new_vols[cat] = st.text_input(cat, value=vols.get(cat, ""), key=f"vol_{cat}")

            if st.form_submit_button("💾 Save Profile"):
                cert_list = [c.strip() for c in new_certs.split(",") if c.strip()]
                updated = {
                    "company_name": new_company,
                    "location":     new_location,
                    "industry":     new_industry,
                    "sourcing_priority": profile.get("sourcing_priority", DEFAULT_PROFILE["sourcing_priority"]),
                    "monthly_volumes":   {k: v for k, v in new_vols.items() if v},
                    "preferred_certifications": cert_list or profile.get("preferred_certifications", []),
                }
                save_user_profile(updated)
                st.success("Profile saved!")
                st.rerun()

    st.markdown("---")
    st.html('<div style="font-size:0.8rem; font-weight:700; color:#8892A4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">📖 Scoring Guide</div>')
    st.markdown("""
| Score | Tier |
|---|---|
| 75–100 | 🟢 Verified |
| 50–74  | 🟡 Promising |
| 0–49   | 🔴 Needs Check |

**Score components:**
- 🔬 Certifications (25 pts)
- 🌍 Export experience (20 pts)
- 📅 Years established (20 pts)
- 🎯 Product specificity (20 pts)
- 📞 Contact available (15 pts)

**Supplier Types:**
- 🏭 Green = Manufacturer
- 🏪 Blue = Distributor
- 🤝 Yellow = Trader/Broker
- 🍁 Purple = Local Vendor
    """)

    st.markdown("---")
    st.html('<div style="font-size:0.8rem; font-weight:700; color:#8892A4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">🔄 Compare Feature</div>')
    st.markdown("Tick ⊕ Compare on up to 4 cards, then click **Compare Selected**.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_search, tab_saved, tab_scores = st.tabs([
    "🔍  Search Suppliers",
    "💾  Saved Suppliers",
    "📊  Scorecards",
])


# ══════════════════════════════════════════════
# TAB 1 — SEARCH
# ══════════════════════════════════════════════
with tab_search:
    st.html(f'<div style="{_SECTION_H}">🔍 Find QSR Suppliers</div>')

    # Reload profile here so form edits are reflected without needing a restart
    profile = load_user_profile()

    # ── QSR Category Selector ──
    st.markdown("**Step 1 — Choose a product category:**")
    selected_category = st.selectbox(
        "QSR Product Category",
        list(QSR_CATEGORIES.keys()),
        key="category_selector",
        label_visibility="collapsed",
    )

    cat_config   = QSR_CATEGORIES[selected_category]
    example_str  = ", ".join(cat_config["examples"][:3])
    cert_focus   = cat_config["cert_focus"]
    has_seasonal = cat_config["seasonal_risk"]

    if has_seasonal:
        st.info(
            f"🌱 **Seasonal category:** {selected_category} products may have supply or "
            "price fluctuations by harvest season. Suppliers will be automatically flagged "
            "with a seasonal risk warning."
        )

    monthly_vol = profile.get("monthly_volumes", {}).get(selected_category, "")
    if monthly_vol:
        st.html(f'<p style="{_MUTED}">Your typical monthly volume for this category: '
                f'<strong>{monthly_vol}</strong></p>')

    # ── Search Form ──
    st.markdown("**Step 2 — Enter product details and search:**")
    with st.form("search_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            product = st.text_input(
                "Specific Product *",
                placeholder=f"e.g., {example_str}",
                help=f"Key certifications for this category: {cert_focus}",
            )
        with col2:
            country = st.text_input(
                "Preferred Origin Country",
                placeholder="e.g., Thailand, USA, Brazil — or leave blank for profile default",
            )

        col3, col4 = st.columns(2)
        with col3:
            certifications = st.text_input(
                "Additional Certification Requirements",
                placeholder=f"e.g., {cert_focus.split(',')[0].strip()}",
            )
        with col4:
            quantity = st.text_input(
                "Quantity Range",
                placeholder=f"e.g., {monthly_vol or '10,000 kg/month'}",
            )

        submitted = st.form_submit_button(
            f"🔍 Search {selected_category} Suppliers",
            use_container_width=True,
            type="primary",
        )

    # ── Form Submission ──
    if submitted:
        if not product.strip():
            st.error("Please enter a specific product name.")
        elif not anthropic_key:
            st.error("Add your Anthropic API key in the sidebar.")
        else:
            # Clear compare and strategy state from previous search
            for key in list(st.session_state.keys()):
                if key.startswith("compare_"):
                    del st.session_state[key]
            st.session_state["show_comparison"]   = False
            st.session_state["sourcing_strategy"] = None

            # ── Web Search (Claude-first, SerpAPI fallback) ──
            with st.spinner("🤖 Searching Claude knowledge base..."):
                try:
                    web_raw, search_method, search_errors = search_suppliers(
                        product=product.strip(),
                        country=country.strip() or None,
                        certifications=certifications.strip() or None,
                        quantity=quantity.strip() or None,
                        api_key=anthropic_key,
                        serpapi_key=serpapi_key,
                        qsr_category=selected_category,
                        user_profile=profile,
                    )
                    st.session_state["search_method"] = search_method

                    if search_method == "serpapi" and search_errors.get("claude"):
                        claude_err = search_errors["claude"]
                        if "RateLimitError" in claude_err:
                            st.info("ℹ️ Rate limit reached — using SerpAPI backup. Wait a moment before searching again.")
                        else:
                            st.info(
                                f"ℹ️ Claude search failed — using SerpAPI backup.\n"
                                f"Claude error: `{claude_err}`"
                            )
                    elif search_method == "none":
                        err_parts = []
                        if search_errors.get("claude"):
                            claude_err = search_errors["claude"]
                            if "RateLimitError" in claude_err:
                                err_parts.append("Rate limit reached — please wait a moment and try again.")
                            else:
                                err_parts.append(f"Claude error: `{claude_err}`")
                        if search_errors.get("serpapi"):
                            err_parts.append(f"SerpAPI error: `{search_errors['serpapi']}`")
                        if not err_parts:
                            err_parts.append("Both search methods returned no results.")
                        st.error(
                            "Search unavailable. Please check your API key and internet connection.\n\n"
                            + "\n\n".join(err_parts)
                        )
                        st.stop()
                except Exception as e:
                    st.error(f"Search failed: {type(e).__name__}: {e}")
                    web_raw = []
                    search_errors = {}
                    st.session_state["search_method"] = "none"

            raw_results = web_raw

            if not raw_results:
                st.warning("No results found. Try a simpler product name or fewer filters.")
            else:
                st.info(
                    f"Found **{len(raw_results)} supplier(s)**. "
                    "Claude is analysing each supplier..."
                )

                # ── Step 2: Claude AI Analysis ──
                progress_bar = st.progress(0, text="Starting analysis...")

                def update_progress(current: int, total: int):
                    """Updates the Streamlit progress bar during batch analysis."""
                    progress_bar.progress(current / total, text=f"🤖 Analysing {current}/{total}...")

                try:
                    summarized = batch_summarize(
                        suppliers_raw=raw_results,
                        api_key=anthropic_key,
                        progress_callback=update_progress,
                        user_profile=profile,
                    )
                except Exception as e:
                    st.error(f"AI analysis failed: {e}")
                    summarized = []

                progress_bar.empty()

                # Sort best-scoring suppliers to the top
                summarized.sort(key=lambda s: s.get("score", 0), reverse=True)

                st.session_state["search_results"]   = summarized
                st.session_state["searched_product"]  = product.strip()
                st.session_state["searched_category"] = selected_category
                st.session_state["save_status"]       = {}

    # ── Results Section ──
    if st.session_state.get("search_results"):
        results           = st.session_state["search_results"]
        searched_product  = st.session_state.get("searched_product", "")
        searched_category = st.session_state.get("searched_category", "")

        st.markdown("---")

        # ── Summary Metrics ──
        avg_score      = round(sum(s.get("score", 0) for s in results) / len(results), 1)
        verified_count = sum(1 for s in results if s.get("score", 0) >= 75)
        flagged_count  = sum(1 for s in results if s.get("risk_flags"))
        high_risk_count = sum(
            1 for s in results
            if s.get("risk_assessment", {}).get("risk_level") == "High"
        )

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Suppliers Found",  len(results))
        m2.metric("Avg Score",        f"{avg_score}/100")
        m3.metric("Verified (75+)",   verified_count)
        m4.metric("With Risk Flags",  flagged_count)
        m5.metric("High Risk",        high_risk_count)

        st.markdown(f"### 📦 Results for **{searched_product}**")
        st.html(f'<span style="{_MUTED}">Category: {searched_category} &nbsp;|&nbsp; '
                f'Location preference: {profile.get("location", "Ontario, Canada")}</span>')

        # ── Compare Controls ──
        compare_indices = [
            i for i in range(len(results))
            if st.session_state.get(f"compare_{i}", False)
        ]
        compare_count = len(compare_indices)

        compare_col, strategy_col, _ = st.columns([2, 2, 2])
        with compare_col:
            if compare_count == 0:
                st.caption("Tick ⊕ Compare on any cards below to compare suppliers.")
            elif compare_count > 4:
                st.warning(f"⚠ {compare_count} selected — only the first 4 will be compared.")
            else:
                if st.button(
                    f"🔄 Compare {compare_count} Supplier{'s' if compare_count != 1 else ''}",
                    type="primary",
                ):
                    st.session_state["show_comparison"] = True

        with strategy_col:
            if st.button("🎯 Generate Sourcing Strategy", type="secondary"):
                with st.spinner("Generating strategy recommendation..."):
                    try:
                        strat = generate_sourcing_strategy(
                            suppliers=results,
                            product=searched_product,
                            qsr_category=searched_category,
                            api_key=anthropic_key,
                            user_profile=profile,
                        )
                        st.session_state["sourcing_strategy"] = strat
                    except Exception as e:
                        st.error(f"Strategy generation failed: {e}")

        # ── Supplier Cards ──
        primary_classes = {"Manufacturer", "Local Vendor"}
        web_primary   = [s for s in results if s.get("supplier_class") in primary_classes]
        web_secondary = [s for s in results if s.get("supplier_class") not in primary_classes]

        if web_primary:
            st.markdown("##### 🏭 Manufacturers & Local Vendors")
        for i, supplier in enumerate(web_primary):
            render_supplier_card(supplier, i, searched_product, profile)
        offset = len(web_primary)

        if web_secondary:
            st.markdown("##### 🏪 Distributors & Traders")
        for i, supplier in enumerate(web_secondary):
            render_supplier_card(supplier, offset + i, searched_product, profile)

        # ── Comparison Panel ──
        if st.session_state.get("show_comparison") and compare_indices:
            selected_for_compare = [results[i] for i in compare_indices[:4]]
            render_comparison_panel(selected_for_compare)
            if st.button("✕ Close Comparison"):
                st.session_state["show_comparison"] = False
                st.rerun()

        # ── Sourcing Strategy ──
        strategy = st.session_state.get("sourcing_strategy")
        if strategy:
            render_sourcing_strategy(strategy)

    elif "search_results" not in st.session_state:
        st.html("""
        <div style="text-align:center; padding:60px 20px;">
            <div style="font-size:3.5rem; margin-bottom:12px;">🏭</div>
            <h3 style="color:#F0F4FF; font-family:'Space Grotesk',sans-serif;">Ready to find QSR suppliers</h3>
            <p style="color:#8892A4;">Choose a product category above, enter a product name, and click Search.</p>
            <p style="font-size:0.85rem; color:#8892A4;">Your profile location and preferences are automatically
            used to prioritise Canadian and CUSMA-eligible suppliers.</p>
        </div>
        """)


# ══════════════════════════════════════════════
# TAB 2 — SAVED SUPPLIERS
# ══════════════════════════════════════════════
with tab_saved:
    st.html(f'<div style="{_SECTION_H}">💾 Saved Suppliers</div>')

    saved_df = get_all_suppliers()

    if saved_df.empty:
        st.info("No suppliers saved yet. Use the Search tab to find and save suppliers.")
    else:
        st.markdown(f"**{len(saved_df)} supplier(s)** in your local database.")

        cats_in_db = ["All"] + sorted(saved_df["qsr_category"].dropna().unique().tolist())
        filter_cat = st.selectbox("Filter by category:", cats_in_db, index=0)

        display_df = saved_df if filter_cat == "All" else saved_df[saved_df["qsr_category"] == filter_cat]

        st.markdown("---")

        for _, row in display_df.iterrows():
            supplier_id = int(row["id"])
            scorecard   = get_scorecard_for_supplier(supplier_id)
            score       = int(row.get("score") or 0)
            risk_level  = str(row.get("risk_level") or "Unknown")
            sclass      = str(row.get("supplier_class") or "Distributor")

            avg_str = ""
            if scorecard:
                avg = round(
                    (scorecard["price_score"] + scorecard["lead_time_score"] + scorecard["reliability_score"]) / 3, 1
                )
                avg_str = f"  ·  ⭐ {avg}/10"

            with st.expander(
                f"**{row['name']}**  —  {row['product']}  |  📍 {row['location']}"
                f"  |  Score: {score}/100  |  Risk: {risk_level}{avg_str}",
                expanded=False,
            ):
                col_info, col_meta, col_actions = st.columns([3, 1.5, 1])

                with col_info:
                    if row.get("website"):
                        st.markdown(f"**Website:** [{row['website']}]({row['website']})")
                    st.markdown(f"**Contact:** {row.get('contact_info', 'N/A')}")
                    st.markdown(f"**MOQ:** {row.get('moq', 'N/A')}  |  **Lead Time:** {row.get('lead_time', 'N/A')}")
                    st.markdown(f"**Summary:** {row.get('summary', 'N/A')}")
                    st.markdown(f"**Strengths:** {row.get('strengths', 'N/A')}")

                    # Show landed cost if available
                    landed = parse_json_dict(row.get("landed_cost_data"))
                    if landed:
                        total_usd = landed.get("total_landed_usd", 0)
                        total_cad = landed.get("total_landed_cad", 0)
                        is_cusma  = landed.get("is_cusma", False)
                        cusma_tag = " 🍁 CUSMA" if is_cusma else ""
                        st.markdown(
                            f"**Landed Cost:** ${total_usd:.3f}/kg USD  |  ${total_cad:.3f}/kg CAD{cusma_tag}"
                        )

                with col_meta:
                    st.html(render_score_bar(score))

                    # Supplier class badge
                    st.html(f"<div style='margin-bottom:6px;'>{get_class_badge(sclass)}</div>")

                    # Risk badge
                    risk_data = parse_json_dict(row.get("risk_data"))
                    overall_risk = risk_data.get("overall_risk_score", 0)
                    st.html(f"<div style='margin-bottom:6px;'>{get_risk_badge(risk_level, overall_risk)}</div>")

                    # Certifications
                    certs = parse_json_list(row.get("certifications"))
                    st.html(f"<div style='margin-bottom:6px;'>{render_cert_badges(certs)}</div>")

                    # Risk flags
                    flags = parse_json_list(row.get("risk_flags"))
                    st.html(f"<div style='margin-bottom:6px;'>{render_risk_badges(flags)}</div>")

                    st.html(f'<span style="{_MUTED}">Saved: {str(row.get("saved_at",""))[:10]}</span>')

                with col_actions:
                    if scorecard:
                        avg = round(
                            (scorecard["price_score"] + scorecard["lead_time_score"] + scorecard["reliability_score"]) / 3, 1
                        )
                        st.metric("Manual Rating", f"{avg}/10")
                    else:
                        st.caption("Not manually rated yet")

                    # Two-step delete confirmation
                    confirm_key = f"confirm_{supplier_id}"
                    if st.session_state.get(confirm_key):
                        st.warning("Confirm delete?")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Yes", key=f"yes_{supplier_id}"):
                                delete_supplier(supplier_id)
                                st.session_state.pop(confirm_key, None)
                                st.rerun()
                        with c2:
                            if st.button("No", key=f"no_{supplier_id}"):
                                st.session_state.pop(confirm_key, None)
                                st.rerun()
                    else:
                        if st.button("🗑️ Delete", key=f"del_{supplier_id}"):
                            st.session_state[confirm_key] = True
                            st.rerun()

        st.markdown("---")
        csv = display_df.drop(columns=["id"], errors="ignore").to_csv(index=False)
        st.download_button(
            "⬇️ Export to CSV",
            data=csv,
            file_name="saved_suppliers.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════
# TAB 3 — SCORECARDS
# ══════════════════════════════════════════════
with tab_scores:
    st.html(f'<div style="{_SECTION_H}">📊 Supplier Scorecards</div>')
    st.caption("Rate your saved suppliers on key procurement criteria and compare them.")

    saved_df = get_all_suppliers()

    if saved_df.empty:
        st.info("Save some suppliers first, then come back here to rate them.")
    else:
        st.markdown("### ✍️ Rate a Supplier")

        supplier_options = {
            f"{row['name']}  ({row['product']})": int(row["id"])
            for _, row in saved_df.iterrows()
        }

        selected_label = st.selectbox("Select supplier to rate:", list(supplier_options.keys()))
        selected_id    = supplier_options[selected_label]
        existing       = get_scorecard_for_supplier(selected_id)

        with st.form("scorecard_form"):
            st.markdown(f"**Scoring:** {selected_label}")
            st.html(f'<span style="{_MUTED}">1 = Poor &nbsp;&nbsp; 5 = Average &nbsp;&nbsp; 10 = Excellent</span>')
            st.markdown("")

            c1, c2, c3 = st.columns(3)
            with c1:
                price_score = st.slider(
                    "💰 Price Competitiveness", min_value=1, max_value=10,
                    value=existing["price_score"] if existing else 5,
                )
            with c2:
                lead_time_score = st.slider(
                    "⏱️ Lead Time", min_value=1, max_value=10,
                    value=existing["lead_time_score"] if existing else 5,
                )
            with c3:
                reliability_score = st.slider(
                    "🔒 Reliability", min_value=1, max_value=10,
                    value=existing["reliability_score"] if existing else 5,
                )

            notes = st.text_area(
                "📝 Notes",
                value=existing["notes"] if existing else "",
                placeholder="e.g., Quick to respond, good MOQ flexibility, request a sample",
                height=90,
            )

            save_btn = st.form_submit_button("💾 Save Scorecard", type="primary")

        if save_btn:
            save_scorecard(selected_id, price_score, lead_time_score, reliability_score, notes)
            avg = round((price_score + lead_time_score + reliability_score) / 3, 1)
            st.success(f"Scorecard saved! Average score: **{avg} / 10**")

        st.markdown("---")
        st.markdown("### 🏆 Full Comparison")

        scores_df = get_all_scorecards()

        if scores_df.empty:
            st.info("Rate at least one supplier above to see the comparison.")
        else:
            top_row = scores_df.iloc[0]
            m1, m2, m3 = st.columns(3)
            m1.metric("Top Rated Supplier", top_row["Supplier"])
            m2.metric("Best Avg Score", f"{top_row['Avg Score']} / 10")
            m3.metric("Suppliers Rated", len(scores_df))

            # Show landed cost in the comparison table where available
            display_cols = ["Supplier", "Product", "Location", "Type", "Risk Level",
                            "Price (1-10)", "Lead Time (1-10)", "Reliability (1-10)",
                            "Avg Score", "Notes", "Last Rated"]
            display_scores = scores_df[[c for c in display_cols if c in scores_df.columns]]
            st.dataframe(display_scores, use_container_width=True, hide_index=True)

            st.markdown("### 📈 Score Breakdown by Supplier")
            chart_data = scores_df.set_index("Supplier")[
                ["Price (1-10)", "Lead Time (1-10)", "Reliability (1-10)"]
            ]
            st.bar_chart(chart_data)
