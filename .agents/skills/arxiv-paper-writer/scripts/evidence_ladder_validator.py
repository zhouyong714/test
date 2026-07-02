#!/usr/bin/env python3
"""Evidence ladder validator.

Validates that evidence levels (L0-L3) are properly assigned and distributed
across the review's study table and Issues CSV.

Checks:
  - All Evidence_RowIDs in Issues exist in study table
  - Evidence levels are assigned to all studies
  - Distribution is reasonable (not all L1)
  - Key claims have sufficient evidence (L2+)
  - Preprints are properly marked

Usage:
    python3 evidence_ladder_validator.py <paper_dir>
    python3 evidence_ladder_validator.py <paper_dir> --strict
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    """Result of validation."""
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)


def find_study_table(paper_dir: Path) -> Path | None:
    """Find study table CSV in paper directory."""
    candidates = [
        paper_dir / "notes" / "study-table.csv",
        paper_dir / "notes" / "pharma-study-table.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def find_issues_csv(paper_dir: Path) -> Path | None:
    """Find Issues CSV in paper directory."""
    issues_dir = paper_dir / "issues"
    if not issues_dir.exists():
        return None
    
    csvs = list(issues_dir.glob("*.csv"))
    if not csvs:
        return None
    
    # Return most recent
    return max(csvs, key=lambda p: p.stat().st_mtime)


def load_study_table(path: Path) -> list[dict[str, str]]:
    """Load study table CSV."""
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_issues_csv(path: Path) -> list[dict[str, str]]:
    """Load Issues CSV."""
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_evidence_levels(studies: list[dict[str, str]]) -> ValidationResult:
    """Validate evidence level assignments."""
    result = ValidationResult()
    
    valid_levels = {"L0", "L1", "L2", "L3"}
    level_counts: Counter[str] = Counter()
    missing_level = []
    invalid_level = []
    
    for study in studies:
        row_id = study.get("Row_ID", "unknown")
        level = study.get("Evidence_Level", "").strip().upper()
        
        if not level:
            missing_level.append(row_id)
        elif level not in valid_levels:
            invalid_level.append(f"{row_id}: {level}")
        else:
            level_counts[level] += 1
    
    if missing_level:
        result.errors.append(f"Missing Evidence_Level: {missing_level}")
        result.passed = False
    
    if invalid_level:
        result.errors.append(f"Invalid Evidence_Level values: {invalid_level}")
        result.passed = False
    
    # Check distribution
    total = sum(level_counts.values())
    result.stats["total_studies"] = total
    result.stats["by_level"] = dict(level_counts)
    
    if total > 0:
        l1_pct = level_counts.get("L1", 0) / total
        if l1_pct > 0.8:
            result.warnings.append(
                f"Warning: {l1_pct:.0%} of studies are L1 (in-silico only). "
                "Consider if more L2/L3 evidence is available."
            )
        
        l0_count = level_counts.get("L0", 0)
        if l0_count > 0:
            result.warnings.append(
                f"Warning: {l0_count} studies marked L0 (anecdotal). "
                "L0 evidence should be used sparingly."
            )
        
        l3_count = level_counts.get("L3", 0)
        if l3_count == 0 and total >= 10:
            result.warnings.append(
                "Warning: No L3 (experimental/clinical) evidence in review. "
                "Consider if any wet-lab validation papers are available."
            )
    
    return result


def validate_preprint_marking(studies: list[dict[str, str]]) -> ValidationResult:
    """Validate preprint status marking."""
    result = ValidationResult()
    
    valid_statuses = {"Published", "Preprint", "Upgraded", ""}
    preprint_counts: Counter[str] = Counter()
    invalid_status = []
    
    for study in studies:
        row_id = study.get("Row_ID", "unknown")
        status = study.get("Preprint_Status", "").strip()
        
        if status and status not in valid_statuses:
            invalid_status.append(f"{row_id}: {status}")
        else:
            preprint_counts[status or "Unknown"] += 1
    
    if invalid_status:
        result.errors.append(f"Invalid Preprint_Status values: {invalid_status}")
        result.passed = False
    
    result.stats["preprint_status"] = dict(preprint_counts)
    
    # Check preprint percentage
    total = sum(preprint_counts.values())
    preprint_count = preprint_counts.get("Preprint", 0)
    if total > 0 and preprint_count / total > 0.5:
        result.warnings.append(
            f"Warning: {preprint_count}/{total} ({preprint_count/total:.0%}) studies are preprints. "
            "Consider running preprint_upgrade_checker.py."
        )
    
    return result


def validate_issues_evidence_refs(
    issues: list[dict[str, str]],
    study_ids: set[str],
) -> ValidationResult:
    """Validate that Evidence_RowIDs in Issues exist in study table."""
    result = ValidationResult()
    
    missing_refs = []
    issues_with_evidence = 0
    
    for issue in issues:
        issue_id = issue.get("Issue_ID", "unknown")
        evidence_refs = issue.get("Evidence_RowIDs", "").strip()
        
        if not evidence_refs:
            continue
        
        issues_with_evidence += 1
        
        # Parse refs (semicolon-separated)
        refs = [r.strip() for r in evidence_refs.split(";") if r.strip()]
        for ref in refs:
            if ref not in study_ids:
                missing_refs.append(f"{issue_id} -> {ref}")
    
    if missing_refs:
        result.errors.append(
            f"Evidence_RowIDs reference non-existent study rows: {missing_refs[:10]}"
            + (f" (+{len(missing_refs)-10} more)" if len(missing_refs) > 10 else "")
        )
        result.passed = False
    
    result.stats["issues_with_evidence"] = issues_with_evidence
    result.stats["total_issues"] = len(issues)
    
    # Warning if few issues have evidence
    if len(issues) > 0:
        pct = issues_with_evidence / len(issues)
        if pct < 0.3:
            result.warnings.append(
                f"Warning: Only {pct:.0%} of issues have Evidence_RowIDs. "
                "Consider linking more claims to evidence."
            )
    
    return result


def validate_key_claims(issues: list[dict[str, str]], studies: list[dict[str, str]]) -> ValidationResult:
    """Validate that key claims have sufficient evidence."""
    result = ValidationResult()
    
    # Build study ID -> level map
    study_levels = {}
    for study in studies:
        row_id = study.get("Row_ID", "")
        level = study.get("Evidence_Level", "").strip().upper()
        if row_id and level:
            study_levels[row_id] = level
    
    # Check writing issues for evidence quality
    weak_evidence_issues = []
    
    for issue in issues:
        issue_id = issue.get("Issue_ID", "")
        phase = issue.get("Phase", "")
        issue_type = (issue.get("Issue_Type") or issue.get("Type") or "").strip()
        
        # Only check writing issues
        if phase != "Writing" and not issue_id.startswith("W"):
            continue
        
        evidence_refs = issue.get("Evidence_RowIDs", "").strip()
        if not evidence_refs:
            continue
        
        refs = [r.strip() for r in evidence_refs.split(";") if r.strip()]
        levels = [study_levels.get(r, "L0") for r in refs]
        
        # Check if all evidence is L0 or L1
        if levels and all(l in ["L0", "L1"] for l in levels):
            weak_evidence_issues.append(issue_id)
    
    if weak_evidence_issues:
        result.warnings.append(
            f"Warning: Writing issues with only L0/L1 evidence: {weak_evidence_issues[:5]}"
            + (f" (+{len(weak_evidence_issues)-5} more)" if len(weak_evidence_issues) > 5 else "")
        )
    
    result.stats["weak_evidence_issues"] = len(weak_evidence_issues)
    
    return result


def run_validation(paper_dir: Path, *, strict: bool = False) -> ValidationResult:
    """Run all evidence ladder validations."""
    combined = ValidationResult()
    
    # Find files
    study_path = find_study_table(paper_dir)
    issues_path = find_issues_csv(paper_dir)
    
    if study_path is None:
        combined.errors.append("Study table not found in notes/")
        combined.passed = False
        return combined
    
    studies = load_study_table(study_path)
    combined.stats["study_table_path"] = str(study_path)
    combined.stats["study_count"] = len(studies)
    
    # Validate evidence levels
    level_result = validate_evidence_levels(studies)
    combined.errors.extend(level_result.errors)
    combined.warnings.extend(level_result.warnings)
    combined.stats.update(level_result.stats)
    if not level_result.passed:
        combined.passed = False
    
    # Validate preprint marking
    preprint_result = validate_preprint_marking(studies)
    combined.errors.extend(preprint_result.errors)
    combined.warnings.extend(preprint_result.warnings)
    combined.stats.update(preprint_result.stats)
    if not preprint_result.passed:
        combined.passed = False
    
    # Validate Issues CSV references
    if issues_path:
        issues = load_issues_csv(issues_path)
        study_ids = {s.get("Row_ID", "") for s in studies if s.get("Row_ID")}
        
        ref_result = validate_issues_evidence_refs(issues, study_ids)
        combined.errors.extend(ref_result.errors)
        combined.warnings.extend(ref_result.warnings)
        combined.stats.update(ref_result.stats)
        if not ref_result.passed:
            combined.passed = False
        
        # Validate key claims
        claims_result = validate_key_claims(issues, studies)
        combined.warnings.extend(claims_result.warnings)
        combined.stats.update(claims_result.stats)
    else:
        combined.warnings.append("Issues CSV not found; skipping cross-reference validation.")
    
    # In strict mode, warnings become errors
    if strict and combined.warnings:
        combined.errors.extend(combined.warnings)
        combined.warnings = []
        combined.passed = False
    
    return combined


def cmd_validate(args: argparse.Namespace) -> int:
    """Run validation."""
    paper_dir = Path(args.paper_dir).resolve()
    
    if not paper_dir.exists():
        print(f"error: paper directory not found: {paper_dir}", file=sys.stderr)
        return 1
    
    result = run_validation(paper_dir, strict=args.strict)
    
    # Print summary
    print("=" * 60)
    print("Evidence Ladder Validation Report")
    print("=" * 60)
    
    print(f"\nStudy table: {result.stats.get('study_table_path', 'N/A')}")
    print(f"Total studies: {result.stats.get('study_count', 0)}")
    
    if "by_level" in result.stats:
        print("\nEvidence Level Distribution:")
        for level in ["L0", "L1", "L2", "L3"]:
            count = result.stats["by_level"].get(level, 0)
            total = result.stats.get("total_studies", 1)
            pct = count / total * 100 if total > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {level}: {count:3d} ({pct:5.1f}%) {bar}")
    
    if "preprint_status" in result.stats:
        print("\nPreprint Status:")
        for status, count in result.stats["preprint_status"].items():
            print(f"  {status}: {count}")
    
    if result.errors:
        print(f"\n❌ ERRORS ({len(result.errors)}):")
        for err in result.errors:
            print(f"  - {err}")
    
    if result.warnings:
        print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
        for warn in result.warnings:
            print(f"  - {warn}")
    
    print("\n" + "=" * 60)
    if result.passed:
        print("✅ VALIDATION PASSED")
    else:
        print("❌ VALIDATION FAILED")
    print("=" * 60)
    
    return 0 if result.passed else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate evidence ladder assignments in Pharma×AI reviews."
    )
    parser.add_argument("paper_dir", help="Paper project directory.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    parser.set_defaults(fn=cmd_validate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
