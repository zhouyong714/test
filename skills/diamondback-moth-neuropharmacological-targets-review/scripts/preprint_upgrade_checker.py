#!/usr/bin/env python3
"""Check bioRxiv/medRxiv preprints for published versions.

This script queries the bioRxiv API to check if preprints have been
published in peer-reviewed journals.

Usage:
    python preprint_upgrade_checker.py --project-dir <paper_dir> [--update-bib]
    python preprint_upgrade_checker.py --doi 10.1101/2024.01.01.123456
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# bioRxiv/medRxiv API endpoint
BIORXIV_API = "https://api.biorxiv.org/pubs/{server}/{doi_suffix}"

# Regex to extract DOI suffix from full DOI
DOI_PATTERN = re.compile(r"10\.1101/(\d{4}\.\d{2}\.\d{2}\.\d+)")

# BibTeX patterns for preprint detection
PREPRINT_PATTERNS = [
    re.compile(r"biorxiv", re.IGNORECASE),
    re.compile(r"medrxiv", re.IGNORECASE),
    re.compile(r"10\.1101/", re.IGNORECASE),
]


def is_preprint_entry(entry: str) -> bool:
    """Check if a BibTeX entry is a preprint."""
    for pattern in PREPRINT_PATTERNS:
        if pattern.search(entry):
            return True
    return False


def extract_doi_suffix(text: str) -> str | None:
    """Extract the DOI suffix (after 10.1101/) from text."""
    match = DOI_PATTERN.search(text)
    if match:
        return match.group(1)
    return None


def check_published_version(doi_suffix: str, server: str = "biorxiv") -> dict | None:
    """Query bioRxiv/medRxiv API for published version.
    
    Returns:
        dict with published DOI info if exists, None otherwise
    """
    url = BIORXIV_API.format(server=server, doi_suffix=doi_suffix)
    
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            if "collection" in data and data["collection"]:
                # API returns collection of publication records
                for record in data["collection"]:
                    if record.get("published_doi"):
                        return {
                            "preprint_doi": f"10.1101/{doi_suffix}",
                            "published_doi": record["published_doi"],
                            "published_journal": record.get("published_journal", "Unknown"),
                            "published_date": record.get("published_date", "Unknown"),
                        }
            return None
            
    except HTTPError as e:
        if e.code == 404:
            return None
        print(f"HTTP Error {e.code} for {doi_suffix}", file=sys.stderr)
        return None
    except URLError as e:
        print(f"URL Error for {doi_suffix}: {e.reason}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON response for {doi_suffix}", file=sys.stderr)
        return None


def parse_bibtex_file(bib_path: Path) -> list[tuple[str, str]]:
    """Parse BibTeX file and return list of (cite_key, entry_text) tuples."""
    content = bib_path.read_text(encoding="utf-8")
    entries = []
    
    # Simple BibTeX parser - find @type{key, ... }
    pattern = re.compile(r"@\w+\{([^,]+),([^@]*)", re.DOTALL)
    
    for match in pattern.finditer(content):
        cite_key = match.group(1).strip()
        entry_text = match.group(0)
        entries.append((cite_key, entry_text))
    
    return entries


def check_project_preprints(project_dir: Path) -> list[dict]:
    """Check all preprints in project's ref.bib for published versions."""
    bib_path = project_dir / "ref.bib"
    
    if not bib_path.exists():
        print(f"Error: {bib_path} not found", file=sys.stderr)
        return []
    
    entries = parse_bibtex_file(bib_path)
    results = []
    
    preprint_count = 0
    for cite_key, entry_text in entries:
        if is_preprint_entry(entry_text):
            preprint_count += 1
            doi_suffix = extract_doi_suffix(entry_text)
            
            if doi_suffix:
                # Determine server (bioRxiv vs medRxiv)
                server = "medrxiv" if "medrxiv" in entry_text.lower() else "biorxiv"
                
                print(f"Checking {cite_key} ({server}/10.1101/{doi_suffix})...", end=" ")
                
                result = check_published_version(doi_suffix, server)
                
                if result:
                    result["cite_key"] = cite_key
                    result["status"] = "UPGRADED"
                    results.append(result)
                    print(f"✓ Published: {result['published_doi']}")
                else:
                    results.append({
                        "cite_key": cite_key,
                        "preprint_doi": f"10.1101/{doi_suffix}",
                        "status": "PREPRINT",
                    })
                    print("✗ Still preprint")
                
                # Rate limiting
                time.sleep(0.5)
            else:
                print(f"Warning: Could not extract DOI from {cite_key}", file=sys.stderr)
    
    print(f"\nTotal preprints found: {preprint_count}")
    print(f"Upgraded to published: {sum(1 for r in results if r['status'] == 'UPGRADED')}")
    print(f"Still preprint: {sum(1 for r in results if r['status'] == 'PREPRINT')}")
    
    return results


