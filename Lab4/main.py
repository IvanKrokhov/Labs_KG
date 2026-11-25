import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import clip
import data
from plane import Plane

SAMPLES = {
    "window": "8\n4 4 8 6\n0 0 12 10\n-3 5 6 11\n12 3 14 9\n1 6 11 4\n6 -2 6 12\n"
              "0 9 5 2\n3 10 9 10\n2 2 10 8\n",
    "polygon": "3\n0 0\n13 3\n5 11\n5\n3 1\n9 1\n11 5\n7 9\n2 6\n",
}
ALGORITHMS = {
    "Лианг-Барски (отрезки, окно)": "window",
    "Сазерленд-Ходжман (выпуклый многоугольник)": "polygon",
}
FORMATS = {
    "window": "Формат: n, затем n строк x1 y1 x2 y2, затем окно xmin ymin xmax ymax",
    "polygon": "Формат: k и k строк x y - отсекаемый многоугольник, затем m и m строк x y - выпуклый многоугольник",
}
NOTE = (
    "Синий - отсекающее окно (многоугольник), красный - исходные отрезки (многоугольник), "
    "зелёный - видимые части. Номера у красных отрезков - порядковые номера из файла. "
    "Линии сетки проходят через целые значения координат, оси со стрелками, текущий масштаб "
    "показан над полем. Колесо мыши - масштаб, левая кнопка - перемещение."
)


class App:
    def __init__(self, root):
        self.root = root
        self.mode = None
        root.title("Лабораторная работа 4: отсечение отрезков и многоугольников")

        top = ttk.Frame(root, padding=6)
        top.pack(fill="x")
        ttk.Label(top, text="Алгоритм:").pack(side="left")
        self.algo = tk.StringVar(value=list(ALGORITHMS)[0])
        box = ttk.Combobox(top, textvariable=self.algo, values=list(ALGORITHMS),
                           width=40, state="readonly")
        box.pack(side="left", padx=4)
        box.bind("<<ComboboxSelected>>", self.algo_changed)
        ttk.Button(top, text="Открыть файл", command=self.open_file).pack(side="left", padx=4)
        ttk.Button(top, text="Отсечь", command=self.build).pack(side="left")

        bar = ttk.Frame(root, padding=(6, 0))
        bar.pack(fill="x")
        ttk.Button(bar, text="+", width=3, command=lambda: self.plane.zoom(1.25)).pack(side="left")
        ttk.Button(bar, text="-", width=3, command=lambda: self.plane.zoom(0.8)).pack(side="left", padx=2)
        ttk.Button(bar, text="Вписать в окно", command=lambda: self.plane.fit()).pack(side="left", padx=4)
        self.scale_text = ttk.Label(bar, text="", width=24)
        self.scale_text.pack(side="left")
        self.cursor_text = ttk.Label(bar, text="", width=22, anchor="e")
        self.cursor_text.pack(side="right")

        body = ttk.Frame(root, padding=6)
        body.pack(fill="both", expand=True)
        self.plane = Plane(body, width=620, height=480)
        self.plane.pack(side="left", fill="both", expand=True)
        self.plane.on_zoom = self.zoomed
        self.plane.on_hover = self.hover

        side = ttk.Frame(body)
        side.pack(side="left", fill="y", padx=(6, 0))
        ttk.Label(side, text="Входные данные:").pack(anchor="w")
        self.format_text = ttk.Label(side, text="", wraplength=360, justify="left")
        self.format_text.pack(anchor="w")
        self.input = tk.Text(side, width=48, height=1, font=("Courier", 10))
        self.input.pack(fill="both", expand=True, pady=4)
        self.status = ttk.Label(side, text="", wraplength=360, justify="left")
        self.status.pack(anchor="w")

        ttk.Label(root, text=NOTE, wraplength=1000, justify="left",
                  padding=(6, 0, 6, 6)).pack(fill="x")

        self.algo_changed()

    def algo_changed(self, event=None):
        mode = ALGORITHMS[self.algo.get()]
        if mode != self.mode:
            self.mode = mode
            self.input.delete("1.0", "end")
            self.input.insert("1.0", SAMPLES[mode])
            self.format_text.config(text=FORMATS[mode])
        self.build()

    def zoomed(self, cell):
        self.scale_text.config(text=f"{cell:.2f} px на единицу")

    def hover(self, x, y):
        self.cursor_text.config(text="" if x is None else f"x = {x:.2f}, y = {y:.2f}")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt"),
                                                     ("Все файлы", "*.*")])
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            messagebox.showerror("Ошибка", "Не удалось прочитать файл")
            return
        self.input.delete("1.0", "end")
        self.input.insert("1.0", text)
        self.build()

    def build(self):
        mode = ALGORITHMS[self.algo.get()]
        text = self.input.get("1.0", "end")
        try:
            if mode == "window":
                segments, window = data.read_window(text)
            else:
                subject, clipper = data.read_polygons(text)
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные входные данные: {e}")
            return

        if mode == "window":
            xmin, ymin, xmax, ymax = window
            clipper = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
            visible = []
            for x1, y1, x2, y2 in segments:
                part = clip.liang_barsky(x1, y1, x2, y2, window)
                if part is not None:
                    visible.append(part)
            self.plane.show_segments(clipper, segments, visible)
            self.status.config(text=f"Видимых отрезков: {len(visible)} из {len(segments)}")
        else:
            result = clip.sutherland_hodgman(subject, clipper)
            if len(result) < 3:
                result = []
                self.status.config(text="Многоугольник целиком вне окна")
            else:
                self.status.config(text=f"Вершин в результате: {len(result)}")
            self.plane.show_polygon(clipper, subject, result)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
