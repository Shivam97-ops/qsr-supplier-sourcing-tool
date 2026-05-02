# curated_suppliers.py
# A curated reference database of major, known QSR-relevant suppliers
# organised by region: Canada, USA, India, Brazil, and Thailand.
#
# WHY THIS FILE EXISTS:
#   The AI search (SerpAPI + Claude) discovers new suppliers, but can miss
#   large, well-known players whose websites are not optimised for our exact
#   search query. This file gives you a reliable, pre-vetted list of real
#   companies you can always reference, compare, or import into the app.
#
# HOW IT IS STRUCTURED:
#   SUPPLIERS is one big Python list. Each item in the list is a dictionary
#   (a set of key-value pairs) that describes one supplier.
#
#   Every supplier has the same keys — this is called a "consistent schema."
#   A consistent schema makes filtering, sorting, and looping much easier
#   because you never have to wonder "does this supplier have a website key?"
#
# HOW TO READ A PYTHON DICTIONARY:
#   {
#       "name":       "Company Name",   <- string  (text in quotes)
#       "founded":    1984,             <- integer (whole number, no quotes)
#       "active":     True,             <- boolean (True or False, capital T/F)
#       "products":   ["rice", "oil"],  <- list    (multiple items in [])
#   }
#
# KEY CONCEPT — CUSMA:
#   The Canada-United States-Mexico Agreement gives 0% import duty on
#   most food goods traded between Canada, the USA, and Mexico.
#   cusma_eligible = True means the buyer in Ontario pays NO import tariff.
#   All other countries face ~12% standard duty on food imports to Canada.


# ─────────────────────────────────────────────────────────────────────────────
# SUPPLIER TYPE REFERENCE
# ─────────────────────────────────────────────────────────────────────────────
#   Manufacturer  — makes or grows the product in their own facility
#   Distributor   — buys in bulk from manufacturers and resells to buyers
#   Trader        — acts as a broker/agent; does not hold inventory


# ─────────────────────────────────────────────────────────────────────────────
# THE MAIN DATABASE
# ─────────────────────────────────────────────────────────────────────────────

