"""
PolyTrace Bio — Plastic Vision Module
=====================================
Guided material identity documentation and preliminary triage for plastic articles.

CRITICAL SCIENTIFIC LIMITATION:
A photograph alone CANNOT determine exact chemical composition, polymer molecular weight,
degree of crystallinity, plasticizer additives, or biodegradability.
This module provides transparent guided triage based on user-documented physical clues
(resin identification codes, visible markings, physical application), NOT unverified AI/ML recognition.
"""

from typing import Dict, Any, List, Optional


RESIN_IDENTIFICATION_CODES = {
    "1 PET": {
        "code": 1,
        "name": "Polyethylene Terephthalate (PET)",
        "acronym": "PET",
        "matched_id": "pet",
        "category": "conventional_fossil",
        "recycling_status": "Widely mechanically recycled (Code 1 curbside).",
        "biodegradability_reality": "Non-biodegradable in natural environments or composting. Recalcitrant aromatic ester backbone.",
        "common_uses": "Beverage bottles, clamshell containers, food trays, polyester fibers."
    },
    "2 HDPE": {
        "code": 2,
        "name": "High-Density Polyethylene (HDPE)",
        "acronym": "PE",
        "matched_id": "pe",
        "category": "conventional_fossil",
        "recycling_status": "Widely mechanically recycled (Code 2).",
        "biodegradability_reality": "Non-biodegradable. Durable aliphatic C-C backbone; persists for centuries.",
        "common_uses": "Milk jugs, detergent bottles, shampoo containers, plastic lumber."
    },
    "3 PVC": {
        "code": 3,
        "name": "Polyvinyl Chloride (PVC)",
        "acronym": "PVC",
        "matched_id": "pvc",
        "category": "conventional_fossil",
        "recycling_status": "Rarely mechanically recycled in municipal streams; severe contaminant in PET/PE streams.",
        "biodegradability_reality": "Non-biodegradable. High ecotoxicity risk from phthalate plasticizers and organotins.",
        "common_uses": "Pipes, blister packaging, medical tubing, vinyl banners, construction films."
    },
    "4 LDPE": {
        "code": 4,
        "name": "Low-Density Polyethylene (LDPE / LLDPE)",
        "acronym": "PE",
        "matched_id": "pe",
        "category": "conventional_fossil",
        "recycling_status": "Recyclable in dedicated flexible film streams (Code 4 drop-offs).",
        "biodegradability_reality": "Non-biodegradable. Abiotically fragments into microplastics under solar UV, but does not mineralize.",
        "common_uses": "Shopping bags, squeeze bottles, agricultural mulch, bubble wrap."
    },
    "5 PP": {
        "code": 5,
        "name": "Polypropylene (PP)",
        "acronym": "PP",
        "matched_id": "pp",
        "category": "conventional_fossil",
        "recycling_status": "Mechanically recycled (Code 5 food containers).",
        "biodegradability_reality": "Non-biodegradable. Resistant aliphatic carbon backbone.",
        "common_uses": "Bottle caps, takeout food containers, yogurt cups, microwaveable trays, woven sacks."
    },
    "6 PS": {
        "code": 6,
        "name": "Polystyrene (PS / EPS)",
        "acronym": "PS",
        "matched_id": "ps",
        "category": "conventional_fossil",
        "recycling_status": "Economically difficult to recycle due to low density of foam.",
        "biodegradability_reality": "Non-biodegradable. Fragments into persistent microplastic beads in aquatic ecosystems.",
        "common_uses": "Disposable cutlery, foam takeaway clamshells, hot drink cup lids, protective foam packaging."
    },
    "7 Other / Mixed / Unknown": {
        "code": 7,
        "name": "Other / Mixed Resins / Bioplastics",
        "acronym": "Other",
        "matched_id": None,
        "category": "mixed_or_bioplastic",
        "recycling_status": "Usually non-recyclable in conventional curbside collection (Code 7 catch-all).",
        "biodegradability_reality": "CRITICAL DUALITY: Code 7 contains BOTH non-biodegradable multi-layer laminates (e.g. Nylon/PE, Polycarbonate) AND certified bioplastics (PLA, PHA, PBAT, PBS). The resin number alone CANNOT confirm biodegradability without verified third-party laboratory certification.",
        "common_uses": "Multi-layer barrier packaging, 3D printing filaments, PLA bio-cups, PHA straws, specialty engineering resins."
    },
    "No code visible": {
        "code": None,
        "name": "Unmarked Plastic / Unknown Polymer",
        "acronym": "Unknown",
        "matched_id": "unknown_additive",
        "category": "unknown",
        "recycling_status": "Rejected by optical sorting facilities or classified as residual waste.",
        "biodegradability_reality": "Unverified. Without chemical testing (FTIR / DSC), chemical composition and environmental fate cannot be assumed.",
        "common_uses": "Unbranded disposable items, unlabelled films, imported packaging."
    }
}


