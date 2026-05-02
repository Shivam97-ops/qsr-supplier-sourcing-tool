# supplier_search.py
# Handles web searches using SerpAPI (a Google Search API wrapper).
# SerpAPI returns structured JSON results instead of raw HTML.
#
# WHAT'S NEW IN THIS VERSION:
#   - Added exclusion terms that filter out academic papers, Wikipedia,
#     news articles, and government reports — common sources of noise.
#   - Added inclusion terms that bias results toward actual supplier/
#     manufacturer/distributor commercial websites.
#   - Canadian buyer context: when the user profile is in Canada, the
#     search is geo-biased toward Canadian and North American suppliers first.
#   - Increased result count to 10 (from 8) for more options.

import requests
from typing import Optional

from qsr_config import QSR_CATEGORIES
from logistics_config import COUNTRY_CERT_TERMS


# ─────────────────────────────────────────────────────────────────────────────
# EXCLUDED DOMAINS
# Post-processing filter applied after SerpAPI returns results.
# Grouped by category so it's clear why each domain is here.
# ─────────────────────────────────────────────────────────────────────────────
EXCLUDED_DOMAINS = (
    # Social media — no real B2B supplier presence
    "instagram.com", "facebook.com", "twitter.com", "x.com",
    "youtube.com", "reddit.com", "pinterest.com", "tiktok.com",
    # Academic / research databases
    "wikipedia.org", "ncbi.nlm.nih.gov", "pubmed.ncbi", "scholar.google",
    "researchgate.net", "academia.edu", "jstor.org", "springer.com",
    "sciencedirect.com", "tandfonline.com", "wiley.com", "slideshare.net",
    # News & media — articles about suppliers, not suppliers themselves
    "bbc.com", "bbc.co.uk", "cnn.com", "reuters.com", "bloomberg.com",
    "theguardian.com", "nytimes.com", "wsj.com", "forbes.com",
    # Q&A / community sites
    "quora.com", "stackexchange.com", "stackoverflow.com",
)

# Page titles that indicate an aggregator/blog, not an actual supplier.
_AGGREGATOR_TITLE_KEYWORDS = (
    "list of suppliers", "supplier directory", "top 10 suppliers",
    "best suppliers", "find suppliers", "suppliers list",
    "directory of", "list of manufacturers",
)

# ─────────────────────────────────────────────────────────────────────────────
# COUNTRY → GOOGLE GEOLOCATION CODE
# The SerpAPI 'gl' parameter biases results toward a specific country.
# Setting gl to the origin country returns locally-hosted supplier websites
# rather than generic global results.
# Full list: https://developers.google.com/custom-search/docs/json_api_reference
# ─────────────────────────────────────────────────────────────────────────────
_COUNTRY_TO_GL: dict[str, str] = {
    "canada":          "ca",
    "usa":             "us",
    "united states":   "us",
    "us":              "us",
    "america":         "us",
    "mexico":          "mx",
    "brazil":          "br",
    "india":           "in",
    "thailand":        "th",
    "china":           "cn",
    "japan":           "jp",
    "south korea":     "kr",
    "korea":           "kr",
    "vietnam":         "vn",
    "indonesia":       "id",
    "malaysia":        "my",
    "singapore":       "sg",
    "philippines":     "ph",
    "australia":       "au",
    "new zealand":     "nz",
    "germany":         "de",
    "france":          "fr",
    "italy":           "it",
    "spain":           "es",
    "netherlands":     "nl",
    "uk":              "uk",
    "united kingdom":  "uk",
    "argentina":       "ar",
    "chile":           "cl",
    "colombia":        "co",
    "peru":            "pe",
    "south africa":    "za",
    "nigeria":         "ng",
    "egypt":           "eg",
    "turkey":          "tr",
    "saudi arabia":    "sa",
    "uae":             "ae",
    "united arab emirates": "ae",
    "israel":          "il",
    "poland":          "pl",
    "sweden":          "se",
    "denmark":         "dk",
    "norway":          "no",
}


