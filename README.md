# QSR Supplier Sourcing Tool

AI-powered supplier discovery, risk scoring, and landed cost analysis for food-service procurement teams.

---

## What it does

1. Set your **buyer profile** (company, location, preferred certifications) in the sidebar
2. Choose a **QSR product category** and type a product name (e.g. "chicken breast", "parboiled rice")
3. Optionally filter by **origin country** — the app geo-biases the search and applies country-appropriate food-safety certification terms
4. The app combines two sources:
   - **⭐ Curated Database** — 40 pre-vetted suppliers across Canada, USA, India, Brazil, and Thailand, ranked by relevance to your buyer location
   - **🌐 Web Search** — live SerpAPI search for additional suppliers, deduplicated against the curated list
5. **Claude AI** analyses every supplier and returns: score (0–100), supplier classification, risk intelligence (geopolitical / environmental / supplier-specific), logistics options (sea FCL/LCL, air, truck), and total landed cost breakdown
6. **Save** suppliers to a local SQLite database, rate them on a scorecard, and compare up to 4 side-by-side
7. **Generate a Sourcing Strategy** — AI-written primary/backup/volume-split recommendation

---

## Key Features

| Feature | Details |
|---|---|
| Supplier classification | Manufacturer / Distributor / Trader/Broker / Local Vendor |
| Risk scoring | 0–100 scale across geopolitical, environmental, and supplier-specific risk |
| Landed cost calculator | 7 components: FOB + freight + insurance + duty + CFIA + inland + inventory holding |
| CUSMA detection | Automatic 0% duty flag for Canada ↔ USA ↔ Mexico trade |
| Country cert terms | Auto-selects FSSAI (India), MAPA/SIF (Brazil), Thai FDA, CFIA/FDA (Canada/USA), etc. |
| Buyer profile | Location drives curated ranking, geo-bias, and AI analysis context |
| Sourcing strategy | AI-generated primary / backup supplier recommendation after each search |

---

## Setup — Local

### Step 1 — Get API Keys

**SerpAPI** (web search):
- Sign up at [serpapi.com](https://serpapi.com) — free plan includes 100 searches/month
- Copy your API key from the dashboard

**Anthropic API** (Claude AI):
- Sign up at [console.anthropic.com](https://console.anthropic.com)
- Create an API key under API Keys

### Step 2 — Install Python 3.11+

Download from [python.org](https://python.org). During installation, check **"Add Python to PATH"**.

### Step 3 — Install dependencies

```bash
cd supplier-sourcing-tool
python -m venv venv

# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 4 — Run

```bash
streamlit run app.py
```

Paste your API keys into the sidebar when the app opens. They are not stored on disk.

---

## Setup — Streamlit Cloud

1. Push this repo to GitHub (`.gitignore` already excludes secrets and the local database)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select your repo → `app.py`
3. Under **Settings → Secrets**, paste:

```toml
[api_keys]
SERPAPI_KEY   = "your_serpapi_key_here"
ANTHROPIC_KEY = "your_anthropic_key_here"
```

See `.streamlit/secrets.toml.example` for the exact format.

---

## Project Structure

```
supplier-sourcing-tool/
├── app.py                  # Streamlit UI — all three tabs (Search, Saved, Scorecards)
├── supplier_search.py      # SerpAPI integration — query builder, geo-params, dedup
├── ai_summarizer.py        # Claude API — scoring, risk, logistics, landed cost, strategy
├── database.py             # SQLite — save/load/delete suppliers and scorecards
├── curated_suppliers.py    # 40 pre-vetted suppliers (CA/US/IN/BR/TH) with helper functions
├── logistics_config.py     # Freight rates, tariff schedules, cert terms, FOB prices
├── qsr_config.py           # QSR category definitions and scoring config
├── requirements.txt        # Python dependencies
├── .gitignore              # Excludes secrets, db, profile, __pycache__
└── .streamlit/
    └── secrets.toml.example  # API key format for Streamlit Cloud
```

---

## Tips for Better Results

- **Be specific**: "corrugated cardboard food boxes" beats "boxes"
- **Set your buyer location**: the app ranks curated suppliers by proximity (same country first, then CUSMA partners, then exporters to your region)
- **Use the country field**: entering "Brazil" for coffee sets `gl=br` and adds Brazilian food-safety cert terms to the query
- **Condiment products**: entering "soy sauce" or "ketchup" automatically switches the query intent from "exporter" to "manufacturer"

---

## Common Issues

| Problem | Solution |
|---|---|
| "SerpAPI request failed" | Check your SerpAPI key; verify free quota hasn't run out |
| "AI analysis failed" | Check your Anthropic API key and account credits |
| App won't start | Activate venv and run `pip install -r requirements.txt` |
| All suppliers score 0 | Rare Claude parse failure — retry the search |
| Curated section shows wrong country | Check your profile Location field: use "City, Country" format, e.g. "Gujarat, India" |
