"""
PolyTrace Bio — Ingredient-Aware Biodegradability Screening & Supply-Chain Transparency Platform
================================================================================================
A scientific decision-support system for sustainable supply chains.
Author: PolyTrace Bio Product & Engineering Team
"""

import streamlit as st
import json
import os
import pandas as pd
import datetime
from typing import List, Dict, Any, Optional

from screening_engine import (
    ScreeningEngine,
    FormulationItem,
    ENVIRONMENTS,
    LABEL_SUPPORTS,
    LABEL_LIMITED,
    LABEL_INSUFFICIENT,
    LABEL_LOW,
    get_curated_sample_materials
)
from formulation_parser import (
    parse_pasted_formulation,
    export_formulation_csv,
    export_formulation_json,
    SAMPLE_PASTE_FORMATS
)
from plastic_vision import (
    RESIN_IDENTIFICATION_CODES,
    analyze_vision_documentation
)

# Page configuration
st.set_page_config(
    page_title="PolyTrace Bio | Scientific Biodegradability Screening",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# BRIGHT EARTH-INSPIRED CUSTOM STYLING
# ==========================================
st.markdown("""
<style>
    /* PolyTrace Bio Earth Palette:
       Forest Green: #183D2B
       Leaf Green:   #347A46
       Sage:         #A9C6A0
       Warm Ivory:   #F7F4EA
       Earth Brown:  #79543A
       Sand:         #DCC9A3
       White:        #FFFFFF
       Dark Text:    #243128
    */

    /* Base Page Styling: Bright & Spacious */
    .stApp {
        background-color: #F7F4EA;
        color: #243128;
    }

    h1, h2, h3, h4 {
        color: #183D2B !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Hero Banner Styling */
    .hero-banner {
        background: linear-gradient(135deg, #183D2B 0%, #224D36 55%, #347A46 100%);
        border-radius: 14px;
        padding: 24px 28px;
        color: #F7F4EA;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(24, 61, 43, 0.12);
        border-bottom: 4px solid #79543A;
    }

    .hero-badge {
        display: inline-block;
        background-color: #DCC9A3;
        color: #183D2B;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        padding: 4px 10px;
        border-radius: 4px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #F7F4EA;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .hero-tagline {
        font-size: 1.15rem;
        font-weight: 600;
        color: #DCC9A3;
        margin: 4px 0 10px 0;
    }

    .hero-desc {
        font-size: 0.94rem;
        color: #E6EFE4;
        line-height: 1.5;
        margin: 0;
        max-width: 820px;
    }

    /* "Choose Your Path" User Cards */
    .user-path-card {
        background-color: #FFFFFF;
        border: 1px solid #C4D7BE;
        border-top: 4px solid #347A46;
        border-radius: 10px;
        padding: 16px 18px;
        min-height: 165px;
        box-shadow: 0 2px 8px rgba(36, 49, 40, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    .user-path-role {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #79543A;
        letter-spacing: 0.6px;
    }

    .user-path-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #183D2B;
        margin: 4px 0 6px 0;
    }

    .user-path-desc {
        font-size: 0.85rem;
        color: #4A5B4F;
        line-height: 1.4;
        margin-bottom: 8px;
    }

    /* Top Horizontal Navigation Styling */
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        gap: 8px;
        background-color: #EFE9DB;
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid #DCC9A3;
        margin-bottom: 20px;
    }

    div[data-testid="stRadio"] label {
        background-color: #FFFFFF;
        border: 1px solid #C4D7BE;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.92rem;
        color: #183D2B;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }

    div[data-testid="stRadio"] label:hover {
        background-color: #EEF3EC;
        border-color: #347A46;
    }

    div[data-testid="stRadio"] label[data-checked="true"],
    div[data-testid="stRadio"] label:has(input:checked) {
        background-color: #183D2B !important;
        color: #F7F4EA !important;
        border-color: #183D2B !important;
        box-shadow: 0 2px 6px rgba(24, 61, 43, 0.2);
    }

    /* Session Metric Cards */
    .session-metrics-row {
        display: flex;
        gap: 14px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }

    .session-metric-card {
        flex: 1;
        min-width: 180px;
        background-color: #FFFFFF;
        border: 1px solid #C4D7BE;
        border-top: 3px solid #347A46;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 2px 6px rgba(36, 49, 40, 0.04);
    }

    .metric-number {
        font-size: 1.65rem;
        font-weight: 700;
        color: #183D2B;
        margin: 2px 0;
    }

    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #79543A;
    }

    .metric-desc {
        font-size: 0.76rem;
        color: #4A5B4F;
        margin: 0;
    }

    /* Qualitative Badges */
    .badge-supports {
        background-color: #D2E4D4;
        color: #183D2B;
        border: 1px solid #A9C6A0;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }

    .badge-limited {
        background-color: #F8ECD5;
        color: #79543A;
        border: 1px solid #DCC9A3;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }

    .badge-insufficient {
        background-color: #E5E9E4;
        color: #4A5B4F;
        border: 1px solid #C8D2C6;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }

    .badge-low {
        background-color: #F5DED9;
        color: #8C2F24;
        border: 1px solid #E2AFA8;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }

    /* Earth-Accented Containers */
    .earth-card {
        background-color: #FFFFFF;
        border: 1px solid #C4D7BE;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(24, 61, 43, 0.04);
    }

    .earth-callout {
        border-left: 4px solid #183D2B;
        background-color: #EEF3EC;
        padding: 12px 16px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }

    .earth-warning {
        border-left: 4px solid #79543A;
        background-color: #FBF6EE;
        padding: 12px 16px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #EFE9DB !important;
        border-right: 1px solid #DCC9A3;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_engine() -> ScreeningEngine:
    """Initialize and cache the screening engine."""
    return ScreeningEngine()


engine = get_engine()
sample_materials = get_curated_sample_materials()


# Initialize Session State
if "active_module" not in st.session_state:
    st.session_state.active_module = "🔬 Biodegradability Screening"
if "active_material_name" not in st.session_state:
    st.session_state.active_material_name = "Commercial Bio-Cup Lining (PLA + Talc)"
if "active_target_env" not in st.session_state:
    st.session_state.active_target_env = "industrial_compost"
if "active_formulation" not in st.session_state:
    st.session_state.active_formulation = sample_materials["Commercial Bio-Cup Lining (PLA + Talc)"]["formulation"]
if "active_use" not in st.session_state:
    st.session_state.active_use = "Hot coffee cup waterproof interior lining"
if "active_eol" not in st.session_state:
    st.session_state.active_eol = "Industrial Composting Facility"
if "latest_passport" not in st.session_state:
    st.session_state.latest_passport = None

# Real session statistics counters
if "session_formulations_count" not in st.session_state:
    st.session_state.session_formulations_count = 0
if "session_unknowns_flagged" not in st.session_state:
    st.session_state.session_unknowns_flagged = 0
if "session_evidence_gaps" not in st.session_state:
    st.session_state.session_evidence_gaps = 0
if "screened_fingerprints" not in st.session_state:
    st.session_state.screened_fingerprints = set()

# Helper function to track session stats
def record_screening_stats(material_name: str, target_env: str, items_count: int, unknowns: int, gaps: int):
    fp = f"{material_name}_{target_env}_{items_count}"
    if fp not in st.session_state.screened_fingerprints:
        st.session_state.screened_fingerprints.add(fp)
        st.session_state.session_formulations_count += 1
        st.session_state.session_unknowns_flagged += unknowns
        st.session_state.session_evidence_gaps += gaps


# Helper to get badge HTML
def get_label_badge(label: str) -> str:
    if label == LABEL_SUPPORTS:
        return f'<span class="badge-supports">✅ {label}</span>'
    elif label == LABEL_LIMITED:
        return f'<span class="badge-limited">⚠️ {label}</span>'
    elif label == LABEL_LOW:
        return f'<span class="badge-low">❌ {label}</span>'
    else:
        return f'<span class="badge-insufficient">❓ {label}</span>'


# ==========================================
# SIDEBAR CONTROLS & PRESET LOADER
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#183D2B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>
        <span style="font-size: 1.4rem; font-weight: 800; color: #183D2B;">PolyTrace Bio</span>
    </div>
    <div style="font-size: 0.82rem; font-weight: 600; color: #79543A; margin-bottom: 12px;">Sustainable Supply Chains MVP</div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Sample Material Presets")
    st.caption("Load realistic verified case studies into the workspace:")

    selected_sample = st.selectbox(
        "Choose sample formulation:",
        list(sample_materials.keys()),
        index=0
    )

    if st.button("📥 Load Preset into Workspace", use_container_width=True):
        preset = sample_materials[selected_sample]
        st.session_state.active_material_name = preset["name"]
        st.session_state.active_target_env = preset["target_env"]
        st.session_state.active_formulation = preset["formulation"]
        st.session_state.active_use = preset["intended_use"]
        st.session_state.active_eol = preset["intended_eol"]
        st.session_state.latest_passport = None
        st.session_state.active_module = "🔬 Biodegradability Screening"
        st.success(f"Loaded '{preset['name']}'! Navigating to Screening.")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Session Activity")
    st.write(f"- Formulations Screened: **{st.session_state.session_formulations_count}**")
    st.write(f"- Unknown Additives Flagged: **{st.session_state.session_unknowns_flagged}**")
    st.write(f"- Evidence Gaps Flagged: **{st.session_state.session_evidence_gaps}**")

    st.markdown("---")
    st.markdown("""
    **Core Scientific Principles:**
    - ❌ *No unvalidated ML probabilities*
    - 🔍 *Deterministic, traceable rules*
    - 📑 *ISO 14855 / EN 13432 / EN 17033*
    - ⚠️ *Real documentation completeness*
    """)
    st.caption("Designed for Sustainable Supply Chains Track")


# ==========================================
# PRODUCT HERO BANNER & LOCAL IMAGE
# ==========================================
hero_col1, hero_col2 = st.columns([1.65, 1.0])

with hero_col1:
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">SUSTAINABLE SUPPLY CHAINS • SCIENTIFIC DECISION SUPPORT</div>
        <div class="hero-title">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#DCC9A3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>
            <span>PolyTrace Bio</span>
        </div>
        <div class="hero-tagline">"From formulation to environmental evidence."</div>
        <p class="hero-desc">
            Understand materials, investigate environmental claims, and support more transparent supply chains.
            Ingredient-aware screening strictly distinguishing industrial composting, home composting, soil burial, and marine persistence.
        </p>
    </div>
    """, unsafe_allow_html=True)

with hero_col2:
    hero_img_path = os.path.join(os.path.dirname(__file__), "assets", "hero_banner.jpg")
    if os.path.exists(hero_img_path):
        st.image(
            hero_img_path,
            caption="PolyTrace Bio: Biopolymer Transparency & Screening Laboratory",
            use_container_width=True
        )


# ==========================================
# "CHOOSE YOUR PATH" — THREE USER ENTRY POINTS
# ==========================================
st.markdown("### 🧭 Choose Your Path")
st.caption("Tailored workflows designed for consumers, materials researchers, and corporate procurement teams:")

path_c1, path_c2, path_c3 = st.columns(3)

with path_c1:
    st.markdown("""
    <div class="user-path-card">
        <div>
            <div class="user-path-role">🔍 Everyday User</div>
            <div class="user-path-title">"I have a plastic product."</div>
            <div class="user-path-desc">
                Identify visible recycling numbers (SPI codes 1–7), packaging stamps, and understand what markings mean in simple language.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Explore Markings →", key="btn_path_everyday", use_container_width=True):
        st.session_state.active_module = "🔍 Explore a Plastic"
        st.rerun()

with path_c2:
    st.markdown("""
    <div class="user-path-card">
        <div>
            <div class="user-path-role">🧪 Biotech or Materials Researcher</div>
            <div class="user-path-title">"I have a formulation."</div>
            <div class="user-path-desc">
                Paste recipe text or spreadsheet data, validate mass balance, check additive biodegradability, and explore condition limitations.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Formulation Lab →", key="btn_path_biotech", use_container_width=True):
        st.session_state.active_module = "🧪 Formulation Lab"
        st.rerun()

with path_c3:
    st.markdown("""
    <div class="user-path-card">
        <div>
            <div class="user-path-role">📋 Business or Procurement Team</div>
            <div class="user-path-title">"I need to verify a claim."</div>
            <div class="user-path-desc">
                Audit supplier green claims against ISO/ASTM standards, uncover substantiation gaps, and export verifiable Material Passports.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Verify Claims & Screening →", key="btn_path_procurement", use_container_width=True):
        st.session_state.active_module = "🔬 Biodegradability Screening"
        st.rerun()


# ==========================================
# PROMINENT TOP HORIZONTAL NAVIGATION
# ==========================================
NAV_MODULES = [
    "🔍 Explore a Plastic",
    "🧪 Formulation Lab",
    "🔬 Biodegradability Screening",
    "⚖️ Compare Materials",
    "📋 Material Passport",
    "📖 Methodology & Science Guide"
]

# Ensure active_module is valid
if st.session_state.active_module not in NAV_MODULES:
    st.session_state.active_module = NAV_MODULES[2]

current_nav_idx = NAV_MODULES.index(st.session_state.active_module)

selected_module = st.radio(
    "Platform Navigation Modules",
    options=NAV_MODULES,
    index=current_nav_idx,
    horizontal=True,
    label_visibility="collapsed",
    key="top_nav_radio"
)

# Sync state if user clicked the radio
if selected_module != st.session_state.active_module:
    st.session_state.active_module = selected_module
    st.rerun()

nav_choice = st.session_state.active_module


# ==========================================
# MODULE 1: EXPLORE A PLASTIC (PLASTIC VISION)
# ==========================================
if nav_choice == "🔍 Explore a Plastic":
    st.header("🔍 Explore a Plastic — Guided Product & Markings Triage")
    st.markdown(
        "Document physical plastic items, identify visible Resin Identification Codes (SPI 1–7), "
        "and investigate candidate polymer identities in plain language before formal scientific screening."
    )

    # Scientific Limitation Notice (Mandatory)
    st.markdown("""
    <div class="earth-warning">
        <strong style="color: #79543A;">🔬 CRITICAL SCIENTIFIC NOTICE ON IMAGE-BASED RECOGNITION:</strong><br>
        A photograph alone <strong>CANNOT</strong> reliably determine exact chemical composition, polymer molecular weight,
        degree of crystallinity, plasticizer additives, or biodegradability.
        PolyTrace Bio implements a <strong>transparent guided identification workflow</strong> using user-documented clues
        (resin identification code, visible markings, tactile application). It does <strong>NOT</strong> make unverified claims of automated AI/ML vision classification.
        Always substantiate material identity with accredited laboratory respirometry reports.
    </div>
    """, unsafe_allow_html=True)

    pv_col1, pv_col2 = st.columns([1, 1])

    with pv_col1:
        st.subheader("1. Visual Product Documentation")
        image_source = st.radio("Choose Image Input Method:", ["📸 Live Camera Capture", "📂 Upload Image File"], horizontal=True)

        captured_image = None
        if image_source == "📸 Live Camera Capture":
            captured_image = st.camera_input("Capture product, resin code stamp, or packaging label:")
        else:
            captured_image = st.file_uploader("Upload product or packaging photo (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])

        if captured_image is not None:
            st.image(captured_image, caption="Documented Plastic Article Preview", use_container_width=True)

    with pv_col2:
        st.subheader("2. Physical Documentation & Markings")
        pv_name = st.text_input("Product Name or Description:", value="Clear Disposable Takeaway Article")
        pv_app = st.text_input("Intended Application / Use Case:", value="Food packaging / beverage container")

        pv_code = st.selectbox(
            "Visible Resin Identification Code (SPI Code):",
            options=list(RESIN_IDENTIFICATION_CODES.keys()),
            index=0,
            help="Check the bottom or stamp on the packaging for the chasing-arrows recycling triangle."
        )

        pv_labels = st.text_area(
            "Visible Label Text & Markings:",
            placeholder="e.g. '100% Recyclable', 'BPI Certified Commercial Compostable', 'Made from Plants', 'ASTM D6400'",
            height=70
        )

        pv_claims = st.text_input("Claimed Environmental Attribute:", placeholder="e.g. Biodegradable, Compostable, Bio-based")
        pv_supplier = st.text_input("Supplier / Brand Name (Optional):", placeholder="e.g. GreenPack Solutions")

    # Run Guided Analysis
    st.markdown("---")
    st.subheader("🔍 Guided Material Identity Triage")

    triage = analyze_vision_documentation(
        product_name=pv_name,
        intended_use=pv_app,
        resin_code_str=pv_code,
        visible_labels=pv_labels,
        product_claims=pv_claims,
        supplier_name=pv_supplier
    )

    t_col1, t_col2 = st.columns([1, 1])

    with t_col1:
        st.markdown("#### Resin Code Profile")
        r_info = triage["resin_info"]
        st.markdown(f"**Identified Polymer Family:** `{r_info['name']}`")
        st.markdown(f"**Acronym:** `{r_info['acronym']}` | **Category:** `{r_info['category']}`")
        st.info(f"**Mechanical Recycling Reality:** {r_info['recycling_status']}")
        st.warning(f"**Biodegradability Reality:** {r_info['biodegradability_reality']}")

    with t_col2:
        st.markdown("#### Clues & Substantiation Analysis")
        if triage["bioplastic_clues"]:
            st.markdown("**Bioplastic Clues Detected:**")
            for c in triage["bioplastic_clues"]:
                st.write(f"- 🌿 {c}")

        if triage["conventional_clues"]:
            st.markdown("**Conventional Polymer Clues:**")
            for cc in triage["conventional_clues"]:
                st.write(f"- ⚠️ {cc}")

        if triage["substantiation_warnings"]:
            st.markdown("**Substantiation Warnings:**")
            for sw in triage["substantiation_warnings"]:
                st.write(f"- 🚨 **{sw}**")
        else:
            st.write("✅ No blatant claim-code contradictions detected.")

        st.markdown(f"**Suggested Candidate for Screening:** `{triage['suggested_candidate']}`")

    # Action: Send to Material Screening
    st.markdown("---")
    if st.button("🚀 Transfer Findings to Biodegradability Screening", type="primary", use_container_width=True):
        candidate_name = triage["suggested_candidate"]
        st.session_state.active_material_name = f"{pv_name} ({triage['resin_info']['acronym']})"
        st.session_state.active_use = pv_app
        st.session_state.active_formulation = [
            FormulationItem(
                name=candidate_name,
                percentage=100.0,
                supplier_claim=pv_claims if pv_claims else "User-documented physical sample"
            )
        ]
        st.session_state.active_module = "🔬 Biodegradability Screening"
        st.success(f"✅ Material '{candidate_name}' transferred! Navigating to Screening...")
        st.rerun()


# ==========================================
# MODULE 2: FORMULATION LAB
# ==========================================
elif nav_choice == "🧪 Formulation Lab":
    st.header("🧪 Formulation Lab — Rapid Recipe & Notebook Intake")
    st.markdown(
        "Paste recipe notations directly from lab notebooks, spreadsheets, or supplier specifications. "
        "The deterministic parser extracts constituents, verifies mass balance, identifies unknown additives, "
        "and routes the recipe into the scientific screening engine."
    )

    # Quick sample paste buttons
    st.markdown("#### 📋 1-Click Sample Recipe Presets:")
    sample_cols = st.columns(len(SAMPLE_PASTE_FORMATS))
    for idx, (label, sample_text) in enumerate(SAMPLE_PASTE_FORMATS.items()):
        with sample_cols[idx]:
            if st.button(f"📄 {label.split(':')[0]}", key=f"sample_btn_{idx}", use_container_width=True):
                st.session_state.lab_paste_text = sample_text
                st.session_state.lab_material_name = f"Lab Formula ({label.split(':')[0]})"

    if "lab_paste_text" not in st.session_state:
        st.session_state.lab_paste_text = SAMPLE_PASTE_FORMATS["Format A: Comma-separated with %"]
    if "lab_material_name" not in st.session_state:
        st.session_state.lab_material_name = "Experimental Bio-Composite Formula #1"

    c_meta1, c_meta2 = st.columns([2, 1])
    with c_meta1:
        lab_mat_name = st.text_input("Formula or Product Identifier:", value=st.session_state.lab_material_name)
    with c_meta2:
        lab_target_env = st.selectbox(
            "Target Disposal Environment:",
            options=list(ENVIRONMENTS.keys()),
            format_func=lambda k: f"{ENVIRONMENTS[k]['name']} ({ENVIRONMENTS[k]['temp']})"
        )

    pasted_input = st.text_area(
        "Paste ingredient list below (supports CSV, tab-delimited, wt%, colon-separated, or multi-line):",
        value=st.session_state.lab_paste_text,
        height=140,
        help="Formats supported:\n- Format A: PLA, 70%\n- Format B: Ingredient, Percentage (with header)\n- Format C: PLA: 70%; talc: 20%\n- Format D: PLA 70 wt%\n- Spreadsheet tab pastes: PLA [tab] 70"
    )

    # Real-time parse execution
    parsed_result = parse_pasted_formulation(pasted_input, engine)

    # Parser diagnostics & feedback
    if not parsed_result["success"] and parsed_result.get("validation_status") == "empty":
        st.info("ℹ️ Paste an ingredient formulation above to begin parsing.")
    elif parsed_result["errors"]:
        for err in parsed_result["errors"]:
            st.error(f"❌ {err}")

    if parsed_result["warnings"]:
        for warn in parsed_result["warnings"]:
            st.warning(f"⚠️ {warn}")

    if parsed_result["items"]:
        st.markdown("### 📊 Parsed Recipe Preview & Corrections")
        st.caption("Review extracted components and categories before screening:")

        # Prepare editable preview dataframe
        preview_data = []
        for it in parsed_result["items"]:
            preview_data.append({
                "Ingredient Name": it["name"],
                "Mass %": it["percentage"] if it["percentage"] is not None else 0.0,
                "Assigned Category": it["category"],
                "Database Status": "Verified Match" if not it["is_unknown"] else "Undisclosed / Unknown"
            })

        df_preview = pd.DataFrame(preview_data)
        st.dataframe(df_preview, use_container_width=True)

        # Mass balance summary banner
        total_p = parsed_result["total_percentage"]
        if 99.0 <= total_p <= 101.0:
            st.success(f"⚖️ Mass balance validated: **{total_p}%** accounted for.")
        elif total_p < 99.0:
            st.warning(f"⚠️ Incomplete mass balance: **{total_p}%** accounted for. Missing fraction is **{parsed_result['missing_percentage']}%**.")
        else:
            st.error(f"❌ Over-reported mass balance: Total is **{total_p}%** (exceeds 100% by {parsed_result['over_percentage']}%).")

        # Optional claim & documentation expander
        with st.expander("📑 Add Supplier Claim & Test Standard (Optional)", expanded=False):
            lab_claim = st.text_input("Supplier Environmental Claim for Formula:", placeholder="e.g. 100% Soil Biodegradable Mulch")
            lab_standard = st.text_input("Cited Standard or Specification:", placeholder="e.g. EN 17033, ISO 14855, ASTM D6400")

        # Action bar
        lab_col1, lab_col2, lab_col3 = st.columns([2, 1, 1])

        with lab_col1:
            if st.button("🚀 Run Scientific Screening on Parsed Formula", type="primary", use_container_width=True):
                form_items = [
                    FormulationItem(
                        name=r["name"],
                        category=r["category"],
                        percentage=r["percentage"],
                        supplier_claim=lab_claim if lab_claim else None,
                        test_standard=lab_standard if lab_standard else None
                    )
                    for r in parsed_result["items"]
                ]

                # Run screening
                scr_res = engine.screen_formulation(form_items, lab_target_env)
                gap_res = engine.generate_green_claim_gap_report(scr_res, lab_mat_name)

                # Record real session statistics
                unknowns_in_this = sum(1 for it in scr_res["evaluated_ingredients"] if it.get("category") == "unknown")
                gaps_in_this = sum(len(cv.get("mismatches", [])) for cv in scr_res["claim_verification"])
                if scr_res["mass_validation"].get("missing_percentage", 0) > 0:
                    gaps_in_this += 1
                record_screening_stats(lab_mat_name, lab_target_env, len(form_items), unknowns_in_this, gaps_in_this)

                # Display Results
                st.markdown("---")
                st.subheader(f"Screening Result: {lab_mat_name}")

                r1, r2 = st.columns([3, 2])
                with r1:
                    st.markdown("**Screening Label:**")
                    st.markdown(get_label_badge(scr_res["formulation_label"]), unsafe_allow_html=True)
                    for rat in scr_res["rationale"]:
                        st.markdown(f"> *{rat}*")
                with r2:
                    d_comp = scr_res["doc_completeness"]
                    st.metric("Documentation Completeness", f"{d_comp['completeness_pct']}%", d_comp["level"])
                    st.progress(d_comp["completeness_pct"] / 100.0)

                # Show Gap Report
                with st.expander("📑 View Generated Green-Claim Gap Report", expanded=True):
                    st.markdown("**What Ingredients Suggest:**")
                    for s in gap_res["sections"]["1_what_ingredients_suggest"]:
                        st.write(f"- {s}")
                    st.markdown("**What Remains Unknown:**")
                    for u in gap_res["sections"]["3_what_remains_unknown"]:
                        st.write(f"- ❓ {u}")
                    st.markdown("**Documents to Request:**")
                    for d in gap_res["sections"]["4_supplier_documents_to_request"]:
                        st.write(f"- 📋 {d}")

                # Generate Passport
                lab_passport = engine.generate_material_passport(
                    material_name=lab_mat_name,
                    formulation=form_items,
                    target_env=lab_target_env,
                    screening_result=scr_res
                )
                st.session_state.latest_passport = lab_passport
                st.session_state.active_material_name = lab_mat_name
                st.session_state.active_formulation = form_items
                st.session_state.active_target_env = lab_target_env
                st.success("✅ Passport generated! Click 'Material Passport' tab above to view/export.")

        with lab_col2:
            csv_data = export_formulation_csv(parsed_result["items"])
            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name=f"{lab_mat_name.replace(' ', '_')}_formulation.csv",
                mime="text/csv",
                use_container_width=True
            )

        with lab_col3:
            json_data = export_formulation_json(parsed_result["items"], {"name": lab_mat_name, "target_env": lab_target_env})
            st.download_button(
                "📥 Download JSON",
                data=json_data,
                file_name=f"{lab_mat_name.replace(' ', '_')}_formulation.json",
                mime="application/json",
                use_container_width=True
            )


# ==========================================
# MODULE 3: BIODEGRADABILITY SCREENING
# ==========================================
elif nav_choice == "🔬 Biodegradability Screening":
    st.header("🔬 Biodegradability Screening & Claim Verification")
    st.markdown(
        "Enter chemical constituents, mass percentages, and supplier claim documentation. "
        "The engine applies conservative scientific rules to detect substantiated biodegradation, "
        "substantiation gaps, and missing documentation."
    )

    # General Information
    with st.expander("📝 Material & Application Overview", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            mat_name = st.text_input("Material / Product Trade Name:", value=st.session_state.active_material_name)
            st.session_state.active_material_name = mat_name
        with col2:
            intended_use = st.text_input("Intended Application:", value=st.session_state.active_use)
            st.session_state.active_use = intended_use
        with col3:
            intended_eol = st.text_input("Claimed End-of-Life Scenario:", value=st.session_state.active_eol)
            st.session_state.active_eol = intended_eol

        target_env = st.selectbox(
            "Target Disposal Environment for Screening:",
            options=list(ENVIRONMENTS.keys()),
            format_func=lambda k: f"{ENVIRONMENTS[k]['name']} ({ENVIRONMENTS[k]['temp']})",
            index=list(ENVIRONMENTS.keys()).index(st.session_state.active_target_env)
        )
        st.session_state.active_target_env = target_env
        st.caption(f"**Disposal context notes:** {ENVIRONMENTS[target_env]['desc']}")

    st.markdown("### 🧪 Ingredient Formulation & Evidence Intake")
    st.caption("Provide known ingredients, fractions by mass (%), supplier claims, and verifiable test standards.")

    # Known materials dropdown choices
    known_materials_list = [m["name"] for m in engine.materials_db.get("materials", [])]
    known_materials_list.append("Custom / Unknown Trade-Name Component")

    formulation_items: List[FormulationItem] = []
    current_items = st.session_state.active_formulation

    num_ingredients = st.number_input("Number of formulation ingredients:", min_value=1, max_value=8, value=len(current_items))

    for i in range(int(num_ingredients)):
        default_item = current_items[i] if i < len(current_items) else None
        st.markdown(f"#### Ingredient #{i+1}")

        with st.container():
            c1, c2, c3 = st.columns([3, 2, 2])

            with c1:
                default_name = default_item.name if default_item else known_materials_list[0]
                ing_select = st.selectbox(
                    f"Select or pick ingredient #{i+1}",
                    options=known_materials_list,
                    index=known_materials_list.index(default_name) if default_name in known_materials_list else len(known_materials_list)-1,
                    key=f"ing_select_{i}"
                )

                if ing_select == "Custom / Unknown Trade-Name Component":
                    ing_name = st.text_input(
                        f"Specify custom / proprietary constituent name #{i+1}:",
                        value=default_item.name if (default_item and default_item.name not in known_materials_list) else "Unknown Trade-Name Additive",
                        key=f"ing_custom_name_{i}"
                    )
                else:
                    ing_name = ing_select

            with c2:
                default_pct = default_item.percentage if (default_item and default_item.percentage is not None) else 0.0
                has_pct = st.checkbox(f"Provide % by mass?", value=(default_item.percentage is not None) if default_item else True, key=f"has_pct_{i}")
                if has_pct:
                    ing_pct = st.number_input(f"Mass Fraction (%) #{i+1}", min_value=0.0, max_value=100.0, value=float(default_pct), step=0.5, key=f"pct_{i}")
                else:
                    ing_pct = None

            with c3:
                mat_entry = engine.find_material(ing_name)
                auto_cat = mat_entry.get("category", "unknown") if mat_entry else "unknown"
                ing_cat = st.selectbox(
                    f"Category #{i+1}",
                    options=["biodegradable_polyester", "natural_polymer", "conventional_fossil", "mineral_filler", "organic_additive", "inorganic_pigment", "unknown"],
                    index=["biodegradable_polyester", "natural_polymer", "conventional_fossil", "mineral_filler", "organic_additive", "inorganic_pigment", "unknown"].index(auto_cat) if auto_cat in ["biodegradable_polyester", "natural_polymer", "conventional_fossil", "mineral_filler", "organic_additive", "inorganic_pigment", "unknown"] else 6,
                    key=f"cat_{i}"
                )

            with st.expander(f"📑 Verification & Evidence Details for Ingredient #{i+1} (Optional)", expanded=False):
                e1, e2 = st.columns(2)
                with e1:
                    ing_claim = st.text_input(
                        "Supplier Environmental Claim:",
                        value=default_item.supplier_claim or "" if default_item else "",
                        placeholder="e.g. 100% Home Compostable, Marine Biodegradable, Biobased",
                        key=f"claim_{i}"
                    )
                    ing_standard = st.text_input(
                        "Test Standard or Method Cited:",
                        value=default_item.test_standard or "" if default_item else "",
                        placeholder="e.g. ISO 14855, EN 13432, ASTM D6400, EN 17033, OECD 301B",
                        key=f"std_{i}"
                    )
                    ing_test_env = st.selectbox(
                        "Test Environment in Lab Report:",
                        options=["", "industrial_compost", "home_compost", "soil", "freshwater", "marine"],
                        index=["", "industrial_compost", "home_compost", "soil", "freshwater", "marine"].index(default_item.test_environment) if (default_item and default_item.test_environment in ["", "industrial_compost", "home_compost", "soil", "freshwater", "marine"]) else 0,
                        key=f"test_env_{i}"
                    )

                with e2:
                    ing_conditions = st.text_input(
                        "Test Duration & Temperature:",
                        value=default_item.test_conditions_duration or "" if default_item else "",
                        placeholder="e.g. 180 days at 58 °C",
                        key=f"cond_{i}"
                    )
                    ing_result = st.text_input(
                        "Test Result Metric:",
                        value=default_item.test_result or "" if default_item else "",
                        placeholder="e.g. 92.4% CO2 conversion; <10% on 2mm sieve",
                        key=f"res_{i}"
                    )
                    ing_cert = st.text_input(
                        "Certification / Lab Reference ID:",
                        value=default_item.certification or default_item.evidence_reference or "" if default_item else "",
                        placeholder="e.g. TÜV OK Compost Certificate #10293, Report LAB-88",
                        key=f"cert_{i}"
                    )

            formulation_items.append(
                FormulationItem(
                    name=ing_name,
                    category=ing_cat,
                    percentage=ing_pct,
                    supplier_claim=ing_claim,
                    test_standard=ing_standard,
                    test_environment=ing_test_env if ing_test_env else None,
                    test_conditions_duration=ing_conditions,
                    test_result=ing_result,
                    certification=ing_cert,
                    evidence_reference=ing_cert
                )
            )

    st.session_state.active_formulation = formulation_items

    # ------------------------------------------
    # EXECUTE SCREENING
    # ------------------------------------------
    st.markdown("---")
    st.subheader("🔍 Scientific Screening & Evidence Assessment")

    screening = engine.screen_formulation(formulation_items, target_env)
    gap_report = engine.generate_green_claim_gap_report(screening, mat_name)

    # Record real session statistics
    unknowns_count = sum(1 for it in screening["evaluated_ingredients"] if it.get("category") == "unknown")
    gaps_count = sum(len(cv.get("mismatches", [])) for cv in screening["claim_verification"])
    if screening["mass_validation"].get("missing_percentage", 0) > 0:
        gaps_count += 1
    record_screening_stats(mat_name, target_env, len(formulation_items), unknowns_count, gaps_count)

    # 1. Mass Balance Status Banner
    mass_val = screening["mass_validation"]
    if mass_val["status"] == "complete":
        st.success(f"⚖️ **Mass Balance Verified:** 100% of formulation accounted for ({mass_val['total_percentage']}%).")
    elif mass_val["status"] == "under_reported":
        st.warning(f"⚠️ **Incomplete Mass Balance:** Accounted: {mass_val['total_percentage']}%. **Unreported Fraction: {mass_val['missing_percentage']}%**. Chemical screening flags this uncharacterized fraction.")
    elif mass_val["status"] == "over_reported":
        st.error(f"❌ **Inconsistent Mass Balance:** Percentages sum to {mass_val['total_percentage']}% (exceeds 100% by {mass_val['over_percentage']}%). Please verify supplier data.")
    elif mass_val["status"] == "qualitative_only":
        st.info("ℹ️ **Qualitative Screening Only:** No percentages supplied. Evaluations represent chemical component presence only without mass-weighting.")
    elif mass_val["status"] == "inconsistent_unreported":
        st.warning(f"⚠️ **Partial Percentages:** Total is {mass_val['total_percentage']}%, but {mass_val['unreported_items_count']} ingredient(s) have unassigned percentages.")

    # 2. Executive Screening Result Cards
    col_res1, col_res2, col_res3 = st.columns([3, 2, 2])

    with col_res1:
        st.markdown("**Qualitative Biodegradability Screening Label:**")
        st.markdown(get_label_badge(screening["formulation_label"]), unsafe_allow_html=True)
        st.caption(f"Screened against: **{screening['target_environment_name']}**")
        for r in screening["rationale"]:
            st.markdown(f"> *{r}*")

    with col_res2:
        doc_comp = screening["doc_completeness"]
        st.markdown("**Documentation Completeness Index:**")
        st.metric(
            label="Completeness Level",
            value=f"{doc_comp['completeness_pct']}%",
            delta=doc_comp["level"]
        )
        st.progress(doc_comp["completeness_pct"] / 100.0)
        st.caption("Measures reporting completeness, **NOT** a biodegradability score.")

    with col_res3:
        st.markdown("**Claim Alignment Status:**")
        claims_rev = screening["claim_verification"]
        high_risk_claims = [c for c in claims_rev if c.get("risk_level") == "High"]
        med_risk_claims = [c for c in claims_rev if c.get("risk_level") == "Medium"]

        if high_risk_claims:
            st.error(f"⚠️ {len(high_risk_claims)} Substantiation Gaps Flagged")
        elif med_risk_claims:
            st.warning(f"ℹ️ {len(med_risk_claims)} Unsubstantiated Claims Detected")
        else:
            st.success("✅ Documented Claims Aligned")
        st.caption("Evaluates claim substantiation against test records.")

    # 3. Environmental Cross-Compatibility Matrix
    st.markdown("### 🌐 Environmental Cross-Compatibility Matrix")
    st.caption("How this formulation behaves across all disposal environments (reveals why industrial compostables fail in nature):")

    env_cols = st.columns(len(screening["environment_matrix"]))
    for idx, (env_k, env_data) in enumerate(screening["environment_matrix"].items()):
        with env_cols[idx]:
            is_active = (env_k == target_env)
            box_style = "border: 2px solid #183D2B; background-color: #E2EBE0;" if is_active else "border: 1px solid #C4D7BE; background-color: #EEF3EC;"
            st.markdown(f"""
            <div style="{box_style} padding: 10px; border-radius: 8px; text-align: center; min-height: 140px;">
                <div style="font-size: 0.85em; font-weight: bold; color: #183D2B; margin-bottom: 4px;">{env_data['name']}</div>
                <div style="font-size: 0.75em; color: #79543A; margin-bottom: 8px;">{ENVIRONMENTS[env_k]['temp']}</div>
                {get_label_badge(env_data['label'])}
                {"<div style='font-size: 0.7em; margin-top: 6px; color: #183D2B; font-weight: bold;'>[SELECTED]</div>" if is_active else ""}
            </div>
            """, unsafe_allow_html=True)

    # 4. Detailed Ingredient Breakdown Table
    st.markdown("### 📋 Component-by-Component Scientific Evidence")
    ing_rows = []
    for ing in screening["evaluated_ingredients"]:
        pct_display = f"{ing.get('percentage')}%" if ing.get("percentage") is not None else "Unspecified"
        ing_rows.append({
            "Ingredient": ing.get("name"),
            "Category": ing.get("category"),
            "Mass %": pct_display,
            "Target Env Evidence": ing.get("label"),
            "Evidence Summary": ing.get("summary"),
            "Standards Cited": ", ".join(ing.get("standards", [])) or "None",
            "Limitations / Caveats": ing.get("limitations")
        })

    df_ing = pd.DataFrame(ing_rows)
    st.dataframe(df_ing, use_container_width=True)

    # 5. Green-Claim Gap Report
    st.markdown("---")
    st.subheader("📑 Green-Claim Gap Report")
    st.markdown("Traceable supply-chain substantiation analysis linking claims to local scientific records:")

    gap_tabs = st.tabs([
        "1. Material Suggestions",
        "2. Supported Evidence",
        "3. What Remains Unknown",
        "4. Documents to Request",
        "5. Relevant Standards",
        "6. Substantiation Gaps",
        "7. Next Steps"
    ])

    sections = gap_report["sections"]

    with gap_tabs[0]:
        st.markdown("**What the chemical composition suggests:**")
        for it in sections["1_what_ingredients_suggest"]:
            st.markdown(f"- {it}")

    with gap_tabs[1]:
        st.markdown("**What is substantiated by local evidence records:**")
        for it in sections["2_what_is_supported"]:
            st.markdown(f"- ✅ {it}")

    with gap_tabs[2]:
        st.markdown("**What remains unknown or unverified:**")
        for it in sections["3_what_remains_unknown"]:
            st.markdown(f"- ❓ {it}")

    with gap_tabs[3]:
        st.markdown("**Official supplier documentation that should be requested:**")
        for it in sections["4_supplier_documents_to_request"]:
            st.markdown(f"- 📋 **{it}**")

    with gap_tabs[4]:
        st.markdown("**Applicable test standards and scope:**")
        st.info(sections["5_relevant_test_environment"])

    with gap_tabs[5]:
        st.markdown("**Unverified claims & condition mismatches:**")
        for it in sections["6_unverified_claims"]:
            st.markdown(f"- ⚠️ {it}")

    with gap_tabs[6]:
        st.markdown("**Actionable supply-chain recommendations:**")
        for idx, it in enumerate(sections["7_recommended_next_steps"], 1):
            st.markdown(f"**{idx}.** {it}")

    # Action bar
    st.markdown("---")
    c_act1, c_act2 = st.columns(2)
    with c_act1:
        if st.button("🚀 Generate Digital Material Passport", type="primary", use_container_width=True):
            passport = engine.generate_material_passport(
                material_name=mat_name,
                formulation=formulation_items,
                target_env=target_env,
                intended_use=intended_use,
                intended_eol=intended_eol,
                screening_result=screening
            )
            st.session_state.latest_passport = passport
            st.session_state.active_module = "📋 Material Passport"
            st.success("✅ Digital Material Passport generated! Navigating to Passport view...")
            st.rerun()
    with c_act2:
        screening_json = json.dumps(screening, indent=2, default=str)
        st.download_button(
            label="💾 Download Screening Result (JSON)",
            data=screening_json,
            file_name=f"PolyTrace_Screening_{mat_name.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )


# ==========================================
# MODULE 4: COMPARE MATERIALS
# ==========================================
elif nav_choice == "⚖️ Compare Materials":
    st.header("⚖️ Material Comparison & Trade-Off Matrix")
    st.markdown(
        "Compare 2 or 3 material formulations side-by-side across multidimensional scientific criteria. "
        "PolyTrace Bio deliberately avoids a single arbitrary ranking number, allowing supply chain engineers to inspect real trade-offs."
    )

    cmp_col1, cmp_col2 = st.columns([1, 1])
    with cmp_col1:
        mat1_choice = st.selectbox(
            "Select Material 1:",
            list(sample_materials.keys()),
            index=0
        )
    with cmp_col2:
        mat2_choice = st.selectbox(
            "Select Material 2:",
            list(sample_materials.keys()),
            index=1
        )

    include_third = st.checkbox("Include 3rd Material for Comparison?")
    mat3_choice = None
    if include_third:
        mat3_choice = st.selectbox(
            "Select Material 3:",
            list(sample_materials.keys()),
            index=3
        )

    cmp_env = st.selectbox(
        "Benchmark against Disposal Environment:",
        options=list(ENVIRONMENTS.keys()),
        format_func=lambda k: f"{ENVIRONMENTS[k]['name']} ({ENVIRONMENTS[k]['temp']})"
    )

    mats_to_compare = [sample_materials[mat1_choice], sample_materials[mat2_choice]]
    if mat3_choice:
        mats_to_compare.append(sample_materials[mat3_choice])

    comp_results = []
    for m in mats_to_compare:
        scr = engine.screen_formulation(m["formulation"], cmp_env)
        comp_results.append({
            "name": m["name"],
            "screening": scr,
            "formulation": m["formulation"]
        })

    st.markdown("### 📊 Side-by-Side Scientific Matrix")

    cols = st.columns(len(comp_results))
    for idx, c_res in enumerate(comp_results):
        scr = c_res["screening"]
        with cols[idx]:
            st.subheader(c_res["name"])
            st.markdown(f"**Target Environment:** {ENVIRONMENTS[cmp_env]['name']}")
            st.markdown(get_label_badge(scr["formulation_label"]), unsafe_allow_html=True)
            st.markdown("---")

            doc_comp = scr["doc_completeness"]
            st.metric("Documentation Completeness", f"{doc_comp['completeness_pct']}%", doc_comp["level"])

            mass_val = scr["mass_validation"]
            st.metric("Mass Accounted For", f"{mass_val['total_percentage']}%", f"Missing: {mass_val.get('missing_percentage', 0)}%")

            unknowns = [ing for ing in scr["evaluated_ingredients"] if ing.get("category") == "unknown"]
            st.metric("Unknown Components", len(unknowns), "Precautionary Risk" if unknowns else "Clean Disclosure")

            st.markdown("#### 🔄 Cross-Environment Compatibility")
            for ek, ev_res in scr["environment_matrix"].items():
                short_name = ev_res["name"].split()[0]
                status_icon = "✅" if ev_res["label"] == LABEL_SUPPORTS else ("⚠️" if ev_res["label"] == LABEL_LIMITED else ("❌" if ev_res["label"] == LABEL_LOW else "❓"))
                st.write(f"- {status_icon} **{short_name}**: {ev_res['label'].split()[0]}")

            st.markdown("#### 📑 Substantiation Gaps")
            mismatches = []
            for cv in scr["claim_verification"]:
                mismatches.extend(cv.get("mismatches", []))
            if mismatches:
                for mis in mismatches[:2]:
                    st.caption(f"⚠️ {mis}")
            else:
                st.caption("✅ No evidence-claim mismatches detected.")

    st.markdown("---")
    st.markdown("### 💡 Scientific Trade-Off Takeaways")
    st.info(
        "**Key Decision-Support Insight:** Notice that no single material is universally 'the greenest'. "
        "A PLA cup lining excels in industrial composting facilities but persists in soil and marine waters. "
        "Conversely, agricultural PBAT mulch films are engineered for ambient soil assimilation, whereas conventional PE bags with pro-degradants cause persistent microplastic accumulation."
    )


# ==========================================
# MODULE 5: MATERIAL PASSPORT
# ==========================================
elif nav_choice == "📋 Material Passport":
    st.header("📋 Digital Material Passport")
    st.markdown(
        "A verifiable material passport documenting formulation, mass balance, screening classification, "
        "evidence completeness, and green-claim substantiation gaps."
    )

    passport = st.session_state.latest_passport

    if passport is None:
        st.info("ℹ️ No active passport generated yet. Screening current active formulation to generate passport...")
        passport = engine.generate_material_passport(
            material_name=st.session_state.active_material_name,
            formulation=st.session_state.active_formulation,
            target_env=st.session_state.active_target_env,
            intended_use=st.session_state.active_use,
            intended_eol=st.session_state.active_eol
        )
        st.session_state.latest_passport = passport

    p_col1, p_col2 = st.columns([3, 1])
    with p_col1:
        st.subheader(f"Material: {passport.get('material_name')}")
        st.markdown(f"**Passport ID:** `{passport.get('passport_id')}` | **Generated:** {passport.get('timestamp')}")
        st.markdown(f"**Intended Application:** {passport.get('intended_use')}")
        st.markdown(f"**Claimed End-of-Life:** {passport.get('intended_end_of_life')}")
    with p_col2:
        qr_b64 = passport.get("qr_code_base64")
        if qr_b64:
            st.image(qr_b64, width=140, caption="Local Offline QR Identifier")
            st.caption("⚠️ Encodes local record ID. Not an external URL.")

    st.markdown("---")

    p_tab1, p_tab2, p_tab3 = st.tabs(["📊 Passport Summary", "📑 Human-Readable Report (Markdown)", "💾 Machine-Readable JSON"])

    with p_tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Screening Evaluation")
            st.markdown(f"- **Target Environment:** {passport.get('target_environment_screened')}")
            st.markdown(f"- **Qualitative Screening:** {get_label_badge(passport.get('screening_classification'))}", unsafe_allow_html=True)
            doc_comp = passport.get("documentation_completeness", {})
            st.markdown(f"- **Documentation Completeness:** {doc_comp.get('completeness_pct')}% ({doc_comp.get('level')})")
        with c2:
            st.markdown("#### Mass Balance Validation")
            mv = passport.get("mass_validation", {})
            st.markdown(f"- **Status:** {mv.get('status')}")
            st.markdown(f"- **Total Accounted:** {mv.get('total_percentage')}%")
            if mv.get("missing_percentage", 0) > 0:
                st.markdown(f"- **Unreported / Missing:** {mv.get('missing_percentage')}%")

        st.markdown("#### Formulation Components")
        st.table(pd.DataFrame(passport.get("formulation", []))[["name", "category", "percentage", "supplier_claim", "test_standard"]])

        st.markdown("#### Traceable Green-Claim Gap Report")
        gap = passport.get("gap_report", {}).get("sections", {})
        st.markdown("**What Ingredients Suggest:**")
        for it in gap.get("1_what_ingredients_suggest", []):
            st.write(f"- {it}")

        st.markdown("**Substantiation Gaps:**")
        for it in gap.get("6_unverified_claims", []):
            st.write(f"- ⚠️ {it}")

        st.markdown("**Recommended Next Verification Steps:**")
        for it in gap.get("7_recommended_next_steps", []):
            st.write(f"- 📋 {it}")

    with p_tab2:
        md_content = engine.export_passport_markdown(passport)
        st.text_area("Markdown Report Preview:", value=md_content, height=360)
        st.download_button(
            label="📥 Download Markdown Report (.md)",
            data=md_content,
            file_name=f"Passport_{passport.get('passport_id')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with p_tab3:
        json_content = json.dumps(passport, indent=2, default=str)
        st.text_area("JSON Payload Preview:", value=json_content, height=360)
        st.download_button(
            label="📥 Download JSON Passport (.json)",
            data=json_content,
            file_name=f"Passport_{passport.get('passport_id')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("---")
    st.caption(f"**Legal & Scientific Disclaimer:** {passport.get('disclaimer')}")


# ==========================================
# MODULE 6: METHODOLOGY & SCIENCE GUIDE
# ==========================================
elif nav_choice == "📖 Methodology & Science Guide":
    st.header("📖 Scientific Methodology & Decision Guide")
    st.markdown(
        "PolyTrace Bio is built on strict polymer physics, biochemistry, and international standards. "
        "Here are the non-negotiable scientific distinctions required for truthful environmental claims."
    )

    t1, t2, t3 = st.tabs(["🔬 The 6 Fundamental Distinctions", "📑 International Standards Framework", "🧪 Common Greenwashing Traps"])

    with t1:
        st.subheader("Why These Properties Are NOT Interchangeable:")

        st.markdown("""
        ### 1. Biodegradability vs Disintegration
        - **Disintegration** is a physical phenomenon: the material breaks down into pieces smaller than 2mm.
        - **Biodegradation** is a biochemical phenomenon: microorganisms convert organic carbon into carbon dioxide (CO2), water, and cellular biomass via cellular respiration.
        - ⚠️ *Danger:* Physical disintegration without microbial assimilation produces millions of invisible microplastics.

        ### 2. Industrial Compostability vs Home Compostability
        - **Industrial Composting (ISO 14855, EN 13432):** Operates at thermophilic temperatures (**≥ 58 °C**) with managed turning and moisture.
        - **Home Composting (NF T51-800, AS 5810):** Operates at ambient temperatures (**20 - 30 °C**).
        - ⚠️ *Danger:* Polylactic Acid (PLA) degrades readily at 58 °C (above its glass transition temperature), but remains essentially intact for years in a backyard home compost heap.

        ### 3. Open Environmental Biodegradation (Soil & Marine)
        - Open natural environments have low microbial densities and low ambient temperatures.
        - Marine pelagic environments have mean temperatures < 15 °C (deep ocean ~ 2-4 °C) with limited nutrients.
        - Almost no industrial compostable bioplastics degrade in the marine environment (with the notable exception of PHAs and natural cellulose).

        ### 4. Recyclability vs Compostability
        - Conventional recycling relies on thermoplastic mechanical re-melting (PET, HDPE, PP).
        - Compostable polymers (PLA, PBAT, TPS) act as **severe contaminants** in mechanical recycling streams. PLA in PET recycling causes haze and catastrophic polymer chain degradation at PET processing temperatures (260 °C).

        ### 5. Environmental Ecotoxicity
        - A material cannot be declared environmentally safe simply because it disappears.
        - EN 13432 and EN 17033 mandate strict terrestrial ecotoxicity testing: plant germination rates (OECD 208) must exceed 90% of blank compost, earthworm toxicity must be evaluated, and heavy metal concentrations must be strictly limited.
        """)

    with t2:
        st.subheader("Key International Standards & Specifications")

        st_data = []
        for s in engine.evidence_db.get("standards", []):
            st_data.append({
                "Standard": s.get("code"),
                "Scope": s.get("scope"),
                "Environment": s.get("environment"),
                "Temperature": s.get("temperature_celsius"),
                "Duration": f"{s.get('typical_duration_days')} days",
                "Key Pass Criterion": s.get("criterion")
            })

        st.dataframe(pd.DataFrame(st_data), use_container_width=True)

        st.markdown("#### Peer-Reviewed Scientific Foundations")
        for lit in engine.evidence_db.get("literature", []):
            st.markdown(f"- **{lit.get('citation')}**")
            st.caption(f"Key Finding: {lit.get('finding')}")

    with t3:
        st.subheader("Common Greenwashing Traps Detected by PolyTrace Bio")

        st.markdown("""
        1. **The 'Bio-based = Biodegradable' Fallacy:**
           - *The Trap:* A supplier claims a bottle is "eco-friendly and biodegradable" because it is bio-based (from sugarcane).
           - *The Reality:* Bio-PE (bio-polyethylene) and Bio-PET are made from bio-ethylene, but their chemical structure is 100% identical to fossil polyolefins. They do not biodegrade.
           - *The Standard:* ASTM D6866 confirms bio-based carbon fraction via radiocarbon (C14) dating, but provides zero proof of biodegradability.

        2. **The 'Degradable / Oxo-degradable' Microplastic Scam:**
           - *The Trap:* Conventional PE or PP bags with added transition metal salts (cobalt, manganese) labeled "d2w" or "oxo-biodegradable".
           - *The Reality:* Sunlight and heat induce abiotic polymer fragmentation into microscopic synthetic dust. Microbes cannot mineralize the recalcitrant polyolefin backbone.
           - *Regulatory Status:* **Banned across the European Union under Directive (EU) 2019/904.**

        3. **The Unqualified '100% Biodegradable' Claim:**
           - *The Trap:* Claiming "biodegradable" without specifying environment (compost vs soil vs marine) or timeframe.
           - *The Reality:* Everything decomposes over geologic time. Unqualified claims mislead consumers into believing items can be littered safely.
        """)

# Footer
st.markdown("---")
foot_c1, foot_c2 = st.columns([2, 1])
with foot_c1:
    st.caption(
        "PolyTrace Bio • Scientific Decision-Support Platform for the Sustainable Supply Chains Track • "
        "Adhering to ISO 14855, EN 13432, EN 17033, and ASTM D6400 methodologies."
    )
with foot_c2:
    if st.button("📖 Read Scientific Methodology Guide", key="btn_footer_methodology", use_container_width=True):
        st.session_state.active_module = "📖 Methodology & Science Guide"
        st.rerun()
