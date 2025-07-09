
"""inference.py
Minimal command‑line helper to apply your fine‑tuned PyTorch image‑classification
model to one or more new images.

Example
-------
$ python inference.py path/to/image.jpg --model path/to/model.pth --classes classes.json
"""

import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms


def load_model(model_path: str | Path, device: str = "cpu") -> torch.nn.Module:
    """Load a serialized ``.pth`` model checkpoint (``torch.save``)."""
    model = torch.load(model_path, map_location=device)
    model.eval()
    return model


def get_transforms() -> transforms.Compose:
    """Return the same preprocessing pipeline used during training."""
    return transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )


@torch.inference_mode()
def predict_one(
    image_path: str | Path,
    model: torch.nn.Module,
    transform: transforms.Compose,
    class_map: dict[str, str],
    device: str = "cpu",
) -> tuple[str, float]:
    """Return *(label, confidence)* for a single image."""
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)
    logits = model(tensor)
    probs = torch.softmax(logits, dim=1).squeeze(0)
    conf, idx = probs.max(dim=0)
    return class_map[str(idx.item())], conf.item()


def main() -> None:
    parser = argparse.ArgumentParser(description="Single‑image classifier")
    parser.add_argument("image", nargs="+", help="Path(s) to image file(s)")
    parser.add_argument(
        "--model", default="model.pth", help="Path to trained model weights (.pth)"
    )
    parser.add_argument(
        "--classes",
        default="classes.json",
        help="Path to JSON mapping of class indices to labels (e.g. {\"0\": \"cat\"})",
    )
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = load_model(args.model, device)
    transform = get_transforms()

    with open(args.classes, "r", encoding="utf-8") as f:
        class_map = json.load(f)

    for img in args.image:
        label, conf = predict_one(img, model, transform, class_map, device)
        print(f"{Path(img).name}: {label}  (confidence={conf:.2%})")


if __name__ == "__main__":  # pragma: no cover
    main()
