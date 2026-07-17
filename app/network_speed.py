"""Real-time network throughput via the Windows IP Helper API (GetIfTable2),
plus taskbar-rectangle lookups for docking a speed readout next to the
system tray. Ported from the standalone SpeedTray.pyw utility -- same
ctypes logic, with the Tkinter-specific window/theme code left out (the Qt
overlay widget replaces that part).
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes

IF_MAX_STRING_SIZE = 256
IF_MAX_PHYS_ADDRESS_LENGTH = 32


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class MIB_IF_ROW2(ctypes.Structure):
    _fields_ = [
        ("InterfaceLuid", ctypes.c_uint64),
        ("InterfaceIndex", wintypes.ULONG),
        ("InterfaceGuid", GUID),
        ("Alias", wintypes.WCHAR * (IF_MAX_STRING_SIZE + 1)),
        ("Description", wintypes.WCHAR * (IF_MAX_STRING_SIZE + 1)),
        ("PhysicalAddressLength", wintypes.ULONG),
        ("PhysicalAddress", ctypes.c_ubyte * IF_MAX_PHYS_ADDRESS_LENGTH),
        ("PermanentPhysicalAddress", ctypes.c_ubyte * IF_MAX_PHYS_ADDRESS_LENGTH),
        ("Mtu", wintypes.ULONG),
        ("Type", wintypes.ULONG),
        ("TunnelType", ctypes.c_int),
        ("MediaType", ctypes.c_int),
        ("PhysicalMediumType", ctypes.c_int),
        ("AccessType", ctypes.c_int),
        ("DirectionType", ctypes.c_int),
        ("InterfaceAndOperStatusFlags", ctypes.c_ubyte),
        ("OperStatus", ctypes.c_int),
        ("AdminStatus", ctypes.c_int),
        ("MediaConnectState", ctypes.c_int),
        ("NetworkGuid", GUID),
        ("ConnectionType", ctypes.c_int),
        ("TransmitLinkSpeed", ctypes.c_uint64),
        ("ReceiveLinkSpeed", ctypes.c_uint64),
        ("InOctets", ctypes.c_uint64),
        ("InUcastPkts", ctypes.c_uint64),
        ("InNUcastPkts", ctypes.c_uint64),
        ("InDiscards", ctypes.c_uint64),
        ("InErrors", ctypes.c_uint64),
        ("InUnknownProtos", ctypes.c_uint64),
        ("InUcastOctets", ctypes.c_uint64),
        ("InMulticastOctets", ctypes.c_uint64),
        ("InBroadcastOctets", ctypes.c_uint64),
        ("OutOctets", ctypes.c_uint64),
        ("OutUcastPkts", ctypes.c_uint64),
        ("OutNUcastPkts", ctypes.c_uint64),
        ("OutDiscards", ctypes.c_uint64),
        ("OutErrors", ctypes.c_uint64),
        ("OutUcastOctets", ctypes.c_uint64),
        ("OutMulticastOctets", ctypes.c_uint64),
        ("OutBroadcastOctets", ctypes.c_uint64),
        ("OutQLen", ctypes.c_uint64),
    ]


class MIB_IF_TABLE2(ctypes.Structure):
    _fields_ = [("NumEntries", wintypes.ULONG), ("Table", MIB_IF_ROW2 * 1)]


class NetworkCounters:
    def __init__(self) -> None:
        self.dll = ctypes.WinDLL("iphlpapi.dll")
        self.get_table = self.dll.GetIfTable2
        self.get_table.argtypes = [ctypes.POINTER(ctypes.POINTER(MIB_IF_TABLE2))]
        self.get_table.restype = wintypes.ULONG
        self.free_table = self.dll.FreeMibTable
        self.free_table.argtypes = [ctypes.c_void_p]

    def read(self) -> dict[int, tuple[int, int]]:
        pointer = ctypes.POINTER(MIB_IF_TABLE2)()
        result = self.get_table(ctypes.byref(pointer))
        if result:
            raise OSError(result, "GetIfTable2 failed")

        physical: dict[int, tuple[int, int]] = {}
        fallback: dict[int, tuple[int, int]] = {}
        try:
            count = pointer.contents.NumEntries
            rows = ctypes.cast(
                ctypes.addressof(pointer.contents.Table),
                ctypes.POINTER(MIB_IF_ROW2),
            )
            for index in range(count):
                row = rows[index]
                alias = row.Alias
                # Up, non-loopback interfaces only. The -0000 rows are Windows
                # filter layers whose byte counts duplicate their parent adapter.
                if row.OperStatus != 1 or row.Type == 24 or alias.endswith("-0000"):
                    continue
                values = (int(row.InOctets), int(row.OutOctets))
                fallback[int(row.InterfaceIndex)] = values
                if row.InterfaceAndOperStatusFlags & 1:  # HardwareInterface
                    physical[int(row.InterfaceIndex)] = values
            return physical or fallback
        finally:
            self.free_table(pointer)


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def taskbar_rects() -> tuple[RECT | None, RECT | None]:
    """Return the taskbar and notification-area rectangles from Explorer."""
    user32 = ctypes.WinDLL("user32")
    find_window = user32.FindWindowW
    find_window.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    find_window.restype = wintypes.HWND
    find_child = user32.FindWindowExW
    find_child.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
    find_child.restype = wintypes.HWND
    get_rect = user32.GetWindowRect
    get_rect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
    get_rect.restype = wintypes.BOOL

    taskbar_hwnd = find_window("Shell_TrayWnd", None)
    bar = RECT()
    if not taskbar_hwnd or not get_rect(taskbar_hwnd, ctypes.byref(bar)):
        return None, None

    tray_hwnd = find_child(taskbar_hwnd, None, "TrayNotifyWnd", None)
    tray = RECT()
    if not tray_hwnd or not get_rect(tray_hwnd, ctypes.byref(tray)):
        return bar, None
    return bar, tray


def default_position(window_width: int, window_height: int) -> tuple[int, int]:
    bar, tray = taskbar_rects()
    if bar:
        bar_width = bar.right - bar.left
        bar_height = bar.bottom - bar.top
        if bar_width >= bar_height:  # Normal horizontal taskbar.
            if tray and tray.left > bar.left + bar_width // 2:
                x = tray.left - window_width - 8
            elif tray:
                x = tray.right + 8
            else:
                x = bar.right - window_width - 245
            x = max(bar.left, min(x, bar.right - window_width))
            y = bar.top + max(0, (bar_height - window_height) // 2)
        else:  # Vertical taskbar.
            x = bar.left + max(0, (bar_width - window_width) // 2)
            if tray and tray.top > bar.top + bar_height // 2:
                y = tray.top - window_height - 8
            elif tray:
                y = tray.bottom + 8
            else:
                y = bar.bottom - window_height - 170
            y = max(bar.top, min(y, bar.bottom - window_height))
        return x, y
    return 100, 100


def taskbar_colors() -> tuple[str, str]:
    """Match the Windows system/taskbar theme and keep the text readable."""
    import winreg
    theme_key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, theme_key) as key:
            light_theme, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
        return ("#f3f3f3", "#111111") if light_theme else ("#1f1f1f", "#ffffff")
    except (FileNotFoundError, OSError):
        return "#1f1f1f", "#ffffff"


def format_rate(bytes_per_second: float) -> str:
    bits_per_second = max(0.0, bytes_per_second * 8.0)
    if bits_per_second >= 1_000_000:
        return f"{bits_per_second / 1_000_000:.1f} Mb/s"
    return f"{bits_per_second / 1_000:.1f} Kb/s"
