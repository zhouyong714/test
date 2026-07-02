# Evidence Table Guide

> How to populate **study-table.csv** and **benchmark-table.csv** in Pharma×AI reviews.

---

## 1. Overview

Pharma×AI reviews require structured evidence extraction to support claims:

| Table | Purpose | Template |
|-------|---------|----------|
| **study-table.csv** | Extract study-level evidence from primary papers | `assets/study-table-template.csv` |
| **benchmark-table.csv** | Catalog datasets and benchmarks with performance metrics | `assets/benchmark-table-template.csv` |

Both tables live under `<paper_dir>/notes/` and are referenced by `Evidence_RowIDs` in the Issues CSV.

---

## 2. Study Table (study-table.csv)

### 2.1 When to Create Rows

Create a row for each **primary study** that:
- Reports original experimental results (not just cites others)
- Is directly relevant to a writing issue
- Provides quantitative evidence for claims in the review

### 2.2 Column Definitions (25 columns)

| Column | Type | Description |
|--------|------|-------------|
| `Row_ID` | String | Unique ID: `S001`, `S002`, ... |
| `Citation_Key` | String | BibTeX key from `ref.bib` |
| `First_Author` | String | Last name of first author |
| `Year` | Integer | Publication year |
| `Title` | String | Paper title (abbreviated OK) |
| `Study_Type` | Enum | `Retrospective`, `Prospective`, `In_Silico`, `Hybrid` |
| `Task` | String | AI task from `taxonomy.yaml` vocabulary |
| `Target_Type` | String | `Small_Molecule`, `Protein`, `RNA`, `Antibody`, `Cell`, `Other` |
| `R_and_D_Stage` | String | `Target`, `Hit`, `Lead`, `ADMET`, `PK`, `Clinical`, `Multi` |
| `Model_Family` | String | `GNN`, `Transformer`, `CNN`, `RF`, `XGBoost`, `Ensemble`, `Other` |
| `Model_Name` | String | Specific model name if notable |
| `Dataset_Name` | String | Primary dataset used |
| `Dataset_Size` | String | N compounds/samples (e.g., `10K`, `1.2M`) |
| `Split_Method` | String | `Random`, `Scaffold`, `Temporal`, `Cluster`, `External` |
| `Primary_Metric` | String | Main evaluation metric (e.g., `AUROC`, `RMSE`, `MAE`) |
| `Primary_Value` | Float | Reported value for primary metric |
| `Secondary_Metric` | String | Optional secondary metric |
| `Secondary_Value` | Float | Optional secondary value |
| `Baseline_Comparison` | String | What baselines were compared |
| `Key_Finding` | String | 1-sentence summary of main result |
| `Limitations` | String | Author-stated or reviewer-identified limitations |
| `Evidence_Level` | Enum | `L0`, `L1`, `L2`, `L3` (see Evidence Ladder) |
| `Preprint_Status` | Enum | `Published`, `Preprint`, `Upgraded` |
| `PMID` | String | PubMed ID if available |
| `Notes` | String | Free-form reviewer notes |

### 2.3 Evidence Level Assignment

| Level | Definition | Typical Source |
|-------|------------|----------------|
| L0 | Anecdotal / no validation | Blog posts, white papers |
| L1 | In-silico only, single dataset | Most ML papers |
| L2 | Multi-dataset OR external validation | Cross-validation studies |
| L3 | Experimental wet-lab / clinical validation | Nature, Cell, clinical trials |

### 2.4 Example Row

```csv
S001,chen2024gnn,Chen,2024,GNN-ADMET: A Graph Neural...,In_Silico,ADMET_Prediction,Small_Molecule,ADMET,GNN,GNN-ADMET,ADMET-Benchmark,45K,Scaffold,AUROC,0.89,AUPRC,0.76,RF/XGBoost/DeepChem,GNN outperforms RF by 8% on scaffold split,Limited to public data only,L2,Published,38123456,Strong external validation
```

