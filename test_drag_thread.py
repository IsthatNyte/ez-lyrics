import webview, threading, time, os, ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.SendMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = ctypes.c_longlong
user32.ReleaseCapture.restype = wintypes.BOOL

def find_our_hwnd():
    pid = os.getpid()
    found = []
    def enum_cb(h, _):
        lp = wintypes.DWORD()
        user32.GetWindowThreadProcessId(h, ctypes.byref(lp))
        if lp.value == pid and user32.IsWindowVisible(h):
            found.append(h)
        return True
    CB = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(CB(enum_cb), 0)
    return found[0] if found else None

class Api:
    def start_drag(self):
        def _drag():
            h = find_our_hwnd()
            if h:
                user32.ReleaseCapture()
                user32.SendMessageW(wintypes.HWND(h), 0x0112, 0xF012, 0)
        threading.Thread(target=_drag, daemon=True).start()
        return True

api = Api()
w = webview.create_window('TestDragThread', html='<h1>Testing Drag Thread</h1>', js_api=api)

def check():
    time.sleep(1.0)
    print('Testing start_drag call...')
    api.start_drag()
    time.sleep(0.5)
    w.destroy()

threading.Thread(target=check, daemon=True).start()
webview.start()
