import os
import sys

import numpy as np
from PIL import Image


def salt_pepper(img, p, rng):
    out = img.copy()
    mask = rng.random(img.shape[:2])
    out[mask < p / 2] = 0
    out[mask > 1 - p / 2] = 255
    return out


def gauss(img, sigma, rng):
    noise = rng.normal(0, sigma, img.shape)
    return np.clip(img + noise, 0, 255).astype(np.uint8)


def low_contrast(img, k):
    return np.clip((img.astype(np.float64) - 128) * k + 128, 0, 255).astype(np.uint8)


def dark(img, k):
    return (img * k).astype(np.uint8)


def bright(img, k):
    return (255 - (255 - img.astype(np.float64)) * k).astype(np.uint8)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python make_tests.py photo.jpg")
        sys.exit(1)

    pil = Image.open(sys.argv[1]).convert("RGB")
    pil.thumbnail((800, 800))
    img = np.array(pil)
    rng = np.random.default_rng(1)

    os.makedirs("tests", exist_ok=True)
    variants = {
        "original": img,
        "salt_pepper_5": salt_pepper(img, 0.05, rng),
        "salt_pepper_20": salt_pepper(img, 0.20, rng),
        "gauss_25": gauss(img, 25, rng),
        "low_contrast": low_contrast(img, 0.3),
        "dark": dark(img, 0.3),
        "bright": bright(img, 0.3),
    }
    for name, arr in variants.items():
        Image.fromarray(arr).save(os.path.join("tests", name + ".png"))