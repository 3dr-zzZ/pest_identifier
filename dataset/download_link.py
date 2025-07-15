#!/usr/bin/env python3
"""
download_inat_images.py
~~~~~~~~~~~~~~~~~~~~~~~
批量下载各文件夹中 multimedia.txt 里前 n 条图片链接。

目录结构示例
└─ root/
   ├─ species_A/
   │   └─ multimedia.txt
   ├─ species_B/
   │   └─ multimedia.txt
   ...

multimedia.txt 行示例
... https://inaturalist-open-data.s3.amazonaws.com/photos/508860958/original.jpg ...
"""

import re
import sys
from pathlib import Path
from urllib.parse import urlparse
import requests
from tqdm import tqdm

# 配置
ROOT_DIR = "/Users/jacksmac/Code/Projects/pest indentifier/dataset/species"  # 文件夹根目录
LIMIT = 50  # 每个物种下载的图片数量
# 下载图片的输出根目录（与 ROOT_DIR 下的文件夹同名）
DOWNLOAD_DIR = "/Users/jacksmac/Code/Projects/pest indentifier/dataset/downloads"

# 匹配 http/https 开头直到空白结束的简单正则
URL_RE = re.compile(r"https?://[^\s]+?\.(?:jpg|jpeg|png)", re.IGNORECASE)

def download_file(url: str, dest: Path, timeout: int = 10):
    """下载单个文件到 dest（完整路径）。若文件已存在则跳过。"""
    if dest.exists():
        return
    try:
        resp = requests.get(url, stream=True, timeout=timeout)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with tqdm(
            total=total, unit="B", unit_scale=True, unit_divisor=1024,
            desc=f"↓ {dest.name}", leave=False
        ) as bar, dest.open("wb") as f:
            for chunk in resp.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
    except Exception as exc:
        print(f"[WARN] Failed {url} -> {exc}", file=sys.stderr)

def process_txt(txt_path: Path, limit: int):
    """读取 multimedia.txt，提取前 limit 条图片链接并下载到同目录。"""
    # 计算与 ROOT_DIR 的相对路径，并在 DOWNLOAD_DIR 中创建对应的输出文件夹
    rel_dir = txt_path.parent.relative_to(Path(ROOT_DIR))
    out_dir = Path(DOWNLOAD_DIR) / rel_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"==> Processing {txt_path}")
    with txt_path.open(encoding="utf-8", errors="ignore") as f:
        urls = []
        for line in f:
            match = URL_RE.search(line)
            if match:
                urls.append(match.group(0))
            if len(urls) >= limit:
                break

    if not urls:
        print("   No image URLs found.")
        return

    for idx, url in enumerate(urls, start=1):
        # 以 URL 最后路径段为文件名（保持原扩展名）
        filename = Path(urlparse(url).path).name
        # 若同名文件已存在，改用 idx 前缀
        dest = out_dir / filename
        if dest.exists():
            dest = out_dir / f"{idx}_{filename}"
        download_file(url, dest)

def main():
    root = Path(ROOT_DIR).expanduser().resolve()
    # 确保 DOWNLOAD_DIR 存在
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

    txt_files = list(root.rglob("multimedia.txt"))

    for txt in txt_files:
        process_txt(txt, LIMIT)

if __name__ == "__main__":
    main()