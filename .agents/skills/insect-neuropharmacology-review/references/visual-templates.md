# 可视化模板

## 触发器

### 1. 分类体系 → 表格或树状图
**触发条件**: 介绍靶标分类、抗性机制分类
**推荐格式**: 
- 表格 (2-3 层级)
- 树状图 (>3 层级)

**示例**:
```latex
\begin{table}[!t]
\caption{昆虫神经系统药理靶标分类}
\begin{tabular}{lll}
\hline
类别 & 靶标 & 代表性杀虫剂 \\
\hline
神经递质受体 & nAChR & 新烟碱类 \\
 & GABA 受体 & 环戊二烯类 \\
离子通道 & VGSC & 拟除虫菊酯类 \\
\hline
\end{tabular}
\end{table}
```

### 2. 时间趋势 → 折线图
**触发条件**: 抗性发展历程、研究热点变化
**推荐格式**: 折线图或时间轴

### 3. 机制对比 → 流程图
**触发条件**: 作用机制、抗性机制
**推荐格式**: 流程图或示意图

**示例**:
```latex
\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{mechanism.pdf}
\caption{nAChR 激动剂作用机制}
\end{figure}
```

### 4. 数据分布 → 柱状图或饼图
**触发条件**: 抗性频率、突变类型分布
**推荐格式**: 
- 柱状图 (比较多组)
- 饼图 (比例关系)

### 5. 关系网络 → 网络图
**触发条件**: 靶标-杀虫剂-抗性关系
**推荐格式**: 网络图或桑基图

## 图表设计原则

### 1. 简洁性
- 避免 3D 效果
- 限制颜色数量 (≤5 种)
- 清晰的标签和图例

### 2. 可读性
- 字体大小 ≥8pt
- 高对比度配色
- 避免过度装饰

### 3. 一致性
- 统一配色方案
- 统一字体和样式
- 统一图表尺寸

## LaTeX 图表模板

### 单栏图表
```latex
\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{figure.pdf}
\caption{图标题}
\label{fig:label}
\end{figure}
```

### 双栏图表
```latex
\begin{figure*}[!t]
\centering
\includegraphics[width=\textwidth]{figure.pdf}
\caption{图标题}
\label{fig:label}
\end{figure*}
```

### 表格
```latex
\begin{table}[!t]
\caption{表标题}
\label{tab:label}
\centering
\begin{tabular}{lcc}
\hline
列1 & 列2 & 列3 \\
\hline
数据1 & 数据2 & 数据3 \\
\hline
\end{tabular}
\end{table}
```

## 工具推荐

### 绘图工具
- **Python**: matplotlib, seaborn
- **R**: ggplot2
- **在线工具**: draw.io, BioRender

### 配色方案
- **色盲友好**: ColorBrewer
- **学术配色**: Nature/Science 配色方案
