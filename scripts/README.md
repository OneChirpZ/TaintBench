# TaintBench Source/Sink 列表处理工具

这个目录包含用于处理和验证 TaintBench Source/Sink 列表的各种工具脚本。

## 📁 脚本说明

### 1. merge_sources_sinks.py
**合并多个 Source/Sink 列表并生成统一的 LDFA_SourcesAndSinks.txt**

功能：
- 支持 Jimple 和 Smali 两种格式解析
- 合并 TB、AD、DB、FD 四个分类列表
- 自动去重并转换为标准 Jimple 格式

使用方法：
```bash
python3 scripts/merge_sources_sinks.py
```

输出：`LDFA_SourcesAndSinks.txt`

---

### 2. comprehensive_check.py
**全面检查 LDFA_SourcesAndSinks.txt 的质量和完整性**

功能：
- 检查格式一致性（Smali 残留、参数格式等）
- 验证关键方法是否包含
- 统计类型分布
- 与原始文件对比覆盖率

使用方法：
```bash
python3 scripts/comprehensive_check.py
```

---

### 3. clean_and_normalize.py
**清理和标准化参数格式**

功能：
- 去除参数格式不一致导致的重复
- 标准化参数格式（统一使用逗号+空格分隔）
- 按字母顺序排序

使用方法：
```bash
python3 scripts/clean_and_normalize.py
```

---

### 4. final_normalize.py
**最终格式标准化**

功能：
- 完全标准化参数列表中的逗号分隔符
- 处理所有特殊情况（包括构造函数）
- 去重

使用方法：
```bash
python3 scripts/final_normalize.py
```

---

### 5. check_parsing.py
**解析检查工具（调试用）**

功能：
- 检查哪些行没有被正确解析
- 显示未解析的示例
- 统计解析成功率

使用方法：
```bash
python3 scripts/check_parsing.py
```

---

## 🔄 典型工作流程

### 生成新的合并列表

```bash
# 1. 合并原始列表
python3 scripts/merge_sources_sinks.py

# 2. 清理和标准化
python3 scripts/clean_and_normalize.py
python3 scripts/final_normalize.py

# 3. 质量检查
python3 scripts/comprehensive_check.py
```

---

## 📊 文件格式

### 输入格式

**Jimple 格式：**
```
<android.telephony.TelephonyManager: java.lang.String getDeviceId()> -> _SOURCE_
```

**Smali 格式：**
```
Landroid/telephony/TelephonyManager;.getDeviceId:()Ljava/lang/String; SENSITIVE_INFO -> _SOURCE_
```

### 输出格式

**标准 Jimple 格式（统一）：**
```
android.telephony.TelephonyManager: java.lang.String getDeviceId() -> _SOURCE_
```

---

## 📝 最终统计

- **Sources**: 131
- **Sinks**: 189
- **总计**: 320 条目

覆盖范围：
- TB (TaintBench): 40 sources, 42 sinks
- AD (Amandroid): 30 sources, 42 sinks
- DB (DroidBench): 15 sources, 23 sinks
- FD (FlowDroid): 89 sources, 133 sinks

---

## 🛠️ 依赖要求

- Python 3.6+
- 标准库：re, pathlib, typing, collections

无需额外安装第三方库。

---

## 📌 注意事项

1. **参数格式标准化**：所有参数之间统一使用 `, ` (逗号+空格)分隔
2. **去重机制**：基于完整的方法签名（类名+方法名+参数）去重
3. **格式验证**：生成后建议运行 `comprehensive_check.py` 进行质量检查

---

## 🔧 维护说明

如需添加新的 Source/Sink 列表：
1. 将文件放到 `TaintBench/` 目录
2. 在 `merge_sources_sinks.py` 的 `input_files` 列表中添加文件名
3. 重新运行合并流程

---

最后更新：2025-02-10
