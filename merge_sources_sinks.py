#!/usr/bin/env python3
"""
合并多个 Source/Sink 列表并去重，生成统一的 LDFA_SourcesAndSinks.txt

支持的格式:
- Jimple: <android.telephony.TelephonyManager: java.lang.String getDeviceId()> -> _SOURCE_
- Smali:  Landroid/telephony/TelephonyManager;.getDeviceId:()Ljava/lang/String; -> _SOURCE_

策略: 优先使用 Jimple 格式，Smali 作为补充（仅包含 Jimple 中没有的）
"""

import re
from pathlib import Path
from typing import Set, Tuple, Optional


def parse_jimple_line(line: str) -> Optional[Tuple[str, str]]:
    """
    解析 Jimple 格式的行
    返回: (方法签名, 类别) 或 None
    """
    line = line.strip()
    if not line or line.startswith('%') or line.startswith('#'):
        return None

    # 匹配 Jimple 格式:
    #   <类名: 返回类型 方法名(参数)> -> _SOURCE_ 或 _SINK_
    #   类名: 返回类型 方法名(参数) -> _SOURCE_ (不带尖括号)
    # 也处理格式: <类名: 返回类型 方法名(参数)> 权限 -> _SOURCE_

    # 先尝试带尖括号的格式
    match = re.match(r'<([^>]+)>\s*(?:\s+[^->]+)?\s*->\s*_?(SOURCE|SINK)_?', line, re.IGNORECASE)
    if match:
        full_sig = match.group(1).strip()
        category = f'_{match.group(2).upper()}_'
        return (full_sig, category)

    # 再尝试不带尖括号的格式
    match = re.match(r'([^:]+:[^:]+:[^(]+\([^)]*\))\s*->\s*_?(SOURCE|SINK)_?', line, re.IGNORECASE)
    if match:
        full_sig = match.group(1).strip()
        category = f'_{match.group(2).upper()}_'
        return (full_sig, category)

    return None


def parse_smali_line_simple(line: str) -> Optional[Tuple[str, str]]:
    """
    简化的 Smali 解析 - 只提取基本信息，不做完整转换
    """
    line = line.strip()
    if not line or line.startswith('%') or line.startswith('#'):
        return None

    # 格式: Landroid/telephony/TelephonyManager;.getDeviceId:()Ljava/lang/String; SENSITIVE_INFO -> _SOURCE_
    if '->' not in line:
        return None

    parts = line.split('->')
    if len(parts) < 2:
        return None

    category = '_SOURCE_' if 'SOURCE' in parts[1].upper() else '_SINK_'

    # 简单提取：将 Smali 中的 . 替换为 : ，添加 <>
    # Landroid/telephony/TelephonyManager;.getDeviceId:()Ljava/lang/String;
    # -> <android.telephony.TelephonyManager: java.lang.String getDeviceId()>
    sig_part = parts[0].strip()

    # 移除额外标签
    sig_part = re.sub(r'\s+(SENSITIVE_INFO|INTERNET|INTENT|AUDIO|LOCATION|MESSAGE)\s*', ' ', sig_part)
    sig_part = sig_part.strip()

    # 提取类名和方法
    # Landroid/telephony/TelephonyManager;.getDeviceId:()Ljava/lang/String;
    # 注意：Smali 中方法名后面有冒号
    match = re.match(r'L([^;]+);\.([^:]+):\s*\(([^)]*)\)(L[^;]+;)?', sig_part)
    if not match:
        return None

    class_path = match.group(1).replace('/', '.')
    method_name = match.group(2)
    params = match.group(3)
    return_type_sig = match.group(4) if match.group(4) else ''

    # 转换类型
    def smali_type_to_java(t: str) -> str:
        t = t.strip()
        if not t:
            return 'void'

        # 数组
        arrays = 0
        while t.startswith('['):
            arrays += 1
            t = t[1:]

        # 基本类型
        prim_map = {
            'Z': 'boolean', 'B': 'byte', 'S': 'short',
            'I': 'int', 'J': 'long', 'F': 'float',
            'D': 'double', 'V': 'void'
        }

        if t in prim_map:
            result = prim_map[t]
        elif t.startswith('L') and t.endswith(';'):
            result = t[1:-1].replace('/', '.')
        else:
            result = t

        return result + ('[]' * arrays)

    # 解析参数
    param_list = []
    i = 0
    while i < len(params):
        if params[i] == '[':
            start = i
            while i < len(params) and params[i] == '[':
                i += 1
            if i < len(params) and params[i] == 'L':
                end = params.find(';', i)
                if end != -1:
                    param_list.append(smali_type_to_java(params[start:end+1]))
                    i = end + 1
                    continue
            elif i < len(params) and params[i] in 'ZBSIJFD':
                param_list.append(smali_type_to_java(params[start:i+1]))
                i += 1
                continue
            else:
                i += 1
        elif params[i] in 'ZBSIJFDV':
            param_list.append(smali_type_to_java(params[i]))
            i += 1
        elif params[i] == 'L':
            end = params.find(';', i)
            if end != -1:
                param_list.append(smali_type_to_java(params[i:end+1]))
                i = end + 1
            else:
                i += 1
        else:
            i += 1

    # 构造 Jimple 格式（标准格式，不带尖括号）
    return_type = smali_type_to_java(return_type_sig) if return_type_sig else 'void'
    param_str = ', '.join(param_list)
    jimple_sig = f'{class_path}: {return_type} {method_name}({param_str})'
    return (jimple_sig, category)


