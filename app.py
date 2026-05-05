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
# GLOBAL CSS — design system
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
  --bg0:#0b0f14; --bg1:#111720; --bg2:#161e2a; --bg3:#1c2535; --bg4:#232f42;
  --border:#2a3a52; --border2:#334760;
  --text1:#e2e8f0; --text2:#94a3b8; --text3:#64748b;
  --accent:#4f83cc; --accent2:#3d6ba8; --accent-dim:#1e3a5f;
  --green:#22c55e; --amber:#f59e0b; --red:#ef4444;
  --teal:#06b6d4; --purple:#8b5cf6;
}

* { font-family:system-ui,-apple-system,sans-serif !important; box-sizing:border-box; }

.stApp { background-color:var(--bg0) !important; }
.stApp > header { background-color:var(--bg0) !important; }
.main .block-container { background-color:var(--bg0) !important; max-width:1400px !important; padding-top:1rem !important; }

[data-testid="stSidebar"] { background-color:var(--bg1) !important; border-right:1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color:var(--text1) !important; }

.stMarkdown, .stMarkdown p, .stMarkdown li { color:var(--text1) !important; }
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3,.stMarkdown h4 { color:var(--text1) !important; }

.stTextInput > div > div > input {
    background-color:var(--bg2) !important; border:1px solid var(--border) !important;
    color:var(--text1) !important; border-radius:6px !important; font-size:0.88rem !important;
}
.stTextInput > div > div > input:focus {
    border-color:var(--accent) !important; box-shadow:0 0 0 2px rgba(79,131,204,0.2) !important;
}
.stTextInput label { color:var(--text3) !important; font-size:0.78rem !important; text-transform:uppercase; letter-spacing:0.05em; }

.stSelectbox > div > div,
.stSelectbox [data-baseweb="select"] > div {
    background-color:var(--bg2) !important; border:1px solid var(--border) !important;
    color:var(--text1) !important;
}
.stSelectbox label { color:var(--text3) !important; font-size:0.78rem !important; text-transform:uppercase; letter-spacing:0.05em; }

.stButton > button {
    background:var(--accent-dim) !important; color:var(--accent) !important;
    border:1px solid var(--accent) !important; border-radius:6px !important;
    font-size:0.82rem !important; font-weight:600 !important; padding:6px 14px !important;
}
.stButton > button:hover { background:var(--accent2) !important; color:#fff !important; }
.stFormSubmitButton > button {
    background:var(--accent) !important; color:#fff !important;
    border:none !important; border-radius:6px !important;
    font-size:0.88rem !important; font-weight:600 !important; padding:10px 20px !important;
}
.stFormSubmitButton > button:hover { background:var(--accent2) !important; }
.stLinkButton a {
    background:transparent !important; border:1px solid var(--border2) !important;
    color:var(--text2) !important; border-radius:6px !important;
    font-size:0.8rem !important; padding:5px 12px !important;
}
.stLinkButton a:hover { border-color:var(--accent) !important; color:var(--accent) !important; }

.stTabs [data-baseweb="tab-list"] { background-color:var(--bg1) !important; border-bottom:1px solid var(--border) !important; gap:4px !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--text3) !important; font-size:0.82rem !important; font-weight:500 !important; border-radius:6px 6px 0 0 !important; padding:8px 16px !important; }
.stTabs [aria-selected="true"] { background:rgba(79,131,204,0.12) !important; color:var(--accent) !important; border-bottom:2px solid var(--accent) !important; }

.streamlit-expanderHeader { background-color:var(--bg3) !important; color:var(--text2) !important; border:1px solid var(--border) !important; border-radius:6px !important; font-size:0.8rem !important; }
.streamlit-expanderContent { background-color:var(--bg3) !important; border:1px solid var(--border) !important; border-top:none !important; border-radius:0 0 6px 6px !important; }

