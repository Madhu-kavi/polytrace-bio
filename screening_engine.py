"""
PolyTrace Bio - Scientific Screening Engine
===========================================
Core scientific evaluation logic decoupled from the Streamlit user interface.
Handles:
- Ingredient and material database lookups
- Formulation percentage and mass-balance validation
- Environment-specific qualitative screening
- Supplier claim verification and substantiation gap analysis
- Green-Claim Gap Report generation
- Digital Material Passport generation (JSON, Markdown, QR code)
- Multi-material comparative trade-off matrix
"""

import json
import os
import uuid
import datetime
import io
import base64
from typing import Dict, List, Optional, Any, Tuple


# Standard environment keys supported by the engine
ENVIRONMENTS = {
    "industrial_compost": {
        "name": "Industrial Composting",
        "temp": "≥ 58 °C (Thermophilic)",
        "desc": "Controlled commercial/municipal facility with elevated temperature, active aeration, and regulated moisture.",
        "primary_standards": ["ISO 14855", "EN 13432", "ASTM D6400"]
    },
    "home_compost": {
        "name": "Home Composting",
        "temp": "20 - 30 °C (Mesophilic/Ambient)",
        "desc": "Ambient, variable backyard compost heap with lower heat accumulation and variable microflora.",
        "primary_standards": ["NF T51-800", "AS 5810"]
    },
    "soil": {
        "name": "Agricultural / Natural Soil",
        "temp": "15 - 25 °C (Ambient)",
        "desc": "Open soil burial environment; critical for agricultural mulch films and ground contact articles.",
        "primary_standards": ["EN 17033", "ISO 17556"]
    },
    "freshwater": {
        "name": "Freshwater Aquatic",
        "temp": "15 - 22 °C (Ambient)",
        "desc": "Aerobic natural rivers, lakes, and reservoirs; lower microbial density than soil or compost.",
        "primary_standards": ["ISO 14851", "ISO 14852"]
    },
    "marine": {
        "name": "Marine Seawater / Pelagic",
        "temp": "10 - 20 °C (Coastal/Pelagic)",
        "desc": "Saline pelagic or benthic marine water; cold, low-nutrient (oligotrophic), specialized biofilms.",
        "primary_standards": ["ISO 22403", "ASTM D6691"]
    }
}

# The 4 strictly defined qualitative labels required by the specification
LABEL_SUPPORTS = "Evidence supports biodegradation under the specified conditions"
LABEL_LIMITED = "Limited or condition-specific evidence"
LABEL_INSUFFICIENT = "Insufficient evidence"
LABEL_LOW = "Evidence indicates low biodegradation under the specified conditions"


def get_base_dir() -> str:
    """Return the absolute path of the directory hosting this script."""
    return os.path.dirname(os.path.abspath(__file__))


