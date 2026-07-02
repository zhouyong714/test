---
name: arxiv-paper-writer
description: >
  Write LaTeX ML/AI and Pharma×AI review articles for arXiv using the IEEEtran template
  and verified BibTeX citations. Supports dual-mode: general ML/AI reviews and
  pharmaceutical AI reviews with evidence tables, PRISMA workflow, and drug R&D lifecycle framing.
compatibility: >
  Python 3.8+ for scripts. Web browsing/search for citation verification.
  LaTeX is required (pdflatex + bibtex or latexmk).
  For pharma mode: PubMed/Europe PMC/Crossref API access recommended.
metadata:
  short-description: ML/AI and Pharma×AI review papers (IEEEtran template) with verified citations
  schema-version: "2.4"
---

# Review Paper Workflow (IEEEtran template)

## When to Use
- ML/AI review papers for arXiv (main text ~6-10 pages; references excluded)
- **Pharma×AI reviews** focusing on drug discovery, ADMET, molecular design, etc.
- LaTeX + BibTeX workflow with verified citations
- Citation validation/repair on existing LaTeX projects

## When NOT to Use
- Novel experimental research papers (this is a review workflow)
- Non-academic documents
- Clinical practice guidelines (requires different evidence standards)

## Review Mode Selection

### Standard Mode (ML/AI)
Default mode for general machine learning and AI reviews.

### Pharma Mode (Pharma×AI)
Activated with `--pharma` flag. Adds:
- Drug R&D lifecycle framing (Target → Hit → Lead → ADMET → Clinical)
- PubMed/Europe PMC/Crossref literature search workflow
- Evidence tables (study-table + benchmark-table)
- PRISMA-style search documentation
- Critical limitations checklist per section
- Preprint policy enforcement (bioRxiv/medRxiv rules)
- Evidence ladder (L0-L3) tracking

## Inputs
- Topic description (required)
- Constraints: venue, page limit, author/affiliations (optional)
- **Review mode**: `--pharma` for pharmaceutical AI reviews
- Existing project path for citation validation (optional)

## Outputs
- `main.tex` (LaTeX source)
- `ref.bib` (verified BibTeX entries)
- `IEEEtran.cls`
- `plan/<timestamp>-<slug>.md`, `issues/<timestamp>-<slug>.csv`
- Figures/tables; `main.pdf`
- `notes/literature-notes.md` (optional per-citation notes)
- `notes/arxiv-registry.sqlite3` (arXiv metadata/BibTeX cache)
- **Pharma mode additional outputs:**
  - `notes/scope.yaml` (review scope contract)
  - `notes/taxonomy.yaml` (dynamic vocabulary)
  - `notes/search-log.md` (PRISMA-S aligned)
  - `notes/study-table.csv` (evidence extraction table)
  - `notes/dataset-benchmark-table.csv` (benchmark catalog)

**Conventions**: run `python3 scripts/...` from this skill folder (where `scripts/` lives); `<paper_dir>` is the paper/project root (contains `main.tex`, `ref.bib`, `plan/`, `issues/`, `notes/`). Paths like `plan/...` are under `<paper_dir>`. For arXiv discovery/metadata/BibTeX, use `scripts/arxiv_registry.py` (no ad-hoc curl/wget).

---

## Review Writing Playbook (硬约束)

> **核心理念**：高质量综述执行一套可复现的"叙事—论证—落地动作链"。
> 以下 6 条硬约束强制每篇综述遵循相同的写作动作。
> 详细指南见 `references/review-writing-playbook.md`。

### Playbook Rule 1: Opening Three-Part Structure
Introduction **MUST** include:
1. **Context/Trend (Why now)**: Field necessity and urgency
2. **Pain Point (What hurts)**: Core problem from domain perspective
3. **Gap Statement**: MUST contain `However|Yet|Despite` + explicit gap

**Validation**: `has_context_pain_gap=Y` in Issues CSV

