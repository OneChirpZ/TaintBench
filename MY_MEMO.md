# TaintBench 数据集结构说明

> 数据来源论文: TaintBench: An Effective and Scalable Benchmark for Evaluating Android Taint Analysis Tools, ISSTA 2022
>
> 官网: https://taintbench.github.io/

## 1. 概述

TaintBench 是一个用于评估 Android 污点分析工具的大规模真实世界**恶意软件**数据集，包含 39 个真实 Android 恶意应用。

### 数据集特点

- **39 个恶意软件样本**: 来自不同恶意软件家族
- **203 个预期污点流**: 恶意数据泄漏路径（应该被检测到）
- **46 个非预期污点流**: 用于测试误报
- **总计 249 条数据流**

## 2. 目录结构

```
TaintBench/
├── README.md                     # 数据集说明
├── CLAUDE.md                     # 项目配置说明
├── TaintBenchDataRaw.json        # 数据集元数据 (39 个应用信息)
├── TaintBenchDataRaw.html        # 原始 HTML 表格
├── TAF-schema.json               # TAF 格式 JSON Schema 定义
├── apks/                         # 39 个恶意软件 APK 文件
│   ├── backflash.apk
│   ├── beita_com_beita_contact.apk
│   └── ...
├── findings/                     # 污点分析结果 (TAF 格式 JSON)
│   ├── backflash_findings.json
│   ├── beita_com_beita_contact_findings.json
│   └── ... (共 39 个文件)
├── tools/                        # 数据集管理工具
│   ├── clone_repos.py            # 克隆源码仓库
│   └── convert_html_to_json.py   # HTML 转 JSON
├── scripts/                      # 相关分析脚本
├── evaluation_output/            # 评估输出结果
├── TB_SourcesAndSinks.txt        # TaintBench 专用 Source/Sink (87 行, 默认)
├── FD_SourcesAndSinks.txt        # FlowDroid 专用 (352 行)
├── AD_SourcesAndSinks.txt        # Amandroid 专用 (72 行)
├── DB_SourcesAndSinks.txt        # DroidBench 专用 (39 行)
├── merged_sources.txt            # SuSi 完整 sources (19,655 个方法)
├── merged_sinks.txt              # SuSi 完整 sinks (9,956 个方法)
└── LDFA_SourcesAndSinks.txt      # 临时文件 (不使用)
```

## 3. Findings JSON 结构 (TAF 格式)

### 完整结构示例

```json
{
  "fileName": "backflash.apk",
  "day": "2019-10-02",
  "findings": [
    {
      "ID": 1,
      "source": {
        "statement": "String BotLocation = telephonyManager.getSimCountryIso();",
        "methodName": "public void onCreate()",
        "className": "com.adobe.flashplayer_.AdobeFlashCore",
        "lineNo": 59,
        "decompiledSourceLineNo": 59,
        "targetName": "getSimCountryIso",
        "targetNo": 1,
        "IRs": [
          {
            "type": "Jimple",
            "IRstatement": "$r9 = virtualinvoke $r4.<android.telephony.TelephonyManager: java.lang.String getSimCountryIso()>()"
          }
        ]
      },
      "sink": {
        "statement": "outputStreamWriter.write(data);",
        "methodName": "private void writeConfig(String config, String data)",
        "className": "com.adobe.flashplayer_.AdobeFlashCore",
        "lineNo": 168,
        "decompiledSourceLineNo": 168,
        "targetName": "write",
        "targetNo": 1,
        "IRs": [
          {
            "type": "Jimple",
            "IRstatement": "virtualinvoke $r3.<java.io.OutputStreamWriter: void write(java.lang.String)>($r2)"
          }
        ]
      },
      "intermediateFlows": [
        {
          "statement": "writeConfig(\"BotLocation\", BotLocation);",
          "methodName": "public void onCreate()",
          "className": "com.adobe.flashplayer_.AdobeFlashCore",
          "lineNo": 80,
          "ID": 1
        }
      ],
      "attributes": {
        "lifecycle": true,
        "partialFlow": true,
        "threading": false,
        "pathConstraints": false,
        "collections": false,
        "interComponentCommunication": false,
        "array": false,
        "staticField": false,
        "nonStaticField": false,
        "callbacks": false,
        "implicitFlows": false,
        "reflection": false
      },
      "description": "This malicious flow leaks the SIM country code into an OutputStream, writing to data that is later read by following flow.",
      "isNegative": false
    }
  ]
}
```

