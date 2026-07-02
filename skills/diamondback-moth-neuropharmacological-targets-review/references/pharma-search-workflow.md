# Pharma Search Workflow

> **Version**: 2.4  
> **Purpose**: PubMed/Europe PMC/Crossref 文献搜索流程，补充 arXiv 搜索

---

## 概述

Pharma×AI 综述需要整合两个文献生态系统：
1. **AI/ML 文献** — arXiv, 计算机科学会议
2. **药学/生物医学文献** — PubMed, PMC, 药学期刊

本工作流定义如何系统性搜索生物医学文献。

---

## 搜索策略

### Step 1: 确定搜索范围

根据 `scope.yaml` 中定义的范围：
- 目标疾病/治疗领域
- 药物研发阶段 (Target → Hit → Lead → ADMET → Clinical)
- AI 技术类型
- 时间范围

### Step 2: 构建搜索查询

#### PubMed Query 构建

**基础模板**:
```
([AI Terms]) AND ([Pharma Terms]) AND ([Constraint Terms])
```

**AI Terms 示例**:
```
"machine learning"[Title/Abstract] OR
"deep learning"[Title/Abstract] OR
"neural network"[Title/Abstract] OR
"artificial intelligence"[Title/Abstract] OR
"graph neural network"[Title/Abstract] OR
"transformer"[Title/Abstract]
```

**Pharma Terms 示例 (按阶段)**:
```
# Target Identification
"target identification"[Title/Abstract] OR
"druggable genome"[Title/Abstract] OR
"disease gene"[Title/Abstract]

# Hit Discovery
"virtual screening"[Title/Abstract] OR
"molecular docking"[Title/Abstract] OR
"compound library"[Title/Abstract]

# Lead Optimization
"lead optimization"[Title/Abstract] OR
"structure-activity relationship"[Title/Abstract] OR
"SAR"[Title/Abstract]

# ADMET
"ADMET"[Title/Abstract] OR
"pharmacokinetics"[Title/Abstract] OR
"toxicity prediction"[Title/Abstract] OR
"drug metabolism"[Title/Abstract]

# Clinical Translation
"clinical trial"[Title/Abstract] OR
"drug repurposing"[Title/Abstract] OR
"biomarker"[Title/Abstract]
```

**时间约束**:
```
AND ("2020"[Date - Publication] : "2024"[Date - Publication])
```

### Step 3: 执行搜索

#### PubMed Search

```bash
# 使用 NCBI E-utilities (推荐)
# 或通过 Web: https://pubmed.ncbi.nlm.nih.gov/

# 记录搜索参数到 notes/search-log.md
```

#### Europe PMC Search

```bash
# API: https://www.ebi.ac.uk/europepmc/webservices/rest/search
# 优势：包含预印本链接、开放获取标记
```

#### Crossref Search

```bash
# API: https://api.crossref.org/works
# 优势：DOI 验证、引用计数
```

---

## 搜索日志 (PRISMA-S 对齐)

### search-log.md 模板

```markdown
# Literature Search Log

## Search Date: YYYY-MM-DD

## Database: PubMed

### Query 1: AI for Target Identification
- **Query String**: (machine learning OR deep learning) AND (target identification) AND 2020:2024[dp]
- **Results**: N papers
- **Screened**: M papers
- **Included**: K papers
- **Exclusion Reasons**: [language, non-relevant, duplicate]

### Query 2: AI for ADMET Prediction
- **Query String**: ...
- **Results**: ...

## Database: Europe PMC
...

## Database: arXiv
(link to arxiv-registry queries)

## PRISMA Flow Summary
- Total identified: XXX
- Duplicates removed: XX
- Screened: XXX
- Full-text assessed: XX
- Included: XX
```

---

## 结果整合

### 去重策略

1. **DOI 匹配** — 首选
2. **标题相似度** — DOI 不可用时
3. **作者 + 年份 + 期刊** — 补充验证

### 分类标签

为每篇文献分配：
- `Primary_Category` — 根据 taxonomy.yaml
- `AI_Technique_Tags` — ML 方法标签
- `Lifecycle_Stage` — 药物研发阶段
- `Evidence_Level` — L0/L1/L2/L3

### 添加到 Issues CSV

```csv
Issue_ID,Search_Keywords,PubMed_Query,PMC_Query,Required_Sources
R1,"GNN ADMET","(graph neural network) AND (ADMET)","same","PubMed>=5;arXiv>=10"
```

---

## 验证检查

### 来源覆盖检查

对于 Pharma×AI 综述，建议：
- **PubMed/PMC 来源**: ≥30% 的引用
- **arXiv 来源**: ≤40% 的引用
- **同行评审期刊**: ≥50% 的引用

### 时效性检查

- 最近 3 年文献: ≥70%
- 经典奠基性论文例外

---

## 工具集成

### 与 arxiv_registry.py 配合

```bash
# arXiv 搜索仍使用 arxiv_registry.py
python3 scripts/arxiv_registry.py --project-dir <paper_dir> search "GNN drug discovery"

# PubMed 搜索可使用独立脚本 (如果可用)
python3 scripts/pubmed_search.py --query "..." --output notes/pubmed-results.json
```

### 文献笔记整合

所有来源的文献笔记统一记录到 `notes/literature-notes.md`：

```markdown
## [DOI/arXiv ID]
- **Title**: ...
- **Source**: PubMed | arXiv | PMC
- **Evidence Level**: L0 | L1 | L2 | L3
- **Key Findings**: ...
- **Relevance to Section**: ...
```