def analyze_vision_documentation(
    product_name: str,
    intended_use: str,
    resin_code_str: str,
    visible_labels: str,
    product_claims: str,
    supplier_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Produce a transparent guided triage report from user-documented image features.
    Explicitly refrains from claiming automated AI vision.
    """
    resin_info = RESIN_IDENTIFICATION_CODES.get(resin_code_str, RESIN_IDENTIFICATION_CODES["No code visible"])
    matched_id = resin_info.get("matched_id")

    # Clues analysis
    labels_lower = (visible_labels or "").lower()
    claims_lower = (product_claims or "").lower()

    bioplastic_clues = []
    conventional_clues = []
    substantiation_warnings = []

    # Check for bioplastic keywords in text
    bioplastic_keywords = ["compostable", "biodegradable", "pla", "pha", "pbat", "biobased", "plant-based", "en 13432", "astm d6400", "ok compost"]
    for kw in bioplastic_keywords:
        if kw in labels_lower or kw in claims_lower:
            bioplastic_clues.append(f"Visible text mentions '{kw}'.")

    # Check resin code compatibility
    if resin_info["code"] in [1, 2, 3, 4, 5, 6]:
        conventional_clues.append(f"Resin code #{resin_info['code']} ({resin_info['name']}) indicates a conventional petroleum-derived polymer family.")
        if bioplastic_clues:
            substantiation_warnings.append(
                f"Severe Claim Mismatch: Article exhibits conventional resin code #{resin_info['code']} ({resin_info['name']}), "
                f"yet user notes claims of biodegradability/compostability. Conventional polyolefins and styrenics do not mineralize."
            )
    elif resin_info["code"] == 7:
        if bioplastic_clues:
            bioplastic_clues.append("Resin Code 7 ('Other') is the standard SPI category used for bioplastics (PLA, PHA, PBAT, TPS blends).")
        else:
            substantiation_warnings.append(
                "Resin Code 7 without verified compostability certification could indicate non-biodegradable multi-layer packaging (e.g. PET/EVOH/PE)."
            )
    else:
        substantiation_warnings.append(
            "Article lacks a visible resin identification code. Optical sorting machines and recycling facilities will reject this item."
        )

    # Candidate suggested screening material
    suggested_candidate = None
    if resin_info["code"] == 1:
        suggested_candidate = "Polyethylene Terephthalate (PET)"
    elif resin_info["code"] in [2, 4]:
        suggested_candidate = "Polyethylene (PE: LDPE / LLDPE / HDPE)"
    elif resin_info["code"] == 3:
        suggested_candidate = "Polyvinyl Chloride (PVC)"
    elif resin_info["code"] == 5:
        suggested_candidate = "Polypropylene (PP)"
    elif resin_info["code"] == 6:
        suggested_candidate = "Polystyrene (PS / EPS)"
    elif resin_info["code"] == 7:
        if "pla" in labels_lower or "pla" in claims_lower or "corn" in labels_lower:
            suggested_candidate = "Polylactic Acid (PLA)"
        elif "pha" in labels_lower or "phb" in labels_lower or "marine" in claims_lower:
            suggested_candidate = "Polyhydroxyalkanoates (PHA: PHB / PHBV)"
        elif "mulch" in intended_use.lower() or "bag" in intended_use.lower() or "pbat" in labels_lower:
            suggested_candidate = "Polybutylene Adipate Terephthalate (PBAT)"
        else:
            suggested_candidate = "Unknown Trade-Name Additive / Proprietary Masterbatch"
    else:
        suggested_candidate = "Unknown Trade-Name Additive / Proprietary Masterbatch"

    return {
        "product_name": product_name or "Unlabeled Plastic Article",
        "intended_use": intended_use or "Unspecified Application",
        "resin_code_str": resin_code_str,
        "resin_info": resin_info,
        "suggested_candidate": suggested_candidate,
        "bioplastic_clues": bioplastic_clues,
        "conventional_clues": conventional_clues,
        "substantiation_warnings": substantiation_warnings,
        "scientific_disclaimer": (
            "CRITICAL SCIENTIFIC NOTICE: Visual inspection and resin identification numbers are preliminary screening clues. "
            "They do NOT constitute analytical laboratory confirmation (such as FTIR spectroscopy, differential scanning calorimetry, "
            "or isotopic radiocarbon analysis). Always verify with accredited laboratory respirometry reports."
        )
    }
