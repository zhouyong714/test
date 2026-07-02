# Evidence Ladder for Pharma×AI Reviews

> **Version**: 2.4  
> **Purpose**: 定义证据层级体系，确保主张与证据强度匹配

---

## 证据层级定义

### L0: Consensus Evidence (共识级证据)

**定义**: 经过多次独立验证、被监管机构或系统综述认可的证据

**典型来源**:
- FDA/EMA 指南文件
- Cochrane 系统综述
- 多中心随机对照试验 (多个独立重复)
- 监管机构认可的验证标准
- 教科书/权威参考书

**允许的表述**:
- "is established as..."
- "regulatory guidance confirms..."
- "meta-analysis demonstrates..."
- "is the gold standard for..."

**Issues CSV**: `Evidence_Level=L0`

---

### L1: Strong Evidence (强证据)

**定义**: 前瞻性研究、随机试验、多站点验证

**典型来源**:
- Phase II/III 临床试验
- 多中心前瞻性验证研究
- 独立实验室重复验证
- 大规模基准测试 (多数据集、多方法对比)
- Nature/Science/Cell 等顶刊的实验验证

**允许的表述**:
- "has been validated in..."
- "prospective studies show..."
- "multi-center evaluation confirms..."
- "demonstrates consistent performance across..."

**Issues CSV**: `Evidence_Level=L1`

---

### L2: Moderate Evidence (中等证据)

**定义**: 同行评审的单站点研究、已建立的基准测试

**典型来源**:
- 同行评审期刊论文 (单站点研究)
- 已建立的公开数据集基准
- 会议全文论文 (NeurIPS, ICML, KDD 等)
- 回顾性验证研究
- 单一但高质量的实验验证

**允许的表述**:
- "shows..."
- "indicates..."
- "achieves ... on benchmark X..."
- "single-site validation demonstrates..."

**Issues CSV**: `Evidence_Level=L2`

---

### L3: Preliminary Evidence (初步证据)

**定义**: 预印本、小规模研究、未经广泛验证的方法

**典型来源**:
- arXiv/bioRxiv/medRxiv 预印本
- Workshop 论文
- 技术报告
- 小规模可行性研究
- 单一数据集/单一任务评估
- 博士论文 (未发表为期刊)

**允许的表述**:
- "preliminary evidence suggests..."
- "early work indicates..."
- "initial results show... [Preprint]"
- "may potentially..."
- "a recent preprint proposes..."

**Issues CSV**: `Evidence_Level=L3`

---

## 主张-证据匹配规则

### 规则矩阵

| 主张类型 | 允许的最低证据 | 示例 |
|----------|---------------|------|
| **安全性声明** | L0-L1 only | "Method X is safe for clinical deployment" |
| **临床效果声明** | L0-L1 only | "Improves patient outcomes" |
| **架构优越性** (关键主张) | L2+ | "GNN outperforms baseline by 15%" |
| **性能数据** (次要) | L2+ | "Achieves 0.85 AUC on dataset Y" |
| **方法论趋势** | L3 OK | "Emerging methods explore..." |
| **未来方向/假设** | L3 OK | "This approach may enable..." |

### 禁止组合

| 主张类型 | 证据层级 | 状态 |
|----------|----------|------|
| 安全性声明 | L3 (预印本) | ❌ 禁止 |
| 临床效果 | L3 (预印本) | ❌ 禁止 |
| 监管合规 | L2-L3 | ❌ 禁止 (必须 L0-L1) |
| 定量性能对比 (关键) | L3 only | ⚠️ 需要明确 hedging |

---

## 语言强度对照表

### L0 允许的断言式表达

```markdown
"X is established as the standard approach for..."
"Regulatory guidance from FDA/EMA confirms that..."
"Systematic reviews consistently show..."
"The consensus in the field is..."
```

### L1 允许的强表达

```markdown
"Prospective validation demonstrates..."
"Multi-center trials have confirmed..."
"Extensive benchmarking shows..."
"Independent replication validates..."
```

