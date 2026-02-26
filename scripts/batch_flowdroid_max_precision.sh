#!/bin/bash

# FlowDroid 批量分析脚本 - 最高精度模式
# 使用 180g 堆内存，不带任何性能优化开关
# 支持黑名单功能

# 配置
APK_DIR="$HOME/LDFA-dataset/TaintBench/apks"
SOURCE_SINK="$HOME/LDFA-dataset/TaintBench/TB_SourcesAndSinks.txt"
OUTPUT_BASE="$HOME/LDFA-dataset/TaintBench/output"
FLOWDROID_JAR="$HOME/FlowDroid/jars/soot-infoflow-cmd-2.14.1-jar-with-dependencies.jar"
ANDROID_PLATFORMS="$HOME/Android/sdk/platforms"
MAX_MEM="180g"

# 黑名单：需要跳过的 APK（不含 .apk 后缀）
# 用空格分隔
BLACKLIST="death_ring_materialflow cajino_baidu"

# 时间戳
TIME_STAMP=$(date +%Y%m%d-%H%M)

# 创建输出目录
OUTPUT_DIR="${OUTPUT_BASE}/${TIME_STAMP}-39apps-max-precision"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# 初始化 SDKMAN
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 计数器
TOTAL=0
SUCCESS=0
FAILED=0
SKIPPED=0

# 日志文件
LOG_FILE="${OUTPUT_DIR}/analysis_summary.log"
SUMMARY_FILE="${OUTPUT_DIR}/results_summary.csv"
BLACKLIST_LOG="${OUTPUT_DIR}/blacklist.log"

# 初始化汇总文件
echo "apk_name,status,leaks_found,sources_found,analysis_time_sec,peak_memory_gb,output_file" > "$SUMMARY_FILE"

# 记录黑名单
echo "Blacklisted APKs:" > "$BLACKLIST_LOG"
for apk in $BLACKLIST; do
    echo "  - $apk" >> "$BLACKLIST_LOG"
done

# 记录开始时间
START_TIME=$(date +%s)

exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "========================================"
echo "FlowDroid 批量分析 - 最高精度模式"
echo "开始时间: $(date)"
echo "输出目录: $OUTPUT_DIR"
echo "黑名单: $BLACKLIST"
echo "========================================"
echo ""

# 遍历所有 APK 文件
for apk_path in "$APK_DIR"/*.apk; do
    apk_name=$(basename "$apk_path" .apk)
    
    # 检查是否在黑名单中
    is_blacklisted=false
    for black_apk in $BLACKLIST; do
        if [ "$apk_name" = "$black_apk" ]; then
            is_blacklisted=true
            break
        fi
    done
    
    if $is_blacklisted; then
        echo "[$((TOTAL+1))/?] 跳过 (黑名单): $apk_name"
        echo "  状态: SKIPPED (黑名单)"
        echo ""
        SKIPPED=$((SKIPPED + 1))
        echo "${apk_name},SKIPPED,0,0,0,0," >> "$SUMMARY_FILE"
        continue
    fi
    
    TOTAL=$((TOTAL + 1))
    output_xml="${OUTPUT_DIR}/${apk_name}_results.xml"
    
    echo "[$TOTAL/39] 正在分析: $apk_name"
    echo "  输出: $output_xml"
    
    # 记录开始时间
    apk_start=$(date +%s)
    
    # 运行 FlowDroid - 最高精度模式（不使用 -ns 或 -ne）
    set +e
    java -Xmx${MAX_MEM} -jar "$FLOWDROID_JAR" \
        -a "$apk_path" \
        -p "$ANDROID_PLATFORMS" \
        -s "$SOURCE_SINK" \
        -cg CHA \
        -o "$output_xml" > "${OUTPUT_DIR}/${apk_name}.log" 2>&1
    
    exit_code=$?
    set -e
    apk_end=$(date +%s)
    apk_duration=$((apk_end - apk_start))
    
    if [ $exit_code -eq 0 ]; then
        SUCCESS=$((SUCCESS + 1))
        status="SUCCESS"
        
        # 提取统计信息
        leaks=$(grep -oP "Found \K[0-9]+(?= leaks)" "${OUTPUT_DIR}/${apk_name}.log" 2>/dev/null || echo "N/A")
        sources=$(grep -oP "found \K[0-9]+(?= sources and)" "${OUTPUT_DIR}/${apk_name}.log" 2>/dev/null || echo "N/A")
        memory=$(grep -oP "Maximum memory consumption: \K[0-9.]+" "${OUTPUT_DIR}/${apk_name}.log" 2>/dev/null || echo "N/A")
        
        echo "  状态: 成功"
        echo "  泄露数: $leaks"
        echo "  源点数: $sources"
        echo "  峰值内存: ${memory} GB"
        echo "  分析时间: ${apk_duration} 秒"
    else
        FAILED=$((FAILED + 1))
        status="FAILED (exit: $exit_code)"
        leaks="N/A"
        sources="N/A"
        memory="N/A"
        
        echo "  状态: 失败 (退出码: $exit_code)"
    fi
    
    # 记录到 CSV
    echo "${apk_name},${status},${leaks},${sources},${apk_duration},${memory},${output_xml}" >> "$SUMMARY_FILE"
    echo ""
done

# 记录结束时间
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))
TOTAL_MINUTES=$((TOTAL_DURATION / 60))

echo "========================================"
echo "分析完成!"
echo "总计: $TOTAL 个 APK"
echo "成功: $SUCCESS"
echo "失败: $FAILED"
echo "跳过: $SKIPPED"
echo "总耗时: ${TOTAL_MINUTES} 分钟 ($TOTAL_DURATION 秒)"
echo "========================================"
echo "汇总文件: $SUMMARY_FILE"
echo "日志文件: $LOG_FILE"
echo "黑名单: $BLACKLIST_LOG"
echo "========================================"

# 输出最终汇总
cat "$SUMMARY_FILE"
