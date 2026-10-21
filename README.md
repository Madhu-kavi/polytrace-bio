# PolyTrace Bio 🌿
### Ingredient-Aware Biodegradability Screening & Supply-Chain Transparency Platform
*Sustainable Supply Chains Track — Scientific Decision-Support MVP*

---

## 1. Executive Summary & Purpose

**PolyTrace Bio** is an ingredient-aware biodegradability screening and supply-chain transparency platform for conventional polymers, biodegradable polyesters, and emerging bioplastics.

Global packaging and supply chains face rampant greenwashing, ambiguous terminology, and aggressive regulatory crackdowns (such as EU Directive 2019/904 and the EU Green Claims Directive). Many commercial products labeled "100% Biodegradable" or "Compostable" fail in real-world disposal environments because buyers, designers, and consumers confuse fundamentally distinct environmental pathways.

PolyTrace Bio enforces clear, non-negotiable scientific boundaries:
- **Biodegradability:** Biochemical carbon mineralization by microbial consortia into CO2, H2O, and cellular biomass.
- **Industrial Compostability:** High-temperature thermophilic degradation (**≥ 58 °C**) requiring regulated moisture and aeration (ISO 14855 / EN 13432 / ASTM D6400).
- **Home Compostability:** Ambient mesophilic degradation (**20 – 30 °C**) in variable backyard compost heaps (NF T51-800 / AS 5810).
- **Disintegration:** Physical fragmentation into particles < 2 mm; if not biochemically mineralized, it creates hazardous **microplastics**.
- **Recyclability:** Mechanical or chemical reprocessing; bioplastics like PLA contaminate conventional PET recycling streams at concentrations as low as 0.1%.
- **Environmental Ecotoxicity:** Ensuring degradation byproducts, mineral residues, and additives do not inhibit seedling emergence (OECD 208) or earthworm survival.

> **CRITICAL SCIENTIFIC DISCLAIMER:** PolyTrace Bio is a scientific decision-support prototype and transparent screening engine. It is **NOT** a certified laboratory testing service, legal certification agency, or unvalidated black-box machine learning model. It relies on deterministic rules, curated standards, and peer-reviewed literature.

---

## 2. Key Modules & New Features

### 🧭 1. Prominent Top Navigation & "Choose Your Path"
- **Top Horizontal Navigation:**
  Moved platform modules from the sidebar to a prominent, responsive horizontal navigation section directly below the hero banner. Supports five core operational modules:
  1. `🔍 Explore a Plastic` — document physical items and decipher visible recycling numbers.
  2. `🧪 Formulation Lab` — paste ingredient recipes and validate mass balance.
  3. `🔬 Biodegradability Screening` — assess environmental evidence against specific disposal targets.
  4. `⚖️ Compare Materials` — side-by-side trade-off matrix across 6 criteria.
  5. `📋 Material Passport` — view and export verifiable digital passport records.
  - Secondary access to `📖 Methodology & Science Guide` is available directly in the top navigation and footer.
- **"Choose Your Path" (Three Distinct User Entry Points):**
  - **Everyday User ("I have a plastic product"):** Fast onboarding to the photo/resin-code triage workflow with plain-language explanations of SPI codes 1–7.
  - **Biotech or Materials Researcher ("I have a formulation"):** Instant routing to the Formulation Lab for pasting raw recipes and evaluating additive biodegradability.
  - **Business or Procurement Team ("I need to verify a claim"):** Immediate access to claim verification, gap reports, and traceable material passports.

### 🎨 2. Professional Earth-Inspired Visual Redesign
- Polished environmental biotechnology SaaS aesthetic built with a nature-aligned, accessible palette:
  - **Deep Forest Green:** `#183D2B` (Headings, primary buttons, verified status badges)
  - **Leaf Green:** `#347A46` (Accent badges, interactive highlights)
  - **Sage:** `#A9C6A0` (Card borders, subtle status dividers)
  - **Warm Ivory:** `#F7F4EA` (Application background)
  - **Earth Brown:** `#79543A` (Secondary accents, borders, warning callouts)
  - **Sand:** `#DCC9A3` (Hero tagline, highlight borders)
  - **White:** `#FFFFFF` (Spacious, bright content cards)
  - **Dark Text:** `#243128` (Readable, accessible contrast text)
- **Product Hero Section:**
  - **Title:** `PolyTrace Bio`
  - **Tagline:** `"From formulation to environmental evidence."`
  - Supporting text: *"Understand materials, investigate environmental claims, and support more transparent supply chains."*
  - Includes local laboratory hero image asset (`assets/hero_banner.jpg`).
