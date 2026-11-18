import numpy as np
from PIL import Image


def to_gray(img):
    if img.ndim == 2:
        return img
    gray = img[:, :, :3] @ np.array([0.299, 0.587, 0.114])
    return np.round(gray).astype(np.uint8)


def histogram(gray):
    return np.bincount(gray.ravel(), minlength=256)


def linear_contrast(img, cut=0.0):
    low, high = np.percentile(img, [cut, 100 - cut])
    if high <= low:
        return img.copy()
    res = (img.astype(np.float64) - low) / (high - low) * 255
    return np.clip(res, 0, 255).round().astype(np.uint8)


def equalize_gray(ch):
    cdf = histogram(ch).cumsum()
    cdf_min = cdf[cdf > 0].min()
    total = ch.size
    if total == cdf_min:
        return ch.copy()
    lut = np.round((cdf - cdf_min) / (total - cdf_min) * 255)
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    return lut[ch]


def equalize_rgb(img):
    out = np.empty_like(img)
    for c in range(3):
        out[:, :, c] = equalize_gray(img[:, :, c])
    return out


def equalize_hsv(img):
    pil = Image.fromarray(img).convert("HSV")
    hsv = np.array(pil)
    hsv[:, :, 2] = equalize_gray(hsv[:, :, 2])
    back = Image.frombytes("HSV", pil.size, hsv.tobytes())
    return np.array(back.convert("RGB"))