def read_sources_sinks(file_path: Path) -> Set[Tuple[str, str]]:
    """读取 source/sink 文件，返回 (方法签名, 类别) 的集合"""
    sources_sinks = set()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith('%') or line.startswith('#'):
                continue

            # 尝试 Jimple 格式
            result = parse_jimple_line(line)
            if result:
                sources_sinks.add(result)
                continue

            # 尝试 Smali 格式
            result = parse_smali_line_simple(line)
            if result:
                sources_sinks.add(result)

    return sources_sinks


def merge_sources_sinks(files: list) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    """合并多个文件中的 sources 和 sinks"""
    all_sources = set()
    all_sinks = set()

    for file_path in files:
        if not file_path.exists():
            print(f"警告: 文件不存在 {file_path}")
            continue

        print(f"处理文件: {file_path.name} ({file_path.stat().st_size / 1024:.1f} KB)")
        sources_sinks = read_sources_sinks(file_path)

        file_sources = set()
        file_sinks = set()

        for method_sig, category in sources_sinks:
            if 'SOURCE' in category.upper():
                all_sources.add((method_sig, category))
                file_sources.add(method_sig)
            elif 'SINK' in category.upper():
                all_sinks.add((method_sig, category))
                file_sinks.add(method_sig)

        print(f"  -> {len(file_sources)} sources, {len(file_sinks)} sinks")

    return all_sources, all_sinks


def write_ldfa_sources_sinks(
    sources: Set[Tuple[str, str]],
    sinks: Set[Tuple[str, str]],
    output_path: Path
):
    """写入 LDFA_SourcesAndSinks.txt 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入文件头
        f.write("# LDFA Source and Sink List\n")
        f.write("# 合并自: TB (TaintBench), AD (Amandroid), DB (DroidBench), FD (FlowDroid)\n")
        f.write("# 格式: <类名: 返回类型 方法名(参数类型)> -> _SOURCE_ 或 _SINK_\n")
        f.write(f"#\n")
        f.write(f"# 统计: {len(sources)} Sources, {len(sinks)} Sinks, 总计 {len(sources) + len(sinks)} 条目\n")
        f.write("#\n")

        # 写入 Sources
        f.write("\n# ==================== Sources ====================\n\n")
        for method_sig, category in sorted(sources, key=lambda x: x[0]):
            f.write(f"{method_sig} -> {category}\n")

        # 写入分隔符
        f.write("\n# ==================== Sinks ====================\n\n")

        # 写入 Sinks
        for method_sig, category in sorted(sinks, key=lambda x: x[0]):
            f.write(f"{method_sig} -> {category}\n")


def main():
    # 定义输入文件
    base_dir = Path('/Users/zhangyiming/My_Documents/My_Code/LDFA-dataset/TaintBench')

    input_files = [
        base_dir / 'TB_SourcesAndSinks.txt',
        base_dir / 'AD_SourcesAndSinks.txt',
        base_dir / 'DB_SourcesAndSinks.txt',
        base_dir / 'FD_SourcesAndSinks.txt',
    ]

    # 合并 sources 和 sinks
    print("=" * 70)
    print("合并 Source/Sink 列表")
    print("=" * 70)
    sources, sinks = merge_sources_sinks(input_files)

    print(f"\n合并结果:")
    print(f"  唯一 Sources: {len(sources)}")
    print(f"  唯一 Sinks: {len(sinks)}")
    print(f"  总计: {len(sources) + len(sinks)}")

    # 写入输出文件
    output_path = base_dir / 'LDFA_SourcesAndSinks.txt'
    write_ldfa_sources_sinks(sources, sinks, output_path)

    print(f"\n已生成: {output_path.name}")
    print(f"文件大小: {output_path.stat().st_size / 1024:.2f} KB")

    # 显示一些示例
    print("\n=== Sources 示例 ===")
    for method_sig, _ in sorted(sources)[:5]:
        print(f"  {method_sig}")

    print("\n=== Sinks 示例 ===")
    for method_sig, _ in sorted(sinks)[:5]:
        print(f"  {method_sig}")

    print("\n" + "=" * 70)
    print("合并完成!")
    print("=" * 70)


if __name__ == '__main__':
    main()
