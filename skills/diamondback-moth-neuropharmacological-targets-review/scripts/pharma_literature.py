#!/usr/bin/env python3
"""Unified biomedical literature API wrapper.

Provides search and metadata retrieval for:
  - PubMed (NCBI E-utilities)
  - Europe PMC
  - Crossref
  - Semantic Scholar

Usage:
    python3 pharma_literature.py search --query "GNN ADMET prediction" --source pubmed --max-results 20
    python3 pharma_literature.py fetch --pmid 12345678 --source pubmed
    python3 pharma_literature.py fetch --doi "10.1234/example" --source crossref
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import random
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional


# Rate limiting defaults (requests per second)
RATE_LIMITS = {
    "pubmed": 3,      # NCBI allows 3/s without API key, 10/s with
    "europe_pmc": 10,
    "crossref": 10,
    "semantic_scholar": 0.3,  # Public API: 100/5min; with API key: 100/s
}

# Semantic Scholar API base
S2_BASE = "https://api.semanticscholar.org/graph/v1"


@dataclass
class PaperMetadata:
    """Unified paper metadata across sources."""
    source: str
    source_id: str  # PMID, PMC, DOI, S2 ID
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    year: int | None = None
    journal: str = ""
    doi: str = ""
    pmid: str = ""
    pmc_id: str = ""
    arxiv_id: str = ""
    is_preprint: bool = False
    preprint_server: str = ""  # bioRxiv, medRxiv, arXiv
    published_doi: str = ""    # If preprint was published
    citation_count: int | None = None
    mesh_terms: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_id": self.source_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "year": self.year,
            "journal": self.journal,
            "doi": self.doi,
            "pmid": self.pmid,
            "pmc_id": self.pmc_id,
            "arxiv_id": self.arxiv_id,
            "is_preprint": self.is_preprint,
            "preprint_server": self.preprint_server,
            "published_doi": self.published_doi,
            "citation_count": self.citation_count,
            "mesh_terms": self.mesh_terms,
            "keywords": self.keywords,
        }


# =============================================================================
# Utilities
# =============================================================================

def now_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    """Return SHA256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def backoff_sleep_s(attempt: int, *, base: float = 0.5, cap: float = 30.0) -> float:
    """Exponential backoff with jitter."""
    exp = min(cap, base * (2 ** attempt))
    return exp * (0.5 + random.random())


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, rps: float):
        self.min_interval = 1.0 / max(rps, 0.001)
        self._next_ts = 0.0

    def wait(self) -> None:
        now = time.time()
        if now < self._next_ts:
            time.sleep(self._next_ts - now)
        self._next_ts = max(self._next_ts, now) + self.min_interval


def fetch_url(
    url: str,
    *,
    timeout_s: int = 30,
    method: str = "GET",
    headers: Optional[Mapping[str, str]] = None,
    data: bytes | None = None,
) -> tuple[int | None, dict[str, str], bytes]:
    """Fetch URL with gzip support and return (status, headers, body)."""
    req_headers = {
        "User-Agent": "pharma-literature-py/2.0 (+https://github.com/latex-arxiv-skill)",
        "Accept": "application/json, text/plain;q=0.9, */*;q=0.1",
        "Accept-Encoding": "gzip",
        "Connection": "keep-alive",
    }
    if headers:
        req_headers.update(dict(headers))

    req = urllib.request.Request(url, headers=req_headers, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            status = getattr(resp, "status", 200)
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            body = resp.read()
    except urllib.error.HTTPError as e:
        status = getattr(e, "code", None)
        resp_headers = {k.lower(): v for k, v in getattr(e, "headers", {}).items()}
        body = e.read() if hasattr(e, "read") else b""
    except urllib.error.URLError:
        return None, {}, b""

    # Transparently decompress gzip
    if resp_headers.get("content-encoding", "").lower() == "gzip" and body:
        try:
            body = gzip.GzipFile(fileobj=io.BytesIO(body)).read()
        except OSError:
            pass

    return status, resp_headers, body


def fetch_url_simple(url: str, *, timeout_s: int = 30, headers: dict | None = None) -> tuple[int | None, bytes]:
    """Simplified fetch for backward compatibility."""
    status, _, body = fetch_url(url, timeout_s=timeout_s, headers=headers)
    return status, body


# =============================================================================
# PubMed (NCBI E-utilities)
# =============================================================================

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Default NCBI API key (can be overridden via CLI)
DEFAULT_NCBI_API_KEY = "0e8da1b0253f7db81459804a5655d8295808"


def pubmed_search(query: str, *, max_results: int = 20, api_key: str = "") -> list[str]:
    """Search PubMed and return list of PMIDs."""
    effective_key = api_key or DEFAULT_NCBI_API_KEY
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": str(max_results),
        "retmode": "json",
        "sort": "relevance",
    }
    if effective_key:
        params["api_key"] = effective_key
    
    url = f"{PUBMED_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    status, body = fetch_url_simple(url)
    
    if status != 200 or not body:
        return []
    
    try:
        data = json.loads(body)
        return data.get("esearchresult", {}).get("idlist", [])
    except json.JSONDecodeError:
        return []


