# Issues CSV Schema Migration Guide

> Migration guide for upgrading from v1 → v2.3 → v2.4 Issues CSV schema.

---

## Schema Version History

| Version | Date | Columns | Key Changes |
|---------|------|---------|-------------|
| v1 | 2024-01 | 15 | Original: basic issue tracking |
| v2.3 | 2025-06 | 55 | Pharma mode: evidence, preprint, PRISMA |
| v2.4 | 2025-12 | 64 | Playbook gates, benchmark rationale |

---

## Quick Reference: Column Additions

### v1 → v2.3 (+40 columns)

```
# New prefix columns (10)
Schema_Version, Review_Mode, R_and_D_Stage, Task_Category, Model_Family,
Target_Modality, Preprint_Check_Date, Evidence_RowIDs, Benchmark_RowIDs, PRISMA_Stage

# New evidence columns (8)
Evidence_Level_Min, Evidence_Level_Actual, Preprint_Count, Published_Count,
Preprint_Upgraded_Count, Study_Count, Benchmark_Count, Limitation_Count

# New taxonomy columns (6)
Task_Vocabulary, Method_Vocabulary, Stage_Vocabulary, Persona_Primary,
Persona_Secondary, DMTA_Relevant

# New quality columns (8)
Has_Mechanism_Para, Has_Failure_Mode, Has_Pharma_Implication, Has_Figure,
Has_Table, Citation_Density, Cross_Ref_Issues, Internal_Links

# New metadata columns (8)
Last_Updated, Updated_By, Review_Comments, Blocked_By, Blocks,
Related_Issues, Sprint, Priority
```

### v2.3 → v2.4 (+9 columns)

```
# Playbook gate columns (6)
has_context_pain_gap, has_scope_deliverables, has_taxonomy_map,
has_section_loop, has_actionable_roadmap, has_evidence_binding

# Benchmark columns (2)
Benchmark_Selection_Rationale, Benchmark_Pools_Used

# Control column (1)
Playbook_Gate_Status
```

---

## Migration Procedure

### Option A: Script-Assisted Migration

```bash
# From paper directory
python3 scripts/validate_paper_issues.py <old_issues.csv> --migrate --target-version v2.4
```

This will:
1. Parse existing CSV
2. Add new columns with default values
3. Preserve all existing data
4. Output to `<old_issues>_v2.4.csv`

### Option B: Manual Migration

1. **Backup** your existing Issues CSV
2. **Download** latest template from `assets/paper-issues-template.v2.4.csv`
3. **Copy** existing data to new template
4. **Fill** new columns with defaults (see below)

---

## Default Values for New Columns

### v2.3 Pharma Columns

| Column | Default | Notes |
|--------|---------|-------|
| Schema_Version | "2.3" | Update to "2.4" if using v2.4 |
| Review_Mode | "Standard" | or "Pharma" for Pharma×AI reviews |
| R_and_D_Stage | "" | Fill based on content |
| Task_Category | "" | From taxonomy.yaml |
| Evidence_RowIDs | "" | Links to study-table.csv |
| Evidence_Level_Min | "L1" | Minimum required |
| Preprint_Count | 0 | Count from citations |
| Has_Mechanism_Para | "N" | Check section content |
| Has_Failure_Mode | "N" | Check section content |

### v2.4 Playbook Columns

| Column | Default | Notes |
|--------|---------|-------|
| has_context_pain_gap | "N" | Check Introduction |
| has_scope_deliverables | "N" | Check Introduction |
| has_taxonomy_map | "N" | Check §3 |
| has_section_loop | "N" | Check each technical section |
| has_actionable_roadmap | "N" | Check Conclusion |
| has_evidence_binding | "N" | Check citations |
| Benchmark_Selection_Rationale | "" | P1-P5 reference |
| Playbook_Gate_Status | "pending" | pending/passed/failed |

---

## Validation After Migration

```bash
# Validate schema structure
python3 scripts/validate_paper_issues.py <migrated.csv> --pharma

# Check playbook gates
python3 scripts/playbook_gate_checker.py <paper_dir>

# Check evidence ladder
python3 scripts/evidence_ladder_validator.py <paper_dir>
```

---

## Column Mappings

### v1 Column → v2.4 Equivalent

| v1 Column | v2.4 Column | Notes |
|-----------|-------------|-------|
| ID | Issue_ID | Renamed |
| Type | Issue_Type | Unchanged |
| Section | Section_Num | Renamed |
| Status | Status | Unchanged |
| Title | Issue_Title | Renamed |
| Description | Description | Unchanged |
| Citations | Verified_Citations | Enhanced |
| - | Evidence_RowIDs | NEW |
| - | Playbook_Gate_Status | NEW |

---

## Backward Compatibility

The `validate_paper_issues.py` script supports:
- Reading any version (v1, v2.3, v2.4)
- Writing to specified target version
- Graceful handling of missing columns

**Note**: Some v2.4 features (playbook gates, evidence ladder) won't work with v1 CSVs until migrated.

---

## Common Migration Issues

### Issue 1: Missing Header
**Symptom**: "Column X not found"
**Fix**: Ensure first row contains all column headers

### Issue 2: Encoding Problems
**Symptom**: Garbled characters
**Fix**: Save as UTF-8 with BOM

### Issue 3: Delimiter Confusion
**Symptom**: Columns merged incorrectly
**Fix**: Ensure comma delimiter, quote strings containing commas

### Issue 4: Row Count Mismatch
**Symptom**: Some rows missing columns
**Fix**: Check for newlines within cells, proper quoting

---

## Rollback Procedure

If migration fails:
1. Restore from backup
2. Report issue with error message
3. Try manual column-by-column addition

---

## Schema Reference

See full column specifications:
- `assets/paper-issues-template.v2.4.csv` - Latest template
- `references/quality-report.md` - Column validation rules
- `SKILL.md` - Issues CSV section
