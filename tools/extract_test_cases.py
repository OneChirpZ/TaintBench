#!/usr/bin/env python3
"""从 TaintBench 数据集提取适合 LDFA 评估的测试用例"""

import json
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class TestCase:
    """简化的测试用例"""
    app_name: str
    source_class: str
    source_method: str
    source_line: int
    source_target: str
    sink_class: str
    sink_method: str
    sink_line: int
    sink_target: str
    is_negative: bool
    flow_id: int
    description: str = ""

    def to_ldfa_format(self) -> dict:
        """转换为 LDFA 查询格式"""
        return {
            "app_name": self.app_name,
            "poi": {
                "method": f"{self.source_class}.{self.source_method}",
                "line": self.source_line,
                "target": self.source_target
            },
            "expected_sinks": [
                {
                    "class": self.sink_class,
                    "method": self.sink_method,
                    "line": self.sink_line,
                    "target": self.sink_target
                }
            ],
            "is_negative": self.is_negative,
            "description": self.description
        }


def extract_test_cases(repos_dir: Path) -> List[TestCase]:
    """从所有 TaintBench 样本中提取测试用例"""
    test_cases = []

    for repo_dir in repos_dir.iterdir():
        if not repo_dir.is_dir():
            continue

        findings_file = repo_dir / f"{repo_dir.name}_findings.json"
        if not findings_file.exists():
            print(f"警告: 未找到 findings 文件: {findings_file}")
            continue

        with open(findings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for finding in data.get('findings', []):
            source = finding.get('source', {})
            sink = finding.get('sink', {})

            test_case = TestCase(
                app_name=repo_dir.name,
                source_class=source.get('className', ''),
                source_method=source.get('methodName', ''),
                source_line=source.get('lineNo', 0),
                source_target=source.get('targetName', ''),
                sink_class=sink.get('className', ''),
                sink_method=sink.get('methodName', ''),
                sink_line=sink.get('lineNo', 0),
                sink_target=sink.get('targetName', ''),
                is_negative=finding.get('isNegative', False),
                flow_id=finding.get('ID', 0),
                description=finding.get('description', '')
            )
            test_cases.append(test_case)

    return test_cases


def analyze_test_cases(test_cases: List[TestCase]) -> Dict:
    """分析测试用例的统计信息"""
    stats = {
        "total": len(test_cases),
        "positive": sum(1 for tc in test_cases if not tc.is_negative),
        "negative": sum(1 for tc in test_cases if tc.is_negative),
        "apps": len(set(tc.app_name for tc in test_cases)),
        "unique_sources": len(set((tc.source_class, tc.source_method, tc.source_target)
                                 for tc in test_cases)),
        "unique_sinks": len(set((tc.sink_class, tc.sink_method, tc.sink_target)
                               for tc in test_cases)),
    }

    # 按应用统计
    by_app = defaultdict(lambda: {"positive": 0, "negative": 0})
    for tc in test_cases:
        if tc.is_negative:
            by_app[tc.app_name]["negative"] += 1
        else:
            by_app[tc.app_name]["positive"] += 1

    stats["by_app"] = dict(by_app)

    return stats


def select_representative_cases(test_cases: List[TestCase],
                                 max_cases_per_app: int = 5) -> List[TestCase]:
    """选择代表性测试用例

    策略：
    1. 优先选择简单的单流程用例（non-partial）
    2. 混合正负样本
    3. 每个应用最多选择 max_cases_per_app 个
    """
    # 按应用分组
    by_app = defaultdict(list)
    for tc in test_cases:
        by_app[tc.app_name].append(tc)

    selected = []

    for app_name, cases in by_app.items():
        # 排序优先级：正样本优先，简单的优先
        def priority(tc):
            return (
                not tc.is_negative,  # 正样本优先
                tc.flow_id          # 按 ID 排序
            )

        cases.sort(key=priority)

        # 选择前 N 个
        selected.extend(cases[:max_cases_per_app])

    return selected


def generate_evaluation_report(test_cases: List[TestCase], output_dir: Path):
    """生成评估报告"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 生成 JSON 格式的测试用例
    ldfa_cases = [tc.to_ldfa_format() for tc in test_cases]
    with open(output_dir / "taintbench_test_cases.json", 'w', encoding='utf-8') as f:
        json.dump(ldfa_cases, f, ensure_ascii=False, indent=2)

    # 2. 生成统计报告
    stats = analyze_test_cases(test_cases)

    with open(output_dir / "taintbench_analysis.md", 'w', encoding='utf-8') as f:
        f.write("# TaintBench 测试用例分析报告\n\n")
        f.write("## 统计摘要\n\n")
        f.write(f"- **总测试用例数**: {stats['total']}\n")
        f.write(f"- **正样本（预期流）**: {stats['positive']}\n")
        f.write(f"- **负样本（非预期流）**: {stats['negative']}\n")
        f.write(f"- **涉及应用数**: {stats['apps']}\n")
        f.write(f"- **唯一源点数**: {stats['unique_sources']}\n")
        f.write(f"- **唯一汇点数**: {stats['unique_sinks']}\n\n")

        f.write("## 各应用测试用例分布\n\n")
        f.write("| 应用 | 正样本 | 负样本 | 总计 |\n")
        f.write("|------|--------|--------|------|\n")

        for app_name, counts in sorted(stats['by_app'].items(),
                                       key=lambda x: x[1]['positive'] + x[1]['negative'],
                                       reverse=True):
            total = counts['positive'] + counts['negative']
            f.write(f"| {app_name} | {counts['positive']} | {counts['negative']} | {total} |\n")

    # 3. 生成简化用例列表（用于快速参考）
    with open(output_dir / "taintbench_simple_cases.csv", 'w', encoding='utf-8') as f:
        f.write("app_name,source_class,source_method,source_line,sink_class,sink_method,sink_line,is_negative\n")
        for tc in test_cases:
            f.write(f"{tc.app_name},{tc.source_class},{tc.source_method},{tc.source_line},"
                   f"{tc.sink_class},{tc.sink_method},{tc.sink_line},{tc.is_negative}\n")

    print(f"报告已生成到: {output_dir}")
    print(f"- taintbench_test_cases.json: {len(ldfa_cases)} 个测试用例")
    print(f"- taintbench_analysis.md: 统计分析报告")
    print(f"- taintbench_simple_cases.csv: 简化用例列表")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="从 TaintBench 提取 LDFA 评估测试用例"
    )
    parser.add_argument(
        '--repos-dir',
        type=str,
        default='TaintBenchRepos',
        help='TaintBench 仓库目录'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='evaluation_output',
        help='输出目录'
    )
    parser.add_argument(
        '--max-cases-per-app',
        type=int,
        default=5,
        help='每个应用最多选择的测试用例数'
    )
    parser.add_argument(
        '--select-representative',
        action='store_true',
        help='是否只选择代表性测试用例'
    )

    args = parser.parse_args()

    repos_dir = Path(args.repos_dir)
    output_dir = Path(args.output_dir)

    if not repos_dir.exists():
        print(f"错误: 仓库目录不存在: {repos_dir}")
        return

    print(f"正在分析 TaintBench 数据集: {repos_dir}")
    test_cases = extract_test_cases(repos_dir)
    print(f"找到 {len(test_cases)} 个测试用例")

    if args.select_representative:
        print(f"选择代表性测试用例（每个应用最多 {args.max_cases_per_app} 个）...")
        test_cases = select_representative_cases(test_cases, args.max_cases_per_app)
        print(f"选择了 {len(test_cases)} 个代表性测试用例")

    generate_evaluation_report(test_cases, output_dir)


if __name__ == '__main__':
    main()
