#!/usr/bin/env python3
"""
精确对比 FlowDroid 和 TaintBench 的检测结果
通过 IR 语句直接匹配
"""
import json
import xml.etree.ElementTree as ET


def main():
    tb_file = 'tmp/backflash_findings.json'
    fd_file = 'tmp/backflash_results.xml'

    # 加载 TaintBench
    with open(tb_file, 'r', encoding='utf-8') as f:
        tb_data = json.load(f)

    tb_positive = [f for f in tb_data['findings'] if not f['isNegative']]

    # 加载 FlowDroid
    tree = ET.parse(fd_file)
    root = tree.getroot()

    # 收集 FlowDroid 检测到的所有 source 和 sink
    fd_sources = set()
    fd_sinks = set()

    for result in root.findall('.//Result'):
        sink = result.find('Sink')
        fd_sinks.add(sink.get('MethodSourceSinkDefinition'))

        sources = result.find('Sources')
        for source in sources.findall('Source'):
            fd_sources.add(source.get('MethodSourceSinkDefinition'))

    print("=" * 100)
    print("TaintBench vs FlowDroid 精确对比")
    print("=" * 100)

    print(f"\n【总体统计】")
    print(f"FlowDroid 检测到的唯一 source: {len(fd_sources)}")
    print(f"FlowDroid 检测到的唯一 sink: {len(fd_sinks)}")

    # 逐个检查 TaintBench 的 positive findings
    print(f"\n【TaintBench 预期的 {len(tb_positive)} 个真实泄露】\n")

    detected = 0
    for finding in tb_positive:
        source_ir = finding['source']['IRs'][0]['IRstatement'] if finding['source']['IRs'] else None
        sink_ir = finding['sink']['IRs'][0]['IRstatement'] if finding['sink']['IRs'] else None

        # 提取方法签名
        if '<' in source_ir and '>' in source_ir:
            source_sig = source_ir[source_ir.find('<'):source_ir.rfind('>')+1]
        else:
            source_sig = source_ir

        if '<' in sink_ir and '>' in sink_ir:
            sink_sig = sink_ir[sink_ir.find('<'):sink_ir.rfind('>')+1]
        else:
            sink_sig = sink_ir

        # 检查是否被检测到
        source_found = source_sig in fd_sources
        sink_found = sink_sig in fd_sinks

        # 同时检查 source 和 sink 是否在同一个结果中
        flow_found = False
        for result in root.findall('.//Result'):
            sink = result.find('Sink')
            if sink.get('MethodSourceSinkDefinition') == sink_sig:
                sources = result.find('Sources')
                for source in sources.findall('Source'):
                    if source.get('MethodSourceSinkDefinition') == source_sig:
                        flow_found = True
                        break
            if flow_found:
                break

        if flow_found:
            detected += 1
            status = "✓ 检测到"
        elif source_found and sink_found:
            status = "△ 部分 (source 和 sink 都检测到，但可能不在同一流中)"
        else:
            status = "✗ 未检测"

        print(f"【Finding {finding['ID']}】 {status}")
        print(f"  {finding['description']}")
        print(f"  Source: {finding['source']['statement']}")
        print(f"    IR: {source_ir}")
        print(f"    签名: {source_sig}")
        print(f"    检测: {'✓' if source_found else '✗'}")
        print(f"  Sink: {finding['sink']['statement']}")
        print(f"    IR: {sink_ir}")
        print(f"    签名: {sink_sig}")
        print(f"    检测: {'✓' if sink_found else '✗'}")
        print()

    print("=" * 100)
    print(f"完整流检测率: {detected}/{len(tb_positive)} = {detected/len(tb_positive)*100:.1f}%")
    print("=" * 100)

    # 列出 FlowDroid 检测到的 Intent.getStringExtra 相关的流
    print(f"\n【FlowDroid 检测到的 Intent.getStringExtra 相关流】")
    intent_sources = [s for s in fd_sources if 'Intent' in s and 'getStringExtra' in s]
    print(f"共 {len(intent_sources)} 个不同的 Intent.getStringExtra source")

    for i, source in enumerate(sorted(intent_sources)[:10], 1):
        print(f"  {i}. {source}")
    if len(intent_sources) > 10:
        print(f"  ... 还有 {len(intent_sources) - 10} 个")


if __name__ == '__main__':
    main()
