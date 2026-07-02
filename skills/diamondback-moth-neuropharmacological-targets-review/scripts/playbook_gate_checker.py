#!/usr/bin/env python3
"""Validate writing playbook compliance for review paper.

This script checks that all writing issues in the Issues CSV pass the
6 playbook gate constraints defined in review-writing-playbook.md.

Usage:
    python playbook_gate_checker.py <issues.csv> [--tex-file main.tex] [--strict]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from dataclasses import dataclass

# Playbook gate columns
GATE_COLUMNS = [
    "has_context_pain_gap",
    "has_scope_deliverables", 
    "has_taxonomy_map",
    "has_section_loop",
    "has_actionable_roadmap",
    "pharma_workflow_alignment",
    "wet_lab_bridge",
    "benchmarking_strategy",
    "data_provenance_notes",
]

# Gap signal words (Playbook Rule 1)
GAP_SIGNALS = [r"\bHowever\b", r"\bYet\b", r"\bDespite\b", r"\bNevertheless\b", r"\bNonetheless\b"]
GAP_INDICATORS = [r"lacking", r"missing", r"gap", r"absent", r"overlooked", r"underexplored", r"no systematic", r"remains unclear"]

# Scope/deliverables indicators (Playbook Rule 2)
SCOPE_INDICATORS = [r"we discuss", r"we summarize", r"we highlight", r"we provide", r"we present", r"this review"]
DELIVERABLE_TYPES = [r"taxonomy", r"comparison", r"table", r"roadmap", r"framework", r"checklist", r"benchmark"]

# Section loop elements (Playbook Rule 4)
MECHANISM_INDICATORS = [r"key insight", r"exploits the", r"based on the assumption", r"leverages the", r"relies on", r"fundamental"]
FAILURE_INDICATORS = [r"limitation", r"fails when", r"tends to", r"practitioners should note", r"caution", r"shortcoming", r"drawback"]
PHARMA_INDICATORS = [r"medicinal chemist", r"DMPK", r"biologist", r"in practice", r"integration with", r"practitioners"]

# Roadmap indicators (Playbook Rule 5)
ROADMAP_INDICATORS = [r"short.?term", r"medium.?term", r"long.?term", r"6.?18 months?", r"2.?5 years?", r"near.?term", r"future direction"]


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    gate: str
    issue_id: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


def check_gap_statement(text: str) -> tuple[bool, str]:
    """Check for Context-Pain-Gap structure (Rule 1)."""
    text_lower = text.lower()
    
    # Check for gap signal word
    has_signal = any(re.search(pattern, text, re.IGNORECASE) for pattern in GAP_SIGNALS)
    
    # Check for gap indicator
    has_indicator = any(re.search(pattern, text_lower) for pattern in GAP_INDICATORS)
    
    if has_signal and has_indicator:
        return True, "Gap statement found with signal word and gap indicator"
    elif has_signal:
        return False, "Gap signal word found but no clear gap indicator"
    elif has_indicator:
        return False, "Gap indicator found but missing However/Yet/Despite signal"
    else:
        return False, "No gap statement found - need 'However/Yet/Despite' + gap description"


def check_scope_deliverables(text: str) -> tuple[bool, str]:
    """Check for Scope & Deliverables statement (Rule 2)."""
    text_lower = text.lower()
    
    # Check for scope indicator
    has_scope = any(re.search(pattern, text_lower) for pattern in SCOPE_INDICATORS)
    
    # Check for deliverable types
    deliverables_found = [d for d in DELIVERABLE_TYPES if re.search(d, text_lower)]
    
    # Check for itemize/enumerate environment (LaTeX)
    has_bullets = r"\begin{itemize}" in text or r"\begin{enumerate}" in text or r"\item" in text
    
    if has_scope and deliverables_found and has_bullets:
        return True, f"Scope statement with deliverables: {deliverables_found}"
    elif has_scope and deliverables_found:
        return False, f"Scope and deliverables mentioned but no bullet list found"
    elif has_scope:
        return False, "Scope mentioned but no specific deliverables listed"
    else:
        return False, "No scope statement found - need 'we discuss/present/provide' + deliverable list"


def check_section_loop(text: str) -> tuple[bool, str]:
    """Check for section narrative loop (Rule 4)."""
    text_lower = text.lower()
    
    has_mechanism = any(re.search(pattern, text_lower) for pattern in MECHANISM_INDICATORS)
    has_failure = any(re.search(pattern, text_lower) for pattern in FAILURE_INDICATORS)
    has_pharma = any(re.search(pattern, text_lower) for pattern in PHARMA_INDICATORS)
    
    elements = []
    if has_mechanism:
        elements.append("mechanism")
    if has_failure:
        elements.append("failure modes")
    if has_pharma:
        elements.append("pharma implications")
    
    # Need at least failure modes + one other element
    if has_failure and (has_mechanism or has_pharma):
        return True, f"Section loop elements found: {elements}"
    elif elements:
        missing = []
        if not has_failure:
            missing.append("failure modes")
        if not has_mechanism and not has_pharma:
            missing.append("mechanism or pharma implications")
        return False, f"Partial loop: found {elements}, missing {missing}"
    else:
        return False, "No section loop elements found - need mechanism + failure modes + pharma implications"


def check_roadmap(text: str) -> tuple[bool, str]:
    """Check for actionable roadmap (Rule 5)."""
    text_lower = text.lower()
    
    has_roadmap = any(re.search(pattern, text_lower) for pattern in ROADMAP_INDICATORS)
    
    if has_roadmap:
        return True, "Roadmap with time horizons found"
    else:
        return False, "No actionable roadmap found - need short-term/medium-term milestones"


def validate_csv_gates(issues_path: Path) -> list[ValidationResult]:
    """Validate all playbook gates in Issues CSV."""
    results = []
    
    with issues_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Check which gate columns exist
    if not rows:
        results.append(ValidationResult("schema", "N/A", False, "Empty CSV file", "error"))
        return results
    
    header = rows[0].keys()
    missing_gates = [g for g in GATE_COLUMNS if g not in header]
    
    if missing_gates:
        results.append(ValidationResult(
            "schema", "N/A", False, 
            f"Missing playbook gate columns: {missing_gates}", "error"
        ))
    
    # Validate each writing issue
    for row in rows:
        issue_id = row.get("ID") or row.get("Issue_ID", "UNKNOWN")
        phase = row.get("Phase", "")
        issue_type = (row.get("Issue_Type") or row.get("Type") or "").strip()
        section = (row.get("Section_Label") or row.get("Section_Target") or "").lower()
        type_lower = issue_type.lower()
        
        # Only check Writing phase issues
        if phase != "Writing":
            continue
        
        # Rule 1: Introduction must have gap statement
        if "intro" in section or type_lower == "intro":
            gate_value = row.get("has_context_pain_gap", "N/A")
            if gate_value == "N":
                results.append(ValidationResult(
                    "has_context_pain_gap", issue_id, False,
                    "Introduction missing Context-Pain-Gap structure"
                ))
            elif gate_value == "Y":
                results.append(ValidationResult(
                    "has_context_pain_gap", issue_id, True,
                    "Gap statement verified", "info"
                ))
        
        # Rule 2: Introduction must have scope/deliverables
        if "intro" in section or type_lower == "intro":
            gate_value = row.get("has_scope_deliverables", "N/A")
            if gate_value == "N":
                results.append(ValidationResult(
                    "has_scope_deliverables", issue_id, False,
                    "Introduction missing Scope & Deliverables bullets"
                ))
            elif gate_value == "Y":
                results.append(ValidationResult(
                    "has_scope_deliverables", issue_id, True,
                    "Scope statement verified", "info"
                ))
        
        # Rule 3: Early sections need taxonomy
        if "taxonomy" in section or type_lower in ["taxonomy", "background"] or section in ["sec:background", "sec:overview"]:
            gate_value = row.get("has_taxonomy_map", "N/A")
            if gate_value == "N":
                results.append(ValidationResult(
                    "has_taxonomy_map", issue_id, False,
                    "Section should contain taxonomy/classification"
                ))
        
        # Rule 4: All body sections need narrative loop
        if type_lower not in ["intro", "roadmap"] and section not in ["sec:intro", "sec:conclusion", "sec:future"]:
            gate_value = row.get("has_section_loop", "N/A")
            if gate_value == "N":
                results.append(ValidationResult(
                    "has_section_loop", issue_id, False,
                    "Section missing narrative loop (mechanism → methods → failure → implications)"
                ))
            elif gate_value == "Y":
                results.append(ValidationResult(
                    "has_section_loop", issue_id, True,
                    "Section loop verified", "info"
                ))
        
        # Rule 5: Conclusion needs roadmap
        if type_lower == "roadmap" or "conclusion" in section or "future" in section:
            gate_value = row.get("has_actionable_roadmap", "N/A")
            if gate_value == "N":
                results.append(ValidationResult(
                    "has_actionable_roadmap", issue_id, False,
                    "Conclusion missing actionable roadmap with time horizons"
                ))
            elif gate_value == "Y":
                results.append(ValidationResult(
                    "has_actionable_roadmap", issue_id, True,
                    "Roadmap verified", "info"
                ))
    
    return results


def validate_tex_content(tex_path: Path) -> list[ValidationResult]:
    """Validate LaTeX content against playbook rules."""
    results = []
    
    if not tex_path.exists():
        results.append(ValidationResult(
            "content", "N/A", False,
            f"TeX file not found: {tex_path}", "warning"
        ))
        return results
    
    content = tex_path.read_text(encoding="utf-8", errors="ignore")
    
    # Extract sections
    section_pattern = re.compile(r"\\section\{([^}]+)\}(.*?)(?=\\section\{|\\end\{document\}|$)", re.DOTALL)
    sections = section_pattern.findall(content)
    
    for section_name, section_content in sections:
        section_lower = section_name.lower()
        
        # Check introduction
        if "introduction" in section_lower:
            passed, msg = check_gap_statement(section_content)
            results.append(ValidationResult(
                "content_gap", section_name, passed, msg,
                "error" if not passed else "info"
            ))
            
            passed, msg = check_scope_deliverables(section_content)
            results.append(ValidationResult(
                "content_scope", section_name, passed, msg,
                "error" if not passed else "info"
            ))
        
        # Check conclusion/future
        elif "conclusion" in section_lower or "future" in section_lower:
            passed, msg = check_roadmap(section_content)
            results.append(ValidationResult(
                "content_roadmap", section_name, passed, msg,
                "error" if not passed else "info"
            ))
        
        # Check body sections
        else:
            passed, msg = check_section_loop(section_content)
            results.append(ValidationResult(
                "content_loop", section_name, passed, msg,
                "warning" if not passed else "info"
            ))
    
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate writing playbook compliance"
    )
    parser.add_argument("issues_csv", help="Path to issues CSV file")
    parser.add_argument("--tex-file", help="Path to main.tex for content validation")
    parser.add_argument("--strict", action="store_true", help="Fail on any violation")
    parser.add_argument("--quiet", action="store_true", help="Only show errors")
    
    args = parser.parse_args()
    
    issues_path = Path(args.issues_csv)
    if not issues_path.exists():
        print(f"Error: Issues CSV not found: {issues_path}", file=sys.stderr)
        return 1
    
    print(f"Validating playbook compliance: {issues_path}")
    print("=" * 60)
    
    # Validate CSV gates
    csv_results = validate_csv_gates(issues_path)
    
    # Validate TeX content if provided
    tex_results = []
    if args.tex_file:
        tex_path = Path(args.tex_file)
        tex_results = validate_tex_content(tex_path)
    
    all_results = csv_results + tex_results
    
    # Print results
    errors = [r for r in all_results if not r.passed and r.severity == "error"]
    warnings = [r for r in all_results if not r.passed and r.severity == "warning"]
    passed = [r for r in all_results if r.passed]
    
    if not args.quiet:
        if passed:
            print("\n✓ PASSED:")
            for r in passed:
                print(f"  [{r.issue_id}] {r.gate}: {r.message}")
    
    if warnings:
        print("\n⚠ WARNINGS:")
        for r in warnings:
            print(f"  [{r.issue_id}] {r.gate}: {r.message}")
    
    if errors:
        print("\n✗ ERRORS:")
        for r in errors:
            print(f"  [{r.issue_id}] {r.gate}: {r.message}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Summary: {len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors")
    
    if errors:
        print("\nPlaybook validation FAILED")
        return 1
    elif warnings and args.strict:
        print("\nPlaybook validation FAILED (strict mode)")
        return 1
    else:
        print("\nPlaybook validation PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
