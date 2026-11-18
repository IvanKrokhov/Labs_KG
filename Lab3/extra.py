import math


def short(s, limit=14):
    return s if len(s) <= limit else s[:limit - 3] + "..."


def castle_pitteway(x0, y0, x1, y1, log=None):
    dx = x1 - x0
    dy = y1 - y0
    steep = abs(dy) > abs(dx)
    sx = 1 if dx >= 0 else -1
    sy = 1 if dy >= 0 else -1
    big = max(abs(dx), abs(dy))
    small = min(abs(dx), abs(dy))
    x = big - small
    y = small
    m1 = "S"
    m2 = "D"
    if log is not None:
        log.append("Алгоритм Кастла-Питвея")
        log.append(f"Отрезок ({x0}, {y0}) -> ({x1}, {y1})")
        log.append(f"Ведущая ось {'y' if steep else 'x'}: X = {big}, Y = {small}")
        log.append("S - шаг по ведущей оси, D - шаг по обеим осям")
        log.append("Строки m1 = S, m2 = D, x = X - Y, y = Y")
        log.append("Пока x != y:")
        log.append("  x > y: x = x - y, m2 = m1 + обратная(m2)")
        log.append("  x < y: y = y - x, m1 = m2 + обратная(m1)")
        log.append("Код отрезка: (m2 + обратная(m1)) повторить x раз")
        log.append("")
        log.append("шаг     x     y   m1              m2")
        log.append(f"  0  {x:4d}  {y:4d}   {short(m1):<14}  {short(m2)}")
    if small == 0:
        code = "S" * big
        if log is not None:
            log.append("Y = 0: все шаги S")
    elif x == 0:
        code = "D" * big
        if log is not None:
            log.append("X = Y: все шаги D")
    else:
        n = 0
        while x != y:
            n += 1
            if x > y:
                x -= y
                m2 = m1 + m2[::-1]
            else:
                y -= x
                m1 = m2 + m1[::-1]
            if log is not None:
                log.append(f"{n:3d}  {x:4d}  {y:4d}   {short(m1):<14}  {short(m2)}")
        code = (m2 + m1[::-1]) * x
        if log is not None:
            log.append(f"x = y = {x}, повторяем (m2 + обратная(m1)) {x} раз")
    if log is not None:
        log.append("")
        log.append("Код отрезка:")
        for k in range(0, len(code), 50):
            log.append(code[k:k + 50])
        log.append("")
        log.append("  i  шаг   пиксель")
    px = x0
    py = y0
    points = [(px, py)]
    if log is not None:
        log.append(f"{0:3d}   -    ({px}, {py})")
    for i, move in enumerate(code, 1):
        if steep:
            py += sy
            if move == "D":
                px += sx
        else:
            px += sx
            if move == "D":
                py += sy
        points.append((px, py))
        if log is not None:
            log.append(f"{i:3d}   {move}    ({px}, {py})")
    return points


def wu_line(x0, y0, x1, y1, log=None):
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        u0, v0, u1, v1 = y0, x0, y1, x1
    else:
        u0, v0, u1, v1 = x0, y0, x1, y1
    if u0 > u1:
        u0, u1 = u1, u0
        v0, v1 = v1, v0
    du = u1 - u0
    dv = v1 - v0
    if log is not None:
        log.append("Алгоритм Ву (сглаживание)")
        log.append(f"Отрезок ({x0}, {y0}) -> ({x1}, {y1})")
        if steep:
            log.append("Ведущая координата u = y, ведомая v = x")
        else:
            log.append("Ведущая координата u = x, ведомая v = y")
        log.append(f"u от {u0} до {u1}, du = {du}, dv = {dv}")
    if du == 0:
        if log is not None:
            log.append("Начало и конец совпадают, один пиксель")
        return [(x0, y0, 1.0)]
    k = dv / du
    if log is not None:
        log.append(f"k = dv / du = {dv} / {du} = {k:.4f}")
        log.append("Для каждого u: v = v0 + k*(u - u0), f = дробная часть v")
        log.append("Нижний пиксель floor(v) получает яркость I = 1 - f,")
        log.append("верхний пиксель floor(v) + 1 получает яркость I = f")
        log.append("")
        log.append(f"{'u':>5}  {'v':>8}  {'f':>5}  {'нижний':<8} {'I':>5}  {'верхний':<8} {'I':>5}")
    points = []
    for u in range(u0, u1 + 1):
        v = v0 + dv * (u - u0) / du
        base = math.floor(v)
        f = v - base
        for pos, level in ((base, 1 - f), (base + 1, f)):
            if level >= 0.005:
                points.append((pos, u, level) if steep else (u, pos, level))
        if log is not None:
            lo = (base, u) if steep else (u, base)
            hi = (base + 1, u) if steep else (u, base + 1)
            log.append(f"{u:5d}  {v:8.3f}  {f:5.3f}  {str(lo):<8} {1 - f:5.3f}  {str(hi):<8} {f:5.3f}")
    return points
