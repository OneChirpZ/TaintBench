#!/usr/bin/env python3
"""检查哪些行没有被解析"""

import re
from pathlib import Path

def parse_jimple_line(line: str):
    line = line.strip()
    if not line or line.startswith('%') or line.startswith('#'):
        return None

    match = re.match(r'<([^>]+)>\s*(?:\s+[^->]+)?\s*->\s*_?(SOURCE|SINK)_?', line, re.IGNORECASE)
    if match:
        return ('parsed', 'with_angle')

    match = re.match(r'([^:]+:[^:]+:[^(]+\([^)]*\))\s*->\s*_?(SOURCE|SINK)_?', line, re.IGNORECASE)
    if match:
        return ('parsed', 'without_angle')

    return ('unparsed', line[:50])

def check_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    total = 0
    parsed = 0
    unparsed_examples = []

    for i, line in enumerate(lines, 1):
        if 'SOURCE' in line or 'SINK' in line:
            total += 1
            result = parse_jimple_line(line)
            if result[0] == 'parsed':
                parsed += 1
            elif len(unparsed_examples) < 10:
                unparsed_examples.append((i, line.strip(), result[1]))

    print(f"\n文件: {file_path.name}")
    print(f"  总行数: {len(lines)}")
    print(f"  SOURCE/SINK行: {total}")
    print(f"  已解析: {parsed}")
    print(f"  未解析: {total - parsed}")

    if unparsed_examples:
        print(f"\n  未解析示例 (前10条):")
        for line_no, line, reason in unparsed_examples:
            print(f"    行{line_no}: {line}")

    return parsed, total

files = [
    Path('TB_SourcesAndSinks.txt'),
    Path('AD_SourcesAndSinks.txt'),
    Path('DB_SourcesAndSinks.txt'),
    Path('FD_SourcesAndSinks.txt'),
]

print("=" * 70)
print("检查各文件解析情况")
print("=" * 70)

total_parsed = 0
total_lines = 0

for file_path in files:
    parsed, total = check_file(file_path)
    total_parsed += parsed
    total_lines += total

print(f"\n总计:")
print(f"  解析成功: {total_parsed}")
print(f"  总条目数: {total_lines}")
print(f"  遗漏: {total_lines - total_parsed}")
