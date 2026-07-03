from dataclasses import fields

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QApplication,
    QComboBox,
    QCheckBox,
    QSlider,
    QPushButton,
    QColorDialog,
    QFileDialog,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QImage

from settings import Settings
from storage import save_settings, app_path
from win_utils import is_key_pressed, button_name, set_capture_hidden
from theme import build_qss, BORDER

PASSO = 0.5
FAIXA_MIN = 0.0
FAIXA_MAX = 20.0
OFFSET_MIN = -500
OFFSET_MAX = 500
NOME_IMAGEM = "custom_crosshair.png"

CAMPOS_CROSSHAIR = [
    "shape",
    "main_color",
    "outline_color",
    "outline_enabled",
    "length",
    "thickness",
    "gap",
    "outline_thickness",
    "opacity",
    "use_image",
    "image_path",
    "image_scale",
]
CAMPOS_POSITION = ["monitor_index", "offset_x", "offset_y"]


class ConfigWindow(QWidget):
    def __init__(self, settings, overlay):
        super().__init__()
        self.settings = settings
        self.overlay = overlay

        self._capturando = False
        self._pronto_pra_capturar = False

        self.setWindowTitle("Crosshair — Settings")
        self.resize(400, 560)
        self.setStyleSheet(build_qss())

        layout_principal = QVBoxLayout(self)
        abas = QTabWidget()
        layout_principal.addWidget(abas)

        abas.addTab(self._montar_aba_crosshair(), "Crosshair")
        abas.addTab(self._montar_aba_position(), "Position")
        abas.addTab(self._montar_aba_visibility(), "Visibility")

        self.btn_reset_all = QPushButton("Reset all to defaults")
        self.btn_reset_all.clicked.connect(self._reset_all)
        layout_principal.addWidget(self.btn_reset_all)

        self._captura_timer = QTimer(self)
        self._captura_timer.timeout.connect(self._verificar_captura)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(400)
        self._save_timer.timeout.connect(self._salvar)

        self._atualizar_habilitacao()
        self._atualizar_habilitacao_imagem()

        self.adjustSize()

        self.setFixedSize(400, self.height())

    def showEvent(self, event):
        self._aplicar_captura_config()
        super().showEvent(event)

    def _montar_aba_crosshair(self):
        aba = QWidget()
        l = QVBoxLayout(aba)

        l.addWidget(self._header("Crosshair shape"))
        self.combo_forma = QComboBox()
        self.combo_forma.addItem("Cross", "cross")
        self.combo_forma.addItem("Dot", "dot")
        self.combo_forma.addItem("X", "x")
        self.combo_forma.setCurrentIndex(self.combo_forma.findData(self.settings.shape))
        self.combo_forma.currentIndexChanged.connect(self._forma_mudou)
        l.addWidget(self.combo_forma)

        self.check_use_image = QCheckBox("Use custom image")
        self.check_use_image.setChecked(self.settings.use_image)
        self.check_use_image.stateChanged.connect(self._use_image_mudou)
        l.addWidget(self.check_use_image)

        linha_img = QHBoxLayout()
        self.btn_choose_image = QPushButton("Choose image...")
        self.btn_choose_image.clicked.connect(self._choose_image)
        linha_img.addWidget(self.btn_choose_image)
        self.label_image = QLabel()
        linha_img.addWidget(self.label_image)
        l.addLayout(linha_img)

        self.slider_scale = self._criar_slider_percent(
            l,
            "Image scale",
            self.settings.image_scale,
            self._scale_mudou,
            min_pct=1,
            max_pct=100,
        )
        self._atualizar_label_imagem()

        self.btn_cor_principal = QPushButton("Main color")
        self.btn_cor_principal.clicked.connect(self._escolher_cor_principal)
        self._pintar_botao(self.btn_cor_principal, self.settings.main_color)
        l.addWidget(self.btn_cor_principal)

        self.btn_cor_outline = QPushButton("Outline color")
        self.btn_cor_outline.clicked.connect(self._escolher_cor_outline)
        self._pintar_botao(self.btn_cor_outline, self.settings.outline_color)
        l.addWidget(self.btn_cor_outline)

        self.check_outline = QCheckBox("Enable outline")
        self.check_outline.setChecked(self.settings.outline_enabled)
        self.check_outline.stateChanged.connect(self._outline_mudou)
        l.addWidget(self.check_outline)

        self.slider_size = self._criar_slider_decimal(
            l, "Size", self.settings.length, self._length_mudou
        )
        self.slider_thickness = self._criar_slider_decimal(
            l, "Thickness", self.settings.thickness, self._thickness_mudou
        )
        self.slider_gap = self._criar_slider_decimal(
            l, "Gap", self.settings.gap, self._gap_mudou
        )
        self.slider_opacity = self._criar_slider_percent(
            l, "Opacity", self.settings.opacity, self._opacity_mudou
        )

        l.addStretch()
        btn = QPushButton("Reset crosshair")
        btn.clicked.connect(self._reset_crosshair)
        l.addWidget(btn)
        return aba

    def _montar_aba_position(self):
        aba = QWidget()
        l = QVBoxLayout(aba)

        l.addWidget(self._header("Monitor"))
        self.combo_monitor = QComboBox()
        for i, tela in enumerate(QApplication.screens()):
            g = tela.geometry()
            self.combo_monitor.addItem(f"Monitor {i + 1} ({g.width()}x{g.height()})", i)
        idx = self.settings.monitor_index
        if idx < 0 or idx >= self.combo_monitor.count():
            idx = 0
        self.combo_monitor.setCurrentIndex(idx)
        self.combo_monitor.currentIndexChanged.connect(self._monitor_mudou)
        l.addWidget(self.combo_monitor)

        self.slider_offx = self._criar_slider_int(
            l,
            "Offset X",
            OFFSET_MIN,
            OFFSET_MAX,
            self.settings.offset_x,
            self._offx_mudou,
        )
        self.slider_offy = self._criar_slider_int(
            l,
            "Offset Y",
            OFFSET_MIN,
            OFFSET_MAX,
            self.settings.offset_y,
            self._offy_mudou,
        )

        l.addStretch()
        btn = QPushButton("Reset position")
        btn.clicked.connect(self._reset_position)
        l.addWidget(btn)
        return aba

    def _montar_aba_visibility(self):
        aba = QWidget()
        l = QVBoxLayout(aba)

        self.check_mostrar = QCheckBox("Show crosshair")
        self.check_mostrar.setChecked(self.settings.crosshair_enabled)
        self.check_mostrar.stateChanged.connect(self._mostrar_mudou)
        l.addWidget(self.check_mostrar)

        self.check_segurar = QCheckBox("Only show while holding button")
        self.check_segurar.setChecked(self.settings.hold_to_show)
        self.check_segurar.stateChanged.connect(self._segurar_mudou)
        l.addWidget(self.check_segurar)

        linha_gatilho = QHBoxLayout()
        linha_gatilho.addWidget(QLabel("Trigger button:"))
        self.btn_gatilho = QPushButton(button_name(self.settings.trigger_button))
        self.btn_gatilho.clicked.connect(self._iniciar_captura)
        linha_gatilho.addWidget(self.btn_gatilho)
        l.addLayout(linha_gatilho)

        l.addWidget(self._header("Hide from OBS"))
        self.check_hide_cross = QCheckBox("Hide crosshair")
        self.check_hide_cross.setChecked(self.settings.hide_crosshair)
        self.check_hide_cross.stateChanged.connect(self._hide_cross_mudou)
        l.addWidget(self.check_hide_cross)

        self.check_hide_all = QCheckBox("Hide everything")
        self.check_hide_all.setChecked(self.settings.hide_everything)
        self.check_hide_all.stateChanged.connect(self._hide_all_mudou)
        l.addWidget(self.check_hide_all)

        l.addStretch()
        return aba

    def _criar_slider_decimal(self, layout, texto, valor, callback):
        n_min = round(FAIXA_MIN / PASSO)
        n_max = round(FAIXA_MAX / PASSO)
        n_val = round(valor / PASSO)

        linha = QHBoxLayout()
        rotulo = QLabel(f"{texto}: {valor:.1f}")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(n_min, n_max)
        slider.setValue(n_val)

        def ao_mudar(pos):
            real = pos * PASSO
            rotulo.setText(f"{texto}: {real:.1f}")
            callback(real)

        slider.valueChanged.connect(ao_mudar)
        linha.addWidget(rotulo)
        linha.addWidget(slider)
        layout.addLayout(linha)
        return slider

    def _criar_slider_percent(
        self, layout, texto, valor_frac, callback, min_pct=0, max_pct=100
    ):
        pct = int(round(valor_frac * 100))

        linha = QHBoxLayout()
        rotulo = QLabel(f"{texto}: {pct}%")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_pct, max_pct)
        slider.setValue(pct)

        def ao_mudar(v):
            rotulo.setText(f"{texto}: {v}%")
            callback(v / 100.0)

        slider.valueChanged.connect(ao_mudar)
        linha.addWidget(rotulo)
        linha.addWidget(slider)
        layout.addLayout(linha)
        return slider

    def _criar_slider_int(self, layout, texto, minimo, maximo, valor, callback):
        linha = QHBoxLayout()
        rotulo = QLabel(f"{texto}: {valor} px")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(minimo, maximo)
        slider.setValue(valor)

        def ao_mudar(v):
            rotulo.setText(f"{texto}: {v} px")
            callback(v)

        slider.valueChanged.connect(ao_mudar)
        linha.addWidget(rotulo)
        linha.addWidget(slider)
        layout.addLayout(linha)
        return slider

    def _header(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("sectionHeader")
        return lbl

    def _pintar_botao(self, botao, cor_hex):
        botao.setStyleSheet(
            f"background-color: {cor_hex}; color: white; "
            f"border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 12px;"
        )

    def _repintar(self):
        self.overlay.forcar_repaint()
        self._save_timer.start()

    def _salvar(self):
        save_settings(self.settings)

    def _aplicar_captura_config(self):
        set_capture_hidden(int(self.winId()), self.settings.hide_everything)

    def _atualizar_label_imagem(self):
        nome = self.settings.image_path
        self.label_image.setText(nome if nome else "No image")

    def _atualizar_habilitacao(self):
        ligada = self.settings.crosshair_enabled
        segurar = self.settings.hold_to_show
        self.check_segurar.setEnabled(ligada)
        self.btn_gatilho.setEnabled(ligada and segurar)

    def _atualizar_habilitacao_imagem(self):
        usar = self.settings.use_image
        self.btn_choose_image.setEnabled(usar)
        self.slider_scale.setEnabled(usar)
        self.combo_forma.setEnabled(not usar)
        self.slider_size.setEnabled(not usar)
        self.slider_thickness.setEnabled(not usar)
        self.slider_gap.setEnabled(not usar)

    def _sync_crosshair(self):
        s = self.settings
        self.combo_forma.setCurrentIndex(self.combo_forma.findData(s.shape))
        self.check_outline.setChecked(s.outline_enabled)
        self.slider_size.setValue(round(s.length / PASSO))
        self.slider_thickness.setValue(round(s.thickness / PASSO))
        self.slider_gap.setValue(round(s.gap / PASSO))
        self.slider_opacity.setValue(round(s.opacity * 100))
        self._pintar_botao(self.btn_cor_principal, s.main_color)
        self._pintar_botao(self.btn_cor_outline, s.outline_color)
        self.check_use_image.setChecked(s.use_image)
        self.slider_scale.setValue(round(s.image_scale * 100))
        self._atualizar_label_imagem()
        self.overlay.reload_image()
        self._atualizar_habilitacao_imagem()

    def _sync_position(self):
        s = self.settings
        self.combo_monitor.setCurrentIndex(
            s.monitor_index if s.monitor_index < self.combo_monitor.count() else 0
        )
        self.slider_offx.setValue(s.offset_x)
        self.slider_offy.setValue(s.offset_y)
        self.overlay.apply_monitor()

    def _sync_visibility(self):
        s = self.settings
        self.check_mostrar.setChecked(s.crosshair_enabled)
        self.check_segurar.setChecked(s.hold_to_show)
        self.btn_gatilho.setText(button_name(s.trigger_button))
        self.check_hide_cross.setChecked(s.hide_crosshair)
        self.check_hide_all.setChecked(s.hide_everything)
        self._atualizar_habilitacao()
        self.overlay.apply_capture_affinity()
        self._aplicar_captura_config()

    def _reset_grupo(self, nomes):
        padrao = Settings()
        for nome in nomes:
            setattr(self.settings, nome, getattr(padrao, nome))

    def _reset_crosshair(self):
        self._reset_grupo(CAMPOS_CROSSHAIR)
        self._sync_crosshair()
        self._repintar()

    def _reset_position(self):
        self._reset_grupo(CAMPOS_POSITION)
        self._sync_position()
        self._repintar()

    def _reset_all(self):
        self._reset_grupo([campo.name for campo in fields(Settings)])
        self._sync_crosshair()
        self._sync_position()
        self._sync_visibility()
        self._repintar()

    def _forma_mudou(self, _index):
        self.settings.shape = self.combo_forma.currentData()
        self._repintar()

    def _use_image_mudou(self, _estado):
        self.settings.use_image = self.check_use_image.isChecked()
        self._atualizar_habilitacao_imagem()
        self._repintar()

    def _choose_image(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Choose image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if not caminho:
            return
        img = QImage(caminho)
        if img.isNull():
            self.label_image.setText("Invalid image")
            return

        img.save(app_path(NOME_IMAGEM), "PNG")
        self.settings.image_path = NOME_IMAGEM
        self.overlay.reload_image()
        self._atualizar_label_imagem()
        self._repintar()

    def _scale_mudou(self, frac):
        self.settings.image_scale = frac
        self._repintar()

    def _escolher_cor_principal(self):
        self._escolher_cor("main")

    def _escolher_cor_outline(self):
        self._escolher_cor("outline")

    def _escolher_cor(self, alvo):
        cor_original = (
            self.settings.main_color if alvo == "main" else self.settings.outline_color
        )
        seletor = QColorDialog(QColor(cor_original), self)
        seletor.setOption(QColorDialog.DontUseNativeDialog, True)

        def preview(cor):
            if alvo == "main":
                self.settings.main_color = cor.name()
            else:
                self.settings.outline_color = cor.name()
            self._repintar()

        seletor.currentColorChanged.connect(preview)

        if seletor.exec():
            cor_final = seletor.selectedColor().name()
            if alvo == "main":
                self.settings.main_color = cor_final
                self._pintar_botao(self.btn_cor_principal, cor_final)
            else:
                self.settings.outline_color = cor_final
                self._pintar_botao(self.btn_cor_outline, cor_final)
        else:
            if alvo == "main":
                self.settings.main_color = cor_original
            else:
                self.settings.outline_color = cor_original
        self._repintar()

    def _outline_mudou(self, _estado):
        self.settings.outline_enabled = self.check_outline.isChecked()
        self._repintar()

    def _length_mudou(self, v):
        self.settings.length = v
        self._repintar()

    def _thickness_mudou(self, v):
        self.settings.thickness = v
        self._repintar()

    def _gap_mudou(self, v):
        self.settings.gap = v
        self._repintar()

    def _opacity_mudou(self, frac):
        self.settings.opacity = frac
        self._repintar()

    def _monitor_mudou(self, _index):
        self.settings.monitor_index = self.combo_monitor.currentData()
        self.overlay.apply_monitor()
        self._repintar()

    def _offx_mudou(self, v):
        self.settings.offset_x = v
        self._repintar()

    def _offy_mudou(self, v):
        self.settings.offset_y = v
        self._repintar()

    def _mostrar_mudou(self, _estado):
        self.settings.crosshair_enabled = self.check_mostrar.isChecked()
        self._atualizar_habilitacao()
        self._repintar()

    def _segurar_mudou(self, _estado):
        self.settings.hold_to_show = self.check_segurar.isChecked()
        self._atualizar_habilitacao()
        self._repintar()

    def _hide_cross_mudou(self, _estado):
        self.settings.hide_crosshair = self.check_hide_cross.isChecked()
        self.overlay.apply_capture_affinity()
        self._repintar()

    def _hide_all_mudou(self, _estado):
        self.settings.hide_everything = self.check_hide_all.isChecked()
        self.overlay.apply_capture_affinity()
        self._aplicar_captura_config()
        self._repintar()

    def _iniciar_captura(self):
        self._capturando = True
        self._pronto_pra_capturar = False
        self.btn_gatilho.setText("Press a button... (Esc cancels)")
        self._captura_timer.start(30)

    def _verificar_captura(self):
        if not self._capturando:
            return
        pressionadas = [vk for vk in range(0x01, 0xFF) if is_key_pressed(vk)]
        if not self._pronto_pra_capturar:
            if not pressionadas:
                self._pronto_pra_capturar = True
            return
        if pressionadas:
            vk = pressionadas[0]
            if vk == 0x1B:
                self._finalizar_captura(salvar=False)
                return
            self.settings.trigger_button = vk
            self._finalizar_captura(salvar=True)

    def _finalizar_captura(self, salvar):
        self._capturando = False
        self._captura_timer.stop()
        self.btn_gatilho.setText(button_name(self.settings.trigger_button))
        if salvar:
            self._repintar()
