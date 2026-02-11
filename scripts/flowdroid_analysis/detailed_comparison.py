#!/usr/bin/env python3
"""
详细分析 FlowDroid 检测到的 TaintBench 预期泄露
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_taintbench_findings(json_file):
    """解析 TaintBench 预期结果"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    findings = []
    for item in data['findings']:
        if not item['isNegative']:  # 只关注 positive flows
            findings.append({
                'id': item['ID'],
                'source_method': item['source']['methodName'],
                'source_class': item['source']['className'],
                'source_statement': item['source']['statement'],
                'source_ir': item['source']['IRs'][0]['IRstatement'] if item['source']['IRs'] else None,
                'sink_method': item['sink']['methodName'],
                'sink_class': item['sink']['className'],
                'sink_statement': item['sink']['statement'],
                'sink_ir': item['sink']['IRs'][0]['IRstatement'] if item['sink']['IRs'] else None,
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


def extract_method_name(signature):
    """从签名中提取方法名"""
    if ': ' in signature:
        # <ClassName: ReturnType method(params)>
        sig_part = signature.split(': ')[1]
        # ReturnType method(params)
        method_part = sig_part.split('(')[0].split()[-1]
        return method_part
    return signature


def extract_class_name(signature):
    """从签名中提取类名"""
    if ': ' in signature:
        # <ClassName: ReturnType method(params)>
        class_part = signature.split(': ')[0].replace('<', '')
        return class_part
    return signature


def main():
    tb_file = 'tmp/backflash_findings.json'
    fd_file = 'tmp/backflash_results.xml'

    print("=" * 100)
    print("TaintBench 预期泄露详细分析")
    print("=" * 100)

    # 解析文件
    tb_findings = parse_taintbench_findings(tb_file)
    fd_results = parse_flowdroid_results(fd_file)

    # 构建 FlowDroid 的 source-sink 映射
    fd_sink_sources = defaultdict(list)
    for result in fd_results:
        sink_def = result['sink']['definition']
        sink_method = extract_method_name(sink_def)
        sink_class = extract_class_name(sink_def)
        for source in result['sources']:
            source_def = source['definition']
            fd_sink_sources[(sink_class, sink_method)].append({
                'source_def': source_def,
                'source_method': extract_method_name(source_def),
                'source_class': extract_class_name(source_def)
            })

    print(f"\nTaintBench 预期的 {len(tb_findings)} 个真实泄露:\n")

    detected_count = 0
    for finding in tb_findings:
        # 检查是否被检测到
        sink_class = finding['sink_class']
        sink_method = finding['sink_method'].split('.')[-1]  # 获取简单方法名

        source_class = finding['source_class']
        source_method = finding['source_statement'].split('(')[0].split()[-1]

        # 查找 FlowDroid 是否检测到类似的流
        is_detected = False
        matched_fds = []

        for (fd_sink_class, fd_sink_method), sources in fd_sink_sources.items():
            if sink_method in fd_sink_method or fd_sink_method in sink_method:
                for source in sources:
                    if source_method in source['source_method'] or source['source_method'] in source_method:
                        is_detected = True
                        matched_fds.append({
                            'sink': f"{fd_sink_class}.{fd_sink_method}",
                            'source': f"{source['source_class']}.{source['source_method']}"
                        })

        if is_detected:
            detected_count += 1
            status = "✓ 已检测"
        else:
            status = "✗ 未检测"

        print(f"【Finding {finding['id']}】 {status}")
        print(f"  描述: {finding['description']}")
        print(f"  Source: {finding['source_statement']}")
        print(f"    类: {finding['source_class']}")
        print(f"  Sink: {finding['sink_statement']}")
        print(f"    类: {finding['sink_class']}")

        if matched_fds:
            print(f"  匹配的 FlowDroid 检测:")
            for match in matched_fds[:3]:  # 只显示前 3 个
                print(f"    - {match['source']} → {match['sink']}")
        print()

    print("=" * 100)
    print(f"检测率: {detected_count}/{len(tb_findings)} = {detected_count/len(tb_findings)*100:.1f}%")
    print("=" * 100)


if __name__ == '__main__':
    from collections import defaultdict
    main()