# Products where "manufacturer" is a better intent word than "exporter".
# Condiment/sauce suppliers typically describe themselves as manufacturers
# rather than exporters — using the wrong word misses their pages.
_MANUFACTURER_KEYWORDS = frozenset({
    "sauce", "seasoning", "spice", "paste", "condiment",
    "marinade", "dressing", "ketchup", "mustard", "mayonnaise",
    "relish", "vinegar", "syrup", "extract", "flavour", "flavor",
})


def _intent_word(product: str) -> str:
    """Return 'manufacturer' for condiment-type products, 'exporter' for everything else."""
    product_lower = product.lower()
    if any(kw in product_lower for kw in _MANUFACTURER_KEYWORDS):
        return "manufacturer"
    return "exporter"


def build_search_query(
    product: str,
    country: Optional[str],
    certifications: Optional[str],
    quantity: Optional[str],
    qsr_category: Optional[str] = None,
    user_profile: Optional[dict] = None,
) -> str:
    """
    Builds a clean plain-text query — no site: operators of any kind.
    Heavy filtering is handled by EXCLUDED_DOMAINS in post-processing.

    Format:
        "{product}" supplier exporter|manufacturer {country}
        wholesale bulk foodservice {cert_terms}

    Country is omitted when blank; gl= geo-parameter handles geo-ranking.

    Args:
        product:        Product to source, e.g. "chicken breast"
        country:        Optional origin country from the search form
        certifications: Optional user-supplied cert filter (overrides country default)
        quantity:       Optional quantity range (appended as "{qty} bulk")
        qsr_category:   Not used in query text; kept for signature compatibility
        user_profile:   Not used in query text; kept for signature compatibility

    Returns:
        A query string ready to send to SerpAPI.
    """
    parts = []

    # 1. Product — exact phrase match
    parts.append(f'"{product}"')

    # 2. Commercial intent: "exporter" for most products, "manufacturer" for sauces/spices
    parts.append(f"supplier {_intent_word(product)}")

    # 3. Origin country — omit entirely if blank
    if country:
        parts.append(country)

    # 4. Broad B2B context terms
    parts.append("wholesale bulk foodservice")

    # 5. Cert terms — country-specific, or user-supplied, or generic fallback
    if certifications:
        parts.append(certifications)
    else:
        country_key = (country or "").strip().lower()
        parts.append(COUNTRY_CERT_TERMS.get(country_key, COUNTRY_CERT_TERMS["_default"]))

    # 6. Optional quantity filter
    if quantity:
        parts.append(f"{quantity} bulk")

    return " ".join(parts)


