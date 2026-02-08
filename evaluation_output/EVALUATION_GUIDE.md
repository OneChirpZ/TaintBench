# TaintBench 测试用例评估指南

本指南说明如何使用从 TaintBench 数据集提取的测试用例来评估 LDFA 框架。

## 📊 数据集概览

### 核心统计

- **总测试用例**: 249 个
- **正样本（预期流）**: 203 个
- **负样本（非预期流）**: 46 个
- **涉及应用**: 39 个真实恶意软件
- **唯一源点**: 143 个
- **唯一汇点**: 109 个

### 为什么 TaintBench 适合评估 LDFA？

**优势**:
1. ✅ **真实场景**: 来自真实恶意软件，反映实际攻击模式
2. ✅ **多样性**: 涵盖多种恶意行为（SMS 泄露、位置追踪、数据窃取等）
3. ✅ **Ground Truth**: 每个用例都有精确的源点-汇点标注
4. ✅ **代码规模**: 中等规模（几十到几百个类），适合实际评估

**挑战**:
1. ⚠️ **复杂性**: 真实恶意软件包含混淆、反射等复杂技术
2. ⚠️ **多跳流**: 部分污点流跨越多个方法/类
3. ⚠️ **ICC 通信**: 部分流涉及组件间通信

## 📁 生成的文件

```
evaluation_output/
├── taintbench_test_cases.json  # 完整测试用例（LDFA 格式）
├── taintbench_analysis.md      # 统计分析报告
└── taintbench_simple_cases.csv # 简化用例列表
```

## 🎯 测试用例格式

每个测试用例包含以下字段：

```json
{
  "app_name": "save_me",
  "poi": {
    "method": "完整方法签名",
    "line": 源点行号,
    "target": "调用的 API 方法名"
  },
  "expected_sinks": [
    {
      "class": "汇点类名",
      "method": "完整方法签名",
      "line": 汇点行号,
      "target": "调用的 API 方法名"
    }
  ],
  "is_negative": false,  // 是否为负样本（不应该存在的流）
  "description": "污点流描述"
}
```

## 🔧 如何使用测试用例

### 方法 1: 直接运行 LDFA

```python
import json

# 加载测试用例
with open('taintbench_test_cases.json', 'r') as f:
    test_cases = json.load(f)

# 运行单个测试用例
case = test_cases[0]

# 构造 LDFA 查询
query = f"""
从 {case['poi']['method']} 的第 {case['poi']['line']} 行
({case['poi']['target']}) 追踪数据流到网络接口
"""

# 执行分析
result = ldfa_main.run(
    query=query,
    target_repo=f"TaintBenchRepos/{case['app_name']}"
)

# 评估结果
expected_sinks = [s['target'] for s in case['expected_sinks']]
actual_sinks = extract_sinks_from_result(result)

# 计算准确率
precision = calculate_precision(actual_sinks, expected_sinks)
recall = calculate_recall(actual_sinks, expected_sinks)
```

### 方法 2: 批量评估脚本

```python
def evaluate_ldfa_on_taintbench(test_cases, max_cases=10):
    """批量评估 LDFA 在 TaintBench 上的表现"""
    results = []

    for case in test_cases[:max_cases]:
        # 运行 LDFA
        result = run_ldfa(case)

        # 评估结果
        metrics = {
            'app_name': case['app_name'],
            'flow_id': case['flow_id'],
            'is_negative': case['is_negative'],
            'found_expected': check_expected_sinks(result, case),
            'false_positives': count_false_positives(result, case),
            'execution_time': result['time']
        }
        results.append(metrics)

    # 计算总体指标
    return compute_overall_metrics(results)
```

## 📈 评估指标

### 1. 精确度（Precision）

```python
precision = TP / (TP + FP)
```

- **TP (True Positive)**: 正确识别的预期污点流
- **FP (False Positive)**: 误报的非预期流

### 2. 召回率（Recall）

```python
recall = TP / (TP + FN)
```

- **FN (False Negative)**: 遗漏的预期流

### 3. F1-Score

```python
f1 = 2 * (precision * recall) / (precision + recall)
```

### 4. 负样本准确率

正确识别并拒绝负样本的比例

## 🎯 推荐的评估策略

### 阶段 1: 小规模验证（5-10 个用例）

**目标**: 验证 LDFA 基本功能

**推荐用例**:
1. `chulia` - 最简单的应用（4 个流，单类）
2. `dsencrypt_samp` - 单个流，验证端到端流程
3. `the_interview_movieshow` - 简单的单流用例
4. `repane` - 基础数据流
5. `jollyserv` - 简单网络泄露

**预期**: 至少识别出 60% 的预期流，无严重误报

### 阶段 2: 中等规模测试（20-30 个用例）

**目标**: 测试不同类型的污点流

**覆盖类别**:
- SMS 泄露（sms_google, samsapo）
- 位置信息（save_me, remote_control_smack）
- 文件操作（proxy_samp）
- 网络通信（chat_hook, fakemart）

**预期**:
- 召回率 > 50%
- 精确度 > 70%

### 阶段 3: 完整评估（所有 249 个用例）

**目标**: 全面评估 LDFA 性能

**分析维度**:
- 按应用规模分析（小/中/大型应用）
- 按污点流长度分析（单跳/多跳）
- 按源点类型分析（SMS/Location/File/Database）
- 负样本误报率

