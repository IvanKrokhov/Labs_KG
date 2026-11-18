import numpy as np


def order_filter(img, size, mode="median"):
    if img.ndim == 3:
        out = np.empty_like(img)
        for c in range(img.shape[2]):
            out[:, :, c] = order_filter(img[:, :, c], size, mode)
        return out

    h, w = img.shape
    r = size // 2
    padded = np.pad(img, r, mode="edge")

    windows = np.empty((size * size, h, w), dtype=img.dtype)
    k = 0
    for dy in range(size):
        for dx in range(size):
            windows[k] = padded[dy:dy + h, dx:dx + w]
            k += 1

    if mode == "min":
        return windows.min(axis=0)
    if mode == "max":
        return windows.max(axis=0)

    mid = size * size // 2
    return np.partition(windows, mid, axis=0)[mid]