[data-testid="stMetricValue"] { color:var(--text1) !important; font-size:1.1rem !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] { color:var(--text3) !important; font-size:0.72rem !important; text-transform:uppercase; letter-spacing:0.05em; }
[data-testid="metric-container"] { background-color:var(--bg2) !important; border:1px solid var(--border) !important; border-radius:8px !important; padding:12px 16px !important; }

.stDataFrame { background-color:var(--bg2) !important; }
.stDataFrame thead tr th { background-color:var(--bg3) !important; color:var(--text3) !important; font-size:0.72rem !important; text-transform:uppercase; }
.stDataFrame tbody tr td { background-color:var(--bg2) !important; color:var(--text1) !important; font-size:0.82rem !important; }

.stProgress > div > div > div > div { background-color:var(--accent) !important; }

[data-testid="stInfo"]    { background:rgba(79,131,204,0.08) !important; border-left:3px solid var(--accent) !important; color:var(--text1) !important; }
[data-testid="stWarning"] { background:rgba(245,158,11,0.08) !important; border-left:3px solid var(--amber) !important; color:var(--text1) !important; }
[data-testid="stError"]   { background:rgba(239,68,68,0.08) !important; border-left:3px solid var(--red) !important; color:var(--text1) !important; }
[data-testid="stSuccess"] { background:rgba(34,197,94,0.08) !important; border-left:3px solid var(--green) !important; color:var(--text1) !important; }

div[data-testid="stCaptionContainer"] p { color:var(--text3) !important; font-size:0.78rem !important; }
.stCheckbox label { color:var(--text2) !important; }
.stSlider label, .stSlider div { color:var(--text2) !important; }
.stTextArea textarea { background-color:var(--bg2) !important; border:1px solid var(--border) !important; color:var(--text1) !important; border-radius:6px !important; font-size:0.85rem !important; }

::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:var(--bg0); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:var(--border2); }
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
# REUSABLE INLINE-STYLE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

_CARD  = "background:#161e2a; border:1px solid #2a3a52; border-radius:8px; padding:14px 16px 10px 16px; margin-bottom:8px;"
_CCARD = "background:#161e2a; border:1px solid #2a3a52; border-radius:8px; padding:14px; margin:4px 0;"

_NAME      = "font-size:0.88rem; font-weight:600; color:#e2e8f0; margin-bottom:2px;"
_CNAME     = "font-size:0.85rem; font-weight:600; color:#e2e8f0; margin-bottom:6px; border-bottom:1px solid #2a3a52; padding-bottom:6px;"
_CLABEL    = "font-size:0.68rem; color:#64748b; text-transform:uppercase; letter-spacing:0.08em; margin-top:8px; margin-bottom:2px;"
_CVALUE    = "font-size:0.82rem; color:#94a3b8; margin-bottom:2px;"
_MUTED     = "color:#64748b; font-size:0.78rem;"
_SECTION_H = "font-size:0.72rem; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; background:#111720; padding:6px 0 6px 0; margin-bottom:10px; border-bottom:1px solid #2a3a52;"

# Supplier-type badges
_CLASS_MANUFACTURER = "background:#1a3a28; color:#22c55e; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600; margin-right:3px;"
_CLASS_DISTRIBUTOR  = "background:#1e3a5f; color:#4f83cc; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600; margin-right:3px;"
_CLASS_TRADER       = "background:#3a2a10; color:#f59e0b; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600; margin-right:3px;"
_CLASS_LOCAL        = "background:#2a1a3a; color:#8b5cf6; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600; margin-right:3px;"

# Risk badges
_RISK_HIGH   = "background:#3a1010; color:#ef4444; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600;"
_RISK_MEDIUM = "background:#3a2a10; color:#f59e0b; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600;"
_RISK_LOW    = "background:#1a3a28; color:#22c55e; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600;"

_CUSMA         = "background:#1e3a5f; color:#4f83cc; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600;"
_CURATED_BADGE = "background:#2a1a3a; color:#8b5cf6; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600; margin-right:3px;"

