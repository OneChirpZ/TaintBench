#!/usr/bin/env python3
"""
FlowDroid 批量分析脚本 - 重试版本
支持指定 APK 列表和自定义超时时间
"""

import os
import subprocess
import time
import csv
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置
APK_DIR = Path.home() / "LDFA-dataset/TaintBench/apks"
SOURCE_SINK = Path.home() / "LDFA-dataset/TaintBench/TB_SourcesAndSinks.txt"
OUTPUT_BASE = Path.home() / "LDFA-dataset/TaintBench/output"
FLOWDROID_JAR = Path.home() / "FlowDroid/jars/soot-infoflow-cmd-2.14.1-jar-with-dependencies.jar"
ANDROID_PLATFORMS = Path.home() / "Android/sdk/platforms"
MAX_MEM = "180g"

# 默认超时配置（秒）
DEFAULT_CALLGRAPH_TIMEOUT = 600    # 10 分钟
DEFAULT_DATAFLOW_TIMEOUT = 1800    # 30 分钟
DEFAULT_RESULT_TIMEOUT = 120       # 2 分钟


class APKAnalyzer:
    def __init__(self, mode: str = "full", apk_list: Optional[List[str]] = None, 
                 timeout_multiplier: int = 1):
        """
        初始化分析器
        
        Args:
            mode: 运行模式
                  - "full": 完整运行（无优化标志）
                  - "ne": 使用 -ne 标志（不跟踪异常流）
                  - "ns": 使用 -ns 标志（不跟踪静态字段）
                  - "ne_ns": 同时使用 -ne 和 -ns
            apk_list: 需要分析的 APK 列表（不含 .apk 后缀）
            timeout_multiplier: 超时时间倍数
        """
        self.mode = mode
        self.apk_list = apk_list  # None 表示分析所有
        self.timeout_multiplier = timeout_multiplier
        
        # 计算超时时间
        self.ct_timeout = DEFAULT_CALLGRAPH_TIMEOUT * timeout_multiplier
        self.dt_timeout = DEFAULT_DATAFLOW_TIMEOUT * timeout_multiplier
        self.rt_timeout = DEFAULT_RESULT_TIMEOUT * timeout_multiplier
        
        # 根据模式设置标志
        self.flags = []
        if mode == "ne":
            self.flags = ["-ne"]
        elif mode == "ns":
            self.flags = ["-ns"]
        elif mode == "ne_ns":
            self.flags = ["-ne", "-ns"]
        
        # 创建输出目录
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        mode_name = {
            "full": "max-precision",
            "ne": "no-exceptions",
            "ns": "no-static",
            "ne_ns": "no-exception-no-static"
        }[mode]
        self.output_dir = OUTPUT_BASE / f"{timestamp}-retry-{timeout_multiplier}x-{mode_name}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 日志文件
        self.log_file = self.output_dir / "analysis_summary.log"
        self.summary_file = self.output_dir / "results_summary.csv"
        
        # 初始化 CSV
        self._init_csv()
        
    def _init_csv(self):
        """初始化 CSV 文件"""
        with open(self.summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'apk_name', 'status', 'leaks_found', 'sources_found', 'sinks_found',
                'callgraph_time_sec', 'dataflow_time_sec', 'result_time_sec',
                'total_time_sec', 'peak_memory_gb', 'exit_code', 'timeout_reason',
                'output_file'
            ])
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')
    
    def _parse_log_file(self, log_file: Path) -> Dict:
        """解析 FlowDroid 日志文件"""
        result = {
            'leaks': 'N/A',
            'sources': 'N/A',
            'sinks': 'N/A',
            'callgraph_time': 'N/A',
            'dataflow_time': 'N/A',
            'memory_gb': 'N/A',
        }
        
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                
            if not content.strip():
                return result
                
            # 提取泄露数
            leaks_match = re.search(r'Found (\d+) leaks', content)
            if leaks_match:
                result['leaks'] = leaks_match.group(1)
            
            # 提取源点和汇点数
            sources_match = re.search(r'found (\d+) sources and (\d+) sinks', content)
            if sources_match:
                result['sources'] = sources_match.group(1)
                result['sinks'] = sources_match.group(2)
            
            # 提取时间信息
            cg_match = re.search(r'Callgraph construction took ([\d.]+) seconds', content)
            if cg_match:
                result['callgraph_time'] = cg_match.group(1)
            
            df_match = re.search(r'Data flow solver took ([\d.]+) seconds', content)
            if df_match:
                result['dataflow_time'] = df_match.group(1)
            
            # 提取内存使用
            memory_match = re.search(r'Maximum memory consumption: ([\d.]+) GB', content)
            if memory_match:
                result['memory_gb'] = memory_match.group(1)
                
        except Exception as e:
            self._log(f"解析日志文件失败: {e}")
        
        return result
    
    def _run_flowdroid(self, apk_path: Path) -> Tuple[int, str, float]:
        """
        运行 FlowDroid 分析
        
        Returns:
            (exit_code, timeout_reason, total_time)
        """
        apk_name = apk_path.stem
        output_xml = self.output_dir / f"{apk_name}_results.xml"
        log_file = self.output_dir / f"{apk_name}.log"
        
        # 构建命令
        env = os.environ.copy()
        env['PATH'] = f"{Path.home()}/.sdkman/candidates/java/current/bin:{env.get('PATH', '')}"
        
        cmd = [
            "java",
            f"-Xmx{MAX_MEM}",
            "-jar", str(FLOWDROID_JAR),
            "-a", str(apk_path),
            "-p", str(ANDROID_PLATFORMS),
            "-s", str(SOURCE_SINK),
            "-cg", "CHA",
            f"-ct", str(self.ct_timeout),
            f"-dt", str(self.dt_timeout),
            f"-rt", str(self.rt_timeout),
            *self.flags,
            "-o", str(output_xml)
        ]
        
        start_time = time.time()
        timeout_reason = ""
        
        try:
            with open(log_file, 'w') as lf:
                result = subprocess.run(
                    cmd,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    env=env,
                    timeout=None
                )
            exit_code = result.returncode
            
        except subprocess.TimeoutExpired:
            exit_code = 124
            timeout_reason = "SUBPROCESS_TIMEOUT"
            
        except Exception as e:
            exit_code = -1
            timeout_reason = f"ERROR: {str(e)}"
            
        total_time = time.time() - start_time
        
        # 检查日志中的超时信息
        if exit_code != 0:
            try:
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    
                if "Callgraph creation timed out" in log_content:
                    timeout_reason = "CALLGRAPH_TIMEOUT"
                elif "Data flow computation timed out" in log_content:
                    timeout_reason = "DATAFLOW_TIMEOUT"
                elif "Result computation timed out" in log_content:
                    timeout_reason = "RESULT_TIMEOUT"
                elif "Running out of memory" in log_content or "OutOfMemoryError" in log_content:
                    timeout_reason = "OUT_OF_MEMORY"
                elif "UnsupportedClassVersionError" in log_content:
                    timeout_reason = "JAVA_VERSION_ERROR"
                    
            except Exception:
                pass
        
        return exit_code, timeout_reason, total_time
    
    def run_analysis(self) -> Dict:
        """运行完整的批量分析"""
        self._log("=" * 60)
        self._log(f"FlowDroid 批量分析 - 模式: {self.mode}")
        self._log(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"输出目录: {self.output_dir}")
        self._log(f"标志: {' '.join(self.flags) if self.flags else '无（完整模式）'}")
        self._log(f"超时设置: CT={self.ct_timeout}s, DT={self.dt_timeout}s, RT={self.rt_timeout}s")
        self._log(f"超时倍数: {self.timeout_multiplier}x")
        if self.apk_list:
            self._log(f"指定 APK: {', '.join(self.apk_list)}")
        self._log("=" * 60)
        
        # 统计
        total = 0
        success = 0
        failed = 0
        
        # 获取 APK 列表
        if self.apk_list:
            apk_files = [APK_DIR / f"{apk}.apk" for apk in self.apk_list]
            # 过滤存在的文件
            apk_files = [f for f in apk_files if f.exists()]
        else:
            apk_files = sorted(APK_DIR.glob("*.apk"))
        
        for apk_path in apk_files:
            apk_name = apk_path.stem
            total += 1
            self._log(f"[{total}/{len(apk_files)}] 正在分析: {apk_name}")
            
            # 运行分析
            exit_code, timeout_reason, total_time = self._run_flowdroid(apk_path)
            
            # 解析日志
            log_file = self.output_dir / f"{apk_name}.log"
            parsed = self._parse_log_file(log_file)
            
            # 确定状态
            if exit_code == 0:
                status = "SUCCESS"
                success += 1
            else:
                status = f"FAILED"
                failed += 1
            
            # 记录结果
            with open(self.summary_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    apk_name,
                    status,
                    parsed['leaks'],
                    parsed['sources'],
                    parsed['sinks'],
                    parsed['callgraph_time'],
                    parsed['dataflow_time'],
                    'N/A',
                    f"{total_time:.2f}",
                    parsed['memory_gb'],
                    exit_code,
                    timeout_reason,
                    str(self.output_dir / f"{apk_name}_results.xml")
                ])
            
            # 输出摘要
            self._log(f"  状态: {status}")
            self._log(f"  泄露数: {parsed['leaks']}")
            self._log(f"  源点数: {parsed['sources']}, 汇点数: {parsed['sinks']}")
            self._log(f"  时间: CG={parsed['callgraph_time']}s, DF={parsed['dataflow_time']}s, 总计={total_time:.2f}s")
            self._log(f"  内存: {parsed['memory_gb']} GB")
            if timeout_reason:
                self._log(f"  失败原因: {timeout_reason}")
            self._log("")
        
        # 输出汇总
        self._log("=" * 60)
        self._log("分析完成!")
        self._log(f"总计: {total} 个 APK")
        self._log(f"成功: {success}")
        self._log(f"失败: {failed}")
        self._log("=" * 60)
        self._log(f"汇总文件: {self.summary_file}")
        self._log(f"日志文件: {self.log_file}")
        
        return {
            'total': total,
            'success': success,
            'failed': failed
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='FlowDroid 批量分析 - 重试版本')
    parser.add_argument('--mode', choices=['full', 'ne', 'ns', 'ne_ns'], 
                       default='full', help='运行模式')
    parser.add_argument('--apks', nargs='*', default=[], 
                       help='指定要分析的 APK 列表（不含 .apk 后缀）')
    parser.add_argument('--timeout-multiplier', type=int, default=1,
                       help='超时时间倍数（默认 1）')
    
    args = parser.parse_args()
    
    analyzer = APKAnalyzer(
        mode=args.mode, 
        apk_list=args.apks if args.apks else None,
        timeout_multiplier=args.timeout_multiplier
    )
    result = analyzer.run_analysis()
    
    print(f"\\n分析结果: {result}")


if __name__ == '__main__':
    main()
