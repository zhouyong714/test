---
name: insect-neuropharmacology-review
description: >
  撰写昆虫神经药理学综述论文，专注于害虫神经系统药理靶标研究。
  使用 IEEEtran 或 Elsevier 模板，支持中英文双语写作，整合 PubMed、Web of Science、
  中国知网等多源文献，遵循农药学和昆虫学领域规范。
compatibility: >
  Python 3.8+。LaTeX 编译环境（pdflatex + bibtex 或 xelatex 支持中文）。
  文献检索：PubMed/Europe PMC、Web of Science、中国知网、万方数据。
metadata:
  short-description: 昆虫神经药理学综述（支持中英文，多源文献整合）
  schema-version: "1.0"
  language: zh-CN, en-US
---

# 昆虫神经药理学综述写作工作流

## 适用场景

- 害虫神经系统药理靶标综述（如小菜蛾、蚜虫、飞虱等）
- 杀虫剂作用机制与抗性机制综述
- 昆虫神经递质系统与农药靶标研究
- 中英文双语学术论文（支持中文期刊和国际期刊）
- LaTeX + BibTeX 工作流，支持多源文献验证

## 不适用场景

- 原创实验研究论文（本工作流专注于综述）
- 非学术文档
- 临床医学综述（需要不同的证据标准）

## 核心特性

### 1. 多源文献整合
- **国际数据库**：PubMed/Europe PMC、Web of Science、Scopus
- **中文数据库**：中国知网（CNKI）、万方数据、维普
- **专业数据库**：CAB Abstracts（农业生物学）、AGRIS（农业科学）
- **灰色文献**：农药登记资料、FAO/WHO 报告、IRAC 分类

### 2. 领域特定框架
- **靶标分类体系**：
  - 神经递质受体（nAChR、GABA、Glu 等）
  - 离子通道（钠通道、钙通道、氯通道）
  - 酶系统（AChE、GABA 转氨酶、线粒体复合体）
  - 其他靶标（保幼激素、蜕皮激素、几丁质合成）
- **抗性机制分类**：
  - 靶标抗性（突变、表达量变化）
  - 代谢抗性（P450、GST、CarE）
  - 穿透抗性与行为抗性

### 3. 证据分级系统（农药学适配）
| 等级 | 名称 | 定义 | 典型来源 |
|------|------|------|----------|
| L0 | 权威共识 | 国际组织指南、系统综述 | WHO/FAO、IRAC、Cochrane |
| L1 | 强证据 | 多点田间试验、分子验证 | 多地区抗性监测、基因功能验证 |
| L2 | 中等证据 | 单点研究、体外实验 | 同行评审期刊、受体结合研究 |
| L3 | 初步证据 | 预印本、会议论文 | bioRxiv、学术会议摘要 |

### 4. 双语支持
- **中文期刊**：使用 xelatex + ctex 宏包
- **国际期刊**：使用 pdflatex + IEEEtran/Elsevier 模板
- **文献管理**：支持中英文混排 BibTeX

## 输入

- 主题描述（必需）：如"小菜蛾神经系统药理靶标"
- 目标害虫物种（必需）：学名和俗名
- 约束条件：目标期刊、页数限制、作者信息（可选）
- 语言选择：中文/英文/双语（可选，默认中文）
- 现有项目路径（可选，用于文献验证）

## 输出

- `main.tex`（LaTeX 源文件）
- `ref.bib`（验证过的 BibTeX 条目）
- 模板文件（IEEEtran.cls 或 elsarticle.cls）
- `plan/<timestamp>-<slug>.md`（计划文档）
- `issues/<timestamp>-<slug>.csv`（任务追踪表）
- `main.pdf`（编译后的 PDF）
- `notes/literature-notes.md`（文献笔记，可选）
- `notes/target-classification.yaml`（靶标分类体系）
- `notes/resistance-mechanisms.yaml`（抗性机制分类）
- `notes/search-log.md`（文献检索日志）
- `notes/evidence-table.csv`（证据提取表）

**约定**：从本 skill 文件夹运行 `python3 scripts/...`；`<paper_dir>` 是论文项目根目录（包含 `main.tex`、`ref.bib`、`plan/`、`issues/`、`notes/`）。

---

## 综述写作规范（硬约束）

### 规则 1：引言三段式结构
引言**必须**包含：
1. **背景与趋势**：害虫危害现状、防治需求、研究热点
2. **核心问题**：当前防治面临的挑战（抗性、环境问题、选择性）
3. **研究空缺**：必须包含 `然而|但是|尽管` + 明确的知识空缺

**验证**：Issues CSV 中 `has_context_pain_gap=Y`

### 规则 2：范围与交付物声明
引言**必须**包含 3-6 条明确的范围声明：
- 覆盖的靶标类型（哪些神经系统靶标）
- 研究对象范围（哪些害虫物种）
- 证据层级范围（实验室/田间/分子）
- 交付物列表（分类体系、证据表、研发路线图）

**禁止**："本文综述了近年来的研究进展"（无具体内容）
**验证**：Issues CSV 中 `has_scope_deliverables=Y`

