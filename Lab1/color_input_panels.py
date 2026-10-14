from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QSlider
from PyQt5.QtCore import Qt, pyqtSignal, QSignalBlocker


class ColorRow(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(1)
        self._updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title_label)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.sliders_layout = QVBoxLayout()
        self.sliders_layout.setSpacing(3)
        self.spinboxes_layout = QVBoxLayout()
        self.spinboxes_layout.setSpacing(3)
        row.addLayout(self.sliders_layout, 4)
        row.addLayout(self.spinboxes_layout, 1)
        layout.addLayout(row)
        self.create_components()

    def create_components(self):
        raise NotImplementedError

    def add_slider_with_spinbox(self, label, minimum, maximum, suffix=""):
        slider_row = QHBoxLayout()
        slider_row.setSpacing(5)
        label_widget = QLabel(label)
        label_widget.setFixedWidth(24)
        slider_row.addWidget(label_widget)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(minimum)
        slider_row.addWidget(slider, 1)
        self.sliders_layout.addLayout(slider_row)

        spin_row = QHBoxLayout()
        spin_label = QLabel(label)
        spin_label.setFixedWidth(24)
        spin_row.addWidget(spin_label)
        spinbox = QSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setValue(minimum)
        spinbox.setSuffix(suffix)
        spinbox.setKeyboardTracking(False)
        spinbox.setFixedWidth(82)
        spin_row.addWidget(spinbox)
        spin_row.addStretch()
        self.spinboxes_layout.addLayout(spin_row)

        def on_slider(val):
            with QSignalBlocker(spinbox):
                spinbox.setValue(val)
            self._on_value_changed()

        def on_spin(val):
            with QSignalBlocker(slider):
                slider.setValue(val)
            self._on_value_changed()

        slider.valueChanged.connect(on_slider)
        spinbox.valueChanged.connect(on_spin)

        spinbox._paired_slider = slider
        return slider, spinbox

    def _set_row_values(self, pairs):
        self._updating = True
        for spin, val in pairs:
            with QSignalBlocker(spin):
                spin.setValue(val)
            with QSignalBlocker(spin._paired_slider):
                spin._paired_slider.setValue(val)
        self._updating = False

    @staticmethod
    def _set_spin_value(spinbox, value):
        with QSignalBlocker(spinbox):
            spinbox.setValue(value)

    @staticmethod
    def _set_slider_value(slider, value):
        with QSignalBlocker(slider):
            slider.setValue(value)

    def _on_value_changed(self):
        raise NotImplementedError


class RGBColorRow(ColorRow):
    rgb_changed = pyqtSignal(int, int, int)

    def __init__(self):
        super().__init__("RGB")

    def create_components(self):
        self.r_slider, self.r_spin = self.add_slider_with_spinbox("R:", 0, 255)
        self.g_slider, self.g_spin = self.add_slider_with_spinbox("G:", 0, 255)
        self.b_slider, self.b_spin = self.add_slider_with_spinbox("B:", 0, 255)

    def _on_value_changed(self):
        if not self._updating:
            self.rgb_changed.emit(self.r_spin.value(), self.g_spin.value(), self.b_spin.value())

    def set_rgb(self, r, g, b):
        self._updating = True
        self.r_spin.setValue(r); self.g_spin.setValue(g); self.b_spin.setValue(b)
        self._updating = False


class CMYKColorRow(ColorRow):
    cmyk_changed = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__("CMYK")

    def create_components(self):
        self.c_slider, self.c_spin = self.add_slider_with_spinbox("C:", 0, 100, "%")
        self.m_slider, self.m_spin = self.add_slider_with_spinbox("M:", 0, 100, "%")
        self.y_slider, self.y_spin = self.add_slider_with_spinbox("Y:", 0, 100, "%")
        self.k_slider, self.k_spin = self.add_slider_with_spinbox("K:", 0, 100, "%")

    def _on_value_changed(self):
        if not self._updating:
            self.cmyk_changed.emit(self.c_spin.value(), self.m_spin.value(), self.y_spin.value(), self.k_spin.value())

    def set_cmyk(self, c, m, y, k):
        self._updating = True
        self.c_spin.setValue(c); self.m_spin.setValue(m); self.y_spin.setValue(y); self.k_spin.setValue(k)
        self._updating = False


class HLSColorRow(ColorRow):
    hls_changed = pyqtSignal(int, int, int)

    def __init__(self):
        super().__init__("HLS")

    def create_components(self):
        self.h_slider, self.h_spin = self.add_slider_with_spinbox("H:", 0, 360, "°")
        self.l_slider, self.l_spin = self.add_slider_with_spinbox("L:", 0, 100, "%")
        self.s_slider, self.s_spin = self.add_slider_with_spinbox("S:", 0, 100, "%")

    def _on_value_changed(self):
        if not self._updating:
            self.hls_changed.emit(self.h_spin.value(), self.l_spin.value(), self.s_spin.value())

    def set_hls(self, h, l, s):
        self._updating = True
        self.h_spin.setValue(h); self.l_spin.setValue(l); self.s_spin.setValue(s)
        self._updating = False