import platform
import timeit

import extra
import raster

LINES = [(100, 37), (1000, 371), (10000, 3719)]
RADII = [10, 100, 1000]
LINE_ALGORITHMS = [
    ("Пошаговый", raster.step_by_step),
    ("ЦДА", raster.dda),
    ("Брезенхем", raster.bresenham_line),
    ("Кастл-Питвей", extra.castle_pitteway),
    ("Ву", extra.wu_line),
]


def measure(func, args, size):
    number = max(1, 20000 // size)
    best = min(timeit.repeat(lambda: func(*args), number=number, repeat=5))
    return best / number * 1e6


def table(title, heads, rows):
    lines = [title, "Алгоритм".ljust(22) + "".join(h.rjust(12) for h in heads)]
    for name, values in rows:
        lines.append(name.ljust(22) + "".join(f"{v:12.1f}" for v in values))
    return lines


def report():
    out = [f"Python {platform.python_version()}, {platform.system()}"]
    out.append("Время одного вызова, мкс (лучшее из 5 серий),")
    out.append("пиксели накапливаются в списке, вывода на экран нет")
    out.append("")
    heads = [f"{dx}x{dy}" for dx, dy in LINES]
    rows = []
    for name, func in LINE_ALGORITHMS:
        rows.append((name, [measure(func, (0, 0, dx, dy), dx) for dx, dy in LINES]))
    out += table("Отрезок (0, 0) - (dx, dy)", heads, rows)
    out.append("")
    heads = [f"R={r}" for r in RADII]
    rows = [("Брезенхем", [measure(raster.bresenham_circle, (0, 0, r), r) for r in RADII])]
    out += table("Окружность с центром (0, 0)", heads, rows)
    return out


if __name__ == "__main__":
    print("\n".join(report()))
