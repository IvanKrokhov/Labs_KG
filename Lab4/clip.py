TOL = 1e-9


def liang_barsky(x1, y1, x2, y2, win):
    xmin, ymin, xmax, ymax = win
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    t0 = 0.0
    t1 = 1.0
    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return None
            continue
        r = q[i] / p[i]
        if p[i] < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
        if t0 > t1:
            return None
    return (x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy)


def area2(poly):
    s = 0
    n = len(poly)
    for i in range(n):
        xa, ya = poly[i]
        xb, yb = poly[(i + 1) % n]
        s += xa * yb - xb * ya
    return s


def is_convex(poly):
    n = len(poly)
    sign = 0
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        cx, cy = poly[(i + 2) % n]
        z = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if abs(z) < TOL:
            continue
        s = 1 if z > 0 else -1
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return sign != 0


def make_ccw(poly):
    if area2(poly) < 0:
        return poly[::-1]
    return list(poly)


def side(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def cross_point(s, e, ds, de):
    t = ds / (ds - de)
    return (s[0] + t * (e[0] - s[0]), s[1] + t * (e[1] - s[1]))


def clean(poly):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > TOL or abs(p[1] - out[-1][1]) > TOL:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) <= TOL and abs(out[0][1] - out[-1][1]) <= TOL:
        out.pop()
    return out


def sutherland_hodgman(subject, clipper):
    result = list(subject)
    n = len(clipper)
    for i in range(n):
        a = clipper[i]
        b = clipper[(i + 1) % n]
        source = result
        result = []
        for j in range(len(source)):
            s = source[j - 1]
            e = source[j]
            ds = side(a, b, s)
            de = side(a, b, e)
            if de >= -TOL:
                if ds < -TOL:
                    result.append(cross_point(s, e, ds, de))
                result.append(e)
            elif ds >= -TOL:
                result.append(cross_point(s, e, ds, de))
        if not result:
            break
    return clean(result)
