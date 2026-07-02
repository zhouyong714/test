# Benchmark Selection Principles

> **Principles over lists**: Dynamic benchmark selection based on review scope, not static enumeration.

---

## 1. Philosophy

Traditional reviews enumerate benchmarks exhaustively. This leads to:
- Obsolete lists (new benchmarks emerge monthly)
- Irrelevant coverage (benchmarks outside review scope)
- Missing context (why a benchmark matters)

**Our approach**: Define selection *principles* that guide dynamic discovery.

---

## 2. Core Selection Principles

### Principle 1: Scope Alignment
> A benchmark is relevant if it directly tests capabilities within the review's scope.

**Check against `scope.yaml`**:
```yaml
# scope.yaml
scope:
  tasks: [ADMET_Prediction, Molecular_Generation]
  modalities: [Small_Molecule, Graph]
  r_and_d_stages: [Hit, Lead, ADMET]
```

A benchmark for protein folding is OUT if scope covers small-molecule ADMET.

### Principle 2: Citation Threshold
> Include benchmarks cited by ≥2 papers in the review corpus.

This ensures:
- Community acceptance
- Sufficient comparison data
- Not one-off datasets

### Principle 3: Temporal Relevance
> Prefer benchmarks with active submissions within 2 years.

Check:
- Last paper using this benchmark
- Leaderboard activity
- Maintenance status

**Exception**: Foundational benchmarks (MoleculeNet, ChEMBL) remain relevant regardless.

### Principle 4: Reproducibility Score
> Prioritize benchmarks with standard splits and public leaderboards.

| Reproducibility | Criteria | Priority |
|-----------------|----------|----------|
| High | Public data + standard split + leaderboard | ✅ Include |
| Medium | Public data + standard split | ✅ Include with note |
| Low | Public data only | ⚠️ Include if essential |
| None | Proprietary / unreproducible | ❌ Exclude or cite limitations |

### Principle 5: Coverage Balance
> Select benchmarks that together cover the taxonomy axes.

Ensure at least one benchmark per:
- Major task category
- Major modality
- Major R&D stage

---

## 3. Benchmark Pools

Organize candidates into pools for structured selection:

### Pool A: Must-Include (Foundational)
Benchmarks that define the field. Include unconditionally if in scope.

**Discovery**: Search for "benchmark" + task in Google Scholar, check citations > 500.

### Pool B: High-Relevance (Established)
Widely-used benchmarks with 100-500 citations.

**Discovery**: Check Papers With Code leaderboards, TDC benchmarks.

### Pool C: Emerging (Recent)
Benchmarks from last 2 years gaining traction.

**Discovery**: Search arXiv for "[task] benchmark" + year filter.

### Pool D: Domain-Specific
Niche benchmarks for specific applications (e.g., clinical trial endpoints).

**Discovery**: Search PubMed for therapeutic area + benchmark.

---

## 4. Selection Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. PARSE SCOPE                                          │
│    - Extract tasks, modalities, R&D stages from scope.yaml │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 2. DISCOVER CANDIDATES                                  │
│    - Search literature for benchmarks per task          │
│    - Check Papers With Code, TDC, MoleculeNet           │
│    - Web-confirm authority (citations, leaderboard)     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 3. APPLY PRINCIPLES                                     │
│    - Filter by scope alignment (P1)                     │
│    - Check citation threshold (P2)                      │
│    - Verify temporal relevance (P3)                     │
│    - Score reproducibility (P4)                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 4. BALANCE COVERAGE                                     │
│    - Ensure taxonomy axis coverage (P5)                 │
│    - Fill gaps from Pool C/D if needed                  │
│    - Document selection rationale                       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 5. OUTPUT                                               │
│    - benchmark-catalog.yaml (full candidate list)       │
│    - benchmark-table.csv (selected with rationale)      │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Rationale Documentation

Every selected benchmark MUST have a documented rationale in `Benchmark_Selection_Rationale`:

### Good Rationales
- "Foundational ADMET benchmark; 1000+ citations; standard scaffold split"
- "Only benchmark with 3D conformer data for molecular docking"
- "TDC official benchmark for BBB permeability; active leaderboard"

### Bad Rationales
- "Popular" (too vague)
- "We used it before" (not principle-based)
- "" (missing)

---

## 6. Exclusion Criteria

Explicitly exclude benchmarks that:
1. **Out of scope**: Task/modality not in `scope.yaml`
2. **Obsolete**: Superseded by newer benchmark with same purpose
3. **Unreproducible**: No public data or non-standard splits
4. **Low adoption**: < 2 papers in review corpus
5. **Controversial**: Known data leakage or methodology issues

Document exclusions in `benchmark-catalog.yaml` under `excluded` section.

---

## 7. Validation

### Automated Checks (benchmark_rationale_validator.py)

```bash
python3 scripts/benchmark_rationale_validator.py <paper_dir>
```

Validates:
- [ ] Every benchmark in table has non-empty Selection_Rationale
- [ ] Rationale mentions at least one principle (P1-P5)
- [ ] No benchmark marked "excluded" appears in table
- [ ] Coverage: at least 1 benchmark per major task in scope

### Manual Review Checklist

- [ ] Do selected benchmarks represent current state of field?
- [ ] Are emerging benchmarks considered (not just classics)?
- [ ] Is rationale defensible to domain expert reviewer?

---

## 8. Integration with Issues CSV

The `Benchmark_Selection_Rationale` column in Issues CSV (v2.4) should reference:
- Specific benchmarks being discussed
- Why they were selected for this issue
- Any caveats or limitations

Example:
```csv
Benchmark_Selection_Rationale: "Using MoleculeNet-BBBP (P1: scope-aligned) and TDC-ADME (P4: standard split) for BBB prediction comparison"
```

---

## 9. Template: benchmark-catalog.yaml

See `assets/benchmark-catalog-template.yaml` for the full structure:

```yaml
metadata:
  generated_at: <timestamp>
  scope_hash: <hash of scope.yaml>
  
pools:
  must_include:
    - name: MoleculeNet
      reason: Foundational; 2000+ citations
      tasks: [Property_Prediction, ADMET_Prediction]
      
  high_relevance:
    - name: TDC-ADMET
      reason: TDC official; active leaderboard
      tasks: [ADMET_Prediction]
      
  emerging:
    - name: DrugBench-2024
      reason: Recent; addresses distribution shift
      tasks: [ADMET_Prediction]
      
  excluded:
    - name: OldBench
      reason: Superseded by MoleculeNet; data leakage issues
```
