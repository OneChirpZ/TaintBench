#!/usr/bin/env python3
"""
分析并统计 FlowDroid 结果
"""

import csv
from pathlib import Path

OUTPUT_BASE = Path.home() / "LDFA-dataset/TaintBench/output"
APK_DIR = Path.home() / "LDFA-dataset/TaintBench/apks"

# 定义输出目录模式
MODE_PATTERNS = {
    'full': '*39apps-max-precision',
    'ne': '*39apps-no-exceptions',
    'ns': '*39apps-no-static', 
    'ne_ns': '*39apps-no-exception-no-static',
}

print("=" * 80)
print("FlowDroid TaintBench 分析结果统计")
print("=" * 80)
print()

# 统计各模式
for mode, pattern in MODE_PATTERNS.items():
    # 找到匹配的目录（取最新的非 retry 目录）
    matching_dirs = sorted([d for d in OUTPUT_BASE.glob(pattern) if 'retry' not in str(d)], reverse=True)
    if not matching_dirs:
        continue
    
    csv_file = matching_dirs[0] / "results_summary.csv"
    if not csv_file.exists():
        continue
    
    with open(csv_file, 'r') as f:
        rows = list(csv.DictReader(f))
    
    total = len([r for r in rows if r['apk_name']])
    success = len([r for r in rows if r['status'] == 'SUCCESS'])
    failed = len([r for r in rows if r['status'] == 'FAILED'])
    skipped = len([r for r in rows if r['status'] == 'SKIPPED'])
    
    print(f"模式: {mode.upper()}")
    print(f"  文件: {matching_dirs[0].name}")
    print(f"  成功: {success}")
    print(f"  失败: {failed}")
    print(f"  跳过: {skipped}")
    print(f"  总计: {total}")
    
    if failed > 0:
        print(f"  失败的 APK:")
        for r in rows:
            if r['status'] == 'FAILED':
                print(f"    - {r['apk_name']} (退出码: {r['exit_code']}, 时间: {r['total_time_sec']}s)")
    print()

print("=" * 80)
print("综合统计")
print("=" * 80)
print()

# 统计所有 APK 在所有模式下的状态
all_apks = sorted([f.stem for f in APK_DIR.glob("*.apk")])

# 读取各模式结果
mode_results = {}
for mode, pattern in MODE_PATTERNS.items():
    matching_dirs = sorted([d for d in OUTPUT_BASE.glob(pattern) if 'retry' not in str(d)], reverse=True)
    if not matching_dirs:
        continue
    
    csv_file = matching_dirs[0] / "results_summary.csv"
    if not csv_file.exists():
        continue
    
    mode_results[mode] = {}
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mode_results[mode][row['apk_name']] = row['status']

# 统计
always_success = []
all_modes_fail = []
partial_fail = []

for apk in all_apks:
    statuses = []
    for mode in ['full', 'ne', 'ns', 'ne_ns']:
        if mode in mode_results and apk in mode_results[mode]:
            statuses.append(mode_results[mode][apk])
    
    if all(s == 'SUCCESS' for s in statuses):
        always_success.append(apk)
    elif all(s in ['FAILED', 'SKIPPED'] for s in statuses if s != 'SKIPPED'):
        all_modes_fail.append(apk)
    elif any(s == 'FAILED' for s in statuses):
        partial_fail.append(apk)

print(f"所有模式都成功: {len(always_success)} 个")
print(f"所有模式都失败或跳过: {len(all_modes_fail)} 个")
print(f"部分模式失败: {len(partial_fail)} 个")
print()

if partial_fail:
    print("部分模式失败的 APK:")
    for apk in partial_fail:
        print(f"\n  {apk}:")
        for mode in ['full', 'ne', 'ns', 'ne_ns']:
            if mode in mode_results and apk in mode_results[mode]:
                status = mode_results[mode][apk]
                print(f"    {mode}: {status}")

print()
print("=" * 80)
