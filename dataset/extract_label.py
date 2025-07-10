# 用于从下载的数据中提取所需要数据的标签
import json

# ====== 文件路径 ======
INPUT_JSON_PATH = 'dataset/train_mini.json'  # 标签 JSON 文件
SPECIES_TXT_PATH = 'classes.txt'  # 需要提取的物种名列表
OUTPUT_JSON_PATH = 'dataset/train_extracted.json'
# =======================

# 读取物种列表
with open(SPECIES_TXT_PATH, 'r', encoding='utf-8') as f:
    species_raw = f.read().splitlines()
    species_list = [name.strip().replace(" ", "_") for name in species_raw if name.strip()]

print(f"Loaded {len(species_list)} target classes from {SPECIES_TXT_PATH}")

# 加载 JSON 数据
with open(INPUT_JSON_PATH, 'r', encoding='utf-8') as f:
    full_data = json.load(f)

# 筛选匹配物种的图像条目
matched_entries = [
    img for img in full_data['images']
    if any(species in img['file_name'] for species in species_list)
]

print(f"Found {len(matched_entries)} total matching entries.")

# 保存为缩进美化的 JSON 文件
with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f_out:
    json.dump(matched_entries, f_out, indent=2, ensure_ascii=False)
print(f"Saved to: {OUTPUT_JSON_PATH}")
