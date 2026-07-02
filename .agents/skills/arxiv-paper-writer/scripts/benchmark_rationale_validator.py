#!/usr/bin/env python3
"""Benchmark rationale validator.

Validates that benchmark selections in the catalog and Issues CSV have
proper rationales based on selection principles (P1-P5).

Principles:
  P1: Scope Alignment - Benchmark tests capabilities within review scope
  P2: Citation Threshold - Cited by ≥2 papers in review corpus
  P3: Temporal Relevance - Active submissions within 2 years
  P4: Reproducibility Score - Standard splits and public data
  P5: Coverage Balance - Together cover taxonomy axes

Usage:
    python3 benchmark_rationale_validator.py <paper_dir>
    python3 benchmark_rationale_validator.py <paper_dir> --strict
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# Principle keywords to look for in rationales
PRINCIPLE_KEYWORDS = {
    "P1": ["scope", "aligned", "within scope", "scope-aligned", "relevant to", "matches scope"],
    "P2": ["citation", "cited", "papers", "corpus", "mention", "referenced"],
    "P3": ["recent", "temporal", "active", "year", "2023", "2024", "2025", "new", "emerging"],
    "P4": ["reproducib", "standard split", "public data", "leaderboard", "benchmark"],
    "P5": ["coverage", "balance", "taxonomy", "axis", "task coverage", "gap"],
}


@dataclass
class ValidationResult:
    """Validation result."""
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)


def load_catalog(paper_dir: Path) -> dict[str, Any] | None:
    """Load benchmark catalog."""
    catalog_path = paper_dir / "notes" / "benchmark-catalog.yaml"
    if not catalog_path.exists():
        return None
    
    with catalog_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_benchmark_table(paper_dir: Path) -> list[dict[str, str]]:
    """Load benchmark table CSV."""
    candidates = [
        paper_dir / "notes" / "dataset-benchmark-table.csv",
        paper_dir / "notes" / "benchmark-table.csv",
    ]
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8", newline="") as f:
                return list(csv.DictReader(f))
    return []


def load_issues_csv(paper_dir: Path) -> list[dict[str, str]]:
    """Load Issues CSV."""
    issues_dir = paper_dir / "issues"
    if not issues_dir.exists():
        return []
    
    csvs = list(issues_dir.glob("*.csv"))
    if not csvs:
        return []
    
    latest = max(csvs, key=lambda p: p.stat().st_mtime)
    with latest.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_rationale_quality(rationale: str) -> tuple[bool, list[str]]:
    """Check if rationale mentions selection principles."""
    if not rationale or not rationale.strip():
        return False, []
    
    rationale_lower = rationale.lower()
    mentioned_principles = []
    
    for principle, keywords in PRINCIPLE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in rationale_lower:
                mentioned_principles.append(principle)
                break
    
    return len(mentioned_principles) >= 1, mentioned_principles


def validate_catalog_rationales(catalog: dict[str, Any]) -> ValidationResult:
    """Validate rationales in benchmark catalog."""
    result = ValidationResult()
    
    selected = catalog.get("selected", [])
    if not selected:
        result.warnings.append("No benchmarks in 'selected' list.")
        return result
    
    missing_rationale = []
    weak_rationale = []
    principles_mentioned: dict[str, int] = {}
    
    for item in selected:
        name = item.get("benchmark_name", "unknown")
        rationale = item.get("selection_rationale", "")
        
        if not rationale or not rationale.strip():
            missing_rationale.append(name)
            result.passed = False
            continue
        
        is_quality, principles = check_rationale_quality(rationale)
        if not is_quality:
            weak_rationale.append(f"{name}: '{rationale[:50]}...'")
        
        for p in principles:
            principles_mentioned[p] = principles_mentioned.get(p, 0) + 1
    
    if missing_rationale:
        result.errors.append(f"Missing selection_rationale: {missing_rationale}")
    
    if weak_rationale:
        result.warnings.append(
            f"Weak rationales (no principle keywords): {weak_rationale[:3]}"
            + (f" (+{len(weak_rationale)-3} more)" if len(weak_rationale) > 3 else "")
        )
    
    result.stats["selected_count"] = len(selected)
    result.stats["missing_rationale"] = len(missing_rationale)
    result.stats["weak_rationale"] = len(weak_rationale)
    result.stats["principles_mentioned"] = principles_mentioned
    
    return result


def validate_benchmark_table_rationales(benchmarks: list[dict[str, str]]) -> ValidationResult:
    """Validate rationales in benchmark table CSV."""
    result = ValidationResult()
    
    if not benchmarks:
        result.warnings.append("Benchmark table is empty.")
        return result
    
    # Check for Selection_Rationale column
    if benchmarks and "Selection_Rationale" not in benchmarks[0]:
        result.warnings.append("Benchmark table missing 'Selection_Rationale' column.")
        return result
    
    missing = []
    weak = []
    
    for row in benchmarks:
        row_id = row.get("Row_ID", "unknown")
        name = row.get("Benchmark_Name", "unknown")
        rationale = row.get("Selection_Rationale", "")
        
        if not rationale or not rationale.strip():
            missing.append(f"{row_id}: {name}")
            result.passed = False
            continue
        
        is_quality, _ = check_rationale_quality(rationale)
        if not is_quality:
            weak.append(f"{row_id}: {name}")
    
    if missing:
        result.errors.append(f"Missing Selection_Rationale in table: {missing[:5]}")
    
    if weak:
        result.warnings.append(f"Weak rationales in table: {weak[:5]}")
    
    result.stats["table_count"] = len(benchmarks)
    result.stats["table_missing"] = len(missing)
    result.stats["table_weak"] = len(weak)
    
    return result


def validate_issues_benchmark_rationales(issues: list[dict[str, str]]) -> ValidationResult:
    """Validate Benchmark_Selection_Rationale in Issues CSV."""
    result = ValidationResult()
    
    # Check if column exists
    if issues and "Benchmark_Selection_Rationale" not in issues[0]:
        result.stats["column_present"] = False
        return result
    
    result.stats["column_present"] = True
    
    issues_with_rationale = 0
    missing = []
    weak = []
    
    for issue in issues:
        issue_id = issue.get("Issue_ID", "unknown")
        issue_type = issue.get("Issue_Type", "")
        rationale = issue.get("Benchmark_Selection_Rationale", "")
        
        # Only check issues that might reference benchmarks
        if not issue_type.startswith("W"):  # Writing issues
            continue
        
        if rationale and rationale.strip():
            issues_with_rationale += 1
            is_quality, _ = check_rationale_quality(rationale)
            if not is_quality:
                weak.append(issue_id)
    
    if weak:
        result.warnings.append(f"Issues with weak benchmark rationales: {weak[:5]}")
    
    result.stats["issues_with_benchmark_rationale"] = issues_with_rationale
    result.stats["issues_weak_rationale"] = len(weak)
    
    return result


def validate_coverage(catalog: dict[str, Any]) -> ValidationResult:
    """Validate that benchmark selection covers scope."""
    result = ValidationResult()
    
    coverage = catalog.get("coverage", {})
    
    tasks_missing = coverage.get("tasks_missing", [])
    modalities_missing = coverage.get("modalities_missing", [])
    stages_missing = coverage.get("r_and_d_stages_missing", [])
    
    if tasks_missing:
        result.warnings.append(f"Tasks not covered by any benchmark: {tasks_missing}")
    
    if modalities_missing:
        result.warnings.append(f"Modalities not covered: {modalities_missing}")
    
    if stages_missing:
        result.warnings.append(f"R&D stages not covered: {stages_missing}")
    
    result.stats["coverage"] = coverage
    
    return result


def validate_no_excluded_selected(catalog: dict[str, Any]) -> ValidationResult:
    """Validate that no excluded benchmarks are in selected list."""
    result = ValidationResult()
    
    excluded_names = {e.get("name", "").lower() for e in catalog.get("excluded", [])}
    selected = catalog.get("selected", [])
    
    violations = []
    for item in selected:
        name = item.get("benchmark_name", "").lower()
        if name in excluded_names:
            violations.append(item.get("benchmark_name"))
    
    if violations:
        result.errors.append(f"Excluded benchmarks appear in selected: {violations}")
        result.passed = False
    
    return result


def run_validation(paper_dir: Path, *, strict: bool = False) -> ValidationResult:
    """Run all benchmark rationale validations."""
    combined = ValidationResult()
    
    # Load catalog
    catalog = load_catalog(paper_dir)
    if catalog is None:
        combined.warnings.append("Benchmark catalog not found (notes/benchmark-catalog.yaml).")
    else:
        # Validate catalog rationales
        cat_result = validate_catalog_rationales(catalog)
        combined.errors.extend(cat_result.errors)
        combined.warnings.extend(cat_result.warnings)
        combined.stats.update(cat_result.stats)
        if not cat_result.passed:
            combined.passed = False
        
        # Validate coverage
        cov_result = validate_coverage(catalog)
        combined.warnings.extend(cov_result.warnings)
        combined.stats.update(cov_result.stats)
        
        # Validate no excluded in selected
        exc_result = validate_no_excluded_selected(catalog)
        combined.errors.extend(exc_result.errors)
        if not exc_result.passed:
            combined.passed = False
    
    # Load and validate benchmark table
    benchmarks = load_benchmark_table(paper_dir)
    if benchmarks:
        table_result = validate_benchmark_table_rationales(benchmarks)
        combined.errors.extend(table_result.errors)
        combined.warnings.extend(table_result.warnings)
        combined.stats.update(table_result.stats)
        if not table_result.passed:
            combined.passed = False
    
    # Load and validate Issues CSV
    issues = load_issues_csv(paper_dir)
    if issues:
        issues_result = validate_issues_benchmark_rationales(issues)
        combined.warnings.extend(issues_result.warnings)
        combined.stats.update(issues_result.stats)
    
    # Strict mode
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
    
    # Print report
    print("=" * 60)
    print("Benchmark Rationale Validation Report")
    print("=" * 60)
    
    if "selected_count" in result.stats:
        print(f"\nCatalog selected benchmarks: {result.stats['selected_count']}")
        print(f"  Missing rationale: {result.stats.get('missing_rationale', 0)}")
        print(f"  Weak rationale: {result.stats.get('weak_rationale', 0)}")
        
        if "principles_mentioned" in result.stats:
            print("\nPrinciples referenced:")
            for p, count in sorted(result.stats["principles_mentioned"].items()):
                print(f"  {p}: {count}")
    
    if "table_count" in result.stats:
        print(f"\nBenchmark table entries: {result.stats['table_count']}")
        print(f"  Missing rationale: {result.stats.get('table_missing', 0)}")
    
    if result.stats.get("column_present"):
        print(f"\nIssues with Benchmark_Selection_Rationale: {result.stats.get('issues_with_benchmark_rationale', 0)}")
    
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
        description="Validate benchmark selection rationales in Pharma×AI reviews."
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
