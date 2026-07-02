#!/usr/bin/env python3
"""
验证 issues CSV 文件的格式和完整性
"""
import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = [
    'ID', 'Type', 'Section', 'Description', 'Status',
    'Verified_Citations', 'has_context_pain_gap', 'has_scope_deliverables',
    'has_taxonomy_map', 'has_section_loop', 'has_actionable_roadmap'
]

VALID_STATUSES = ['TODO', 'DOING', 'DONE', 'SKIP']
VALID_TYPES = ['W', 'Q', 'V', 'M']


def validate_csv(csv_path: Path, strict: bool = False) -> int:
    """验证 CSV 文件"""
    if not csv_path.exists():
        print(f"错误: 找不到 {csv_path}", file=sys.stderr)
        return 1

    errors = []
    warnings = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # 检查列
        if not all(col in reader.fieldnames for col in REQUIRED_COLUMNS):
            missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
            errors.append(f"缺少必需列: {missing}")
            return 1

        # 检查每行
        for i, row in enumerate(reader, start=2):
            issue_id = row.get('ID', f'行{i}')

            # 检查状态
            status = row.get('Status', '')
            if status not in VALID_STATUSES:
                errors.append(f"{issue_id}: 无效状态 '{status}'")

            # 检查类型
            issue_type = row.get('Type', '')
            if issue_type not in VALID_TYPES:
                errors.append(f"{issue_id}: 无效类型 '{issue_type}'")

            # 检查引用计数
            if status == 'DONE':
                citations = row.get('Verified_Citations', '0')
                try:
                    if int(citations) == 0:
                        warnings.append(f"{issue_id}: 标记为 DONE 但无验证引用")
                except ValueError:
                    errors.append(f"{issue_id}: 引用计数无效 '{citations}'")

            # 检查 playbook 门控
            if issue_type == 'W' and status == 'DONE':
                for gate in ['has_context_pain_gap', 'has_scope_deliverables',
                            'has_taxonomy_map', 'has_section_loop', 'has_actionable_roadmap']:
                    value = row.get(gate, '')
                    if value not in ['Y', 'N', 'N/A']:
                        if strict:
                            errors.append(f"{issue_id}: 门控 {gate} 值无效 '{value}'")
                        else:
                            warnings.append(f"{issue_id}: 门控 {gate} 值无效 '{value}'")

    # 输出结果
    if errors:
        print("验证失败:", file=sys.stderr)
        for err in errors:
            print(f"  ❌ {err}", file=sys.stderr)
        return 1

    if warnings:
        print("验证通过,但有警告:")
        for warn in warnings:
            print(f"  ⚠️  {warn}")
    else:
        print("✅ 验证通过")

    return 0


def main():
    parser = argparse.ArgumentParser(description='验证 issues CSV 文件')
    parser.add_argument('csv_file', type=Path, help='CSV 文件路径')
    parser.add_argument('--strict', action='store_true', help='严格模式(警告视为错误)')

    args = parser.parse_args()
    return validate_csv(args.csv_file, args.strict)


if __name__ == '__main__':
    sys.exit(main())