### 字段说明

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `fileName` | string | APK 文件名 |
| `day` | string | 分析日期 |
| `findings` | array | 数据流数组 |

#### Finding 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `ID` | int | 数据流唯一标识 |
| `source` | object | 敏感数据来源 |
| `sink` | object | 数据泄露点 |
| `intermediateFlows` | array | 中间调用路径 |
| `attributes` | object | 数据流属性标签 |
| `description` | string | 数据流描述说明 |
| `isNegative` | bool | 是否为非预期流 (false=预期恶意流, true=非预期流) |

#### Source/Sink 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `statement` | string | 源码语句 |
| `methodName` | string | 所在方法名 |
| `className` | string | 所在类名 |
| `lineNo` | int | 源码行号 |
| `decompiledSourceLineNo` | int | 反编译源码行号 |
| `targetName` | string | 目标 API 方法名 |
| `targetNo` | int | 目标参数位置 |
| `IRs` | array | 中间表示 (Jimple) |

#### Attributes 字段

| 字段 | 说明 |
|------|------|
| `lifecycle` | 涉及生命周期回调 |
| `appendToString` | 字符串拼接操作 |
| `threading` | 多线程相关 |
| `pathConstraints` | 有路径约束条件 |
| `collections` | 集合操作 |
| `partialFlow` | 部分数据流 |
| `nonStaticField` | 非静态字段 |
| `interComponentCommunication` | 组件间通信 (IPC) |
| `array` | 数组操作 |
| `staticField` | 静态字段 |
| `callbacks` | 回调函数 |
| `implicitFlows` | 隐式数据流 |
| `reflection` | 反射调用 |
| `payload` | 恶意载荷 |
| `interAppCommunication` | 应用间通信 |

## 4. 数据集统计

### 总体统计

| 指标 | 数值 |
|------|------|
| 应用数量 | 39 |
| 总 Findings 数 | 249 |
| Positive (预期污点流) | 203 |
| Negative (非预期污点流) | 46 |

### Attributes 分布 (值为 true 的数量)

| Attribute | 数量 | 占比 |
|-----------|------|------|
| lifecycle | 104 | 41.8% |
| appendToString | 99 | 39.8% |
| threading | 80 | 32.1% |
| pathConstraints | 74 | 29.7% |
| collections | 67 | 26.9% |
| partialFlow | 63 | 25.3% |
| nonStaticField | 61 | 24.5% |
| interComponentCommunication | 49 | 19.7% |
| array | 39 | 15.7% |
| staticField | 31 | 12.4% |
| callbacks | 23 | 9.2% |
| implicitFlows | 6 | 2.4% |
| reflection | 5 | 2.0% |
| payload | 5 | 2.0% |
| interAppCommunication | 2 | 0.8% |

### 按应用统计 (前 10)

| 应用 | 总数 | Positive | Negative |
|------|------|----------|----------|
| save_me | 31 | 25 | 6 |
| backflash | 24 | 13 | 11 |
| proxy_samp | 20 | 17 | 3 |
| overlaylocker2_android_samp | 19 | 7 | 12 |
| remote_control_smack | 17 | 17 | 0 |
| cajino_baidu | 15 | 12 | 3 |
| chat_hook | 13 | 12 | 1 |
| sms_send_locker_qqmagic | 8 | 6 | 2 |
| roidsec | 6 | 6 | 0 |
| overlay_android_samp | 6 | 4 | 2 |

