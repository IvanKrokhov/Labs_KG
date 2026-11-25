import math

import clip


def numbers(text):
    result = []
    for token in text.split():
        try:
            v = float(token)
        except ValueError:
            raise ValueError(f"'{token}' не является числом")
        if not math.isfinite(v):
            raise ValueError(f"'{token}' не является числом")
        result.append(v)
    return result


def read_count(v, pos):
    if pos >= len(v):
        raise ValueError("не хватает данных")
    n = v[pos]
    if n != int(n) or n < 1:
        raise ValueError("количество должно быть целым положительным числом")
    return int(n)


def read_items(v, pos, n, size):
    end = pos + n * size
    if end > len(v):
        raise ValueError("не хватает данных")
    items = []
    for i in range(n):
        start = pos + i * size
        items.append(tuple(v[start:start + size]))
    return items, end


def read_window(text):
    v = numbers(text)
    n = read_count(v, 0)
    segments, pos = read_items(v, 1, n, 4)
    if len(v) != pos + 4:
        raise ValueError("после отрезков должны идти ровно 4 числа: xmin ymin xmax ymax")
    xmin, ymin, xmax, ymax = v[pos:pos + 4]
    if xmin >= xmax or ymin >= ymax:
        raise ValueError("должно быть xmin < xmax и ymin < ymax")
    return segments, (xmin, ymin, xmax, ymax)


def read_polygons(text):
    v = numbers(text)
    k = read_count(v, 0)
    if k < 3:
        raise ValueError("в многоугольнике должно быть не меньше 3 вершин")
    subject, pos = read_items(v, 1, k, 2)
    m = read_count(v, pos)
    if m < 3:
        raise ValueError("в многоугольнике должно быть не меньше 3 вершин")
    poly, end = read_items(v, pos + 1, m, 2)
    if end != len(v):
        raise ValueError("лишние данные в конце")
    if not clip.is_convex(poly):
        raise ValueError("отсекающий многоугольник должен быть выпуклым")
    return subject, clip.make_ccw(poly)
