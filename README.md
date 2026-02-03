# TaintBench 数据集

本目录包含 [TaintBench](https://taintbench.github.io/) 数据集的相关文件和工具。

## 目录结构

```
TaintBench/
├── README.md                     # 本文件
├── tools/                        # 数据集工具
│   ├── README.md                # 工具使用文档
│   ├── clone_repos.py           # 仓库克隆脚本
│   └── convert_html_to_json.py  # HTML 转 JSON 脚本
├── TaintBenchDataRaw.html       # 原始数据表格
├── TaintBenchDataRaw.json       # 转换后的结构化数据
├── TaintBenchApks/              # APK 文件（39 个应用）
└── TaintBenchRepos/             # Git 仓库（39 个项目）
```

## 关于 TaintBench

TaintBench 是一个用于评估 Android 污点分析工具的大规模真实世界恶意软件数据集。它包含 39 个真实世界的 Android 恶意应用，涵盖多种恶意行为模式。

**详细信息**: https://taintbench.github.io/

**论文**:
- TaintBench: An Effective and Scalable Benchmark for Evaluating Android Taint Analysis Tools
- ISSTA 2022

## 数据集内容

- **39 个恶意软件样本**: 来自不同家族的 Android 恶意应用
- **203 个预期的污点流**: 用于测试分析工具的准确性
- **46 个非预期的污点流**: 用于测试误报率
- **总计 39 个 APK 文件**: 可在 TaintBenchApks/ 目录找到
- **对应的源代码仓库**: 已克隆到 TaintBenchRepos/ 目录

## 快速开始

查看 [tools/README.md](tools/README.md) 了解如何使用工具克隆和管理数据集。

## 许可

TaintBench 数据集遵循其原始许可证。请访问 https://taintbench.github.io/ 了解详细信息。
