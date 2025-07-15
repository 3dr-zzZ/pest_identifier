"""
split_dataset.py
~~~~~~~~~~~~~~~~
将下载好的物种图像随机拆分为 train / test 目录。

目录结构假设
DOWNLOAD_DIR/
└─ Aedes_albopictus/
   ├─ img1.jpg
   └─ ...
└─ Culex_pipiens/
   └─ ...

运行后会得到
OUTPUT_DIR/
├─ train/
│   ├─ Aedes_albopictus/...
│   └─ Culex_pipiens/...
└─ test/
    ├─ Aedes_albopictus/...
    └─ Culex_pipiens/...
"""

import random
import shutil
from pathlib import Path

# ============ 用户可修改的配置 ============ #
INPUT_DIR   = "D:\Pest\dataset\download\downloads"
OUTPUT_DIR  = "D:\Pest\dataset\download\split"
TRAIN_RATIO = 0.80          # 训练集比例
SEED        = 42            # 随机种子（设为 None 则每次不同）
MOVE_FILES  = False         # True=移动文件；False=复制文件
# ========================================= #

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff"}

def split_files(files, train_ratio):
    random.shuffle(files)
    k = int(len(files) * train_ratio)
    return files[:k], files[k:]

def copy_or_move(src: Path, dst: Path, move: bool = False):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if move:
        shutil.move(src, dst)
    else:
        shutil.copy2(src, dst)

def process_species_dir(species_dir: Path, out_root: Path,
                        train_ratio: float, move: bool):
    species_name = species_dir.name
    imgs = [p for p in species_dir.iterdir() if p.suffix.lower() in IMG_EXTS]

    if not imgs:
        print(f"[WARN] No images in {species_dir}")
        return

    train_files, test_files = split_files(imgs, train_ratio)
    print(f"[{species_name}] total={len(imgs)}  "
          f"train={len(train_files)}  test={len(test_files)}")

    for f in train_files:
        dst = out_root / "train" / species_name / f.name
        copy_or_move(f, dst, move)

    for f in test_files:
        dst = out_root / "test" / species_name / f.name
        copy_or_move(f, dst, move)

def main():
    if SEED is not None:
        random.seed(SEED)

    in_root  = Path(INPUT_DIR).expanduser().resolve()
    out_root = Path(OUTPUT_DIR).expanduser().resolve()

    species_dirs = [d for d in in_root.iterdir() if d.is_dir()]
    if not species_dirs:
        print(f"[ERR] No sub-folders found in {in_root}")
        return

    for sd in species_dirs:
        process_species_dir(sd, out_root,
                            train_ratio=TRAIN_RATIO, move=MOVE_FILES)

    print("✅ Dataset split completed.")

if __name__ == "__main__":
    main()