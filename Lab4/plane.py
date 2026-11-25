import math
import tkinter as tk

MIN_CELL = 0.05
MAX_CELL = 300


def label_step(cell):
    for step in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000):
        if step * cell >= 30:
            return step
    return 10000


class Plane(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg="white", highlightthickness=1,
                         highlightbackground="gray", **kw)
        self.cell = 24
        self.ox = None
        self.oy = None
        self.clipper = []
        self.segments = []
        self.visible = []
        self.subject = []
        self.result = []
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

    def to_world(self, sx, sy):
        return (sx - self.ox) / self.cell, (self.oy - sy) / self.cell

    def show_segments(self, clipper, segments, visible):
        self.clipper = clipper
        self.segments = segments
        self.visible = visible
        self.subject = []
        self.result = []
        self.fit()

    def show_polygon(self, clipper, subject, result):
        self.clipper = clipper
        self.segments = []
        self.visible = []
        self.subject = subject
        self.result = result
        self.fit()

    def fit(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 50 or h < 50:
            return
        points = list(self.clipper) + list(self.subject)
        for x1, y1, x2, y2 in self.segments:
            points.append((x1, y1))
            points.append((x2, y2))
        xs = [p[0] for p in points] or [0]
        ys = [p[1] for p in points] or [0]
        left, right = min(xs), max(xs)
        bottom, top = min(ys), max(ys)
        size = min(w / (max(right - left, 1) * 1.2), h / (max(top - bottom, 1) * 1.2))
        self.cell = max(MIN_CELL, min(MAX_CELL, size))
        self.ox = w / 2 - (left + right) / 2 * self.cell
        self.oy = h / 2 + (bottom + top) / 2 * self.cell
        if self.on_zoom:
            self.on_zoom(self.cell)
        self.redraw()

    def zoom(self, factor, cx=None, cy=None):
        size = max(MIN_CELL, min(MAX_CELL, self.cell * factor))
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
        self.zoom(1.25 if up else 0.8, event.x, event.y)

    def motion(self, event):
        if self.ox is not None and self.on_hover:
            self.on_hover(*self.to_world(event.x, event.y))

    def leave(self, event):
        if self.on_hover:
            self.on_hover(None, None)

    def screen_coords(self, points):
        coords = []
        for x, y in points:
            coords.extend(self.to_screen(x, y))
        return coords

    def redraw(self):
        self.delete("all")
        if self.ox is None:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        c = self.cell
        xl, yt = self.to_world(0, 0)
        xr, yb = self.to_world(w, h)
        left, right = math.floor(xl), math.ceil(xr)
        bottom, top = math.floor(yb), math.ceil(yt)
        step = label_step(c)
        grid = 1 if c >= 6 else step

        for i in range(left, right + 1):
            if i % grid == 0:
                sx = self.ox + i * c
                self.create_line(sx, 0, sx, h, fill="gray85")
        for j in range(bottom, top + 1):
            if j % grid == 0:
                sy = self.oy - j * c
                self.create_line(0, sy, w, sy, fill="gray85")

        if len(self.subject) >= 3:
            self.create_polygon(self.screen_coords(self.subject), fill="",
                                outline="red", width=1)
        for i, (x1, y1, x2, y2) in enumerate(self.segments, 1):
            self.create_line(*self.to_screen(x1, y1), *self.to_screen(x2, y2), fill="red")
            if len(self.segments) <= 30:
                mx, my = self.to_screen((x1 + x2) / 2, (y1 + y2) / 2)
                self.create_text(mx + 8, my - 8, text=str(i), fill="red")

        if len(self.result) >= 3:
            self.create_polygon(self.screen_coords(self.result), fill="lightgreen",
                                outline="green", width=3)
        for x1, y1, x2, y2 in self.visible:
            sx1, sy1 = self.to_screen(x1, y1)
            sx2, sy2 = self.to_screen(x2, y2)
            self.create_line(sx1, sy1, sx2, sy2, fill="green", width=3)
            self.create_oval(sx1 - 3, sy1 - 3, sx1 + 3, sy1 + 3, fill="green", outline="green")
            self.create_oval(sx2 - 3, sy2 - 3, sx2 + 3, sy2 + 3, fill="green", outline="green")

        if len(self.clipper) >= 3:
            self.create_polygon(self.screen_coords(self.clipper), fill="",
                                outline="blue", width=2)

        x_axis = 0 <= self.oy <= h
        y_axis = 0 <= self.ox <= w
        if x_axis:
            self.create_line(0, self.oy, w, self.oy, width=2, arrow=tk.LAST)
        if y_axis:
            self.create_line(self.ox, h, self.ox, 0, width=2, arrow=tk.LAST)
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
