#!/usr/bin/env python3
"""
修复 LDFA_SourcesAndSinks.txt 中的格式问题：
1. 去除参数格式不一致导致的重复
2. 标准化参数格式（统一使用逗号+空格）
3. 按字母顺序排序
"""

import re
from pathlib import Path
from typing import Set, Tuple


def normalize_signature(signature: str) -> str:
    """
    标准化方法签名：
    1. 参数之间统一使用 ", " (逗号+空格)
    2. 移除多余的空格
    """
    # 提取参数部分
    match = re.match(r'([^:]+:\s*[^:]+\s+\w+)\s*\(([^)]*)\)(\s*->\s*_SOURCE_|_SINK_)', signature)
    if not match:
        return signature

    prefix = match.group(1).strip()
    params = match.group(2).strip()
    suffix = match.group(3)

    # 标准化参数：在每个逗号后添加空格
    if params:
        # 先移除所有逗号后的空格
        params = params.replace(', ', ',')
        # 再在每个逗号后添加空格
        param_list = [p.strip() for p in params.split(',')]
        params = ', '.join(param_list)

    return f"{prefix}({params}){suffix}"


def load_and_deduplicate(file_path: Path) -> Tuple[Set[str], Set[str]]:
    """加载文件并去重"""
    sources = {}
    sinks = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 标准化签名
            normalized = normalize_signature(line)

            # 提取签名部分（用于去重）
            sig_part = normalized.split('->')[0].strip() if '->' in normalized else normalized

            if '_SOURCE_' in normalized:
                # 使用签名部分作为键来去重
                sources[sig_part] = normalized
            elif '_SINK_' in normalized:
                sinks[sig_part] = normalized

    return set(sources.values()), set(sinks.values())


def write_cleaned_file(sources: Set[str], sinks: Set[str], output_path: Path):
    """写入清理后的文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入文件头
        f.write("# LDFA Source and Sink List\n")
        f.write("# 合并自: TB (TaintBench), AD (Amandroid), DB (DroidBench), FD (FlowDroid)\n")
        f.write("# 格式: 类名: 返回类型 方法名(参数类型) -> _SOURCE_ 或 _SINK_\n")
        f.write(f"#\n")
        f.write(f"# 统计: {len(sources)} Sources, {len(sinks)} Sinks, 总计 {len(sources) + len(sinks)} 条目\n")
        f.write("# 注意: 参数格式已标准化（统一使用逗号+空格分隔）\n")
        f.write("#\n")

        # 写入 Sources
        f.write("\n# ==================== Sources ====================\n\n")
        for entry in sorted(sources):
            f.write(f"{entry}\n")

        # 写入 Sinks
        f.write("\n# ==================== Sinks ====================\n\n")
        for entry in sorted(sinks):
            f.write(f"{entry}\n")


def main():
    input_path = Path('/Users/zhangyiming/My_Documents/My_Code/LDFA-dataset/TaintBench/LDFA_SourcesAndSinks.txt')
    output_path = Path('/Users/zhangyiming/My_Documents/My_Code/LDFA-dataset/TaintBench/LDFA_SourcesAndSinks.txt')

    print("=" * 80)
    print("清理和标准化 LDFA SourcesAndSinks")
    print("=" * 80)

    # 加载并去重
    print(f"\n读取文件: {input_path.name}")
    sources, sinks = load_and_deduplicate(input_path)

    print(f"\n去重前统计:")
    print(f"  Sources: {len(sources)}")
    print(f"  Sinks: {len(sinks)}")
    print(f"  总计: {len(sources) + len(sinks)}")

    # 显示去重的数量
    original_sources = original_sinks = 0
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '_SOURCE_' in line and not line.startswith('#'):
                original_sources += 1
            elif '_SINK_' in line and not line.startswith('#'):
                original_sinks += 1

    print(f"\n去重效果:")
    print(f"  Sources: {original_sources} -> {len(sources)} (减少 {original_sources - len(sources)} 个)")
    print(f"  Sinks: {original_sinks} -> {len(sinks)} (减少 {original_sinks - len(sinks)} 个)")
    print(f"  总计: {original_sources + original_sinks} -> {len(sources) + len(sinks)} (减少 {(original_sources + original_sinks) - (len(sources) + len(sinks))} 个)")

    # 写入清理后的文件
    print(f"\n写入文件: {output_path.name}")
    write_cleaned_file(sources, sinks, output_path)

    print(f"\n文件大小: {output_path.stat().st_size / 1024:.2f} KB")

    # 验证
    print("\n" + "=" * 80)
    print("验证标准化结果")
    print("=" * 80)

    # 检查参数格式一致性
    all_entries = sources | sinks
    inconsistent = 0

    for entry in list(all_entries)[:100]:  # 检查前100个
        # 查找 ", " 和 "," 混用的情况
        if ', ' in entry:
            # 提取参数部分
            match = re.search(r'\(([^)]+)\)', entry)
            if match:
                params = match.group(1)
                # 检查是否有 ", ," 或 ",," 的情况
                if ', ,' in params or ',,' in params:
                    inconsistent += 1
                # 检查是否所有逗号后面都有空格
                elif re.search(r',[^ ]', params):
                    inconsistent += 1

    if inconsistent == 0:
        print("✓ 参数格式完全一致")
    else:
        print(f"⚠️  仍有 {inconsistent} 个条目的参数格式不一致")

    # 显示示例
    print("\n标准化后的条目示例:")
    for entry in sorted(list(sources))[:3]:
        print(f"  {entry}")
    for entry in sorted(list(sinks))[:3]:
        print(f"  {entry}")

    print("\n" + "=" * 80)
    print("清理完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()