### 规则 3：分类体系优先
- 靶标分类体系**必须**出现在正文前 10-20%
- 后续所有章节**必须**映射回分类体系
- 优先使用"靶标-杀虫剂-抗性"组织逻辑，而非单纯技术分类

**验证**：Issues CSV 中 `has_taxonomy_map=Y`

### 规则 4：章节叙事循环
每个技术章节**必须**包含：
1. **作用机制**（1 段）：为什么有效（分子机制、结构基础）
2. **代表性杀虫剂**（2-4 段）：对比分析，非简单罗列
3. **抗性机制**（≥1 段）：何时/为何失效，边界条件
4. **应用启示**（1 段）：对抗性治理和新药研发的意义

**验证**：Issues CSV 中 `has_section_loop=Y`

### 规则 5：可操作的研发路线图
结论**必须**包含：
- 短期目标（1-3 年）+ 中期目标（3-5 年）
- 回应引言中的知识空缺
- 维度：靶标发现、抗性监测、绿色农药、综合防治

**禁止**："未来应加强研究"（无具体内容）
**验证**：Issues CSV 中 `has_actionable_roadmap=Y`

### 规则 6：证据绑定
- 所有定量声明**必须**有引用
- 不确定性使用：`初步|提示|可能|早期证据`
- 预印本**必须**标注 `[预印本]` 或 `[Preprint]`，不能作为关键论断的唯一证据

---

## 门控工作流

### 门控 0：研究快照 + 草案计划
1. 确认约束条件（期刊、页数、作者、截止日期）
2. 确认目标害虫物种（学名、俗名、分类地位）
3. 确认语言（中文/英文/双语）
4. 翻译主题为检索关键词，进行初步文献发现（15-25 篇核心文献）：
   - 国际数据库：PubMed、Web of Science
   - 中文数据库：知网、万方
   - 专业数据库：CAB Abstracts
5. 提出 2-4 个候选标题
6. 搭建项目文件夹并生成草案计划：
   ```bash
   python3 scripts/bootstrap_insect_review.py --stage kickoff --topic "小菜蛾神经系统药理靶标" --species "Plutella xylostella" --language zh
   ```
7. 在 `main.tex` 中创建**框架骨架**（章节标题 + 每节 2-4 条要点 + 种子引用；**无正文**）
8. 更新计划文件，反映框架、候选标题、章节规划
9. 早期编译：`python3 scripts/compile_paper.py --project-dir <paper_dir>`
10. 返回给用户：
    - 提议的大纲（5-8 节，每节 2-4 条要点）
    - 计划的可视化（3-5 个图表）
    - 澄清问题
11. **停止**，等待用户批准

### 门控 1：创建 Issues CSV（批准后）
1. 检查计划中的启动门控：`- [x] 用户已在对话中确认范围和大纲`
2. 创建 issues CSV（如果门控未勾选，脚本会拒绝）：
   ```bash
   python3 scripts/bootstrap_insect_review.py --stage issues --topic "小菜蛾神经系统药理靶标" --with-literature-notes
   ```
3. 验证：
   ```bash
   python3 scripts/validate_paper_issues.py <paper_dir>/issues/<timestamp>-<slug>.csv
   ```
4. 如果启用文献笔记，保持简短摘要以避免重复检索
5. 计划可能演变；根据需要添加/拆分/插入 issues，重新验证后继续，直到所有 issues 为 `DONE` 或 `SKIP`

### 阶段 2：按 Issue 写作循环
对于 CSV 中的每个写作 issue：
1. **研究**：8-15 篇章节特定文献（国际 + 中文）
2. **写作**：每 3 句必有引用；段落长度变化
3. **可视化**：匹配内容触发器（见 `references/visual-templates.md`）
4. **验证**：网络搜索 + 打开源页面（及 PDF）后再添加到 `ref.bib`
5. **更新**：标记 issue 为 `DONE`，填写 `Verified_Citations` 计数
6. 有意义的更改后编译；标记 `DONE` 前修复 `Overfull \hbox`

### 阶段 2.5：节奏优化
所有写作 issues 完成后，使用 `latex-rhythm-refiner` skill 逐节优化文本。

### 阶段 3：QA 门控
1. 运行内部 QA 检查清单
2. 编译；确保 `main.log` 中无 `Overfull \hbox` 警告
3. 验证所有 playbook 门控在 issues CSV 中已满足
4. 交付 `main.tex`、`ref.bib`、图表和 `main.pdf`

---

## 文献检索策略

### 国际数据库检索
**PubMed/Europe PMC**：
```
("Plutella xylostella"[Title/Abstract] OR "diamondback moth"[Title/Abstract])
AND ("insecticide resistance"[MeSH] OR "target site"[Title/Abstract] OR "neurotransmitter"[Title/Abstract])
AND ("2019/01/01"[PDAT] : "2026/12/31"[PDAT])
```

**Web of Science**：
```
TS=("Plutella xylostella" OR "diamondback moth") 
AND TS=("insecticide resistance" OR "target site" OR "acetylcholinesterase" OR "GABA receptor")
AND PY=(2019-2026)
```

