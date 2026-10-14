from typing import Tuple


class ColorConverter:
    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def rgb_to_cmyk(r: int, g: int, b: int) -> Tuple[int, int, int, int]:
        r_n = ColorConverter._clamp(r, 0, 255) / 255.0
        g_n = ColorConverter._clamp(g, 0, 255) / 255.0
        b_n = ColorConverter._clamp(b, 0, 255) / 255.0

        k = 1.0 - max(r_n, g_n, b_n)
        if k >= 1.0 - 1e-7:
            return 0, 0, 0, 100

        c = (1.0 - r_n - k) / (1.0 - k)
        m = (1.0 - g_n - k) / (1.0 - k)
        y = (1.0 - b_n - k) / (1.0 - k)
        return round(c * 100), round(m * 100), round(y * 100), round(k * 100)

    @staticmethod
    def cmyk_to_rgb(c: int, m: int, y: int, k: int) -> Tuple[int, int, int]:
        c_n = ColorConverter._clamp(c, 0, 100) / 100.0
        m_n = ColorConverter._clamp(m, 0, 100) / 100.0
        y_n = ColorConverter._clamp(y, 0, 100) / 100.0
        k_n = ColorConverter._clamp(k, 0, 100) / 100.0

        r = 255.0 * (1.0 - c_n) * (1.0 - k_n)
        g = 255.0 * (1.0 - m_n) * (1.0 - k_n)
        b = 255.0 * (1.0 - y_n) * (1.0 - k_n)
        return round(ColorConverter._clamp(r, 0, 255)), \
               round(ColorConverter._clamp(g, 0, 255)), \
               round(ColorConverter._clamp(b, 0, 255))

    @staticmethod
    def rgb_to_hls(r: int, g: int, b: int, fallback_h: int = 0) -> Tuple[int, int, int]:
        r_n = ColorConverter._clamp(r, 0, 255) / 255.0
        g_n = ColorConverter._clamp(g, 0, 255) / 255.0
        b_n = ColorConverter._clamp(b, 0, 255) / 255.0

        max_c = max(r_n, g_n, b_n)
        min_c = min(r_n, g_n, b_n)
        delta = max_c - min_c

        l = (max_c + min_c) / 2.0

        if delta < 1e-6:
            h = fallback_h / 360.0
            s = 0.0
        else:
            s = delta / (2.0 - max_c - min_c) if l > 0.5 else delta / (max_c + min_c)
            if max_c == r_n:
                h = (g_n - b_n) / delta + (6.0 if g_n < b_n else 0.0)
            elif max_c == g_n:
                h = (b_n - r_n) / delta + 2.0
            else:
                h = (r_n - g_n) / delta + 4.0
            h /= 6.0

        h_deg = round(h * 360) % 360
        if fallback_h == 360 and h_deg == 0:
            h_deg = 360

        return h_deg, round(l * 100), round(s * 100)

    @staticmethod
    def hls_to_rgb(h: int, l: int, s: int) -> Tuple[int, int, int]:
        h_deg = ColorConverter._clamp(h, 0, 360)
        h_n = (h_deg % 360) / 360.0
        l_n = ColorConverter._clamp(l, 0, 100) / 100.0
        s_n = ColorConverter._clamp(s, 0, 100) / 100.0

        if s_n < 1e-6:
            val = round(ColorConverter._clamp(l_n * 255.0, 0, 255))
            return val, val, val

        def hue2rgb(p, q, t):
            if t < 0.0: t += 1.0
            if t > 1.0: t -= 1.0
            if t < 1.0 / 6.0: return p + (q - p) * 6.0 * t
            if t < 1.0 / 2.0: return q
            if t < 2.0 / 3.0: return p + (q - p) * (2.0 / 3.0 - t) * 6.0
            return p

        q = l_n * (1.0 + s_n) if l_n < 0.5 else l_n + s_n - (l_n * s_n)
        p = 2.0 * l_n - q

        r = hue2rgb(p, q, h_n + 1.0 / 3.0)
        g = hue2rgb(p, q, h_n)
        b = hue2rgb(p, q, h_n - 1.0 / 3.0)

        return (
            int(ColorConverter._clamp(r * 255.0 + 0.5, 0, 255)),
            int(ColorConverter._clamp(g * 255.0 + 0.5, 0, 255)),
            int(ColorConverter._clamp(b * 255.0 + 0.5, 0, 255))
        )