## 📋 快速开始示例

### 1. 选择代表性用例

```bash
cd tools/
python extract_test_cases.py --select-representative --max-cases-per-app 3
```

这将生成约 117 个测试用例（39 个应用 × 3 个用例）

### 2. 查看应用分布

```bash
# 查看复杂度较低的应用（适合初测）
ls -lh TaintBenchRepos/ | grep -E "chulia|dsencrypt|repane|jollyserv"

# 查看中等复杂度应用
ls -lh TaintBenchRepos/ | grep -E "sms_google|fakemart|fakeplay"
```

### 3. 运行单个测试

```bash
# 假设要测试 chulia 应用
python ../ldfa_main.py \
  --query "追踪从 getContentResolver().query() 到网络接口的数据流" \
  --target-repo TaintBenchRepos/chulia \
  --poi-style "line$\"42\""
```

### 4. 批量评估

创建评估脚本 `evaluate_taintbench.py`:

```python
import json
from pathlib import Path

def run_evaluation(test_cases_file='taintbench_test_cases.json'):
    with open(test_cases_file) as f:
        cases = json.load(f)

    results = []
    for case in cases[:10]:  # 先测试 10 个
        print(f"测试 {case['app_name']} - Flow #{case.get('flow_id')}")

        # 构造查询
        poi = case['poi']
        query = f"追踪数据流从 {poi['method']} (行 {poi['line']})"

        # 运行 LDFA（伪代码）
        result = run_ldfa(query, case['app_name'])

        # 比对结果
        expected = case['expected_sinks']
        actual = extract_sinks(result)

        metrics = {
            'app': case['app_name'],
            'expected_count': len(expected),
            'actual_count': len(actual),
            'matched': len(match_sinks(expected, actual)),
            'is_negative': case['is_negative']
        }
        results.append(metrics)

    return results

if __name__ == '__main__':
    results = run_evaluation()
    print_results(results)
```

## 🔍 分析技巧

### 1. 按源点类型筛选

```python
# SMS 相关源点
sms_cases = [c for c in cases if 'sms' in c['poi']['method'].lower()]

# 位置相关源点
location_cases = [c for c in cases if 'location' in c['description'].lower()]
```

### 2. 按流长度筛选

```python
# 单跳流（源点和汇点在同一方法）
simple_cases = [c for c in cases
                if c['poi']['method'] == c['expected_sinks'][0]['method']]

# 跨方法流
cross_method_cases = [c for c in cases
                      if c['poi']['method'] != c['expected_sinks'][0]['method']]
```

### 3. 按应用规模筛选

```python
# 小应用（< 20 个类）
small_apps = ['chulia', 'dsencrypt_samp', 'repane', 'jollyserv']
small_cases = [c for c in cases if c['app_name'] in small_apps]
```

## 📊 报告生成

评估完成后，生成报告：

```python
def generate_report(results, output_file='evaluation_report.md'):
    with open(output_file, 'w') as f:
        f.write("# LDFA 在 TaintBench 上的评估结果\n\n")

        f.write("## 总体指标\n\n")
        f.write(f"- **测试用例数**: {len(results)}\n")
        f.write(f"- **精确度**: {compute_precision(results):.2%}\n")
        f.write(f"- **召回率**: {compute_recall(results):.2%}\n")
        f.write(f"- **F1-Score**: {compute_f1(results):.2%}\n\n")

        f.write("## 按应用详细结果\n\n")
        for result in results:
            f.write(f"### {result['app_name']}\n")
            f.write(f"- 预期: {result['expected_count']}\n")
            f.write(f"- 实际: {result['actual_count']}\n")
            f.write(f"- 匹配: {result['matched']}\n\n")
```

## 🚨 常见问题

### Q1: merged_sources.txt 有 19655 个源点，是否都需要支持？

**A**: 不需要。这些是所有可能的源点定义，但实际测试用例只用了其中的 143 个。LDFA 只需支持这 143 个即可。

### Q2: 遇到 ICC 通信（Intent/BroadcastReceiver）怎么办？

**A**: 这是 TaintBench 的难点之一。建议：
- 阶段 1-2：跳过包含 ICC 的用例
- 阶段 3：测试 LDFA 的 CodeRecall 机制处理 ICC 的能力

### Q3: 如何处理负样本？

**A**: 负样本不应该存在污点流。如果 LDFA 报告发现了流，则为误报（False Positive）。

### Q4: 可以只测试部分应用吗？

**A**: 完全可以。建议从简单应用开始，逐步增加复杂度。

## 📚 参考资源

- TaintBench 论文: ISSTA 2022
- TaintBench 网站: https://taintbench.github.io/
- LDFA 文档: `docs/` 目录

## 🎓 预期结果基准

根据 TaintBench 论文，主流工具的性能：

| 工具 | Recall | Precision |
|------|--------|-----------|
| FlowDroid | 52.2% | 62.5% |
| IccTA | 58.1% | 68.2% |
| DroidSafe | 65.3% | 71.4% |

**LDFA 目标**:
- 阶段 1: Recall > 30%, Precision > 50%
- 阶段 2: Recall > 50%, Precision > 70%
- 阶段 3: Recall > 60%, Precision > 75%

---

**提示**: 开始评估前，建议先手动分析 2-3 个简单用例，理解污点流的实际路径，再进行自动化评估。
