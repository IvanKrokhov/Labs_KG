import tkinter as tk
from tkinter import ttk, messagebox

import bench
import extra
import raster
from plane import Plane, MIN_CELL, MAX_CELL

LIMIT = 1000
CIRCLE = "Брезенхем (окружность)"
WU = "Ву (сглаживание)"
ALGORITHMS = {
    "Пошаговый": raster.step_by_step,
    "ЦДА": raster.dda,
    "Брезенхем (отрезок)": raster.bresenham_line,
    CIRCLE: raster.bresenham_circle,
    "Кастл-Питвей": extra.castle_pitteway,
    WU: extra.wu_line,
}
NOTE = (
    "Целые координаты (x, y) - это центр клетки сетки: клетка занимает [x - 0.5; x + 0.5] "
    "по горизонтали и [y - 0.5; y + 0.5] по вертикали, поэтому линии сетки идут по "
    "полуцелым значениям, а оси и подписи проходят через центры клеток. Ось Y направлена "
    "вверх. Красная линия - идеальный отрезок (окружность), закрашены клетки, выбранные "
    "алгоритмом. У алгоритма Ву оттенок клетки и число в ней - яркость."
)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Лабораторная работа 3: базовые растровые алгоритмы")

        top = ttk.Frame(root, padding=6)
        top.pack(fill="x")
        ttk.Label(top, text="Алгоритм:").pack(side="left")
        self.algo = tk.StringVar(value="Брезенхем (отрезок)")
        box = ttk.Combobox(top, textvariable=self.algo, values=list(ALGORITHMS),
                           width=24, state="readonly")
        box.pack(side="left", padx=4)
        box.bind("<<ComboboxSelected>>", self.algo_changed)

        self.labels = {}
        self.entries = {}
        for name, value in (("x0", "-6"), ("y0", "-3"), ("x1", "9"), ("y1", "5"), ("R", "7")):
            label = ttk.Label(top, text=f"  {name}:")
            label.pack(side="left")
            entry = ttk.Entry(top, width=6)
            entry.insert(0, value)
            entry.pack(side="left")
            entry.bind("<Return>", lambda e: self.build())
            self.labels[name] = label
            self.entries[name] = entry
        ttk.Button(top, text="Построить", command=self.build).pack(side="left", padx=8)
        ttk.Button(top, text="Замер времени", command=self.run_bench).pack(side="left")

        bar = ttk.Frame(root, padding=(6, 0))
        bar.pack(fill="x")
        ttk.Label(bar, text="Масштаб:").pack(side="left")
        self.scale = tk.DoubleVar(value=24)
        ttk.Scale(bar, from_=MIN_CELL, to=MAX_CELL, variable=self.scale, length=180,
                  command=self.scale_changed).pack(side="left", padx=4)
        self.scale_text = ttk.Label(bar, text="24 px на клетку", width=16)
        self.scale_text.pack(side="left")
        self.ideal = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text="Идеальная линия", variable=self.ideal,
                        command=self.toggle_ideal).pack(side="left", padx=8)
        ttk.Button(bar, text="Вписать в окно", command=lambda: self.plane.fit()).pack(side="left")
        self.cursor_text = ttk.Label(bar, text="", width=20, anchor="e")
        self.cursor_text.pack(side="right")

        body = ttk.Frame(root, padding=6)
        body.pack(fill="both", expand=True)
        self.plane = Plane(body, width=620, height=480)
        self.plane.pack(side="left", fill="both", expand=True)
        self.plane.on_zoom = self.zoomed
        self.plane.on_hover = self.hover
        side = ttk.Frame(body)
        side.pack(side="left", fill="y", padx=(6, 0))
        self.log = tk.Text(side, width=68, height=1, font=("Courier", 9), wrap="none")
        scroll = ttk.Scrollbar(side, command=self.log.yview)
        self.log.config(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log.pack(side="left", fill="y")

        ttk.Label(root, text=NOTE, wraplength=1100, justify="left",
                  padding=(6, 0, 6, 6)).pack(fill="x")

        self.algo_changed()
        self.build()

    def algo_changed(self, event=None):
        circle = self.algo.get() == CIRCLE
        for name in ("x1", "y1"):
            self.entries[name].config(state="disabled" if circle else "normal")
        self.entries["R"].config(state="normal" if circle else "disabled")
        self.labels["x0"].config(text="  xc:" if circle else "  x0:")
        self.labels["y0"].config(text="  yc:" if circle else "  y0:")

    def scale_changed(self, value):
        size = int(float(value))
        self.scale_text.config(text=f"{size} px на клетку")
        if size != self.plane.cell:
            self.plane.zoom(size)

    def zoomed(self, size):
        self.scale.set(size)
        self.scale_text.config(text=f"{size} px на клетку")

    def hover(self, x, y):
        self.cursor_text.config(text="" if x is None else f"x = {x}, y = {y}")

    def toggle_ideal(self):
        self.plane.show_ideal = self.ideal.get()
        self.plane.redraw()

    def show_log(self, lines):
        self.log.delete("1.0", "end")
        self.log.insert("1.0", "\n".join(lines))

    def build(self):
        name = self.algo.get()
        circle = name == CIRCLE
        keys = ("x0", "y0", "R") if circle else ("x0", "y0", "x1", "y1")
        try:
            values = [int(self.entries[k].get()) for k in keys]
        except ValueError:
            messagebox.showerror("Ошибка", "Значения должны быть целыми числами")
            return
        if any(abs(v) > LIMIT for v in values) or (circle and values[2] < 0):
            messagebox.showerror("Ошибка", f"Допустимы целые числа от -{LIMIT} до {LIMIT}, "
                                           "радиус не может быть отрицательным")
            return
        log = []
        points = ALGORITHMS[name](*values, log)
        ideal = ("circle", *values) if circle else ("line", *values)
        cells = [p if len(p) == 3 else (p[0], p[1], 1.0) for p in points]
        self.plane.show(cells, ideal, name == WU)
        self.show_log(log)

    def run_bench(self):
        self.root.config(cursor="watch")
        self.root.update()
        try:
            lines = bench.report()
        finally:
            self.root.config(cursor="")
        self.show_log(lines)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
