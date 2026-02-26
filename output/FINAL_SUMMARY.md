# FlowDroid TaintBench 批量分析汇总报告

## 分析配置

- **数据集**: TaintBench (39 个 APK)
- **Source/Sink**: TB_SourcesAndSinks.txt
- **Callgraph 算法**: CHA
- **堆内存**: 180g
- **超时设置**:
  - Callgraph: 600s (10分钟)
  - Dataflow: 1800s (30分钟)
  - Result: 120s (2分钟)

## 四种运行模式

### 1. Full 模式（最高精度，无优化标志）
- **输出目录**: `20260211-1812-39apps-max-precision`
- **成功**: 31
- **失败**: 4
- **失败 APK**:
  - `remote_control_smack` (326s, 退出码 -9)
  - `scipiex` (221s, 退出码 -9)
  - `vibleaker_android_samp` (271s, 退出码 -9)
  - `xbot_android_samp` (147s, 退出码 -9)

### 2. ne 模式（-ne 标志，不跟踪异常流）
- **输出目录**: `20260211-1837-39apps-no-exceptions`
- **成功**: 31
- **失败**: 0
- **备注**: 所有 APK 成功完成，包括 full 模式失败的 4 个

### 3. ns 模式（-ns 标志，不跟踪静态字段）
- **输出目录**: `20260211-1837-39apps-no-static`
- **成功**: 31
- **失败**: 1
- **失败 APK**:
  - `xbot_android_samp` (120s, 退出码 -9)

### 4. ne_ns 模式（-ne -ns 标志）
- **输出目录**: `20260211-1833-39apps-no-exception-no-static`
- **成功**: 31
- **失败**: 1
- **失败 APK**:
  - `xbot_android_samp` (131s, 退出码 -9)

## 关键发现

### 内存不足 APK（退出码 -9 = SIGKILL）
以下 APK 在 Full 模式下内存不足，但在优化模式下成功：
- `remote_control_smack`
- `scipiex`
- `vibleaker_android_samp`
- `xbot_android_samp`

### xbot_android_samp
- **最难分析的 APK**：在 Full、ns、ne_ns 三种模式下均失败
- 仅在 ne 模式下成功
- 失败时间：120-147 秒
- 可能需要同时使用 -ne 和 -ns 标志才能成功

### sms_google.apk
- **ne 模式下最耗时**：1441 秒（24 分钟）
- 数据流分析时间：710 秒（12 分钟）
- Full 模式下：246 秒

## 文件结构

```
~/LDFA-dataset/TaintBench/output/
├── 20260211-1812-39apps-max-precision/         # Full 模式
│   ├── results_summary.csv
│   ├── analysis_summary.log
│   └── *.xml / *.log
├── 20260211-1837-39apps-no-exceptions/         # ne 模式
│   ├── results_summary.csv
│   ├── analysis_summary.log
│   └── *.xml / *.log
├── 20260211-1837-39apps-no-static/             # ns 模式
│   ├── results_summary.csv
│   ├── analysis_summary.log
│   └── *.xml / *.log
└── 20260211-1833-39apps-no-exception-no-static/ # ne_ns 模式
    ├── results_summary.csv
    ├── analysis_summary.log
    └── *.xml / *.log
```

## 脚本位置

批量分析脚本：`~/LDFA-dataset/TaintBench/scripts/batch_flowdroid_analyzer.py`

使用方法：
```bash
# Full 模式
python3 batch_flowdroid_analyzer.py --mode full --blacklist apk1 apk2

# ne 模式
python3 batch_flowdroid_analyzer.py --mode ne --blacklist apk1 apk2

# ns 模式
python3 batch_flowdroid_analyzer.py --mode ns --blacklist apk1 apk2

# ne_ns 模式
python3 batch_flowdroid_analyzer.py --mode ne_ns --blacklist apk1 apk2
```

## 建议

1. 对于大内存 APK（如 xbot_android_samp），建议使用 ne 模式
2. 对于普通 APK，Full 模式提供最高精度
3. ns 模式大幅减少内存使用，适合快速扫描
4. ne 模式在精度和性能间取得平衡

---
生成时间: 2026-02-11
