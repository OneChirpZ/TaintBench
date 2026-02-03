#!/usr/bin/env python3
"""克隆 TaintBench 数据集中的所有 Git 仓库"""

import json
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional


@dataclass
class CloneResult:
    """克隆结果"""
    name: str
    url: str
    success: bool
    message: str
    already_exists: bool = False


def run_command(cmd: list, cwd: Optional[Path] = None) -> tuple[bool, str]:
    """
    运行 shell 命令

    Args:
        cmd: 命令列表
        cwd: 工作目录

    Returns:
        (是否成功, 输出信息)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 分钟超时
        )
        success = result.returncode == 0
        return success, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "命令执行超时"
    except Exception as e:
        return False, str(e)


def clone_repository(
    repo_url: str,
    repo_name: str,
    target_dir: Path,
    force_update: bool = False
) -> CloneResult:
    """
    克隆单个 Git 仓库

    Args:
        repo_url: 仓库 URL
        repo_name: 仓库名称
        target_dir: 目标目录
        force_update: 是否强制更新已存在的仓库

    Returns:
        CloneResult
    """
    repo_path = target_dir / repo_name

    # 检查仓库是否已存在
    if repo_path.exists():
        if force_update:
            # 尝试更新已有仓库
            print(f"更新已有仓库: {repo_name}")
            success, output = run_command(
                ["git", "pull", "origin", "master"],
                cwd=repo_path
            )
            if success:
                return CloneResult(
                    name=repo_name,
                    url=repo_url,
                    success=True,
                    message="仓库已更新",
                    already_exists=True
                )
            else:
                return CloneResult(
                    name=repo_name,
                    url=repo_url,
                    success=False,
                    message=f"更新失败: {output}",
                    already_exists=True
                )
        else:
            return CloneResult(
                name=repo_name,
                url=repo_url,
                success=True,
                message="仓库已存在，跳过",
                already_exists=True
            )

    # 克隆新仓库
    print(f"克隆仓库: {repo_name} from {repo_url}")
    success, output = run_command(
        ["git", "clone", repo_url, str(repo_path)],
        cwd=target_dir.parent
    )

    if success:
        return CloneResult(
            name=repo_name,
            url=repo_url,
            success=True,
            message="克隆成功"
        )
    else:
        return CloneResult(
            name=repo_name,
            url=repo_url,
            success=False,
            message=f"克隆失败: {output}"
        )


def clone_all_repositories(
    json_file: Path,
    output_dir: Path,
    force_update: bool = False,
    max_workers: int = 4
) -> list[CloneResult]:
    """
    并发克隆所有仓库

    Args:
        json_file: JSON 数据文件路径
        output_dir: 输出目录
        force_update: 是否强制更新已存在的仓库
        max_workers: 最大并发数

    Returns:
        CloneResult 列表
    """
    # 读取 JSON 数据
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    # 使用线程池并发克隆
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for item in data:
            repo_url = item.get('repository_url')
            repo_name = item.get('repository_name')

            if not repo_url or not repo_name:
                print(f"警告: 跳过无效仓库: {item}")
                continue

            future = executor.submit(
                clone_repository,
                repo_url,
                repo_name,
                output_dir,
                force_update
            )
            futures[future] = repo_name

        # 收集结果
        for future in as_completed(futures):
            repo_name = futures[future]
            try:
                result = future.result()
                results.append(result)
                status_icon = "✓" if result.success else "✗"
                print(f"{status_icon} {repo_name}: {result.message}")
            except Exception as e:
                print(f"✗ {repo_name}: 发生异常 - {e}")
                results.append(CloneResult(
                    name=repo_name,
                    url="",
                    success=False,
                    message=f"异常: {e}"
                ))

    return results


def print_summary(results: list[CloneResult]):
    """打印克隆摘要"""
    total = len(results)
    success = sum(1 for r in results if r.success)
    failed = total - success
    already_exists = sum(1 for r in results if r.already_exists)

    print("\n" + "=" * 60)
    print("克隆摘要")
    print("=" * 60)
    print(f"总计: {total} 个仓库")
    print(f"成功: {success} 个")
    print(f"失败: {failed} 个")
    print(f"已存在: {already_exists} 个")

    if failed > 0:
        print("\n失败的仓库:")
        for result in results:
            if not result.success:
                print(f"  - {result.name}: {result.message}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="克隆 TaintBench 数据集中的所有 Git 仓库"
    )
    parser.add_argument(
        '--json-file',
        type=str,
        default='TaintBenchDataRaw.json',
        help='JSON 数据文件路径 (默认: TaintBenchDataRaw.json)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='TaintBenchRepos',
        help='输出目录 (默认: TaintBenchRepos)'
    )
    parser.add_argument(
        '--force-update',
        action='store_true',
        help='强制更新已存在的仓库'
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='最大并发数 (默认: 4)'
    )

    args = parser.parse_args()

    # 获取脚本所在目录（tools/ 子目录）
    script_dir = Path(__file__).parent.parent
    json_file = script_dir / args.json_file
    output_dir = script_dir / args.output_dir

    if not json_file.exists():
        print(f"错误: JSON 文件不存在: {json_file}")
        sys.exit(1)

    print(f"从 JSON 文件读取仓库列表: {json_file}")
    print(f"目标目录: {output_dir}")
    print(f"并发数: {args.max_workers}")
    if args.force_update:
        print("将更新已存在的仓库")
    print()

    results = clone_all_repositories(
        json_file=json_file,
        output_dir=output_dir,
        force_update=args.force_update,
        max_workers=args.max_workers
    )

    print_summary(results)

    # 如果有失败的，返回非零退出码
    if any(not r.success for r in results):
        sys.exit(1)


if __name__ == '__main__':
    main()