SUPPLIERS: list[dict] = [

    # ══════════════════════════════════════════════════════════════════════════
    # CANADA — PROTEINS
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Cargill Canada",
        "country":        "Canada",
        "region":         "Alberta (HQ); also Ontario, Quebec",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Beef patties", "Ground beef", "Beef cuts", "Pork products"],
        "certifications": ["HACCP", "CFIA approved", "ISO 22000", "Halal"],
        "website":        "https://www.cargill.com/en/canada",
        "cusma_eligible": True,
        "export_markets": ["USA", "Japan", "South Korea", "China", "Mexico"],
        "notes": (
            "One of the largest beef processors in Canada. Major packing plants in "
            "High River AB and Guelph ON. Supplies McDonald's and other major QSR chains "
            "across North America. Part of the global Cargill group (Minneapolis MN)."
        ),
    },

    {
        "name":           "Maple Leaf Foods",
        "country":        "Canada",
        "region":         "Ontario (HQ: Toronto); plants in MB, SK, ON, BC",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Pork", "Bacon", "Sausages", "Prepared meats", "Chicken"],
        "certifications": ["HACCP", "CFIA approved", "ISO 22000", "FSSC 22000", "Halal"],
        "website":        "https://www.mapleleaffoods.com",
        "cusma_eligible": True,
        "export_markets": ["USA", "Japan", "China", "Australia", "UK"],
        "notes": (
            "Canada's largest pork and prepared meat processor. Publicly traded on TSX. "
            "Declared carbon-neutral in 2019. Supplies QSR and retail nationally."
        ),
    },

    {
        "name":           "Olymel L.P.",
        "country":        "Canada",
        "region":         "Quebec (HQ: Boucherville); plants in QC, AB, ON, SK",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Pork", "Chicken", "Turkey", "Ham", "Deli meats", "Sausages"],
        "certifications": ["HACCP", "CFIA approved", "ISO 22000", "Halal", "Kosher"],
        "website":        "https://www.olymel.com",
        "cusma_eligible": True,
        "export_markets": ["USA", "Japan", "China", "Australia", "EU"],
        "notes": (
            "Quebec-based cooperative and one of Canada's top pork and poultry processors. "
            "Significant export volume to Asia and the USA. Cooperative ownership "
            "structure — owned by La Coop federee."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # USA — PROTEINS
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Tyson Foods USA",
        "country":        "USA",
        "region":         "Arkansas (HQ: Springdale); plants in 20+ US states",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Chicken patties", "Chicken nuggets", "Beef patties", "Pork", "IQF chicken"],
        "certifications": ["HACCP", "USDA approved", "FDA registered", "ISO 22000", "Halal"],
        "website":        "https://www.tysonfoods.com",
        "cusma_eligible": True,
        "export_markets": ["Canada", "Japan", "China", "Mexico", "EU", "South Korea", "Middle East"],
        "notes": (
            "World's largest chicken processor. Supplies McDonald's, KFC, Chick-fil-A, "
            "and hundreds of QSR chains. CUSMA = 0% import duty to Canada. "
            "Very high volume with consistent quality. Cross-border truck to Ontario."
        ),
    },

    {
        "name":           "JBS USA (JBS Food Canada)",
        "country":        "USA",
        "region":         "Colorado (US HQ: Greeley); Canadian plant in Brooks, AB",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Beef patties", "Ground beef", "Beef cuts", "Pork"],
        "certifications": ["HACCP", "USDA approved", "CFIA approved", "Halal", "ISO 22000"],
        "website":        "https://www.jbssa.com",
        "cusma_eligible": True,
        "export_markets": ["Canada", "Japan", "China", "EU", "Middle East", "Australia"],
        "notes": (
            "World's largest beef processor overall. JBS Food Canada operates the largest "
            "single-site beef plant in Canada (Brooks AB). Canadian plant production "
            "qualifies as Canadian origin for CUSMA purposes."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # CANADA / USA — PRODUCE & DISTRIBUTION
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Sysco Canada",
        "country":        "Canada",
        "region":         "Ontario (HQ: Mississauga); DCs nationwide",
        "supplier_type":  "Distributor",
        "categories":     ["🥬 Produce", "🧂 Condiments & Sauces", "🌾 Dry Goods", "❄️ Frozen & Cold Chain"],
        "products":       ["Fresh produce", "Sauces", "Dry ingredients", "Frozen foods", "Dairy"],
        "certifications": ["HACCP", "CFIA registered", "ISO 9001", "SQF"],
        "website":        "https://www.sysco.ca",
        "cusma_eligible": True,
        "export_markets": ["Canada"],
        "notes": (
            "Canada's largest broad-line food service distributor. Not a manufacturer — "
            "Sysco sources from hundreds of producers and resells to QSR chains. "
            "Excellent for buyers who want one supplier for multiple categories."
        ),
    },

    {
        "name":           "Gordon Food Service (GFS) Canada",
        "country":        "Canada",
        "region":         "Ontario (HQ: Milton); DCs in ON, QC, AB, BC",
        "supplier_type":  "Distributor",
        "categories":     ["🥬 Produce", "🧂 Condiments & Sauces", "🌾 Dry Goods", "❄️ Frozen & Cold Chain"],
        "products":       ["Fresh produce", "Frozen proteins", "Sauces", "Dry goods", "Packaging"],
        "certifications": ["HACCP", "CFIA registered", "SQF"],
        "website":        "https://www.gfs.ca",
        "cusma_eligible": True,
        "export_markets": ["Canada"],
        "notes": (
            "Second-largest food service distributor in Canada. Family-owned US company "
            "with major Canadian operations. Very QSR-friendly with dedicated account "
            "managers for chain restaurant accounts."
        ),
    },

    {
        "name":           "McCain Foods Limited",
        "country":        "Canada",
        "region":         "New Brunswick (HQ: Florenceville-Bristol); 12 plants in Canada",
        "supplier_type":  "Manufacturer",
        "categories":     ["🥬 Produce", "❄️ Frozen & Cold Chain"],
        "products":       ["Frozen french fries", "Hash browns", "Potato wedges", "Frozen vegetables"],
        "certifications": ["HACCP", "CFIA approved", "ISO 22000", "FSSC 22000", "BRC"],
        "website":        "https://www.mccain.com",
        "cusma_eligible": True,
        "export_markets": ["USA", "UK", "Australia", "Japan", "France", "Germany", "China"],
        "notes": (
            "World's largest manufacturer of frozen french fries — supplies McDonald's globally. "
            "Canadian-owned family company. 50+ plants worldwide. If sourcing frozen fries, "
            "McCain is typically the primary benchmark supplier."
        ),
    },

    {
        "name":           "Fresh Del Monte Produce",
        "country":        "USA",
        "region":         "Florida (HQ: Coral Gables); Canadian operations in ON",
        "supplier_type":  "Distributor",
        "categories":     ["🥬 Produce"],
        "products":       ["Bananas", "Pineapples", "Lettuce", "Tomatoes", "Cut fruit", "Salad mixes"],
        "certifications": ["GlobalG.A.P", "HACCP", "FDA registered", "USDA GAP"],
        "website":        "https://www.freshdelmonte.com",
        "cusma_eligible": True,
        "export_markets": ["Canada", "Europe", "Middle East", "Asia"],
        "notes": (
            "One of the world's largest fresh fruit and vegetable companies. Sources from "
            "Central/South America and Africa. Canadian operations serve QSR and retail "
            "in Ontario and Quebec. Note: fresh produce has seasonal supply risk."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # CANADA — DRY GOODS
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Rogers Sugar / Lantic Inc.",
        "country":        "Canada",
        "region":         "Quebec (HQ: Montreal); refineries in AB and QC",
        "supplier_type":  "Manufacturer",
        "categories":     ["🌾 Dry Goods"],
        "products":       ["Refined cane sugar", "Brown sugar", "Icing sugar", "Liquid sugar"],
        "certifications": ["HACCP", "CFIA approved", "Kosher", "Halal", "ISO 22000"],
        "website":        "https://www.lantic.ca",
        "cusma_eligible": True,
        "export_markets": ["USA"],
        "notes": (
            "Canada's largest sugar refiner. Publicly traded (TSX: RSI). Lantic brand "
            "serves food service; Rogers brand serves retail. Domestic production means "
            "no import duties and shortest possible lead times for Canadian QSR buyers."
        ),
    },

    {
        "name":           "Richardson International Limited",
        "country":        "Canada",
        "region":         "Manitoba (HQ: Winnipeg); operations across Western Canada",
        "supplier_type":  "Manufacturer",
        "categories":     ["🌾 Dry Goods"],
        "products":       ["Canola oil", "Wheat flour", "Canola meal", "Oats", "Flaxseed"],
        "certifications": ["HACCP", "CFIA approved", "ISO 22000", "Non-GMO", "Kosher"],
        "website":        "https://www.richardson.ca",
        "cusma_eligible": True,
        "export_markets": ["China", "Japan", "India", "EU", "USA", "Mexico"],
        "notes": (
            "Canada's largest agribusiness and one of the largest grain handlers in the world. "
            "Major producer of Canadian canola oil — a staple QSR frying oil. "
            "Privately held by the Richardson family, Winnipeg."
        ),
    },

    {
        "name":           "Bunge Canada",
        "country":        "Canada",
        "region":         "Ontario (HQ: Hamilton); crush plants in MB, SK, AB",
        "supplier_type":  "Manufacturer",
        "categories":     ["🌾 Dry Goods"],
        "products":       ["Canola oil", "Soybean oil", "Shortenings", "Margarine"],
        "certifications": ["HACCP", "CFIA approved", "ISO 22000", "FSSC 22000", "Kosher", "Halal"],
        "website":        "https://www.bungecanada.com",
        "cusma_eligible": True,
        "export_markets": ["USA", "China", "Japan", "EU", "Brazil", "Mexico"],
        "notes": (
            "Largest canola crusher in Canada. Part of Bunge Limited (NYSE: BG), a global "
            "agribusiness. Supplies cooking oils to QSR chains, food manufacturers, and "
            "bakeries. Canadian crush means CUSMA eligibility for oil products."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # CANADA / USA — PACKAGING
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Cascades Inc.",
        "country":        "Canada",
        "region":         "Quebec (HQ: Kingsey Falls); plants across Canada and USA",
        "supplier_type":  "Manufacturer",
        "categories":     ["📦 Packaging"],
        "products":       ["Paper bags", "Tissue products", "Cardboard boxes", "Cups", "Foodservice packaging"],
        "certifications": ["FSC certified", "FDA food contact", "ISO 9001", "ISO 14001", "BRC"],
        "website":        "https://www.cascades.com",
        "cusma_eligible": True,
        "export_markets": ["USA", "Europe"],
        "notes": (
            "One of Canada's largest packaging companies. Publicly traded (TSX: CAS). "
            "Known for sustainable packaging with 80%+ recycled fibre content. "
            "Key QSR clients include Tim Hortons and McDonald's Canada."
        ),
    },

    {
        "name":           "Novatek International",
        "country":        "Canada",
        "region":         "Ontario (HQ: Mississauga)",
        "supplier_type":  "Manufacturer",
        "categories":     ["📦 Packaging"],
        "products":       ["Plastic food containers", "Clamshells", "Cups", "Lids", "Food wrap"],
        "certifications": ["FDA food contact", "ISO 9001", "BRC"],
        "website":        "https://www.novatek.ca",
        "cusma_eligible": True,
        "export_markets": ["Canada", "USA"],
        "notes": (
            "Ontario-based manufacturer of plastic foodservice packaging. Serves QSR, "
            "fast casual, and grocery chains across Canada. Shorter lead times than "
            "offshore alternatives. Custom printing available."
        ),
    },

    {
        "name":           "Graphic Packaging International (Canada)",
        "country":        "USA",
        "region":         "Georgia (US HQ: Atlanta); Canadian operations in ON, QC",
        "supplier_type":  "Manufacturer",
        "categories":     ["📦 Packaging"],
        "products":       ["Paperboard cartons", "Folding cartons", "Quick-serve packaging", "Cups"],
        "certifications": ["FDA food contact", "FSC certified", "SFI", "ISO 9001", "BRC"],
        "website":        "https://www.graphicpkg.com",
        "cusma_eligible": True,
        "export_markets": ["Canada", "Europe", "Asia", "Mexico"],
        "notes": (
            "Global leader in paperboard packaging (NYSE: GPK). Supplies Tim Hortons, "
            "McDonald's Canada, and Starbucks Canada. High minimum order quantities — "
            "best suited for high-volume QSR chains."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # CANADA / USA — CONDIMENTS & SAUCES
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "French's Food Company (McCormick Canada)",
        "country":        "Canada",
        "region":         "Ontario (Leamington plant — uses Ontario-grown tomatoes)",
        "supplier_type":  "Manufacturer",
        "categories":     ["🧂 Condiments & Sauces"],
        "products":       ["Ketchup", "Mustard", "Worcestershire sauce", "Hot sauce"],
        "certifications": ["HACCP", "CFIA approved", "ISO 22000"],
        "website":        "https://www.frenchs.com",
        "cusma_eligible": True,
        "export_markets": ["Canada", "USA"],
        "notes": (
            "French's ketchup is made in Leamington ON using 100% Canadian-grown tomatoes — "
            "a major selling point for Canadian QSR buyers who want local sourcing. "
            "Now owned by McCormick and Company."
        ),
    },

    {
        "name":           "Kraft Heinz Canada",
        "country":        "Canada",
        "region":         "Ontario (HQ: Don Mills); sourcing from US and Canada",
        "supplier_type":  "Manufacturer",
        "categories":     ["🧂 Condiments & Sauces"],
        "products":       ["Ketchup", "Mayonnaise", "Mustard", "BBQ sauce", "Ranch dressing"],
        "certifications": ["HACCP", "CFIA approved", "FDA registered", "ISO 22000", "FSSC 22000"],
        "website":        "https://www.kraftheinzcompany.com",
        "cusma_eligible": True,
        "export_markets": ["USA", "EU", "Australia", "China", "Middle East"],
        "notes": (
            "One of the world's largest food companies. Dominant QSR condiment supplier. "
            "Supplies ketchup and sauces to McDonald's and Burger King globally. "
            "High volume, very consistent quality."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # CANADA — FROZEN & COLD CHAIN
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Cavendish Farms",
        "country":        "Canada",
        "region":         "PEI (HQ: Charlottetown); plants in PEI, NB, AB",
        "supplier_type":  "Manufacturer",
        "categories":     ["❄️ Frozen & Cold Chain", "🥬 Produce"],
        "products":       ["Frozen french fries", "Potato wedges", "Hash browns", "Onion rings"],
        "certifications": ["HACCP", "CFIA approved", "ISO 22000", "BRC", "SQF"],
        "website":        "https://www.cavendishfarms.com",
        "cusma_eligible": True,
        "export_markets": ["USA", "Japan", "China", "UK"],
        "notes": (
            "Canadian-owned frozen potato processor (Irving family group). Direct "
            "competitor to McCain Foods — both are major frozen fry suppliers for QSR. "
            "Uses PEI and New Brunswick potatoes."
        ),
    },

    {
        "name":           "Conagra Brands Canada",
        "country":        "Canada",
        "region":         "Ontario (HQ: Mississauga); multiple Canadian plants",
        "supplier_type":  "Manufacturer",
        "categories":     ["❄️ Frozen & Cold Chain", "🧂 Condiments & Sauces"],
        "products":       ["Frozen meals", "Frozen proteins", "Tomato products", "Sauces"],
        "certifications": ["HACCP", "CFIA approved", "FDA registered", "ISO 22000", "SQF"],
        "website":        "https://www.conagrabrands.com",
        "cusma_eligible": True,
        "export_markets": ["USA", "Mexico"],
        "notes": (
            "Major North American packaged food company with strong Canadian food service "
            "presence. Supplies frozen and shelf-stable products to QSR and institutional "
            "food service. Very high volume capacity."
        ),
    },


    # ══════════════════════════════════════════════════════════════════════════
    # INDIA — PROTEINS
    # Tariff note: Indian suppliers face ~12% standard Canadian import duty.
    # India is NOT a CUSMA partner. Freight from India to Ontario: ~25-35 days
    # by sea via Vancouver or Halifax.
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Suguna Foods",
        "country":        "India",
        "region":         "Tamil Nadu (HQ: Coimbatore); operations across 18 states",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Fresh chicken", "Frozen chicken cuts", "Processed chicken", "Chicken nuggets"],
        "certifications": ["HACCP", "FSSAI", "ISO 22000", "Halal", "BRC"],
        "website":        "https://www.sugunafoods.com",
        "cusma_eligible": False,
        "export_markets": ["Middle East", "Malaysia", "Singapore", "UK"],
        "notes": (
            "India's largest integrated poultry company — processes over 3 million birds/day. "
            "Major QSR supplier to KFC and McDonald's India. HACCP-certified processing plants. "
            "Strong Halal certification for Middle East export markets. Growing export capacity "
            "but primarily serves the Indian domestic and regional Asian markets."
        ),
    },

    {
        "name":           "Venky's India Ltd.",
        "country":        "India",
        "region":         "Maharashtra (HQ: Pune); processing plants across India",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Whole chicken", "Chicken cuts", "Ready-to-cook chicken", "Egg products"],
        "certifications": ["ISO 22000", "HACCP", "FSSAI", "Halal", "EU approved"],
        "website":        "https://www.venkys.com",
        "cusma_eligible": False,
        "export_markets": ["Middle East", "EU", "Japan", "Singapore", "Malaysia"],
        "notes": (
            "Vertically integrated poultry conglomerate — controls the entire chain from "
            "feed to processing. Publicly traded on Bombay Stock Exchange. "
            "EU-approved export status means their standards meet stringent European "
            "requirements, which is a strong quality signal for Canadian buyers."
        ),
    },

    {
        "name":           "ITC Agribusiness Division",
        "country":        "India",
        "region":         "West Bengal (HQ: Kolkata); sourcing across multiple Indian states",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins", "🌾 Dry Goods", "🧂 Condiments & Sauces"],
        "products":       ["Wheat flour", "Spices", "Condiment bases", "Ready meals", "Frozen snacks"],
        "certifications": ["HACCP", "ISO 22000", "FSSC 22000", "FSSAI", "Halal"],
        "website":        "https://www.itcportal.com/businesses/agri-business.aspx",
        "cusma_eligible": False,
        "export_markets": ["USA", "EU", "Middle East", "Australia", "Japan"],
        "notes": (
            "Diversified Indian conglomerate with a large agribusiness and food division. "
            "Operates the e-Choupal digital agri-sourcing network across 35,000 villages. "
            "Strong QSR food service supply presence in India. Exports branded food products "
            "globally under the Kitchens of India and Aashirvaad brands."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # INDIA — PRODUCE
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "FieldFresh Foods Pvt. Ltd.",
        "country":        "India",
        "region":         "Haryana (HQ: Gurgaon); farming operations in Punjab, Haryana, Maharashtra",
        "supplier_type":  "Manufacturer",
        "categories":     ["🥬 Produce"],
        "products":       ["Baby corn", "Snow peas", "Asparagus", "Bell peppers", "Cut vegetables", "Salad mixes"],
        "certifications": ["GlobalG.A.P", "ISO 22000", "HACCP", "FSSAI", "BRC"],
        "website":        "https://www.fieldfreshfoods.com",
        "cusma_eligible": False,
        "export_markets": ["EU", "UK", "Middle East", "Japan", "Southeast Asia"],
        "notes": (
            "Joint venture between the Bharti Group and Del Monte Pacific. Produces and "
            "exports fresh and processed vegetables specifically for food service and QSR. "
            "GlobalG.A.P certified farms — the international standard for farm food safety. "
            "EU export approval means their produce meets some of the strictest food safety "
            "standards in the world."
        ),
    },

    {
        "name":           "Freshtrop Fruits Ltd.",
        "country":        "India",
        "region":         "Maharashtra (HQ: Nashik); orchards and packing in Nashik region",
        "supplier_type":  "Manufacturer",
        "categories":     ["🥬 Produce"],
        "products":       ["Grapes", "Pomegranates", "Bananas", "Mangoes", "Onions", "Fresh vegetables"],
        "certifications": ["GlobalG.A.P", "HACCP", "FSSAI", "EurepGAP", "FDA registered"],
        "website":        "https://www.freshtrop.com",
        "cusma_eligible": False,
        "export_markets": ["EU", "UK", "Russia", "Middle East", "Canada", "USA"],
        "notes": (
            "One of India's most experienced fresh produce exporters. Nashik region is "
            "India's premier grape and onion growing area. Freshtrop has shipped directly "
            "to Canada and the USA, making them a viable option for a QSR buyer in Ontario. "
            "Seasonal product availability — plan sourcing windows in advance."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # INDIA — DRY GOODS
    # Note: India is the world's largest basmati rice exporter.
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "KRBL Limited",
        "country":        "India",
        "region":         "Delhi (HQ); milling plants in UP, Punjab, Haryana",
        "supplier_type":  "Manufacturer",
        "categories":     ["🌾 Dry Goods"],
        "products":       ["Basmati rice", "Brown rice", "Steam rice", "Organic rice"],
        "certifications": ["ISO 22000", "HACCP", "Kosher", "Halal", "FSSAI", "Non-GMO"],
        "website":        "https://www.krbl.in",
        "cusma_eligible": False,
        "export_markets": ["Middle East", "USA", "Canada", "Europe", "Australia", "UK", "Japan"],
        "notes": (
            "India's largest rice exporter and maker of the India Gate brand. Publicly traded "
            "on NSE. KRBL ships to Canada regularly — Canada has a significant South Asian "
            "diaspora that demands basmati rice at QSR and grocery scale. "
            "Very strong food safety certifications including Kosher and Halal."
        ),
    },

    {
        "name":           "LT Foods Limited",
        "country":        "India",
        "region":         "Haryana (HQ: Gurgaon); milling and processing across Punjab, Haryana",
        "supplier_type":  "Manufacturer",
        "categories":     ["🌾 Dry Goods"],
        "products":       ["Basmati rice (Daawat brand)", "Organic rice", "Ready-to-cook rice"],
        "certifications": ["FSSC 22000", "ISO 22000", "HACCP", "Organic", "Halal", "BRC"],
        "website":        "https://www.ltfoods.com",
        "cusma_eligible": False,
        "export_markets": ["USA", "Canada", "Europe", "UK", "Australia", "Middle East"],
        "notes": (
            "Maker of the Daawat brand — one of the best-known basmati rice brands in "
            "Canada and the USA. FSSC 22000 certified (one of the highest food safety "
            "standards globally). Strong distributor network in Canadian cities. "
            "Publicly traded on BSE and NSE."
        ),
    },

    {
        "name":           "Kohinoor Foods Ltd.",
        "country":        "India",
        "region":         "Delhi (HQ: New Delhi); sourcing and milling in Punjab, Haryana",
        "supplier_type":  "Manufacturer",
        "categories":     ["🌾 Dry Goods"],
        "products":       ["Premium basmati rice", "Ready meals", "Spices", "Instant foods"],
        "certifications": ["ISO 22000", "HACCP", "Halal", "Kosher", "BRC"],
        "website":        "https://www.kohinoorfoods.in",
        "cusma_eligible": False,
        "export_markets": ["USA", "Canada", "UK", "EU", "Middle East", "Australia", "Africa", "Japan"],
        "notes": (
            "Exports to 60+ countries, making Kohinoor one of India's most globally "
            "distributed rice brands. Publicly traded. Strong brand recognition in "
            "the Canadian South Asian community. Both Halal and Kosher certified "
            "which broadens their addressable QSR market."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # INDIA — CONDIMENTS & SAUCES
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Cremica Food Industries Ltd.",
        "country":        "India",
        "region":         "Himachal Pradesh / Punjab (HQ: Una, HP); plants in HP and Rajasthan",
        "supplier_type":  "Manufacturer",
        "categories":     ["🧂 Condiments & Sauces", "🌾 Dry Goods"],
        "products":       ["Ketchup", "Mayonnaise", "Mustard", "BBQ sauces", "Salad dressings", "Burger buns"],
        "certifications": ["HACCP", "ISO 22000", "FSSC 22000", "FSSAI", "Halal"],
        "website":        "https://www.cremica.in",
        "cusma_eligible": False,
        "export_markets": ["Middle East", "Southeast Asia", "UK"],
        "notes": (
            "India's leading QSR sauce and condiment manufacturer. Direct supplier to "
            "McDonald's India, Subway India, KFC India, and Domino's India — arguably the "
            "strongest QSR reference list of any Indian food company. "
            "Also manufactures burger buns and bakery items for QSR chains. "
            "An excellent option for any QSR buyer sourcing Indian-market condiments."
        ),
    },

    {
        "name":           "Hindustan Unilever Food Solutions",
        "country":        "India",
        "region":         "Maharashtra (HQ: Mumbai); manufacturing across India",
        "supplier_type":  "Manufacturer",
        "categories":     ["🧂 Condiments & Sauces", "🌾 Dry Goods"],
        "products":       ["Knorr soups", "Sauces", "Seasonings", "Stock", "Mayonnaise", "Dressings"],
        "certifications": ["ISO 22000", "HACCP", "FSSAI", "FSSC 22000", "Halal"],
        "website":        "https://www.unileverfoodsolutions.co.in",
        "cusma_eligible": False,
        "export_markets": ["Global (via Unilever network)", "Middle East", "Southeast Asia"],
        "notes": (
            "Food service division of Hindustan Unilever Limited — India's largest FMCG company "
            "and a subsidiary of the global Unilever group. Carries the Knorr brand, which is "
            "sold in every country Unilever operates in. For a Canadian buyer, Unilever's "
            "global infrastructure provides very high quality consistency and food safety standards."
        ),
    },


    # ══════════════════════════════════════════════════════════════════════════
    # BRAZIL — PROTEINS
    # Tariff note: Brazilian suppliers face ~12% Canadian import duty (not CUSMA).
    # Sea freight from Brazil to Ontario: ~20-30 days via Montreal.
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "JBS S.A. (Brazil)",
        "country":        "Brazil",
        "region":         "Sao Paulo (HQ); processing plants across all Brazilian states",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Beef", "Pork", "Chicken", "Lamb", "Processed meats", "Ready meals"],
        "certifications": ["SIF (MAPA Brazil)", "HACCP", "ISO 22000", "Halal", "FSSC 22000", "BRC"],
        "website":        "https://www.jbs.com.br",
        "cusma_eligible": False,
        "export_markets": ["USA", "EU", "China", "Japan", "Canada", "Middle East", "Australia"],
        "notes": (
            "World's largest meat processor by revenue. Parent company of JBS USA and "
            "JBS Food Canada. SIF certification (Servico de Inspecao Federal) is the "
            "Brazilian federal inspection standard required for export. Supplies "
            "McDonald's, Burger King, and most major QSR chains globally. "
            "Note: JBS Brazil and JBS USA are the same corporate group."
        ),
    },

    {
        "name":           "Marfrig Global Foods",
        "country":        "Brazil",
        "region":         "Sao Paulo (HQ); major plants in RS, MT, MS, MG states",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins"],
        "products":       ["Beef patties", "Ground beef", "Beef cuts", "Processed beef"],
        "certifications": ["SIF (MAPA Brazil)", "HACCP", "ISO 22000", "Halal", "Kosher", "BRC"],
        "website":        "https://www.marfrig.com.br",
        "cusma_eligible": False,
        "export_markets": ["USA", "EU", "China", "Japan", "Canada", "Middle East"],
        "notes": (
            "World's second-largest beef processor. Key global supplier to McDonald's "
            "for beef patties — McDonald's holds a strategic equity stake in Marfrig. "
            "Publicly traded on B3 (Brazilian stock exchange). Very strong food safety "
            "track record with strict SIF and ISO 22000 compliance."
        ),
    },

    {
        "name":           "BRF S.A. (Brasil Foods)",
        "country":        "Brazil",
        "region":         "Sao Paulo (HQ); plants across Brazil, Thailand, UAE, Turkey",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins", "❄️ Frozen & Cold Chain"],
        "products":       ["Frozen chicken", "Turkey", "Pork", "Sausages", "Processed meats", "Ready meals"],
        "certifications": ["SIF (MAPA Brazil)", "BRC", "ISO 22000", "HACCP", "Halal", "FSSC 22000"],
        "website":        "https://www.brf-global.com",
        "cusma_eligible": False,
        "export_markets": ["Middle East", "EU", "Japan", "China", "USA", "Canada", "Asia"],
        "notes": (
            "One of the world's largest food companies. Sells under the Sadia and Perdigao "
            "brands — both are well-known in Brazilian communities in Canada. "
            "Exports to 150+ countries. Publicy traded on B3 and NYSE. "
            "Has processing plants outside Brazil (Thailand, Turkey, UAE) which can "
            "sometimes provide shorter lead times depending on product."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # BRAZIL — PRODUCE
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Dole Brazil",
        "country":        "Brazil",
        "region":         "Sao Paulo (HQ); sourcing from SP, PR, BA, MG states",
        "supplier_type":  "Distributor",
        "categories":     ["🥬 Produce"],
        "products":       ["Bananas", "Pineapples", "Citrus", "Tropical fruits", "Frozen fruit"],
        "certifications": ["GlobalG.A.P", "FDA registered", "ISO 22000", "HACCP"],
        "website":        "https://www.dole.com",
        "cusma_eligible": False,
        "export_markets": ["USA", "Canada", "EU", "Middle East", "Japan"],
        "notes": (
            "Brazilian operations of Dole Food Company — the world's largest producer "
            "and marketer of fresh fruits and vegetables. Brazil is a major global "
            "source for tropical fruits. Dole's brand recognition provides strong "
            "quality assurance for QSR buyers."
        ),
    },

    {
        "name":           "Bonduelle Brazil",
        "country":        "Brazil",
        "region":         "Parana (HQ: Curitiba); plants in PR and RS states",
        "supplier_type":  "Manufacturer",
        "categories":     ["🥬 Produce", "❄️ Frozen & Cold Chain"],
        "products":       ["Canned corn", "Canned peas", "Frozen vegetables", "Canned beans", "Ready salads"],
        "certifications": ["ISO 22000", "BRC", "IFS", "HACCP", "FSSAI equivalent"],
        "website":        "https://www.bonduelle.com.br",
        "cusma_eligible": False,
        "export_markets": ["South America", "USA", "Canada", "EU"],
        "notes": (
            "Brazilian subsidiary of Bonduelle Group — the world's largest canned and "
            "frozen vegetable company (headquartered in France). "
            "ISO 22000 and BRC certifications meet Canadian CFIA requirements. "
            "Products like canned corn and peas are staple QSR ingredients."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # BRAZIL — DRY GOODS
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Cargill Brazil (Cargill Agricola S.A.)",
        "country":        "Brazil",
        "region":         "Sao Paulo (HQ); processing plants across MT, GO, PR, MG states",
        "supplier_type":  "Manufacturer",
        "categories":     ["🌾 Dry Goods", "🧂 Condiments & Sauces"],
        "products":       ["Corn starch", "Soybean oil", "Sunflower oil", "Glucose syrup", "Starches"],
        "certifications": ["HACCP", "ISO 22000", "FSSC 22000", "Halal", "Kosher"],
        "website":        "https://www.cargill.com.br",
        "cusma_eligible": False,
        "export_markets": ["USA", "Canada", "EU", "China", "Japan", "Middle East"],
        "notes": (
            "Brazilian operations of Cargill (same company as Cargill Canada). "
            "Brazil is one of Cargill's largest global sourcing operations. "
            "A QSR buyer comfortable with Cargill Canada may also directly "
            "source Brazilian-origin oils and starches from the same corporate group "
            "with consistent food safety standards."
        ),
    },

    {
        "name":           "Louis Dreyfus Company Brazil",
        "country":        "Brazil",
        "region":         "Sao Paulo (HQ); operations across 15 Brazilian states",
        "supplier_type":  "Trader",
        "categories":     ["🌾 Dry Goods"],
        "products":       ["Soybeans", "Corn", "Sugar", "Cotton", "Coffee", "Soybean oil"],
        "certifications": ["HACCP", "ISO 22000", "ISCC (sustainability)"],
        "website":        "https://www.ldc.com",
        "cusma_eligible": False,
        "export_markets": ["China", "USA", "EU", "Japan", "Canada", "Middle East", "India"],
        "notes": (
            "One of the world's top commodity trading companies (ABCD group). "
            "Note supplier_type is Trader — LDC does not manufacture finished food "
            "products, but is one of the world's largest commodity originators. "
            "Relevant for a QSR buyer sourcing bulk commodity ingredients at scale. "
            "Brazil is the world's largest soybean and coffee exporter."
        ),
    },


    # ══════════════════════════════════════════════════════════════════════════
    # THAILAND — PROTEINS
    # Tariff note: Thai suppliers face ~12% Canadian import duty.
    # Sea freight: ~25-35 days via Vancouver + CN Rail to Ontario.
    # Thailand has strong food export infrastructure and world-class QSR clients.
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "CP Foods (Charoen Pokphand Foods PCL)",
        "country":        "Thailand",
        "region":         "Bangkok (HQ); processing plants across Thailand, Vietnam, Malaysia, UK",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins", "❄️ Frozen & Cold Chain"],
        "products":       ["Frozen chicken cuts", "Chicken nuggets", "Chicken patties", "Pork", "Shrimp", "IQF chicken"],
        "certifications": ["HACCP", "BRC", "ISO 22000", "GlobalG.A.P", "GMP", "Halal", "FDA registered"],
        "website":        "https://www.cpfworldwide.com",
        "cusma_eligible": False,
        "export_markets": ["EU", "Japan", "China", "Australia", "Canada", "USA", "Middle East", "UK"],
        "notes": (
            "Asia's largest poultry exporter and one of the world's largest integrated "
            "food companies. Supplies McDonald's, KFC, Subway, and Burger King globally — "
            "arguably the strongest QSR reference list in Asia. Publicly traded on "
            "the Bangkok Stock Exchange. Has processing plants in the UK and Europe, "
            "which can provide additional supply chain diversification."
        ),
    },

    {
        "name":           "Thai Union Group PCL",
        "country":        "Thailand",
        "region":         "Samut Sakhon (HQ); processing plants in Thailand, Vietnam, Ghana, USA",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins", "❄️ Frozen & Cold Chain"],
        "products":       ["Canned tuna", "Frozen tuna", "Shrimp", "Salmon", "Sardines", "Seafood products"],
        "certifications": ["BRC", "ISO 22000", "MSC certified", "HACCP", "FDA registered", "IFFO"],
        "website":        "https://www.thaiunion.com",
        "cusma_eligible": False,
        "export_markets": ["USA", "EU", "Canada", "Japan", "Australia", "Middle East"],
        "notes": (
            "The world's largest tuna processor, responsible for approximately 1 in 5 "
            "cans of tuna sold globally. Brands include John West, Chicken of the Sea, "
            "and Sealect. BRC and MSC certified — meets the highest international "
            "seafood standards. Listed on the Bangkok Stock Exchange. "
            "Relevant for QSR menus featuring fish burgers, seafood wraps, or canned tuna."
        ),
    },

    {
        "name":           "Betagro Group",
        "country":        "Thailand",
        "region":         "Bangkok (HQ); integrated operations across Thailand",
        "supplier_type":  "Manufacturer",
        "categories":     ["🍗 Proteins", "❄️ Frozen & Cold Chain"],
        "products":       ["Chicken", "Pork", "Processed meats", "Eggs", "Ready-to-cook chicken"],
        "certifications": ["HACCP", "GMP", "ISO 22000", "BRC", "Halal", "EU approved"],
        "website":        "https://www.betagro.com",
        "cusma_eligible": False,
        "export_markets": ["EU", "Japan", "South Korea", "Middle East", "Singapore"],
        "notes": (
            "Thailand's second-largest integrated poultry and pork company. "
            "EU-approved export status — a strong quality signal for Canadian buyers, "
            "as EU approval requires meeting some of the strictest food safety "
            "standards in the world. Significant exporter to Japan which is known "
            "for extremely high food safety requirements."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # THAILAND — DRY GOODS
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name":           "Thai Roong Ruang Sugar Group",
        "country":        "Thailand",
        "region":         "Bangkok (HQ); sugar mills across Central and Eastern Thailand",
        "supplier_type":  "Manufacturer",
        "categories":     ["🌾 Dry Goods"],
        "products":       ["White refined sugar", "Raw sugar", "Brown sugar", "Molasses"],
        "certifications": ["ISO 9001", "ISO 22000", "HACCP", "GMP", "Bonsucro (sustainable sugar)"],
        "website":        "https://www.thaisugar.co.th",
        "cusma_eligible": False,
        "export_markets": ["ASEAN", "China", "Middle East", "Japan", "South Korea", "EU"],
        "notes": (
            "One of Thailand's largest sugar producers. Thailand is the world's third-largest "
            "sugar exporter. Bonsucro certification signals commitment to sustainable "
            "sugarcane production — increasingly important for QSR buyers with ESG commitments. "
            "ISO 22000 and HACCP meet CFIA requirements for food ingredients imported to Canada."
        ),
    },

]   # ← end of SUPPLIERS list


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# These make it easy to query the SUPPLIERS list without writing loops manually.
# Think of them as mini search tools for this database.
# ─────────────────────────────────────────────────────────────────────────────

def get_by_category(category: str) -> list[dict]:
    """
    Returns all suppliers that serve a given QSR product category.

    Args:
        category: One of the keys from QSR_CATEGORIES, e.g. "🍗 Proteins"

    Returns:
        A filtered list of supplier dicts.

    Example:
        for s in get_by_category("🍗 Proteins"):
            print(s["name"])
    """
    return [s for s in SUPPLIERS if category in s.get("categories", [])]


def get_by_region(country: str) -> list[dict]:
    """
    Returns all suppliers from a given country.

    Args:
        country: Country name, e.g. "Canada", "India", "Thailand", "Brazil", "USA"

    Returns:
        A filtered list of supplier dicts.

    Note:
        Matching is case-insensitive so "canada" and "Canada" both work.

    Example:
        indian_suppliers = get_by_region("India")
    """
    return [s for s in SUPPLIERS if s.get("country", "").lower() == country.lower()]


# Keep the old name as an alias so any code that already uses get_by_country()
# continues to work without breaking.
# An alias just means: get_by_country IS get_by_region (same function, two names).
get_by_country = get_by_region


def get_cusma_eligible() -> list[dict]:
    """
    Returns all suppliers that qualify for 0% import duty to Canada under CUSMA.
    These are suppliers based in Canada, the USA, or Mexico.

    Example:
        zero_duty = get_cusma_eligible()
    """
    return [s for s in SUPPLIERS if s.get("cusma_eligible", False)]


def get_manufacturers_only() -> list[dict]:
    """
    Returns only direct manufacturers (excludes Distributors and Traders).
    Manufacturers are generally preferred in QSR sourcing because:
    - Lower price (no distributor margin)
    - Direct quality control relationship
    - Ability to customise product specs
    """
    return [s for s in SUPPLIERS if s.get("supplier_type") == "Manufacturer"]


def search_by_product(keyword: str) -> list[dict]:
    """
    Searches for suppliers by a keyword that appears in their product list.
    Matching is case-insensitive.

    Args:
        keyword: Part of a product name, e.g. "fries", "sugar", "canola", "tuna"

    Returns:
        List of matching supplier dicts.

    Example:
        fry_suppliers = search_by_product("fries")
    """
    keyword_lower = keyword.lower()
    results = []
    for supplier in SUPPLIERS:
        # Join all product names into one long string, then check if keyword is in it
        products_text = " ".join(supplier.get("products", [])).lower()
        if keyword_lower in products_text:
            results.append(supplier)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# COUNTRY NAME NORMALISATION
# Maps common abbreviations and alternate spellings to a single canonical form.
# This ensures "USA", "United States", and "US" all resolve to "usa".
# ─────────────────────────────────────────────────────────────────────────────
_COUNTRY_ALIASES: dict[str, str] = {
    "us":                          "usa",
    "u.s.":                        "usa",
    "u.s.a.":                      "usa",
    "united states":               "usa",
    "united states of america":    "usa",
    "america":                     "usa",
    "uk":                          "united kingdom",
    "great britain":               "united kingdom",
    "england":                     "united kingdom",
    "uae":                         "united arab emirates",
    "emirates":                    "united arab emirates",
    "south korea":                 "south korea",
    "korea":                       "south korea",
    "democratic republic of congo": "drc",
}


# ─────────────────────────────────────────────────────────────────────────────
# REGIONAL MARKET GROUPS
# Many suppliers list "Southeast Asia" or "Middle East" in their export_markets
# rather than naming individual countries. This map translates those region
# labels into the set of countries they cover so a buyer from Thailand matches
# a supplier that exports to "Southeast Asia".
#
# None means "global" / "worldwide" — matches any buyer country.
# ─────────────────────────────────────────────────────────────────────────────
_REGION_MAP: dict[str, set | None] = {
    "southeast asia":  {"thailand", "vietnam", "malaysia", "singapore", "indonesia", "philippines", "myanmar", "cambodia"},
    "asean":           {"thailand", "vietnam", "malaysia", "singapore", "indonesia", "philippines", "myanmar", "cambodia"},
    "middle east":     {"united arab emirates", "uae", "saudi arabia", "kuwait", "qatar", "bahrain", "oman", "jordan", "egypt", "israel"},
    "south america":   {"brazil", "argentina", "chile", "colombia", "peru", "ecuador", "uruguay"},
    "latin america":   {"brazil", "argentina", "chile", "colombia", "peru", "mexico", "ecuador", "uruguay"},
    "eu":              {"germany", "france", "italy", "spain", "netherlands", "belgium", "poland", "sweden", "denmark", "austria"},
    "europe":          {"germany", "france", "italy", "spain", "netherlands", "belgium", "poland", "sweden", "denmark", "austria", "united kingdom"},
    "asia":            {"china", "japan", "south korea", "india", "thailand", "vietnam", "malaysia", "singapore", "indonesia"},
    "north america":   {"canada", "usa", "mexico"},
    "oceania":         {"australia", "new zealand"},
    "africa":          {"south africa", "nigeria", "kenya", "egypt", "ghana"},
    "global":          None,   # None → matches any country
    "worldwide":       None,
    "international":   None,
}


def _normalise_country(name: str) -> str:
    """
    Convert a country name to its canonical lowercase form.
    E.g., "United States" → "usa", "UK" → "united kingdom".
    """
    lower = name.strip().lower()
    return _COUNTRY_ALIASES.get(lower, lower)


def _parse_country_from_location(location: str) -> str:
    """
    Extracts the country from any common location string format.

    This function is intentionally defensive — it handles whatever the user
    types into the profile Location field, including:
      "India"                       →  "India"
      "india"                       →  "india"  (normalised later via _normalise_country)
      "Gujarat, India"              →  "India"
      "Mumbai, Maharashtra, India"  →  "India"
      "Ontario, Canada"             →  "Canada"
      "New York, USA"               →  "USA"

    Rule: split on commas, strip whitespace, take the LAST non-empty segment.
    This works for 'City, Country' and 'City, Province, Country' formats because
    the country is almost always the final part of a comma-separated address.
    """
    if not location or not location.strip():
        return "Canada"     # Safe default if profile location is empty
    parts = [p.strip() for p in location.split(",") if p.strip()]
    return parts[-1] if parts else "Canada"


# Words that carry no product meaning and should be stripped before keyword matching.
# Keeping this tight — only true filler words, not food adjectives.
_STOP_WORDS: frozenset = frozenset({
    "the", "for", "in", "of", "a", "an", "and", "or", "with", "from",
    "bulk", "wholesale", "fresh", "dried", "raw", "processed", "packaged",
    "food", "grade", "product", "products", "supply", "supplier", "suppliers",
})


def _extract_product_keywords(product: str) -> list[str]:
    """
    Extracts meaningful keywords from a product search string.

    Removes stop words and very short tokens so that only the informative
    words remain for matching against supplier product lists.

    Examples:
        "parboiled rice"        → ["parboiled", "rice"]
        "fresh chicken breast"  → ["chicken", "breast"]
        "BBQ sauce bulk"        → ["bbq", "sauce"]
        "for bulk wholesale"    → []   (all stop words — no filter applied)
    """
    words = product.lower().split()
    return [w for w in words if w not in _STOP_WORDS and len(w) > 2]


def get_top_suppliers_for_profile(buyer_location: str, category: str, product: str = "") -> list[dict]:
    """
    Returns suppliers for a given QSR category, sorted by relevance to the
    buyer's location. This mirrors the real-world sourcing priority:
      1. Same country as buyer  (no duties, shortest lead time)
      2. CUSMA partners         (0% duty, fast lead times — CA/US/MX buyers only)
      3. Suppliers that already export to the buyer's country or region
      4. All other suppliers    (higher duty, longer freight)

    Args:
        buyer_location: Full location string from user_profile.json, e.g.
                        "India", "Gujarat, India", "Ontario, Canada", "USA"
        category:       The QSR category to search, e.g. "🍗 Proteins"
        product:        Specific product searched for, e.g. "chicken breast".
                        When provided, only suppliers whose products list or notes
                        contain at least one matching keyword are returned.
                        If no match is found, returns an empty list rather than
                        showing irrelevant suppliers. Example: searching "coffee"
                        will not return protein suppliers even if they are in the
                        same QSR category.

    Returns:
        Sorted list of supplier dicts, best match first.
    """
    # Parse location string → extract country → normalise to canonical lowercase
    buyer_country  = _parse_country_from_location(buyer_location)

    # Narrow down to suppliers that serve this category
    candidates = get_by_category(category)

    # ── Product relevance filter ──
    # Extract meaningful keywords from the searched product and only keep
    # suppliers whose products list (strong match) or notes (weak match)
    # contain at least one keyword.
    #
    # Priority:
    #   Exact product keyword in products list  → included (stronger signal)
    #   Keyword found only in notes             → included (weaker signal)
    #   No keyword match anywhere               → excluded (never show)
    #
    # If keywords list is empty (all stop words) → skip filtering entirely.
    keywords = _extract_product_keywords(product) if product.strip() else []
    if keywords:
        exact_matches = [
            s for s in candidates
            if any(kw in " ".join(s.get("products", [])).lower() for kw in keywords)
        ]
        notes_matches = [
            s for s in candidates
            if s not in exact_matches
            and any(kw in s.get("notes", "").lower() for kw in keywords)
        ]
        # Exact product matches first, notes-only matches second
        candidates = exact_matches + notes_matches

    buyer_norm     = _normalise_country(buyer_country)
    cusma_members  = {"canada", "usa", "mexico"}
    buyer_is_cusma = buyer_norm in cusma_members

    def _exports_to_buyer(supplier: dict) -> bool:
        """
        Returns True if the supplier's export_markets list covers the buyer's
        country — either as a direct name match or via a regional group.
        """
        for market in supplier.get("export_markets", []):
            market_norm = _normalise_country(market)

            # Direct country match (e.g., "Canada" → "canada" == buyer "canada")
            if market_norm == buyer_norm:
                return True

            # Regional group match (e.g., "Southeast Asia" covers "thailand")
            if market_norm in _REGION_MAP:
                group = _REGION_MAP[market_norm]
                if group is None:               # "Global" / "Worldwide"
                    return True
                if buyer_norm in group:
                    return True

        return False

    def _priority(supplier: dict) -> int:
        """
        Returns a sort priority integer (lower = higher priority).
        Python's sorted() is stable, so equal-priority items keep their list order.
        """
        supplier_norm = _normalise_country(supplier.get("country", ""))

        # Priority 0 — same country as the buyer
        if supplier_norm == buyer_norm:
            return 0

        # Priority 1 — CUSMA free-trade partner (Canada ↔ USA ↔ Mexico, 0% duty)
        if supplier.get("cusma_eligible", False) and buyer_is_cusma:
            return 1

        # Priority 2 — supplier already exports to this buyer's country or region
        if _exports_to_buyer(supplier):
            return 2

        # Priority 3 — everyone else
        return 3

    return sorted(candidates, key=_priority)


def get_summary() -> dict:
    """
    Returns a high-level overview of the database contents.
    Useful for a quick sanity check without reading every entry.
    """
    all_countries = sorted({s.get("country", "Unknown") for s in SUPPLIERS})
    all_categories = sorted({cat for s in SUPPLIERS for cat in s.get("categories", [])})

    return {
        "total_suppliers":    len(SUPPLIERS),
        "by_country":         {c: len(get_by_region(c)) for c in all_countries},
        "manufacturers":      len(get_manufacturers_only()),
        "distributors":       len([s for s in SUPPLIERS if s.get("supplier_type") == "Distributor"]),
        "traders":            len([s for s in SUPPLIERS if s.get("supplier_type") == "Trader"]),
        "cusma_eligible":     len(get_cusma_eligible()),
        "categories_covered": all_categories,
    }


# ─────────────────────────────────────────────────────────────────────────────
# QUICK TEST — runs only when you execute this file directly
# Type:  python curated_suppliers.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    summary = get_summary()
    print("=" * 62)
    print("  QSR Global Supplier Database - Summary")
    print("=" * 62)
    print(f"  Total suppliers:     {summary['total_suppliers']}")
    print(f"  Manufacturers:       {summary['manufacturers']}")
    print(f"  Distributors:        {summary['distributors']}")
    print(f"  Traders:             {summary['traders']}")
    print(f"  CUSMA eligible:      {summary['cusma_eligible']}")
    print(f"  Categories covered:  {len(summary['categories_covered'])}")
    print()
    print("  Suppliers by country:")
    for country, count in summary["by_country"].items():
        print(f"    {country:<20} {count} supplier(s)")

    print()
    print("  --- get_top_suppliers_for_profile('Canada', 'Proteins') ---")
    from qsr_config import QSR_CATEGORIES
    protein_cat = list(QSR_CATEGORIES.keys())[0]  # First category = Proteins
    ranked = get_top_suppliers_for_profile("Canada", protein_cat, "")
    for s in ranked:
        tag = "[CUSMA]" if s.get("cusma_eligible") else "[Offshore]"
        print(f"    {tag:<12} {s['name']:<40} ({s['country']})")

    print()
    print("  --- search_by_product('fries') ---")
    for s in search_by_product("fries"):
        print(f"    {s['name']} ({s['country']})")

    print()
    print("  --- search_by_product('sugar') ---")
    for s in search_by_product("sugar"):
        print(f"    {s['name']} ({s['country']})")
