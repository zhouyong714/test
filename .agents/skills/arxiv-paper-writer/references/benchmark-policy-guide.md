# Benchmark Policy Guide for Pharma×AI Reviews

> **Version**: 2.4  
> **Purpose**: 定义基准测试发现、评估和报告的标准化流程

---

## 概述

药学×AI 综述必须系统性地整理和评估相关基准测试，帮助读者理解：
1. 现有方法在哪些任务上有可靠对比
2. 基准测试的局限性和适用范围
3. 从基准到实际药物研发的差距

---

## 基准发现流程 (AUTO Discovery)

### Step 1: 文献驱动发现

从核心论文中提取使用的数据集/基准：

```markdown
For each paper in literature notes:
  1. Extract dataset names from Methods section
  2. Extract benchmark names from Experiments section
  3. Record source URLs/DOIs
  4. Note reported metrics and splits
```

### Step 2: 仓库扫描

检查常用基准仓库：

| 领域 | 仓库 | URL |
|------|------|-----|
| 分子性质预测 | MoleculeNet | moleculenet.org |
| 药物-靶点 | TDC | tdcommons.ai |
| 蛋白质结构 | CASP, CAMEO | predictioncenter.org |
| 毒性预测 | Tox21, ToxCast | epa.gov/comptox |
| 药物相互作用 | DrugBank | drugbank.com |

### Step 3: Web 搜索补充

搜索新兴基准：
- "[task] benchmark dataset 2023 2024"
- "[domain] evaluation dataset machine learning"
- "new benchmark [specific method type]"

---

## 基准评估标准

### 质量维度

| 维度 | 评分 | 定义 |
|------|------|------|
| **Size** | S/M/L | <1K / 1K-100K / >100K samples |
| **Diversity** | Low/Med/High | Chemical/biological diversity |
| **Curation** | Auto/Semi/Manual | Data curation level |
| **Temporal** | Static/Updated | Update frequency |
| **Splits** | Random/Scaffold/Temporal | Split methodology |
| **Leakage Risk** | Low/Med/High | Train-test overlap risk |

### 药学相关性评估

| 问题 | 评分依据 |
|------|----------|
| 代表性 | 化合物是否代表真实药物化学空间? |
| 端点相关性 | 预测端点是否与药物研发决策相关? |
| 噪声水平 | 实验数据的噪声和变异性? |
| 适用阶段 | 适用于哪个研发阶段? |

---

## 基准目录表格格式

### dataset-benchmark-table.csv 模板

```csv
Benchmark_ID,Name,Domain,Task_Type,Size,Diversity,Curation,Split_Method,Metrics,Source_URL,DOI,Last_Updated,Leakage_Risk,Pharma_Relevance,Quality_Score,Notes
BM01,MoleculeNet-BBBP,ADMET,Classification,2039,Medium,Semi,Scaffold,AUC-ROC,moleculenet.org,10.xxx/xxx,2017,Medium,High,B,Blood-brain barrier permeability
BM02,TDC-hERG,Toxicity,Classification,6055,High,Manual,Scaffold,AUC-ROC,tdcommons.ai,10.xxx/xxx,2022,Low,High,A,Cardiac toxicity
```

### 列定义

| 列 | 类型 | 说明 |
|----|------|------|
| Benchmark_ID | String | 唯一标识符 (BM01, BM02, ...) |
| Name | String | 基准名称 |
| Domain | Enum | ADMET/Toxicity/Binding/Property/... |
| Task_Type | Enum | Classification/Regression/Generation/... |
| Size | Integer | 样本数量 |
| Diversity | Enum | Low/Medium/High |
| Curation | Enum | Auto/Semi/Manual |
| Split_Method | String | 数据划分方法 |
| Metrics | String | 常用评估指标 |
| Source_URL | URL | 数据来源 |
| DOI | String | 关联论文 DOI |
| Last_Updated | Date | 最后更新时间 |
| Leakage_Risk | Enum | Low/Medium/High |
| Pharma_Relevance | Enum | Low/Medium/High |
| Quality_Score | Enum | A/B/C/D |
| Notes | String | 备注 |

