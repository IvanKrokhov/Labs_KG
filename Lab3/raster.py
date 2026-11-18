import math


def rnd(v):
    return math.floor(v + 0.5)


def par(v, fmt=""):
    s = format(v, fmt)
    return f"({s})" if v < 0 else s


def step_by_step(x0, y0, x1, y1, log=None):
    dx = x1 - x0
    dy = y1 - y0
    if log is not None:
        log.append("Пошаговый алгоритм")
        log.append(f"Отрезок ({x0}, {y0}) -> ({x1}, {y1})")
        log.append(f"dx = {dx}, dy = {dy}")
    if dx == 0 and dy == 0:
        if log is not None:
            log.append("Начало и конец совпадают, один пиксель")
        return [(x0, y0)]
    points = []
    if abs(dx) >= abs(dy):
        k = dy / dx
        b = y0 - k * x0
        step = 1 if dx > 0 else -1
        if log is not None:
            log.append("|dx| >= |dy|: идём по x с шагом 1, y = k*x + b")
            log.append(f"k = dy / dx = {dy} / {dx} = {k:.4f}")
            log.append(f"b = y0 - k*x0 = {y0} - {par(k, '.4f')}*{par(x0)} = {b:.4f}")
            log.append("")
            log.append("  i       x           y    пиксель")
        for i, x in enumerate(range(x0, x1 + step, step)):
            y = k * x + b
            py = rnd(y)
            points.append((x, py))
            if log is not None:
                log.append(f"{i:3d}  {x:6d}  {y:10.4f}    ({x}, {py})")
    else:
        k = dx / dy
        b = x0 - k * y0
        step = 1 if dy > 0 else -1
        if log is not None:
            log.append("|dy| > |dx|: идём по y с шагом 1, x = k*y + b")
            log.append(f"k = dx / dy = {dx} / {dy} = {k:.4f}")
            log.append(f"b = x0 - k*y0 = {x0} - {par(k, '.4f')}*{par(y0)} = {b:.4f}")
            log.append("")
            log.append("  i       y           x    пиксель")
        for i, y in enumerate(range(y0, y1 + step, step)):
            x = k * y + b
            px = rnd(x)
            points.append((px, y))
            if log is not None:
                log.append(f"{i:3d}  {y:6d}  {x:10.4f}    ({px}, {y})")
    return points


def dda(x0, y0, x1, y1, log=None):
    dx = x1 - x0
    dy = y1 - y0
    length = max(abs(dx), abs(dy))
    if log is not None:
        log.append("Алгоритм ЦДА")
        log.append(f"Отрезок ({x0}, {y0}) -> ({x1}, {y1})")
        log.append(f"dx = {dx}, dy = {dy}")
    if length == 0:
        if log is not None:
            log.append("Начало и конец совпадают, один пиксель")
        return [(x0, y0)]
    sx = dx / length
    sy = dy / length
    if log is not None:
        log.append(f"L = max(|dx|, |dy|) = {length}")
        log.append(f"sx = dx / L = {sx:.4f}, sy = dy / L = {sy:.4f}")
        log.append("На каждом шаге x = x + sx, y = y + sy, пиксель = округление")
        log.append("")
        log.append("  i         x          y    пиксель")
    x = float(x0)
    y = float(y0)
    points = []
    for i in range(length + 1):
        px = rnd(x)
        py = rnd(y)
        points.append((px, py))
        if log is not None:
            log.append(f"{i:3d}  {x:9.4f}  {y:9.4f}    ({px}, {py})")
        x += sx
        y += sy
    return points


def bresenham_line(x0, y0, x1, y1, log=None):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1
    steep = dy > dx
    minor = "x" if steep else "y"
    if log is not None:
        log.append("Алгоритм Брезенхема (отрезок)")
        log.append(f"Отрезок ({x0}, {y0}) -> ({x1}, {y1})")
        log.append(f"dx = |x1 - x0| = {dx}, dy = |y1 - y0| = {dy}")
    if steep:
        dx, dy = dy, dx
        if log is not None:
            log.append(f"dy > dx: ведущая ось y, меняем роли: dx = {dx}, dy = {dy}")
    elif log is not None:
        log.append("dx >= dy: ведущая ось x")
    d = 2 * dy - dx
    if log is not None:
        log.append(f"d0 = 2*dy - dx = {d}")
        log.append(f"d >= 0: {minor} меняется, d = d + 2*(dy - dx)")
        log.append(f"d < 0:  {minor} прежний, d = d + 2*dy")
        log.append("")
        log.append("  i       x       y       d    решение")
    x = x0
    y = y0
    points = []
    for i in range(dx + 1):
        points.append((x, y))
        if log is not None:
            if i == dx:
                action = "конец"
            elif d >= 0:
                action = f"{minor} меняется"
            else:
                action = f"{minor} прежний"
            log.append(f"{i:3d}  {x:6d}  {y:6d}  {d:6d}    {action}")
        if d >= 0:
            if steep:
                x += sx
            else:
                y += sy
            d -= 2 * dx
        if steep:
            y += sy
        else:
            x += sx
        d += 2 * dy
    return points


def bresenham_circle(cx, cy, r, log=None):
    x = 0
    y = r
    d = 3 - 2 * r
    if log is not None:
        log.append("Алгоритм Брезенхема (окружность)")
        log.append(f"Центр ({cx}, {cy}), R = {r}")
        log.append("Считаем один октант от x = 0, y = R, остальные семь")
        log.append("получаем симметрией: (±x, ±y) и (±y, ±x) от центра")
        log.append(f"d0 = 3 - 2*R = {d}")
        log.append("d < 0:  d = d + 4*x + 6")
        log.append("d >= 0: d = d + 4*(x - y) + 10, y = y - 1")
        log.append("После каждого шага x = x + 1, пока x <= y")
        log.append("")
        log.append("  i      x      y       d    точка октанта")
    points = {}
    i = 0
    while x <= y:
        for px, py in ((x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)):
            points[(cx + px, cy + py)] = None
        if log is not None:
            log.append(f"{i:3d}  {x:5d}  {y:5d}  {d:6d}    ({cx + x}, {cy + y})")
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1
        i += 1
    return list(points)
