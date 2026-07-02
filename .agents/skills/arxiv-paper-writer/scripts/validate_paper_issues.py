#!/usr/bin/env python3
"""Validate paper issues CSV schema and required fields.

Supports both standard schema and pharma v2.4 schema (64 columns).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

# Standard schema (10 columns)
REQUIRED_COLUMNS = [
    "ID",
    "Phase",
    "Title",
    "Description",
    "Target_Citations",
    "Visualization",
    "Acceptance",
    "Status",
    "Verified_Citations",
    "Notes",
]

# Pharma v2.4 schema - base columns (subset that must exist)
PHARMA_BASE_COLUMNS = [
    "Issue_ID",
    "Phase",
    "Type",
    "Section_Target",
    "Description",
    "Dependencies",
    "Priority",
    "Status",
    "Verified_Citations",
    "Notes",
]

# Pharma v2.4 playbook gate columns (must all be present in pharma mode)
PHARMA_PLAYBOOK_COLUMNS = [
    "has_context_pain_gap",
    "has_scope_deliverables",
    "has_taxonomy_map",
    "has_section_loop",
    "has_actionable_roadmap",
]

ALLOWED_STATUS = {"TODO", "DOING", "DONE", "SKIP"}
ALLOWED_PHASES = {"Research", "Writing", "Refinement", "QA"}


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def main() -> int:
    if len(sys.argv) < 2:
        return fail("usage: validate_paper_issues.py <issues.csv> [--strict] [--pharma]")

    path = Path(sys.argv[1])
    strict = "--strict" in sys.argv
    pharma_mode = "--pharma" in sys.argv

    if not path.exists():
        return fail(f"file not found: {path}")

    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if any(cell.strip() for cell in row):
                rows.append(row)

    if not rows:
        return fail("csv is empty")

    header = rows[0]
    
    # Determine schema based on mode and header
    if pharma_mode:
        # Check for pharma v2.4 schema
        missing_base = [col for col in PHARMA_BASE_COLUMNS if col not in header]
        if missing_base:
            return fail(
                f"Pharma mode requires v2.4 schema. Missing base columns: {missing_base}"
            )
        missing_playbook = [col for col in PHARMA_PLAYBOOK_COLUMNS if col not in header]
        if missing_playbook:
            return fail(
                f"Pharma mode requires playbook columns. Missing: {missing_playbook}"
            )
        print(f"Validating pharma v2.4 schema ({len(header)} columns)")
        id_column = "Issue_ID"
        required_fields = ["Issue_ID", "Phase", "Type", "Description", "Status"]
    else:
        # Standard schema
        if header != REQUIRED_COLUMNS:
            # Check if it's actually a pharma schema being validated without --pharma
            if "Issue_ID" in header and len(header) > 20:
                print("Note: Detected pharma v2.4 schema. Consider using --pharma flag.", file=sys.stderr)
            return fail(
                "invalid header. expected: "
                + ",".join(REQUIRED_COLUMNS)
                + " | got: "
                + ",".join(header)
            )
        id_column = "ID"
        required_fields = ["ID", "Phase", "Title", "Description", "Acceptance", "Status"]

    seen_ids: set[str] = set()
    total_target_citations = 0
    total_verified_citations = 0
    status_counts = {"TODO": 0, "DOING": 0, "DONE": 0, "SKIP": 0}
    phase_counts = {"Research": 0, "Writing": 0, "Refinement": 0, "QA": 0}
    playbook_compliance = {"Y": 0, "N": 0, "": 0}
    errors = 0
    warnings = 0

    for idx, row in enumerate(rows[1:], start=2):
        if len(row) != len(header):
            print(f"error: row {idx}: expected {len(header)} columns, got {len(row)}", file=sys.stderr)
            errors += 1
            continue

        row_data = dict(zip(header, row))

        # Check required fields
        for col in required_fields:
            if col in row_data and not row_data[col].strip():
                print(f"error: row {idx}: '{col}' is empty", file=sys.stderr)
                errors += 1

        # Validate Status
        status = row_data.get("Status", "").strip()
        if status not in ALLOWED_STATUS:
            print(f"error: row {idx}: 'Status' must be one of {sorted(ALLOWED_STATUS)}, got '{status}'", file=sys.stderr)
            errors += 1
        else:
            status_counts[status] += 1

        # Validate Phase
        phase = row_data.get("Phase", "").strip()
        if phase not in ALLOWED_PHASES:
            print(f"error: row {idx}: 'Phase' must be one of {sorted(ALLOWED_PHASES)}, got '{phase}'", file=sys.stderr)
            errors += 1
        else:
            phase_counts[phase] += 1

        # Check for duplicate IDs
        issue_id = row_data.get(id_column, "").strip()
        if issue_id in seen_ids:
            print(f"error: row {idx}: duplicate ID '{issue_id}'", file=sys.stderr)
            errors += 1
        seen_ids.add(issue_id)

        # Parse citation counts (standard mode uses Target_Citations, pharma uses Min_Citations)
        target_col = "Target_Citations" if not pharma_mode else "Min_Citations"
        if target_col in row_data:
            try:
                target = int(row_data[target_col].strip()) if row_data[target_col].strip() else 0
                total_target_citations += target
            except ValueError:
                if strict:
                    print(f"warning: row {idx}: '{target_col}' is not a number", file=sys.stderr)
                    warnings += 1

        if "Verified_Citations" in row_data:
            try:
                verified = int(row_data["Verified_Citations"].strip()) if row_data["Verified_Citations"].strip() else 0
                total_verified_citations += verified
            except ValueError:
                if strict:
                    print(f"warning: row {idx}: 'Verified_Citations' is not a number", file=sys.stderr)
                    warnings += 1

        # Pharma mode: validate playbook gates for Writing issues
        if pharma_mode and phase == "Writing":
            for gate_col in PHARMA_PLAYBOOK_COLUMNS:
                if gate_col in row_data:
                    val = row_data[gate_col].strip().upper()
                    if val in playbook_compliance:
                        playbook_compliance[val] += 1
                    elif val == "TODO":
                        playbook_compliance[""] += 1
                    elif strict and val not in ("Y", "N", "", "TODO"):
                        print(f"warning: row {idx}: '{gate_col}' should be Y/N, got '{val}'", file=sys.stderr)
                        warnings += 1

    if errors > 0:
        print(f"\nValidation failed with {errors} error(s).", file=sys.stderr)
        return 1

    # Print summary
    print("Validation passed!")
    print(f"\nSummary:")
    print(f"  Total issues: {len(rows) - 1}")
    print(
        "  By phase: "
        f"Research={phase_counts['Research']}, "
        f"Writing={phase_counts['Writing']}, "
        f"Refinement={phase_counts['Refinement']}, "
        f"QA={phase_counts['QA']}"
    )
    print(f"  By status: TODO={status_counts['TODO']}, DOING={status_counts['DOING']}, DONE={status_counts['DONE']}, SKIP={status_counts['SKIP']}")
    print(f"  Target citations: {total_target_citations}")
    print(f"  Verified citations: {total_verified_citations}")

    if total_target_citations > 0:
        progress = (total_verified_citations / total_target_citations) * 100
        print(f"  Citation progress: {progress:.1f}%")

    if status_counts["DONE"] > 0:
        completion = (status_counts["DONE"] / (len(rows) - 1)) * 100
        print(f"  Task completion: {completion:.1f}%")

    # Pharma mode: print playbook compliance summary
    if pharma_mode:
        total_gates = playbook_compliance["Y"] + playbook_compliance["N"] + playbook_compliance[""]
        if total_gates > 0:
            print(f"\nPlaybook Compliance:")
            print(f"  Passed (Y): {playbook_compliance['Y']}")
            print(f"  Failed (N): {playbook_compliance['N']}")
            print(f"  Pending: {playbook_compliance['']}")
            if playbook_compliance["Y"] > 0:
                compliance_pct = (playbook_compliance["Y"] / total_gates) * 100
                print(f"  Compliance rate: {compliance_pct:.1f}%")

    if warnings > 0:
        print(f"\n{warnings} warning(s) found.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
