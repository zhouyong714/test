# Review Writing Playbook (综述写作方法论)

> **Version**: 2.4  
> **Last Updated**: 2025-01-01  
> **Purpose**: 定义 6 条写作硬约束，确保每篇综述执行可复现的"叙事—论证—落地动作链"

---

## 核心理念

高质量药学×AI综述不是罗列文献，而是：
1. **叙事驱动** — 从领域痛点出发，不是从技术出发
2. **论证闭环** — 每个技术讨论都回答"对药学家意味着什么"
3. **可执行性** — 读者读完知道下一步该做什么

本 Playbook 定义 6 条**硬约束**，必须在 Issues CSV 中验证通过。

---

## 硬约束 1: Opening Three-Part Structure (开场三段式)

### 规则
Introduction 第一段**必须**包含：
1. **Context/Trend (Why now)** — 领域必要性与紧迫性
2. **Pain Point (What hurts)** — 从领域视角的核心问题
3. **Gap Statement (Gap句)** — 包含 `However|Yet|Despite` + 明确的知识缺口

### Gap 句示例

**药物发现领域**:
> "Despite the rapid adoption of graph neural networks for molecular property prediction, 
> **no systematic review has examined their failure modes on multi-target drugs** 
> where polypharmacology is intentional rather than accidental."

**ADMET 预测领域**:
> "Yet current ADMET prediction benchmarks **remain dominated by single-endpoint datasets**, 
> overlooking the cascading dependencies between absorption, distribution, and clearance 
> that define real-world drug disposition."

**临床翻译领域**:
> "However, **the gap between retrospective validation and prospective clinical deployment** 
> remains poorly characterized, with most AI-driven tools stalling at the proof-of-concept stage."

### 验证
- Issues CSV: `has_context_pain_gap=Y`
- 自检: grep Introduction 段落，确认包含 However/Yet/Despite + 明确缺口描述

---

## 硬约束 2: Scope & Deliverables (范围与交付物)

### 规则
Introduction **必须**包含 3-6 条 bullet 明确说明：
- 覆盖的任务范围 (which AI tasks)
- 覆盖的对象范围 (which modalities/molecules)
- 覆盖的证据层级 (which R&D stages)
- 交付物清单 (taxonomy, tables, roadmap)

### 示例

> This review provides:
> - A **taxonomy of 47 deep learning architectures** for molecular property prediction, organized by inductive bias
> - **Comparative benchmarks** across 12 public datasets spanning ADMET endpoints
> - **Evidence tables** linking each method to validated clinical use cases (N=23 FDA/EMA references)
> - An **actionable 18-month roadmap** for integrating GNN-based ADMET into early discovery pipelines

### 禁止写法
❌ "We review recent progress in AI for drug discovery."  
❌ "This paper surveys machine learning methods for molecules."  
❌ 无具体数字、无交付物列表的泛泛陈述

### 验证
- Issues CSV: `has_scope_deliverables=Y`
- 自检: 确认 Introduction 有 bullet list，每条有具体数字或明确边界

---

## 硬约束 3: Taxonomy-First (分类框架在前)

### 规则
- 分类框架/Taxonomy **必须**出现在论文正文的前 10-20% 位置
- 后续所有章节**必须**映射回 Taxonomy
- 优先采用"药学决策驱动"组织方式，而非"AI技术驱动"

### 组织方式对比

**推荐 (Pharma-Decision-Driven)**:
```
2. Taxonomy of AI in Drug R&D
   2.1 Target Identification & Validation
   2.2 Hit Discovery & Virtual Screening  
   2.3 Lead Optimization & ADMET
   2.4 Preclinical Safety & Toxicology
   2.5 Clinical Translation & Biomarkers
```

**避免 (AI-Tech-Driven)**:
```
2. Deep Learning Methods
   2.1 Convolutional Neural Networks
   2.2 Recurrent Neural Networks
   2.3 Graph Neural Networks
   2.4 Transformers
```

### 验证
- Issues CSV: `has_taxonomy_map=Y`
- 自检: Taxonomy 章节在 Section 2 或更早；后续章节标题可追溯到 Taxonomy 分支

---

## 硬约束 4: Section Narrative Loop (每节叙述循环)

### 规则
每个技术章节**必须**包含 4 个要素（顺序可调整）：

| 要素 | 内容 | 典型篇幅 |
|------|------|----------|
| **Mechanism** | Why it works (归纳偏置、数学原理) | 1 段 |
| **Representative Methods** | 代表性方法对比（不是罗列） | 2-4 段 |
| **Failure Modes** | 何时/为何失效，边界条件 | ≥1 段 |
| **Pharma Implications** | 药学从业者如何使用 | 1 段 |

### 示例结构

