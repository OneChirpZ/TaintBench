#!/usr/bin/env python3
"""
合并多个 Source/Sink 列表并去重，生成统一的 LDFA_SourcesAndSinks.txt
"""

import re
from pathlib import Path
from typing import Set, Tuple, List


def parse_jimple_line(line: str) -> Tuple[str, str, str]:
    """
    解析 Jimple 格式的行：
    <android.telephony.TelephonyManager: java.lang.String getDeviceId()> -> _SOURCE_
    返回: (方法签名, 类别, 标注)
    """
    line = line.strip()
    if not line or line.startswith('%') or line.startswith('#'):
        return None, None, None

    # 匹配 Jimple 格式
    match = re.match(r'<([^:]+:\s*[^>]+)>(.*?)->\s*(SOURCE|SINK)', line)
    if match:
        method_sig = match.group(1).strip()
        extra_info = match.group(2).strip()
        category = match.group(3).strip()
        return method_sig, category, extra_info

    return None, None, None


def parse_smali_line(line: str) -> Tuple[str, str, str]:
    """
    解析 Smali 格式的行：
    Landroid/telephony/TelephonyManager;.getDeviceId:()Ljava/lang/String; -> _SOURCE_
    转换为 Jimple 格式
    """
    line = line.strip()
    if not line or line.startswith('%') or line.startswith('#'):
        return None, None, None

    # 移除额外的标签（如 SENSITIVE_INFO, INTERNET 等）
    parts = line.split('->')
    if len(parts) < 2:
        return None, None, None

    method_part = parts[0].strip()
    category_part = parts[1].strip()

    # 提取类别
    category = '_SOURCE_' if 'SOURCE' in category_part.upper() else '_SINK_'

    # 转换 Smali 到 Jimple
    # Landroid/telephony/TelephonyManager;.getDeviceId:()Ljava/lang/String;
    # -> <android.telephony.TelephonyManager: java.lang.String getDeviceId()>

    # 移除开头的 L 和结尾的 ;
    method_part = method_part.strip('L;')

    # 分割类名和方法
    match = re.match(r'([^;]+)\.([^(]+)\(([^)]*)\)(.+)', method_part)
    if not match:
        return None, None, None

    class_name = match.group(1).replace('/', '.')
    method_name = match.group(2)
    params = match.group(3)
    return_type = match.group(4)

    # 转换参数类型
    def convert_type(t: str) -> str:
        t = t.strip()
        if not t:
            return 'void'

        # 数组类型
        if t.startswith('['):
            base_type = convert_type(t[1:])
            return base_type + '[]'

        # 基本类型
        type_map = {
            'Z': 'boolean',
            'B': 'byte',
            'S': 'short',
            'I': 'int',
            'J': 'long',
            'F': 'float',
            'D': 'double',
            'V': 'void'
        }

        if t in type_map:
            return type_map[t]

        # 对象类型 Ljava/lang/String; -> java.lang.String
        if t.startswith('L') and t.endswith(';'):
            return t[1:-1].replace('/', '.')

        return t

    # 处理参数列表
    if params:
        param_list = []
        i = 0
        while i < len(params):
            if params[i] == '[':
                # 数组类型
                j = i
                while j < len(params) and params[j] == '[':
                    j += 1
                base_type = convert_type(params[j:j+1] if params[j] in 'ZBSIJFDV' else params[j:params.index(';', j)+1])
                param_list.append(base_type + ('[]' * (j - i)))
                i = params.index(';', j) + 1 if params[j] not in 'ZBSIJFDV' else j + 1
            elif params[i] in 'ZBSIJFDV':
                param_list.append(convert_type(params[i]))
                i += 1
            elif params[i] == 'L':
                semicolon = params.index(';', i)
                param_list.append(convert_type(params[i:semicolon+1]))
                i = semicolon + 1
            else:
                i += 1

        param_str = ','.join(param_list)
    else:
        param_str = ''

    # 构造 Jimple 格式
    jimple_sig = f'<{class_name}: {convert_type(return_type)} {method_name}({param_str})>'

    return jimple_sig, category, ''


def read_sources_sinks(file_path: Path) -> Set[Tuple[str, str]]:
    """
    读取 source/sink 文件，返回 (方法签名, 类别) 的集合
    """
    sources_sinks = set()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # 尝试 Jimple 格式
            method_sig, category, _ = parse_jimple_line(line)
            if method_sig:
                sources_sinks.add((method_sig, category))
                continue

            # 尝试 Smali 格式
            method_sig, category, _ = parse_smali_line(line)
            if method_sig:
                sources_sinks.add((method_sig, category))

    return sources_sinks


def merge_sources_sinks(files: List[Path]) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    """
    合并多个文件中的 sources 和 sinks
    返回: (sources_set, sinks_set)
    """
    all_sources = set()
    all_sinks = set()

    for file_path in files:
        print(f"处理文件: {file_path.name}")
        sources_sinks = read_sources_sinks(file_path)

        for method_sig, category in sources_sinks:
            if 'SOURCE' in category.upper():
                all_sources.add((method_sig, category))
            elif 'SINK' in category.upper():
                all_sinks.add((method_sig, category))

    return all_sources, all_sinks


def write_ldfa_sources_sinks(
    sources: Set[Tuple[str, str]],
    sinks: Set[Tuple[str, str]],
    output_path: Path
):
    """
    写入 LDFA_SourcesAndSinks.txt 文件
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入文件头
        f.write("# LDFA Source and Sink List\n")
        f.write("# 合并自: TB, AD, DB, FD 四个分类列表\n")
        f.write("# 格式: <类名: 返回类型 方法名(参数类型)> -> _SOURCE_ 或 _SINK_\n")
        f.write("#\n")

        # 写入 Sources
        f.write("\n# ==================== Sources ====================\n\n")
        for method_sig, category in sorted(sources, key=lambda x: x[0]):
            f.write(f"{method_sig} -> {category}\n")

        # 写入分隔符
        f.write("\n\n")

        # 写入 Sinks
        f.write("# ==================== Sinks ====================\n\n")
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

    # 检查文件是否存在
    for file_path in input_files:
        if not file_path.exists():
            print(f"警告: 文件不存在 {file_path}")

    # 合并 sources 和 sinks
    print("开始合并 Source/Sink 列表...")
    sources, sinks = merge_sources_sinks(input_files)

    print(f"\n统计结果:")
    print(f"  唯一 Sources: {len(sources)}")
    print(f"  唯一 Sinks: {len(sinks)}")
    print(f"  总计: {len(sources) + len(sinks)}")

    # 写入输出文件
    output_path = base_dir / 'LDFA_SourcesAndSinks.txt'
    write_ldfa_sources_sinks(sources, sinks, output_path)

    print(f"\n已生成: {output_path}")
    print(f"文件大小: {output_path.stat().st_size / 1024:.2f} KB")

    # 显示一些示例
    print("\n=== Sources 示例 (前 5 个) ===")
    for i, (method_sig, _) in enumerate(sorted(sources)[:5]):
        print(f"  {method_sig}")

    print("\n=== Sinks 示例 (前 5 个) ===")
    for i, (method_sig, _) in enumerate(sorted(sinks)[:5]):
        print(f"  {method_sig}")


if __name__ == '__main__':
    main()
