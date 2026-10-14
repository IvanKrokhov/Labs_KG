from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QImage
from color_converter import ColorConverter


class ColorMapWidget(QWidget):
    color_selected = pyqtSignal(int, int, int)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(360, 240)
        self.selected_h = 0
        self.selected_l = 50
        self.current_s = 100
        self._dragging = False

        self._cached_image = self._generate_palette_image(180, 100)

    @staticmethod
    def _generate_palette_image(width, height):
        img = QImage(width, height, QImage.Format_RGB32)
        for y in range(height):
            l = round((1.0 - (y / (height - 1))) * 100)
            for x in range(width):
                h = round((x / (width - 1)) * 360)
                r, g, b = ColorConverter.hls_to_rgb(h, l, 100)
                img.setPixel(x, y, QColor(r, g, b).rgb())
        return img

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self._cached_image)

        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        w = max(1, self.width() - 1)
        h = max(1, self.height() - 1)
        px = (self.selected_h / 360.0) * w
        py = (1.0 - (self.selected_l / 100.0)) * h

        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(Qt.black, 3))
        painter.drawEllipse(QPointF(px, py), 6, 6)
        painter.setPen(QPen(Qt.white, 2))
        painter.drawEllipse(QPointF(px, py), 5, 5)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._select_from_pos(event.pos())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._select_from_pos(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False

    def _select_from_pos(self, pos):
        w = max(1, self.width() - 1)
        h = max(1, self.height() - 1)

        clamped_x = max(0, min(pos.x(), w))
        clamped_y = max(0, min(pos.y(), h))

        self.selected_h = round((clamped_x / w) * 360)
        self.selected_l = round((1.0 - (clamped_y / h)) * 100)

        sat = self.current_s if self.current_s > 0 else 100
        r, g, b = ColorConverter.hls_to_rgb(self.selected_h, self.selected_l, sat)

        self.update()
        self.color_selected.emit(r, g, b)

    def set_rgb_color(self, r, g, b):
        if self._dragging:
            return

        h, l, s = ColorConverter.rgb_to_hls(r, g, b, fallback_h=self.selected_h)
        self.selected_h = h
        self.selected_l = l
        if s > 0:
            self.current_s = s
        self.update()