import re

# 1. Update app.py
app_path = r"C:\Users\dryde\spicy_spotify_lyrics\app.py"
with open(app_path, "r", encoding="utf-8") as f:
    app_text = f.read()

# Add resource_path helper
if "def resource_path(" not in app_text:
    app_text = app_text.replace(
        '# Configure Win32 function signatures explicitly for 64-bit Windows',
        '''def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Configure Win32 function signatures explicitly for 64-bit Windows'''
    )

# Add WebView2 environment optimizations
if "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS" not in app_text:
    app_text = app_text.replace(
        'import webview',
        '''import webview

os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (
    "--disable-background-networking "
    "--disable-background-timer-throttling "
    "--disable-backgrounding-occluded-windows "
    "--disable-breakpad "
    "--disable-component-update "
    "--disable-features=Translate,OptimizationHints,MediaRouter "
    "--enable-features=VaapiVideoDecoder "
    "--no-default-browser-check "
    "--process-per-site"
)'''
    )

# Update WebBridge in app.py with get_telemetry and get_track_details (eliminates 1.9GB memory leak)
old_bridge_methods = """    def get_state(self):
        with state_lock:
            return app_state"""

new_bridge_methods = """    def get_telemetry(self):
        with state_lock:
            return {
                "version": app_state["version"],
                "pos": app_state["base_pos"],
                "dur": app_state["duration"],
                "is_playing": app_state["is_playing"],
                "peak": app_state["audio_peak"],
                "loop": app_state["is_loop"],
                "shuffle": app_state["is_shuffle"]
            }

    def get_track_details(self):
        with state_lock:
            return {
                "version": app_state["version"],
                "title": app_state["current_track"],
                "artist": app_state["current_artist"],
                "cover": app_state["album_cover"],
                "lyrics": app_state["lyrics"],
                "duration": app_state["duration"]
            }

    def get_state(self):
        with state_lock:
            return app_state"""

if old_bridge_methods in app_text:
    app_text = app_text.replace(old_bridge_methods, new_bridge_methods, 1)

# In main(), use resource_path("index.html")
old_main_load = """    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(html_file, "r", encoding="utf-8") as f:
        html_code = f.read()"""

new_main_load = """    html_file = resource_path("index.html")
    with open(html_file, "r", encoding="utf-8") as f:
        html_code = f.read()"""

if old_main_load in app_text:
    app_text = app_text.replace(old_main_load, new_main_load, 1)

# Add periodic working set memory trimmer
if "def memory_trimmer_worker():" not in app_text:
    app_text = app_text.replace(
        'def main():',
        '''def memory_trimmer_worker():
    while True:
        time.sleep(30.0)
        try:
            ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        except Exception:
            pass

def main():
    threading.Thread(target=memory_trimmer_worker, daemon=True).start()'''
    )

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_text)

print("SUCCESS: app.py optimized!")
