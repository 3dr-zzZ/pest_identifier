"""Perform pest/vector classification on a image, then look for species info in a database.

Example:
    $ python workwork.py pest_img.jpg

Functions:
    main()

Author: 3dr-zzZ
"""

import torch, json
import predict, look_up

from pathlib import Path
from sys import argv


# ------ configuration ------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT/"database"/"pests.db"
MODEL_PATH = PROJECT_ROOT/"best_convnext_tiny.pth"
CLASS_MAP_PATH = PROJECT_ROOT/"class_mapping.json"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TOPK = 3
# ---------------------------


# ------ load model ------
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
        class_map = json.load(f)
model = predict.load_model(MODEL_PATH, num_classes = len(class_map), device = DEVICE)
transform = predict.get_transforms()

# ------ load database ------
con = look_up.load_database(DB_PATH)
cur = con.cursor()


if __name__ == "__main__":
    import time
    t0 = time.perf_counter()

    IMG_PATH = argv[1]
    print(f"Classifying: {IMG_PATH}")
    label_confs = predict.predict_one(IMG_PATH, model, transform, class_map, DEVICE, TOPK)
    lbls = []
    confs = []
    for lbl, conf in label_confs:
        lbls.append(lbl.replace("_", " "))
        confs.append(confs)
        pairs = [f"{lbl} (confidence={conf:.2%})"]
        print(f", ".join(pairs))
    t1 = time.perf_counter()
    print(f"Classifying took {t1 - t0:.3f}s\n")
    
    print(f"Searching in database: {DB_PATH}")
    for i in range(len(lbls)):
        scientific_name = "_".join(lbls[i].split()[-2:])
        print(scientific_name + ":")
        look_up.format_db_output(look_up.look_up(scientific_name, cur))  # look up and format the result
        print("\n")
    t2 = time.perf_counter()
    print(f"Searching took {t2 - t1:.3f}s\n")