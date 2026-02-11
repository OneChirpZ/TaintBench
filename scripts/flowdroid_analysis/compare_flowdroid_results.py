#!/usr/bin/env python3
"""
对比 FlowDroid 分析结果与 TaintBench 预期结果
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict


def parse_taintbench_findings(json_file):
    """解析 TaintBench 预期结果"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    findings = []
    for item in data['findings']:
        source_info = {
            'method': item['source']['methodName'],
            'class': item['source']['className'],
            'statement': item['source']['statement'],
            'ir': item['source']['IRs'][0]['IRstatement'] if item['source']['IRs'] else None,
            'is_negative': item['isNegative']
        }
        sink_info = {
            'method': item['sink']['methodName'],
            'class': item['sink']['className'],
            'statement': item['sink']['statement'],
            'ir': item['sink']['IRs'][0]['IRstatement'] if item['sink']['IRs'] else None,
        }
        findings.append({
            'id': item['ID'],
            'source': source_info,
            'sink': sink_info,
            'is_negative': item['isNegative'],
            'description': item['description']
        })
    return findings


def parse_flowdroid_results(xml_file):
    """解析 FlowDroid 结果"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    results = []
    for result in root.findall('.//Result'):
        sink_elem = result.find('Sink')
        sources_elem = result.find('Sources')

        sink_info = {
            'statement': sink_elem.get('Statement'),
            'method': sink_elem.get('Method'),
            'definition': sink_elem.get('MethodSourceSinkDefinition')
        }

        sources = []
        for source in sources_elem.findall('Source'):
            sources.append({
                'statement': source.get('Statement'),
                'method': source.get('Method'),
                'definition': source.get('MethodSourceSinkDefinition')
            })

        results.append({
            'sink': sink_info,
            'sources': sources
        })
    return results


def extract_signature(ir_statement):
    """从 IR 语句中提取方法签名"""
    # 提取 <ClassName: ReturnType method(Params)> 部分
    if '<' in ir_statement and '>' in ir_statement:
        start = ir_statement.find('<')
        end = ir_statement.rfind('>') + 1
        return ir_statement[start:end]
    return ir_statement


def compare_results(taintbench_findings, flowdroid_results):
    """对比两个结果集"""
    tb_signatures = set()
    fd_signatures = set()

    # 构建 TaintBench 的 source-sink 对
    for finding in taintbench_findings:
        if not finding['is_negative']:  # 只统计 positive flows
            source_sig = extract_signature(finding['source']['ir']) if finding['source']['ir'] else None
            sink_sig = extract_signature(finding['sink']['ir']) if finding['sink']['ir'] else None
            if source_sig and sink_sig:
                tb_signatures.add((source_sig, sink_sig))

    # 构建 FlowDroid 的 source-sink 对
    for result in flowdroid_results:
        sink_sig = result['sink']['definition']
        for source in result['sources']:
            source_sig = source['definition']
            fd_signatures.add((source_sig, sink_sig))

    return tb_signatures, fd_signatures


def main():
    tb_file = 'tmp/backflash_findings.json'
    fd_file = 'tmp/backflash_results.xml'

    print("=" * 80)
    print("TaintBench vs FlowDroid 结果对比分析")
    print("=" * 80)

    # 解析文件
    tb_findings = parse_taintbench_findings(tb_file)
    fd_results = parse_flowdroid_results(fd_file)

    # 统计
    tb_positive = [f for f in tb_findings if not f['is_negative']]
    tb_negative = [f for f in tb_findings if f['is_negative']]

    print(f"\n【TaintBench 预期结果】")
    print(f"  总发现数: {len(tb_findings)}")
    print(f"  Positive flows (真实泄露): {len(tb_positive)}")
    print(f"  Negative flows (误报): {len(tb_negative)}")

    print(f"\n【FlowDroid 检测结果】")
    print(f"  检测到的泄露: {len(fd_results)}")
    print(f"  涉及的源点总数: {sum(len(r['sources']) for r in fd_results)}")

    # 对比
    tb_sigs, fd_sigs = compare_results(tb_findings, fd_results)

    print(f"\n【Source-Sink 对对比】")
    print(f"  TaintBench unique pairs: {len(tb_sigs)}")
    print(f"  FlowDroid detected pairs: {len(fd_sigs)}")

    # 计算重叠
    overlap = tb_sigs & fd_sigs
    tb_only = tb_sigs - fd_sigs
    fd_only = fd_sigs - tb_sigs

    print(f"\n【重叠分析】")
    print(f"  双方都检测到: {len(overlap)}")
    print(f"  仅 TaintBench 有: {len(tb_only)}")
    print(f"  仅 FlowDroid 检测到: {len(fd_only)}")

    if tb_only:
        print(f"\n【TaintBench 预期但 FlowDroid 未检测到的流】")
        for i, (src, sink) in enumerate(sorted(tb_only)[:10], 1):
            print(f"  {i}. {src}")
            print(f"     → {sink}")
        if len(tb_only) > 10:
            print(f"  ... 还有 {len(tb_only) - 10} 个")

    if fd_only:
        print(f"\n【FlowDroid 检测到但 TaintBench 未列出的流】")
        for i, (src, sink) in enumerate(sorted(fd_only)[:10], 1):
            print(f"  {i}. {src}")
            print(f"     → {sink}")
        if len(fd_only) > 10:
            print(f"  ... 还有 {len(fd_only) - 10} 个")

    # 检测率
    if len(tb_sigs) > 0:
        recall = len(overlap) / len(tb_sigs) * 100
        print(f"\n【检测率】")
        print(f"  Recall (召回率): {recall:.1f}% ({len(overlap)}/{len(tb_sigs)})")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