def load_material_database(filepath: Optional[str] = None) -> Dict[str, Any]:
    """Load curated material database from JSON file."""
    if filepath is None:
        filepath = os.path.join(get_base_dir(), "material_data.json")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Material database not found at {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_evidence_sources(filepath: Optional[str] = None) -> Dict[str, Any]:
    """Load curated standards, certifications, and literature sources."""
    if filepath is None:
        filepath = os.path.join(get_base_dir(), "evidence_sources.json")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Evidence sources not found at {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


class FormulationItem:
    """Represents an individual ingredient or component in a material formulation."""

    def __init__(
        self,
        name: str,
        category: str = "auto",
        percentage: Optional[float] = None,
        supplier_claim: Optional[str] = None,
        test_standard: Optional[str] = None,
        test_environment: Optional[str] = None,
        test_conditions_duration: Optional[str] = None,
        test_result: Optional[str] = None,
        certification: Optional[str] = None,
        evidence_reference: Optional[str] = None,
        thickness_microns: Optional[float] = None
    ):
        self.name = name.strip() if name else "Unknown Component"
        self.category = category
        self.percentage = float(percentage) if percentage is not None else None
        self.supplier_claim = supplier_claim.strip() if supplier_claim else None
        self.test_standard = test_standard.strip() if test_standard else None
        self.test_environment = test_environment.strip() if test_environment else None
        self.test_conditions_duration = test_conditions_duration.strip() if test_conditions_duration else None
        self.test_result = test_result.strip() if test_result else None
        self.certification = certification.strip() if certification else None
        self.evidence_reference = evidence_reference.strip() if evidence_reference else None
        self.thickness_microns = float(thickness_microns) if thickness_microns is not None else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "percentage": self.percentage,
            "supplier_claim": self.supplier_claim,
            "test_standard": self.test_standard,
            "test_environment": self.test_environment,
            "test_conditions_duration": self.test_conditions_duration,
            "test_result": self.test_result,
            "certification": self.certification,
            "evidence_reference": self.evidence_reference,
            "thickness_microns": self.thickness_microns
        }


class ScreeningEngine:
    """Scientific decision-support and screening engine for polymers and bioplastics."""

    def __init__(self, data_path: Optional[str] = None, evidence_path: Optional[str] = None):
        self.materials_db = load_material_database(data_path)
        self.evidence_db = load_evidence_sources(evidence_path)
        self._build_indexes()

    def _build_indexes(self):
        """Build normalized lookup indexes for rapid, flexible ingredient matching."""
        self.by_id: Dict[str, Dict[str, Any]] = {}
        self.by_name_or_synonym: Dict[str, Dict[str, Any]] = {}

        for mat in self.materials_db.get("materials", []):
            mat_id = mat.get("id", "").lower().strip()
            self.by_id[mat_id] = mat

            name_norm = mat.get("name", "").lower().strip()
            self.by_name_or_synonym[name_norm] = mat

            for syn in mat.get("synonyms", []):
                self.by_name_or_synonym[syn.lower().strip()] = mat

    def find_material(self, query: str) -> Optional[Dict[str, Any]]:
        """Look up material entry by ID, exact name, or synonym (case-insensitive)."""
        if not query:
            return None
        q = query.strip().lower()

        # Direct ID match
        if q in self.by_id:
            return self.by_id[q]

        # Exact synonym or name match
        if q in self.by_name_or_synonym:
            return self.by_name_or_synonym[q]

        # Explicit acronym map
        acronym_map = {
            "pe": "pe", "ldpe": "pe", "hdpe": "pe", "lldpe": "pe",
            "pp": "pp", "pet": "pet", "ps": "ps", "eps": "ps",
            "pvc": "pvc", "pla": "pla", "pha": "pha", "phb": "pha",
            "phbv": "pha", "pbat": "pbat", "pbs": "pbs", "tps": "tps",
            "starch": "tps", "cellophane": "cellulose", "cellulose": "cellulose",
            "caco3": "caco3", "talc": "talc", "atbc": "atbc",
            "tio2": "tio2", "carbon black": "carbon_black"
        }
        if q in acronym_map:
            mapped_id = acronym_map[q]
            return self.by_id.get(mapped_id)

        # Exact token match inside parentheses or delimiters, e.g. "Polyethylene (PE)"
        for mat in self.materials_db.get("materials", []):
            syns = [s.lower() for s in mat.get("synonyms", [])]
            if q in syns:
                return mat

        # Normalized query substring only when query is a substantive phrase (length >= 4)
        # Avoid short substring false positives (e.g. 'ca' in 'chemical')
        for key, entry in self.by_name_or_synonym.items():
            if len(key) >= 4 and len(q) >= 4:
                # Query matches key directly or key is a full word in query
                words_in_q = q.replace("(", " ").replace(")", " ").replace("/", " ").replace("-", " ").split()
                if key in words_in_q or q in key:
                    return entry

        return None

    def validate_mass_balance(self, items: List[FormulationItem]) -> Dict[str, Any]:
        """
        Validate formulation percentages.
        Checks if percentages sum to ~100%, flags missing, inconsistent, or unreported fractions.
        Does NOT automatically fill missing fractions.
        """
        items_with_pct = [it for it in items if it.percentage is not None]
        items_without_pct = [it for it in items if it.percentage is None]

        if not items:
            return {
                "valid": False,
                "status": "empty",
                "total_percentage": 0.0,
                "missing_percentage": 100.0,
                "over_percentage": 0.0,
                "unreported_items_count": 0,
                "message": "Formulation is empty. Please add at least one ingredient."
            }

        if len(items_with_pct) == 0:
            return {
                "valid": True,
                "status": "qualitative_only",
                "total_percentage": 0.0,
                "missing_percentage": 100.0,
                "over_percentage": 0.0,
                "unreported_items_count": len(items_without_pct),
                "message": "No ingredient percentages supplied. Screening performed on qualitative formulation presence only."
            }

        total_pct = round(sum(it.percentage for it in items_with_pct), 2)
        unreported_count = len(items_without_pct)

        if 99.0 <= total_pct <= 101.0:
            if unreported_count == 0:
                return {
                    "valid": True,
                    "status": "complete",
                    "total_percentage": total_pct,
                    "missing_percentage": 0.0,
                    "over_percentage": 0.0,
                    "unreported_items_count": 0,
                    "message": f"Formulation mass balance verified: {total_pct}% accounted for."
                }
            else:
                return {
                    "valid": False,
                    "status": "inconsistent_unreported",
                    "total_percentage": total_pct,
                    "missing_percentage": 0.0,
                    "over_percentage": 0.0,
                    "unreported_items_count": unreported_count,
                    "message": f"Percentages total {total_pct}%, but {unreported_count} ingredient(s) have unassigned percentages."
                }
        elif total_pct < 99.0:
            missing = round(100.0 - total_pct, 2)
            return {
                "valid": False,
                "status": "under_reported",
                "total_percentage": total_pct,
                "missing_percentage": missing,
                "over_percentage": 0.0,
                "unreported_items_count": unreported_count,
                "message": f"Formulation incomplete: total accounts for only {total_pct}%. Missing/unreported fraction is {missing}%."
            }
        else:
            over = round(total_pct - 100.0, 2)
            return {
                "valid": False,
                "status": "over_reported",
                "total_percentage": total_pct,
                "missing_percentage": 0.0,
                "over_percentage": over,
                "unreported_items_count": unreported_count,
                "message": f"Inconsistent formulation: total percentages sum to {total_pct}% (exceeds 100% by {over}%)."
            }

    def compute_documentation_completeness(self, items: List[FormulationItem], target_env: str) -> Dict[str, Any]:
        """
        Calculates Documentation Completeness Index based on provided evidence fields.
        Clearly labeled as documentation completeness, NOT a biodegradability score.
        """
        if not items:
            return {"completeness_pct": 0.0, "level": "None", "details": []}

        total_points = 0
        earned_points = 0
        details = []

        # Criteria per item:
        # 1. Ingredient identified in verified database (2 pts)
        # 2. Percentage specified (1 pt)
        # 3. Test standard documented (2 pts)
        # 4. Test environment matches target environment (2 pts)
        # 5. Test conditions/duration documented (1 pt)
        # 6. Test result / metric documented (1 pt)
        # 7. Independent certification or lab reference cited (2 pts)
        max_pts_per_item = 11

        for it in items:
            mat = self.find_material(it.name)
            pts = 0
            gaps = []

            if mat and mat.get("id") != "unknown_additive":
                pts += 2
            else:
                gaps.append("Chemical identity undisclosed or not matched in verified database")

            if it.percentage is not None:
                pts += 1
            else:
                gaps.append("Mass fraction percentage missing")

            if it.test_standard and it.test_standard.strip() and it.test_standard.lower() not in ["none", "n/a", "undocumented"]:
                pts += 2
            else:
                gaps.append("No standard test method cited (e.g., ISO, ASTM, EN)")

            if it.test_environment:
                norm_env = it.test_environment.lower().replace(" ", "_")
                if norm_env == target_env.lower().replace(" ", "_"):
                    pts += 2
                else:
                    gaps.append(f"Test environment ({it.test_environment}) does not match target environment ({target_env})")
            else:
                gaps.append("Test environment undocumented")

            if it.test_conditions_duration and it.test_conditions_duration.strip() and it.test_conditions_duration.lower() not in ["none", "n/a"]:
                pts += 1
            else:
                gaps.append("Test duration and conditions undocumented")

            if it.test_result and it.test_result.strip() and it.test_result.lower() not in ["none", "n/a"]:
                pts += 1
            else:
                gaps.append("Test result metric missing (e.g. % CO2 mineralization)")

            if (it.certification and it.certification.strip() and it.certification.lower() not in ["none", "n/a"]) or \
               (it.evidence_reference and it.evidence_reference.strip() and it.evidence_reference.lower() not in ["none", "n/a"]):
                pts += 2
            else:
                gaps.append("No third-party certification certificate or test report reference cited")

            total_points += max_pts_per_item
            earned_points += pts
            details.append({
                "ingredient": it.name,
                "earned_points": pts,
                "max_points": max_pts_per_item,
                "gaps": gaps
            })

        completeness_pct = round((earned_points / max_points) * 100, 1) if (max_points := total_points) > 0 else 0.0

        if completeness_pct >= 80:
            level = "Comprehensive"
        elif completeness_pct >= 50:
            level = "Moderate"
        elif completeness_pct >= 25:
            level = "Basic"
        else:
            level = "Minimal / Incomplete"

        return {
            "completeness_pct": completeness_pct,
            "level": level,
            "earned_points": earned_points,
            "total_points": total_points,
            "details": details,
            "disclaimer": "Documentation Completeness measures verifiable reporting thoroughness. It is NOT a biodegradability score or proof of environmental degradation."
        }

    def verify_supplier_claims(self, items: List[FormulationItem], target_env: str) -> List[Dict[str, Any]]:
        """
        Compare supplier claims with documentation and scientific evidence.
        Flags mismatches without using judgmental terms (fraud/false).
        """
        claim_reports = []

        for it in items:
            mat = self.find_material(it.name)
            claim = it.supplier_claim
            claim_text = claim.strip() if claim else "No explicit environmental claim stated"

            mismatches = []
            verified_points = []
            status = "Verified"

            # If no claim made
            if not claim or claim.lower() in ["none", "n/a", "unclaimed"]:
                claim_reports.append({
                    "ingredient": it.name,
                    "claim": "No environmental claim provided",
                    "status": "Neutral",
                    "mismatches": [],
                    "verified_points": ["No unsubstantiated claims detected."],
                    "risk_level": "Low"
                })
                continue

            claim_lower = claim.lower()

            # Check 1: Broad "Biodegradable" claim without test environment
            if "biodegradable" in claim_lower and not ("compost" in claim_lower or "soil" in claim_lower or "marine" in claim_lower):
                mismatches.append(
                    "Unqualified claim: 'Biodegradable' stated without specifying target disposal environment or test timeline."
                )

            # Check 2: Claiming compostable or biodegradable for non-degradable conventional polymers
            if mat and mat.get("category") == "conventional_fossil":
                mismatches.append(
                    f"Fundamental material mismatch: '{it.name}' possesses a non-hydrolyzable carbon-carbon backbone. "
                    "Claiming biodegradability contradicts established polymer science literature unless a fully documented novel enzymatic pathway is validated."
                )

            # Check 3: Claiming Home Compostable when evidence is only Industrial Compostable (e.g. PLA)
            if "home" in claim_lower and "compost" in claim_lower:
                if mat and mat.get("id") == "pla":
                    mismatches.append(
                        "Thermal condition mismatch: Neat PLA requires thermophilic industrial temperatures (≥58 °C) to hydrolyze. "
                        "Ambient home composting (20-30 °C) is documented to result in negligible degradation."
                    )
                if it.test_standard and "14855" in it.test_standard and not any(h in it.test_standard for h in ["51-800", "5810"]):
                    mismatches.append(
                        "Standard scope mismatch: Home compostability claimed, but cited standard (ISO 14855) is an industrial composting specification."
                    )

            # Check 4: Claiming Marine Biodegradable
            if "marine" in claim_lower or "ocean" in claim_lower or "sea" in claim_lower:
                if mat and mat.get("id") not in ["pha", "tps", "cellulose"]:
                    mismatches.append(
                        f"Marine vulnerability: Documented marine evidence for '{it.name}' indicates persistence in cold, oligotrophic seawater. "
                        "Marine claims require specific respirometry under ISO 22403 or ASTM D6691."
                    )
                if not it.test_standard or not any(m in it.test_standard for m in ["22403", "6691"]):
                    mismatches.append(
                        "Missing marine test standard: Marine biodegradability claimed without ISO 22403 or ASTM D6691 testing."
                    )

            # Check 5: Biobased vs Biodegradable confusion
            if "biobased" in claim_lower or "bio-based" in claim_lower or "plant-based" in claim_lower:
                if "biodegradable" in claim_lower or "compostable" in claim_lower:
                    if it.test_standard and "6866" in it.test_standard:
                        mismatches.append(
                            "Concept conflation: ASTM D6866 confirms bio-based carbon origin, but provides zero evidence of biodegradability. "
                            "Bio-based origin and end-of-life biodegradability are governed by distinct mechanisms."
                        )

            # Check 6: Claim made but zero evidence fields populated
            has_evidence = bool(
                (it.test_standard and it.test_standard.strip() and it.test_standard.lower() not in ["none", "n/a"]) or
                (it.certification and it.certification.strip() and it.certification.lower() not in ["none", "n/a"]) or
                (it.evidence_reference and it.evidence_reference.strip() and it.evidence_reference.lower() not in ["none", "n/a"])
            )
            if not has_evidence:
                mismatches.append(
                    "Substantiation gap: Environmental claim provided without any supporting test standard, test report, or certification certificate."
                )

            # Check 7: Target environment mismatch
            if it.test_environment and target_env:
                norm_test_env = it.test_environment.lower().replace(" ", "_")
                norm_tgt_env = target_env.lower().replace(" ", "_")
                if norm_test_env != norm_tgt_env:
                    mismatches.append(
                        f"Disposal context divergence: Supplier claim tested under '{it.test_environment}', whereas intended screening environment is '{target_env}'."
                    )

            # Determine status
            if mismatches:
                status = "Substantiation Gap / Condition Mismatch"
                risk_level = "High" if len(mismatches) >= 2 else "Medium"
            elif has_evidence:
                status = "Supported by Provided Documentation"
                verified_points.append("Claim is aligned with provided standard and documented test context.")
                risk_level = "Low"
            else:
                status = "Unsubstantiated Claim"
                risk_level = "Medium"

            claim_reports.append({
                "ingredient": it.name,
                "claim": claim_text,
                "status": status,
                "mismatches": mismatches,
                "verified_points": verified_points,
                "risk_level": risk_level
            })

        return claim_reports

    def screen_formulation(self, items: List[FormulationItem], target_env: str) -> Dict[str, Any]:
        """
        Evaluate a complete formulation against the selected target disposal environment.
        Applies transparent, deterministic scientific rules.
        """
        if target_env not in ENVIRONMENTS:
            raise ValueError(f"Unknown target environment: '{target_env}'. Must be one of {list(ENVIRONMENTS.keys())}")

        mass_validation = self.validate_mass_balance(items)
        doc_completeness = self.compute_documentation_completeness(items, target_env)
        claim_verification = self.verify_supplier_claims(items, target_env)

        evaluated_ingredients = []
        has_conventional_polymer = False
        has_unknown_ingredient = False
        has_conditional_biopolymer = False
        all_biodegradable_in_env = True
        total_conventional_pct = 0.0
        total_unknown_pct = 0.0

        for it in items:
            mat = self.find_material(it.name)
            pct = it.percentage if it.percentage is not None else 0.0

            if not mat or mat.get("id") == "unknown_additive":
                # Unknown ingredient
                has_unknown_ingredient = True
                total_unknown_pct += pct
                all_biodegradable_in_env = False
                eval_item = {
                    "name": it.name,
                    "matched_id": "unknown_additive",
                    "category": "unknown",
                    "percentage": it.percentage,
                    "label": LABEL_INSUFFICIENT,
                    "summary": "Chemical composition undisclosed. Cannot verify microbial degradation kinetics or environmental safety without composition disclosure.",
                    "conditions": "Unverified",
                    "standards": ["Undocumented"],
                    "references": ["Scientific Precautionary Principle"],
                    "limitations": "Risk of non-biodegradable synthetic additives, microplastic persistence, and unassessed ecotoxicity.",
                    "disintegration_vs_biodegradation": "Fragmentation of unknown resins risks generation of persistent synthetic particles.",
                    "recyclability": "Unknown effect on recycling streams.",
                    "ecotoxicity": "Cannot be verified without SDS Section 3 disclosure and heavy metal / PFAS screening."
                }
            else:
                env_profile = mat.get("environments", {}).get(target_env, {})
                label = env_profile.get("label", LABEL_INSUFFICIENT)

                if mat.get("category") == "conventional_fossil":
                    has_conventional_polymer = True
                    total_conventional_pct += pct
                    all_biodegradable_in_env = False
                elif label == LABEL_LOW:
                    all_biodegradable_in_env = False
                elif label == LABEL_LIMITED:
                    has_conditional_biopolymer = True
                    all_biodegradable_in_env = False
                elif label == LABEL_INSUFFICIENT:
                    all_biodegradable_in_env = False

                eval_item = {
                    "name": it.name,
                    "matched_id": mat.get("id"),
                    "category": mat.get("category"),
                    "percentage": it.percentage,
                    "label": label,
                    "summary": env_profile.get("summary", "No verified summary available."),
                    "conditions": env_profile.get("conditions", "Not specified"),
                    "standards": env_profile.get("standards", []),
                    "references": env_profile.get("references", []),
                    "limitations": env_profile.get("limitations", "No specific limitations noted."),
                    "disintegration_vs_biodegradation": mat.get("disintegration_vs_biodegradation_notes", ""),
                    "recyclability": mat.get("recyclability_notes", ""),
                    "ecotoxicity": mat.get("ecotoxicity_notes", "")
                }

            evaluated_ingredients.append(eval_item)

        # Determine Formulation-Level Qualitative Label
        # Strict scientific decision logic:
        # Rule 1: If formulation contains conventional non-biodegradable polymers (>1% or primary structure) -> Low biodegradation
        # Rule 2: If significant unknown components exist without evidence -> Insufficient evidence
        # Rule 3: If key biopolymers have low biodegradation in target environment (e.g. PLA in marine/soil) -> Low biodegradation under conditions
        # Rule 4: If all organic biopolymers have verified evidence in target env (e.g. PHA in soil/home compost, PLA in industrial) -> Supports biodegradation
        # Rule 5: If conditional evidence exists (e.g. PBAT in home compost or PBS in soil) -> Limited or condition-specific evidence
        # Rule 6: Default fallback -> Insufficient evidence

        rationale = []

        if len(items) == 0:
            formulation_label = LABEL_INSUFFICIENT
            rationale.append("No formulation components provided.")
        elif has_conventional_polymer:
            formulation_label = LABEL_LOW
            rationale.append(
                f"Formulation contains conventional non-biodegradable polymer(s) (accounting for ~{total_conventional_pct}% mass). "
                "Conventional polyolefins and aromatic polyesters do not undergo biological carbon mineralization under environmental conditions."
            )
        elif has_unknown_ingredient and (total_unknown_pct > 1.0 or mass_validation.get("status") == "qualitative_only"):
            formulation_label = LABEL_INSUFFICIENT
            rationale.append(
                f"Formulation includes unknown or undisclosed components (accounting for ~{total_unknown_pct}% mass or unquantified). "
                "Under international standards (e.g. EN 13432), any unidentified organic constituent exceeding 1% invalidates compostability claims."
            )
        elif any(e["label"] == LABEL_LOW for e in evaluated_ingredients):
            formulation_label = LABEL_LOW
            low_mats = [e["name"] for e in evaluated_ingredients if e["label"] == LABEL_LOW]
            rationale.append(
                f"Formulation contains component(s) with low biodegradation under '{ENVIRONMENTS[target_env]['name']}': {', '.join(low_mats)}. "
                "These materials require different environmental conditions (e.g., thermophilic composting at >58 °C) to trigger degradation."
            )
        elif all_biodegradable_in_env and len(evaluated_ingredients) > 0:
            formulation_label = LABEL_SUPPORTS
            rationale.append(
                f"Curated scientific evidence supports biodegradation of all organic components under '{ENVIRONMENTS[target_env]['name']}'. "
                "Biodegradation kinetics remain dependent on physical article geometry, wall thickness, and absence of prohibited heavy metal additives."
            )
        elif has_conditional_biopolymer or any(e["label"] == LABEL_LIMITED for e in evaluated_ingredients):
            formulation_label = LABEL_LIMITED
            cond_mats = [e["name"] for e in evaluated_ingredients if e["label"] == LABEL_LIMITED]
            rationale.append(
                f"Formulation contains component(s) with limited or conditional evidence under '{ENVIRONMENTS[target_env]['name']}': {', '.join(cond_mats)}. "
                "Biodegradation is heavily dependent on specific grade characteristics, molecular weight, blending morphology, and thickness thresholds."
            )
        else:
            formulation_label = LABEL_INSUFFICIENT
            rationale.append("Available scientific evidence is insufficient to verify biodegradation performance under the chosen environment.")

        # Environmental compatibility cross-check matrix
        env_matrix = {}
        for env_key, env_info in ENVIRONMENTS.items():
            labels_in_env = []
            for it in items:
                mat = self.find_material(it.name)
                if not mat or mat.get("id") == "unknown_additive":
                    labels_in_env.append(LABEL_INSUFFICIENT)
                else:
                    labels_in_env.append(mat.get("environments", {}).get(env_key, {}).get("label", LABEL_INSUFFICIENT))

            if LABEL_LOW in labels_in_env:
                agg_env_label = LABEL_LOW
            elif LABEL_INSUFFICIENT in labels_in_env:
                agg_env_label = LABEL_INSUFFICIENT
            elif LABEL_LIMITED in labels_in_env:
                agg_env_label = LABEL_LIMITED
            elif all(l == LABEL_SUPPORTS for l in labels_in_env) and len(labels_in_env) > 0:
                agg_env_label = LABEL_SUPPORTS
            else:
                agg_env_label = LABEL_INSUFFICIENT

            env_matrix[env_key] = {
                "name": env_info["name"],
                "label": agg_env_label
            }

        return {
            "target_environment": target_env,
            "target_environment_name": ENVIRONMENTS[target_env]["name"],
            "target_environment_conditions": ENVIRONMENTS[target_env]["desc"],
            "formulation_label": formulation_label,
            "rationale": rationale,
            "mass_validation": mass_validation,
            "doc_completeness": doc_completeness,
            "claim_verification": claim_verification,
            "evaluated_ingredients": evaluated_ingredients,
            "environment_matrix": env_matrix,
            "critical_distinction_notes": {
                "disintegration_vs_biodegradation": "Disintegration is the physical breakdown into small fragments; Biodegradation is conversion by microorganisms into CO2, water, and microbial biomass. Physical disappearance does not equal biodegradation.",
                "compostability_vs_environmental": "Industrial compostability (58 °C) does NOT equal open environment (soil or ocean) biodegradability. Most industrial compostables persist in cold nature.",
                "biobased_vs_biodegradable": "Bio-based refers to the carbon origin (plants vs petroleum); Biodegradability refers to chemical structure susceptibility to enzymatic cleavage. Bio-PE is 100% bio-based but non-biodegradable.",
                "ecotoxicity_clause": "Compostability standards require verification that degradation byproducts and residues do not inhibit plant seedling growth or earthworm survival."
            }
        }

    def generate_green_claim_gap_report(self, screening_result: Dict[str, Any], material_name: str) -> Dict[str, Any]:
        """
        Generates the 7-section Green-Claim Gap Report.
        Ensures transparent, traceable reasoning linking conclusions to local evidence records.
        """
        ingredients = screening_result.get("evaluated_ingredients", [])
        target_env_name = screening_result.get("target_environment_name", "Target Environment")
        claim_verification = screening_result.get("claim_verification", [])
        mass_val = screening_result.get("mass_validation", {})

        # 1. What the ingredients suggest
        ingredient_suggestions = []
        for ing in ingredients:
            name = ing.get("name")
            cat = ing.get("category", "")
            pct_str = f" ({ing.get('percentage')}%)" if ing.get("percentage") is not None else ""
            if cat == "conventional_fossil":
                ingredient_suggestions.append(f"{name}{pct_str}: Conventional polyolefin/fossil resin with recalcitrant C-C backbone; inherently resistant to environmental biodegradation.")
            elif cat == "biodegradable_polyester":
                ingredient_suggestions.append(f"{name}{pct_str}: Aliphatic or aliphatic-aromatic polyester susceptible to enzymatic or hydrolytic cleavage under suitable thermal and microbial conditions.")
            elif cat == "natural_polymer":
                ingredient_suggestions.append(f"{name}{pct_str}: Naturally synthesized polysaccharide with ubiquitous microbial depolymerase pathways in natural soil and aquatic media.")
            elif cat == "mineral_filler":
                ingredient_suggestions.append(f"{name}{pct_str}: Inorganic mineral constituent. Does not undergo carbon mineralization; remains as mineral ash/residue.")
            elif cat == "organic_additive":
                ingredient_suggestions.append(f"{name}{pct_str}: Small molecular weight organic additive; typically bio-assimilated if verified non-toxic.")
            elif cat == "inorganic_pigment":
                ingredient_suggestions.append(f"{name}{pct_str}: Elemental or metal oxide pigment; does not mineralize to CO2.")
            else:
                ingredient_suggestions.append(f"{name}{pct_str}: Undisclosed or unclassified chemistry. No structural biodegradability inferences possible.")

        # 2. What is supported by available evidence
        supported_evidence = []
        for ing in ingredients:
            lbl = ing.get("label")
            name = ing.get("name")
            if lbl == LABEL_SUPPORTS:
                stds = ", ".join(ing.get("standards", [])) or "Standard laboratory respirometry"
                supported_evidence.append(f"{name}: Proven microbial mineralization under {target_env_name} conditions adhering to {stds}.")
            elif lbl == LABEL_LIMITED:
                supported_evidence.append(f"{name}: Partial or condition-dependent degradation documented. Limited to specific gauge thicknesses or copolymer ratios.")

        if not supported_evidence:
            supported_evidence.append("No positive claims of environmental biodegradation are currently supported by the provided records.")

        # 3. What remains unknown
        unknowns = []
        if mass_val.get("missing_percentage", 0) > 0:
            unknowns.append(f"{mass_val.get('missing_percentage')}% of the formulation mass fraction is unaccounted for.")
        if mass_val.get("unreported_items_count", 0) > 0:
            unknowns.append(f"{mass_val.get('unreported_items_count')} ingredient(s) lack percentage concentrations.")

        for ing in ingredients:
            if ing.get("category") == "unknown":
                unknowns.append(f"Chemical composition and CAS number for '{ing.get('name')}' are undisclosed.")

        unknowns.append("Physical article thickness/gauge is unverified (biodegradation kinetics vary inversely with thickness).")
        unknowns.append("Heavy metal concentration and ecotoxicity testing (OECD 208 plant phytotoxicity) remain unverified for the compounded article.")

        # 4. Which supplier documents should be requested
        documents_to_request = [
            "Complete Safety Data Sheet (SDS) with full Section 3 constituent disclosure (down to 0.1% threshold).",
            f"Third-party accredited laboratory test report for respirometric biodegradation under {target_env_name} (ISO or ASTM certified).",
            "Physical disintegration test certificate for the maximum finished product wall thickness.",
            "Heavy metal and fluorinated substance (PFAS) chemical screening analysis.",
            "Independent certification certificate (e.g., TÜV AUSTRIA, DIN CERTCO, BPI) with valid certificate registration number and scope."
        ]

        # 5. Which test environment is relevant
        relevant_test_env = (
            f"The primary relevant test environment for this query is {target_env_name}. "
            f"Key applicable test standards include: {', '.join(ENVIRONMENTS.get(screening_result.get('target_environment'), {}).get('primary_standards', []))}."
        )

        # 6. Which claims cannot currently be verified
        unverified_claims = []
        for cv in claim_verification:
            if cv.get("status") != "Verified" and cv.get("mismatches"):
                for m in cv.get("mismatches"):
                    unverified_claims.append(f"{cv.get('ingredient')} - {m}")

        if not unverified_claims:
            unverified_claims.append("All documented supplier claims align with provided evidence fields (no explicit unverified claims flagged).")

        # 7. Recommended next steps
        recommended_next_steps = [
            "Conduct mass-balance audit with supplier to ensure 100% chemical constituent disclosure.",
            "Issue Formal Document Request to supplier for the specific test certificates identified in Section 4.",
            "Validate that the product labeling strictly adheres to verified disposal channels (e.g., avoid unrestricted 'biodegradable' labels; use specific 'Industrial Compostable Only' or 'Soil Biodegradable Mulch').",
            "Perform laboratory disintegration and phytotoxicity screening on the final converted article prior to commercial sustainability marketing."
        ]

        return {
            "material_name": material_name,
            "target_environment": target_env_name,
            "report_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "sections": {
                "1_what_ingredients_suggest": ingredient_suggestions,
                "2_what_is_supported": supported_evidence,
                "3_what_remains_unknown": unknowns,
                "4_supplier_documents_to_request": documents_to_request,
                "5_relevant_test_environment": relevant_test_env,
                "6_unverified_claims": unverified_claims,
                "7_recommended_next_steps": recommended_next_steps
            }
        }

    def generate_material_passport(
        self,
        material_name: str,
        formulation: List[FormulationItem],
        target_env: str,
        intended_use: str = "Packaging / Disposable Consumer Product",
        intended_eol: str = "Industrial Composting Facility",
        screening_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates a Digital Material Passport record.
        Includes unique ID, full formulation, classification, documentation completeness,
        gap report, disclaimer, and offline QR code.
        """
        if screening_result is None:
            screening_result = self.screen_formulation(formulation, target_env)

        gap_report = self.generate_green_claim_gap_report(screening_result, material_name)

        passport_id = f"PTB-{datetime.datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        passport_record = {
            "passport_id": passport_id,
            "material_name": material_name,
            "timestamp": timestamp,
            "intended_use": intended_use,
            "intended_end_of_life": intended_eol,
            "target_environment_screened": screening_result.get("target_environment_name"),
            "screening_classification": screening_result.get("formulation_label"),
            "documentation_completeness": screening_result.get("doc_completeness"),
            "mass_validation": screening_result.get("mass_validation"),
            "formulation": [it.to_dict() for it in formulation],
            "gap_report": gap_report,
            "standards_and_sources": self.evidence_db.get("standards", []),
            "disclaimer": (
                "SCIENTIFIC SCREENING DISCLAIMER: PolyTrace Bio is an academic and decision-support prototype. "
                "This passport represents an algorithmic evidence screening based on local scientific datasets and user-supplied inputs. "
                "It is NOT a certification, laboratory test report, legal compliance verification, or substitute for physical standard testing."
            )
        }

        # Generate QR code for offline passport identifier
        qr_base64 = self._generate_qr_code_base64(passport_id, material_name, passport_record["screening_classification"])
        passport_record["qr_code_base64"] = qr_base64

        return passport_record

    def _generate_qr_code_base64(self, passport_id: str, material_name: str, classification: str) -> Optional[str]:
        """Generate a QR code image as base64 string encoding local passport summary."""
        try:
            import qrcode
            qr_payload = (
                f"PolyTrace Bio Passport\n"
                f"ID: {passport_id}\n"
                f"Material: {material_name}\n"
                f"Screening: {classification}\n"
                f"Notice: Local Offline Record Identifier"
            )
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2,
            )
            qr.add_data(qr_payload)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0F5132", back_color="#FFFFFF")

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()
            return f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
        except Exception:
            return None

    def export_passport_markdown(self, passport: Dict[str, Any]) -> str:
        """Render material passport as human-readable Markdown report."""
        lines = []
        lines.append(f"# PolyTrace Bio — Digital Material Passport")
        lines.append(f"**Passport ID**: `{passport.get('passport_id')}`  ")
        lines.append(f"**Material Name**: {passport.get('material_name')}  ")
        lines.append(f"**Generated**: {passport.get('timestamp')}  ")
        lines.append(f"**Intended Application**: {passport.get('intended_use')}  ")
        lines.append(f"**Target End-of-Life Scenario**: {passport.get('intended_end_of_life')}  ")
        lines.append("")
        lines.append("---")
        lines.append("## 1. Executive Screening Result")
        lines.append(f"- **Target Disposal Environment**: {passport.get('target_environment_screened')}")
        lines.append(f"- **Qualitative Screening Label**: **{passport.get('screening_classification')}**")
        doc_comp = passport.get("documentation_completeness", {})
        lines.append(f"- **Documentation Completeness**: **{doc_comp.get('completeness_pct')}%** ({doc_comp.get('level')})")
        lines.append(f"  *{doc_comp.get('disclaimer')}*")
        lines.append("")

        lines.append("## 2. Formulation Mass Balance")
        mv = passport.get("mass_validation", {})
        lines.append(f"- **Status**: {mv.get('status')}")
        lines.append(f"- **Total Mass Accounted**: {mv.get('total_percentage')}%")
        if mv.get("missing_percentage", 0) > 0:
            lines.append(f"- **Unreported / Missing Mass**: {mv.get('missing_percentage')}%")
        lines.append("")
        lines.append("| Ingredient | Category | Mass % | Claimed EoL | Standard Cited | Certification |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for f in passport.get("formulation", []):
            pct = f"{f.get('percentage')}%" if f.get('percentage') is not None else "Unspecified"
            std = f.get('test_standard') or "None"
            cert = f.get('certification') or "None"
            claim = f.get('supplier_claim') or "None"
            lines.append(f"| {f.get('name')} | {f.get('category')} | {pct} | {claim} | {std} | {cert} |")
        lines.append("")

        lines.append("## 3. Green-Claim Gap Report")
        gap = passport.get("gap_report", {}).get("sections", {})

        lines.append("### 3.1 What Ingredients Suggest")
        for it in gap.get("1_what_ingredients_suggest", []):
            lines.append(f"- {it}")

        lines.append("### 3.2 What Is Supported by Available Evidence")
        for it in gap.get("2_what_is_supported", []):
            lines.append(f"- {it}")

        lines.append("### 3.3 What Remains Unknown")
        for it in gap.get("3_what_remains_unknown", []):
            lines.append(f"- {it}")

        lines.append("### 3.4 Supplier Documents to Request")
        for it in gap.get("4_supplier_documents_to_request", []):
            lines.append(f"- [ ] {it}")

        lines.append("### 3.5 Relevant Test Standards")
        lines.append(f"{gap.get('5_relevant_test_environment', '')}")

        lines.append("### 3.6 Unverified Claims & Substantiation Gaps")
        for it in gap.get("6_unverified_claims", []):
            lines.append(f"- ⚠️ {it}")

        lines.append("### 3.7 Recommended Next Steps")
        for it in gap.get("7_recommended_next_steps", []):
            lines.append(f"1. {it}")

        lines.append("")
        lines.append("---")
        lines.append("## 4. Verification & Scientific Disclaimer")
        lines.append(f"> {passport.get('disclaimer')}")
        lines.append("")
        lines.append("*Passport Record generated by PolyTrace Bio — Decision Support MVP for Sustainable Supply Chains.*")

        return "\n".join(lines)


def get_curated_sample_materials() -> Dict[str, Dict[str, Any]]:
    """Return pre-configured realistic demo materials for instant testing."""
    return {
        "Commercial Bio-Cup Lining (PLA + Talc)": {
            "name": "Commercial Bio-Cup Lining (PLA + Talc)",
            "intended_use": "Hot coffee cup waterproof interior lining",
            "intended_eol": "Industrial Composting Facility",
            "target_env": "industrial_compost",
            "formulation": [
                FormulationItem(
                    name="Polylactic Acid (PLA)",
                    category="biodegradable_polyester",
                    percentage=95.0,
                    supplier_claim="100% Compostable in commercial facilities",
                    test_standard="ISO 14855 / ASTM D6400",
                    test_environment="industrial_compost",
                    test_conditions_duration="180 days at 58 °C",
                    test_result=">90% CO2 evolution; disintegrated in 84 days",
                    certification="BPI Commercial Compostable #105284",
                    evidence_reference="TUV Report 2023-ENV-882",
                    thickness_microns=35.0
                ),
                FormulationItem(
                    name="Talc Mineral Filler",
                    category="mineral_filler",
                    percentage=5.0,
                    supplier_claim="Inorganic nucleating mineral",
                    test_standard="EN 13432 ash content clause",
                    test_environment="industrial_compost",
                    test_conditions_duration="N/A",
                    test_result="Compliant with volatile solids threshold (>50%)",
                    certification="Certificate of Mineral Purity",
                    evidence_reference="Supplier Spec Sheet TALC-99",
                    thickness_microns=35.0
                )
            ]
        },
        "Agricultural Mulch Film (PBAT + Starch + CaCO3 + Carbon Black)": {
            "name": "Agricultural Mulch Film (PBAT + Starch + CaCO3 + Carbon Black)",
            "intended_use": "Agricultural weed control soil mulch film",
            "intended_eol": "In-situ Soil Biodegradation (plowed into field)",
            "target_env": "soil",
            "formulation": [
                FormulationItem(
                    name="Polybutylene Adipate Terephthalate (PBAT)",
                    category="biodegradable_polyester",
                    percentage=55.0,
                    supplier_claim="Biodegradable in soil under EN 17033",
                    test_standard="EN 17033 / ISO 17556",
                    test_environment="soil",
                    test_conditions_duration="24 months at 25 °C",
                    test_result="91.4% carbon conversion in natural soil",
                    certification="TÜV AUSTRIA OK Biodegradable SOIL",
                    evidence_reference="Soil Lab Study AGRI-2022-441",
                    thickness_microns=15.0
                ),
                FormulationItem(
                    name="Thermoplastic Starch (TPS)",
                    category="natural_polymer",
                    percentage=30.0,
                    supplier_claim="Natural biobased starch polysaccharide",
                    test_standard="ISO 17556",
                    test_environment="soil",
                    test_conditions_duration="12 months at 20 °C",
                    test_result="Complete microbial conversion >95%",
                    certification="USDA Certified Biobased",
                    evidence_reference="Agro-Starch Dossier 2021",
                    thickness_microns=15.0
                ),
                FormulationItem(
                    name="Calcium Carbonate (CaCO3 Filler)",
                    category="mineral_filler",
                    percentage=13.0,
                    supplier_claim="Natural mineral chalk",
                    test_standard="EN 17033 heavy metal limits",
                    test_environment="soil",
                    test_conditions_duration="N/A",
                    test_result="Free of Pb, Cd, As contamination",
                    certification="ISO 9001 Supplier Declaration",
                    evidence_reference="Batch Certificate CAL-884",
                    thickness_microns=15.0
                ),
                FormulationItem(
                    name="Carbon Black (Black Pigment)",
                    category="inorganic_pigment",
                    percentage=2.0,
                    supplier_claim="Black opacity masterbatch",
                    test_standard="EN 17033 Annex A",
                    test_environment="soil",
                    test_conditions_duration="N/A",
                    test_result="Inert elemental carbon <2% cap",
                    certification="Compliant with PAH limits",
                    evidence_reference="Masterbatch Cert MB-BLK-01",
                    thickness_microns=15.0
                )
            ]
        },
        "Marine-Degradable Cold Beverage Straw (PHA + ATBC)": {
            "name": "Marine-Degradable Cold Beverage Straw (PHA + ATBC)",
            "intended_use": "Single-use cold drink straw",
            "intended_eol": "Home Compost / Accidental Marine Exposure",
            "target_env": "marine",
            "formulation": [
                FormulationItem(
                    name="Polyhydroxyalkanoates (PHA: PHB / PHBV)",
                    category="biodegradable_polyester",
                    percentage=92.0,
                    supplier_claim="Marine biodegradable and ocean-safe",
                    test_standard="ISO 22403 / ASTM D6691",
                    test_environment="marine",
                    test_conditions_duration="180 days at 20 °C in natural seawater",
                    test_result="88.6% biochemical oxygen demand conversion",
                    certification="TÜV AUSTRIA OK Biodegradable MARINE",
                    evidence_reference="Oceanographic Lab Report OCN-2023-71",
                    thickness_microns=200.0
                ),
                FormulationItem(
                    name="Acetyl Tributyl Citrate (ATBC Plasticizer)",
                    category="organic_additive",
                    percentage=8.0,
                    supplier_claim="Food-contact biobased plasticizer",
                    test_standard="OECD 301B",
                    test_environment="freshwater",
                    test_conditions_duration="28 days aerobic aquatic respirometry",
                    test_result="82% ready biodegradation",
                    certification="FDA 21 CFR 175.105 compliant",
                    evidence_reference="Citroflex Tech Bulletin 2020",
                    thickness_microns=200.0
                )
            ]
        },
        "'Eco-Degradable' Bag (PE + Pro-degradant Additive)": {
            "name": "'Eco-Degradable' Bag (PE + Pro-degradant Additive)",
            "intended_use": "Supermarket checkout grocery bag",
            "intended_eol": "Home Compost or Landfill",
            "target_env": "home_compost",
            "formulation": [
                FormulationItem(
                    name="Polyethylene (PE: LDPE / LLDPE / HDPE)",
                    category="conventional_fossil",
                    percentage=97.0,
                    supplier_claim="Recyclable conventional resin",
                    test_standard="None",
                    test_environment=None,
                    test_conditions_duration=None,
                    test_result=None,
                    certification=None,
                    evidence_reference=None,
                    thickness_microns=20.0
                ),
                FormulationItem(
                    name="Unknown Trade-Name Additive / Proprietary Masterbatch",
                    category="unknown",
                    percentage=3.0,
                    supplier_claim="Proprietary d2w / oxo-biodegradable masterbatch promoting 100% degradation",
                    test_standard="ASTM D6954 (abiotic degradation only)",
                    test_environment="soil",
                    test_conditions_duration="Abiotic UV exposure",
                    test_result="Embrittlement and fragmentation observed",
                    certification="None",
                    evidence_reference="Marketing brochure claim",
                    thickness_microns=20.0
                )
            ]
        },
        "Cellulose Film with Synthetic Barrier Coating": {
            "name": "Cellulose Film with Synthetic Barrier Coating",
            "intended_use": "High-barrier dry snack packaging wrap",
            "intended_eol": "Industrial Composting",
            "target_env": "industrial_compost",
            "formulation": [
                FormulationItem(
                    name="Regenerated Cellulose / Cellophane",
                    category="natural_polymer",
                    percentage=80.0,
                    supplier_claim="NatureFlex biobased cellulose film",
                    test_standard="ISO 14855 / EN 13432",
                    test_environment="industrial_compost",
                    test_conditions_duration="45 days at 58 °C",
                    test_result="99.1% mineralization (positive control)",
                    certification="TÜV OK Compost INDUSTRIAL",
                    evidence_reference="Cellulose Tech Spec 2022",
                    thickness_microns=25.0
                ),
                FormulationItem(
                    name="Unknown Trade-Name Additive / Proprietary Masterbatch",
                    category="unknown",
                    percentage=None,
                    supplier_claim="Moisture vapor barrier PVDC/acrylic synthetic coating",
                    test_standard="None",
                    test_environment=None,
                    test_conditions_duration=None,
                    test_result=None,
                    certification=None,
                    evidence_reference=None,
                    thickness_microns=2.0
                )
            ]
        }
    }
