import torch, json, sqlite3
import inference
from sys import argv


# ------ configuration ------
MODEL_PATH = "..\\best_convnext_tiny.pth"
CLASS_MAP_PATH = "..\\class_mapping.json"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DB_PATH = "..\\database\\schema.sql"
TOPK = 3



# ------ load model ------
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
        class_map = json.load(f)
model = inference.load_model(MODEL_PATH, num_classes = len(class_map), device = DEVICE)
transform = inference.get_transforms()

# ------ open database ------


# ------ make a inference ------
def look_up(scientific_name: str) -> dict|None:
        """Look up species w/ scientific_name in the database."""

def main():
    IMG_PATH = argv[1]
    label_confs = inference.predict_one(IMG_PATH, model, transform, class_map, DEVICE, TOPK)
    lbls = []
    confs = []
    for lbl, conf in label_confs:
        lbls.append(lbl.replace("_", " "))
        confs.append(confs)
        pairs = [f"{lbl} (confidence={conf:.2%})"]
    print(f"{IMG_PATH}: " + ", ".join(pairs))

    for i in range(len(lbls)):
        scientific_name = "_".join(lbls[i].split()[-2:])
        # TODO: add the format in db look up.
        

    
if __name__ == "__main__":
        main()

