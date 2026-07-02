# Preprint Policy for Pharma×AI Reviews

> **Version**: 2.4  
> **Purpose**: 定义预印本（bioRxiv, medRxiv, arXiv）在药学×AI综述中的引用规则

---

## 核心原则

1. **预印本不等于同行评审** — 始终优先使用已发表版本
2. **领域风险分级** — 临床/安全相关主张需要更高证据标准
3. **透明标注** — 读者必须能识别哪些引用来自预印本

---

## 预印本来源分类

### 允许来源 (Allowed)

| 来源 | arXiv 类别 | 使用场景 |
|------|-----------|----------|
| 机器学习方法 | cs.LG, cs.AI, stat.ML | 方法论、架构、算法 |
| 计算化学 | physics.chem-ph, cond-mat | 物理建模、量子化学 |
| 计算生物 | q-bio.BM, q-bio.QM | 结构预测、序列分析 |
| 生物医学预印 | bioRxiv, medRxiv | 实验数据（受限使用） |

### 禁止来源 (Forbidden)

| 来源 | 原因 |
|------|------|
| 专利申请 | 非科学证据，可用于背景但不能作为主张依据 |
| 会议摘要 (无全文) | 证据不足 |
| 个人通讯 | 无法验证 |
| 社交媒体/博客 | 非学术来源 |
| 新闻稿 | 可能存在选择性报道 |

---

## 预印本处理规则

### 规则 1: 优先使用同行评审版本

```
IF 预印本已有同行评审版本:
    → 使用同行评审版本，不引用预印本
    
IF 预印本无同行评审版本:
    → 检查发布时间，应用以下规则
```

### 规则 2: 时间敏感性

| 预印本年龄 | 处理方式 |
|-----------|----------|
| < 6 个月 | 可引用，标注 `[Preprint]`，设置 `Preprint_Status=unreviewed` |
| 6-12 个月 | 可引用，但需说明为何无同行评审版本 |
| > 12 个月 | 降级：不能支持关键主张，仅用于背景/趋势 |

### 规则 3: 主张类型限制

| 主张类型 | 允许的最低证据 | 预印本可用性 |
|----------|---------------|-------------|
| 关键架构优越性 | L2 (同行评审) | ❌ 不可作为唯一证据 |
| 安全性声明 | L1 (强证据) | ❌ 绝对禁止 |
| 临床效果声明 | L0-L1 | ❌ 绝对禁止 |
| 方法论趋势 | L3 (初步) | ✅ 可用，需 hedging |
| 新兴技术描述 | L3 (初步) | ✅ 可用，需标注 |

---

## 标注规范

### 文内标注

在正文中引用预印本时，必须包含 `[Preprint]` 标记：

✅ 正确:
> "Recent work proposes a novel attention mechanism for protein-ligand binding [Preprint] (Smith et al., 2024)."

❌ 错误:
> "This method has been validated for clinical use (Smith et al., 2024)."  
> [如果引用的是预印本]

### BibTeX 标注

在 `ref.bib` 中，预印本条目必须：
1. 使用 `@unpublished` 或 `@misc` 类型
2. 在 `note` 字段标注预印本状态

```bibtex
@misc{smith2024novel,
  author = {Smith, John and Doe, Jane},
  title = {A Novel Approach to Drug-Target Interaction},
  year = {2024},
  eprint = {2024.01.12345},
  archiveprefix = {bioRxiv},
  note = {Preprint, not peer-reviewed}
}
```

### Issues CSV 标注

| 列名 | 值 | 含义 |
|------|-----|------|
| `Preprint_Status` | `peer-reviewed` | 已有同行评审版本 |
| `Preprint_Status` | `unreviewed` | 纯预印本 |
| `Preprint_Status` | `NA` | 非预印本来源 |

---

## Hedging 语言指南

### L3 证据的 Hedging 模板

| 场景 | Hedging 表达 |
|------|-------------|
| 方法初步结果 | "Preliminary evidence suggests..." |
| 未经广泛验证 | "Early work indicates..." |
| 单一研究 | "In one study, ... [Preprint]" |
| 理论预测 | "Theoretical analysis predicts..." |
| 新兴趋势 | "Emerging approaches propose..." |

### 禁止表达 (与预印本搭配)

❌ "This has been established by..."  
❌ "Validated results show..."  
❌ "Conclusive evidence demonstrates..."  
❌ "Clinical trials confirm..."

---

## 特殊场景处理

### 场景 1: 里程碑预印本

某些预印本在领域内影响力极大（如 AlphaFold 论文）：
- 可以引用，但仍需标注 `[Preprint]`
- 尽快更新为同行评审版本
- 如果超过 6 个月仍无正式版，说明原因

### 场景 2: 快速演进领域

对于快速演进的领域（如 LLM for drug discovery）：
- 可以引用近期预印本作为趋势指标
- 必须包含 hedging 语言
- 建议设置 `Preprint_Warning` 提醒未来更新

### 场景 3: 预印本冲突

当预印本与同行评审文献结论冲突：
- 优先采信同行评审版本
- 可以提及预印本作为"争议观点"
- 不能用预印本推翻已有共识

---

## 验证检查清单

### Issues CSV 验证

```python
# 验证脚本应检查：
for issue in issues:
    if issue.has_preprint_citations:
        assert issue.preprint_status in ['unreviewed', 'peer-reviewed']
        assert issue.claim_type != 'safety'  # 安全主张不能用预印本
        assert issue.claim_type != 'clinical'  # 临床主张不能用预印本
```

### 文本验证

1. 计算 bioRxiv/medRxiv/arXiv 引用数量
2. 计算 `[Preprint]` 标记数量
3. 确保 标记数量 ≥ 预印本引用数量

### QA Gate 检查

| 检查项 | 通过标准 |
|--------|----------|
| 预印本标注完整性 | 100% 预印本有 `[Preprint]` 标记 |
| 安全主张预印本 | 0 个安全主张仅由预印本支持 |
| 临床主张预印本 | 0 个临床主张仅由预印本支持 |
| Hedging 语言 | 所有 L3 预印本有适当 hedging |

---

## Quick Reference

```
┌────────────────────────────────────────────────────────────┐
│                   PREPRINT POLICY                          │
├────────────────────────────────────────────────────────────┤
│ ✅ ALLOWED                                                 │
│    cs.LG, stat.ML, q-bio.BM, bioRxiv (with restrictions)  │
├────────────────────────────────────────────────────────────┤
│ ❌ FORBIDDEN                                               │
│    Patents, abstracts-only, personal comms, social media  │
├────────────────────────────────────────────────────────────┤
│ 📋 RULES                                                   │
│    1. Prefer peer-reviewed version if exists              │
│    2. Mark all preprints with [Preprint]                  │
│    3. No preprints for safety/clinical claims             │
│    4. Hedge language for L3 evidence                      │
│    5. Downgrade >12 month old unreviewed preprints        │
└────────────────────────────────────────────────────────────┘
```