## 5. Source/Sink 配置文件

### 分类列表 (推荐使用)

| 文件 | 行数 | 用途 |
|------|------|------|
| `TB_SourcesAndSinks.txt` | 87 | **TaintBench 专用 (默认)** |
| `FD_SourcesAndSinks.txt` | 352 | FlowDroid 专用 |
| `AD_SourcesAndSinks.txt` | 72 | Amandroid 专用 |
| `DB_SourcesAndSinks.txt` | 39 | DroidBench 专用 |

### SuSi 完整数据库

| 文件 | 数量 | 说明 |
|------|------|------|
| `merged_sources.txt` | 19,655 | SuSi 数据库所有 sources |
| `merged_sinks.txt` | 9,956 | SuSi 数据库所有 sinks |

## 6. 用于评估数据流分析 Agent

### 提取评估数据的代码示例

```python
import json
import os

def extract_taintbench_findings(findings_dir):
    """提取 TaintBench 数据用于评估"""
    results = []

    for filename in os.listdir(findings_dir):
        if not filename.endswith('_findings.json'):
            continue

        filepath = os.path.join(findings_dir, filename)
        with open(filepath) as f:
            data = json.load(f)

        for finding in data.get('findings', []):
            results.append({
                'app': data['fileName'],
                'flow_id': finding['ID'],
                'is_negative': finding.get('isNegative', False),
                'source_api': finding['source']['targetName'],
                'source_class': finding['source']['className'],
                'source_method': finding['source']['methodName'],
                'source_line': finding['source']['lineNo'],
                'sink_api': finding['sink']['targetName'],
                'sink_class': finding['sink']['className'],
                'sink_method': finding['sink']['methodName'],
                'sink_line': finding['sink']['lineNo'],
                'description': finding.get('description', ''),
                'attributes': finding.get('attributes', {}),
                'intermediate_count': len(finding.get('intermediateFlows', [])),
            })

    return results

# 使用
data = extract_taintbench_findings('findings/')

# 分离 positive 和 negative
positive = [d for d in data if not d['is_negative']]  # 预期恶意流 (应被检测)
negative = [d for d in data if d['is_negative']]       # 非预期流
```

### 评估指标

| 指标 | 公式 | 说明 |
|------|------|------|
| **Recall** | TP / (TP + FN) | 203 个预期恶意流中被检测到的比例 |
| **Precision** | TP / (TP + FP) | 检测结果中真正的恶意流比例 |
| **F1-Score** | 2 * (P * R) / (P + R) | 精确率和召回率的调和平均 |

### 分类定义

| 标签 | 含义 | 用途 |
|------|------|------|
| `isNegative: false` | 预期的恶意数据流 | 应该被检测到 (True Positive 候选) |
| `isNegative: true` | 非预期的数据流 | 用于评估误报 |

### 按属性过滤测试

可根据 `attributes` 字段筛选特定类型的数据流进行针对性测试：

```python
# 测试生命周期相关的数据流
lifecycle_flows = [f for f in data if f['attributes'].get('lifecycle')]

# 测试隐式流
implicit_flows = [f for f in data if f['attributes'].get('implicitFlows')]

# 测试反射调用
reflection_flows = [f for f in data if f['attributes'].get('reflection')]
```

## 7. 注意事项

1. **数据性质**: 数据集为**恶意软件**，分析时需在隔离环境中进行
2. **APK 来源**: 原始 APK 文件位于 `apks/` 目录
3. **Source/Sink 配置**: 默认使用 `TB_SourcesAndSinks.txt`
4. **中间路径**: `intermediateFlows` 提供完整的数据流路径信息
5. **IR 表示**: `IRs` 字段包含 Jimple 中间表示，便于工具对比

---

*文档生成时间: 2026-02-25*