### Playbook Rule 2: Scope & Deliverables
Introduction **MUST** include 3-6 bullet scope statement:
- Task coverage (which AI tasks)
- Object scope (which modalities/molecules)
- Evidence level scope (which R&D stages)
- Deliverables list (taxonomy, tables, roadmap)

**FORBIDDEN**: "We review recent progress" without specifics
**Validation**: `has_scope_deliverables=Y` in Issues CSV

### Playbook Rule 3: Taxonomy-First
- Taxonomy/classification MUST appear in first 10-20% of paper body
- All subsequent sections MUST map back to taxonomy
- Prefer pharma-decision-driven organization over AI-tech-driven

**Validation**: `has_taxonomy_map=Y` in Issues CSV

### Playbook Rule 4: Section Narrative Loop
Each technical section **MUST** contain:
1. **Mechanism** (1¶): Why it works (inductive bias, math principle)
2. **Representative Methods** (2-4¶): With comparison, not listing
3. **Failure Modes** (≥1¶): When/why it fails, boundary conditions
4. **Pharma Implications** (1¶): How practitioners use it

**Validation**: `has_section_loop=Y` in Issues CSV

### Playbook Rule 5: Actionable Roadmap
Conclusion **MUST** include:
- Short-term (6-18 months) + medium-term (2-5 years) milestones
- Reference back to Introduction gap statement
- Dimensions: data, benchmarks, experimental loop, translational path

**FORBIDDEN**: Generic "future work should address" statements
**Validation**: `has_actionable_roadmap=Y` in Issues CSV

### Playbook Rule 6: Evidence Binding
- All quantitative claims MUST have citations
- Uncertainty uses: `preliminary|suggests|may|early evidence`
- Preprints MUST be marked `[Preprint]`, cannot be sole evidence for key claims

---

## Gated Workflow

> Tip: Run `python3 scripts/<script>.py --help` before use.
> Open reference files only when a step calls them out.

### Non-Negotiable Rules
1. **No prose in `main.tex`** until plan approved AND issues CSV exists.
2. First deliverable: research snapshot + outline + clarification questions + draft plan.
3. **Use plan + issues tracking for all new papers; do not opt out.**
4. Issues CSV is the execution contract; update `Status` and `Verified_Citations` per issue, and add/split/insert issue rows when scope grows (do not do untracked work).
5. **Template is fixed**: use IEEEtran two-column layout (`assets/template/IEEEtran.cls`).
   Treat two-column width as a layout constraint (use two-column floats when needed).
6. **Playbook compliance**: All Writing issues must pass playbook gate validation.
7. **Preprint policy** (pharma mode): Follow `references/preprint-policy.md` rules.
8. **Evidence tracking** (pharma mode): Link claims to Evidence_RowIDs.

### Gate 0: Research Snapshot + Draft Plan
1. Confirm constraints (venue, page limit, author block, date range).
2. **Select review mode**: Standard (ML/AI) or Pharma (Pharma×AI with `--pharma`).
3. Translate the topic into search keywords and run a light discovery pass:
   10-20 key papers (see `references/research-workflow.md`).
   - For pharma mode, also search PubMed/Europe PMC (see `references/pharma-search-workflow.md`).
   - After step 4 (once `<paper_dir>` exists), cache arXiv discovery with `arxiv_registry.py search`.
4. Propose 2-4 candidate titles aligned to the topic.
5. Scaffold the project folder and draft plan:
   ```bash
   python3 scripts/bootstrap_ieee_review_paper.py --stage kickoff --topic "<topic>" [--pharma]
   ```
   This copies LaTeX templates from `assets/template/`; plan/issues are generated from templates in `assets/`.
   - Pharma mode also generates `notes/scope.yaml` and `notes/taxonomy.yaml`.
   - Initialize arXiv registry (once): `python3 scripts/arxiv_registry.py --project-dir <paper_dir> init`.
6. **Benchmark Scan** (pharma mode): Discover benchmarks from literature + web, create catalog.
   See `references/benchmark-policy-guide.md` for AUTO discovery rules.