### L2 允许的中性表达

```markdown
"Studies show that..."
"Benchmark results indicate..."
"Published work demonstrates..."
"Peer-reviewed analysis suggests..."
```

### L3 必须的 Hedging 表达

```markdown
"Preliminary evidence suggests..."
"Early work indicates..."
"Initial results show [Preprint]..."
"May potentially offer..."
"Recent preprints propose..."
"Emerging approaches explore..."
```

---

## 药学领域特殊规则

### 药物安全性主张

**绝对禁止**使用低于 L1 的证据声称：
- 药物安全性
- 毒性预测准确性
- 临床可部署性
- 监管合规性

**示例 (错误)**:
> ❌ "This AI model accurately predicts cardiotoxicity (Smith, 2024 [Preprint])."

**示例 (正确)**:
> ✅ "Preliminary work explores cardiotoxicity prediction using AI, though prospective validation remains needed [Preprint] (Smith, 2024)."

### 基准性能主张

对于核心方法论主张：
- 必须有 L2+ 证据
- 必须指明具体基准和数据集
- 必须包含对比方法

**示例**:
> ✅ "On the ToxCast benchmark, Graph Transformer achieves 0.78 AUC-ROC, outperforming MPNN (0.72) and RF (0.68) (Chen et al., 2023, J. Chem. Inf. Model.)."

### 临床转化主张

任何关于"临床就绪"或"可部署"的声明：
- 必须有 L0-L1 证据
- 或明确标注为"研究阶段"

---

## Issues CSV 集成

### Evidence_Level 列

每个 Wx (Writing) issue 应标注主张类型和要求的证据层级：

```csv
Issue_ID,Section_Target,Claim_Type,Min_Evidence_Level,Evidence_RowIDs
W3,3.2-GNN,performance,L2,E12;E15;E18
W5,4.1-Safety,safety,L1,E22;E24
W7,5.1-Clinical,clinical,L1,E30;E31;E32
```

### 验证规则

```python
def validate_evidence(issue, evidence_table):
    for evidence_id in issue.evidence_row_ids:
        evidence = evidence_table[evidence_id]
        if issue.claim_type in ['safety', 'clinical']:
            assert evidence.level in ['L0', 'L1'], \
                f"Safety/clinical claims require L0-L1, got {evidence.level}"
        if issue.claim_type == 'performance' and issue.is_key_claim:
            assert evidence.level in ['L0', 'L1', 'L2'], \
                f"Key performance claims require L2+, got {evidence.level}"
```

---

## 证据升级路径

### 从 L3 升级到 L2

当预印本被接收为同行评审论文：
1. 更新 `ref.bib` 为正式版本
2. 移除 `[Preprint]` 标记
3. 更新 `Evidence_Level` 为 L2
4. 可以升级主张的语言强度

### 从 L2 升级到 L1

当有独立实验室重复验证：
1. 添加验证研究的引用
2. 更新 `Evidence_Level` 为 L1
3. 可以使用更强的断言式表达

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│                    EVIDENCE LADDER                          │
├─────────────────────────────────────────────────────────────┤
│ L0 CONSENSUS   FDA/EMA guidance, meta-analysis, textbooks   │
│                → "is established", "regulatory confirms"    │
├─────────────────────────────────────────────────────────────┤
│ L1 STRONG      Prospective trials, multi-site validation    │
│                → "has been validated", "demonstrates"       │
├─────────────────────────────────────────────────────────────┤
│ L2 MODERATE    Peer-reviewed single-site, benchmarks        │
│                → "shows", "indicates", "achieves"           │
├─────────────────────────────────────────────────────────────┤
│ L3 PRELIMINARY Preprints, workshops, small-scale            │
│                → "preliminary suggests", "may", "[Preprint]"│
├─────────────────────────────────────────────────────────────┤
│ ⚠️  SAFETY/CLINICAL CLAIMS: L0-L1 ONLY, NEVER PREPRINTS    │
└─────────────────────────────────────────────────────────────┘
```
