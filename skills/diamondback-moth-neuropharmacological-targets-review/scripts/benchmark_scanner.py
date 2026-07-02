#!/usr/bin/env python3
"""Benchmark discovery and catalog generation.

Discovers benchmarks from:
  - Literature (papers in registry)
  - Papers With Code API
  - TDC (Therapeutics Data Commons)
  - Manual additions

Modes:
  - AUTO: Fully automated discovery from literature
  - HYBRID: Automated discovery + manual curation
  - MANUAL: Manual benchmark list only

Usage:
    python3 benchmark_scanner.py <paper_dir> --mode AUTO
    python3 benchmark_scanner.py <paper_dir> --mode HYBRID --add-benchmark "NewBench"
    python3 benchmark_scanner.py <paper_dir> --validate
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


# Known benchmark patterns for pharma/drug discovery
BENCHMARK_PATTERNS = [
    # MoleculeNet and derivatives
    r"\bMoleculeNet\b",
    r"\bTox21\b",
    r"\bSIDER\b",
    r"\bClinTox\b",
    r"\bBBBP\b",
    r"\bBACE\b",
    r"\bHIV\b",
    r"\bMUV\b",
    r"\bFreeSolv\b",
    r"\bLipophilicity\b",
    r"\bESoL\b",
    
    # TDC benchmarks
    r"\bTDC[-\s]ADMET\b",
    r"\bTherapeutics Data Commons\b",
    r"\bTDC\b",
    
    # Binding/interaction
    r"\bPDBbind\b",
    r"\bDavis\b",
    r"\bKIBA\b",
    r"\bBindingDB\b",
    r"\bChEMBL\b",
    
    # Molecular generation
    r"\bZINC\b",
    r"\bGUACamol\b",
    r"\bMOSES\b",
    
    # Docking
    r"\bDUD[-\s]?E\b",
    r"\bDECOYS\b",
    r"\bPOSIT\b",
    
    # ADMET specific
    r"\bADMET[-\s]?Benchmark\b",
    r"\bAqSol\b",
    r"\bCYP450\b",
    r"\bhERG\b",
    
    # General ML
    r"\bOGB[-\s]?Mol\b",
    r"\bPapers\s?With\s?Code\b",
    r"\bQM[789]\b",
]

# Known benchmark metadata
KNOWN_BENCHMARKS: dict[str, dict[str, Any]] = {
    "MoleculeNet": {
        "canonical_name": "MoleculeNet",
        "tasks": ["Property_Prediction", "ADMET_Prediction"],
        "modalities": ["SMILES", "Graph"],
        "source_url": "https://moleculenet.org",
        "citations": 2000,
        "year_introduced": 2017,
    },
    "TDC-ADMET": {
        "canonical_name": "TDC-ADMET",
        "tasks": ["ADMET_Prediction"],
        "modalities": ["SMILES"],
        "source_url": "https://tdcommons.ai",
        "citations": 500,
        "year_introduced": 2021,
    },
    "PDBbind": {
        "canonical_name": "PDBbind",
        "tasks": ["Binding_Affinity"],
        "modalities": ["3D_Structure"],
        "source_url": "http://www.pdbbind.org.cn",
        "citations": 1500,
        "year_introduced": 2004,
    },
    "ZINC": {
        "canonical_name": "ZINC",
        "tasks": ["Molecular_Generation", "Virtual_Screening"],
        "modalities": ["SMILES", "3D_Structure"],
        "source_url": "https://zinc.docking.org",
        "citations": 3000,
        "year_introduced": 2005,
    },
    "ChEMBL": {
        "canonical_name": "ChEMBL",
        "tasks": ["Property_Prediction", "Bioactivity"],
        "modalities": ["SMILES"],
        "source_url": "https://www.ebi.ac.uk/chembl/",
        "citations": 5000,
        "year_introduced": 2012,
    },
}


@dataclass
class BenchmarkCandidate:
    """A discovered benchmark candidate."""
    name: str
    canonical_name: str = ""
    tasks: list[str] = field(default_factory=list)
    modalities: list[str] = field(default_factory=list)
    r_and_d_stages: list[str] = field(default_factory=list)
    citations: int = 0
    year_introduced: int = 0
    source_url: str = ""
    leaderboard_url: str = ""
    has_standard_split: bool = False
    split_types: list[str] = field(default_factory=list)
    primary_metric: str = ""
    discovery_source: str = ""
    mention_count: int = 0
    selection_reason: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "canonical_name": self.canonical_name or self.name,
            "tasks": self.tasks,
            "modalities": self.modalities,
            "r_and_d_stages": self.r_and_d_stages,
            "citations": self.citations,
            "year_introduced": self.year_introduced,
            "source_url": self.source_url,
            "leaderboard_url": self.leaderboard_url,
            "has_standard_split": self.has_standard_split,
            "split_types": self.split_types,
            "primary_metric": self.primary_metric,
            "discovery_source": self.discovery_source,
            "mention_count": self.mention_count,
            "selection_reason": self.selection_reason,
        }


def load_scope(paper_dir: Path) -> dict[str, Any]:
    """Load scope.yaml from paper directory."""
    scope_path = paper_dir / "notes" / "scope.yaml"
    if not scope_path.exists():
        return {}
    
    with scope_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def scan_registry_for_benchmarks(paper_dir: Path) -> list[BenchmarkCandidate]:
    """Scan arXiv registry for benchmark mentions."""
    db_path = paper_dir / "notes" / "arxiv-registry.sqlite3"
    if not db_path.exists():
        return []
    
    candidates: dict[str, BenchmarkCandidate] = {}
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    try:
        rows = conn.execute(
            "SELECT arxiv_id, title, summary FROM works;"
        ).fetchall()
        
        for row in rows:
            text = f"{row['title']} {row['summary'] or ''}"
            
            for pattern in BENCHMARK_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    name = match.strip()
                    if name not in candidates:
                        # Check if we have known metadata
                        known = KNOWN_BENCHMARKS.get(name, {})
                        candidates[name] = BenchmarkCandidate(
                            name=name,
                            canonical_name=known.get("canonical_name", name),
                            tasks=known.get("tasks", []),
                            modalities=known.get("modalities", []),
                            citations=known.get("citations", 0),
                            year_introduced=known.get("year_introduced", 0),
                            source_url=known.get("source_url", ""),
                            discovery_source="arxiv_registry",
                        )
                    candidates[name].mention_count += 1
    finally:
        conn.close()
    
    return list(candidates.values())


def scan_bibtex_for_benchmarks(paper_dir: Path) -> list[BenchmarkCandidate]:
    """Scan ref.bib for benchmark mentions."""
    bib_path = paper_dir / "ref.bib"
    if not bib_path.exists():
        return []
    
    candidates: dict[str, BenchmarkCandidate] = {}
    text = bib_path.read_text(encoding="utf-8", errors="replace")
    
    for pattern in BENCHMARK_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            name = match.strip()
            if name not in candidates:
                known = KNOWN_BENCHMARKS.get(name, {})
                candidates[name] = BenchmarkCandidate(
                    name=name,
                    canonical_name=known.get("canonical_name", name),
                    tasks=known.get("tasks", []),
                    modalities=known.get("modalities", []),
                    citations=known.get("citations", 0),
                    year_introduced=known.get("year_introduced", 0),
                    source_url=known.get("source_url", ""),
                    discovery_source="bibtex",
                )
            candidates[name].mention_count += 1
    
    return list(candidates.values())


def fetch_papers_with_code_benchmarks(task: str) -> list[BenchmarkCandidate]:
    """Fetch benchmarks from Papers With Code API."""
    # Note: This is a simplified implementation
    # Real implementation would use the PwC API
    url = f"https://paperswithcode.com/api/v1/datasets/?task={urllib.parse.quote(task)}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "benchmark-scanner/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            candidates = []
            for item in data.get("results", [])[:10]:
                candidates.append(BenchmarkCandidate(
                    name=item.get("name", ""),
                    source_url=item.get("url", ""),
                    discovery_source="papers_with_code",
                ))
            return candidates
    except Exception:
        return []


def categorize_into_pools(
    candidates: list[BenchmarkCandidate],
    scope: dict[str, Any],
) -> dict[str, list[BenchmarkCandidate]]:
    """Categorize candidates into priority pools."""
    pools: dict[str, list[BenchmarkCandidate]] = {
        "must_include": [],
        "high_relevance": [],
        "emerging": [],
        "domain_specific": [],
    }
    
    current_year = datetime.now().year
    scope_tasks = set(scope.get("scope", {}).get("tasks", []))
    
    for candidate in candidates:
        # Pool A: Must-Include (Foundational)
        if candidate.citations >= 500:
            candidate.selection_reason = f"Foundational benchmark; {candidate.citations}+ citations"
            pools["must_include"].append(candidate)
        # Pool B: High-Relevance
        elif candidate.citations >= 100 or candidate.mention_count >= 3:
            candidate.selection_reason = f"Widely used; {candidate.mention_count} mentions in corpus"
            pools["high_relevance"].append(candidate)
        # Pool C: Emerging
        elif candidate.year_introduced and candidate.year_introduced >= current_year - 2:
            candidate.selection_reason = f"Recent benchmark ({candidate.year_introduced}); gaining traction"
            pools["emerging"].append(candidate)
        # Pool D: Domain-Specific
        elif any(t in scope_tasks for t in candidate.tasks):
            candidate.selection_reason = "Domain-specific; matches scope tasks"
            pools["domain_specific"].append(candidate)
    
    return pools


def generate_catalog(
    pools: dict[str, list[BenchmarkCandidate]],
    scope: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    """Generate benchmark catalog YAML structure."""
    import hashlib
    
    scope_str = json.dumps(scope, sort_keys=True)
    scope_hash = hashlib.sha256(scope_str.encode()).hexdigest()[:12]
    
    catalog = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "scope_hash": scope_hash,
            "scope_file": "notes/scope.yaml",
            "discovery_mode": mode,
            "last_updated": datetime.now().isoformat(),
        },
        "selection_criteria": {
            "min_citations": 2,
            "max_age_years": 5,
            "require_public_data": True,
            "require_standard_split": True,
            "require_leaderboard": False,
        },
        "pools": {
            pool_name: [c.to_dict() for c in candidates]
            for pool_name, candidates in pools.items()
        },
        "excluded": [],
        "coverage": {
            "tasks_covered": [],
            "tasks_missing": [],
            "modalities_covered": [],
            "modalities_missing": [],
            "r_and_d_stages_covered": [],
            "r_and_d_stages_missing": [],
        },
        "selected": [],
        "validation": {
            "all_selected_have_rationale": False,
            "coverage_complete": False,
            "no_excluded_in_selected": True,
            "last_validated_at": "",
        },
    }
    
    # Analyze coverage
    all_tasks = set()
    all_modalities = set()
    for pool_candidates in pools.values():
        for c in pool_candidates:
            all_tasks.update(c.tasks)
            all_modalities.update(c.modalities)
    
    catalog["coverage"]["tasks_covered"] = list(all_tasks)
    catalog["coverage"]["modalities_covered"] = list(all_modalities)
    
    scope_tasks = set(scope.get("scope", {}).get("tasks", []))
    catalog["coverage"]["tasks_missing"] = list(scope_tasks - all_tasks)
    
    return catalog


def validate_catalog(paper_dir: Path) -> list[str]:
    """Validate existing benchmark catalog."""
    catalog_path = paper_dir / "notes" / "benchmark-catalog.yaml"
    if not catalog_path.exists():
        return ["Benchmark catalog not found"]
    
    errors = []
    
    with catalog_path.open("r", encoding="utf-8") as f:
        catalog = yaml.safe_load(f) or {}
    
    # Check that all selected have rationale
    for item in catalog.get("selected", []):
        if not item.get("selection_rationale"):
            errors.append(f"Missing selection_rationale for: {item.get('benchmark_name', 'unknown')}")
    
    # Check no excluded in selected
    excluded_names = {e.get("name") for e in catalog.get("excluded", [])}
    for item in catalog.get("selected", []):
        if item.get("benchmark_name") in excluded_names:
            errors.append(f"Excluded benchmark in selected: {item.get('benchmark_name')}")
    
    # Check coverage
    missing_tasks = catalog.get("coverage", {}).get("tasks_missing", [])
    if missing_tasks:
        errors.append(f"Tasks not covered by any benchmark: {missing_tasks}")
    
    return errors


def cmd_scan(args: argparse.Namespace) -> int:
    """Scan for benchmarks and generate catalog."""
    paper_dir = Path(args.paper_dir).resolve()
    
    if not paper_dir.exists():
        print(f"error: paper directory not found: {paper_dir}", file=sys.stderr)
        return 1
    
    scope = load_scope(paper_dir)
    
    # Discover candidates
    candidates: list[BenchmarkCandidate] = []
    
    if args.mode in ["AUTO", "HYBRID"]:
        # Scan registry
        registry_candidates = scan_registry_for_benchmarks(paper_dir)
        candidates.extend(registry_candidates)
        print(f"Found {len(registry_candidates)} candidates from arXiv registry")
        
        # Scan bibtex
        bibtex_candidates = scan_bibtex_for_benchmarks(paper_dir)
        candidates.extend(bibtex_candidates)
        print(f"Found {len(bibtex_candidates)} candidates from ref.bib")
    
    # Add manual benchmarks
    if args.add_benchmark:
        for name in args.add_benchmark:
            known = KNOWN_BENCHMARKS.get(name, {})
            candidates.append(BenchmarkCandidate(
                name=name,
                canonical_name=known.get("canonical_name", name),
                tasks=known.get("tasks", []),
                modalities=known.get("modalities", []),
                citations=known.get("citations", 0),
                year_introduced=known.get("year_introduced", 0),
                source_url=known.get("source_url", ""),
                discovery_source="manual",
            ))
    
    # Deduplicate
    seen = set()
    unique_candidates = []
    for c in candidates:
        key = c.canonical_name or c.name
        if key not in seen:
            seen.add(key)
            unique_candidates.append(c)
    
    print(f"Total unique candidates: {len(unique_candidates)}")
    
    # Categorize into pools
    pools = categorize_into_pools(unique_candidates, scope)
    
    for pool_name, pool_candidates in pools.items():
        print(f"  {pool_name}: {len(pool_candidates)}")
    
    # Generate catalog
    catalog = generate_catalog(pools, scope, args.mode)
    
    # Write output
    output_path = paper_dir / "notes" / "benchmark-catalog.yaml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(catalog, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"Catalog written to: {output_path}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate existing catalog."""
    paper_dir = Path(args.paper_dir).resolve()
    
    errors = validate_catalog(paper_dir)
    
    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    
    print("Catalog validation passed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark discovery and catalog generation for Pharma×AI reviews."
    )
    parser.add_argument("paper_dir", help="Paper project directory.")
    
    sub = parser.add_subparsers(dest="cmd")
    
    # Scan command (default)
    p_scan = sub.add_parser("scan", help="Scan for benchmarks and generate catalog.")
    p_scan.add_argument(
        "--mode",
        choices=["AUTO", "HYBRID", "MANUAL"],
        default="AUTO",
        help="Discovery mode (default: AUTO).",
    )
    p_scan.add_argument(
        "--add-benchmark",
        action="append",
        help="Manually add a benchmark by name.",
    )
    p_scan.set_defaults(fn=cmd_scan)
    
    # Validate command
    p_validate = sub.add_parser("validate", help="Validate existing catalog.")
    p_validate.set_defaults(fn=cmd_validate)
    
    # Default to scan if no subcommand
    parser.set_defaults(fn=cmd_scan, mode="AUTO", add_benchmark=None)
    
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