---

## 质量分级标准

### A 级 (Gold Standard)

- Manual curation
- Scaffold/temporal split
- Low leakage risk
- High pharma relevance
- Well-documented provenance

**示例**: Therapeutics Data Commons (TDC) curated benchmarks

### B 级 (Reliable)

- Semi-automated curation
- Scaffold split
- Medium leakage risk
- Medium-high pharma relevance

**示例**: MoleculeNet core benchmarks

### C 级 (Usable with Caution)

- Auto curation
- Random split or scaffold split
- Some concerns about data quality
- Document limitations

**示例**: Large-scale auto-extracted datasets

### D 级 (Not Recommended)

- Known data quality issues
- High leakage risk
- Low pharma relevance
- Use only if no alternatives

---

## 综述中的基准报告规范

### 报告必须包含

1. **基准选择理由**
   - 为什么选择这些基准
   - 覆盖了哪些任务/阶段
   - 有哪些已知局限

2. **评估设置标准化**
   - 使用的数据划分
   - 评估指标
   - 对比方法

3. **局限性讨论**
   - 基准与实际应用的差距
   - 数据偏差问题
   - 泛化性问题

### 禁止行为

❌ 不报告数据划分方法  
❌ 使用已知有泄露问题的基准而不说明  
❌ 混淆不同评估协议的结果  
❌ 声称 SOTA 而不指明基准和设置

---

## Issues CSV 集成

### Benchmark_IDs 列

在 Wx (Writing) issues 中标注使用的基准：

```csv
Issue_ID,Section_Target,Benchmark_IDs
W3,3.1-PropertyPrediction,BM01;BM02;BM05
W4,3.2-Toxicity,BM02;BM08;BM12
```

### Dataset_IDs 列

标注使用的数据集：

```csv
Issue_ID,Section_Target,Dataset_IDs
W3,3.1-PropertyPrediction,DS01;DS02
```

---

## 常用基准快速参考

### ADMET Prediction

| 基准 | 任务 | 推荐等级 |
|------|------|----------|
| TDC ADMET Benchmark | Multi-endpoint | A |
| MoleculeNet ADMET | Multi-endpoint | B |
| Tox21 | Toxicity | B |
| ToxCast | Toxicity | B |

### Molecular Property

| 基准 | 任务 | 推荐等级 |
|------|------|----------|
| MoleculeNet QM7/8/9 | Quantum properties | A |
| ESOL | Solubility | B |
| FreeSolv | Solvation | B |

### Drug-Target Interaction

| 基准 | 任务 | 推荐等级 |
|------|------|----------|
| TDC DTI | Binding prediction | A |
| DAVIS | Kinase binding | B |
| KIBA | Kinase binding | B |
| BindingDB | General binding | C |

### Generative Models

| 基准 | 任务 | 推荐等级 |
|------|------|----------|
| MOSES | Molecule generation | A |
| GuacaMol | Molecule generation | A |
| TDC Generation | Goal-directed gen | A |

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│                 BENCHMARK POLICY GUIDE                      │
├─────────────────────────────────────────────────────────────┤
│ DISCOVERY: Literature → Repositories → Web Search          │
├─────────────────────────────────────────────────────────────┤
│ EVALUATE:  Size, Diversity, Curation, Splits, Leakage     │
├─────────────────────────────────────────────────────────────┤
│ GRADE:     A (Gold) → B (Reliable) → C (Caution) → D (No) │
├─────────────────────────────────────────────────────────────┤
│ REPORT:    Selection rationale, setup, limitations         │
├─────────────────────────────────────────────────────────────┤
│ ⚠️  Always document splits and leakage risks              │
└─────────────────────────────────────────────────────────────┘
```
