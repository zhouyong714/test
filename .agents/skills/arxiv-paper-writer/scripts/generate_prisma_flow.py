#!/usr/bin/env python3
"""Generate PRISMA flow diagram data from prisma-counts.json.

Outputs:
  - Markdown summary for inclusion in review
  - JSON data suitable for diagram generation
  - LaTeX table for direct inclusion

Usage:
    python3 generate_prisma_flow.py <paper_dir>
    python3 generate_prisma_flow.py <paper_dir> --format latex
    python3 generate_prisma_flow.py <paper_dir> --format markdown
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def load_prisma_counts(paper_dir: Path) -> dict[str, Any]:
    """Load prisma-counts.json from paper directory."""
    counts_path = paper_dir / "notes" / "prisma-counts.json"
    if not counts_path.exists():
        raise FileNotFoundError(f"PRISMA counts file not found: {counts_path}")
    
    with counts_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_counts(data: dict[str, Any]) -> list[str]:
    """Validate PRISMA counts for internal consistency."""
    errors = []
    counts = data.get("counts", {})
    
    # Check identification totals
    ident = counts.get("identification", {})
    db_total = sum(ident.get("databases", {}).values())
    declared_total = ident.get("total_records", 0)
    
    if db_total + ident.get("registers", 0) + ident.get("other_sources", 0) != declared_total:
        errors.append(f"Identification total mismatch: databases={db_total}, declared={declared_total}")
    
    # Check dedup math
    after_dedup = ident.get("records_after_dedup", 0)
    expected_after = declared_total - ident.get("duplicates_removed", 0)
    if after_dedup != expected_after:
        errors.append(f"Dedup math error: {declared_total} - {ident.get('duplicates_removed', 0)} != {after_dedup}")
    
    # Check screening flow
    screening = counts.get("screening", {})
    title_abstract = screening.get("title_abstract", {})
    full_text = screening.get("full_text", {})
    
    screened = title_abstract.get("screened", 0)
    excluded = title_abstract.get("excluded", 0)
    
    if screened != after_dedup:
        errors.append(f"Title/abstract screened should equal records after dedup: {screened} != {after_dedup}")
    
    remaining_after_ta = screened - excluded
    sought = full_text.get("sought", 0)
    if sought != remaining_after_ta:
        errors.append(f"Full-text sought should equal remaining after T/A: {sought} != {remaining_after_ta}")
    
    # Check inclusion
    included = counts.get("included", {})
    ft_assessed = full_text.get("assessed", 0)
    ft_excluded = full_text.get("excluded", 0)
    studies_included = included.get("studies_in_review", 0)
    
    if studies_included != ft_assessed - ft_excluded:
        errors.append(f"Included studies mismatch: {ft_assessed} - {ft_excluded} != {studies_included}")
    
    return errors


def generate_flow_boxes(data: dict[str, Any]) -> dict[str, str]:
    """Generate text for PRISMA flow diagram boxes."""
    counts = data.get("counts", {})
    ident = counts.get("identification", {})
    screening = counts.get("screening", {})
    included = counts.get("included", {})
    
    databases = ident.get("databases", {})
    db_breakdown = ", ".join([f"{k}: {v}" for k, v in databases.items() if v > 0])
    
    ta = screening.get("title_abstract", {})
    ft = screening.get("full_text", {})
    
    ta_reasons = ta.get("reasons", {})
    ta_reasons_str = "; ".join([f"{k}: {v}" for k, v in ta_reasons.items() if v > 0])
    
    ft_reasons = ft.get("reasons", {})
    ft_reasons_str = "; ".join([f"{k}: {v}" for k, v in ft_reasons.items() if v > 0])
    
    evidence_levels = included.get("by_evidence_level", {})
    el_str = ", ".join([f"{k}: {v}" for k, v in evidence_levels.items() if v > 0])
    
    return {
        "identification": f"Records identified from databases (n={ident.get('total_records', 0)})\n({db_breakdown})",
        "registers": f"Records from registers (n={ident.get('registers', 0)})",
        "other": f"Other sources (n={ident.get('other_sources', 0)})",
        "duplicates": f"Duplicates removed (n={ident.get('duplicates_removed', 0)})",
        "after_dedup": f"Records after deduplication (n={ident.get('records_after_dedup', 0)})",
        "screened": f"Records screened (n={ta.get('screened', 0)})",
        "ta_excluded": f"Records excluded (n={ta.get('excluded', 0)})\n({ta_reasons_str})",
        "ft_sought": f"Full-text articles sought (n={ft.get('sought', 0)})",
        "ft_not_retrieved": f"Not retrieved (n={ft.get('not_retrieved', 0)})",
        "ft_assessed": f"Full-text assessed for eligibility (n={ft.get('assessed', 0)})",
        "ft_excluded": f"Full-text excluded (n={ft.get('excluded', 0)})\n({ft_reasons_str})",
        "included": f"Studies included in review (n={included.get('studies_in_review', 0)})\n({el_str})",
    }


def format_markdown(data: dict[str, Any]) -> str:
    """Generate Markdown summary of PRISMA flow."""
    counts = data.get("counts", {})
    ident = counts.get("identification", {})
    screening = counts.get("screening", {})
    included = counts.get("included", {})
    
    boxes = generate_flow_boxes(data)
    
    md = """# PRISMA Flow Summary

## Identification

