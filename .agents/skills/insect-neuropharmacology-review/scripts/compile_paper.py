#!/usr/bin/env python3
"""
LaTeX 编译脚本,支持 xelatex 和 pdflatex,包含页数统计功能
"""
import argparse
import subprocess
import sys
from pathlib import Path


def compile_latex(project_dir: Path, report_pages: bool = False) -> int:
    """编译 LaTeX 项目"""
    main_tex = project_dir / "main.tex"
    if not main_tex.exists():
        print(f"错误: 找不到 {main_tex}", file=sys.stderr)
        return 1

    # 检测是否需要 xelatex (中文支持)
    content = main_tex.read_text(encoding='utf-8')
    use_xelatex = '\\usepackage{ctex}' in content or '\\usepackage{xeCJK}' in content

    latex_cmd = 'xelatex' if use_xelatex else 'pdflatex'

    # 编译流程: latex -> bibtex -> latex -> latex
    commands = [
        [latex_cmd, '-interaction=nonstopmode', 'main.tex'],
        ['bibtex', 'main'],
        [latex_cmd, '-interaction=nonstopmode', 'main.tex'],
        [latex_cmd, '-interaction=nonstopmode', 'main.tex'],
    ]

    for cmd in commands:
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)
        if result.returncode != 0 and cmd[0] != 'bibtex':
            print(f"编译失败: {' '.join(cmd)}", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1

    # 检查警告
    log_file = project_dir / "main.log"
    if log_file.exists():
        log_content = log_file.read_text(encoding='utf-8', errors='ignore')
        if 'Overfull \\hbox' in log_content:
            print("警告: 发现 Overfull \\hbox 警告", file=sys.stderr)
        if 'Citation' in log_content and 'undefined' in log_content:
            print("警告: 发现未定义的引用", file=sys.stderr)

    # 页数统计
    if report_pages:
        aux_file = project_dir / "main.aux"
        if aux_file.exists():
            aux_content = aux_file.read_text(encoding='utf-8', errors='ignore')
            # 查找 \newlabel{ReferencesStart}{{}{页码}}
            import re
            match = re.search(r'\\newlabel\{ReferencesStart\}\{\{[^}]*\}\{(\d+)\}\}', aux_content)
            if match:
                ref_start = int(match.group(1))
                print(f"正文页数: {ref_start - 1}")

    print(f"编译成功: {project_dir / 'main.pdf'}")
    return 0


def main():
    parser = argparse.ArgumentParser(description='编译 LaTeX 论文项目')
    parser.add_argument('--project-dir', type=Path, required=True, help='论文项目目录')
    parser.add_argument('--report-page-counts', action='store_true', help='报告页数统计')

    args = parser.parse_args()

    if not args.project_dir.is_dir():
        print(f"错误: {args.project_dir} 不是有效目录", file=sys.stderr)
        return 1

    return compile_latex(args.project_dir, args.report_page_counts)


if __name__ == '__main__':
    sys.exit(main())
