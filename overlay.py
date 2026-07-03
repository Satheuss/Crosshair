import os

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap

from win_utils import make_click_through, set_capture_hidden, is_key_pressed
from storage import app_path

VK_END = 0x23


class Overlay(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self._mostrando = True
        self._pixmap = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.apply_monitor()
        self.reload_image()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tique)
        self._timer.start(50)

    def showEvent(self, event):
        make_click_through(int(self.winId()))
        self.apply_capture_affinity()
        super().showEvent(event)

    def apply_monitor(self):
        telas = QApplication.screens()
        i = self.settings.monitor_index
        if i < 0 or i >= len(telas):
            i = 0
            self.settings.monitor_index = 0
        self.setGeometry(telas[i].geometry())

    def apply_capture_affinity(self):
        escondido = self.settings.hide_crosshair or self.settings.hide_everything
        set_capture_hidden(int(self.winId()), escondido)

    def reload_image(self):
        self._pixmap = None
        nome = self.settings.image_path
        if nome:
            caminho = app_path(nome)
            if os.path.exists(caminho):
                pm = QPixmap(caminho)
                if not pm.isNull():
                    self._pixmap = pm

    def _tique(self):
        if is_key_pressed(VK_END):
            QApplication.quit()
            return
        novo = self._calcular_visibilidade()
        if novo != self._mostrando:
            self._mostrando = novo
            self.update()

    def _calcular_visibilidade(self) -> bool:
        s = self.settings
        if not s.crosshair_enabled:
            return False
        if s.hold_to_show:
            return is_key_pressed(s.trigger_button)
        return True

    def forcar_repaint(self):
        self._mostrando = self._calcular_visibilidade()
        self.update()

    def paintEvent(self, event):
        if not self._mostrando:
            return

        s = self.settings
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setOpacity(s.opacity)

        if s.use_image and self._pixmap is not None:
            self._desenhar_imagem(painter)
            return

        if s.outline_enabled:
            self._desenhar(painter, QColor(s.outline_color), is_outline=True)
        self._desenhar(painter, QColor(s.main_color), is_outline=False)

    def _desenhar_imagem(self, painter):
        s = self.settings

        largura = max(1, int(self._pixmap.width() * s.image_scale))
        altura = max(1, int(self._pixmap.height() * s.image_scale))
        escalado = self._pixmap.scaled(
            largura, altura, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        cx = self.width() / 2.0 + s.offset_x
        cy = self.height() / 2.0 + s.offset_y

        x = cx - escalado.width() / 2.0
        y = cy - escalado.height() / 2.0
        painter.drawPixmap(QPointF(x, y), escalado)

    def _desenhar(self, painter, cor, is_outline):
        s = self.settings
        cx = self.width() / 2.0 + s.offset_x
        cy = self.height() / 2.0 + s.offset_y

        if s.shape == "dot":
            painter.setPen(Qt.NoPen)
            painter.setBrush(cor)
            raio = s.length + (s.outline_thickness if is_outline else 0.0)
            painter.drawEllipse(QPointF(cx, cy), raio, raio)
            return

        caneta = QPen(cor)
        largura = s.thickness + (2.0 * s.outline_thickness if is_outline else 0.0)
        caneta.setWidthF(largura)
        painter.setPen(caneta)
        painter.setBrush(Qt.NoBrush)

        if s.shape == "cross":
            painter.drawLine(
                QPointF(cx - s.gap - s.length, cy), QPointF(cx - s.gap, cy)
            )
            painter.drawLine(
                QPointF(cx + s.gap, cy), QPointF(cx + s.gap + s.length, cy)
            )
            painter.drawLine(
                QPointF(cx, cy - s.gap - s.length), QPointF(cx, cy - s.gap)
            )
            painter.drawLine(
                QPointF(cx, cy + s.gap), QPointF(cx, cy + s.gap + s.length)
            )

        elif s.shape == "x":
            d = 0.7071067811865476
            for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                x1 = cx + sx * d * s.gap
                y1 = cy + sy * d * s.gap
                x2 = cx + sx * d * (s.gap + s.length)
                y2 = cy + sy * d * (s.gap + s.length)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
