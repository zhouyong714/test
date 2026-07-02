# Search Strategy Log (PRISMA-S Aligned)

> **Project**: [Project Title]  
> **Created**: YYYY-MM-DD  
> **Last Updated**: YYYY-MM-DD  
> **Author**: [Author Name]

---

## Search Overview

| Item | Description |
|------|-------------|
| **Objective** | [What is the review trying to find?] |
| **Date Range** | [YYYY - YYYY] |
| **Languages** | English |
| **Databases Searched** | PubMed, Europe PMC, arXiv, Semantic Scholar |

---

## Database: PubMed (NCBI)

### Search 1: [Topic Area]
- **Date Executed**: YYYY-MM-DD
- **Query**:
  ```
  ("drug discovery"[MeSH] OR "drug design"[MeSH]) 
  AND ("deep learning"[tiab] OR "graph neural network"[tiab] OR "transformer"[tiab])
  AND ("2020"[PDAT] : "2024"[PDAT])
  ```
- **Filters Applied**: 
  - Publication Type: Journal Article, Review
  - Language: English
  - Date: 2020-2024
- **Total Hits**: [N]
- **Notes**: [Any observations about results]

### Search 2: [Specific Subtopic]
- **Date Executed**: YYYY-MM-DD
- **Query**:
  ```
  [Query string]
  ```
- **Filters Applied**: [List]
- **Total Hits**: [N]
- **Notes**: [Any observations]

---

## Database: Europe PMC

### Search 1: [Topic Area]
- **Date Executed**: YYYY-MM-DD
- **Query**:
  ```
  (ABSTRACT:"ADMET prediction" OR ABSTRACT:"molecular property") 
  AND (ABSTRACT:"machine learning" OR ABSTRACT:"deep learning")
  AND (PUB_YEAR:[2020 TO 2024])
  ```
- **Filters Applied**:
  - Open Access: Yes (optional)
- **Total Hits**: [N]
- **Notes**: [Any observations]

---

## Database: arXiv

### Search 1: [Topic Area]
- **Date Executed**: YYYY-MM-DD
- **Categories**: cs.LG, q-bio.BM, stat.ML
- **Query**:
  ```
  all:("drug discovery" AND ("graph neural network" OR "molecular generation"))
  ```
- **Date Range**: 2020-01-01 to 2024-12-31
- **Total Hits**: [N]
- **Notes**: [Any observations]

---

## Database: Semantic Scholar

### Search 1: [Topic Area]
- **Date Executed**: YYYY-MM-DD
- **Query**: [Natural language query]
- **Filters**:
  - Year: 2020-2024
  - Fields of Study: Computer Science, Biology, Chemistry
- **Total Hits**: [N]
- **Notes**: [Any observations]

---

## Deduplication

| Step | Records |
|------|---------|
| **Total from all sources** | [N] |
| **Duplicates by DOI** | -[N] |
| **Duplicates by Title** | -[N] |
| **After Deduplication** | [N] |

**Method**: Automated matching by DOI, then fuzzy title matching (threshold 0.9)

---

## Screening Criteria

### Inclusion Criteria
1. Original research or systematic review
2. Focuses on AI/ML methods for drug discovery
3. Published in peer-reviewed venue or established preprint server
4. English language
5. Published 2020-2024 (exceptions for foundational works)

### Exclusion Criteria
1. Not related to drug discovery (e.g., pure chemistry without pharma context)
2. Conference abstracts only (no full paper)
3. Editorial, commentary, or opinion pieces
4. Non-English
5. Retracted or withdrawn

---

## PRISMA Flow Summary

```
Records identified through database searching (n = [N])
    ↓
Records after duplicates removed (n = [N])
    ↓
Records screened (n = [N])
    ↓
Records excluded (n = [N])
    ↓
Full-text articles assessed for eligibility (n = [N])
    ↓
Full-text articles excluded with reasons (n = [N])
    ↓
Studies included in qualitative synthesis (n = [N])
```

---

## Search Log Updates

| Date | Update Description | By |
|------|-------------------|-----|
| YYYY-MM-DD | Initial search | [Name] |
| YYYY-MM-DD | Added [database] search | [Name] |
| YYYY-MM-DD | Updated with recent publications | [Name] |

---

## Reproducibility Notes

- All queries are documented verbatim above
- Results exported to `notes/records.csv`
- Screening decisions in `notes/screening.csv`
- Flow counts in `notes/prisma-counts.json`