- **Real Session Metric Cards:**
  - Live counters for **Formulations Screened**, **Unknown Ingredients Flagged**, and **Evidence Gaps Detected** in the current user session (backed by real session state, never fabricated numbers).
- Configured with `.streamlit/config.toml` and inline SVG accents.

---

### 📷 3. Explore a Plastic (Plastic Vision): Camera + Image Upload (Guided Identification)
- **Visual Capture Controls:**
  - Live webcam / device camera capture using Streamlit's `st.camera_input`.
  - Image file upload alternative using `st.file_uploader` (JPG, JPEG, PNG).
  - Real-time image preview.
- **Documentation Inputs:**
  - Product name and intended application.
  - Visible Resin Identification Code selector (SPI Codes 1–7 + "No code visible"):
    - `1 PET` (Polyethylene Terephthalate)
    - `2 HDPE` (High-Density Polyethylene)
    - `3 PVC` (Polyvinyl Chloride)
    - `4 LDPE` (Low-Density Polyethylene)
    - `5 PP` (Polypropylene)
    - `6 PS` (Polystyrene)
    - `7 Other / Mixed / Unknown` (Bioplastics like PLA/PHA/PBAT, or multi-layer barrier laminates)
    - `No code visible` (Unmarked / residual waste)
  - Visible packaging label text, recycling symbols, supplier name, and known claims.
- **Guided Triage & Analysis:**
  - Analyzes resin code against recycling streams and real biodegradability fate.
  - Detects bioplastic vs conventional polymer clues in label text.
  - Flags severe claim mismatches (e.g. claiming "compostable" on Code 1 PET or Code 2 HDPE).
  - Suggests database candidates and offers a 1-click **"Send Guided Findings to Material Screening"** action.
- **CRITICAL SCIENTIFIC LIMITATION:**
  - A photograph alone **CANNOT** determine exact polymer chemistry, molecular weight, additives, or biodegradability.
  - This feature uses a **transparent guided identification workflow** using user-supplied clues. It does **NOT** make false claims of an automated AI/ML vision classification model. Images are processed purely locally and are **never** transmitted to external cloud services.

---

### 🧪 3. Formulation Lab: Copy-Paste Recipe Intake
Designed specifically for bioplastic researchers, packaging engineers, and supply chain managers pasting formulations from laboratory notebooks, spreadsheets, or supplier specifications.

#### Supported Paste Formats:
- **Format A (Comma-separated with %):**
  ```text
  PLA, 70%
  Talc, 20%
  Plasticizer, 8%
  Pigment, 2%
  ```
- **Format B (Spreadsheet table with header):**
  ```text
  Ingredient, Percentage
  PLA, 70
  Talc, 20
  Plasticizer, 8
  Pigment, 2
  ```
- **Format C (Inline semicolon / colon pairs):**
  ```text
  PLA: 70%; talc: 20%; plasticizer: 8%; pigment: 2%
  ```
- **Format D (wt% notation):**
  ```text
  PLA 70 wt%
  Talc 20 wt%
  Plasticizer 8 wt%
  Pigment 2 wt%
  ```
- **Tab-Separated Spreadsheet Pastes:** Direct copy-paste from Microsoft Excel or Google Sheets (`PLA\t70`).

#### Capabilities:
- **Deterministic Python Parser (`formulation_parser.py`):**
  - Handles line breaks, semicolons, tabs, colons, commas, and `wt%` / `mass%` notations.
  - Rejects negative percentages and malformed values.
  - Warns on duplicate ingredient entries.
  - Flags undisclosed trade-name additives (e.g., "Plasticizer", "Compatibilizer X") as **Unknown**.
  - Validates mass balance: enforces ~100% total; warns on under-reported (<99%) and over-reported (>101%) without silently inventing or auto-filling amounts.
- **Interactive Preview & Editable Dataframe:**
  - Displays parsed ingredient names, mass fractions, assigned categories, and database match status.
- **Direct Scientific Screening:**
  - 1-Click execution feeding directly into `screening_engine.py`.
  - Generates Green-Claim Gap Report and Digital Material Passport.
- **Exports:** Download parsed recipes as clean **CSV** or structured **JSON**.
- **Quick-Load Sample Buttons:** 1-Click buttons to populate the paste box with realistic bioplastic recipes.

---

