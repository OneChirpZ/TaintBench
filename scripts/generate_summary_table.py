#!/usr/bin/env python3
"""
生成 FlowDroid 分析结果综合表格
"""

import csv
from pathlib import Path
from collections import defaultdict

# 配置
OUTPUT_BASE = Path.home() / "LDFA-dataset/TaintBench/output"
APK_DIR = Path.home() / "LDFA-dataset/TaintBench/apks"

# 定义输出目录模式
MODE_PATTERNS = {
    'full (1x)': '*39apps-max-precision',
    'ne (1x)': '*39apps-no-exceptions',
    'ns (1x)': '*39apps-no-static', 
    'ne_ns (1x)': '*39apps-no-exception-no-static',
}

# 读取所有 APK 列表
all_apks = sorted([f.stem for f in APK_DIR.glob("*.apk")])

# 存储结果
results = {}

for apk in all_apks:
    results[apk] = {
        'path': str(APK_DIR / f"{apk}.apk"),
        'full (1x)': '-',
        'ne (1x)': '-',
        'ns (1x)': '-',
        'ne_ns (1x)': '-',
    }

# 读取各模式的结果
for mode, pattern in MODE_PATTERNS.items():
    # 找到匹配的目录（取最新的）
    matching_dirs = sorted(OUTPUT_BASE.glob(pattern), reverse=True)
    if not matching_dirs:
        continue
    
    # 使用最新的非 retry 目录
    for dir_path in matching_dirs:
        if 'retry' not in str(dir_path):
            csv_file = dir_path / "results_summary.csv"
            break
    else:
        # 如果都包含 retry，使用第一个
        csv_file = matching_dirs[0] / "results_summary.csv"
    
    if not csv_file.exists():
        continue
    
    # 读取 CSV
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            apk_name = row['apk_name']
            status = row['status']
            
            if apk_name in results:
                if status == 'SUCCESS':
                    results[apk_name][mode] = '✓'
                elif status == 'FAILED':
                    # 显示退出码
                    exit_code = row.get('exit_code', '')
                    results[apk_name][mode] = f'✗ ({exit_code})'
                elif status == 'SKIPPED':
                    results[apk_name][mode] = '○ (黑名单)'

# 生成 Markdown 表格
output = []
output.append("# FlowDroid TaintBench 分析结果综合表格\n")
output.append("## 配置说明\n")
output.append("- **1x**: 原始超时设置 (CT=600s, DT=1800s, RT=120s)")
output.append("- **✓**: 成功")
output.append("- **✗ (-9)**: 失败 (内存不足, SIGKILL)")
output.append("- **○ (黑名单)**: 已跳过\n")
output.append("| APK | APK 路径 | Full (1x) | ne (1x) | ns (1x) | ne_ns (1x) |")
output.append("|-----|----------|-----------|---------|---------|------------|")

for apk in sorted(results.keys()):
    r = results[apk]
    apk_path_short = r['path'].replace(str(Path.home()), '~')
    output.append(f"| {apk} | `{apk_path_short}` | {r['full (1x)']} | {r['ne (1x)']} | {r['ns (1x)']} | {r['ne_ns (1x)']} |")

# 保存到文件
output_file = OUTPUT_BASE / "COMPREHENSIVE_SUMMARY.md"
with open(output_file, 'w') as f:
    f.write('\n'.join(output))

print(f"综合表格已生成: {output_file}")
print("\n表格预览:")
print('\n'.join(output[:20]))  # 显示前 20 行
print("... (完整内容见文件)")