7. Create a **framework skeleton** in `main.tex`
   (section headings + 2-4 bullets per section + seed citations; **no prose**).
   - **Pharma mode**: Use taxonomy-first structure, map to drug R&D lifecycle.
8. Update the plan file to reflect the framework, proposed titles, and section/subsection plan.
9. Compile early: `python3 scripts/compile_paper.py --project-dir <paper_dir>`
   Fix any `Overfull \hbox` warnings (see Layout Hygiene below).
10. Return to user:
    - Proposed outline (5-8 sections, 2-4 bullets each)
    - Planned visualizations (5+) mapped to sections (see `references/visual-templates.md`)
    - Clarification questions
    - **Pharma mode**: Scope.yaml summary, benchmark catalog preview
11. **STOP** until user approves.

### Gate 1: Create Issues CSV (after approval)
1. Check kickoff gate in plan: `- [x] User confirmed scope + outline in chat`.
2. Create issues CSV (script refuses if gate unchecked):
   ```bash
   python3 scripts/bootstrap_ieee_review_paper.py --stage issues --topic "<topic>" --with-literature-notes [--pharma]
   ```
   - Pharma mode uses v2.4 schema (64 columns with playbook gates).
3. Validate:
   ```bash
   python3 scripts/validate_paper_issues.py <paper_dir>/issues/<timestamp>-<slug>.csv [--pharma]
   ```
4. If literature notes are enabled, keep short summaries and (optional) abstract snippets to avoid re-search.
5. The plan may evolve; add/split/insert issues as needed, re‑validate after edits, and keep going until all issues (including inserted ones) are `DONE` or `SKIP` (when feasible, in the same run).

### Phase 2: Per-Issue Writing Loop
For each writing issue in the CSV:
- If an issue balloons (new figure, new subsection, new benchmark set, or a large QA fix), split/insert new issue row(s) (e.g., `W6a`, `Q5`) before proceeding; re-run `python3 scripts/validate_paper_issues.py <issues.csv>`; keep going until all issues are `DONE`/`SKIP`.

1. **Research**: 8-12 section-specific papers.
   - Pharma mode: Include PubMed/Europe PMC sources; update Evidence_RowIDs.
2. **Write**: Never 3 sentences without citations; varied paragraph rhythm
   (see `references/writing-style.md`).
   - **ENFORCE PLAYBOOK**: Check section loop (mechanism → methods → failure → implications).
   - For section intent and structure, use `references/template-usage.md`.
3. **Visualize**: Match content triggers (see `references/visual-templates.md`).
   Prioritize single-column sizing; use double-column spans only when necessary (see Layout Hygiene).
   Cite externally sourced figure content.
4. **Verify**: Web search + open source page (and PDF if available) before adding to `ref.bib`.
   For arXiv entries, append BibTeX via `python3 scripts/arxiv_registry.py --project-dir <paper_dir> export-bibtex <arxiv_id> --out-bib <paper_dir>/ref.bib`.
   - **Pharma mode**: Apply preprint policy and evidence ladder rules.
5. **Playbook Gate** (mandatory for Wx issues):
   - Check `has_section_loop=Y` for all body sections.
   - Check `has_context_pain_gap=Y` for Introduction issues.
   - Check `has_scope_deliverables=Y` for scope statement.
   - Check `has_taxonomy_map=Y` for taxonomy section.
   - Check `has_actionable_roadmap=Y` for Conclusion issues.
6. **Update**: Mark issue `DONE` with `Verified_Citations` count.
   - Pharma mode: Also update `Evidence_RowIDs` if applicable.
7. Compile after meaningful changes; fix `Overfull \hbox` before marking `DONE`.

### Phase 2.5: Rhythm Refinement
After all writing issues are `DONE`, refine prose section-by-section using the `latex-rhythm-refiner` skill. This step varies sentence/paragraph lengths and removes filler phrases while preserving all citations.

