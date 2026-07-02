# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of custom skills for the Codex agent system. Each skill is a self-contained module that provides specialized capabilities for academic paper writing, LaTeX editing, and AI agent collaboration.

## Available Skills

### arxiv-paper-writer
Comprehensive workflow for writing ML/AI and Pharma×AI review papers using the IEEEtran LaTeX template. Supports two modes:
- **Standard mode**: General ML/AI reviews
- **Pharma mode** (`--pharma` flag): Pharmaceutical AI reviews with evidence tables, PRISMA workflow, and drug R&D lifecycle framing

### latex-rhythm-refiner
Post-processes LaTeX prose to improve readability through varied sentence/paragraph lengths while preserving all citations and semantic meaning.

### collaborating-with-claude
Delegates tasks to Claude Code CLI via a bridge script for second opinions, code review, and multi-turn collaboration sessions.

### collaborating-with-gemini
Delegates tasks to Gemini CLI via a bridge script for alternative perspectives and prototyping.

## Common Development Commands

### Running Scripts
All Python scripts should be run from the skill's root directory (where `scripts/` lives):

```bash
# From arxiv-paper-writer skill directory
python3 scripts/arxiv_registry.py --help
python3 scripts/compile_paper.py --project-dir <paper_dir>
python3 scripts/bootstrap_ieee_review_paper.py --stage kickoff --topic "Your Topic"
python3 scripts/validate_paper_issues.py <paper_dir>/issues/<file>.csv
```

### Paper Compilation
```bash
# Compile a paper project
python3 scripts/compile_paper.py --project-dir <paper_dir>

# With page count report
python3 scripts/compile_paper.py --project-dir <paper_dir> --report-page-counts
```

### arXiv Registry Operations
```bash
# Initialize registry
python3 scripts/arxiv_registry.py --project-dir <paper_dir> init

# Search arXiv
python3 scripts/arxiv_registry.py --project-dir <paper_dir> search 'all:"world model" AND cat:cs.LG'

# Export BibTeX with stable citation keys
python3 scripts/arxiv_registry.py --project-dir <paper_dir> export-bibtex <arxiv_id> --out-bib <paper_dir>/ref.bib
```

## Architecture

### Skill Structure
Each skill follows this layout:
```
skill-name/
├── SKILL.md              # Skill metadata and usage instructions
├── assets/               # Templates and static resources
├── references/           # Reference documentation and guides
└── scripts/              # Python utilities and automation
```

### Paper Project Structure
The arxiv-paper-writer skill creates projects with:
```
<paper_dir>/
├── main.tex              # Main LaTeX document
├── ref.bib               # BibTeX references
├── IEEEtran.cls          # Document class
├── plan/                 # Planning documents (timestamped)
├── issues/               # Issue tracking CSVs (timestamped)
└── notes/                # Literature notes, arXiv registry, scope/taxonomy (pharma mode)
```

### Key Design Patterns

**Gated Workflow**: The arxiv-paper-writer enforces a strict gate system:
1. Gate 0: Research snapshot + draft plan (user approval required)
2. Gate 1: Create issues CSV (only after plan approval)
3. Phase 2: Per-issue writing loop (tracked in CSV)
4. Phase 3: QA gate (validation before delivery)

**Timestamped Artifacts**: Plans and issues use `YYYY-MM-DD_HH-mm-ss-<slug>` naming for auditability and version tracking.

**Registry Pattern**: The arXiv registry (`arxiv_registry.py`) uses SQLite to cache metadata and BibTeX entries, avoiding redundant API calls and ensuring stable citation keys.

**Bridge Pattern**: Collaboration skills use bridge scripts that wrap CLI tools and return structured JSON with session IDs for multi-turn conversations.

## Important Conventions

### Path Handling
- Scripts expect to be run from the skill root directory
- `<paper_dir>` refers to the paper project root (contains `main.tex`, `ref.bib`)
- Use `--project-dir` to specify paper directory for most scripts
- Paths in documentation like `plan/...` are relative to `<paper_dir>`

