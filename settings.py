from dataclasses import dataclass


@dataclass
class Settings:
    shape: str = "cross"
    main_color: str = "#6F42E0"
    outline_color: str = "#000000"
    outline_enabled: bool = True
    length: float = 8.0
    thickness: float = 2.0
    gap: float = 4.0
    outline_thickness: float = 2.0
    opacity: float = 1.0

    use_image: bool = False
    image_path: str = ""
    image_scale: float = 0.10

    monitor_index: int = 0
    offset_x: int = 0
    offset_y: int = 0

    crosshair_enabled: bool = True
    hold_to_show: bool = False
    trigger_button: int = 0x02

    hide_crosshair: bool = False
    hide_everything: bool = False
