# TaintBench 数据集说明

## 目录结构

```
TaintBench/
├── apks/                           # 原始数据集的 APK 文件
├── findings/                       # 各应用的 source-sink 污点流及中间路径分析结果
│   └── *_findings.json            # 每个应用对应的污点分析 findings
├── tools/                          # 下载应用代码仓库的工具（反编译得到的代码）
├── evaluation_output/              # 评估输出结果
├── scripts/                        # 相关脚本
├── TB_SourcesAndSinks.txt          # TaintBench 专用 source-sink 列表（87行，默认使用）
├── AD_SourcesAndSinks.txt          # Amandroid 工具专用（72行）
├── DB_SourcesAndSinks.txt          # DroidBench 测试集（39行）
├── FD_SourcesAndSinks.txt          # FlowDroid 工具专用（352行）
├── merged_sources.txt              # SuSi 数据库 sources（19,655 个方法签名）
├── merged_sinks.txt                # SuSi 数据库 sinks（9,956 个方法签名）
├── LDFA_SourcesAndSinks.txt        # 临时文件，暂不使用
├── TAF-schema.json                 # Taint Analysis Framework schema
└── README.md                       # TaintBench 说明文档
```

## Sources and Sinks 说明

### SuSi 数据库（完整版）

- `merged_sources.txt` 和 `merged_sinks.txt` 来自 **SuSi 数据库**（Sources and Sinks Database）
  - 超大规模 Android API 安全方法数据库
  - 包含几乎所有 Android SDK 中可能涉及敏感数据的方法
  - 共计约 30,000 个方法签名（19,655 个 sources + 9,956 个 sinks）

### 分类列表（精选子集）

| 文件 | 行数 | 用途 |
|------|------|------|
| AD_SourcesAndSinks.txt | 72 | Amandroid 工具专用 |
| DB_SourcesAndSinks.txt | 39 | DroidBench 测试集 |
| FD_SourcesAndSinks.txt | 352 | FlowDroid 工具专用 |
| TB_SourcesAndSinks.txt | 87 | TaintBench 数据集专用（**默认使用**） |

总计约 550 行

**注意：** `LDFA_SourcesAndSinks.txt` 为临时文件，除非有特殊要求，默认使用 `TB_SourcesAndSinks.txt`。

## Findings 格式

`findings/` 目录包含各应用的污点分析结果，每个应用的 JSON 文件包含：
- Source-sink 污点流路径
- 中间调用路径
- 相关的敏感数据源和汇点信息