```markdown
### 3.2 Graph Neural Networks for Molecular Property Prediction

**Mechanism.** GNNs exploit the natural graph structure of molecules...
[1 paragraph on message passing, permutation invariance]

**Representative Methods.** We compare three dominant architectures:
MPNN (Gilmer et al., 2017), AttentiveFP (Xiong et al., 2020), and
SchNet (Schütt et al., 2018)... [2-3 paragraphs with table]

**Failure Modes.** GNNs underperform on:
(1) Molecules with rare substructures absent from training data...
(2) Properties dominated by global rather than local features...
[1-2 paragraphs]

**Implications for Drug Discovery.** For hit-to-lead optimization,
practitioners should... [1 paragraph with actionable guidance]
```

### 验证
- Issues CSV: `has_section_loop=Y` (per Wx issue)
- 自检: 每个 Section 3.x/4.x 有上述 4 要素的段落标记或隐含结构

---

## 硬约束 5: Actionable Roadmap (行动化路线图)

### 规则
Conclusion **必须**包含：
- **短期 (6-18 月)** + **中期 (2-5 年)** 里程碑
- 回指 Introduction 的 Gap 声明
- 四个维度的建议：数据、基准、实验闭环、转化路径

### 禁止写法
❌ "Future work should address the limitations mentioned above."  
❌ "More research is needed in this area."  
❌ 无时间线、无具体行动的泛泛展望

### 示例

> **Short-term (6-18 months):**
> - Release multi-endpoint ADMET benchmark with cascading dependencies (Data)
> - Establish standardized GNN evaluation protocol for polypharmacology (Benchmark)
> - Pilot prospective validation in 2-3 pharma partners (Experimental Loop)
>
> **Medium-term (2-5 years):**
> - Integrate uncertainty quantification into FDA submission packages (Translational)
> - Develop interpretable GNN variants meeting regulatory explainability bar (Benchmark)
>
> These milestones directly address the gap identified in Section 1: the lack of 
> systematic evaluation of GNN failure modes in multi-target drug contexts.

### 验证
- Issues CSV: `has_actionable_roadmap=Y`
- 自检: Conclusion 有时间线表格或分段，回指 Introduction gap

---

## 硬约束 6: Evidence Binding (证据绑定)

### 规则
1. **所有定量声明**必须有引用
2. **不确定性表达**使用：`preliminary|suggests|may|early evidence indicates`
3. **预印本**必须标注 `[Preprint]`，不能作为关键声明的唯一证据

### 定量声明示例

✅ "GNNs achieve 0.78 AUC-ROC on hERG inhibition prediction (Xiong et al., 2020)."  
❌ "GNNs achieve good performance on hERG prediction."

### 不确定性措辞

| 证据层级 | 允许措辞 |
|----------|----------|
| L0-L1 (Strong) | "demonstrates", "establishes", "confirms" |
| L2 (Moderate) | "shows", "indicates", "suggests" |
| L3 (Preliminary) | "preliminary evidence suggests", "early work indicates", "may" |

### 预印本标注

✅ "Recent work proposes... [Preprint] (Smith et al., 2024, bioRxiv)."  
❌ "This method has been validated... (Smith et al., 2024)." [if preprint]

### 验证
- Issues CSV: 通过 `Preprint_Status` 列和 `Evidence_Level` 列追踪
- 自检: grep `[Preprint]` 标注数量 ≥ 预印本引用数量

---

## 自检协议 (Self-Check Protocol)

### Phase 3 QA Gate 必须执行以下检查：

| Checkpoint | 方法 | 通过标准 |
|------------|------|----------|
| Gap 句检查 | grep Introduction for However/Yet/Despite | 找到 ≥1 个 Gap 句 |
| Scope Bullet 检查 | 人工确认 Introduction bullet list | 3-6 bullets with specifics |
| Taxonomy 位置 | 计算 Taxonomy 结束位置 / 总正文长度 | ≤ 20% |
| Section Loop 抽查 | 随机抽 2 个技术章节 | 4 要素齐全 |
| Roadmap 时间线 | grep Conclusion for month/year | 有 6-18m 和 2-5y 提及 |
| Preprint 标注 | grep `[Preprint]` | 数量 ≥ bioRxiv/medRxiv 引用数 |

### 验证失败处理

如果任何检查失败：
1. 在 Issues CSV 中插入 `Qx` 修复任务
2. 明确指出违反的硬约束编号
3. 修复后重新验证

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                 REVIEW WRITING PLAYBOOK                     │
├─────────────────────────────────────────────────────────────┤
│ 1. OPENING      Context → Pain → Gap句 (However/Yet/Despite)│
│ 2. SCOPE        3-6 bullets with deliverables               │
│ 3. TAXONOMY     First 10-20% of body, pharma-decision-driven│
│ 4. SECTION LOOP Mechanism → Methods → Failures → Implications│
│ 5. ROADMAP      6-18m + 2-5y milestones, ref back to Gap    │
│ 6. EVIDENCE     Cite all quant claims, hedge L3, mark preprints│
└─────────────────────────────────────────────────────────────┘
```
