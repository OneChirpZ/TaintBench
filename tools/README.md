# TaintBench 数据集工具

本目录包含用于管理 TaintBench 数据集的工具脚本。

## 工具列表

### 1. clone_repos.py

克隆 TaintBench 数据集中的所有 Git 仓库到本地。

**功能特性**:
- 并发克隆：支持多线程并发克隆，默认 4 个并发，可配置
- 智能检测：自动跳过已存在的仓库，避免重复克隆
- 强制更新：可选的 `--force-update` 模式，更新已存在的仓库
- 错误处理：完善的错误处理和摘要报告
- 进度显示：实时显示克隆进度

**基本用法**:

```bash
# 从 TaintBench 目录运行
cd tools/
python clone_repos.py

# 指定并发数为 8
python clone_repos.py --max-workers 8

# 强制更新已存在的仓库
python clone_repos.py --force-update
```

### 2. convert_html_to_json.py

将 TaintBench HTML 数据表格转换为结构化的 JSON 格式。

**功能特性**:
- 提取表格中的所有元数据（名称、污点流数量、代码规模等）
- 自动提取 GitHub 仓库链接
- 关联本地 APK 文件
- 清理和规范化数据格式

**基本用法**:

```bash
# 从 TaintBench 目录运行
cd tools/
python convert_html_to_json.py
```

## 参数说明

### clone_repos.py

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--json-file` | `../TaintBenchDataRaw.json` | JSON 数据文件路径（相对于 tools/） |
| `--output-dir` | `../TaintBenchRepos` | 输出目录（相对于 tools/） |
| `--max-workers` | `4` | 最大并发数 |
| `--force-update` | `False` | 强制更新已存在的仓库 |

## 目录结构

```
TaintBench/
├── README.md                     # 数据集说明文档
├── tools/                        # 工具目录（本目录）
│   ├── README.md                # 本文件
│   ├── clone_repos.py           # 仓库克隆脚本
│   └── convert_html_to_json.py  # HTML 转 JSON 脚本
├── TaintBenchDataRaw.html       # 原始数据表格
├── TaintBenchDataRaw.json       # 转换后的结构化数据
├── TaintBenchApks/              # APK 文件（39 个应用）
└── TaintBenchRepos/             # Git 仓库（39 个项目）
```

## 使用示例

### 克隆所有仓库

```bash
cd evaluation/dataset/TaintBench/tools
python clone_repos.py
```

输出示例：
```
从 JSON 文件读取仓库列表: ../TaintBenchDataRaw.json
目标目录: ../TaintBenchRepos
并发数: 4

克隆仓库: backflash from https://github.com/TaintBench/backflash
克隆仓库: beita_com_beita_contact from https://github.com/TaintBench/beita_com_beita_contact
...
✓ backflash: 克隆成功
✓ beita_com_beita_contact: 克隆成功
...

============================================================
克隆摘要
============================================================
总计: 39 个仓库
成功: 39 个
失败: 0 个
已存在: 0 个
```

### 更新已有仓库

```bash
python clone_repos.py --force-update
```

## 与 Submodule 的对比

### 为什么不使用 Git Submodule？

| 特性 | Submodule | 独立克隆 |
|------|-----------|----------|
| **管理复杂度** | 高（需要 init/update） | 低 |
| **版本固定** | 固定到特定 commit | 可灵活更新 |
| **适用场景** | 项目依赖 | 外部分析对象 |
| **更新操作** | 需要特定命令 | 标准 git pull |
| **权限要求** | 需要修改父仓库 | 无需修改 |

对于 TaintBench 这样的评估数据集，**独立克隆**更加合适：
1. 这些是外部独立的恶意软件/应用样本，不是项目依赖
2. 分析过程可能需要不同的版本或分支
3. 更容易管理和维护
4. 减少了 Git 操作的复杂度

## 常见问题

### 1. 如何更新所有仓库？

```bash
python clone_repos.py --force-update
```

### 2. 如何重新克隆所有仓库？

```bash
# 删除现有目录
rm -rf ../TaintBenchRepos

# 重新克隆
python clone_repos.py
```

### 3. 克隆速度慢怎么办？

增加并发数（注意：过高的并发数可能导致网络限制）：

```bash
python clone_repos.py --max-workers 10
```

### 4. 部分仓库克隆失败怎么办？

脚本会显示失败的仓库列表，可以：
1. 检查网络连接
2. 单独克隆失败的仓库
3. 重新运行脚本（已成功的会跳过）

## 数据文件格式

脚本读取的 JSON 文件应包含以下字段：

```json
{
  "no": 1,
  "name": "backflash",
  "repository_url": "https://github.com/TaintBench/backflash",
  "repository_name": "backflash",
  "expected_flows": 13,
  "unexpected_flows": 11,
  "executable": "YES",
  "classes": 338,
  "methods": 2477,
  "loc": 20965,
  "apk_filename": "backflash.apk",
  "apk_exists": true,
  "apk_path": "/path/to/backflash.apk"
}
```

必需字段：
- `repository_url`: Git 仓库 URL
- `repository_name`: 仓库名称（用于本地目录名）

```bash
python clone_repos.py --force-update
```

### 2. 如何重新克隆所有仓库？

```bash
# 删除现有目录
rm -rf TaintBenchRepos

# 重新克隆
python clone_repos.py
```

### 3. 克隆速度慢怎么办？

增加并发数（注意：过高的并发数可能导致网络限制）：

```bash
python clone_repos.py --max-workers 10
```

### 4. 部分仓库克隆失败怎么办？

脚本会显示失败的仓库列表，可以：

1. 检查网络连接
2. 单独克隆失败的仓库
3. 重新运行脚本（已成功的会跳过）

## 数据文件格式

脚本读取的 JSON 文件应包含以下字段：

```json
{
  "no": 1,
  "name": "backflash",
  "repository_url": "https://github.com/TaintBench/backflash",
  "repository_name": "backflash",
  ...
}
```

必需字段：
- `repository_url`: Git 仓库 URL
- `repository_name`: 仓库名称（用于本地目录名）
