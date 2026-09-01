from io import BytesIO
import numpy as np
from PIL import Image, ImageFilter

def analyze_image(image_bytes: bytes):
    """
    Lightweight visual triage for the offline hackathon demo.
    This is NOT a landslide diagnosis model.
    It estimates image quality and texture/edge richness that can help
    prioritize human review. Replace with a validated vision model in production.
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((512, 512))
    arr = np.asarray(img).astype(np.float32)

    brightness = float(arr.mean() / 255.0)
    contrast = float(arr.std() / 128.0)
    gray = arr.mean(axis=2)
    edges_x = np.abs(np.diff(gray, axis=1)).mean()
    edges_y = np.abs(np.diff(gray, axis=0)).mean()
    texture = float(np.clip((edges_x + edges_y) / 60.0, 0, 1))
    quality = float(np.clip(0.35*contrast + 0.35*texture + 0.30*(1-abs(brightness-.55)), 0, 1))

    if quality > .72:
        label = "GOOD_FIELD_EVIDENCE"
    elif quality > .45:
        label = "REVIEWABLE"
    else:
        label = "LOW_QUALITY_REVIEW"

    return {
        "quality": round(quality, 3),
        "triage_label": label,
        "image_size": list(img.size),
        "note": "Visual triage only; human/geotechnical verification required."
    }
