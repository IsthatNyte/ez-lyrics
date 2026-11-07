import webview, threading, time, ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
user32.PostMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL
user32.ReleaseCapture.restype = wintypes.BOOL

class Api:
    def __init__(self):
        self.w = None
    def test_post(self):
        hwnd = self.w.native.Handle.ToInt64()
        user32.ReleaseCapture()
        ret = user32.PostMessageW(wintypes.HWND(hwnd), 0x0112, 0xF012, 0)
        print('PostMessage ret:', ret)
        return ret

api = Api()
w = webview.create_window('TestDrag', html='<h1>Drag test</h1>', js_api=api)
api.w = w

def check():
    time.sleep(1.0)
    api.test_post()
    time.sleep(0.5)
    w.destroy()

threading.Thread(target=check, daemon=True).start()
webview.start()
