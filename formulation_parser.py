"""
PolyTrace Bio — Formulation Lab Parser
=======================================
Robust, deterministic parser for bioplastic formulations pasted from lab notebooks,
spreadsheets, supplier data sheets, and scientific papers.

Supports:
- Format A: Comma-separated with % (e.g. "PLA, 70%")
- Format B: Header + values (e.g. "Ingredient, Percentage\nPLA, 70")
- Format C: Semicolon / colon pairs (e.g. "PLA: 70%; talc: 20%; plasticizer: 8%")
- Format D: wt% / mass% notation (e.g. "PLA 70 wt%\nTalc 20 wt%")
- Tab-separated spreadsheet copies (e.g. "PLA\t70")
- Multi-line, space-delimited, and mixed capitalization formats
- Duplicate detection, negative percentage rejection, and mass-balance checks.
"""

import re
import csv
import io
import json
from typing import Dict, List, Any, Optional, Tuple


def clean_text_line(line: str) -> str:
    """Strip whitespace, leading bullet points, and trailing comments."""
    l = line.strip()
    # Remove leading markdown or bullet list characters like -, *, •, 1., etc.
    l = re.sub(r"^[\*\-\•\d+\.]\s*", "", l)
    # Strip comments if any
    l = re.split(r"#|//", l)[0].strip()
    return l


def is_header_line(line: str) -> bool:
    """Detect if a line is a spreadsheet/table header rather than an ingredient row."""
    lower = line.lower()
    headers = [
        "ingredient", "component", "material", "constituent", "substance",
        "percentage", "percent", "%", "fraction", "wt%", "mass%", "ratio", "loading"
    ]
    # Check if multiple header tokens occur
    tokens = re.split(r"[,;:\t|]+", lower)
    clean_tokens = [t.strip() for t in tokens if t.strip()]
    if len(clean_tokens) >= 2:
        matches = sum(1 for t in clean_tokens if any(h in t for h in headers))
        if matches >= 1 and not any(re.search(r"\d", t) for t in clean_tokens):
            return True
    return False


def parse_single_ingredient_token(token: str) -> Tuple[Optional[str], Optional[float], List[str]]:
    """
    Parse an ingredient name and percentage from a single line or segment.
    Returns: (name, percentage_float, errors)
    """
    errors = []
    t = clean_text_line(token)
    if not t:
        return None, None, []

    # Check for negative percentage attempt
    if re.search(r"-\s*\d", t):
        errors.append(f"Negative mass percentage detected in '{token}'. Mass percentages must be non-negative.")

    # Match common patterns:
    # 1. Colon separated: "PLA : 70%" or "PLA: 70 wt%"
    colon_match = re.match(r"^([^:]+):\s*([+-]?\d+(?:\.\d+)?)\s*(?:%|wt%|mass%|w/w|wt\s*%)?$", t, re.IGNORECASE)
    if colon_match:
        name = colon_match.group(1).strip()
        val_str = colon_match.group(2)
        try:
            val = float(val_str)
            return name, val, errors
        except ValueError:
            pass

    # 2. Comma or Tab separated: "PLA, 70%" or "PLA\t70"
    delim_match = re.split(r"[,\t|]+", t)
    if len(delim_match) >= 2:
        name = delim_match[0].strip()
        val_part = delim_match[1].strip()
        # Extract number from val_part
        num_match = re.search(r"([+-]?\d+(?:\.\d+)?)", val_part)
        if num_match:
            try:
                val = float(num_match.group(1))
                return name, val, errors
            except ValueError:
                pass

    # 3. Space separated with wt% / %: "PLA 70 wt%" or "PLA 70%" or "PLA 70"
    space_match = re.match(r"^(.+?)\s+([+-]?\d+(?:\.\d+)?)\s*(?:%|wt%|mass%|w/w|wt\s*%)?$", t, re.IGNORECASE)
    if space_match:
        name = space_match.group(1).strip()
        val_str = space_match.group(2)
        try:
            val = float(val_str)
            return name, val, errors
        except ValueError:
            pass

    # 4. Fallback: only name found, no number
    # If the token has no digits, it's an ingredient with unassigned percentage
    if not re.search(r"\d", t):
        return t.strip(), None, errors

    errors.append(f"Could not reliably extract percentage from '{token}'.")
    return t.strip(), None, errors


