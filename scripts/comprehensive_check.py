#!/usr/bin/env python3
"""
全面检查 LDFA_SourcesAndSinks.txt 的质量和完整性
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Set, Tuple, List


def load_entries(file_path: Path) -> Tuple[Set[str], Set[str]]:
    """加载所有 sources 和 sinks"""
    sources = set()
    sinks = set()

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '_SOURCE_' in line:
                sources.add(line)
            elif '_SINK_' in line:
                sinks.add(line)

    return sources, sinks


def check_format_consistency(sources: Set[str], sinks: Set[str]) -> List[str]:
    """检查格式一致性问题"""
    issues = []

    all_entries = sources | sinks

    # 检查1: 是否还有 Smali 格式的类型签名
    smali_pattern = re.compile(r'L[a-zA-Z/$]+;')
    for entry in all_entries:
        if smali_pattern.search(entry):
            issues.append(f"❌ 发现 Smali 格式: {entry[:80]}...")

    # 检查2: 是否有空格不一致的问题（参数之间）
    # 提取所有方法签名
    method_sigs = defaultdict(list)
    for entry in all_entries:
        # 提取方法签名部分（在 -> 之前）
        sig_part = entry.split('->')[0].strip()

        # 标准化：移除参数之间的空格
        normalized = re.sub(r',\s+', ',', sig_part)

        # 提取方法名和参数部分（用于分组）
        match = re.match(r'([^:]+: [^(]+)\(([^)]*)\)', sig_part)
        if match:
            class_return = match.group(1)
            params = match.group(2)

            # 标准化参数
            normalized_params = re.sub(r',\s+', ',', params)
            key = f"{class_return}({normalized_params})"

            method_sigs[key].append(entry)
        else:
            issues.append(f"⚠️  无法解析的方法签名: {entry[:80]}...")

    # 检查3: 查找可能的重复（参数格式不同）
    duplicates = []
    for key, entries in method_sigs.items():
        if len(entries) > 1:
            duplicates.append((key, entries))

    if duplicates:
        issues.append(f"\n🔍 发现 {len(duplicates)} 组可能的重复（参数格式不同）:")
        for key, entries in duplicates[:10]:  # 只显示前10组
            issues.append(f"   方法: {key}")
            for entry in entries:
                issues.append(f"     - {entry[:100]}")
        if len(duplicates) > 10:
            issues.append(f"   ... 还有 {len(duplicates) - 10} 组")

    # 检查4: 查找构造函数（<init>）
    constructors = [e for e in all_entries if '<init>' in e]
    if constructors:
        issues.append(f"\n✓ 构造函数: {len(constructors)} 个")
        for cons in constructors[:5]:
            issues.append(f"   - {cons[:100]}")
        if len(constructors) > 5:
            issues.append(f"   ... 还有 {len(constructors) - 5} 个")

    return issues


def compare_with_sources(sources: Set[str], sinks: Set[str]) -> List[str]:
    """与原始文件对比，检查覆盖率"""
    issues = []

    base_dir = Path('/Users/zhangyiming/My_Documents/My_Code/LDFA-dataset/TaintBench')
    original_files = {
        'TB': 'TB_SourcesAndSinks.txt',
        'AD': 'AD_SourcesAndSinks.txt',
        'DB': 'DB_SourcesAndSinks.txt',
        'FD': 'FD_SourcesAndSinks.txt',
    }

    all_entries = sources | sinks

    # 创建查找索引
    created_index = defaultdict(set)
    for entry in all_entries:
        # 提取类名和方法名
        match = re.match(r'([^:]+):\s*(?:[^:]+:\s*)?(\w+)\s*\(', entry)
        if match:
            class_name = match.group(1)
            method_name = match.group(2)
            created_index[(class_name, method_name)].add(entry)

    # 检查每个原始文件
    for file_tag, file_name in original_files.items():
        file_path = base_dir / file_name
        if not file_path.exists():
            continue

        missing = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('%') or line.startswith('#'):
                    continue

                # 提取方法信息
                # Jimple 格式
                match = re.match(r'<([^:>]+):\s*([^:]+)\s+(\w+)\s*\(', line)
                if match:
                    class_name = match.group(1)
                    method_name = match.group(3)
                else:
                    # 不带尖括号的 Jimple 格式
                    match = re.match(r'([^:>]+):\s*(?:[^:]+:\s*)?(\w+)\s*\(', line)
                    if match:
                        class_name = match.group(1)
                        method_name = match.group(2)
                    else:
                        # Smali 格式
                        match = re.match(r'L([^;]+);\.([^:]+):\s*\(', line)
                        if match:
                            class_name = match.group(1).replace('/', '.')
                            method_name = match.group(2)
                        else:
                            continue

                key = (class_name, method_name)
                if key not in created_index:
                    missing.append(f"{class_name}.{method_name}")

        if missing:
            issues.append(f"\n⚠️  {file_tag} 文件中有 {len(missing)} 个方法可能在合并列表中缺失:")
            for m in missing[:10]:
                issues.append(f"   - {m}")
            if len(missing) > 10:
                issues.append(f"   ... 还有 {len(missing) - 10} 个")

    return issues


def check_specific_patterns(sources: Set[str], sinks: Set[str]) -> List[str]:
    """检查特定的方法和类型"""
    issues = []

    all_entries = sources | sinks

    # 关键方法检查
    key_methods = [
        ('getDeviceId', '获取设备ID'),
        ('getSubscriberId', '获取订阅者ID'),
        ('getSimSerialNumber', '获取SIM序列号'),
        ('sendTextMessage', '发送短信'),
        ('Log', '日志输出'),
        ('<init>', '构造函数'),
        ('getIntent', '获取Intent'),
        ('putExtra', '添加Extra'),
        ('startService', '启动服务'),
        ('sendBroadcast', '发送广播'),
    ]

    issues.append("\n🔍 关键方法检查:")
    for method, desc in key_methods:
        found = [e for e in all_entries if method in e]
        if found:
            issues.append(f"  ✓ {desc} ({method}): {len(found)} 个")
        else:
            issues.append(f"  ✗ {desc} ({method}): 未找到")

    # 类型检查
    issues.append("\n📊 类型统计:")
    type_counts = defaultdict(int)
    for entry in all_entries:
        # 提取所有 java.xxx 和 android.xxx 类型
        types = re.findall(r'(?:java|android|javax)\.[a-zA-Z0-9.]+', entry)
        for t in types:
            type_counts[t] += 1

    # 显示最常见的类型
    common_types = sorted(type_counts.items(), key=lambda x: -x[1])[:10]
    for type_name, count in common_types:
        issues.append(f"  - {type_name}: {count} 次")

    return issues


def main():
    print("=" * 80)
    print("LDFA SourcesAndSinks 全面检查")
    print("=" * 80)

    file_path = Path('/Users/zhangyiming/My_Documents/My_Code/LDFA-dataset/TaintBench/LDFA_SourcesAndSinks.txt')

    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return

    # 加载条目
    sources, sinks = load_entries(file_path)

    print(f"\n📋 基本信息:")
    print(f"  Sources: {len(sources)}")
    print(f"  Sinks: {len(sinks)}")
    print(f"  总计: {len(sources) + len(sinks)}")

    # 检查1: 格式一致性
    print(f"\n{'=' * 80}")
    print("检查 1: 格式一致性")
    print("=" * 80)
    issues = check_format_consistency(sources, sinks)
    for issue in issues:
        print(issue)

    # 检查2: 与原始文件对比
    print(f"\n{'=' * 80}")
    print("检查 2: 与原始文件对比")
    print("=" * 80)
    issues = compare_with_sources(sources, sinks)
    for issue in issues:
        print(issue)

    # 检查3: 特定模式和关键方法
    print(f"\n{'=' * 80}")
    print("检查 3: 关键方法和类型统计")
    print("=" * 80)
    issues = check_specific_patterns(sources, sinks)
    for issue in issues:
        print(issue)

    # 检查4: 参数格式标准化问题
    print(f"\n{'=' * 80}")
    print("检查 4: 参数格式标准化建议")
    print("=" * 80)

    all_entries = sources | sinks
    param_format_issues = []

    for entry in list(all_entries)[:50]:  # 检查前50个
        match = re.search(r'\(([^)]+)\)', entry)
        if match:
            params = match.group(1)
            # 检查参数之间的空格是否一致
            if ', ' in params and ',' in params.replace(', ', ''):
                param_format_issues.append(f"参数空格不一致: {entry[:100]}")

    if param_format_issues:
        print(f"发现 {len(param_format_issues)} 个参数格式不一致的条目（前50个中）:")
        for issue in param_format_issues[:5]:
            print(f"  - {issue}")
    else:
        print("✓ 参数格式一致性良好")

    print(f"\n{'=' * 80}")
    print("检查完成")
    print("=" * 80)


if __name__ == '__main__':
    main()