_CERT_PILL = "border:1px solid #22c55e; color:#22c55e; padding:1px 6px; border-radius:3px; font-size:0.68rem; font-weight:500; margin-right:3px; display:inline-block; margin-bottom:2px;"
_RISK_PILL = "background:#3a1010; color:#ef4444; padding:1px 6px; border-radius:3px; font-size:0.68rem; font-weight:500; margin-right:3px; display:inline-block; margin-bottom:2px;"
_BAR_BG    = "background:#1c2535; border-radius:3px; height:4px; width:100%; margin:4px 0 2px 0; overflow:hidden;"


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
    """Compact score label for comparison panel."""
    tier  = get_score_tier(score)
    color = tier["color"]
    label = tier["label"]
    return (f'<div style="text-align:center; font-size:1rem; font-weight:700; color:{color};">'
            f'{score}<span style="font-size:0.65rem; color:#64748b;">/100</span></div>'
            f'<div style="text-align:center; font-size:0.65rem; color:{color}; letter-spacing:0.05em;">{label.upper()}</div>')


def generate_score_ring(score: int) -> str:
    """60×60px SVG radial ring gauge. r=23, circumference≈144."""
    color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
    offset = 144 - (score / 100 * 144)
    return (
        f'<div style="display:inline-flex; align-items:center; justify-content:center; flex-shrink:0;">'
        f'<svg width="52" height="52" viewBox="0 0 56 56">'
        f'<circle cx="28" cy="28" r="23" fill="none" stroke="#1c2535" stroke-width="5"/>'
        f'<circle cx="28" cy="28" r="23" fill="none" stroke="{color}" stroke-width="5"'
        f' stroke-dasharray="144" stroke-dashoffset="{offset:.1f}"'
        f' stroke-linecap="round" transform="rotate(-90 28 28)"/>'
        f'<text x="28" y="33" text-anchor="middle" font-size="13" font-weight="600"'
        f' fill="#e2e8f0" font-family="system-ui">{score}</text>'
        f'</svg>'
        f'</div>'
    )


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
    if certs:
        return " ".join(f'<span style="{_CERT_PILL}">✓ {c}</span>' for c in certs)
    if supplier_class in ("Manufacturer", "Local Vendor"):
        return '<span style="border:1px solid #f59e0b; color:#f59e0b; padding:1px 6px; border-radius:3px; font-size:0.68rem;">⚠ Unconfirmed — verify</span>'
    return '<span style="color:#ef4444; font-size:0.72rem;">✕ None found</span>'


def render_risk_badges(flags: list) -> str:
    if not flags:
        return '<span style="color:#22c55e; font-size:0.72rem;">✓ No flags</span>'
    return " ".join(f'<span style="{_RISK_PILL}">{flag}</span>' for flag in flags)


def _risk_color(score: int) -> str:
    if score >= 61:
        return "#ef4444"
    if score >= 31:
        return "#f59e0b"
    return "#22c55e"


def _risk_tag(score: int) -> str:
    if score >= 61:
        return "High"
    if score >= 31:
        return "Med"
    return "Low"


def _risk_width(score: int) -> int:
    """Map 0–100 risk score to a fill-width percentage for the bar (15–80%)."""
    return max(5, min(80, score))


def render_risk_bar(score: int, label: str, color: str) -> str:
    """Horizontal bar with always-visible score and risk level label."""
    tag = _risk_tag(score)
    w   = _risk_width(score)
    risk_label = "Low" if score <= 30 else "Medium" if score <= 60 else "High"
    return (
        f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:7px;">'
        f'<span style="width:90px; font-size:0.75rem; color:#94a3b8; flex-shrink:0;">{label}</span>'
        f'<div style="flex:1; background:#1c2535; border-radius:3px; height:8px; overflow:hidden;">'
        f'<div style="width:{w}%; height:8px; background:{color}; border-radius:3px;"></div>'
        f'</div>'
        f'<span style="width:72px; font-size:0.72rem; font-weight:600; color:{color}; text-align:right;">{score}/100 {risk_label}</span>'
        f'</div>'
    )


