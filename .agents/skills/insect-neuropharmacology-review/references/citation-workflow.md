# 引用验证流程

## 验证标准

### 必须验证
1. 所有定量声明 (数字、百分比、统计值)
2. 关键论断 (机制、抗性、效果)
3. 新发现或争议性观点

### 可选验证
1. 教科书级别的常识
2. 已在多篇综述中引用的经典研究

## 验证步骤

### 步骤 1: 网络搜索
```bash
# 搜索标题 + 第一作者
"Insecticide resistance in Plutella xylostella" + "Talekar"

# 搜索 DOI
10.1146/annurev.ento.51.110104.151146
```

### 步骤 2: 打开源页面
- 期刊官网
- PubMed/PMC
- ResearchGate/Academia.edu (备选)

### 步骤 3: 核对信息
- 标题、作者、年份
- 期刊名、卷期页码
- DOI/PMID

### 步骤 4: 阅读摘要/全文
- 确认引用的具体数据
- 检查上下文是否匹配
- 注意预印本标注

## BibTeX 格式

### 期刊文章
```bibtex
@article{Talekar2003,
  author = {Talekar, N. S. and Shelton, A. M.},
  title = {Biology, ecology, and management of the diamondback moth},
  journal = {Annual Review of Entomology},
  year = {2003},
  volume = {48},
  pages = {275--301},
  doi = {10.1146/annurev.ento.48.091801.112605}
}
```

### 中文文章
```bibtex
@article{Zhang2020,
  author = {张三 and 李四},
  title = {小菜蛾抗药性研究进展},
  journal = {昆虫学报},
  year = {2020},
  volume = {63},
  number = {5},
  pages = {601--610},
  language = {zh}
}
```

### 预印本
```bibtex
@article{Smith2025,
  author = {Smith, J. and Doe, A.},
  title = {Novel nAChR mutations in resistant populations},
  journal = {bioRxiv},
  year = {2025},
  doi = {10.1101/2025.01.15.123456},
  note = {Preprint}
}
```

## 引用密度

### 目标
- 每 3 句至少 1 条引用
- 每段 2-4 条引用
- 每节 8-12 条引用

### 分布
- 引言: 15-20 条
- 技术章节: 每节 8-12 条
- 结论: 5-8 条

## 常见错误

### 1. 二次引用
❌ 引用综述中提到的原始数据
✅ 追溯到原始文献

### 2. 过度引用
❌ 每句话都有引用
✅ 关键论断有引用,常识性陈述无需引用

### 3. 引用不匹配
❌ 引用的文献不支持该论断
✅ 仔细核对引用内容