def pubmed_fetch(pmids: list[str], *, api_key: str = "") -> list[PaperMetadata]:
    """Fetch PubMed metadata for given PMIDs."""
    if not pmids:
        return []
    
    effective_key = api_key or DEFAULT_NCBI_API_KEY
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    if effective_key:
        params["api_key"] = effective_key
    
    url = f"{PUBMED_FETCH_URL}?{urllib.parse.urlencode(params)}"
    status, body = fetch_url_simple(url)
    
    if status != 200 or not body:
        return []
    
    return parse_pubmed_xml(body)


def parse_pubmed_xml(xml_bytes: bytes) -> list[PaperMetadata]:
    """Parse PubMed XML response."""
    results = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    
    for article in root.findall(".//PubmedArticle"):
        try:
            medline = article.find(".//MedlineCitation")
            if medline is None:
                continue
            
            pmid_elem = medline.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else ""
            
            article_elem = medline.find(".//Article")
            if article_elem is None:
                continue
            
            title_elem = article_elem.find(".//ArticleTitle")
            title = "".join(title_elem.itertext()) if title_elem is not None else ""
            
            abstract_elem = article_elem.find(".//Abstract/AbstractText")
            abstract = "".join(abstract_elem.itertext()) if abstract_elem is not None else ""
            
            # Authors
            authors = []
            for author in article_elem.findall(".//Author"):
                lastname = author.find("LastName")
                forename = author.find("ForeName")
                if lastname is not None:
                    name = lastname.text or ""
                    if forename is not None and forename.text:
                        name = f"{forename.text} {name}"
                    authors.append(name)
            
            # Journal
            journal_elem = article_elem.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else ""
            
            # Year
            year = None
            pub_date = article_elem.find(".//PubDate/Year")
            if pub_date is not None and pub_date.text:
                try:
                    year = int(pub_date.text)
                except ValueError:
                    pass
            
            # DOI
            doi = ""
            for eloc in article_elem.findall(".//ELocationID"):
                if eloc.get("EIdType") == "doi":
                    doi = eloc.text or ""
                    break
            
            # MeSH terms
            mesh_terms = []
            for mesh in medline.findall(".//MeshHeading/DescriptorName"):
                if mesh.text:
                    mesh_terms.append(mesh.text)
            
            # Keywords
            keywords = []
            for kw in medline.findall(".//KeywordList/Keyword"):
                if kw.text:
                    keywords.append(kw.text)
            
            results.append(PaperMetadata(
                source="pubmed",
                source_id=pmid,
                title=title,
                authors=authors,
                abstract=abstract,
                year=year,
                journal=journal,
                doi=doi,
                pmid=pmid,
                mesh_terms=mesh_terms,
                keywords=keywords,
            ))
        except Exception:
            continue
    
    return results


# =============================================================================
# Europe PMC
# =============================================================================

EUROPE_PMC_SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def europe_pmc_search(query: str, *, max_results: int = 20) -> list[PaperMetadata]:
    """Search Europe PMC."""
    params = {
        "query": query,
        "format": "json",
        "pageSize": str(max_results),
        "resultType": "core",
    }
    
    url = f"{EUROPE_PMC_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    status, body = fetch_url_simple(url)
    
    if status != 200 or not body:
        return []
    
    try:
        data = json.loads(body)
        results = []
        for item in data.get("resultList", {}).get("result", []):
            year = None
            if item.get("pubYear"):
                try:
                    year = int(item["pubYear"])
                except ValueError:
                    pass
            
            # Check if preprint
            is_preprint = item.get("source") in ["PPR", "MED"]
            preprint_server = ""
            if is_preprint:
                doi = item.get("doi", "")
                if "biorxiv" in doi.lower():
                    preprint_server = "bioRxiv"
                elif "medrxiv" in doi.lower():
                    preprint_server = "medRxiv"
            
            results.append(PaperMetadata(
                source="europe_pmc",
                source_id=item.get("id", ""),
                title=item.get("title", ""),
                authors=[a.get("fullName", "") for a in item.get("authorList", {}).get("author", [])],
                abstract=item.get("abstractText", ""),
                year=year,
                journal=item.get("journalTitle", ""),
                doi=item.get("doi", ""),
                pmid=item.get("pmid", ""),
                pmc_id=item.get("pmcid", ""),
                is_preprint=is_preprint,
                preprint_server=preprint_server,
                citation_count=item.get("citedByCount"),
            ))
        return results
    except json.JSONDecodeError:
        return []


# =============================================================================
# Crossref
# =============================================================================

CROSSREF_WORKS_URL = "https://api.crossref.org/works"


