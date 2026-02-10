#!/usr/bin/env python3
"""
最终清理：完全标准化参数格式
"""

import re
from pathlib import Path


def fully_normalize_params(text: str) -> str:
    """完全标准化参数列表中的逗号分隔符"""
    # 找到所有参数列表并标准化
    def replace_params(match):
        prefix = match.group(1)
        params = match.group(2)
        # 移除所有逗号周围的空格
        params = params.replace(', ', ',')
        params = params.replace(' ,', ',')
        # 分割并清理每个参数
        if params:
            param_list = [p.strip() for p in params.split(',')]
            # 重新组合，统一使用 ", "
            return f"{prefix}({', '.join(param_list)})"
        else:
            return f"{prefix}()"

    # 匹配方法签名的参数部分
    return re.sub(r'(\w+\s*\()([^)]*)\)', replace_params, text)


def main():
    file_path = Path('/Users/zhangyiming/My_Documents/My_Code/LDFA-dataset/TaintBench/LDFA_SourcesAndSinks.txt')

    print("标准化参数格式...")

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 处理每一行
    cleaned_lines = []
    for line in lines:
        if line.strip() and not line.startswith('#'):
            # 标准化参数格式
            normalized = fully_normalize_params(line)
            cleaned_lines.append(normalized)
        else:
            cleaned_lines.append(line)

    # 去重（使用签名部分作为键）
    seen = set()
    unique_lines = []
    for line in cleaned_lines:
        if line.strip() and not line.startswith('#'):
            # 提取签名部分用于去重
            sig_part = line.split('->')[0].strip() if '->' in line else line.strip()
            if sig_part not in seen:
                seen.add(sig_part)
                unique_lines.append(line)
        else:
            unique_lines.append(line)

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(unique_lines)

    print(f"✓ 已标准化参数格式")
    print(f"✓ 总行数: {len(cleaned_lines)} -> {len(unique_lines)} (去重后)")

    # 验证
    print("\n验证结果:")
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if line.strip() and not line.startswith('#'):
                # 检查是否还有 ",android." 或 ",java." 的情况
                if re.search(r',(?:android|java|javax)\.', line):
                    print(f"  ⚠️  行 {i}: 仍需处理")
                    print(f"    {line.strip()[:100]}")

    print("\n完成！")


if __name__ == '__main__':
    main()