def parse_pasted_formulation(raw_text: str, engine=None) -> Dict[str, Any]:
    """
    Main parser for user-pasted formulation text.
    Handles multi-line pastes, semicolon lists, CSV, tab-delimited, and space wt% notations.
    """
    if not raw_text or not raw_text.strip():
        return {
            "success": False,
            "raw_text": raw_text or "",
            "items": [],
            "total_percentage": 0.0,
            "validation_status": "empty",
            "errors": ["Input is empty. Please paste an ingredient formulation."],
            "warnings": [],
            "duplicates": [],
            "unknown_count": 0,
            "known_count": 0
        }

    lines = raw_text.strip().splitlines()
    candidate_tokens: List[str] = []

    for line in lines:
        cleaned = clean_text_line(line)
        if not cleaned:
            continue
        # Check if line contains multiple entries separated by semicolons (Format C)
        if ";" in cleaned:
            parts = [p.strip() for p in cleaned.split(";") if p.strip()]
            candidate_tokens.extend(parts)
        else:
            candidate_tokens.append(cleaned)

    parsed_rows: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []
    seen_names: Dict[str, int] = {}
    duplicates: List[str] = []

    for idx, token in enumerate(candidate_tokens):
        # Skip header lines if present
        if idx == 0 and is_header_line(token):
            continue

        name, pct, token_errors = parse_single_ingredient_token(token)
        if token_errors:
            errors.extend(token_errors)

        if not name:
            continue

        # Check for duplicate names (normalized)
        norm_name = name.strip().lower()
        if norm_name in seen_names:
            duplicates.append(name)
            warnings.append(f"Duplicate ingredient detected: '{name}'. Formulation items should be combined or uniquely named.")
        seen_names[norm_name] = seen_names.get(norm_name, 0) + 1

        # Check negative or extreme percentages
        if pct is not None:
            if pct < 0:
                if f"Negative mass percentage for '{name}'" not in errors:
                    errors.append(f"Negative mass percentage ({pct}%) for '{name}' is invalid.")
            elif pct > 100.0:
                warnings.append(f"Individual ingredient '{name}' has percentage {pct}% > 100%.")

        # Material lookup if engine available
        matched_material = None
        is_unknown = True
        suggested_category = "unknown"

        if engine is not None:
            mat = engine.find_material(name)
            if mat and mat.get("id") != "unknown_additive":
                matched_material = mat
                is_unknown = False
                suggested_category = mat.get("category", "unknown")
            else:
                is_unknown = True
                suggested_category = "unknown"
                warnings.append(f"Ingredient '{name}' is not recognized in the verified database. Treated as unknown component.")

        parsed_rows.append({
            "name": name,
            "percentage": pct,
            "category": suggested_category,
            "is_unknown": is_unknown,
            "matched_id": matched_material.get("id") if matched_material else None,
            "raw_token": token
        })

    if not parsed_rows:
        return {
            "success": False,
            "raw_text": raw_text,
            "items": [],
            "total_percentage": 0.0,
            "validation_status": "empty_after_parsing",
            "errors": ["Failed to extract any ingredients. Please check formatting guidelines."],
            "warnings": warnings,
            "duplicates": duplicates,
            "unknown_count": 0,
            "known_count": 0
        }

    # Calculate mass balance
    valid_pcts = [r["percentage"] for r in parsed_rows if r["percentage"] is not None and r["percentage"] >= 0]
    unassigned_count = sum(1 for r in parsed_rows if r["percentage"] is None)
    total_percentage = round(sum(valid_pcts), 2)

    unknown_count = sum(1 for r in parsed_rows if r.get("is_unknown", True))
    known_count = len(parsed_rows) - unknown_count

    # Mass balance validation status
    if len(valid_pcts) == 0:
        val_status = "qualitative_only"
        warnings.append("No mass percentages provided. Formulation will be screened on qualitative presence only.")
    elif 99.0 <= total_percentage <= 101.0:
        if unassigned_count == 0:
            val_status = "complete"
        else:
            val_status = "inconsistent_unreported"
            warnings.append(f"Percentages total {total_percentage}%, but {unassigned_count} ingredient(s) have unassigned percentages.")
    elif total_percentage < 99.0:
        val_status = "under_reported"
        missing = round(100.0 - total_percentage, 2)
        warnings.append(f"Formulation totals {total_percentage}% (incomplete). Missing unassigned fraction: {missing}%. PolyTrace Bio does NOT auto-fill missing fractions.")
    else:
        val_status = "over_reported"
        over = round(total_percentage - 100.0, 2)
        errors.append(f"Formulation percentages sum to {total_percentage}%, exceeding 100% by {over}%. Please check values.")

    success = len(errors) == 0 and len(parsed_rows) > 0

    return {
        "success": success,
        "raw_text": raw_text,
        "items": parsed_rows,
        "total_percentage": total_percentage,
        "validation_status": val_status,
        "missing_percentage": round(100.0 - total_percentage, 2) if total_percentage < 99.0 else 0.0,
        "over_percentage": round(total_percentage - 100.0, 2) if total_percentage > 101.0 else 0.0,
        "unassigned_count": unassigned_count,
        "errors": errors,
        "warnings": warnings,
        "duplicates": duplicates,
        "unknown_count": unknown_count,
        "known_count": known_count
    }


def export_formulation_csv(items: List[Dict[str, Any]]) -> str:
    """Export parsed items to clean CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ingredient", "Percentage", "Category", "Database_Match"])
    for it in items:
        writer.writerow([
            it.get("name", ""),
            it.get("percentage") if it.get("percentage") is not None else "",
            it.get("category", "unknown"),
            it.get("matched_id") or "Unmatched"
        ])
    return output.getvalue()


def export_formulation_json(items: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
    """Export parsed items and metadata to structured JSON format."""
    payload = {
        "metadata": metadata or {},
        "ingredients": items
    }
    return json.dumps(payload, indent=2)


# Sample formulations matching user requirements
SAMPLE_PASTE_FORMATS = {
    "Format A: Comma-separated with %": (
        "PLA, 70%\n"
        "Talc, 20%\n"
        "Plasticizer, 8%\n"
        "Pigment, 2%"
    ),
    "Format B: Spreadsheet Table with Header": (
        "Ingredient, Percentage\n"
        "PLA, 70\n"
        "Talc, 20\n"
        "Plasticizer, 8\n"
        "Pigment, 2"
    ),
    "Format C: Semicolon / Colon Pairs": (
        "PLA: 70%; talc: 20%; plasticizer: 8%; pigment: 2%"
    ),
    "Format D: wt% Notation": (
        "PLA 70 wt%\n"
        "Talc 20 wt%\n"
        "Plasticizer 8 wt%\n"
        "Pigment 2 wt%"
    ),
    "Mulch Film Recipe (EN 17033 Target)": (
        "Polybutylene Adipate Terephthalate (PBAT), 55%\n"
        "Thermoplastic Starch (TPS), 30%\n"
        "Calcium Carbonate (CaCO3 Filler), 13%\n"
        "Carbon Black (Black Pigment), 2%"
    )
}
