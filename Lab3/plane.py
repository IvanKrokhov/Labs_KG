import math
import tkinter as tk

MIN_CELL = 1
MAX_CELL = 60
FIT_CELL = 40
BASE = (70, 130, 180)


def shade(level):
    r, g, b = (round(255 - level * (255 - c)) for c in BASE)
    return f"#{r:02x}{g:02x}{b:02x}"


def label_step(cell):
    for step in (1, 2, 5, 10, 20, 50, 100, 200, 500):
        if step * cell >= 30:
            return step
    return 1000


class Plane(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg="white", highlightthickness=1,
                         highlightbackground="gray", **kw)
        self.cell = 24
        self.ox = None
        self.oy = None
        self.cells = []
        self.ideal = None
        self.numbers = False
        self.show_ideal = True
        self.on_zoom = None
        self.on_hover = None
        self.grab = None
        self.bind("<Configure>", self.resized)
        self.bind("<ButtonPress-1>", self.press)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<MouseWheel>", self.wheel)
        self.bind("<Button-4>", self.wheel)
        self.bind("<Button-5>", self.wheel)
        self.bind("<Motion>", self.motion)
        self.bind("<Leave>", self.leave)

    def to_screen(self, x, y):
        return self.ox + x * self.cell, self.oy - y * self.cell

    def to_cell(self, sx, sy):
        return (math.floor((sx - self.ox) / self.cell + 0.5),
                math.floor((self.oy - sy) / self.cell + 0.5))

    def show(self, cells, ideal, numbers):
        self.cells = cells
        self.ideal = ideal
        self.numbers = numbers
        self.fit()

    def fit(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 50 or h < 50:
            return
        xs = [c[0] for c in self.cells] or [0]
        ys = [c[1] for c in self.cells] or [0]
        left, right = min(xs), max(xs)
        bottom, top = min(ys), max(ys)
        size = min(w / (right - left + 3), h / (top - bottom + 3))
        self.cell = max(MIN_CELL, min(FIT_CELL, int(size)))
        self.ox = w / 2 - (left + right) / 2 * self.cell
        self.oy = h / 2 + (bottom + top) / 2 * self.cell
        if self.on_zoom:
            self.on_zoom(self.cell)
        self.redraw()

    def zoom(self, size, cx=None, cy=None):
        size = max(MIN_CELL, min(MAX_CELL, size))
        if size == self.cell:
            return
        if self.ox is None:
            self.cell = size
            return
        if cx is None:
            cx = self.winfo_width() / 2
            cy = self.winfo_height() / 2
        wx = (cx - self.ox) / self.cell
        wy = (cy - self.oy) / self.cell
        self.cell = size
        self.ox = cx - wx * size
        self.oy = cy - wy * size
        if self.on_zoom:
            self.on_zoom(size)
        self.redraw()

    def resized(self, event):
        if self.ox is None:
            self.fit()
        else:
            self.redraw()

    def press(self, event):
        self.focus_set()
        self.grab = (event.x, event.y)

    def drag(self, event):
        if self.ox is None or self.grab is None:
            return
        self.ox += event.x - self.grab[0]
        self.oy += event.y - self.grab[1]
        self.grab = (event.x, event.y)
        self.redraw()
        self.motion(event)

    def wheel(self, event):
        up = event.num == 4 or event.delta > 0
        self.zoom(self.cell + (2 if up else -2), event.x, event.y)

    def motion(self, event):
        if self.ox is not None and self.on_hover:
            self.on_hover(*self.to_cell(event.x, event.y))

    def leave(self, event):
        if self.on_hover:
            self.on_hover(None, None)

    def redraw(self):
        self.delete("all")
        if self.ox is None:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        c = self.cell
        half = c / 2
        left, top = self.to_cell(0, 0)
        right, bottom = self.to_cell(w, h)

        for x, y, level in self.cells:
            if left <= x <= right and bottom <= y <= top:
                sx, sy = self.to_screen(x, y)
                self.create_rectangle(sx - half, sy - half, sx + half, sy + half,
                                      fill=shade(level), outline="")
                if self.numbers and c >= 36:
                    self.create_text(sx - half + 3, sy - half + 2, text=f"{level:.2f}",
                                     anchor="nw", font=("Arial", 7),
                                     fill="black" if level < 0.55 else "white")

        if c >= 6:
            for i in range(left, right + 2):
                sx = self.ox + (i - 0.5) * c
                self.create_line(sx, 0, sx, h, fill="gray80")
            for j in range(bottom, top + 2):
                sy = self.oy - (j - 0.5) * c
                self.create_line(0, sy, w, sy, fill="gray80")

        if self.ideal and self.show_ideal:
            if self.ideal[0] == "line":
                _, x0, y0, x1, y1 = self.ideal
                self.create_line(*self.to_screen(x0, y0), *self.to_screen(x1, y1), fill="red")
            else:
                _, cx, cy, r = self.ideal
                coords = []
                for k in range(361):
                    t = 2 * math.pi * k / 360
                    coords.extend(self.to_screen(cx + r * math.cos(t), cy + r * math.sin(t)))
                self.create_line(*coords, fill="red")

        x_axis = 0 <= self.oy <= h
        y_axis = 0 <= self.ox <= w
        if x_axis:
            self.create_line(0, self.oy, w, self.oy, width=2, arrow=tk.LAST)
        if y_axis:
            self.create_line(self.ox, h, self.ox, 0, width=2, arrow=tk.LAST)
        step = label_step(c)
        label_y = min(max(self.oy + 12, 10), h - 10)
        label_x = min(max(self.ox - 8, 26), w - 4)
        for i in range(left, right + 1):
            if i % step == 0:
                sx = self.ox + i * c
                self.create_text(sx, label_y, text=str(i))
                if x_axis:
                    self.create_line(sx, self.oy - 3, sx, self.oy + 3)
        for j in range(bottom, top + 1):
            if j % step == 0 and j != 0:
                sy = self.oy - j * c
                self.create_text(label_x, sy, text=str(j), anchor="e")
                if y_axis:
                    self.create_line(self.ox - 3, sy, self.ox + 3, sy)
        self.create_text(w - 10, min(max(self.oy - 12, 10), h - 10), text="x",
                         font=("Arial", 11, "italic"))
        self.create_text(min(max(self.ox + 12, 10), w - 10), 10, text="y",
                         font=("Arial", 11, "italic"))
