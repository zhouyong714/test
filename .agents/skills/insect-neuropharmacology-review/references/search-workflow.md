# 文献检索工作流

## 检索策略

### 1. 国际数据库

**PubMed/Europe PMC**
- 优势: 生物医学权威库,免费全文多
- 检索语法:
  ```
  ("Plutella xylostella"[Title/Abstract] OR "diamondback moth"[Title/Abstract])
  AND ("insecticide resistance"[MeSH] OR "target site"[Title/Abstract])
  AND ("2019/01/01"[PDAT] : "2026/12/31"[PDAT])
  ```

**Web of Science**
- 优势: 引文追踪,影响因子高
- 检索语法:
  ```
  TS=("Plutella xylostella" OR "diamondback moth") 
  AND TS=("insecticide resistance" OR "acetylcholinesterase")
  AND PY=(2019-2026)
  ```

**Scopus**
- 优势: 覆盖面广,包含会议论文
- 检索语法:
  ```
  TITLE-ABS-KEY("Plutella xylostella" OR "diamondback moth") 
  AND TITLE-ABS-KEY("insecticide resistance")
  AND PUBYEAR > 2018
  ```

### 2. 中文数据库

**中国知网 (CNKI)**
- 检索语法:
  ```
  主题="小菜蛾" AND (主题="抗药性" OR 主题="靶标")
  时间范围: 2019-2026
  ```

**万方数据**
- 检索语法:
  ```
  题名或关键词:(小菜蛾) AND 题名或关键词:(抗性 OR 靶标)
  年份: 2019-2026
  ```

**维普**
- 检索语法:
  ```
  M=(小菜蛾) AND M=(抗药性 OR 乙酰胆碱酯酶)
  年份: 2019-2026
  ```

### 3. 专业数据库

**CAB Abstracts** (农业生物学权威)
- 检索语法:
  ```
  (Plutella xylostella OR diamondback moth) 
  AND (insecticide resistance OR target site)
  ```

**AGRIS** (FAO 农业科学库)
- 检索语法:
  ```
  "Plutella xylostella" AND "insecticide resistance"
  ```

## 检索流程

### 阶段 1: 初步发现 (15-25 篇)
1. 使用核心关键词在 PubMed 和知网检索
2. 筛选近 5 年高引文献
3. 阅读摘要,确定综述范围

### 阶段 2: 章节深入 (每节 8-12 篇)
1. 针对具体靶标/机制细化关键词
2. 结合中英文数据库
3. 追踪引文链

### 阶段 3: 补充验证
1. 检索灰色文献 (FAO/WHO 报告、IRAC 分类)
2. 查找最新预印本 (bioRxiv)
3. 补充田间试验数据

## 关键词库

### 害虫物种
- 小菜蛾: Plutella xylostella, diamondback moth
- 蚜虫: aphid, Aphis gossypii
- 飞虱: planthopper, Nilaparvata lugens

### 靶标类型
- 乙酰胆碱酯酶: acetylcholinesterase, AChE
- 烟碱型受体: nicotinic acetylcholine receptor, nAChR
- GABA 受体: GABA receptor, RDL
- 钠通道: voltage-gated sodium channel, VGSC

### 抗性机制
- 靶标抗性: target-site resistance, mutation
- 代谢抗性: metabolic resistance, P450, GST
- 穿透抗性: penetration resistance, cuticle

## 文献管理

### 记录格式
```markdown
## [标题]
- **来源**: 期刊名, 年份, 卷(期): 页码
- **DOI/PMID**: 
- **核心发现**: 
- **证据等级**: L0/L1/L2/L3
- **引用价值**: 
```

### 去重策略
1. 优先选择最新综述
2. 原创研究优于二次引用
3. 田间数据优于实验室数据