### Phase 3: QA Gate
1. Run internal QA checklist (see `references/quality-report.md`).
2. **Playbook Self-Check** (pharma mode): Run checklist from `references/review-writing-playbook.md`.
3. Compile; ensure no `Overfull \hbox` warnings in `main.log`.
4. Validate all playbook gates are satisfied in issues CSV.
5. Deliver `main.tex`, `ref.bib`, figures, and `main.pdf`.

---

## Preprint Policy (Pharma Mode)

> See `references/preprint-policy.md` for full rules.

### Allowed Sources
- **cs.* / stat.ML / eess.***: Generally allowed for methodology
- **q-bio.BM / q-bio.QM**: Computational biology, allowed with standard handling
- **bioRxiv/medRxiv**: Allowed under restrictions (see below)

### Preprint Handling Rules
| Condition | Action |
|-----------|--------|
| Preprint with peer-reviewed version exists | Use peer-reviewed version, NOT preprint |
| Preprint <6 months old, no peer-reviewed version | Mark `[Preprint]` in text, flag `Preprint_Status=unreviewed` |
| Preprint >12 months old, still no peer-reviewed version | Downgrade: cannot support key claims |
| Clinical/safety claims | NEVER cite preprints as sole evidence |

### Forbidden Sources
- Patent applications as evidence (can mention for landscape)
- Personal communications, conference abstracts only
- Social media, blog posts, press releases

---

## Evidence Ladder (Pharma Mode)

> See `references/evidence-ladder.md` for full definitions and examples.

### Evidence Levels

| Level | Name | Definition | Typical Sources |
|-------|------|------------|-----------------|
| L0 | Consensus | Meta-analysis, systematic reviews, regulatory guidance | FDA/EMA guidance, Cochrane reviews |
| L1 | Strong | Prospective studies, randomized trials, multi-site validation | Phase II/III trials, multi-center benchmarks |
| L2 | Moderate | Peer-reviewed single-site studies, established benchmarks | Top-tier journals, established datasets |
| L3 | Preliminary | Preprints, conference papers, small-scale studies | arXiv, bioRxiv, workshop papers |

### Evidence Usage Rules
- **Key claims** (architecture superiority, safety assertions): Require L0-L2
- **Trend indicators**: L3 acceptable with hedging language
- **Novel methods** (no alternatives): L3 acceptable with explicit uncertainty
- **Pharma safety/efficacy**: L0-L1 only, never preprints alone

---

## Existing Paper Workflow (No Re-Scaffold)
If a paper folder already exists, do NOT rerun scaffold:
```bash
# Create plan
python3 scripts/create_paper_plan.py --topic "<topic>" --stage plan --output-dir <paper_dir> [--pharma]
# STOP for approval, then check kickoff gate box
# Create issues (use timestamp/slug from plan filename/frontmatter)
python3 scripts/create_paper_plan.py --topic "<topic>" --stage issues --timestamp "<TS>" --slug "<slug>" --output-dir <paper_dir> --with-literature-notes [--pharma]
```

## Citation-Validation Variant
1. Treat provided path as LaTeX project root.
2. Follow `references/citation-workflow.md`.
3. Use `references/bibtex-guide.md` for BibTeX rules if entries need repair.
4. **Pharma mode**: Also validate preprint policy compliance.
5. Deliver validation report and corrected `ref.bib` if requested.

---

## Success Criteria

**Compilation**: `python3 scripts/compile_paper.py --project-dir <paper_dir>` (exit 0, no "Citation undefined" warnings). Use `--report-page-counts` for main-text page count.

**Standard Quality Metrics**:
- 6-10 pages of main text (references excluded)
- 60-80 total citations (8+ per section)
- 100% citation verification rate
- 70%+ citations from last 3 years
- 5+ visualization types
- All issues `DONE` or `SKIP`

**Pharma Mode Additional Metrics**:
- 30%+ citations from PubMed/PMC sources
- Evidence ladder L0-L2 for all key claims
- 100% preprint policy compliance
- All 6 playbook gates satisfied (via Issues CSV)
- Persona coverage: ≥3 of 5 lifecycle stages addressed

