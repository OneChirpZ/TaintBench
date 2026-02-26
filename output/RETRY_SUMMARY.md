# FlowDroid 失败 APK 重试分析汇总报告

## 重试配置

- **超时时间倍数**: 3x
- **具体超时设置**:
  - Callgraph: 1800s (30分钟)
  - Dataflow: 5400s (90分钟) 
  - Result: 360s (6分钟)
- **堆内存**: 180g

## 重试的 APK 列表

1. `remote_control_smack`
2. `scipiex`
3. `vibleaker_android_samp`
4. `xbot_android_samp`

## 重试结果

### Full 模式 (3x 超时)
**输出目录**: `20260211-2019-retry-3x-max-precision`

| APK | 状态 | 时间(秒) | 退出码 | 原因 |
|-----|------|----------|--------|------|
| remote_control_smack | FAILED | 209.99 | -9 | 内存不足(SIGKILL) |
| scipiex | FAILED | 241.74 | -9 | 内存不足(SIGKILL) |
| vibleaker_android_samp | FAILED | 260.81 | -9 | 内存不足(SIGKILL) |
| xbot_android_samp | FAILED | 220.05 | -9 | 内存不足(SIGKILL) |

### ne 模式 (3x 超时)
**输出目录**: `20260211-2019-retry-3x-no-exceptions`

| APK | 状态 | 时间(秒) | 退出码 | 原因 |
|-----|------|----------|--------|------|
| remote_control_smack | FAILED | 113.09 | -9 | 内存不足(SIGKILL) |
| scipiex | FAILED | 173.53 | -9 | 内存不足(SIGKILL) |
| vibleaker_android_samp | FAILED | 259.38 | -9 | 内存不足(SIGKILL) |
| xbot_android_samp | FAILED | 121.67 | -9 | 内存不足(SIGKILL) |

### ns 模式 (3x 超时)
**输出目录**: `20260211-2019-retry-3x-no-static`

| APK | 状态 | 时间(秒) | 退出码 | 原因 |
|-----|------|----------|--------|------|
| remote_control_smack | FAILED | 136.14 | -9 | 内存不足(SIGKILL) |
| scipiex | FAILED | 110.65 | -9 | 内存不足(SIGKILL) |
| vibleaker_android_samp | FAILED | 257.36 | -9 | 内存不足(SIGKILL) |
| xbot_android_samp | FAILED | 89.01 | -9 | 内存不足(SIGKILL) |

### ne_ns 模式 (3x 超时)
**输出目录**: `20260211-2019-retry-3x-no-exception-no-static`

| APK | 状态 | 时间(秒) | 退出码 | 原因 |
|-----|------|----------|--------|------|
| remote_control_smack | FAILED | 170.91 | -9 | 内存不足(SIGKILL) |
| scipiex | FAILED | 177.76 | -9 | 内存不足(SIGKILL) |
| vibleaker_android_samp | FAILED | 279.77 | -9 | 内存不足(SIGKILL) |
| xbot_android_samp | FAILED | 148.50 | -9 | 内存不足(SIGKILL) |

## 结论

### 失败原因分析

所有 4 个 APK 在 4 种模式下均失败，退出码均为 **-9 (SIGKILL)**，表明：

1. **不是超时问题**: 失败时间范围 89-279 秒，远低于 90 分钟超时设置
2. **是内存问题**: 被系统 OOM killer 杀死
3. **180GB 内存不足**: 这些 APK 需要更多内存才能成功分析

### 最难分析的 APK (按失败时间排序)

1. **vibleaker_android_samp**: 在 4 种模式下均运行最久 (257-280 秒)
2. **scipiex**: 相对稳定 (110-241 秒)
3. **remote_control_smack**: 相对稳定 (113-209 秒)
4. **xbot_android_samp**: 在 ne_ns 模式下最快失败 (89 秒)

### 建议

由于 180GB 内存仍不足，建议：

1. **增加内存**: 尝试 256GB 或更高内存配置
2. **单独分析**: 对这些 APK 使用更高内存单独分析
3. **分批分析**: 一次只分析一个 APK，避免内存竞争
4. **使用 -ns 标志**: 虽然不能解决根本问题，但可以减少内存使用

## 输出目录

```
~/LDFA-dataset/TaintBench/output/
├── 20260211-2019-retry-3x-max-precision/              # Full 模式
│   ├── results_summary.csv
│   ├── analysis_summary.log
│   └── *.log / *.xml
├── 20260211-2019-retry-3x-no-exceptions/              # ne 模式
│   ├── results_summary.csv
│   ├── analysis_summary.log
│   └── *.log / *.xml
├── 20260211-2019-retry-3x-no-static/                  # ns 模式
│   ├── results_summary.csv
│   ├── analysis_summary.log
│   └── *.log / *.xml
└── 20260211-2019-retry-3x-no-exception-no-static/     # ne_ns 模式
    ├── results_summary.csv
    ├── analysis_summary.log
    └── *.log / *.xml
```

---
生成时间: 2026-02-11