def crossref_search(query: str, *, max_results: int = 20) -> list[PaperMetadata]:
    """Search Crossref."""
    params = {
        "query": query,
        "rows": str(max_results),
        "select": "DOI,title,author,abstract,published,container-title,type",
    }
    
    url = f"{CROSSREF_WORKS_URL}?{urllib.parse.urlencode(params)}"
    status, body = fetch_url_simple(url)
    
    if status != 200 or not body:
        return []
    
    try:
        data = json.loads(body)
        results = []
        for item in data.get("message", {}).get("items", []):
            title = item.get("title", [""])[0] if item.get("title") else ""
            
            # Authors
            authors = []
            for author in item.get("author", []):
                name = author.get("family", "")
                if author.get("given"):
                    name = f"{author['given']} {name}"
                if name:
                    authors.append(name)
            
            # Year
            year = None
            published = item.get("published", {})
            date_parts = published.get("date-parts", [[]])
            if date_parts and date_parts[0]:
                try:
                    year = int(date_parts[0][0])
                except (ValueError, IndexError):
                    pass
            
            # Check if preprint
            is_preprint = item.get("type") == "posted-content"
            preprint_server = ""
            doi = item.get("DOI", "")
            if "biorxiv" in doi.lower():
                preprint_server = "bioRxiv"
            elif "medrxiv" in doi.lower():
                preprint_server = "medRxiv"
            elif "arxiv" in doi.lower():
                preprint_server = "arXiv"
            
            results.append(PaperMetadata(
                source="crossref",
                source_id=doi,
                title=title,
                authors=authors,
                abstract=item.get("abstract", ""),
                year=year,
                journal=item.get("container-title", [""])[0] if item.get("container-title") else "",
                doi=doi,
                is_preprint=is_preprint,
                preprint_server=preprint_server,
            ))
        return results
    except json.JSONDecodeError:
        return []


def crossref_fetch_doi(doi: str) -> PaperMetadata | None:
    """Fetch metadata for a specific DOI from Crossref."""
    url = f"{CROSSREF_WORKS_URL}/{urllib.parse.quote(doi, safe='')}"
    status, body = fetch_url_simple(url)
    
    if status != 200 or not body:
        return None
    
    try:
        data = json.loads(body)
        item = data.get("message", {})
        
        title = item.get("title", [""])[0] if item.get("title") else ""
        
        authors = []
        for author in item.get("author", []):
            name = author.get("family", "")
            if author.get("given"):
                name = f"{author['given']} {name}"
            if name:
                authors.append(name)
        
        year = None
        published = item.get("published", {})
        date_parts = published.get("date-parts", [[]])
        if date_parts and date_parts[0]:
            try:
                year = int(date_parts[0][0])
            except (ValueError, IndexError):
                pass
        
        is_preprint = item.get("type") == "posted-content"
        preprint_server = ""
        if "biorxiv" in doi.lower():
            preprint_server = "bioRxiv"
        elif "medrxiv" in doi.lower():
            preprint_server = "medRxiv"
        
        return PaperMetadata(
            source="crossref",
            source_id=doi,
            title=title,
            authors=authors,
            abstract=item.get("abstract", ""),
            year=year,
            journal=item.get("container-title", [""])[0] if item.get("container-title") else "",
            doi=doi,
            is_preprint=is_preprint,
            preprint_server=preprint_server,
        )
    except json.JSONDecodeError:
        return None


# =============================================================================
# Semantic Scholar (Enhanced with batch + citation network support)
# =============================================================================

S2_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_PAPER_URL = "https://api.semanticscholar.org/graph/v1/paper"


def s2_headers(api_key: str | None) -> dict[str, str]:
    """Return S2 headers. Empty api_key = public shared pool (no x-api-key)."""
    if not api_key:
        return {}
    return {"x-api-key": api_key}


