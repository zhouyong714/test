#!/usr/bin/env python3
"""
昆虫神经药理学综述项目初始化脚本
支持 kickoff 和 issues 阶段,包含中英文双语支持
"""
import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path


def create_project_structure(project_dir: Path):
    """创建项目目录结构"""
    dirs = ['plan', 'issues', 'notes']
    for d in dirs:
        (project_dir / d).mkdir(parents=True, exist_ok=True)


def generate_timestamp_slug(topic: str) -> str:
    """生成时间戳-slug 格式的文件名"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    slug = topic.lower().replace(' ', '-').replace('/', '-')[:40]
    return f"{timestamp}-{slug}"


def kickoff_stage(project_dir: Path, topic: str, species: str, language: str):
    """门控 0: 创建项目结构和草案计划"""
    create_project_structure(project_dir)

    slug = generate_timestamp_slug(topic)
    plan_file = project_dir / 'plan' / f'{slug}.md'

    # 创建草案计划
    plan_content = f"""# 综述计划: {topic}

## 基本信息
- **主题**: {topic}
- **目标物种**: {species}
- **语言**: {language}
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 约束条件
- [ ] 目标期刊: (待确认)
- [ ] 页数限制: (待确认)
- [ ] 截止日期: (待确认)

## 候选标题
1. (待补充)
2. (待补充)

## 大纲草案
### 1. 引言
- 背景与趋势
- 核心问题
- 研究空缺

### 2. 靶标分类体系
- (待补充)

### 3-6. 技术章节
- (待补充)

### 7. 结论与展望
- 短期目标 (1-3 年)
- 中期目标 (3-5 年)

## 可视化计划
- (待补充)

## 启动门控
- [ ] 用户已在对话中确认范围和大纲
"""

    plan_file.write_text(plan_content, encoding='utf-8')
    print(f"✅ 创建计划文件: {plan_file}")

    # 创建 main.tex 框架
    if language == 'zh':
        template = r"""\documentclass[journal]{IEEEtran}
\usepackage{ctex}
\usepackage{cite}
\usepackage{graphicx}

\begin{document}

\title{标题待定}
\author{作者待定}
\maketitle

\begin{abstract}
摘要待补充
\end{abstract}

\section{引言}
% 框架骨架,无正文

\section{结论}
% 框架骨架,无正文

\label{ReferencesStart}
\bibliographystyle{IEEEtran}
\bibliography{ref}

\end{document}
"""
    else:
        template = r"""\documentclass[journal]{IEEEtran}
\usepackage{cite}
\usepackage{graphicx}

\begin{document}

\title{Title TBD}
\author{Author TBD}
\maketitle

\begin{abstract}
Abstract TBD
\end{abstract}

\section{Introduction}
% Skeleton only, no prose

\section{Conclusion}
% Skeleton only, no prose

\label{ReferencesStart}
\bibliographystyle{IEEEtran}
\bibliography{ref}

\end{document}
"""

    main_tex = project_dir / 'main.tex'
    main_tex.write_text(template, encoding='utf-8')
    print(f"✅ 创建 main.tex 框架")

    # 创建空 ref.bib
    ref_bib = project_dir / 'ref.bib'
    ref_bib.write_text('', encoding='utf-8')
    print(f"✅ 创建 ref.bib")


def issues_stage(project_dir: Path, topic: str, with_literature_notes: bool):
    """门控 1: 创建 issues CSV"""
    # 检查启动门控
    plan_files = sorted((project_dir / 'plan').glob('*.md'))
    if not plan_files:
        print("错误: 找不到计划文件,请先运行 kickoff 阶段", file=sys.stderr)
        return 1

    latest_plan = plan_files[-1]
    plan_content = latest_plan.read_text(encoding='utf-8')

    if '- [x] 用户已在对话中确认范围和大纲' not in plan_content:
        print("错误: 启动门控未勾选,请先获得用户批准", file=sys.stderr)
        return 1

    slug = generate_timestamp_slug(topic)
    issues_file = project_dir / 'issues' / f'{slug}.csv'

    # 创建 issues CSV
    headers = [
        'ID', 'Type', 'Section', 'Description', 'Status',
        'Verified_Citations', 'has_context_pain_gap', 'has_scope_deliverables',
        'has_taxonomy_map', 'has_section_loop', 'has_actionable_roadmap'
    ]

    rows = [
        ['W1', 'W', 'Introduction', '撰写引言', 'TODO', '0', 'Y', 'Y', 'N/A', 'N/A', 'N/A'],
        ['W2', 'W', 'Taxonomy', '撰写靶标分类体系', 'TODO', '0', 'N/A', 'N/A', 'Y', 'N/A', 'N/A'],
        ['W3', 'W', 'Conclusion', '撰写结论', 'TODO', '0', 'N/A', 'N/A', 'N/A', 'N/A', 'Y'],
        ['Q1', 'Q', 'All', 'QA 检查', 'TODO', '0', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
    ]

    with open(issues_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"✅ 创建 issues CSV: {issues_file}")

    # 可选: 创建文献笔记
    if with_literature_notes:
        notes_file = project_dir / 'notes' / 'literature-notes.md'
        notes_file.write_text('# 文献笔记\n\n', encoding='utf-8')
        print(f"✅ 创建文献笔记: {notes_file}")

    return 0


def main():
    parser = argparse.ArgumentParser(description='昆虫神经药理学综述项目初始化')
    parser.add_argument('--stage', choices=['kickoff', 'issues'], required=True,
                       help='执行阶段')
    parser.add_argument('--topic', required=True, help='综述主题')
    parser.add_argument('--species', default='', help='目标物种 (kickoff 阶段)')
    parser.add_argument('--language', choices=['zh', 'en'], default='zh',
                       help='语言选择 (kickoff 阶段)')
    parser.add_argument('--with-literature-notes', action='store_true',
                       help='创建文献笔记 (issues 阶段)')
    parser.add_argument('--project-dir', type=Path, default=Path.cwd(),
                       help='项目目录 (默认当前目录)')

    args = parser.parse_args()

    if args.stage == 'kickoff':
        kickoff_stage(args.project_dir, args.topic, args.species, args.language)
        return 0
    elif args.stage == 'issues':
        return issues_stage(args.project_dir, args.topic, args.with_literature_notes)


if __name__ == '__main__':
    sys.exit(main())