---

## 3. Benchmark Table (benchmark-table.csv)

### 3.1 When to Create Rows

Create a row for each **benchmark dataset** that:
- Is cited by 2+ papers in the review
- Is relevant to the review's scope (per `scope.yaml`)
- Has established leaderboards or standard splits

### 3.2 Column Definitions (17 columns)

| Column | Type | Description |
|--------|------|-------------|
| `Row_ID` | String | Unique ID: `B001`, `B002`, ... |
| `Benchmark_Name` | String | Canonical name (e.g., `MoleculeNet`, `TDC-ADMET`) |
| `Task_Category` | String | Task from taxonomy vocabulary |
| `Data_Modality` | String | `SMILES`, `Graph`, `3D`, `Sequence`, `Image`, `Multi` |
| `Size` | String | Number of samples/compounds |
| `Split_Available` | Boolean | `Y` or `N` - has standard train/val/test split |
| `Split_Type` | String | `Random`, `Scaffold`, `Temporal`, `Cluster` |
| `Primary_Metric` | String | Standard evaluation metric |
| `SOTA_Value` | Float | Current state-of-the-art value |
| `SOTA_Model` | String | Model achieving SOTA |
| `SOTA_Citation` | String | BibTeX key for SOTA paper |
| `SOTA_Year` | Integer | Year of SOTA result |
| `Source_URL` | String | Official benchmark URL |
| `Leaderboard_URL` | String | Public leaderboard if exists |
| `Selection_Rationale` | String | Why this benchmark was selected for the review |
| `R_and_D_Relevance` | String | Which R&D stages this benchmark addresses |
| `Notes` | String | Free-form notes |

### 3.3 Example Row

```csv
B001,MoleculeNet-BBBP,ADMET_Prediction,SMILES,2039,Y,Scaffold,AUROC,0.94,Uni-Mol,wang2023unimol,2023,https://moleculenet.org,https://paperswithcode.com/sota/...,Standard ADMET benchmark,ADMET,Most-cited BBB permeability dataset
```

---

## 4. Workflow Integration

### 4.1 Population Timing

1. **Gate 0**: Initialize empty tables with headers
2. **Phase 2 (Per-Issue Writing)**: Add rows as you review papers
3. **QA Phase**: Validate completeness and cross-reference

### 4.2 Linking to Issues CSV

In the Issues CSV, use `Evidence_RowIDs` column to link:
```
Evidence_RowIDs: S001;S002;B001
```

This creates traceability: Issue → Evidence rows → Citations.

### 4.3 Validation Checks

Run validation to ensure:
- All `Evidence_RowIDs` in Issues exist in tables
- All `Citation_Key` values exist in `ref.bib`
- Evidence levels are appropriately distributed (not all L1)

```bash
python3 scripts/evidence_ladder_validator.py <paper_dir>
```

---

## 5. Best Practices

1. **Be consistent with taxonomy**: Use exact terms from `taxonomy.yaml` for Task, Model_Family
2. **Don't over-extract**: Only include studies directly supporting review claims
3. **Note limitations honestly**: Capture both author-stated and reviewer-identified limitations
4. **Track preprints**: Mark preprint status and update when published versions appear
5. **Use Evidence Ladder**: Assign appropriate levels; avoid over-claiming

---

## 6. Quick Reference

### Study Table Minimum Required Fields
- Row_ID, Citation_Key, Year, Task, Model_Family, Primary_Metric, Primary_Value, Evidence_Level

### Benchmark Table Minimum Required Fields
- Row_ID, Benchmark_Name, Task_Category, Size, Primary_Metric, Selection_Rationale

### Common Mistakes to Avoid
- ❌ Citing a paper without adding to study table
- ❌ Using benchmarks not in benchmark table
- ❌ Claiming L3 evidence for in-silico-only studies
- ❌ Forgetting to update Preprint_Status when upgraded