def s2_get_json(
    *,
    url: str,
    timeout_s: int,
    limiter: RateLimiter,
    api_key: str | None,
    max_retries: int = 6,
) -> tuple[int | None, dict[str, str], dict]:
    """GET request to S2 API with retry/backoff."""
    for attempt in range(max_retries + 1):
        limiter.wait()
        status, hdrs, body = fetch_url(url, timeout_s=timeout_s, headers=s2_headers(api_key))
        if status in (200, 201) and body:
            try:
                return status, hdrs, json.loads(body.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                return status, hdrs, {}

        # Respect Retry-After if present
        if status in (429, 500, 502, 503, 504):
            ra = hdrs.get("retry-after")
            if ra and ra.isdigit():
                time.sleep(float(ra))
            else:
                time.sleep(backoff_sleep_s(attempt))
            continue

        return status, hdrs, {}
    return None, {}, {}


def s2_post_json(
    *,
    url: str,
    payload: dict,
    timeout_s: int,
    limiter: RateLimiter,
    api_key: str | None,
    max_retries: int = 6,
) -> tuple[int | None, dict[str, str], Any]:
    """POST request to S2 API with retry/backoff."""
    data = json.dumps(payload).encode("utf-8")
    extra_headers = {"Content-Type": "application/json"}
    extra_headers.update(s2_headers(api_key))
    for attempt in range(max_retries + 1):
        limiter.wait()
        status, hdrs, body = fetch_url(
            url,
            timeout_s=timeout_s,
            method="POST",
            headers=extra_headers,
            data=data,
        )
        if status in (200, 201) and body:
            try:
                return status, hdrs, json.loads(body.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                return status, hdrs, None

        if status in (429, 500, 502, 503, 504):
            ra = hdrs.get("retry-after")
            if ra and ra.isdigit():
                time.sleep(float(ra))
            else:
                time.sleep(backoff_sleep_s(attempt))
            continue

        return status, hdrs, None
    return None, {}, None


def semantic_scholar_search(
    query: str,
    *,
    max_results: int = 20,
    api_key: str = "",
    verbose: bool = False,
) -> list[PaperMetadata]:
    """Search Semantic Scholar with retry/backoff support.
    
    Args:
        query: Search query string
        max_results: Maximum number of results (capped at 100)
        api_key: Optional S2 API key for higher rate limits
        verbose: Print diagnostic info to stderr
    
    Returns:
        List of PaperMetadata objects
    """
    params = {
        "query": query,
        "limit": str(min(max_results, 100)),
        "fields": "paperId,title,authors,abstract,year,venue,externalIds,citationCount,isOpenAccess",
    }
    
    url = f"{S2_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    
    # Use rate limiter with appropriate RPS based on whether we have an API key
    rps = 10.0 if api_key else RATE_LIMITS.get("semantic_scholar", 0.3)
    limiter = RateLimiter(rps)
    
    if verbose:
        print(f"[S2] Searching: {query[:50]}... (rps={rps})", file=sys.stderr)
    
    # Use s2_get_json which has built-in retry/backoff for 429 errors
    status, hdrs, data = s2_get_json(
        url=url,
        timeout_s=30,
        limiter=limiter,
        api_key=api_key if api_key else None,
        max_retries=6,
    )
    
    if status != 200 or not data:
        if verbose:
            print(f"[S2] Search failed: status={status}, has_data={bool(data)}", file=sys.stderr)
            if status == 429:
                print("[S2] Rate limited (429). Consider using an API key or waiting.", file=sys.stderr)
        return []
    
    if verbose:
        total = data.get("total", "?")
        print(f"[S2] Found {total} total results", file=sys.stderr)
    
    results = []
    for item in data.get("data", []):
        ext_ids = item.get("externalIds", {}) or {}
        
        # Check if preprint
        arxiv_id = ext_ids.get("ArXiv", "")
        is_preprint = bool(arxiv_id) and not ext_ids.get("DOI")
        preprint_server = "arXiv" if is_preprint else ""
        
        results.append(PaperMetadata(
            source="semantic_scholar",
            source_id=item.get("paperId", ""),
            title=item.get("title", ""),
            authors=[a.get("name", "") for a in item.get("authors", [])],
            abstract=item.get("abstract", "") or "",
            year=item.get("year"),
            journal=item.get("venue", ""),
            doi=ext_ids.get("DOI", ""),
            pmid=ext_ids.get("PubMed", ""),
            arxiv_id=arxiv_id,
            is_preprint=is_preprint,
            preprint_server=preprint_server,
            citation_count=item.get("citationCount"),
        ))
    return results


# =============================================================================
# SQLite Database for S2 Citation Network
# =============================================================================

def init_s2_schema(conn: sqlite3.Connection) -> None:
    """Initialize S2 tables for paper cache and citation edges."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS s2_papers (
          paper_id TEXT PRIMARY KEY,
          corpus_id INTEGER,
          title TEXT,
          year INTEGER,
          url TEXT,
          external_ids_json TEXT,
          open_access_pdf_json TEXT,
          citation_count INTEGER,
          reference_count INTEGER,
          fetched_at TEXT NOT NULL,
          raw_sha256 TEXT,
          raw_json TEXT
        );

        CREATE INDEX IF NOT EXISTS s2_papers_year_idx ON s2_papers(year);

        CREATE TABLE IF NOT EXISTS s2_edges (
          src_paper_id TEXT NOT NULL,
          dst_paper_id TEXT NOT NULL,
          relation TEXT NOT NULL CHECK(relation IN ('cites','cited_by')),
          is_influential INTEGER,
          intents_json TEXT,
          contexts_json TEXT,
          fetched_at TEXT NOT NULL,
          subject_paper_id TEXT NOT NULL,
          PRIMARY KEY (relation, subject_paper_id, src_paper_id, dst_paper_id)
        );

        CREATE INDEX IF NOT EXISTS s2_edges_src_idx ON s2_edges(src_paper_id);
        CREATE INDEX IF NOT EXISTS s2_edges_dst_idx ON s2_edges(dst_paper_id);

        CREATE TABLE IF NOT EXISTS s2_fetch_log (
          fetch_id INTEGER PRIMARY KEY AUTOINCREMENT,
          kind TEXT NOT NULL,
          url TEXT NOT NULL,
          status INTEGER,
          fetched_at TEXT NOT NULL,
          body_sha256 TEXT
        );
    """)
    conn.commit()


def s2_upsert_paper(conn: sqlite3.Connection, paper: dict, raw_json: str | None = None, raw_sha: str | None = None) -> None:
    """Upsert a paper record into s2_papers."""
    paper_id = paper.get("paperId")
    if not paper_id:
        return
    conn.execute(
        """
        INSERT INTO s2_papers(
          paper_id, corpus_id, title, year, url,
          external_ids_json, open_access_pdf_json,
          citation_count, reference_count,
          fetched_at, raw_sha256, raw_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(paper_id) DO UPDATE SET
          corpus_id=excluded.corpus_id,
          title=COALESCE(excluded.title, s2_papers.title),
          year=COALESCE(excluded.year, s2_papers.year),
          url=COALESCE(excluded.url, s2_papers.url),
          external_ids_json=COALESCE(excluded.external_ids_json, s2_papers.external_ids_json),
          open_access_pdf_json=COALESCE(excluded.open_access_pdf_json, s2_papers.open_access_pdf_json),
          citation_count=COALESCE(excluded.citation_count, s2_papers.citation_count),
          reference_count=COALESCE(excluded.reference_count, s2_papers.reference_count),
          fetched_at=excluded.fetched_at,
          raw_sha256=COALESCE(excluded.raw_sha256, s2_papers.raw_sha256),
          raw_json=COALESCE(excluded.raw_json, s2_papers.raw_json);
        """,
        (
            paper_id,
            paper.get("corpusId"),
            paper.get("title"),
            paper.get("year"),
            paper.get("url"),
            json.dumps(paper.get("externalIds") or {}, ensure_ascii=False),
            json.dumps(paper.get("openAccessPdf") or {}, ensure_ascii=False),
            paper.get("citationCount"),
            paper.get("referenceCount"),
            now_iso(),
            raw_sha,
            raw_json,
        ),
    )


def s2_record_fetch(conn: sqlite3.Connection, *, kind: str, url: str, status: int | None, body: bytes) -> None:
    """Log a fetch operation."""
    conn.execute(
        """
        INSERT INTO s2_fetch_log(kind, url, status, fetched_at, body_sha256)
        VALUES(?, ?, ?, ?, ?);
        """,
        (kind, url, status, now_iso(), sha256_bytes(body) if body else None),
    )


def s2_iter_edges(
    *,
    kind: str,              # "references" or "citations"
    subject_id: str,        # e.g. "ARXIV:2106.15928" or S2 paperId
    fields: str,
    timeout_s: int,
    limiter: RateLimiter,
    api_key: str | None,
):
    """Iterate over citation/reference edges with pagination (limit<=1000)."""
    offset = 0
    while True:
        params = {"fields": fields, "offset": offset, "limit": 1000}
        url = f"{S2_BASE}/paper/{urllib.parse.quote(subject_id, safe='')}/{kind}?{urllib.parse.urlencode(params)}"
        status, hdrs, payload = s2_get_json(url=url, timeout_s=timeout_s, limiter=limiter, api_key=api_key)
        if not isinstance(payload, dict):
            return

        data = payload.get("data") or []
        if not data:
            return

        yield status, url, payload

        nxt = payload.get("next")
        if nxt is None:
            return
        try:
            nxt_i = int(nxt)
        except (TypeError, ValueError):
            return
        if nxt_i <= offset:
            return
        offset = nxt_i


def s2_ingest_edges(conn: sqlite3.Connection, *, relation: str, subject: str, payload: dict) -> None:
    """Ingest citation edges from API response."""
    fetched = now_iso()
    for item in payload.get("data") or []:
        if not isinstance(item, dict):
            continue

        # references: item["citedPaper"]; citations: item["citingPaper"]
        if relation == "cites":
            other = item.get("citedPaper") or {}
            src = subject
            dst = other.get("paperId")
        else:  # "cited_by"
            other = item.get("citingPaper") or {}
            src = other.get("paperId")
            dst = subject

        if not src or not dst:
            continue

        conn.execute(
            """
            INSERT OR IGNORE INTO s2_edges(
              src_paper_id, dst_paper_id, relation,
              is_influential, intents_json, contexts_json,
              fetched_at, subject_paper_id
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                src,
                dst,
                relation,
                1 if item.get("isInfluential") else 0 if item.get("isInfluential") is not None else None,
                json.dumps(item.get("intents") or [], ensure_ascii=False),
                json.dumps(item.get("contexts") or [], ensure_ascii=False),
                fetched,
                subject,
            ),
        )

        # Also cache the other paper's minimal info
        if isinstance(other, dict) and other.get("paperId"):
            s2_upsert_paper(conn, other)


# =============================================================================
# Unified Interface
# =============================================================================

def search(
    query: str,
    *,
    sources: list[str] | None = None,
    max_results: int = 20,
    pubmed_api_key: str = "",
    s2_api_key: str = "",
    sleep_between: float = 0.5,
) -> dict[str, list[PaperMetadata]]:
    """Search across multiple sources."""
    if sources is None:
        sources = ["pubmed", "europe_pmc", "crossref", "semantic_scholar"]
    
    results: dict[str, list[PaperMetadata]] = {}
    
    for source in sources:
        if source == "pubmed":
            pmids = pubmed_search(query, max_results=max_results, api_key=pubmed_api_key)
            if pmids:
                time.sleep(sleep_between)
                results["pubmed"] = pubmed_fetch(pmids, api_key=pubmed_api_key)
            else:
                results["pubmed"] = []
        elif source == "europe_pmc":
            results["europe_pmc"] = europe_pmc_search(query, max_results=max_results)
        elif source == "crossref":
            results["crossref"] = crossref_search(query, max_results=max_results)
        elif source == "semantic_scholar":
            results["semantic_scholar"] = semantic_scholar_search(
                query, max_results=max_results, api_key=s2_api_key
            )
        
        if sleep_between > 0 and source != sources[-1]:
            time.sleep(sleep_between)
    
    return results


def deduplicate_results(results: dict[str, list[PaperMetadata]]) -> list[PaperMetadata]:
    """Deduplicate papers across sources by DOI/PMID."""
    seen_dois: set[str] = set()
    seen_pmids: set[str] = set()
    unique: list[PaperMetadata] = []
    
    # Priority order: PubMed > Europe PMC > Crossref > Semantic Scholar
    priority_order = ["pubmed", "europe_pmc", "crossref", "semantic_scholar"]
    
    for source in priority_order:
        for paper in results.get(source, []):
            doi = paper.doi.lower().strip() if paper.doi else ""
            pmid = paper.pmid.strip() if paper.pmid else ""
            
            is_dup = False
            if doi and doi in seen_dois:
                is_dup = True
            if pmid and pmid in seen_pmids:
                is_dup = True
            
            if not is_dup:
                unique.append(paper)
                if doi:
                    seen_dois.add(doi)
                if pmid:
                    seen_pmids.add(pmid)
    
    return unique


# =============================================================================
# CLI
# =============================================================================

def cmd_search(args: argparse.Namespace) -> int:
    """Handle search command."""
    sources = args.sources.split(",") if args.sources else None
    
    results = search(
        args.query,
        sources=sources,
        max_results=args.max_results,
        pubmed_api_key=args.pubmed_api_key or "",
        s2_api_key=args.s2_api_key or "",
        sleep_between=args.sleep,
    )
    
    if args.dedupe:
        papers = deduplicate_results(results)
        output = {"deduplicated": [p.to_dict() for p in papers]}
    else:
        output = {src: [p.to_dict() for p in papers] for src, papers in results.items()}
    
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    """Handle fetch command."""
    paper: PaperMetadata | None = None
    
    if args.pmid:
        papers = pubmed_fetch([args.pmid], api_key=args.pubmed_api_key or "")
        paper = papers[0] if papers else None
    elif args.doi:
        paper = crossref_fetch_doi(args.doi)
    else:
        print("error: must specify --pmid or --doi", file=sys.stderr)
        return 2
    
    if paper:
        print(json.dumps(paper.to_dict(), indent=2, ensure_ascii=False))
        return 0
    else:
        print("error: paper not found", file=sys.stderr)
        return 1


def cmd_s2_enrich(args: argparse.Namespace) -> int:
    """Batch fetch S2 paper metadata for given paper IDs."""
    db_path = Path(args.db).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    limiter = RateLimiter(args.s2_rps)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        init_s2_schema(conn)
        
        # Get paper IDs from input file or stdin
        if args.ids_file:
            with open(args.ids_file, "r", encoding="utf-8") as f:
                ids = [line.strip() for line in f if line.strip()]
        else:
            # Read from works table if exists, otherwise require input
            try:
                rows = conn.execute("SELECT arxiv_id FROM works WHERE arxiv_id IS NOT NULL ORDER BY work_id ASC;").fetchall()
                ids = [f"ARXIV:{r['arxiv_id']}" for r in rows if r["arxiv_id"]]
            except sqlite3.OperationalError:
                print("error: no works table found. Provide --ids-file or create works table first.", file=sys.stderr)
                return 1
        
        if not ids:
            print("No paper IDs to enrich.")
            return 0
        
        print(f"Enriching {len(ids)} papers via S2 batch API...")
        
        # /paper/batch: 500 ids per call
        fields = ",".join([
            "paperId", "corpusId", "title", "year", "url",
            "externalIds", "openAccessPdf",
            "citationCount", "referenceCount",
        ])
        
        enriched = 0
        for i in range(0, len(ids), 500):
            chunk = ids[i:i+500]
            url = f"{S2_BASE}/paper/batch?{urllib.parse.urlencode({'fields': fields})}"
            status, hdrs, data = s2_post_json(
                url=url,
                payload={"ids": chunk},
                timeout_s=args.timeout_s,
                limiter=limiter,
                api_key=args.s2_api_key if args.s2_api_key else None,
            )
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            s2_record_fetch(conn, kind="s2_paper_batch", url=url, status=status, body=raw)

            if isinstance(data, list):
                for paper in data:
                    if isinstance(paper, dict) and paper.get("paperId"):
                        s2_upsert_paper(conn, paper)
                        enriched += 1
            conn.commit()
            print(f"  Processed {min(i+500, len(ids))}/{len(ids)} IDs...")

        print(f"S2 enrich complete. {enriched} papers cached.")
    finally:
        conn.close()
    return 0


def cmd_s2_graph(args: argparse.Namespace, *, mode: str) -> int:
    """Fetch S2 references or citations and store edges."""
    relation = "cites" if mode == "references" else "cited_by"
    limiter = RateLimiter(args.s2_rps)
    
    db_path = Path(args.db).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        init_s2_schema(conn)
        
        # Get subject IDs
        if args.ids_file:
            with open(args.ids_file, "r", encoding="utf-8") as f:
                subjects = [line.strip() for line in f if line.strip()]
        else:
            try:
                rows = conn.execute("SELECT arxiv_id FROM works WHERE arxiv_id IS NOT NULL ORDER BY work_id ASC;").fetchall()
                subjects = [f"ARXIV:{r['arxiv_id']}" for r in rows if r["arxiv_id"]]
            except sqlite3.OperationalError:
                # Try s2_papers table
                rows = conn.execute("SELECT paper_id FROM s2_papers ORDER BY paper_id ASC;").fetchall()
                subjects = [r["paper_id"] for r in rows]
        
        if not subjects:
            print("No subjects to fetch citations for.")
            return 0
        
        print(f"Fetching S2 {mode} for {len(subjects)} papers...")
        
        if mode == "references":
            fields = "isInfluential,intents,contexts,citedPaper.paperId,citedPaper.title,citedPaper.year,citedPaper.externalIds"
        else:
            fields = "isInfluential,intents,contexts,citingPaper.paperId,citingPaper.title,citingPaper.year,citingPaper.externalIds"
        
        total_edges = 0
        for idx, subj in enumerate(subjects, 1):
            subj_edges = 0
            for status, url, payload in s2_iter_edges(
                kind=mode,
                subject_id=subj,
                fields=fields,
                timeout_s=args.timeout_s,
                limiter=limiter,
                api_key=args.s2_api_key if args.s2_api_key else None,
            ):
                raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                s2_record_fetch(conn, kind=f"s2_{mode}", url=url, status=status, body=raw)
                s2_ingest_edges(conn, relation=relation, subject=subj, payload=payload)
                subj_edges += len(payload.get("data") or [])
            conn.commit()
            total_edges += subj_edges
            print(f"  [{idx}/{len(subjects)}] {subj}: {subj_edges} edges")

        print(f"S2 {mode} ingestion complete. {total_edges} total edges.")
    finally:
        conn.close()
    return 0


def cmd_s2_stats(args: argparse.Namespace) -> int:
    """Show S2 database statistics."""
    db_path = Path(args.db).expanduser()
    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        return 1
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        papers = conn.execute("SELECT COUNT(*) as cnt FROM s2_papers;").fetchone()["cnt"]
        edges = conn.execute("SELECT COUNT(*) as cnt FROM s2_edges;").fetchone()["cnt"]
        cites = conn.execute("SELECT COUNT(*) as cnt FROM s2_edges WHERE relation='cites';").fetchone()["cnt"]
        cited_by = conn.execute("SELECT COUNT(*) as cnt FROM s2_edges WHERE relation='cited_by';").fetchone()["cnt"]
        fetches = conn.execute("SELECT COUNT(*) as cnt FROM s2_fetch_log;").fetchone()["cnt"]
        
        print(f"S2 Database: {db_path}")
        print(f"  Papers cached: {papers}")
        print(f"  Total edges: {edges}")
        print(f"    - cites (references): {cites}")
        print(f"    - cited_by (citations): {cited_by}")
        print(f"  Fetch log entries: {fetches}")
    finally:
        conn.close()
    return 0


def cmd_s2_export(args: argparse.Namespace) -> int:
    """Export S2 edges to edge list or GraphML."""
    db_path = Path(args.db).expanduser()
    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        return 1
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        edges = conn.execute("""
            SELECT src_paper_id, dst_paper_id, relation, is_influential
            FROM s2_edges
            ORDER BY src_paper_id, dst_paper_id;
        """).fetchall()
        
        if args.format == "edgelist":
            output_lines = []
            for e in edges:
                line = f"{e['src_paper_id']}\t{e['dst_paper_id']}\t{e['relation']}"
                if e['is_influential']:
                    line += "\tinfluential"
                output_lines.append(line)
            content = "\n".join(output_lines)
        else:  # graphml
            nodes = set()
            for e in edges:
                nodes.add(e['src_paper_id'])
                nodes.add(e['dst_paper_id'])
            
            lines = ['<?xml version="1.0" encoding="UTF-8"?>']
            lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">')
            lines.append('  <key id="relation" for="edge" attr.name="relation" attr.type="string"/>')
            lines.append('  <key id="influential" for="edge" attr.name="influential" attr.type="boolean"/>')
            lines.append('  <graph id="G" edgedefault="directed">')
            for n in sorted(nodes):
                lines.append(f'    <node id="{n}"/>')
            for i, e in enumerate(edges):
                inf = "true" if e['is_influential'] else "false"
                lines.append(f'    <edge id="e{i}" source="{e["src_paper_id"]}" target="{e["dst_paper_id"]}">')
                lines.append(f'      <data key="relation">{e["relation"]}</data>')
                lines.append(f'      <data key="influential">{inf}</data>')
                lines.append('    </edge>')
            lines.append('  </graph>')
            lines.append('</graphml>')
            content = "\n".join(lines)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Exported {len(edges)} edges to {args.output}")
        else:
            print(content)
    finally:
        conn.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified biomedical literature API wrapper for Pharma×AI reviews."
    )
    
    # Global arguments
    parser.add_argument("--s2-api-key", default="", 
                        help="Semantic Scholar API key. Leave empty for public shared pool (no x-api-key).")
    parser.add_argument("--s2-rps", type=float, default=8.0, 
                        help="Semantic Scholar request rate limit (RPS). Shared pool recommends 5~10.")
    
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    # Search command
    p_search = sub.add_parser("search", help="Search across biomedical databases.")
    p_search.add_argument("query", help="Search query.")
    p_search.add_argument(
        "--sources",
        help="Comma-separated sources: pubmed,europe_pmc,crossref,semantic_scholar",
    )
    p_search.add_argument("--max-results", type=int, default=20, help="Max results per source.")
    p_search.add_argument("--pubmed-api-key", help="NCBI API key for higher rate limits.")
    p_search.add_argument("--sleep", type=float, default=0.5, help="Sleep between source queries.")
    p_search.add_argument("--dedupe", action="store_true", help="Deduplicate across sources.")
    p_search.set_defaults(fn=cmd_search)
    
    # Fetch command
    p_fetch = sub.add_parser("fetch", help="Fetch metadata for a specific paper.")
    p_fetch.add_argument("--pmid", help="PubMed ID to fetch.")
    p_fetch.add_argument("--doi", help="DOI to fetch.")
    p_fetch.add_argument("--pubmed-api-key", help="NCBI API key.")
    p_fetch.set_defaults(fn=cmd_fetch)
    
    # S2 Enrich command - batch fetch paper metadata
    p_s2_enrich = sub.add_parser("s2-enrich", help="Batch fetch S2 paper metadata.")
    p_s2_enrich.add_argument("--db", default="./notes/s2-cache.sqlite3", 
                              help="SQLite database path for S2 cache.")
    p_s2_enrich.add_argument("--ids-file", help="File with paper IDs (one per line). Supports ARXIV:xxx, DOI:xxx, etc.")
    p_s2_enrich.add_argument("--timeout-s", type=int, default=30, help="Request timeout in seconds.")
    p_s2_enrich.set_defaults(fn=cmd_s2_enrich)
    
    # S2 References command
    p_s2_refs = sub.add_parser("s2-references", help="Fetch S2 references (papers this paper cites).")
    p_s2_refs.add_argument("--db", default="./notes/s2-cache.sqlite3", 
                            help="SQLite database path for S2 cache.")
    p_s2_refs.add_argument("--ids-file", help="File with paper IDs (one per line).")
    p_s2_refs.add_argument("--timeout-s", type=int, default=30, help="Request timeout in seconds.")
    p_s2_refs.set_defaults(fn=lambda a: cmd_s2_graph(a, mode="references"))
    
    # S2 Citations command
    p_s2_cites = sub.add_parser("s2-citations", help="Fetch S2 citations (papers citing this paper).")
    p_s2_cites.add_argument("--db", default="./notes/s2-cache.sqlite3", 
                             help="SQLite database path for S2 cache.")
    p_s2_cites.add_argument("--ids-file", help="File with paper IDs (one per line).")
    p_s2_cites.add_argument("--timeout-s", type=int, default=30, help="Request timeout in seconds.")
    p_s2_cites.set_defaults(fn=lambda a: cmd_s2_graph(a, mode="citations"))
    
    # S2 Stats command
    p_s2_stats = sub.add_parser("s2-stats", help="Show S2 database statistics.")
    p_s2_stats.add_argument("--db", default="./notes/s2-cache.sqlite3", 
                             help="SQLite database path.")
    p_s2_stats.set_defaults(fn=cmd_s2_stats)
    
    # S2 Export command
    p_s2_export = sub.add_parser("s2-export", help="Export S2 edges to file.")
    p_s2_export.add_argument("--db", default="./notes/s2-cache.sqlite3", 
                              help="SQLite database path.")
    p_s2_export.add_argument("--format", choices=["edgelist", "graphml"], default="edgelist",
                              help="Output format.")
    p_s2_export.add_argument("--output", "-o", help="Output file (stdout if not specified).")
    p_s2_export.set_defaults(fn=cmd_s2_export)
    
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
