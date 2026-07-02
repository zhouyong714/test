# Pharma Task Dictionary

> **Version**: 2.4  
> **Purpose**: 为每种 Issue 类型定义标准化任务描述和验收标准

---

## 概述

Issues CSV 中的每个 Issue 都应有清晰的任务定义。本字典提供标准化的任务模板。

---

## Research Phase Issues (Rx)

### R1: Literature Discovery
**任务**: 执行系统性文献搜索
**输入**: topic, scope.yaml
**输出**: literature-notes.md, search-log.md
**验收标准**:
- [ ] PubMed 查询已执行并记录
- [ ] arXiv 搜索已缓存到 registry
- [ ] 识别 10-20 篇核心论文
- [ ] 来源覆盖: PubMed ≥30%, arXiv ≤40%

### R2: Framework Scaffolding
**任务**: 创建论文骨架和大纲
**输入**: literature notes, chosen template
**输出**: main.tex (headings + bullets only)
**验收标准**:
- [ ] 选择并应用 outline template
- [ ] Taxonomy section 在前 20%
- [ ] 每节 2-4 bullet points
- [ ] 种子引用已分配到章节

### R3: Benchmark Catalog
**任务**: 发现并整理相关基准测试
**输入**: literature notes, web search
**输出**: dataset-benchmark-table.csv
**验收标准**:
- [ ] 识别 ≥5 个相关基准
- [ ] 记录数据集来源、大小、任务
- [ ] 标注数据质量问题

### R4: Visualization Planning
**任务**: 规划论文可视化
**输入**: outline, visual-templates.md
**输出**: viz plan in plan.md
**验收标准**:
- [ ] ≥5 种可视化类型
- [ ] 每个可视化映射到章节
- [ ] 确认单/双栏需求

---

## Writing Phase Issues (Wx)

### W-Intro: Introduction Writing
**任务**: 撰写 Introduction
**特殊要求**: Playbook Rules 1-2 强制
**输出**: main.tex Introduction section
**验收标准**:
- [ ] has_context_pain_gap=Y
- [ ] has_scope_deliverables=Y
- [ ] Gap 句包含 However/Yet/Despite
- [ ] 3-6 bullet scope statement
- [ ] 8+ citations

### W-Taxonomy: Taxonomy Section
**任务**: 撰写分类框架章节
**特殊要求**: Playbook Rule 3 强制
**输出**: main.tex Taxonomy section
**验收标准**:
- [ ] has_taxonomy_map=Y
- [ ] 出现在论文前 20%
- [ ] 药学决策驱动组织
- [ ] 清晰的分类图/表

### W-Body-X: Body Section X
**任务**: 撰写技术章节
**特殊要求**: Playbook Rule 4 强制
**输出**: main.tex Section X
**验收标准**:
- [ ] has_section_loop=Y
- [ ] Mechanism 段落 (1¶)
- [ ] Representative Methods (2-4¶ with comparison)
- [ ] Failure Modes (≥1¶)
- [ ] Pharma Implications (1¶)
- [ ] 8+ citations
- [ ] L2+ evidence for key claims

### W-Conclusion: Conclusion Writing
**任务**: 撰写结论和路线图
**特殊要求**: Playbook Rule 5 强制
**输出**: main.tex Conclusion section
**验收标准**:
- [ ] has_actionable_roadmap=Y
- [ ] 短期 (6-18m) 里程碑
- [ ] 中期 (2-5y) 里程碑
- [ ] 回指 Introduction gap
- [ ] 四维度建议 (数据/基准/实验/转化)

---

## Figure/Table Issues (Fx/Tx)

### F-Taxonomy: Taxonomy Figure
**任务**: 创建分类框架可视化
**输出**: TikZ/SVG taxonomy diagram
**验收标准**:
- [ ] 清晰层次结构
- [ ] 颜色编码一致
- [ ] 适合单栏或双栏

### F-Pipeline: Pipeline Figure
**任务**: 创建方法流程图
**输出**: Pipeline diagram
**验收标准**:
- [ ] 输入 → 处理 → 输出清晰
- [ ] 关键步骤标注
- [ ] 与正文描述一致

### T-Study: Study Evidence Table
**任务**: 创建研究证据表
**输出**: study-table in main.tex
**验收标准**:
- [ ] 列: Method, Dataset, Metrics, Results, Level
- [ ] Evidence Level 标注
- [ ] 按 taxonomy 组织

### T-Benchmark: Benchmark Comparison Table
**任务**: 创建基准对比表
**输出**: benchmark table in main.tex
**验收标准**:
- [ ] 列: Dataset, Size, Task, Source, Quality
- [ ] 数据来源 URL/DOI
- [ ] 质量问题标注

---

## Refinement Phase Issues (RFx)

### RF1: Rhythm Refinement
**任务**: 应用 latex-rhythm-refiner 优化句式
**输入**: 完成的 main.tex
**输出**: 优化后的 main.tex
**验收标准**:
- [ ] 句子长度多样化
- [ ] 移除填充词
- [ ] 保留所有引用
- [ ] 段落节奏改善

### RF2: Citation Balance
**任务**: 平衡引用分布
**输入**: main.tex
**输出**: 平衡后的引用
**验收标准**:
- [ ] 每节 8+ citations
- [ ] 不超过 3 句无引用
- [ ] 时效性: 70%+ 近 3 年

---

## QA Phase Issues (Qx)

### Q1: Citation Verification
**任务**: 验证所有引用
**输入**: ref.bib
**输出**: 验证报告
**验收标准**:
- [ ] 100% citations verified
- [ ] BibTeX 格式正确
- [ ] 预印本标注完整

### Q2: Playbook Compliance
**任务**: Playbook 合规检查
**输入**: main.tex, issues.csv
**输出**: 合规报告
**验收标准**:
- [ ] 6 条硬约束全部通过
- [ ] 所有 has_* columns = Y
- [ ] 自检协议执行完成

### Q3: Evidence Compliance
**任务**: 证据层级合规检查
**输入**: main.tex, evidence mapping
**输出**: 证据报告
**验收标准**:
- [ ] 安全主张: L0-L1 only
- [ ] 关键主张: L2+
- [ ] 预印本正确标注

### Q4: Layout Hygiene
**任务**: 布局检查和修复
**输入**: main.log
**输出**: 修复后的 main.tex
**验收标准**:
- [ ] No Overfull \hbox warnings
- [ ] 图表尺寸合适
- [ ] 分页合理

### Q5: Compilation
**任务**: 最终编译
**输入**: main.tex, ref.bib
**输出**: main.pdf
**验收标准**:
- [ ] Exit code 0
- [ ] No "Citation undefined" warnings
- [ ] 6-10 pages main text

---

## Issue ID 命名规范

| 前缀 | 含义 | 示例 |
|------|------|------|
| R | Research | R1, R2, R3 |
| W | Writing | W1, W2, W-Intro |
| F | Figure | F1, F-Taxonomy |
| T | Table | T1, T-Study |
| RF | Refinement | RF1, RF2 |
| Q | QA | Q1, Q2 |

**插入规则**: 当 issue 膨胀时，使用子编号：W3a, W3b, Q2-fix