**Playbook Compliance Metrics** (all modes):
- Introduction has Context-Pain-Gap structure (Gap句 with However/Yet/Despite)
- Scope statement has 3-6 explicit deliverable bullets
- Taxonomy appears in first 10-20% of body
- All body sections follow narrative loop (mechanism → methods → failures → implications)
- Conclusion has actionable roadmap (6-18 month + 2-5 year milestones)

---

## Safety & Guardrails
- **Never fabricate** citations or results; add TODO and ask user if evidence missing.
- **Verify every citation** via web search + source page (and PDF if available) before adding to `ref.bib`.
- **Confirm before** large literature searches.
- **Do not overwrite** user files without confirmation.
- **Issues CSV** is the contract; mark `DONE` only when criteria met.
- **No submission bundles** unless user requests.
- **Pharma mode additional**:
  - Never cite preprints for clinical/safety claims.
  - Always mark preprints with `[Preprint]` in text.
  - Use hedging language for L3 evidence.
  - Flag conflicts of interest when evident in source.

## Layout Hygiene
Fix `Overfull \hbox` warnings before marking issues `DONE`:
- Figures: start with `figure` + `\columnwidth`; switch to `figure*` + `\textwidth` if needed
- Tables: prefer `p{...}` column widths / `\tabcolsep` over `\resizebox`
- Equations: use `split`, `multline`, `aligned`, or `IEEEeqnarray` for line-breaking

---

## Issues CSV Schema

### Standard Schema (v1.x)
| Phase | Issues |
|-------|--------|
| Research | Rx: discovery, scaffolding, framework, viz planning |
| Writing | Wx: each section with target citations and visualization |
| Refinement | RFx: apply `latex-rhythm-refiner` skill (after all Wx DONE) |
| QA | Qx: citation verification, QA checklist, compilation, final review |

### Pharma Schema v2.4 (64 columns)
Extended schema for pharma mode with:

**Base Columns (10)**: Issue_ID, Phase, Type, Section_Target, Description, Dependencies, Priority, Status, Verified_Citations, Notes

**Literature Columns (15)**: Search_Keywords, Required_Sources, PubMed_Query, PMC_Query, Preprint_Policy, Evidence_RowIDs, Min_L0L1_Pct, Allowed_Preprint_Categories, ...

**Pharma Columns (15)**: Persona_Tags, Lifecycle_Stage, Benchmark_IDs, Critical_Limitations, Study_Table_Rows, Dataset_IDs, Wet_Lab_Relevance, ...

**Taxonomy Columns (9)**: Primary_Category, Secondary_Categories, AI_Technique_Tags, Molecule_Type_Tags, Disease_Area_Tags, ...

**Playbook Gate Columns (9)**: has_context_pain_gap, has_scope_deliverables, has_taxonomy_map, has_section_loop, has_actionable_roadmap, pharma_workflow_alignment, wet_lab_bridge, benchmarking_strategy, data_provenance_notes

**QA Columns (6)**: Layout_Status, Citation_Check_Status, Playbook_Compliance, Evidence_Compliance, ...

Status: `TODO` → `DOING` → `DONE`. Schema validated by `validate_paper_issues.py --pharma`.

---

## Reference Files Index

### Standard Mode
- `references/research-workflow.md`: Literature search methodology
- `references/writing-style.md`: Prose style guide
- `references/template-usage.md`: Section intent and structure
- `references/visual-templates.md`: Visualization triggers
- `references/citation-workflow.md`: Citation verification process
- `references/bibtex-guide.md`: BibTeX formatting rules
- `references/quality-report.md`: QA checklist

### Pharma Mode Additional
- `references/pharma-search-workflow.md`: PubMed/PMC search methodology
- `references/pharma-outline-templates.md`: Drug R&D lifecycle outlines
- `references/pharma-task-dictionary.md`: Section-specific task guides
- `references/preprint-policy.md`: Preprint handling rules
- `references/evidence-ladder.md`: Evidence level definitions
- `references/benchmark-policy-guide.md`: Benchmark discovery rules
- `references/review-writing-playbook.md`: Writing methodology (6 硬约束)
