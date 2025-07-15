"""predict.py
A library including functions to load image classification model and make prediction.

Example:
    $ python predict.py path/to/image.jpg --model path/to/model.pth --classes classes.json --topk 3

Functions:
    load_model(): function to load image classification model.
    get_transforms(): function to get transforms.
    predict_one(): make prediction on an image.
    main()

Author: 3dr-zzZ
"""

import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms
import timm


def load_model(
    model_path: str | Path,
    num_classes: int,
    device: str = "cpu",
    arch: str = "convnext_tiny.in12k",
) -> torch.nn.Module:
    """
    Rebuild the network architecture with timm, then load either a full
    serialized model *or* a plain state‑dict saved via ``model.state_dict()``.
    """
    checkpoint = torch.load(model_path, map_location=device)

    # Case 1 ‑ the file already contains a full nn.Module object
    if isinstance(checkpoint, torch.nn.Module):
        model = checkpoint

    # Case 2 ‑ the file is a state‑dict (what we saved during training)
    else:
        model = timm.create_model(
            arch, pretrained=False, num_classes=num_classes
        )
        model.load_state_dict(checkpoint, strict=True)

    model.to(device)
    model.eval()
    return model


def get_transforms() -> transforms.Compose:
    """Return the same preprocessing pipeline used during training."""
    return transforms.Compose(
        [
            transforms.Resize((224, 224)),
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
    topk: int = 1,
) -> list[tuple[str, float]]:
    """Return a list of *(label, confidence)* tuples for the top‑``k`` predictions."""
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)
    print("running on", device)
    logits = model(tensor)
    probs = torch.softmax(logits, dim=1).squeeze(0)

    # pick the top‑k predictions
    confs, indices = probs.topk(topk)
    return [
        (class_map[str(idx.item())], conf.item())
        for conf, idx in zip(confs, indices)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Single‑image classifier")
    parser.add_argument("image", nargs="+", help="Path(s) to image file(s)")
    parser.add_argument(
        "--model", default="..\\best_convnext_tiny.pth", help="Path to trained model weights (.pth)"
    )
    parser.add_argument(
        "--classes",
        default="..\\class_mapping.json",
        help="Path to JSON mapping of class indices to labels (e.g. {\"0\": \"cat\"})",
    )
    parser.add_argument(
        "--topk", "-k", type=int, default=1,
        help="Number of top predictions to return (default: 1)",
    )
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    with open(args.classes, "r", encoding="utf-8") as f:
        class_map = json.load(f)

    model = load_model(args.model, num_classes=len(class_map), device=device)
    transform = get_transforms()

    for img in args.image:
        label_confs = predict_one(
            img, model, transform, class_map, device, args.topk
        )
        pairs = [f"{lbl} (confidence={conf:.2%})" for lbl, conf in label_confs]
        print(f"{Path(img).name}: " + ", ".join(pairs))


if __name__ == "__main__":  # pragma: no cover
    main()