### 🔬 4. Material Formulation Screening
- Evaluates multi-component formulations containing conventional resins (PE, PP, PET, PS, PVC), biopolymers (PLA, PHA, PBAT, PBS), natural polymers (TPS starch, cellulose), mineral fillers (CaCO3, talc), plasticizers (ATBC), pigments (TiO2, carbon black), and undisclosed additives.
- **Conservative Precautionary Rule:** Unrecognized or proprietary ingredients evaluate to *Insufficient Evidence* and are never assumed safe or biodegradable.
- **Mass-Balance Validation:** Enforces mass fractions to approximately 100%. Flags missing, under-reported, and over-reported fractions.

---

### 🏷️ 5. Transparent Qualitative Screening Labels
To prevent pseudo-scientific precision, the engine rejects uncalibrated numerical probabilities and assigns one of four verifiable qualitative labels backed by local evidence records:
1. `Evidence supports biodegradation under the specified conditions` (e.g. PLA in industrial compost; PHA in marine/soil)
2. `Limited or condition-specific evidence` (e.g. PBAT in home compost depending on thickness; PBS in soil)
3. `Insufficient evidence` (e.g. undisclosed trade secret additives, missing test reports)
4. `Evidence indicates low biodegradation under the specified conditions` (e.g. neat PLA in ambient ocean/soil; conventional PE/PP/PET in any compost)

---

### 📊 6. Documentation Completeness Index
- Evaluates provided supplier claims, test standards, test conditions, duration, quantitative metrics, and third-party certifications.
- Computes an objective documentation completeness percentage (0–100%).
- **Explicitly labeled as documentation completeness, NOT a biodegradability score.**

---

### 📑 7. Green-Claim Gap Report
For every screening, generates a 7-section traceable gap report:
1. **What the ingredients suggest:** Baseline chemical characteristics and theoretical degradation kinetics.
2. **What is supported by available evidence:** Verified facts linked directly to standards and local citations.
3. **What remains unknown:** Missing fractions, thickness parameters, ecotoxicity clearance.
4. **Supplier documents to request:** Specific audit requests (SDS Section 3, ISO/ASTM test reports, phytotoxicity clearance).
5. **Relevant test environment:** Standard matching the intended end-of-life channel.
6. **Unverified claims & mismatches:** Flags thermal mismatches (e.g. claiming home compostable with an industrial standard) and origin confusion (claiming bio-based carbon = biodegradable).
7. **Recommended next steps:** Actionable steps for sustainable procurement and packaging engineers.

---

### 📋 8. Digital Material Passport
- Generates a downloadable material passport containing a unique record ID (`PTB-2026-XXXXXXXX`), creation timestamp, formulation breakdown, screening classification, gap report, and verified disclaimer.
- Generates a **Local Offline QR Code** encoding the passport record identifier.
- Exports in both machine-readable **JSON** and human-readable **Markdown (.md)** formats.

---

### ⚖️ 9. Multi-Material Comparative Decision Matrix
- Compares 2 or 3 material formulations side-by-side against a benchmark disposal environment.
- Evaluates target environment evidence, documentation completeness, unknown ingredient count, mass balance, cross-environment compatibility, and substantiation gaps.
- Deliberately avoids an arbitrary single ranking number, surfacing genuine scientific trade-offs.

---

### 📖 10. Methodology & Educational Science Guide
- Interactive primer for biotechnology students, packaging engineers, and supply chain managers.
- Explains the 6 fundamental distinctions, the "Bio-based = Biodegradable" myth (ASTM D6866), and the EU ban on oxo-degradable plastics (Directive 2019/904).

---

## 3. Technology Stack & Architecture

