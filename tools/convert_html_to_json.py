#!/usr/bin/env python3
"""将 TaintBench HTML 表格转换为 JSON 格式"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup


def parse_html_to_json(html_file_path: str, output_file_path: str, apks_dir: str = None) -> None:
    """
    解析 TaintBench HTML 表格并转换为 JSON

    Args:
        html_file_path: HTML 文件路径
        output_file_path: 输出 JSON 文件路径
        apks_dir: APK 文件目录路径（可选）
    """
    # 收集已有的 APK 文件列表
    available_apks = set()
    if apks_dir:
        apks_path = Path(apks_dir)
        if apks_path.exists():
            available_apks = {apk.stem for apk in apks_path.glob('*.apk')}
            print(f"找到 {len(available_apks)} 个 APK 文件")
        else:
            print(f"警告: APK 目录不存在: {apks_dir}")
    # 读取 HTML 文件
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到表格
    table = soup.find('table')
    if not table:
        raise ValueError("未找到表格")

    # 解析表头
    thead = table.find('thead')
    header_row = thead.find('tr')
    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]

    # 确定列索引（跳过 "View Flows on GitPod" 列）
    column_mapping = {}
    gitpod_col_idx = None
    for idx, header in enumerate(headers):
        if 'View Flows on GitPod' in header:
            gitpod_col_idx = idx
            continue

        # 映射原始列索引到新列索引
        new_idx = idx if gitpod_col_idx is None or idx < gitpod_col_idx else idx - 1
        column_mapping[new_idx] = header

    # 解析数据行
    tbody = table.find('tbody')
    data_list = []

    for row in tbody.find_all('tr'):
        cells = row.find_all('td')

        # 跳过最后一行（sum 行）
        if len(cells) > 0 and cells[0].get_text(strip=True) == 'sum':
            continue

        # 跳过空行
        if len(cells) == 0:
            continue

        item = {}

        # 填充数据（跳过 GitPod 列）
        new_idx = 0
        for old_idx, cell in enumerate(cells):
            # 跳过 GitPod 列
            if old_idx == gitpod_col_idx:
                continue

            header = column_mapping.get(new_idx)
            if not header:
                new_idx += 1
                continue

            # 处理 Repository 列（提取链接）
            if 'Repository' in header:
                link_tag = cell.find('a')
                if link_tag and link_tag.get('href'):
                    # 清理 URL 末尾的空格
                    repo_url = link_tag.get('href').strip()
                    item['repository_url'] = repo_url
                    # 提取仓库名称并清理空格
                    item['repository_name'] = repo_url.split('/')[-1].strip()
                else:
                    item['repository_url'] = None
                    item['repository_name'] = None
            # 处理 Executable 列（特殊处理包含换行的字段）
            elif 'Executable' in header:
                text = cell.get_text(strip=True)
                item['executable'] = text
            # 处理其他列
            else:
                # 清理文本（处理换行符等）
                text = cell.get_text(strip=True)
                # 转换列名到 snake_case
                key = header.lower().replace('.', '').replace('#', '').replace(' ', '_')
                key = re.sub(r'[^\w]', '_', key)
                key = key.strip('_')

                # 尝试转换为数字
                if text.isdigit():
                    item[key] = int(text)
                elif text:
                    item[key] = text
                else:
                    item[key] = None

            new_idx += 1

        # 添加原始序号
        if cells and cells[0].get_text(strip=True).isdigit():
            item['no'] = int(cells[0].get_text(strip=True))

        # 添加 APK 相关信息
        if item.get('repository_name'):
            apk_filename = f"{item['repository_name']}.apk"
            item['apk_filename'] = apk_filename
            item['apk_exists'] = item['repository_name'] in available_apks
            if item['apk_exists'] and apks_dir:
                item['apk_path'] = str(Path(apks_dir) / apk_filename)
            else:
                item['apk_path'] = None
        else:
            item['apk_filename'] = None
            item['apk_exists'] = False
            item['apk_path'] = None

        data_list.append(item)

    # 输出 JSON
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)

    print(f"成功转换 {len(data_list)} 条记录到 {output_file_path}")


if __name__ == '__main__':
    # 获取当前脚本所在目录（tools/ 子目录）
    script_dir = Path(__file__).parent.parent
    html_file = script_dir / 'TaintBenchDataRaw.html'
    json_file = script_dir / 'TaintBenchDataRaw.json'
    apks_dir = script_dir / 'TaintBenchApks'

    if not html_file.exists():
        print(f"错误: 未找到文件 {html_file}")
        exit(1)

    parse_html_to_json(str(html_file), str(json_file), str(apks_dir))
