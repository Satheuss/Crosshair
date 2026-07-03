BG = "#000021"
SURFACE = "#141414"
SURFACE_HOVER = "#1E1E2E"
ACCENT = "#6F42E0"
ACCENT_HOVER = "#8259EA"
ACCENT_PRESSED = "#5A34C0"
TEXT = "#EDEDF5"
TEXT_MUTED = "#9A9AB0"
BORDER = "#24243A"


FONT_SANS = '"Times New Roman", "Times", serif'

FONT_SERIF = '"Cormorant Garamond", "Playfair Display", Georgia, serif'


def build_qss() -> str:
    return f"""
    QWidget {{
        background-color: {BG};
        color: {TEXT};
        font-family: {FONT_SANS};
        font-size: 13px;
    }}
    QLabel {{ background: transparent; color: {TEXT}; }}
    QLabel#sectionHeader {{
        font-family: {FONT_SERIF};
        font-style: italic;
        font-size: 18px;
        color: {ACCENT};
        padding-top: 6px;
    }}

    QPushButton {{
        background-color: {SURFACE};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 12px;
    }}
    QPushButton:hover {{ background-color: {SURFACE_HOVER}; border-color: {ACCENT}; }}
    QPushButton:pressed {{ background-color: {ACCENT_PRESSED}; border-color: {ACCENT_PRESSED}; }}
    QPushButton:disabled {{ color: {TEXT_MUTED}; border-color: {BORDER}; }}

    QComboBox {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 4px 8px;
    }}
    QComboBox:hover {{ border-color: {ACCENT}; }}
    QComboBox:disabled {{ color: {TEXT_MUTED}; }}
    QComboBox QAbstractItemView {{
        background-color: {SURFACE};
        color: {TEXT};
        selection-background-color: {ACCENT};
        border: 1px solid {BORDER};
        outline: none;
    }}

    QCheckBox {{ color: {TEXT}; spacing: 8px; background: transparent; }}
    QCheckBox:disabled {{ color: {TEXT_MUTED}; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border: 1px solid {BORDER};
        border-radius: 4px;
        background: {SURFACE};
    }}
    QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}

    QSlider::groove:horizontal {{ height: 4px; background: {BORDER}; border-radius: 2px; }}
    QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
    QSlider::handle:horizontal {{
        background: {ACCENT};
        width: 14px; height: 14px;
        margin: -6px 0;
        border-radius: 7px;
    }}
    QSlider::handle:horizontal:hover {{ background: {ACCENT_HOVER}; }}
    QSlider:disabled {{ }}
    QSlider::sub-page:horizontal:disabled {{ background: {BORDER}; }}
    QSlider::handle:horizontal:disabled {{ background: {TEXT_MUTED}; }}

    QTabWidget::pane {{ border: 1px solid {BORDER}; border-radius: 6px; background: {BG}; top: -1px; }}
    QTabBar::tab {{
        background: {SURFACE};
        color: {TEXT};
        padding: 6px 14px;
        border: 1px solid {BORDER};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{ background: {ACCENT}; color: #FFFFFF; }}
    QTabBar::tab:hover:!selected {{ background: {SURFACE_HOVER}; }}
    """
