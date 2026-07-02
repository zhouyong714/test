# BibTeX 格式指南

## 基本格式

### 期刊文章 (@article)
```bibtex
@article{CitationKey2023,
  author = {Last1, First1 and Last2, First2},
  title = {Article title},
  journal = {Journal Name},
  year = {2023},
  volume = {10},
  number = {5},
  pages = {123--145},
  doi = {10.1234/journal.2023.12345}
}
```

### 书籍 (@book)
```bibtex
@book{Author2020,
  author = {Last, First},
  title = {Book Title},
  publisher = {Publisher Name},
  year = {2020},
  address = {City},
  edition = {2nd}
}
```

### 会议论文 (@inproceedings)
```bibtex
@inproceedings{Author2022,
  author = {Last, First},
  title = {Paper title},
  booktitle = {Proceedings of Conference Name},
  year = {2022},
  pages = {100--110},
  address = {City, Country}
}
```

### 预印本 (@article with note)
```bibtex
@article{Smith2025,
  author = {Smith, John},
  title = {Preprint title},
  journal = {bioRxiv},
  year = {2025},
  doi = {10.1101/2025.01.15.123456},
  note = {Preprint}
}
```

## 中文文献

### 中文期刊
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

### 中文书籍
```bibtex
@book{Wang2018,
  author = {王五},
  title = {昆虫毒理学},
  publisher = {科学出版社},
  year = {2018},
  address = {北京},
  language = {zh}
}
```

## Citation Key 规则

### 格式
`FirstAuthorLastName + Year`

### 示例
- 单作者: `Talekar2003`
- 多作者: `Smith2020` (使用第一作者)
- 同年多篇: `Smith2020a`, `Smith2020b`

### 中文作者
- 使用拼音: `Zhang2020`, `Wang2018`
- 避免使用中文字符

## 必需字段

### @article
- author, title, journal, year

### @book
- author, title, publisher, year

### @inproceedings
- author, title, booktitle, year

## 可选但推荐字段

- **doi**: 数字对象标识符 (强烈推荐)
- **volume, number, pages**: 期刊文章
- **url**: 在线资源
- **note**: 特殊说明 (如 "Preprint")

## 格式规范

### 作者名
- 格式: `Last, First and Last2, First2`
- 多作者用 `and` 连接
- 中文: `张三 and 李四`

### 标题
- 使用句首大写或标题大写
- 特殊术语用 `{}` 保护: `{DNA}`, `{GABA}`

### 页码
- 使用双连字符: `123--145`
- 不要用单连字符: `123-145`

### 期刊名
- 使用全称或标准缩写
- 保持一致性

## 常见错误

### 1. 页码格式
❌ `pages = {123-145}`
✅ `pages = {123--145}`

### 2. 作者分隔
❌ `author = {Smith, J., Doe, A.}`
✅ `author = {Smith, J. and Doe, A.}`

### 3. 缺少必需字段
❌ 缺少 year 或 journal
✅ 包含所有必需字段

### 4. 特殊字符
❌ 直接使用 `&`, `%`, `_`
✅ 转义: `\&`, `\%`, `\_`
