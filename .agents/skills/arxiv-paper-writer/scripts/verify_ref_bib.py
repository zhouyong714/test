#!/usr/bin/env python3
"""Verify that BibTeX entries are reachable from authoritative online sources.

This is a lightweight audit for the "verified citations" requirement in this repo:
- If an entry has a DOI, we fetch BibTeX from doi.org (Crossref fallback).
- Otherwise, we try arXiv (abs page) when an arXiv ID can be inferred.
- Otherwise, we try the entry URL (HTTP 200-399).

Outputs a CSV log (default: <project_dir>/notes/citation-verification.csv).

Usage:
  python verify_ref_bib.py --project-dir <paper_dir> [--strict] [--limit N]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import concurrent.futures as cf
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s<>\"'}]+)", re.IGNORECASE)


@dataclass
class CheckResult:
    cite_key: str
    id_type: str
    identifier: str
    check_url: str
    ok: bool
    http_status: str
    error: str


def _extract_field(entry: str, field: str) -> str:
    pattern = re.compile(rf"(?is)\b{re.escape(field)}\s*=\s*")
    match = pattern.search(entry)
    if not match:
        return ""

    i = match.end()
    while i < len(entry) and entry[i].isspace():
        i += 1
    if i >= len(entry):
        return ""

    if entry[i] == "{":
        depth = 0
        j = i
        while j < len(entry):
            ch = entry[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return entry[i + 1 : j].strip()
            j += 1
        return ""
    if entry[i] == '"':
        j = i + 1
        while j < len(entry):
            ch = entry[j]
            if ch == '"' and entry[j - 1] != "\\":
                return entry[i + 1 : j].strip()
            j += 1
        return ""

    # Fallback: read until comma or newline.
    j = i
    while j < len(entry) and entry[j] not in ",\n\r":
        j += 1
    return entry[i:j].strip().strip("{}\"")


def _normalize_doi(text: str) -> str | None:
    text = (text or "").strip()
    if not text:
        return None
    text = re.sub(r"^doi:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    match = DOI_RE.search(text)
    if not match:
        return None
    return match.group(1).strip().rstrip(".").lower()


def _urlopen_ok(req: urllib.request.Request, *, timeout_s: int) -> tuple[bool, str, str]:
    last_err: str = ""
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                status = getattr(resp, "status", None)
                status_text = str(status) if status is not None else ""
                _ = resp.read(256)
            ok = status is None or 200 <= int(status) < 400
            return ok, status_text, ""
        except urllib.error.HTTPError as e:
            code = int(getattr(e, "code", 0) or 0)
            if code in {429, 503} and attempt < 3:
                time.sleep(0.5 * (2**attempt))
                continue
            ok = 200 <= code < 400
            return ok, str(code) if code else "", str(e)
        except urllib.error.URLError as e:
            last_err = str(e)
            if attempt < 3:
                time.sleep(0.5 * (2**attempt))
                continue
            return False, "", last_err
        except Exception as e:
            last_err = str(e)
            if attempt < 3:
                time.sleep(0.5 * (2**attempt))
                continue
            return False, "", last_err
    return False, "", last_err or "unknown error"


def _fetch_bibtex_for_doi(doi: str, *, timeout_s: int) -> tuple[bool, str, str]:
    url = f"https://doi.org/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/x-bibtex; charset=utf-8",
            "User-Agent": "verify-ref-bib/2.4 (+https://github.com/latex-arxiv-skill)",
        },
        method="GET",
    )
    ok, status, err = _urlopen_ok(req, timeout_s=timeout_s)
    if ok:
        return True, status, ""

    # Crossref fallback.
    xf = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}/transform/application/x-bibtex"
    req2 = urllib.request.Request(
        xf,
        headers={
            "Accept": "application/x-bibtex; charset=utf-8",
            "User-Agent": "verify-ref-bib/2.4 (+https://github.com/latex-arxiv-skill)",
        },
        method="GET",
    )
    ok2, status2, err2 = _urlopen_ok(req2, timeout_s=timeout_s)
    return ok2, status2, err2 or err


def _infer_arxiv_id(entry: str) -> str | None:
    # Prefer explicit eprint.
    eprint = _extract_field(entry, "eprint")
    if eprint and re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", eprint):
        return eprint

    url = _extract_field(entry, "url")
    if url:
        m = re.search(r"arxiv\.org/abs/([0-9]{4}\.[0-9]{4,5}(v\d+)?)", url)
        if m:
            return m.group(1)
    return None


def _check_arxiv_abs(arxiv_id: str, *, timeout_s: int) -> tuple[bool, str, str]:
    url = f"https://arxiv.org/abs/{arxiv_id}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "verify-ref-bib/2.4 (+https://github.com/latex-arxiv-skill)"},
        method="GET",
    )
    return _urlopen_ok(req, timeout_s=timeout_s)


def _check_url(url: str, *, timeout_s: int) -> tuple[bool, str, str]:
    # Some sites dislike HEAD; use GET with small read.
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "verify-ref-bib/2.4 (+https://github.com/latex-arxiv-skill)"},
        method="GET",
    )
    return _urlopen_ok(req, timeout_s=timeout_s)


def _parse_bibtex_file(bib_path: Path) -> list[tuple[str, str]]:
    content = bib_path.read_text(encoding="utf-8")
    pattern = re.compile(r"@\w+\s*\{([^,]+),([^@]*)", re.DOTALL)
    entries: list[tuple[str, str]] = []
    for match in pattern.finditer(content):
        cite_key = match.group(1).strip()
        entry_text = match.group(0)
        entries.append((cite_key, entry_text))
    return entries


def _check_entry(cite_key: str, entry_text: str, *, timeout_s: int) -> CheckResult:
    doi = _normalize_doi(_extract_field(entry_text, "doi"))
    if doi:
        ok, status, err = _fetch_bibtex_for_doi(doi, timeout_s=timeout_s)
        return CheckResult(
            cite_key=cite_key,
            id_type="doi",
            identifier=doi,
            check_url=f"https://doi.org/{doi}",
            ok=ok,
            http_status=status,
            error=err,
        )

    arxiv_id = _infer_arxiv_id(entry_text)
    if arxiv_id:
        ok, status, err = _check_arxiv_abs(arxiv_id, timeout_s=timeout_s)
        return CheckResult(
            cite_key=cite_key,
            id_type="arxiv",
            identifier=arxiv_id,
            check_url=f"https://arxiv.org/abs/{arxiv_id}",
            ok=ok,
            http_status=status,
            error=err,
        )

    url = _extract_field(entry_text, "url")
    if url:
        ok, status, err = _check_url(url, timeout_s=timeout_s)
        return CheckResult(
            cite_key=cite_key,
            id_type="url",
            identifier=url,
            check_url=url,
            ok=ok,
            http_status=status,
            error=err,
        )

    return CheckResult(
        cite_key=cite_key,
        id_type="missing",
        identifier="",
        check_url="",
        ok=False,
        http_status="",
        error="no doi/arxiv/url field found",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify BibTeX entries against online sources")
    parser.add_argument("--project-dir", required=True, help="Paper directory containing ref.bib")
    parser.add_argument("--out", help="Output CSV path (default: <project_dir>/notes/citation-verification.csv)")
    parser.add_argument("--strict", action="store_true", help="Fail if any entry cannot be verified")
    parser.add_argument("--limit", type=int, default=0, help="Only check first N entries (0 = all)")
    parser.add_argument("--sleep-ms", type=int, default=150, help="Sleep between checks (rate limiting)")
    parser.add_argument("--timeout-s", type=int, default=15, help="Per-request timeout in seconds")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent workers (use 1 for serial)")
    args = parser.parse_args()

    project_dir = Path(args.project_dir)
    bib_path = project_dir / "ref.bib"
    if not bib_path.exists():
        print(f"error: missing {bib_path}", file=sys.stderr)
        return 1

    out_path = Path(args.out) if args.out else (project_dir / "notes" / "citation-verification.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    entries = _parse_bibtex_file(bib_path)
    if args.limit and args.limit > 0:
        entries = entries[: args.limit]

    results: list[CheckResult] = []
    ok_count = 0
    fail_count = 0

    started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Verifying {len(entries)} entries from {bib_path}")
    print(f"Started: {started}")

    if args.workers <= 1:
        for i, (cite_key, entry_text) in enumerate(entries, start=1):
            r = _check_entry(cite_key, entry_text, timeout_s=args.timeout_s)
            results.append(r)
            if r.ok:
                ok_count += 1
            else:
                fail_count += 1
            if args.sleep_ms > 0:
                time.sleep(args.sleep_ms / 1000.0)
            if i % 25 == 0 or i == len(entries):
                print(f"  checked {i}/{len(entries)} (ok={ok_count}, fail={fail_count})")
    else:
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = [
                ex.submit(_check_entry, cite_key, entry_text, timeout_s=args.timeout_s)
                for cite_key, entry_text in entries
            ]
            completed = 0
            for fut in cf.as_completed(futures):
                r = fut.result()
                results.append(r)
                completed += 1
                if r.ok:
                    ok_count += 1
                else:
                    fail_count += 1
                if args.sleep_ms > 0:
                    time.sleep(args.sleep_ms / 1000.0)
                if completed % 25 == 0 or completed == len(entries):
                    print(f"  checked {completed}/{len(entries)} (ok={ok_count}, fail={fail_count})")

    # Write CSV log.
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "cite_key",
                "id_type",
                "identifier",
                "check_url",
                "ok",
                "http_status",
                "error",
            ]
        )
        for r in results:
            writer.writerow([r.cite_key, r.id_type, r.identifier, r.check_url, "Y" if r.ok else "N", r.http_status, r.error])

    finished = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Finished: {finished}")
    print(f"OK: {ok_count}  FAIL: {fail_count}")
    print(f"Log: {out_path}")

    if fail_count > 0 and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