def search_suppliers_serpapi(
    product: str,
    country: Optional[str] = None,
    certifications: Optional[str] = None,
    quantity: Optional[str] = None,
    api_key: str = "",
    num_results: int = 10,
    qsr_category: Optional[str] = None,
    user_profile: Optional[dict] = None,
) -> list[dict]:
    """
    SerpAPI fallback search — calls Google via SerpAPI.

    Renamed from search_suppliers() to make its role explicit. Invoked only
    when Claude web search is unavailable or returns too few results.

    Args:
        product:        Specific product to source (e.g., "iceberg lettuce")
        country:        Optional country of origin filter
        certifications: Optional certification filter
        quantity:       Optional quantity range
        api_key:        SerpAPI key
        num_results:    Number of search results (up to ~10 on free plans)
        qsr_category:   QSR category string
        user_profile:   Optional buyer profile dict

    Returns:
        List of raw supplier dicts: name, website, snippet, product, qsr_category
    """
    query = build_search_query(
        product, country, certifications, quantity, qsr_category, user_profile
    )
    # gl = Google geolocation code, derived from the ORIGIN COUNTRY (not buyer profile).
    # This biases Google toward supplier websites hosted in that country's market.
    # If no origin country specified, default to "us" (most neutral global index).
    country_key = (country or "").strip().lower()
    gl_setting  = _COUNTRY_TO_GL.get(country_key, "us")

    params = {
        "engine":  "google",
        "q":       query,
        "api_key": api_key,
        "num":     num_results,
        "hl":      "en",
        "gl":      gl_setting,
    }

    try:
        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        raise ConnectionError("SerpAPI request timed out. Check your internet connection.")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"SerpAPI returned an error: {e}. Check your API key.")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to SerpAPI: {e}")

    organic_results = data.get("organic_results", [])

    if not organic_results:
        return []

    suppliers = []
    for result in organic_results[:num_results]:
        url   = result.get("link", "")
        title = result.get("title", "").lower()

        # Drop known non-supplier domains (social media, academic, news, Q&A)
        if any(domain in url for domain in EXCLUDED_DOMAINS):
            continue

        # Drop aggregator/directory pages — these list suppliers but aren't suppliers
        if any(kw in title for kw in _AGGREGATOR_TITLE_KEYWORDS):
            continue

        supplier = {
            "name":          result.get("title", "Unknown"),
            "website":       url,
            "displayed_url": result.get("displayed_link", ""),
            "snippet":       result.get("snippet", "No description available."),
            "product":       product,
            "qsr_category":  qsr_category or "General",
        }
        suppliers.append(supplier)

    return suppliers


def search_suppliers(
    product: str,
    country: Optional[str] = None,
    certifications: Optional[str] = None,
    quantity: Optional[str] = None,
    api_key: str = "",           # Anthropic API key — drives Claude web search
    serpapi_key: str = "",       # SerpAPI key — optional fallback
    num_results: int = 10,
    qsr_category: Optional[str] = None,
    user_profile: Optional[dict] = None,
) -> tuple[list[dict], str]:
    """
    Claude-first supplier search with SerpAPI as optional fallback.

    How the fallback chain works:
      1. Call Claude web search (primary) — finds real suppliers with contact info
      2. If Claude returns ≥3 results → use Claude results        (method "claude")
      3. If Claude returns <3 or fails → call SerpAPI             (method "serpapi")
      4. If both return results → combine, deduplicating overlaps  (method "combined")
      5. If both fail → return empty list                          (method "none")

    SerpAPI is now optional — if no serpapi_key is provided, the tool still
    works using Claude alone. SerpAPI enhances local supplier discovery when
    Claude's web search returns thin results for niche products.

    Args:
        api_key:     Anthropic API key (required for Claude web search)
        serpapi_key: SerpAPI key (optional — enhances local supplier discovery)

    Returns:
        (suppliers_list, search_method)
        search_method is one of: "claude" | "serpapi" | "combined" | "none"
    """
    # Import here to avoid a module-level circular dependency:
    # supplier_search.py → ai_summarizer.py → qsr_config, logistics_config
    from ai_summarizer import search_suppliers_with_claude

    _MIN_CLAUDE = 3   # Minimum Claude results before considering SerpAPI supplement
    _TARGET     = 8   # Ideal total result count from web search

    claude_results:  list[dict] = []
    serpapi_results: list[dict] = []
    claude_ok    = False
    claude_error = ""
    serp_error   = ""

    # ── Step 1: Claude web search (primary) ──
    if api_key:
        try:
            claude_results = search_suppliers_with_claude(
                product=product,
                country=country,
                qsr_category=qsr_category or "General",
                user_profile=user_profile,
                api_key=api_key,
            )
            claude_ok = len(claude_results) >= _MIN_CLAUDE
        except Exception as _claude_exc:
            claude_error = f"{type(_claude_exc).__name__}: {_claude_exc}"
            print(f"[search_suppliers] Claude failed: {claude_error}")
            claude_ok = False

    # ── Step 2: SerpAPI fallback (only when Claude is thin or absent) ──
    if not claude_ok and serpapi_key:
        try:
            serpapi_results = search_suppliers_serpapi(
                product=product,
                country=country,
                certifications=certifications,
                quantity=quantity,
                api_key=serpapi_key,
                num_results=num_results,
                qsr_category=qsr_category,
                user_profile=user_profile,
            )
        except Exception as _serp_exc:
            serp_error = f"{type(_serp_exc).__name__}: {_serp_exc}"
            print(f"[search_suppliers] SerpAPI failed: {serp_error}")

    errors = {}
    if claude_error:
        errors["claude"] = claude_error
    if serp_error:
        errors["serpapi"] = serp_error

    # ── Step 3: Determine method and return ──
    has_claude  = len(claude_results) >= _MIN_CLAUDE
    has_serpapi = len(serpapi_results) > 0

    if has_claude and not has_serpapi:
        return claude_results[:_TARGET], "claude", errors

    if has_serpapi and not has_claude:
        return serpapi_results[:_TARGET], "serpapi", errors

    if has_claude and has_serpapi:
        claude_names   = [r["name"] for r in claude_results]
        serpapi_unique = [
            r for r in serpapi_results
            if not any(_names_overlap(r["name"], cn) for cn in claude_names)
        ]
        return (claude_results + serpapi_unique)[:_TARGET], "combined", errors

    return [], "none", errors


