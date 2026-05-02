# logistics_config.py
# Stores all freight rate assumptions, tariff schedules, and transit time estimates.
# Destination is always Ontario, Canada (buyer's location from user profile).
#
# HOW TO USE:
#   Import the constants you need in ai_summarizer.py to calculate logistics options
#   and total landed cost per supplier. These are industry averages for 2024-2025.
#   Update them when market rates shift significantly (check Freightos, Xeneta, or
#   a freight forwarder quote for current rates).

# ─────────────────────────────────────────────────────────────────────────────
# DESTINATION
# ─────────────────────────────────────────────────────────────────────────────
DESTINATION_PROVINCE = "Ontario, Canada"
DESTINATION_CITY = "Toronto, ON"

# ─────────────────────────────────────────────────────────────────────────────
# COUNTRY → REGION MAPPING
# Maps a country name (lowercase) to one of our region codes.
# Region codes are used to look up freight rates below.
# ─────────────────────────────────────────────────────────────────────────────
COUNTRY_TO_REGION: dict[str, str] = {
    # Canada — local shipments
    "canada": "canada",

    # USA — CUSMA partner, road/truck is default mode
    "united states": "usa", "usa": "usa", "us": "usa", "america": "usa",
    "united states of america": "usa",

    # Asia Pacific
    "china": "asia", "thailand": "asia", "vietnam": "asia", "indonesia": "asia",
    "malaysia": "asia", "philippines": "asia", "india": "asia", "bangladesh": "asia",
    "cambodia": "asia", "myanmar": "asia", "south korea": "asia", "japan": "asia",
    "taiwan": "asia", "hong kong": "asia", "singapore": "asia", "pakistan": "asia",

    # Europe
    "germany": "europe", "france": "europe", "spain": "europe", "italy": "europe",
    "netherlands": "europe", "belgium": "europe", "poland": "europe",
    "uk": "europe", "united kingdom": "europe", "denmark": "europe",
    "sweden": "europe", "norway": "europe", "finland": "europe",

    # South America
    "brazil": "south_america", "argentina": "south_america", "chile": "south_america",
    "peru": "south_america", "colombia": "south_america", "ecuador": "south_america",
    "uruguay": "south_america", "paraguay": "south_america",

    # Central America & Mexico (CUSMA eligible for Mexico)
    "mexico": "mexico",
    "guatemala": "central_america", "costa rica": "central_america",
    "honduras": "central_america", "panama": "central_america",
    "el salvador": "central_america", "nicaragua": "central_america",

    # Middle East
    "turkey": "middle_east", "uae": "middle_east", "united arab emirates": "middle_east",
    "saudi arabia": "middle_east", "israel": "middle_east", "egypt": "middle_east",
    "iran": "middle_east", "jordan": "middle_east",

    # Africa
    "south africa": "africa", "kenya": "africa", "ethiopia": "africa",
    "ghana": "africa", "ivory coast": "africa", "nigeria": "africa",
    "morocco": "africa", "tanzania": "africa", "uganda": "africa",

    # Oceania
    "australia": "oceania", "new zealand": "oceania",
}

# ─────────────────────────────────────────────────────────────────────────────
# CUSMA / USMCA ELIGIBLE COUNTRIES
# Canada, USA, and Mexico qualify for 0% import duty under the free-trade agreement.
# ─────────────────────────────────────────────────────────────────────────────
CUSMA_COUNTRIES: set[str] = {
    "canada", "united states", "usa", "us", "america",
    "united states of america", "mexico",
}

