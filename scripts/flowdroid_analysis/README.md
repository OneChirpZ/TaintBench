# FlowDroid 分析脚本

本目录包含用于对比 FlowDroid 分析结果与 TaintBench 预期结果的脚本。

## 脚本说明

### compare_flowdroid_results.py

对比 FlowDroid 分析结果与 TaintBench 预期结果，统计检测率和重叠情况。

**功能**：
- 解析 TaintBench findings JSON 文件
- 解析 FlowDroid XML 结果文件
- 提取 source-sink 对并对比
- 计算召回率（Recall）

**使用方法**：
```bash
python3 compare_flowdroid_results.py
```

**输入文件**：
- `tmp/2026-02-11-flowdroid-comparison/backflash_findings.json`
- `tmp/2026-02-11-flowdroid-comparison/backflash_results.xml`

**输出**：
- 控制台打印对比统计结果

---

### detailed_comparison.py

详细分析每个 TaintBench finding 是否被 FlowDroid 检测到。

**功能**：
- 逐个检查 TaintBench 的 positive flows
- 匹配 FlowDroid 检测到的对应流
- 显示详细的 source/sink 信息

**使用方法**：
```bash
python3 detailed_comparison.py
```

**输出**：
- 每个 finding 的检测状态
- 匹配的 FlowDroid 流详情

---

### precise_comparison.py

精确对比，通过 IR 语句直接匹配验证检测率。

**功能**：
- 从 IR 语句中提取方法签名
- 检查 source 和 sink 是否在同一个污点流中
- 提供最准确的检测率统计

**使用方法**：
```bash
python3 precise_comparison.py
```

**输出**：
- 逐个 finding 的详细匹配信息
- 最终检测率统计
- FlowDroid 检测到的 Intent.getStringExtra 相关流

## 使用示例

### 1. 运行 FlowDroid 分析

```bash
# 在 gosec workstation 上执行
source "$HOME/.sdkman/bin/sdkman-init.sh"
java -Xmx8g -jar ~/FlowDroid/jars/soot-infoflow-cmd-2.14.1-jar-with-dependencies.jar \
  -a ~/LDFA-dataset/TaintBench/apks/backflash.apk \
  -p ~/Android/sdk/platforms \
  -s ~/LDFA-dataset/TaintBench/TB_SourcesAndSinks.txt \
  -cg CHA -ns -o /tmp/backflash_results.xml
```

### 2. 下载结果到本地

```bash
# 使用 SSH MCP 工具下载
# 下载 backflash_results.xml 和 backflash_findings.json 到 tmp/2026-02-11-flowdroid-comparison/
```

### 3. 运行对比分析

```bash
cd /Users/zhangyiming/My_Documents/My_Code/LDFA-dataset
python3 TaintBench/scripts/flowdroid_analysis/precise_comparison.py
```

## 依赖要求

- Python 3.6+
- 标准库：json, xml.etree.ElementTree, collections, pathlib

## 分析结果示例

使用 `TB_SourcesAndSinks.txt` 在 backflash.apk 上的分析结果：

- **TaintBench 预期**: 13 个 positive flows
- **FlowDroid 检测**: 31 个泄露
- **检测率**: 100% (13/13)
- **执行时间**: 1.58 秒
- **内存消耗**: 峰值 267 MB

## 注意事项

1. 确保 XML 和 JSON 文件路径正确
2. 文件应放在 `tmp/2026-02-11-flowdroid-comparison/` 目录
3. 对比时只考虑 TaintBench 的 positive flows (isNegative: false)

## 维护说明

如需添加新的对比脚本：
1. 将脚本放入本目录
2. 更新本 README 说明文件用途
3. 遵循现有命名规范（小写字母和下划线）
4. 提供清晰的输出格式

---

最后更新：2026-02-11
