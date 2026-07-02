#!/usr/bin/env python3
"""Fetch BibTeX entries for DOI identifiers and append to a .bib file.

This complements arxiv_registry.py for non-arXiv, DOI-addressable works
(journals, ChemRxiv, OpenReview with DOI, etc.).

Verification model:
  - A DOI is considered "verified" once a BibTeX payload is fetched from an
    authoritative online source (doi.org, with a Crossref fallback).
  - The fetched entry is then written to the project's ref.bib.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s<>\"']+)", re.IGNORECASE)

STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "to",
    "toward",
    "towards",
    "with",
}


def normalize_doi(text: str) -> str | None:
    text = (text or "").strip()
    if not text:
        return None
    # Accept DOI as raw, doi:..., or URL form.
    text = re.sub(r"^doi:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    match = DOI_RE.search(text)
    if not match:
        return None
    return match.group(1).strip().rstrip(".").lower()


def fetch_bibtex_from_doi_org(doi: str, *, timeout_s: int = 30) -> str:
    url = f"https://doi.org/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/x-bibtex; charset=utf-8",
            "User-Agent": "doi-bibtex/2.4 (+https://github.com/latex-arxiv-skill)",
        },
        method="GET",
    )
    last_err: Exception | None = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                charset = getattr(resp.headers, "get_content_charset", lambda: None)() or "utf-8"
                body = resp.read()
            return body.decode(charset, errors="replace").strip()
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in {429, 503} and attempt < 5:
                time.sleep(0.5 * (2 ** attempt))
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt < 5:
                time.sleep(0.5 * (2 ** attempt))
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("failed to fetch BibTeX from doi.org")


def fetch_bibtex_from_crossref(doi: str, *, timeout_s: int = 30) -> str:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}/transform/application/x-bibtex"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/x-bibtex; charset=utf-8",
            "User-Agent": "doi-bibtex/2.4 (+https://github.com/latex-arxiv-skill)",
        },
        method="GET",
    )
    last_err: Exception | None = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                charset = getattr(resp.headers, "get_content_charset", lambda: None)() or "utf-8"
                body = resp.read()
            return body.decode(charset, errors="replace").strip()
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in {429, 503} and attempt < 5:
                time.sleep(0.5 * (2 ** attempt))
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt < 5:
                time.sleep(0.5 * (2 ** attempt))
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("failed to fetch BibTeX from Crossref transform endpoint")


def ensure_newline(text: str) -> str:
    return text.rstrip() + "\n"


def sanitize_bibtex_ascii(text: str) -> str:
    """Make BibTeX payload safe for BibTeX (which is not Unicode-aware)."""
    text = (text or "").replace("\u00a0", " ")
    text = text.replace("\u2013", "--").replace("\u2014", "--")  # en/em dash
    text = text.replace("\u2212", "-")  # minus
    text = text.replace("\u2018", "'").replace("\u2019", "'")  # curly quotes
    text = text.replace("\u201c", "\"").replace("\u201d", "\"")
    text = text.replace("\u2026", "...")

    # Strip remaining non-ASCII (best-effort transliteration).
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def normalize_bibtex_fields(entry: str, doi: str) -> str:
    """Normalize a fetched BibTeX payload.

    - Lowercase common field names (doi/url) when they arrive as DOI/URL.
    - Normalize dx.doi.org URLs to https://doi.org/.
    - Ensure a doi field exists.
    """
    text = sanitize_bibtex_ascii(entry).strip()
    if not text.startswith("@"):
        raise ValueError("BibTeX payload does not start with '@'")

    # Normalize URL variants.
    text = re.sub(r"url\s*=\s*\{http://dx\.doi\.org/", "url={https://doi.org/", text, flags=re.IGNORECASE)
    text = re.sub(r"url\s*=\s*\{https?://dx\.doi\.org/", "url={https://doi.org/", text, flags=re.IGNORECASE)

    # Normalize DOI field name.
    text = re.sub(r"\bDOI\s*=", "doi=", text)

    # Ensure DOI field present.
    if not re.search(r"\bdoi\s*=\s*[{\"].+?[}\"],?", text, flags=re.IGNORECASE | re.DOTALL):
        # Insert before final closing brace.
        text = re.sub(r"\n\}\s*$", f",\n  doi={{ {doi} }}\n}}\n", ensure_newline(text))

    # Ensure URL field present (helpful for verification/audit).
    if not re.search(r"\burl\s*=\s*[{\"].+?[}\"],?", text, flags=re.IGNORECASE | re.DOTALL):
        text = re.sub(r"\n\}\s*$", f",\n  url={{ https://doi.org/{doi} }}\n}}\n", ensure_newline(text))

    return ensure_newline(text)


def extract_bibtex_entry_key(entry: str) -> str | None:
    match = re.search(r"@\w+\s*\{\s*([^,]+)\s*,", entry)
    return match.group(1).strip() if match else None


def rewrite_bibtex_key(entry: str, new_key: str) -> str:
    match = re.search(r"@(\w+)\s*\{\s*([^,]+)\s*,", entry)
    if not match:
        return entry
    start = match.start(2)
    end = match.end(2)
    return entry[:start] + new_key + entry[end:]


def _extract_bibtex_field(entry: str, field: str) -> str:
    """Extract a BibTeX field value (best-effort; supports {} and \"\" values)."""
    pattern = re.compile(rf"(?i)\b{re.escape(field)}\s*=\s*")
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

    # Fallback: read until comma or newline
    j = i
    while j < len(entry) and entry[j] not in ",\n\r":
        j += 1
    return entry[i:j].strip().strip("{}\"")


def _slug_word(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text)
    for w in words:
        lw = w.lower()
        if lw not in STOPWORDS:
            return lw
    return words[0].lower() if words else "paper"


def _normalize_last_name(author: str) -> str:
    author = re.sub(r"[\{\}]", "", author).strip()
    author = re.sub(r"\\[a-zA-Z]+", "", author)  # drop LaTeX commands (best effort)
    author = re.sub(r"\s+", " ", author).strip()
    if not author:
        return "unknown"

    # Prefer "Last, First" format when present.
    first = author.split(" and ", 1)[0].strip()
    if "," in first:
        last = first.split(",", 1)[0].strip()
    else:
        parts = [p for p in first.split(" ") if p]
        last = parts[-1] if parts else first
    last = re.sub(r"[^A-Za-z0-9]+", "", last).lower()
    return last or "unknown"


def generate_key(entry: str) -> str:
    author = _extract_bibtex_field(entry, "author")
    year = _extract_bibtex_field(entry, "year")
    title = _extract_bibtex_field(entry, "title")

    last = _normalize_last_name(author)
    year_digits = re.search(r"\d{4}", year)
    year_str = year_digits.group(0) if year_digits else "0000"
    word = _slug_word(title)
    return f"{last}{year_str}{word}"


def parse_existing_keys_and_dois(bib_path: Path) -> tuple[set[str], set[str]]:
    if not bib_path.exists():
        return set(), set()

    content = bib_path.read_text(encoding="utf-8", errors="replace")
    keys = set(re.findall(r"@\w+\{([^,]+),", content))
    dois = set()

    for match in re.finditer(r"(?i)\bdoi\s*=\s*\{([^}]+)\}", content):
        value = normalize_doi(match.group(1))
        if value:
            dois.add(value)
    for match in re.finditer(r'(?i)\bdoi\s*=\s*"([^"]+)"', content):
        value = normalize_doi(match.group(1))
        if value:
            dois.add(value)
    return keys, dois


@dataclass
class AddResult:
    doi: str
    cite_key: str
    action: str  # added | skipped | failed
    message: str = ""


def fetch_bibtex(doi: str, *, prefer: str, timeout_s: int) -> str:
    """Fetch BibTeX for a DOI.

    prefer:
      - auto: doi.org then Crossref fallback
      - doi: doi.org only
      - crossref: Crossref only
    """
    if prefer not in {"auto", "doi", "crossref"}:
        raise ValueError(f"invalid prefer: {prefer}")

    if prefer in {"auto", "doi"}:
        try:
            return fetch_bibtex_from_doi_org(doi, timeout_s=timeout_s)
        except Exception:
            if prefer == "doi":
                raise

    return fetch_bibtex_from_crossref(doi, timeout_s=timeout_s)


def add_doi_to_bib(
    doi: str,
    *,
    bib_path: Path,
    existing_keys: set[str],
    existing_dois: set[str],
    timeout_s: int,
    sleep_s: float,
    prefer: str,
    fetched_bibtex: str | None = None,
) -> AddResult:
    if doi in existing_dois:
        return AddResult(doi=doi, cite_key="", action="skipped", message="duplicate DOI")

    try:
        raw = fetched_bibtex if fetched_bibtex is not None else fetch_bibtex(doi, prefer=prefer, timeout_s=timeout_s)

        entry = normalize_bibtex_fields(raw, doi)
        key = generate_key(entry)

        # Ensure key uniqueness.
        if key in existing_keys:
            suffix = ord("a")
            while f"{key}{chr(suffix)}" in existing_keys and suffix <= ord("z"):
                suffix += 1
            key = f"{key}{chr(suffix)}"

        entry = rewrite_bibtex_key(entry, key)
        bib_path.parent.mkdir(parents=True, exist_ok=True)
        with bib_path.open("a", encoding="utf-8", newline="\n") as handle:
            if bib_path.stat().st_size and not entry.startswith("\n"):
                handle.write("\n")
            handle.write(entry)

        existing_keys.add(key)
        existing_dois.add(doi)

        if sleep_s > 0:
            time.sleep(sleep_s)

        return AddResult(doi=doi, cite_key=key, action="added")
    except Exception as e:
        return AddResult(doi=doi, cite_key="", action="failed", message=str(e))


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch DOI BibTeX and append to ref.bib.")
    parser.add_argument("--project-dir", help="Paper/project directory; defaults out-bib to <project-dir>/ref.bib.")
    parser.add_argument("--out-bib", help="Output .bib file to append to.")
    parser.add_argument("--doi", action="append", default=[], help="DOI (repeatable).")
    parser.add_argument("--doi-file", help="Text file with one DOI per line (comments with #).")
    parser.add_argument("--timeout-s", type=int, default=30, help="Network timeout seconds (default: 30).")
    parser.add_argument("--sleep-s", type=float, default=0.2, help="Sleep between requests (default: 0.2).")
    parser.add_argument("--prefer", choices=["auto", "doi", "crossref"], default="auto", help="BibTeX source preference (default: auto).")
    parser.add_argument("--workers", type=int, default=1, help="Parallel fetch workers (default: 1).")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any DOI fails.")
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    if args.out_bib:
        bib_path = Path(args.out_bib)
    elif project_dir:
        bib_path = project_dir / "ref.bib"
    else:
        print("error: provide --out-bib or --project-dir", file=sys.stderr)
        return 2

    dois: list[str] = []
    for d in args.doi:
        nd = normalize_doi(d)
        if nd:
            dois.append(nd)
        else:
            print(f"warning: could not parse DOI: {d}", file=sys.stderr)

    if args.doi_file:
        doi_file = Path(args.doi_file)
        if not doi_file.exists():
            print(f"error: DOI file not found: {doi_file}", file=sys.stderr)
            return 2
        for line in doi_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            nd = normalize_doi(line)
            if nd:
                dois.append(nd)

    # Dedupe input DOIs while preserving order.
    seen: set[str] = set()
    ordered: list[str] = []
    for d in dois:
        if d not in seen:
            ordered.append(d)
            seen.add(d)

    existing_keys, existing_dois = parse_existing_keys_and_dois(bib_path)

    # Skip duplicates early to avoid unnecessary network calls.
    to_fetch = [d for d in ordered if d not in existing_dois]
    fetched_map: dict[str, str] = {}
    fetch_failures: dict[str, str] = {}

    if args.workers <= 1 or len(to_fetch) <= 1:
        for d in to_fetch:
            try:
                fetched_map[d] = fetch_bibtex(d, prefer=args.prefer, timeout_s=args.timeout_s)
            except Exception as e:
                fetch_failures[d] = str(e)
            if args.sleep_s > 0:
                time.sleep(args.sleep_s)
    else:
        workers = min(args.workers, max(1, len(to_fetch)))
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(fetch_bibtex, d, prefer=args.prefer, timeout_s=args.timeout_s): d for d in to_fetch}
            for fut in cf.as_completed(futures):
                d = futures[fut]
                try:
                    fetched_map[d] = fut.result()
                except Exception as e:
                    fetch_failures[d] = str(e)

    results: list[AddResult] = []
    for d in ordered:
        if d in existing_dois:
            results.append(AddResult(doi=d, cite_key="", action="skipped", message="duplicate DOI"))
            continue
        if d in fetch_failures:
            results.append(AddResult(doi=d, cite_key="", action="failed", message=fetch_failures[d]))
            continue
        results.append(
            add_doi_to_bib(
                d,
                bib_path=bib_path,
                existing_keys=existing_keys,
                existing_dois=existing_dois,
                timeout_s=args.timeout_s,
                sleep_s=0.0,  # already rate-limited during fetch stage
                prefer=args.prefer,
                fetched_bibtex=fetched_map.get(d),
            )
        )

    added = [r for r in results if r.action == "added"]
    skipped = [r for r in results if r.action == "skipped"]
    failed = [r for r in results if r.action == "failed"]

    print(f"BibTeX out: {bib_path}")
    print(f"Input DOIs: {len(ordered)}")
    print(f"Added: {len(added)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Failed: {len(failed)}")
    if failed:
        for r in failed[:20]:
            print(f"- {r.doi}: {r.message}", file=sys.stderr)
        if len(failed) > 20:
            print(f"(+{len(failed)-20} more failures)", file=sys.stderr)
        if args.strict:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
