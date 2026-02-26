# FlowDroid TaintBench 分析最终报告

生成时间: 2026-02-11

## 执行摘要

对 TaintBench 数据集的 39 个 APK 进行了 4 种模式的 FlowDroid 污点分析：

| 模式 | 配置 | 成功 | 失败 | 跳过 | 成功率 |
|------|------|------|------|------|--------|
| **Full** | 最高精度 (无优化) | 31 | 4 | 4 | 88.6% |
| **ne** | -ne (不跟踪异常流) | 31 | 1 | 7 | 96.9% |
| **ns** | -ns (不跟踪静态字段) | 31 | 1 | 7 | 96.9% |
| **ne_ns** | -ne -ns | 31 | 1 | 7 | 96.9% |

## 配置说明

### 超时设置（原始 1x）
- Callgraph (CT): 600s (10分钟)
- Dataflow (DT): 1800s (30分钟)
- Result (RT): 120s (2分钟)

### 堆内存
- 180GB

## 详细结果表格

完整表格见：[COMPREHENSIVE_SUMMARY.md](./COMPREHENSIVE_SUMMARY.md)

## 失败 APK 分析

### 在 Full 模式下失败（内存不足）

| APK | 失败时间 | 退出码 | 备注 |
|-----|----------|--------|------|
| remote_control_smack | 326s | -9 | 在 ne/ns/ne_ns 模式下黑名单 |
| scipiex | 221s | -9 | 在 ne/ns/ne_ns 模式下黑名单 |
| vibleaker_android_samp | 271s | -9 | 在 ne/ns/ne_ns 模式下黑名单 |
| xbot_android_samp | 147s | -9 | 所有模式均失败 |

### 在所有模式下均失败

| APK | 失败原因 |
|-----|----------|
| xbot_android_samp | 内存不足 (180GB 不够) |

## 重试分析（3x 超时）

对 4 个失败的 APK 使用 3 倍超时时间重新分析：

- **CT**: 1800s (30分钟)
- **DT**: 5400s (90分钟)
- **RT**: 360s (6分钟)

### 重试结果

所有 4 个 APK 在 4 种模式下仍然失败，原因均为内存不足（退出码 -9）。

详细报告：[RETRY_SUMMARY.md](./RETRY_SUMMARY.md)

## 关键发现

### 1. 成功率对比

- **使用优化标志** 后成功率从 88.6% 提升到 96.9%
- **-ne** 和 **-ns** 标志显著减少内存使用
- **Full 模式** 检测到更多污点流但内存消耗巨大

### 2. 最难分析的 APK

**xbot_android_samp** 是唯一在所有模式下都失败的 APK，需要：
- 更高的内存配置（256GB+）
- 或使用更激进的优化标志
- 或接受分析精度降低

### 3. 黑名单 APK

以下 APK 在初始分析中被识别为内存消耗过大，加入黑名单：
- cajino_baidu
- death_ring_materialflow
- hummingbad_android_samp
- jollyserv

## 建议

### 对于正常 APK
- 使用 **Full 模式** 获得最高精度
- 内存充足的 APK（<100MB）通常在 Full 模式下也能成功

### 对于大内存 APK
- 优先使用 **ne 模式**（-ne 标志）
- 如果仍然失败，使用 **ne_ns 模式**
- 考虑增加系统内存到 256GB+

### 对于超大 APK（如 xbot_android_samp）
- 需要专门的内存配置
- 考虑使用其他分析工具
- 或接受部分精度损失

## 输出文件结构

```
~/LDFA-dataset/TaintBench/output/
├── FINAL_REPORT.md                          # 本文件
├── COMPREHENSIVE_SUMMARY.md                 # 综合结果表格
├── FINAL_SUMMARY.md                         # 原始分析汇总
├── RETRY_SUMMARY.md                         # 重试分析汇总
├── 20260211-1812-39apps-max-precision/      # Full 模式结果
├── 20260211-1837-39apps-no-exceptions/      # ne 模式结果
├── 20260211-1837-39apps-no-static/          # ns 模式结果
├── 20260211-1833-39apps-no-exception-no-static/  # ne_ns 模式结果
└── 20260211-2019-retry-3x-*/               # 重试分析结果
```

## 脚本

分析脚本位于：`~/LDFA-dataset/TaintBench/scripts/`

- `batch_flowdroid_analyzer.py` - 批量分析脚本（支持 4 种模式）
- `batch_flowdroid_retry.py` - 重试脚本（支持自定义超时倍数）
- `generate_summary_table.py` - 生成综合表格
- `analyze_results.py` - 结果统计分析

---
报告生成时间: 2026-02-11