- **Language:** Python 3.10+
- **Frontend Framework:** [Streamlit](https://streamlit.io/) (Earth-themed biotechnology dashboard)
- **Data Analysis & Export:** Pandas
- **QR Code Engine:** `qrcode` + `Pillow` (offline PNG base64 rendering)
- **Theme Configuration:** `.streamlit/config.toml` (Deep forest green, warm ivory, earth brown)
- **Architecture:** Strictly decoupled modular design:
  - `formulation_parser.py`: Multi-format recipe parser, regex tokenizers, mass-balance validator, CSV/JSON exporters.
  - `plastic_vision.py`: Resin code dictionary (SPI 1-7), guided clue analyzer, substantiation warning detector.
  - `screening_engine.py`: Core deterministic scientific screening rules, mass-balance validator, claim verifier, gap report generator, passport builder.
  - `app.py`: Streamlit user interface and interactive workflow.
  - `material_data.json`: Curated polymer, bioplastic, and additive database.
  - `evidence_sources.json`: Verifiable ISO/ASTM/EN standards, certification schemes, and literature citations.
  - `tests/test_screening_engine.py`: 23 automated unit tests.

---

## 4. Installation & Local Execution

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.

### Setup Instructions
1. **Navigate to the repository directory:**
   ```bash
   cd "Biopoly trace"
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
   *The application will open automatically in your browser at `http://localhost:8501`.*

---

## 5. Automated Test Suite (23 Tests)

PolyTrace Bio includes 23 automated unit tests validating scientific rules, multi-format recipe parsing, mass-balance bounds, claim verification, guided vision triage, and passport export:

```bash
python -m unittest discover -s tests -v
```

### Verified Test Cases:
1. `test_01_ingredient_lookup`: Verifies exact ID, name, and synonym lookups across polymers (e.g. PLA, PE, PHB, Cellophane).
2. `test_02_unknown_ingredient_handling`: Confirms unrecognized ingredients evaluate to *Insufficient Evidence* without guessing.
3. `test_03_percentage_validation`: Validates complete (100%), under-reported (<99%), over-reported (>101%), and qualitative formulations.
4. `test_04_environment_specific_evidence_matching`: Confirms condition-specific matching (PHA in marine vs industrial compost).
5. `test_05_distinguishing_compostability_from_environmental_biodegradation`: Verifies PLA supports industrial composting (≥58 °C) but exhibits low biodegradation in soil, marine, and home compost.
6. `test_06_no_unsupported_positive_claims_conventional_polymers`: Verifies PE + pro-degradant additive returns *Low biodegradation*, preventing false positives.
7. `test_07_supplier_claim_gaps_and_mismatches`: Detects thermal mismatches and marine vulnerability claims without marine testing.
8. `test_08_missing_documentation_completeness`: Confirms documentation completeness calculations for bare vs fully documented items.
9. `test_09_digital_material_passport_generation`: Validates passport ID generation, JSON serializability, Markdown export, and offline QR code.
10. `test_10_multi_ingredient_formulation_soil_mulch`: Validates multi-component agricultural mulch film (PBAT + Starch + CaCO3 + Carbon Black).
11. `test_11_insufficient_evidence_when_completely_undocumented`: Confirms empty or completely undocumented items yield *Insufficient Evidence*.
12. `test_12_parser_format_a_comma_separated`: Verifies parsing of Format A (comma-separated with `%`).
13. `test_13_parser_format_b_table_with_header`: Verifies parsing of Format B (table format with header line).
14. `test_14_parser_format_c_semicolon_colon`: Verifies parsing of Format C (inline semicolon-separated pairs).
15. `test_15_parser_format_d_wt_percent`: Verifies parsing of Format D (`wt%` notation).
16. `test_16_parser_tab_delimited_spreadsheet`: Verifies parsing of tab-delimited spreadsheet cell pastes.
17. `test_17_parser_negative_and_invalid_percentages`: Verifies rejection of negative percentages and malformed values.
18. `test_18_parser_missing_percentages_and_unknowns`: Confirms unassigned percentages and unknown additive flags.
19. `test_19_parser_totals_bounds`: Validates under-reported (<99%) and over-reported (>101%) mass balance alerts.
20. `test_20_parser_duplicate_ingredients`: Validates duplicate ingredient detection and warning.
21. `test_21_parser_empty_input`: Confirms graceful handling of empty or blank string input.
22. `test_22_plastic_vision_guided_identification`: Verifies Plastic Vision resin code profiling, clue detection, and claim mismatch flags without an image.
23. `test_23_preservation_of_passport_and_screening`: End-to-end integration test: Pasted text -> Parse -> Screen -> Passport Export.

---

## 6. Scientific Sources & Standards Reference

| Standard / Reference | Scope | Description |
| :--- | :--- | :--- |
| **ISO 14855-1 / ISO 14855-2** | Industrial Composting | Aerobic biodegradation under controlled thermophilic composting conditions (58 °C). |
| **EN 13432:2000** | Packaging Composting | Harmonized European standard requiring characterization, 90% biodegradation, disintegration (<2mm), and plant ecotoxicity tests. |
| **ASTM D6400-23** | Industrial Composting | Standard specification for solid plastics compostable in commercial/municipal facilities. |
| **NF T51-800 / AS 5810** | Home Composting | Specifications for plastics suitable for ambient temperature (20–30 °C) home composting. |
| **EN 17033:2018 / ISO 17556** | Soil Biodegradation | Biodegradable mulch films in agriculture; requires 90% soil biodegradation in 24 months + terrestrial ecotoxicity. |
| **ISO 22403 / ASTM D6691** | Marine Biodegradation | Intrinsic biodegradability assessment exposed to marine inocula. |
| **ASTM D6866-24** | Feedstock Carbon Dating | Radiocarbon dating determining bio-based carbon fraction (**does NOT measure biodegradability**). |
| **Narancic et al. (2018)** | *Environ. Sci. Technol.* | Landmark real-world testing of bioplastics across industrial, home, soil, and aquatic environments. |
| **Haider et al. (2019)** | *Angew. Chem. Int. Ed.* | Comprehensive review of abiotic hydrolysis vs microbial mineralization mechanisms. |
| **EU SAPEA (2020)** | European Commission | Scientific Opinion on the biodegradability of plastics in the open environment. |

---

## 7. Assumptions & Scientific Limitations

1. **Geometry and Article Thickness:** Standard respirometry tests evaluate powdered or thin films. In real-world composting or soil burial, thicker articles (e.g. >2 mm) disintegrate significantly slower due to surface-area-to-volume constraints.
2. **Local Facility Infrastructure:** Industrial compostability requires access to commercial facilities operating thermophilic composting phases (>58 °C). In municipalities lacking organic waste collection, compostable plastics end up in landfill (anaerobic methane emissions) or incinerators.
3. **No Substitute for Laboratory Testing:** This software screens claims and flags documentation gaps. It does not replace physical certification (e.g., DIN CERTCO, TÜV AUSTRIA, BPI) on the final converted article.
4. **Plastic Vision Scope:** A photograph alone cannot determine chemical composition or biodegradability. Plastic Vision is a **guided triage** tool that maps physical clues to known resin profiles; it does **not** perform analytical chemical testing (such as FTIR spectroscopy).
5. **Offline QR Code Scope:** QR codes generated by the passport represent local offline snapshot identifiers. They do not connect to a live public cloud server.

---

## 8. Free Deployment Guide

PolyTrace Bio requires zero paid APIs, zero database servers, and zero mandatory API keys. It can be deployed for free on:

### Option A: Streamlit Community Cloud (Recommended)
1. Push this repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **New app**, select your repository, branch (`main`), and set the entry file to `app.py`.
4. Click **Deploy!** Your app will be live with a public URL in ~2 minutes.

### Option B: Hugging Face Spaces
1. Create a free account on [huggingface.co](https://huggingface.co).
2. Create a new Space, select **Streamlit** as the SDK.
3. Push or upload the project files. Hugging Face will automatically build and host the application.

### Option C: Render (Free Web Service)
1. Create a free account on [render.com](https://render.com).
2. Connect your GitHub repository as a **Web Service**.
3. Environment: `Python 3`.
4. Build Command: `pip install -r requirements.txt`.
5. Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.

---

## 9. Genuine vs Prototype Features

| Feature | Implementation Status | Technical Mechanism |
| :--- | :--- | :--- |
| **Ingredient & Synonyms Lookup** | ✅ **Genuinely Functional** | Deterministic token matching against verified chemical entries in `material_data.json`. |
| **Multi-Format Recipe Parser** | ✅ **Genuinely Functional** | Deterministic regex parsing supporting Formats A, B, C, D, tab-separated, wt%, and mass-balance checks in `formulation_parser.py`. |
| **Plastic Vision Guided Triage** | ✅ **Genuinely Functional** | Live `st.camera_input` and file uploader + resin code dictionary (SPI 1-7) + clue analysis in `plastic_vision.py`. |
| **Mass-Balance Validation** | ✅ **Genuinely Functional** | Mathematical mass summation, under/over-reported bounds, qualitative fallback. |
| **Environment-Specific Evidence Matching** | ✅ **Genuinely Functional** | Condition-matched respirometric criteria from ISO/ASTM/EN datasets. |
| **Supplier Claim Verification** | ✅ **Genuinely Functional** | Rule-based semantic mismatch detector comparing claims with standards and test scopes. |
| **Green-Claim Gap Report** | ✅ **Genuinely Functional** | 7-part structured gap breakdown linking claims directly to local evidence records. |
| **Digital Material Passport** | ✅ **Genuinely Functional** | Unique ID generation, JSON export, Markdown export, and local offline QR code rendering. |
| **Material Comparison Matrix** | ✅ **Genuinely Functional** | Multi-dimensional side-by-side trade-off matrix across 6 criteria. |
| **Automated AI/ML Vision Classification** | ❌ *Intentionally Excluded* | A photograph alone cannot determine polymer composition; guided triage is used instead to avoid pseudo-science. |
| **Physical Laboratory Testing** | ⚙️ *Decision-Support Prototype* | Software decision-support tool; cannot perform physical respirometry or GC-MS lab testing. |
