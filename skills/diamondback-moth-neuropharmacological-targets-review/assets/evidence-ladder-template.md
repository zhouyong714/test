# Evidence Ladder Checklist

> Per-paper checklist for assigning evidence levels (L0-L3).
> See `references/evidence-ladder.md` for full definitions.

---

## Paper Information

- **Citation Key**: `_______________`
- **Title**: `_______________`
- **Year**: `_______________`

---

## Level Determination Checklist

### L0: Anecdotal / No Validation
- [ ] No experimental validation presented
- [ ] Opinion piece, editorial, or commentary
- [ ] Blog post or white paper without peer review
- [ ] Results not reproducible (no code/data)

**If ANY checked → L0**

---

### L1: In-Silico Only, Single Dataset
- [ ] Computational experiments only
- [ ] Single dataset used for evaluation
- [ ] Random split (no scaffold/temporal)
- [ ] Internal validation only (train/val/test from same source)
- [ ] No comparison to established baselines

**If ALL checked and no L2+ criteria → L1**

---

### L2: Multi-Dataset OR External Validation
Check if ANY of the following apply:

- [ ] Multiple independent datasets used
- [ ] Scaffold or temporal split employed
- [ ] External validation set (different source than training)
- [ ] Cross-validation with proper stratification
- [ ] Comparison to multiple established baselines
- [ ] Ablation studies demonstrate robustness
- [ ] Prospective in-silico validation (time-based)

**If ANY checked → L2 (unless L3 criteria met)**

---

### L3: Experimental / Clinical Validation
Check if ANY of the following apply:

- [ ] Wet-lab experimental validation of predictions
- [ ] Prospective prediction → experimental confirmation
- [ ] Clinical trial data used for validation
- [ ] Real-world deployment results reported
- [ ] Published in Nature/Science/Cell tier journal with experimental validation
- [ ] DMTA (Design-Make-Test-Analyze) cycle completed
- [ ] Regulatory submission based on results

**If ANY checked → L3**

---

## Decision Tree

```
                    ┌─────────────────────────┐
                    │ Has experimental        │
                    │ (wet-lab/clinical)      │
                    │ validation?             │
                    └───────────┬─────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                   YES                   NO
                    │                     │
                    ▼                     ▼
                  ┌───┐        ┌─────────────────────┐
                  │L3 │        │ Multi-dataset OR    │
                  └───┘        │ external validation │
                               │ OR scaffold split?  │
                               └───────────┬─────────┘
                                          │
                               ┌──────────┴──────────┐
                               │                     │
                              YES                   NO
                               │                     │
                               ▼                     ▼
                             ┌───┐        ┌─────────────────────┐
                             │L2 │        │ Any computational   │
                             └───┘        │ validation?         │
                                          └───────────┬─────────┘
                                                     │
                                          ┌──────────┴──────────┐
                                          │                     │
                                         YES                   NO
                                          │                     │
                                          ▼                     ▼
                                        ┌───┐                 ┌───┐
                                        │L1 │                 │L0 │
                                        └───┘                 └───┘
```

---

## Final Assignment

- **Assigned Level**: `L___`
- **Justification**: `_______________________________________________`
- **Reviewer**: `_______________`
- **Date**: `_______________`

---

## Special Cases

### Preprints
- Preprints can achieve L1 or L2 based on methodology
- Preprints CANNOT achieve L3 without published experimental validation
- Mark `[Preprint]` in all citations

### Mixed Evidence
- If paper has both in-silico and experimental components:
  - Assign based on the evidence supporting YOUR specific claim
  - A paper can be L3 for one claim and L1 for another

### Review/Survey Papers
- Reviews themselves are L0 (no original validation)
- But they can cite L1-L3 evidence
- Prefer citing primary sources over reviews

---

## Upgrade Triggers

If a paper is currently assigned L1 or L2, upgrade if:

| Current | Upgrade Trigger | New Level |
|---------|-----------------|-----------|
| L1 | External dataset validation added | L2 |
| L1 | Scaffold/temporal split analysis | L2 |
| L2 | Wet-lab confirmation of predictions | L3 |
| L2 | Clinical deployment results | L3 |
| Preprint | Published version with experiments | May upgrade |

---

## Quick Reference: Common Scenarios

| Scenario | Level |
|----------|-------|
| arXiv paper, random split, one dataset | L1 |
| NeurIPS paper, scaffold split, two datasets | L2 |
| Nature paper with experimental validation | L3 |
| Blog post about LLMs in drug discovery | L0 |
| bioRxiv with prospective validation | L2 (preprint) |
| Clinical trial results published in Lancet | L3 |