def render_risk_dashboard(risk: dict):
    if not risk:
        st.caption("Risk data not available.")
        return
    geo = risk.get("geopolitical_risk", 0)
    env = risk.get("environmental_risk", 0)
    sup = risk.get("supplier_risk", 0)
    html = (
        f'<div style="margin-bottom:4px;">'
        f'<span style="font-size:0.68rem; font-weight:600; color:#f59e0b; text-transform:uppercase; letter-spacing:0.08em;">● RISK INTELLIGENCE</span>'
        f'</div>'
        + render_risk_bar(geo, "Geopolitical", _risk_color(geo))
        + render_risk_bar(env, "Environmental", _risk_color(env))
        + render_risk_bar(sup, "Supplier",      _risk_color(sup))
    )
    st.markdown(html, unsafe_allow_html=True)


def render_logistics_section(logistics: dict, landed: dict):
    if not logistics and not landed:
        st.caption("Logistics data not available.")
        return

    # ── Best Logistics (top recommended mode only) ──
    if logistics:
        priority = ["road", "sea_fcl", "sea_lcl", "air", "intermodal"]
        rows_html = '<div style="font-size:0.75rem; font-weight:600; color:#8b5cf6; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">● BEST LOGISTICS</div>'
        for key in priority + [k for k in logistics if k not in priority]:
            if key not in logistics:
                continue
            opt  = logistics[key]
            mode = opt.get("mode", key)
            days = opt.get("transit_days", ("?", "?"))
            days_str = f"{days[0]}–{days[1]}d" if isinstance(days, tuple) else str(days)
            rows_html += (
                f'<div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">'
                f'<span style="font-size:0.82rem; color:#e2e8f0; font-weight:500; min-width:90px;">{mode}</span>'
                f'<span style="border:1px solid #2a3a52; color:#94a3b8; padding:1px 5px; border-radius:3px; font-size:0.72rem;">{days_str}</span>'
                f'<span style="background:#4f83cc22; color:#4f83cc; border:1px solid #4f83cc44; padding:1px 5px; border-radius:3px; font-size:0.72rem;">Recommended</span>'
                f'</div>'
            )
            break
        st.html(rows_html)

    # ── Landed Cost ──
    if landed:
        is_cusma  = landed.get("is_cusma", False)
        tariff    = landed.get("tariff_rate_pct", 12)
        total_usd = landed.get("total_landed_usd", 0)
        total_cad = landed.get("total_landed_cad", 0)

        items = [
            ("Product (FOB)",    landed.get("fob_price_usd", 0)),
            ("Freight",          landed.get("freight_per_kg_usd", 0)),
            (f"Duty {tariff:.0f}%", landed.get("import_duty_per_kg_usd", 0)),
            ("Insurance",        landed.get("insurance_per_kg_usd", 0)),
            ("Compliance/Other", (landed.get("cfia_fee_per_kg_usd", 0)
                                  + landed.get("inland_per_kg_usd", 0)
                                  + landed.get("inventory_cost_per_kg_usd", 0))),
        ]
        lines = "".join(
            f'<div style="display:flex; justify-content:space-between; font-size:0.72rem; padding:1px 0;">'
            f'<span style="color:#64748b; font-size:0.78rem;">{lbl}</span>'
            f'<span style="color:{"#f59e0b" if "Duty" in lbl and v > 0 else "#94a3b8"}; font-size:0.78rem;">${v:.3f}/kg</span>'
            f'</div>'
            for lbl, v in items
        )
        cusma_badge = (f'<span style="{_CUSMA}">🍁 CUSMA 0%</span>' if is_cusma
                       else f'<span style="color:#f59e0b; font-size:0.68rem;">Duty: {tariff:.0f}%</span>')
        st.html(f"""
        <div style="font-size:0.75rem; font-weight:600; color:#06b6d4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">● LANDED COST (USD)</div>
        {lines}
        <div style="display:flex; justify-content:space-between; border-top:1px solid #2a3a52; margin-top:4px; padding-top:4px;">
            <span style="font-size:0.82rem; font-weight:600; color:#06b6d4;">Total</span>
            <span style="font-size:0.82rem; font-weight:600; color:#06b6d4;">${total_usd:.3f}/kg &nbsp;<span style="color:#64748b; font-weight:400;">${total_cad:.3f} CAD</span></span>
        </div>
        <div style="margin-top:4px;">{cusma_badge}</div>
        """)


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
    score     = supplier.get("score", 0)
    sclass    = supplier.get("supplier_class", supplier.get("supplier_type", "Distributor"))
    certs     = supplier.get("certifications", [])
    flags     = supplier.get("risk_flags", [])
    risk      = supplier.get("risk_assessment", {})
    logistics = supplier.get("logistics_options", {})
    landed    = supplier.get("landed_cost", {})

    risk_level  = risk.get("risk_level", "Unknown")
    overall_risk = risk.get("overall_risk_score", 0)
    is_cusma    = landed.get("is_cusma", False)
    total_usd   = landed.get("total_landed_usd", 0)
    is_curated  = supplier.get("is_curated", False)
    contact_note = supplier.get("contact_note", "") or supplier.get("contact_info", "")

    # Score tier for left border accent
    ring_color = "#22c55e" if score >= 75 else ("#f59e0b" if score >= 50 else "#ef4444")

    # Top-pick: highest-scoring Manufacturer/Local Vendor
    is_top = (score == max((s.get("score", 0) for s in [supplier]), default=0)
              and sclass in ("Manufacturer", "Local Vendor") and score >= 60)

    top_badge  = '<span style="background:#1a3a28; color:#22c55e; border:1px solid #22c55e44; padding:1px 6px; border-radius:3px; font-size:0.65rem; font-weight:700; margin-right:4px;">★ TOP PICK</span>' if is_top else ""
    cur_badge  = f'<span style="{_CURATED_BADGE}">⭐ Verified</span>' if is_curated else ""
    class_badge = get_class_badge(sclass)
    cusma_badge = (f'<span style="{_CUSMA}">🍁 CUSMA</span>' if is_cusma
                   else '<span style="background:#3a1010; color:#ef4444; padding:2px 7px; border-radius:4px; font-size:0.68rem;">Non-CUSMA</span>')
    risk_badge  = get_risk_badge(risk_level, overall_risk)

    tier_label  = "PROMISING" if score >= 50 else "NEEDS VERIFICATION"
    tier_color  = "#f59e0b"   if score >= 50 else "#ef4444"
    if score >= 75:
        tier_label = "VERIFIED"
        tier_color = "#22c55e"
    status_badge = f'<span style="background:{tier_color}22; color:{tier_color}; border:1px solid {tier_color}44; padding:2px 7px; border-radius:4px; font-size:0.68rem; font-weight:600;">{tier_label}</span>'

    cost_note = f'${total_usd:.2f}/kg' if total_usd else ""
    moq       = supplier.get("moq", "")
    lead      = supplier.get("lead_time", "")
    summary   = supplier.get("summary", "")
    website   = supplier.get("website", "")

    border_extra = f"box-shadow:0 0 0 1px #1e3a5f; border-color:#3d6ba8;" if is_top else ""

    card_html = f"""
    <div style="{_CARD} border-left:3px solid {ring_color}; {border_extra}">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
            <div style="font-size:0.92rem; font-weight:600; color:#e2e8f0; line-height:1.3; padding-right:12px;">
                {top_badge}{cur_badge}{supplier.get('name','Unknown Supplier')}
            </div>
            <span style="background:{ring_color}22; color:{ring_color}; border:1px solid {ring_color}44; padding:4px 12px; border-radius:12px; font-size:0.82rem; font-weight:700; flex-shrink:0;">{score}</span>
        </div>
        <div>
            <div style="font-size:0.78rem; color:#94a3b8; margin-bottom:6px;">
                📍 {supplier.get('location','Not specified')}
                {f'&nbsp;·&nbsp;<a href="{website}" target="_blank" style="color:#4f83cc; text-decoration:none;">↗ website</a>' if website and website.startswith("http") else ""}
                {f"&nbsp;·&nbsp;<span style='color:#22c55e; font-weight:600;'>{cost_note}</span>" if cost_note else ""}
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:6px; align-items:center;">
                {class_badge}{cusma_badge}{status_badge}{risk_badge}
            </div>
            <div style="margin-bottom:5px; font-size:0.75rem; color:#94a3b8;">CERTS &nbsp;{render_cert_badges(certs, sclass)}</div>
            <div style="margin-bottom:6px; font-size:0.75rem; color:#94a3b8;">FLAGS &nbsp;{render_risk_badges(flags[:3])}</div>
            <div style="color:#94a3b8; font-size:0.82rem; line-height:1.5; margin-bottom:6px; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; max-height:2.9em; word-break:break-word;">
                {summary}
            </div>
            <div style="display:flex; gap:16px; font-size:0.76rem; color:#94a3b8; flex-wrap:wrap;">
                {"<span>MOQ: <strong style='color:#94a3b8;'>" + moq + "</strong></span>" if moq and moq.lower() != "not specified" else ""}
                {"<span>Lead: <strong style='color:#94a3b8;'>" + lead + "</strong></span>" if lead and lead.lower() != "not specified" else ""}
                {"<span>📞 <span style='color:#94a3b8;'>" + contact_note + "</span></span>" if contact_note else ""}
            </div>
        </div>
    </div>"""

    col_name, col_ring = st.columns([9, 1])
    with col_name:
        st.html(card_html)
    with col_ring:
        st.html(generate_score_ring(score))

    # ── Inline detail section: Risk | Landed Cost | Logistics ──
    col_risk, col_cost, col_log = st.columns(3)

    with col_risk:
        render_risk_dashboard(risk)

    with col_cost:
        render_logistics_section({}, landed)

    with col_log:
        render_logistics_section(logistics, {})

    # ── Action buttons ──
    col_save, col_cmp, col_web = st.columns(3)

    with col_save:
        save_key = f"save_{index}"
        if st.session_state.get("save_status", {}).get(save_key):
            st.success("Saved ✓")
        elif st.button("Save", key=save_key, use_container_width=True):
            if supplier_already_saved(supplier.get("name", ""), product):
                st.warning("Already saved.")
            else:
                save_supplier(supplier)
                st.session_state.setdefault("save_status", {})[save_key] = True
                st.rerun()

    with col_cmp:
        st.checkbox("Compare", key=f"compare_{index}",
                    value=st.session_state.get(f"compare_{index}", False))

    with col_web:
        if website and website.startswith("http"):
            st.link_button("↗ Website", website, use_container_width=True)

    st.html("<div style='height:2px;'></div>")


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

        # ── Metrics bar ──
        avg_score       = round(sum(s.get("score", 0) for s in results) / len(results), 1)
        verified_count  = sum(1 for s in results if s.get("score", 0) >= 75)
        cusma_count     = sum(1 for s in results if s.get("landed_cost", {}).get("is_cusma"))
        unconf_count    = sum(1 for s in results if not s.get("certifications"))
        high_risk_count = sum(1 for s in results if s.get("risk_assessment", {}).get("risk_level") == "High")
        best_cost       = min((s.get("landed_cost", {}).get("total_landed_usd", 999) for s in results), default=0)
        best_cost_str   = f"${best_cost:.2f}/kg" if best_cost and best_cost < 900 else "—"

        def _metric(label, value, color):
            return (f'<div style="background:#161e2a; border:1px solid #2a3a52; border-radius:6px;'
                    f' padding:10px 14px; flex:1; min-width:90px;">'
                    f'<div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:3px;">{label}</div>'
                    f'<div style="font-size:1rem; font-weight:700; color:{color};">{value}</div>'
                    f'</div>')

        st.html(
            f'<div style="display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap;">'
            + _metric("Suppliers", len(results), "#4f83cc")
            + _metric("Avg Score", f"{avg_score}/100", "#e2e8f0")
            + _metric("CUSMA", cusma_count, "#22c55e")
            + _metric("Unconfirmed Certs", unconf_count, "#f59e0b")
            + _metric("High Risk", high_risk_count, "#ef4444")
            + _metric("Best Landed", best_cost_str, "#22c55e")
            + '</div>'
        )

        # ── Strategy bar (above cards) ──
        strategy = st.session_state.get("sourcing_strategy")
        strat_col, btn_col = st.columns([5, 1])
        with btn_col:
            if st.button("Generate Strategy →", use_container_width=True):
                with st.spinner("Generating..."):
                    try:
                        strat = generate_sourcing_strategy(
                            suppliers=results, product=searched_product,
                            qsr_category=searched_category,
                            api_key=anthropic_key, user_profile=profile,
                        )
                        st.session_state["sourcing_strategy"] = strat
                        st.rerun()
                    except Exception as e:
                        st.error(f"Strategy failed: {e}")
        with strat_col:
            if strategy:
                primary   = strategy.get("primary_supplier", "—")
                backup    = strategy.get("backup_supplier", "—")
                vol_split = strategy.get("volume_split", "—")
                savings   = strategy.get("estimated_savings_note", "")
                savings_html = f'<span style="font-size:0.75rem; color:#22c55e;">{savings}</span>' if savings else ""
                st.html(
                    f'<div style="background:#161e2a; border:1px solid #2a3a52; border-radius:6px;'
                    f' padding:8px 14px; display:flex; gap:20px; align-items:center; flex-wrap:wrap;">'
                    f'<span style="font-size:0.75rem; color:#64748b;">Primary: <strong style="color:#4f83cc;">{primary}</strong></span>'
                    f'<span style="font-size:0.75rem; color:#64748b;">Backup: <strong style="color:#94a3b8;">{backup}</strong></span>'
                    f'<span style="font-size:0.75rem; color:#64748b;">Split: <strong style="color:#e2e8f0;">{vol_split}</strong></span>'
                    f'{savings_html}'
                    f'</div>'
                )
            else:
                st.caption("Click Generate Strategy for an AI sourcing recommendation.")

        # ── Compare controls ──
        compare_indices = [i for i in range(len(results)) if st.session_state.get(f"compare_{i}")]
        compare_count = len(compare_indices)
        if compare_count > 0:
            c1, c2 = st.columns([2, 4])
            with c1:
                if compare_count > 4:
                    st.warning(f"{compare_count} selected — max 4")
                elif st.button(f"Compare {compare_count} selected →", type="primary"):
                    st.session_state["show_comparison"] = True

        # ── Section header + single-column card list ──
        primary_classes = {"Manufacturer", "Local Vendor"}
        web_primary   = [s for s in results if s.get("supplier_class") in primary_classes]
        web_secondary = [s for s in results if s.get("supplier_class") not in primary_classes]
        buyer_loc     = profile.get("location", "Ontario, Canada")

        if web_primary:
            st.html(
                f'<div style="{_SECTION_H}">MANUFACTURERS & LOCAL VENDORS — {searched_product} · {buyer_loc} · {len(web_primary)} of {len(results)} shown</div>'
            )
            for i, supplier in enumerate(web_primary):
                with st.container():
                    render_supplier_card(supplier, i, searched_product, profile)

        offset = len(web_primary)
        if web_secondary:
            st.html(
                f'<div style="{_SECTION_H}">DISTRIBUTORS & TRADERS — {len(web_secondary)} shown</div>'
            )
            for i, supplier in enumerate(web_secondary):
                with st.container():
                    render_supplier_card(supplier, offset + i, searched_product, profile)

        # ── Comparison Panel ──
        if st.session_state.get("show_comparison") and compare_indices:
            selected_for_compare = [results[i] for i in compare_indices[:4]]
            render_comparison_panel(selected_for_compare)
            if st.button("✕ Close Comparison"):
                st.session_state["show_comparison"] = False
                st.rerun()

        # ── Full strategy detail (below cards) ──
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
