import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from PIL import Image, ImageTk

from filters import order_filter
from contrast import to_gray, histogram, linear_contrast, equalize_rgb, equalize_hsv

PANEL = 300
HIST_H = 120
MAX_SIDE = 800

FILTERS = {"Медиана": "median", "Минимум": "min", "Максимум": "max"}


class App:
    def __init__(self, root):
        self.root = root
        root.title("Лабораторная работа 2")

        self.image = None
        self.arrays = [None] * 4
        self.photos = [None] * 4

        top = ttk.Frame(root, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="Открыть изображение", command=self.open_image).pack(side="left")

        ttk.Label(top, text="   Фильтр:").pack(side="left")
        self.filter_var = tk.StringVar(value="Медиана")
        ttk.Combobox(top, textvariable=self.filter_var, values=list(FILTERS),
                     width=9, state="readonly").pack(side="left", padx=4)
        ttk.Label(top, text="окно:").pack(side="left")
        self.size_var = tk.StringVar(value="3")
        ttk.Combobox(top, textvariable=self.size_var, values=["3", "5", "7", "9"],
                     width=3, state="readonly").pack(side="left", padx=4)
        ttk.Button(top, text="Применить фильтр", command=self.apply_filter).pack(side="left")

        ttk.Label(top, text="      Обрезка, %:").pack(side="left")
        self.cut_var = tk.StringVar(value="0")
        ttk.Combobox(top, textvariable=self.cut_var, values=["0", "1", "2", "5"],
                     width=3, state="readonly").pack(side="left", padx=4)
        ttk.Button(top, text="Сравнить методы контраста",
                   command=self.compare_contrast).pack(side="left")

        ttk.Label(root, text="Двойной щелчок по результату - сделать его исходным").pack()

        panels = ttk.Frame(root, padding=8)
        panels.pack()
        self.titles = []
        self.labels = []
        self.hists = []
        for i in range(4):
            frame = ttk.Frame(panels)
            frame.grid(row=0, column=i, padx=5)
            title = ttk.Label(frame, text="")
            title.pack()
            box = ttk.Frame(frame, width=PANEL, height=PANEL)
            box.pack_propagate(False)
            box.pack()
            label = ttk.Label(box)
            label.pack(expand=True)
            if i > 0:
                label.bind("<Double-Button-1>", lambda e, k=i: self.make_source(k))
            hist = tk.Canvas(frame, width=PANEL, height=HIST_H, bg="white",
                             highlightthickness=1, highlightbackground="gray")
            hist.pack(pady=(6, 0))
            self.titles.append(title)
            self.labels.append(label)
            self.hists.append(hist)

    def show(self, i, arr, title):
        self.arrays[i] = arr
        pil = Image.fromarray(arr)
        pil.thumbnail((PANEL, PANEL))
        self.photos[i] = ImageTk.PhotoImage(pil)
        self.labels[i].config(image=self.photos[i])
        self.titles[i].config(text=title)
        self.draw_hist(i, to_gray(arr))

    def draw_hist(self, i, gray):
        canvas = self.hists[i]
        canvas.delete("all")
        h = histogram(gray)
        base = HIST_H - 16
        bar = PANEL / 256
        for level in range(256):
            height = h[level] / h.max() * (base - 6)
            x = level * bar
            canvas.create_rectangle(x, base - height, x + bar, base, fill="gray", outline="")
        canvas.create_text(2, HIST_H - 2, text="0", anchor="sw")
        canvas.create_text(PANEL - 2, HIST_H - 2, text="255", anchor="se")

    def clear(self, i):
        self.arrays[i] = None
        self.photos[i] = None
        self.labels[i].config(image="")
        self.hists[i].delete("all")
        self.titles[i].config(text="")

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"), ("Все файлы", "*.*")])
        if not path:
            return
        try:
            pil = Image.open(path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return
        pil.thumbnail((MAX_SIDE, MAX_SIDE))
        self.image = np.array(pil)
        self.show(0, self.image, "Исходное")
        for i in (1, 2, 3):
            self.clear(i)

    def check_image(self):
        if self.image is None:
            messagebox.showinfo("Нет изображения", "Сначала откройте изображение")
            return False
        return True

    def apply_filter(self):
        if not self.check_image():
            return
        name = self.filter_var.get()
        size = int(self.size_var.get())
        self.root.config(cursor="watch")
        self.root.update()
        result = order_filter(self.image, size, FILTERS[name])
        self.root.config(cursor="")
        self.show(1, result, f"{name} {size}x{size}")
        self.clear(2)
        self.clear(3)

    def compare_contrast(self):
        if not self.check_image():
            return
        cut = float(self.cut_var.get())
        self.show(1, linear_contrast(self.image, cut), f"Линейное контрастирование ({cut:g}%)")
        self.show(2, equalize_rgb(self.image), "Эквализация RGB")
        self.show(3, equalize_hsv(self.image), "Эквализация V (HSV)")

    def make_source(self, i):
        if self.arrays[i] is None:
            return
        self.image = self.arrays[i]
        self.show(0, self.image, "Исходное (после обработки)")
        for k in (1, 2, 3):
            self.clear(k)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()