# ─────────────────────────────────────────────────────────────────────────────
# SEA FREIGHT RATES (to Ontario via Canadian port of entry)
#
# fcl_20ft_usd   — Full Container Load, 20-foot container, USD total
# fcl_40ft_usd   — Full Container Load, 40-foot container, USD total
# lcl_per_cbm_usd — Less-than-Container Load, per cubic meter
# transit_days_range — (min, max) port-to-port + inland rail/truck to Ontario
# ─────────────────────────────────────────────────────────────────────────────
SEA_FREIGHT: dict[str, dict] = {
    "asia": {
        "port_of_entry": "Vancouver, BC",
        "fcl_20ft_usd": 2200,
        "fcl_40ft_usd": 3800,
        "lcl_per_cbm_usd": 85,
        "transit_days_range": (25, 35),
        "route_note": "Asia → Vancouver (sea) → CN Rail → Ontario",
        "intermodal_available": True,
    },
    "europe": {
        "port_of_entry": "Montreal, QC or Halifax, NS",
        "fcl_20ft_usd": 1800,
        "fcl_40ft_usd": 3200,
        "lcl_per_cbm_usd": 75,
        "transit_days_range": (18, 28),
        "route_note": "Europe → Halifax or Montreal → Truck to Ontario",
        "intermodal_available": False,
    },
    "south_america": {
        "port_of_entry": "Montreal, QC",
        "fcl_20ft_usd": 2400,
        "fcl_40ft_usd": 4200,
        "lcl_per_cbm_usd": 90,
        "transit_days_range": (20, 30),
        "route_note": "South America → Panama Canal → Montreal",
        "intermodal_available": False,
    },
    "middle_east": {
        "port_of_entry": "Halifax, NS",
        "fcl_20ft_usd": 2000,
        "fcl_40ft_usd": 3500,
        "lcl_per_cbm_usd": 80,
        "transit_days_range": (22, 32),
        "route_note": "Middle East → Suez Canal → Halifax → Ontario",
        "intermodal_available": False,
    },
    "africa": {
        "port_of_entry": "Halifax, NS",
        "fcl_20ft_usd": 2600,
        "fcl_40ft_usd": 4500,
        "lcl_per_cbm_usd": 95,
        "transit_days_range": (25, 38),
        "route_note": "Africa → Atlantic Ocean → Halifax → Ontario",
        "intermodal_available": False,
    },
    "oceania": {
        "port_of_entry": "Vancouver, BC",
        "fcl_20ft_usd": 2500,
        "fcl_40ft_usd": 4300,
        "lcl_per_cbm_usd": 90,
        "transit_days_range": (22, 30),
        "route_note": "Australia/NZ → Vancouver (sea) → CN Rail → Ontario",
        "intermodal_available": True,
    },
    "central_america": {
        "port_of_entry": "Montreal, QC",
        "fcl_20ft_usd": 2000,
        "fcl_40ft_usd": 3500,
        "lcl_per_cbm_usd": 75,
        "transit_days_range": (15, 22),
        "route_note": "Central America → Panama Canal → Montreal → Ontario",
        "intermodal_available": False,
    },
    "mexico": {
        "port_of_entry": "Land border (CUSMA — truck to Ontario)",
        "fcl_20ft_usd": 1500,
        "fcl_40ft_usd": 2600,
        "lcl_per_cbm_usd": 60,
        "transit_days_range": (5, 10),
        "route_note": "Mexico → US border → Ontario (truck, CUSMA eligible)",
        "intermodal_available": False,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# AIR FREIGHT RATES (per kg, all origins)
# Air freight is 5-10× more expensive than sea — flag it as emergency/premium.
# ─────────────────────────────────────────────────────────────────────────────
AIR_FREIGHT: dict[str, dict] = {
    "asia":            {"cost_per_kg_usd": 4.50, "transit_days_range": (3, 7)},
    "europe":          {"cost_per_kg_usd": 3.50, "transit_days_range": (2, 5)},
    "south_america":   {"cost_per_kg_usd": 4.00, "transit_days_range": (2, 5)},
    "middle_east":     {"cost_per_kg_usd": 3.80, "transit_days_range": (2, 5)},
    "africa":          {"cost_per_kg_usd": 5.00, "transit_days_range": (3, 6)},
    "oceania":         {"cost_per_kg_usd": 5.50, "transit_days_range": (2, 4)},
    "central_america": {"cost_per_kg_usd": 3.00, "transit_days_range": (2, 4)},
    "mexico":          {"cost_per_kg_usd": 2.50, "transit_days_range": (1, 3)},
    "usa":             {"cost_per_kg_usd": 1.50, "transit_days_range": (1, 2)},
    "canada":          {"cost_per_kg_usd": 0.80, "transit_days_range": (1, 2)},
}

# ─────────────────────────────────────────────────────────────────────────────
# ROAD / TRUCK RATES (North America only — Canada, USA, Mexico)
# ─────────────────────────────────────────────────────────────────────────────
ROAD_FREIGHT: dict[str, dict] = {
    "canada": {
        "description": "Canadian domestic truck",
        "cost_per_kg_usd": 0.10,
        "transit_days_range": (1, 4),
        "note": "Best option for Canadian suppliers — no tariffs, shortest lead time",
    },
    "usa": {
        "description": "US-Canada cross-border truck (CUSMA)",
        "cost_per_kg_usd": 0.18,
        "transit_days_range": (1, 4),
        "note": "CUSMA eliminates tariffs — cost-effective for US suppliers",
    },
    "mexico": {
        "description": "Mexico-Canada truck via US (CUSMA)",
        "cost_per_kg_usd": 0.28,
        "transit_days_range": (4, 7),
        "note": "CUSMA eligible — driver change required at US-Canada border",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# INTERMODAL (Sea + Rail) — Asia and Oceania to Ontario via Vancouver
# CN Rail connects Vancouver to Toronto/Montreal — very common for Asian imports.
# ─────────────────────────────────────────────────────────────────────────────
INTERMODAL: dict[str, dict] = {
    "asia": {
        "route": "Asia → Vancouver (sea, ~18d) → CN Rail → Ontario (~7d)",
        "total_transit_days_range": (28, 38),
        "extra_cost_vs_sea_usd_per_container": 800,  # Rail leg adds ~$800
        "note": "Standard route for Asian food imports to Ontario",
    },
    "oceania": {
        "route": "Australia/NZ → Vancouver (sea, ~14d) → CN Rail → Ontario (~7d)",
        "total_transit_days_range": (24, 32),
        "extra_cost_vs_sea_usd_per_container": 800,
        "note": "Same rail leg as Asia route after Vancouver arrival",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# INLAND FREIGHT (port → Ontario distribution centre)
# Cost per kg to truck from the Canadian port to an Ontario DC.
# These costs are included in the total landed cost calculation.
# ─────────────────────────────────────────────────────────────────────────────
INLAND_TO_ONTARIO: dict[str, dict] = {
    "Vancouver, BC":                      {"cost_per_kg_usd": 0.09, "days": 5},
    "Montreal, QC":                       {"cost_per_kg_usd": 0.04, "days": 1},
    "Halifax, NS":                        {"cost_per_kg_usd": 0.07, "days": 2},
    "Montreal, QC or Halifax, NS":        {"cost_per_kg_usd": 0.05, "days": 2},
    "Land border (CUSMA — truck to Ontario)": {"cost_per_kg_usd": 0.06, "days": 2},
}

# Fallback inland cost when port is not in the lookup table
INLAND_FALLBACK = {"cost_per_kg_usd": 0.06, "days": 3}

# ─────────────────────────────────────────────────────────────────────────────
# TARIFF RATES
# CUSMA (Canada-US-Mexico Agreement): 0% duty on qualifying food goods.
# Standard MFN rate for food imports from non-CUSMA countries: ~12%.
# Actual rates vary by HS code — consult the CBSA tariff schedule for precision.
# ─────────────────────────────────────────────────────────────────────────────
TARIFF_RATES = {
    "cusma": 0.00,    # 0% — Canada, USA, Mexico
    "standard": 0.12, # 12% — all other countries (approximate average)
}

# CFIA (Canadian Food Inspection Agency) inspection fee, per kg imported.
# This is an approximation — actual fees depend on product type and shipment size.
CFIA_FEE_PER_KG_CAD = 0.02  # CAD per kg

# Marine cargo insurance — standard rate as a percentage of CIF value.
INSURANCE_RATE = 0.005  # 0.5% of FOB price

# Inventory holding cost — approximates 3 months of carrying costs (capital + warehouse).
# Formula: (15% annual holding cost / 12 months) × 3 months average cycle.
INVENTORY_HOLDING_RATE = 0.0375  # 3.75% of FOB price

# ─────────────────────────────────────────────────────────────────────────────
# CURRENCY
# ─────────────────────────────────────────────────────────────────────────────
USD_TO_CAD = 1.37   # 1 USD = 1.37 CAD (approximate — update periodically)
CAD_TO_USD = 0.73

# Average weight per 20-foot container for food products (kg).
# Actual weight depends on product density — this is a reasonable mid-estimate.
KG_PER_20FT_CONTAINER = 17000

# ─────────────────────────────────────────────────────────────────────────────
# TYPICAL FOB PRICE RANGES (USD/kg) by QSR Category
# Used when no price data is available from the supplier.
# These are rough mid-market estimates — actual quotes will vary.
# ─────────────────────────────────────────────────────────────────────────────
TYPICAL_FOB_PRICES: dict[str, dict] = {
    "🍗 Proteins":           {"low": 1.50, "mid": 3.00, "high": 6.00},
    "🥬 Produce":            {"low": 0.30, "mid": 0.80, "high": 2.00},
    "📦 Packaging":          {"low": 0.50, "mid": 1.20, "high": 3.00},
    "🧂 Condiments & Sauces": {"low": 0.80, "mid": 1.50, "high": 4.00},
    "🌾 Dry Goods":          {"low": 0.40, "mid": 0.90, "high": 2.50},
    "❄️ Frozen & Cold Chain": {"low": 1.20, "mid": 2.50, "high": 5.00},
    "General":               {"low": 0.80, "mid": 1.50, "high": 4.00},
}


# ─────────────────────────────────────────────────────────────────────────────
# COUNTRY-SPECIFIC CERTIFICATION SEARCH TERMS
# Used in SerpAPI queries to surface suppliers certified to local food-safety
# standards rather than always searching for FDA (a US/Canada regulator).
#
# Keys are lowercase country names matching the "Country of Origin" form field.
# "_default" is the fallback when the origin country is not listed or not given.
# ─────────────────────────────────────────────────────────────────────────────
COUNTRY_CERT_TERMS: dict[str, str] = {
    # North America — FDA and CFIA are the primary regulators
    "canada":        '"CFIA" OR "FDA" OR "HACCP"',
    "usa":           '"FDA" OR "USDA" OR "HACCP"',
    "united states": '"FDA" OR "USDA" OR "HACCP"',
    "mexico":        '"FDA" OR "COFEPRIS" OR "HACCP"',

    # India — FSSAI is the national food regulator
    "india":         '"FSSAI" OR "ISO 22000" OR "HACCP"',

    # Brazil — MAPA is the agriculture/food ministry; SIF is the federal inspection
    "brazil":        '"MAPA certified" OR "SIF certified" OR "ISO 22000"',

    # Thailand — Thai FDA and GMP are the primary standards
    "thailand":      '"HACCP" OR "GMP" OR "Thai FDA"',

    # China
    "china":         '"HACCP" OR "GB standard" OR "ISO 22000"',

    # Europe
    "germany":       '"EU organic" OR "IFS" OR "BRC" OR "ISO 22000"',
    "france":        '"EU organic" OR "IFS" OR "BRC" OR "ISO 22000"',
    "netherlands":   '"IFS" OR "BRC" OR "ISO 22000" OR "HACCP"',

    # Australia / New Zealand
    "australia":     '"FSANZ" OR "HACCP" OR "ISO 22000"',
    "new zealand":   '"FSANZ" OR "HACCP" OR "ISO 22000"',

    # Vietnam
    "vietnam":       '"HACCP" OR "ISO 22000" OR "HALAL"',

    # Generic fallback — used for any country not listed above, or no country given
    "_default":      '"ISO 22000" OR "HACCP" OR "food grade"',
}


# ─────────────────────────────────────────────────────────────────────────────
# B2B SUPPLIER DIRECTORIES BY REGION
# Used to build a site-inclusion query instead of domain exclusions.
# Targeting known directories directly yields better-quality supplier pages
# than trying to block noise after the fact.
#
# Note on path-restricted entries (e.g. "kompass.com/brazil"):
#   Google's site: operator supports URL-path prefixes, so
#   site:kompass.com/brazil returns only kompass.com pages under /brazil/.
#   This narrows Kompass results to the relevant regional section.
# ─────────────────────────────────────────────────────────────────────────────
SUPPLIER_DIRECTORIES: dict[str, list[str]] = {
    # High-quality global B2B platforms — included in every search
    "GLOBAL": [
        "alibaba.com",
        "kompass.com",
        "tradekey.com",
        "globalsources.com",
        "ec21.com",
    ],

    # North America / USA / Mexico
    "NORTH_AMERICA": [
        "thomasnet.com",
        "mfgsupplier.com",
        "made-in-china.com",
    ],

    # Brazil — official trade promotion + B2B portals
    "BRAZIL": [
        "braziltradenet.gov.br",
        "apexbrasil.com.br",
        "anba.com.br",
        "kompass.com/brazil",
    ],

    # India — dominant domestic B2B marketplaces
    "INDIA": [
        "indiamart.com",
        "tradeindia.com",
        "exportersindia.com",
        "indianyellowpages.com",
    ],

    # Thailand — government trade portal + global platforms active in TH
    "THAILAND": [
        "thaitrade.com",
        "ditp.go.th",
        "globalsources.com",
    ],

    # Canada — manufacturer directories specific to Canadian market
    "CANADA": [
        "canadianmanufacturers.ca",
        "kompass.com/canada",
        "yellowpages.ca",
    ],
}
