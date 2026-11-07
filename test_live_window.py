import webview, threading, time, os, ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.SetWindowPos.restype = wintypes.BOOL

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
    def resize_window(self, w, h):
        h_val = find_our_hwnd()
        if h_val:
            user32.SetWindowPos(wintypes.HWND(h_val), wintypes.HWND(-1), 100, 100, int(w), int(h), 0x0040)
            return True
        return False

api = Api()
w = webview.create_window('TestLive', html='<h1>Live test</h1>', js_api=api)

def bg():
    time.sleep(1.0)
    print('Calling api.resize_window(500, 300)...')
    ret = api.resize_window(500, 300)
    print('Result:', ret)
    time.sleep(0.5)
    w.destroy()

threading.Thread(target=bg, daemon=True).start()
webview.start()