# ─────────────────────────────────────────────────────────────────────────────
# CURATED DATABASE INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────

def _extract_country_from_location(location: str) -> str:
    """Extract country from 'City, Province, Country' format → returns last part."""
    parts = [p.strip() for p in location.split(",")]
    return parts[-1] if parts else location


def _names_overlap(name1: str, name2: str) -> bool:
    """Returns True if two company names likely refer to the same company."""
    n1, n2 = name1.lower().strip(), name2.lower().strip()
    if n1 == n2 or n1 in n2 or n2 in n1:
        return True
    # If first significant word matches, treat as same company
    generic = {"the", "a", "an", "of", "for", "ltd", "inc", "corp", "co", "group"}
    words1 = [w for w in n1.split() if w not in generic and len(w) > 3]
    words2 = [w for w in n2.split() if w not in generic and len(w) > 3]
    if words1 and words2 and words1[0] == words2[0]:
        return True
    return False


def deduplicate_raw_results(curated: list[dict], web: list[dict]) -> list[dict]:
    """Remove from web any entries whose name closely matches a curated supplier."""
    curated_names = [s["name"] for s in curated]
    return [w for w in web if not any(_names_overlap(w["name"], c) for c in curated_names)]


def get_curated_raw_results(
    user_profile: dict,
    qsr_category: str,
    product: str,
    max_results: int = 5,
) -> list[dict]:
    """
    Fetches the top curated suppliers for the buyer's profile and converts them
    to the same raw dict format expected by batch_summarize().

    The curated supplier's notes, products, certifications, and export markets
    are packed into the 'snippet' field so Claude can analyse them normally.
    """
    from curated_suppliers import get_top_suppliers_for_profile

    buyer_location = user_profile.get("location", "Canada")
    # Pass product so irrelevant curated suppliers are filtered out
    curated = get_top_suppliers_for_profile(buyer_location, qsr_category, product)

    results = []
    for s in curated[:max_results]:
        snippet = (
            f"{s.get('notes', '')} "
            f"Key products: {', '.join(s.get('products', []))}. "
            f"Certifications: {', '.join(s.get('certifications', []))}. "
            f"Export markets: {', '.join(s.get('export_markets', []))}."
        )
        results.append({
            "name":            s["name"],
            "website":         s.get("website", ""),
            "displayed_url":   s.get("website", ""),
            "snippet":         snippet.strip(),
            "product":         product,
            "qsr_category":    qsr_category,
            "is_curated":      True,
            "curated_country": s.get("country", ""),
            "curated_certs":   s.get("certifications", []),
        })
    return results
