import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QColorDialog, QFrame
)
from PyQt5.QtCore import Qt

from color_map import ColorMapWidget
from color_input_panels import RGBColorRow, CMYKColorRow, HLSColorRow
from color_converter import ColorConverter


class ColorConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converter = ColorConverter()
        self._sync_in_progress = False
        self._build_ui()
        self._connect_signals()
        self._set_initial_color(255, 0, 0)

    def _build_ui(self):
        self.setWindowTitle("Color converter (CMYK - RGB - HLS) | Вариант 5")
        self.setMinimumSize(1180, 700)
        self.resize(1280, 760)

        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.setContentsMargins(14, 14, 14, 14)
        main.setSpacing(18)

        left = QVBoxLayout()
        label = QLabel("HLS Palette (X: Тон, Y: Светлота)")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        left.addWidget(label)

        self.color_map = ColorMapWidget()
        left.addWidget(self.color_map, 1, Qt.AlignCenter)

        ctrl_row = QHBoxLayout()
        self.preview_box = QFrame()
        self.preview_box.setFixedSize(65, 45)
        self.preview_box.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.preview_box.setLineWidth(2)
        ctrl_row.addWidget(self.preview_box)

        btn_dialog = QPushButton("Выбрать цвет из системной палитры...")
        btn_dialog.setFixedHeight(45)
        btn_dialog.setStyleSheet("font-weight: bold;")
        btn_dialog.clicked.connect(self.open_color_dialog)
        ctrl_row.addWidget(btn_dialog)
        left.addLayout(ctrl_row)

        right = QVBoxLayout()
        title = QLabel("Цветовые модели (CMYK, RGB, HLS):")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        right.addWidget(title)

        self.rgb_row = RGBColorRow()
        right.addWidget(self.rgb_row)

        self.cmyk_row = CMYKColorRow()
        right.addWidget(self.cmyk_row)

        self.hls_row = HLSColorRow()
        right.addWidget(self.hls_row)

        right.addStretch()

        main.addLayout(left, 5)
        main.addLayout(right, 5)

        self.setStyleSheet("""
            QMainWindow { background: #f5f5f5; }
            QFrame { background: white; border: 1px solid #d0d0d0; border-radius: 6px; }
            QSlider::groove:horizontal { height: 5px; background: #d5d5d5; border-radius: 2px; }
            QSlider::handle:horizontal { width: 14px; margin: -5px 0; border-radius: 7px; background: #555; }
            QSpinBox { padding: 3px; }
            QPushButton { background: #e0e0e0; border: 1px solid #bbb; border-radius: 4px; padding: 6px; }
            QPushButton:hover { background: #d0d0d0; }
        """)

    def _connect_signals(self):
        self.rgb_row.rgb_changed.connect(self.on_rgb_changed)
        self.cmyk_row.cmyk_changed.connect(self.on_cmyk_changed)
        self.hls_row.hls_changed.connect(self.on_hls_changed)
        self.color_map.color_selected.connect(self.on_color_map_changed)

    def _set_initial_color(self, r, g, b):
        self._update_from_rgb(r, g, b)

    def _update_from_rgb(self, r, g, b):
        self._sync_in_progress = True
        self.preview_box.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border-radius: 6px;")
        self.rgb_row.set_rgb(r, g, b)
        self.cmyk_row.set_cmyk(*self.converter.rgb_to_cmyk(r, g, b))
        self.hls_row.set_hls(*self.converter.rgb_to_hls(r, g, b))
        self.color_map.set_rgb_color(r, g, b)
        self._sync_in_progress = False

    def on_rgb_changed(self, r, g, b):
        if self._sync_in_progress: return
        self._sync_in_progress = True

        self.preview_box.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border-radius: 6px;")
        self.cmyk_row.set_cmyk(*self.converter.rgb_to_cmyk(r, g, b))

        current_h = self.hls_row.h_spin.value()
        self.hls_row.set_hls(*self.converter.rgb_to_hls(r, g, b, fallback_h=current_h))

        self.color_map.set_rgb_color(r, g, b)
        self._sync_in_progress = False

    def on_cmyk_changed(self, c, m, y, k):
        if self._sync_in_progress: return
        self._sync_in_progress = True

        r, g, b = self.converter.cmyk_to_rgb(c, m, y, k)
        self.preview_box.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border-radius: 6px;")
        self.rgb_row.set_rgb(r, g, b)

        current_h = self.hls_row.h_spin.value()
        self.hls_row.set_hls(*self.converter.rgb_to_hls(r, g, b, fallback_h=current_h))

        self.color_map.set_rgb_color(r, g, b)
        self._sync_in_progress = False

    def on_hls_changed(self, h, l, s):
        if self._sync_in_progress: return
        self._sync_in_progress = True

        r, g, b = self.converter.hls_to_rgb(h, l, s)
        self.preview_box.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border-radius: 6px;")

        self.rgb_row.set_rgb(r, g, b)
        self.cmyk_row.set_cmyk(*self.converter.rgb_to_cmyk(r, g, b))
        self.color_map.set_rgb_color(r, g, b)
        self._sync_in_progress = False

    def on_color_map_changed(self, r, g, b):
        if self._sync_in_progress: return
        self._sync_in_progress = True

        self.preview_box.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border-radius: 6px;")
        self.rgb_row.set_rgb(r, g, b)
        self.cmyk_row.set_cmyk(*self.converter.rgb_to_cmyk(r, g, b))

        current_s = self.hls_row.s_spin.value()
        h, l, _ = self.converter.rgb_to_hls(r, g, b, fallback_h=self.color_map.selected_h)
        self.hls_row.set_hls(h, l, current_s if current_s > 0 else 100)

        self._sync_in_progress = False

    def open_color_dialog(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self._update_from_rgb(col.red(), col.green(), col.blue())


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ColorConverterApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()