| Source | Records |
|--------|---------|
"""
    for source, count in ident.get("databases", {}).items():
        if count > 0:
            md += f"| {source} | {count} |\n"
    
    md += f"| Registers | {ident.get('registers', 0)} |\n"
    md += f"| Other sources | {ident.get('other_sources', 0)} |\n"
    md += f"| **Total** | **{ident.get('total_records', 0)}** |\n"
    md += f"| Duplicates removed | {ident.get('duplicates_removed', 0)} |\n"
    md += f"| **After deduplication** | **{ident.get('records_after_dedup', 0)}** |\n"
    
    md += """
## Screening

### Title/Abstract Screening

| Metric | Count |
|--------|-------|
"""
    ta = screening.get("title_abstract", {})
    md += f"| Screened | {ta.get('screened', 0)} |\n"
    md += f"| Excluded | {ta.get('excluded', 0)} |\n"
    
    for reason, count in ta.get("reasons", {}).items():
        if count > 0:
            md += f"| - {reason} | {count} |\n"
    
    md += """
### Full-Text Screening

| Metric | Count |
|--------|-------|
"""
    ft = screening.get("full_text", {})
    md += f"| Sought | {ft.get('sought', 0)} |\n"
    md += f"| Not retrieved | {ft.get('not_retrieved', 0)} |\n"
    md += f"| Assessed | {ft.get('assessed', 0)} |\n"
    md += f"| Excluded | {ft.get('excluded', 0)} |\n"
    
    for reason, count in ft.get("reasons", {}).items():
        if count > 0:
            md += f"| - {reason} | {count} |\n"
    
    md += """
## Included Studies

| Metric | Count |
|--------|-------|
"""
    md += f"| **Total included** | **{included.get('studies_in_review', 0)}** |\n"
    
    md += "\n### By Evidence Level\n\n"
    for level, count in included.get("by_evidence_level", {}).items():
        md += f"- {level}: {count}\n"
    
    md += "\n### By Study Type\n\n"
    for stype, count in included.get("by_study_type", {}).items():
        if count > 0:
            md += f"- {stype}: {count}\n"
    
    preprints = included.get("preprints", {})
    md += f"""
### Preprint Status

- Total preprints: {preprints.get('total', 0)}
- Upgraded to published: {preprints.get('upgraded_to_published', 0)}
- Still preprint: {preprints.get('still_preprint', 0)}
"""
    
    return md


def format_latex(data: dict[str, Any]) -> str:
    """Generate LaTeX table for PRISMA summary."""
    counts = data.get("counts", {})
    ident = counts.get("identification", {})
    screening = counts.get("screening", {})
    included = counts.get("included", {})
    
    latex = r"""\begin{table}[htbp]
\centering
\caption{PRISMA Flow Summary}
\label{tab:prisma}
\begin{tabular}{lr}
\toprule
\textbf{Stage} & \textbf{Count} \\
\midrule
\multicolumn{2}{l}{\textit{Identification}} \\
"""
    
    for source, count in ident.get("databases", {}).items():
        if count > 0:
            latex += f"\\quad {source} & {count} \\\\\n"
    
    latex += f"\\quad Total records & {ident.get('total_records', 0)} \\\\\n"
    latex += f"\\quad Duplicates removed & {ident.get('duplicates_removed', 0)} \\\\\n"
    latex += f"\\quad After deduplication & {ident.get('records_after_dedup', 0)} \\\\\n"
    latex += "\\midrule\n"
    
    ta = screening.get("title_abstract", {})
    ft = screening.get("full_text", {})
    
    latex += r"\multicolumn{2}{l}{\textit{Screening}} \\" + "\n"
    latex += f"\\quad Title/abstract screened & {ta.get('screened', 0)} \\\\\n"
    latex += f"\\quad Title/abstract excluded & {ta.get('excluded', 0)} \\\\\n"
    latex += f"\\quad Full-text assessed & {ft.get('assessed', 0)} \\\\\n"
    latex += f"\\quad Full-text excluded & {ft.get('excluded', 0)} \\\\\n"
    latex += "\\midrule\n"
    
    latex += r"\multicolumn{2}{l}{\textit{Included}} \\" + "\n"
    latex += f"\\quad \\textbf{{Studies in review}} & \\textbf{{{included.get('studies_in_review', 0)}}} \\\\\n"
    
    for level, count in included.get("by_evidence_level", {}).items():
        if count > 0:
            latex += f"\\quad \\quad {level} & {count} \\\\\n"
    
    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    
    return latex


def format_json(data: dict[str, Any]) -> str:
    """Generate enhanced JSON with flow boxes."""
    output = {
        "counts": data.get("counts", {}),
        "flow_boxes": generate_flow_boxes(data),
        "generated_at": datetime.now().isoformat(),
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate PRISMA flow output."""
    paper_dir = Path(args.paper_dir).resolve()
    
    try:
        data = load_prisma_counts(paper_dir)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    
    # Validate
    errors = validate_counts(data)
    if errors and not args.force:
        print("Validation errors found:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        print("Use --force to generate anyway.", file=sys.stderr)
        return 1
    
    if errors and args.force:
        print("Warning: generating despite validation errors", file=sys.stderr)
    
    # Generate output
    if args.format == "markdown":
        output = format_markdown(data)
    elif args.format == "latex":
        output = format_latex(data)
    else:
        output = format_json(data)
    
    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output written to: {out_path}")
    else:
        print(output)
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate PRISMA flow diagram data from prisma-counts.json."
    )
    parser.add_argument("paper_dir", help="Paper project directory.")
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "latex"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument("--output", "-o", help="Output file path (default: stdout).")
    parser.add_argument("--force", action="store_true", help="Generate even if validation fails.")
    parser.set_defaults(fn=cmd_generate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
