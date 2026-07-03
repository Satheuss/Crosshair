import ctypes
from ctypes import wintypes

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020


WDA_NONE = 0x00000000
WDA_EXCLUDEFROMCAPTURE = 0x00000011


def make_click_through(hwnd: int) -> None:
    user32 = ctypes.windll.user32
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]

    estilo = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, estilo | WS_EX_LAYERED | WS_EX_TRANSPARENT)


def set_capture_hidden(hwnd: int, hidden: bool) -> bool:
    user32 = ctypes.windll.user32
    user32.SetWindowDisplayAffinity.restype = wintypes.BOOL
    user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
    afinidade = WDA_EXCLUDEFROMCAPTURE if hidden else WDA_NONE
    return bool(user32.SetWindowDisplayAffinity(hwnd, afinidade))


def is_key_pressed(vk_code: int) -> bool:
    return bool(ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000)


def set_app_id(app_id: str) -> None:
    try:
        shell32 = ctypes.windll.shell32
        shell32.SetCurrentProcessExplicitAppUserModelID.argtypes = [ctypes.c_wchar_p]
        shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


_SPECIAL_NAMES = {
    0x01: "Left Mouse (M1)",
    0x02: "Right Mouse (M2)",
    0x04: "Middle Mouse (M3)",
    0x05: "Mouse Side (M4)",
    0x06: "Mouse Side (M5)",
    0x08: "Backspace",
    0x09: "Tab",
    0x0D: "Enter",
    0x10: "Shift",
    0x11: "Ctrl",
    0x12: "Alt",
    0x14: "CapsLock",
    0x1B: "Esc",
    0x20: "Space",
}


def button_name(vk_code: int) -> str:
    if vk_code in _SPECIAL_NAMES:
        return _SPECIAL_NAMES[vk_code]
    if 0x30 <= vk_code <= 0x39:
        return chr(vk_code)
    if 0x41 <= vk_code <= 0x5A:
        return chr(vk_code)
    if 0x70 <= vk_code <= 0x7B:
        return f"F{vk_code - 0x6F}"
    return f"Key 0x{vk_code:02X}"
