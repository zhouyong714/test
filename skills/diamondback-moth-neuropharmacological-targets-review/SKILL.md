---
name: diamondback-moth-neuropharmacological-targets-review
description: >
  Write a LaTeX review article on the fixed topic "小菜蛾神经系统相关药理靶标概述"
  using the IEEEtran template and verified BibTeX citations. Keep the same
  workflow, scripts, evidence tables, and PRISMA-style review structure as arxiv-paper-writer.
compatibility: >
  Python 3.8+ for scripts. Web browsing/search for citation verification.
  LaTeX is required (pdflatex + bibtex or latexmk).
  For pharma mode: PubMed/Europe PMC/Crossref API access recommended.
metadata:
  short-description: Fixed-topic review paper skill for "小菜蛾神经系统相关药理靶标概述"
  schema-version: "2.4"
---

# Review Paper Workflow (IEEEtran template)

This skill is a topic-fixed clone of `arxiv-paper-writer`.

## Fixed Topic
- Always use `小菜蛾神经系统相关药理靶标概述` as the review topic unless the user explicitly asks to change it.
- Keep the original workflow, scripts, templates, references, outputs, and review gates unchanged.

## How to Use
1. Read and follow `D:/papers/codex/.agents/skills/arxiv-paper-writer/SKILL.md` as the canonical workflow.
2. Run the copied `scripts/`, `references/`, and `assets/` from this skill folder so the new skill remains self-contained.
3. Replace every example `--topic "<topic>"` invocation with `--topic "小菜蛾神经系统相关药理靶标概述"`.
4. Keep all validation, citation, plan/issues, PRISMA, and compile steps unchanged.

## Fixed Command Variants

```bash
python3 scripts/bootstrap_ieee_review_paper.py --stage kickoff --topic "小菜蛾神经系统相关药理靶标概述" [--pharma]
python3 scripts/bootstrap_ieee_review_paper.py --stage issues --topic "小菜蛾神经系统相关药理靶标概述" --with-literature-notes [--pharma]
python3 scripts/create_paper_plan.py --topic "小菜蛾神经系统相关药理靶标概述" --stage plan --output-dir <paper_dir> [--pharma]
python3 scripts/create_paper_plan.py --topic "小菜蛾神经系统相关药理靶标概述" --stage issues --timestamp "<TS>" --slug "<slug>" --output-dir <paper_dir> --with-literature-notes [--pharma]
```

## Resources
- `scripts/`, `references/`, and `assets/` in this folder are copied from `arxiv-paper-writer` without functional changes.
- If the source skill is updated later, this clone will not update automatically.