### Citation Management
- Never fabricate citations
- Always verify citations via web search before adding to `ref.bib`
- Use `arxiv_registry.py` for arXiv papers (no ad-hoc curl/wget)
- Pharma mode: Apply preprint policy rules (see `references/preprint-policy.md`)

### Issues CSV Workflow
- Issues CSV is the execution contract for paper writing
- Update `Status` column: `TODO` → `DOING` → `DONE` → `SKIP`
- Track `Verified_Citations` count per issue
- Split/insert new issues (e.g., `W6a`, `Q5`) when scope grows
- Validate after changes: `python3 scripts/validate_paper_issues.py <file>.csv`
- Pharma mode uses v2.4 schema (64 columns) with playbook gates

### Schema Versions
- Standard mode: v1.0 (10 columns)
- Pharma mode: v2.4 (64 columns with playbook compliance tracking)
- Use `--pharma` flag consistently across all commands for pharma projects

### LaTeX Compilation
- Prefer `latexmk` if available, fallback to `pdflatex + bibtex`
- Fix `Overfull \hbox` warnings before marking issues `DONE`
- Use two-column layout constraints (IEEEtran template)
- Add `\label{ReferencesStart}` at bibliography start for page counting

## Playbook Compliance (Pharma Mode)

The arxiv-paper-writer enforces 6 hard constraints for pharma reviews:

1. **Opening Three-Part Structure**: Context/Trend + Pain Point + Gap Statement (with However/Yet/Despite)
2. **Scope & Deliverables**: 3-6 bullet scope statement in Introduction
3. **Taxonomy-First**: Taxonomy appears in first 10-20% of paper body
4. **Section Narrative Loop**: Each section has Mechanism → Methods → Failure Modes → Pharma Implications
5. **Actionable Roadmap**: Conclusion has short-term (6-18mo) + medium-term (2-5yr) milestones
6. **Evidence Binding**: All quantitative claims have citations, preprints marked `[Preprint]`

Validate compliance: `python3 scripts/playbook_gate_checker.py <paper_dir>`

## Shell Quoting for Bridge Scripts

When passing prompts with Markdown backticks to bridge scripts, use heredoc syntax to avoid shell command substitution:

```bash
PROMPT="$(cat <<'EOF'
Review src/auth.py around login() and propose fixes.
OUTPUT: Unified Diff Patch ONLY.
EOF
)"
python3 scripts/claude_bridge.py --cd "." --PROMPT "$PROMPT"
```

See `collaborating-with-claude/references/shell-quoting.md` for details.

## Testing and Validation

### Validate Issues CSV
```bash
python3 scripts/validate_paper_issues.py <issues.csv>           # Standard mode
python3 scripts/validate_paper_issues.py <issues.csv> --pharma  # Pharma mode
python3 scripts/validate_paper_issues.py <issues.csv> --strict  # Extra warnings
```

### Verify BibTeX References
```bash
python3 scripts/verify_ref_bib.py <paper_dir>/ref.bib
```

### Check Playbook Compliance (Pharma)
```bash
python3 scripts/playbook_gate_checker.py <paper_dir>
```

## Common Pitfalls

- **Don't skip gates**: Never write prose in `main.tex` before plan approval and issues CSV creation
- **Don't bypass validation**: Always run `validate_paper_issues.py` after modifying issues CSV
- **Don't mix modes**: Use `--pharma` consistently or not at all within a project
- **Don't modify templates**: IEEEtran template is fixed; work within two-column layout constraints
- **Don't create untracked work**: Add new issues to CSV when scope grows; don't do work outside the issues contract
- **Don't use relative timestamps**: Convert "Thursday" → "2026-04-27" in project memories

## File Naming Patterns

- Plans: `YYYY-MM-DD_HH-mm-ss-<slug>.md`
- Issues: `YYYY-MM-DD_HH-mm-ss-<slug>.csv`
- Slugs: lowercase, hyphen-delimited (e.g., `transformer-vision-review`)
- Registry: `notes/arxiv-registry.sqlite3` (per paper project)
- Literature notes: `notes/literature-notes.md` (optional)
- Pharma artifacts: `notes/scope.yaml`, `notes/taxonomy.yaml`