### 中文数据库检索
**中国知网（CNKI）**：
```
主题="小菜蛾" AND (主题="抗药性" OR 主题="靶标" OR 主题="神经系统")
时间范围：2019-2026
```

**万方数据**：
```
题名或关键词:(小菜蛾) AND 题名或关键词:(抗性 OR 靶标 OR 乙酰胆碱酯酶)
年份:2019-2026
```

### 专业数据库
**CAB Abstracts**（农业生物学权威库）：
```
(Plutella xylostella OR diamondback moth) AND (insecticide resistance OR target site)
```

---

## 靶标分类体系（示例）

```yaml
# notes/target-classification.yaml
classification:
  - category: 神经递质受体
    targets:
      - name: 烟碱型乙酰胆碱受体 (nAChR)
        insecticides: [新烟碱类, 鱼尼丁受体类]
        irac_group: [4A, 4B, 4C, 4D]
      - name: GABA 受体
        insecticides: [环戊二烯类, 苯基吡唑类]
        irac_group: [2A, 2B]
      - name: 谷氨酸门控氯通道 (GluCl)
        insecticides: [阿维菌素类]
        irac_group: [6]
  
  - category: 离子通道
    targets:
      - name: 电压门控钠通道 (VGSC)
        insecticides: [拟除虫菊酯类, DDT]
        irac_group: [3A]
      - name: 鱼尼丁受体 (RyR)
        insecticides: [邻甲酰氨基苯甲酰胺类]
        irac_group: [28]
  
  - category: 酶系统
    targets:
      - name: 乙酰胆碱酯酶 (AChE)
        insecticides: [有机磷类, 氨基甲酸酯类]
        irac_group: [1A, 1B]
      - name: 线粒体复合体
        insecticides: [鱼藤酮, 吡虫啉]
        irac_group: [21A, 21B]
```

---

## 抗性机制分类（示例）

```yaml
# notes/resistance-mechanisms.yaml
mechanisms:
  - type: 靶标抗性
    subtypes:
      - name: 点突变
        examples:
          - target: AChE
            mutation: [G119S, F290V, G227A]
            species: [小菜蛾, 蚜虫, 飞虱]
          - target: VGSC
            mutation: [L1014F, M918T, T929I]
            species: [小菜蛾, 棉铃虫]
      - name: 表达量变化
        examples:
          - target: nAChR α6
            change: 上调
            species: 小菜蛾
  
  - type: 代谢抗性
    subtypes:
      - name: 细胞色素 P450
        genes: [CYP6BG1, CYP6B6, CYP9A61]
      - name: 谷胱甘肽 S-转移酶 (GST)
        genes: [GSTe2, GSTd1]
      - name: 羧酸酯酶 (CarE)
        genes: [CarE1, CarE2]
  
  - type: 穿透抗性
    mechanism: 表皮增厚、脂质组成变化
  
  - type: 行为抗性
    mechanism: 回避行为、取食偏好改变
```

---

## 成功标准

**编译**：`python3 scripts/compile_paper.py --project-dir <paper_dir>`（退出码 0，无"Citation undefined"警告）

**质量指标**：
- 6-12 页正文（不含参考文献）
- 60-100 条总引用（每节 8-12 条）
- 100% 引用验证率
- 60%+ 引用来自近 5 年
- 中英文文献比例合理（中文期刊 ≥30% 中文文献；国际期刊以英文为主）
- 3-5 种可视化类型
- 所有 issues 为 `DONE` 或 `SKIP`

**领域特定指标**：
- 覆盖 ≥3 个主要靶标类别
- 包含抗性机制分析
- 引用 IRAC 分类或 WHO/FAO 指南
- 田间数据与实验室数据结合

---

## 安全与防护措施

- **绝不伪造**引用或结果；如缺少证据，添加 TODO 并询问用户
- **验证每条引用**：网络搜索 + 源页面（及 PDF）后再添加到 `ref.bib`
- **大规模文献检索前确认**
- **不覆盖**用户文件（除非确认）
- **Issues CSV 是合同**；仅在满足标准时标记 `DONE`
- **无提交包**（除非用户请求）

## 布局卫生

标记 issues 为 `DONE` 前修复 `Overfull \hbox` 警告：
- 图表：从 `figure` + `\columnwidth` 开始；需要时切换到 `figure*` + `\textwidth`
- 表格：优先使用 `p{...}` 列宽 / `\tabcolsep`，而非 `\resizebox`
- 公式：使用 `split`、`multline`、`aligned` 或 `IEEEeqnarray` 换行

---

## 参考文件索引

- `references/search-workflow.md`：文献检索方法论
- `references/writing-style-zh.md`：中文写作风格指南
- `references/writing-style-en.md`：英文写作风格指南
- `references/citation-workflow.md`：引用验证流程
- `references/bibtex-guide.md`：BibTeX 格式规则
- `references/visual-templates.md`：可视化触发器
- `references/target-classification-guide.md`：靶标分类指南
- `references/resistance-mechanisms-guide.md`：抗性机制分类指南
- `references/irac-moa-classification.md`：IRAC 作用机制分类