def write_upgrade_log(project_dir: Path, results: list[dict]) -> None:
    """Write preprint upgrade log to notes directory."""
    notes_dir = project_dir / "notes"
    notes_dir.mkdir(exist_ok=True)
    
    log_path = notes_dir / "preprint-upgrade-log.md"
    
    with log_path.open("w", encoding="utf-8") as f:
        f.write("# Preprint Upgrade Check Log\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        total = len(results)
        upgraded = sum(1 for r in results if r["status"] == "UPGRADED")
        f.write(f"- Total preprints checked: {total}\n")
        f.write(f"- Upgraded to published: {upgraded}\n")
        f.write(f"- Still preprint: {total - upgraded}\n\n")
        
        if any(r["status"] == "UPGRADED" for r in results):
            f.write("## Upgraded Preprints\n\n")
            f.write("| Cite Key | Preprint DOI | Published DOI | Journal |\n")
            f.write("|----------|--------------|---------------|----------|\n")
            for r in results:
                if r["status"] == "UPGRADED":
                    f.write(f"| {r['cite_key']} | {r['preprint_doi']} | {r['published_doi']} | {r.get('published_journal', 'N/A')} |\n")
            f.write("\n")
        
        if any(r["status"] == "PREPRINT" for r in results):
            f.write("## Still Preprint\n\n")
            f.write("| Cite Key | Preprint DOI | Action |\n")
            f.write("|----------|--------------|--------|\n")
            for r in results:
                if r["status"] == "PREPRINT":
                    f.write(f"| {r['cite_key']} | {r['preprint_doi']} | Mark [Preprint] in text |\n")
            f.write("\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. For UPGRADED entries: Update `ref.bib` with published DOI\n")
        f.write("2. For PREPRINT entries: Ensure `[Preprint]` marker in text\n")
        f.write("3. Verify preprint policy compliance for each usage\n")
    
    print(f"\nUpgrade log written to: {log_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check bioRxiv/medRxiv preprints for published versions"
    )
    parser.add_argument("--project-dir", help="Paper project directory")
    parser.add_argument("--doi", help="Single DOI to check (e.g., 10.1101/2024.01.01.123456)")
    parser.add_argument("--update-bib", action="store_true", help="Update ref.bib with published versions")
    
    args = parser.parse_args()
    
    if args.doi:
        # Single DOI check
        doi_suffix = extract_doi_suffix(args.doi)
        if not doi_suffix:
            print(f"Error: Could not parse DOI: {args.doi}", file=sys.stderr)
            return 1
        
        print(f"Checking bioRxiv/medRxiv for: 10.1101/{doi_suffix}")
        
        for server in ["biorxiv", "medrxiv"]:
            result = check_published_version(doi_suffix, server)
            if result:
                print(f"\n✓ Found published version!")
                print(f"  Published DOI: {result['published_doi']}")
                print(f"  Journal: {result['published_journal']}")
                print(f"  Date: {result['published_date']}")
                return 0
        
        print("\n✗ No published version found. Still a preprint.")
        return 0
    
    elif args.project_dir:
        # Project-wide check
        project_dir = Path(args.project_dir)
        if not project_dir.exists():
            print(f"Error: Project directory not found: {project_dir}", file=sys.stderr)
            return 1
        
        results = check_project_preprints(project_dir)
        
        if results:
            write_upgrade_log(project_dir, results)
        
        return 0
    
    else:
        print("Error: Specify --project-dir or --doi", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
