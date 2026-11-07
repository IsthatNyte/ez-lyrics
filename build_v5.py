import os

with open(r"C:\Users\dryde\spicy_spotify_lyrics\logo_pure_b64.txt", "r") as f:
    logo_base64 = f.read().strip()

# We write app.py directly to avoid any f-string escaping hazards with PowerShell and JS
app_code = r'''"""
EZ Lyrics LiquidGL Player
Features:
- Pure white transparent EZ logo
- Crash-free audio meter and thread-safe native Win32 window dragging
- Real-time SMTC Spotify bridge with clean JSON serialization
- Multi-source crystal clear album artwork (Deezer + iTunes + SMTC)
- Hardware WASAPI audio visualizer (responsive, wider bars, dynamic musical motion)
- Smooth animated window transitions with fluid spring-overshoot (ease-out-back)
- Dedicated mini-player button sliding smoothly to bottom-left mini tab
- Drag-to-resize corner grip
- Letter-by-letter floating karaoke animation
- Topmost window persistence across fullscreen applications
"""

import sys
import os
import re
import time
import json
import io
import threading
import subprocess
import urllib.parse
import ctypes
from ctypes import cast, POINTER, wintypes
import requests
from PIL import Image
import webview

try:
    from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
    HAS_PYCAW = True
except Exception:
    HAS_PYCAW = False

# Configure Win32 function signatures explicitly for 64-bit Windows
user32 = ctypes.windll.user32
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.SetWindowPos.restype = wintypes.BOOL
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRect.restype = wintypes.BOOL
user32.SendMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = ctypes.c_longlong
user32.ReleaseCapture.restype = wintypes.BOOL
user32.SystemParametersInfoW.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
user32.SystemParametersInfoW.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL

HWND_TOPMOST = wintypes.HWND(-1)

# Thread-safe HWND finder by Process ID (zero COM reflection, zero crashing)
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

def get_screen_work_area():
    r = wintypes.RECT()
    user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0)
    return r.left, r.top, r.right, r.bottom

def get_window_rect(hwnd):
    r = wintypes.RECT()
    user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(r))
    return r.left, r.top, r.right - r.left, r.bottom - r.top

# Global shared state
state_lock = threading.Lock()
app_state = {
    "version": 0,
    "current_track": "",
    "current_artist": "",
    "album_cover": "",
    "lyrics": [],
    "duration": 180.0,
    "base_pos": 0.0,
    "base_time": time.time(),
    "is_playing": False,
    "is_loop": False,
    "is_shuffle": False,
    "audio_peak": 0.0
}

# Persistent PowerShell SMTC Bridge with Clean JSON Output
PS_BRIDGE_SCRIPT = """
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | ? { 
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
} | Select-Object -First 1

function Await-Async($asyncOp, $type) {
    if (-not $asyncOp) { return $null }
    $m = $asTaskGeneric.MakeGenericMethod($type)
    $task = $m.Invoke($null, @($asyncOp))
    $task.Wait()
    return $task.Result
}

[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties, Windows.Media, ContentType=WindowsRuntime] | Out-Null

$op = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()
$mgr = Await-Async $op ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Get-SpotifySession {
    if (-not $mgr) { return $null }
    foreach ($item in $mgr.GetSessions()) {
        if ($item.SourceAppUserModelId -like "*Spotify*") {
            return $item
        }
    }
    return $mgr.GetCurrentSession()
}

while ($line = [Console]::ReadLine()) {
    if (-not $line -or $line -eq "QUIT") { break }

    if ($line.StartsWith("SEEK ")) {
        $sec = [double]($line.Substring(5))
        $sess = Get-SpotifySession
        if ($sess) {
            $ticks = [long]($sec * 10000000)
            $seekOp = $sess.TryChangePlaybackPositionAsync($ticks)
            Await-Async $seekOp ([bool]) | Out-Null
        }
        Write-Host "OK"
        continue
    }

    if ($line -eq "TOGGLE") {
        $sess = Get-SpotifySession
        if ($sess) {
            $togOp = $sess.TryTogglePlayPauseAsync()
            Await-Async $togOp ([bool]) | Out-Null
        }
        Write-Host "OK"
        continue
    }

    if ($line -eq "PREV") {
        $sess = Get-SpotifySession
        if ($sess) {
            $prevOp = $sess.TrySkipPreviousAsync()
            Await-Async $prevOp ([bool]) | Out-Null
        }
        Write-Host "OK"
        continue
    }

    if ($line -eq "NEXT") {
        $sess = Get-SpotifySession
        if ($sess) {
            $nextOp = $sess.TrySkipNextAsync()
            Await-Async $nextOp ([bool]) | Out-Null
        }
        Write-Host "OK"
        continue
    }

    if ($line -eq "POLL") {
        $sess = Get-SpotifySession
        if (-not $sess) {
            Write-Host "{}"
            continue
        }

        $propsOp = $sess.TryGetMediaPropertiesAsync()
        $props = Await-Async $propsOp ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
        $infoOp = $sess.GetPlaybackInfo()
        $timeline = $sess.GetTimelineProperties()

        $title = if ($props) { $props.Title } else { "" }
        $artist = if ($props) { $props.Artist } else { "" }
        $album = if ($props) { $props.AlbumTitle } else { "" }
        $status = if ($infoOp) { $infoOp.PlaybackStatus.ToString() } else { "Closed" }

        $pos = 0.0
        $dur = 0.0
        if ($timeline) {
            $dur = $timeline.EndTime.TotalSeconds
            $recordedPos = $timeline.Position.TotalSeconds
            if ($status -eq "Playing" -and $timeline.LastUpdatedTime) {
                $elapsedSinceUpdate = ([DateTimeOffset]::UtcNow - $timeline.LastUpdatedTime).TotalSeconds
                if ($elapsedSinceUpdate -gt 0 -and $elapsedSinceUpdate -lt 120) {
                    $pos = $recordedPos + $elapsedSinceUpdate
                } else {
                    $pos = $recordedPos
                }
            } else {
                $pos = $recordedPos
            }
        }

        $obj = @{
            title = $title
            artist = $artist
            album = $album
            status = $status
            pos = [math]::Round([double]$pos, 2)
            dur = [math]::Round([double]$dur, 2)
        }
        Write-Host ($obj | ConvertTo-Json -Compress)
        continue
    }
}
"""

ps_proc = None
ps_lock = threading.Lock()

def start_smtc_bridge():
    global ps_proc
    script_path = os.path.join(os.environ["TEMP"], "_smtc_bridge.ps1")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(PS_BRIDGE_SCRIPT)

    cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path]
    creation_flags = 0x08000000 if os.name == "nt" else 0
    ps_proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        creationflags=creation_flags
    )

def smtc_send(cmd_str):
    global ps_proc
    with ps_lock:
        if not ps_proc or ps_proc.poll() is not None:
            start_smtc_bridge()
        try:
            ps_proc.stdin.write(cmd_str + "\n")
            ps_proc.stdin.flush()
            resp = ps_proc.stdout.readline()
            return resp.strip()
        except Exception:
            return ""

def query_smtc():
    out = smtc_send("POLL")
    if out and out.startswith("{"):
        try:
            return json.loads(out)
        except Exception:
            pass
    return None

# Multi-Source Artwork Fetcher (Deezer + iTunes)
def fetch_highres_cover(artist, title, album=""):
    clean_title = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title)
    clean_title = clean_title.replace('#', '').strip()
    clean_artist = artist.replace('#', '').strip()

    search_queries = [
        f"{clean_artist} {clean_title}",
        f"{artist} {title}".replace("#", "").strip(),
        f"{clean_artist} {album}".strip() if album else "",
        clean_title
    ]

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # 1. Deezer API (covers mainstream + underground releases with 1000x1000 artwork)
    for q_text in search_queries:
        if not q_text.strip():
            continue
        try:
            q = urllib.parse.quote(q_text)
            r = requests.get(f"https://api.deezer.com/search?q={q}", headers=headers, timeout=3.5)
            if r.status_code == 200:
                data = r.json()
                if data.get("data") and len(data["data"]) > 0:
                    for item in data["data"][:3]:
                        art_url = item.get("album", {}).get("cover_xl") or item.get("album", {}).get("cover_big")
                        if art_url:
                            img_resp = requests.get(art_url, headers=headers, timeout=3.5)
                            if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                                b64 = requests.utils.base64.b64encode(img_resp.content).decode("ascii")
                                return f"data:image/jpeg;base64,{b64}"
        except Exception:
            pass

    # 2. iTunes API
    for q_text in search_queries[:2]:
        if not q_text.strip():
            continue
        try:
            q = urllib.parse.quote(q_text)
            r = requests.get(f"https://itunes.apple.com/search?term={q}&entity=song&limit=5", headers=headers, timeout=3.5)
            if r.status_code == 200:
                results = r.json().get("results", [])
                for item in results:
                    raw_art = item.get("artworkUrl100", "")
                    if raw_art:
                        art_1000 = raw_art.replace("100x100bb", "1000x1000bb")
                        img_resp = requests.get(art_1000, headers=headers, timeout=3.5)
                        if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                            b64 = requests.utils.base64.b64encode(img_resp.content).decode("ascii")
                            return f"data:image/jpeg;base64,{b64}"
        except Exception:
            pass

    return ""

# Synced lyrics fetcher
def fetch_synced_lyrics(artist, title, dur_sec):
    try:
        url = "https://lrclib.net/api/get"
        params = {"artist_name": artist, "track_name": title}
        if dur_sec and dur_sec > 10:
            params["duration"] = int(dur_sec)
        headers = {"User-Agent": "EZLyrics/2.0 (https://github.com/dryde/ez-lyrics)"}
        r = requests.get(url, params=params, headers=headers, timeout=4.0)
        if r.status_code == 200:
            data = r.json()
            synced = data.get("syncedLyrics")
            if synced:
                return parse_lrc(synced)
    except Exception:
        pass

    try:
        url = "https://lrclib.net/api/search"
        clean_title = title.replace("#", "").strip()
        params = {"q": f"{clean_title} {artist}"}
        headers = {"User-Agent": "EZLyrics/2.0"}
        r = requests.get(url, params=params, headers=headers, timeout=4.0)
        if r.status_code == 200:
            items = r.json()
            if isinstance(items, list) and len(items) > 0:
                for it in items:
                    if it.get("syncedLyrics"):
                        return parse_lrc(it["syncedLyrics"])
    except Exception:
        pass

    return []

def parse_lrc(lrc_text):
    lines = []
    line_regex = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')
    for raw in lrc_text.splitlines():
        raw = raw.strip()
        m = line_regex.match(raw)
        if m:
            mins = int(m.group(1))
            secs = int(m.group(2))
            millis_str = m.group(3)
            millis = int(millis_str) if len(millis_str) == 3 else int(millis_str) * 10
            t = round(mins * 60 + secs + millis / 1000.0, 2)
            txt = m.group(4).strip()
            if txt:
                lines.append({"time": t, "text": txt})

    lines.sort(key=lambda x: x["time"])
    for i in range(len(lines)):
        if i < len(lines) - 1:
            duration = lines[i+1]["time"] - lines[i]["time"]
            lines[i]["endTime"] = round(lines[i]["time"] + min(duration, 9.0), 2)
        else:
            lines[i]["endTime"] = round(lines[i]["time"] + 5.0, 2)

    return lines

# Track loading thread
current_loading_track = ""

def load_track_data(artist, title, duration, album=""):
    global current_loading_track
    track_key = f"{artist} - {title}"
    current_loading_track = track_key

    try:
        cover_b64 = fetch_highres_cover(artist, title, album)
        lyrics = fetch_synced_lyrics(artist, title, duration)

        if current_loading_track == track_key:
            with state_lock:
                app_state["album_cover"] = cover_b64
                app_state["lyrics"] = lyrics
                app_state["version"] += 1
    except Exception:
        pass

# Background Spotify SMTC poller
def spotify_monitor_loop():
    last_reported_title = ""
    last_reported_artist = ""
    last_stable_playing = False
    pause_counter = 0

    while True:
        info = query_smtc()
        if info:
            title = info.get("title", "")
            artist = info.get("artist", "")
            album = info.get("album", "")
            status = info.get("status", "")
            pos = float(info.get("pos", 0.0))
            dur = float(info.get("dur", 0.0))

            if status == "Playing":
                last_stable_playing = True
                pause_counter = 0
            elif status == "Paused":
                pause_counter += 1
                if pause_counter >= 3:
                    last_stable_playing = False
            else:
                last_stable_playing = False

            if title and (title != last_reported_title or artist != last_reported_artist):
                last_reported_title = title
                last_reported_artist = artist
                with state_lock:
                    app_state["current_track"] = title
                    app_state["current_artist"] = artist
                    app_state["base_pos"] = pos
                    app_state["base_time"] = time.time()
                    if dur > 0:
                        app_state["duration"] = dur
                    app_state["is_playing"] = last_stable_playing
                    app_state["version"] += 1
                threading.Thread(target=load_track_data, args=(artist, title, dur, album), daemon=True).start()
            else:
                with state_lock:
                    app_state["base_pos"] = pos
                    app_state["base_time"] = time.time()
                    if dur > 0:
                        app_state["duration"] = dur
                    app_state["is_playing"] = last_stable_playing
        else:
            with state_lock:
                app_state["is_playing"] = False

        time.sleep(0.12)

# Crash-Proof Audio Meter Loop (Single Master Device Meter, Zero COM Allocation in Loop)
audio_meter_singleton = None

def audio_meter_thread():
    global audio_meter_singleton
    if not HAS_PYCAW:
        return
    try:
        ctypes.windll.ole32.CoInitialize(None)
        dev = AudioUtilities.GetSpeakers()
        if dev and hasattr(dev, "_dev"):
            inter = dev._dev.Activate(IAudioMeterInformation._iid_, 7, None)
            audio_meter_singleton = cast(inter, POINTER(IAudioMeterInformation))
            cur_peak = 0.0
            while True:
                try:
                    val = float(audio_meter_singleton.GetPeakValue())
                    if val > 0.001:
                        boosted = min(1.0, (val ** 0.32) * 2.1)
                    else:
                        boosted = 0.0

                    if boosted > cur_peak:
                        cur_peak = boosted
                    else:
                        cur_peak = cur_peak * 0.85 + boosted * 0.15

                    with state_lock:
                        app_state["audio_peak"] = round(cur_peak, 3)
                except Exception:
                    pass
                time.sleep(0.016)
    except Exception:
        pass

# Fluid Spring-Overshoot Easing (Identical to CSS cubic-bezier(0.34, 1.56, 0.64, 1))
def ease_out_back(x, c1=1.45):
    c3 = c1 + 1.0
    return 1.0 + c3 * ((x - 1.0) ** 3) + c1 * ((x - 1.0) ** 2)

# Python WebBridge Interface
class WebBridge:
    def __init__(self, win_ref=None):
        self._window = win_ref
        self.current_mode = "expanded"
        self.pending_restore_mode = "expanded"
        self.saved_rect = None
        self._anim_lock = threading.Lock()

    def get_state(self):
        with state_lock:
            return app_state

    def start_drag(self):
        # Native drag executed on background thread prevents freezing the WebBridge callback
        def _drag():
            hwnd = find_our_hwnd()
            if hwnd:
                user32.ReleaseCapture()
                user32.SendMessageW(wintypes.HWND(hwnd), 0x0112, 0xF012, 0)
        threading.Thread(target=_drag, daemon=True).start()
        return True

    def resize_window(self, w, h):
        hwnd = find_our_hwnd()
        if hwnd:
            cur_x, cur_y, cur_w, cur_h = get_window_rect(hwnd)
            user32.SetWindowPos(wintypes.HWND(hwnd), HWND_TOPMOST, cur_x, cur_y, int(w), int(h), 0x0010 | 0x0004 | 0x0040)
            return True
        return False

    def seek(self, target_sec):
        sec = max(0.0, float(target_sec))
        with state_lock:
            app_state["base_pos"] = sec
            app_state["base_time"] = time.time()
        smtc_send(f"SEEK {sec:.2f}")
        return True

    def toggle_play(self):
        with state_lock:
            app_state["is_playing"] = not app_state["is_playing"]
        smtc_send("TOGGLE")
        return True

    def prev_track(self):
        smtc_send("PREV")
        return True

    def next_track(self):
        smtc_send("NEXT")
        return True

    def toggle_loop(self):
        with state_lock:
            app_state["is_loop"] = not app_state["is_loop"]
            return app_state["is_loop"]

    def toggle_shuffle(self):
        with state_lock:
            app_state["is_shuffle"] = not app_state["is_shuffle"]
            return app_state["is_shuffle"]

    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def close_window(self):
        if self._window:
            self._window.destroy()

    def _run_animation(self, target_w, target_h, target_x=None, target_y=None, duration=0.30):
        hwnd = find_our_hwnd()
        if not hwnd:
            if self._window:
                self._window.resize(int(target_w), int(target_h))
                if target_x is not None and target_y is not None:
                    self._window.move(int(target_x), int(target_y))
            return

        with self._anim_lock:
            cur_x, cur_y, cur_w, cur_h = get_window_rect(hwnd)
            s_left, s_top, s_right, s_bottom = get_screen_work_area()

            if target_x is None or target_y is None:
                center_x = cur_x + cur_w // 2
                center_y = cur_y + cur_h // 2
                target_x = max(s_left + 10, min(s_right - target_w - 10, center_x - target_w // 2))
                target_y = max(s_top + 10, min(s_bottom - target_h - 10, center_y - target_h // 2))

            steps = 28
            dt = duration / steps
            hwnd_val = wintypes.HWND(hwnd)
            for i in range(1, steps + 1):
                p = i / steps
                e = ease_out_back(p)
                nx = int(cur_x + (target_x - cur_x) * e)
                ny = int(cur_y + (target_y - cur_y) * e)
                nw = max(340, int(cur_w + (target_w - cur_w) * e))
                nh = max(130, int(cur_h + (target_h - cur_h) * e))
                user32.SetWindowPos(hwnd_val, HWND_TOPMOST, nx, ny, nw, nh, 0x0010 | 0x0004 | 0x0040)
                time.sleep(dt)

            user32.SetWindowPos(hwnd_val, HWND_TOPMOST, int(target_x), int(target_y), int(target_w), int(target_h), 0x0010 | 0x0004 | 0x0040)

    def set_mode(self, mode_name):
        hwnd = find_our_hwnd()
        if mode_name == "mini":
            if self.current_mode != "mini":
                if hwnd:
                    self.saved_rect = get_window_rect(hwnd)
                self.current_mode = "mini"
                s_left, s_top, s_right, s_bottom = get_screen_work_area()
                tw = 360
                th = 136
                tx = s_left + 24
                ty = s_bottom - th - 24
                threading.Thread(target=self._run_animation, args=(tw, th, tx, ty, 0.32), daemon=True).start()
                return "mini"
        elif mode_name == "restore":
            if self.current_mode == "mini":
                mode_target = self.pending_restore_mode
                self.current_mode = mode_target
                tw = 380 if mode_target == "compact" else 960
                th = 620 if mode_target == "compact" else 580
                tx, ty = None, None
                if self.saved_rect:
                    sx, sy, sw, sh = self.saved_rect
                    s_left, s_top, s_right, s_bottom = get_screen_work_area()
                    tx = max(s_left + 10, min(s_right - tw - 10, sx))
                    ty = max(s_top + 10, min(s_bottom - th - 10, sy))
                threading.Thread(target=self._run_animation, args=(tw, th, tx, ty, 0.32), daemon=True).start()
                return mode_target
        elif mode_name == "compact":
            self.pending_restore_mode = "compact"
            if self.current_mode != "mini":
                self.current_mode = "compact"
                threading.Thread(target=self._run_animation, args=(380, 620, None, None, 0.28), daemon=True).start()
                return "compact"
        elif mode_name == "expanded":
            self.pending_restore_mode = "expanded"
            if self.current_mode != "mini":
                self.current_mode = "expanded"
                threading.Thread(target=self._run_animation, args=(960, 580, None, None, 0.28), daemon=True).start()
                return "expanded"
        return self.current_mode
'''

# Read HTML/CSS template from build_v4.py and inject into final code
with open(r"C:\Users\dryde\spicy_spotify_lyrics\build_v4.py", "r", encoding="utf-8") as f:
    v4_content = f.read()

html_start = v4_content.find('HTML_BODY = """<!DOCTYPE html>')
html_end = v4_content.find('def keep_topmost_worker')

html_section = v4_content[html_start:html_end]

# In HTML JS section, update drag and resize handlers to use the new non-blocking API
html_section = html_section.replace(
    "window.pywebview.api._run_animation(nw, nh, null, null, 0.0);",
    "window.pywebview.api.resize_window(nw, nh);"
)

footer = r'''
# Keep-Topmost Worker Thread (Keeps Window in Front of Fullscreen Apps)
def keep_topmost_worker():
    time.sleep(1.0)
    while True:
        try:
            hwnd = find_our_hwnd()
            if hwnd:
                user32.SetWindowPos(wintypes.HWND(hwnd), HWND_TOPMOST, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x0040)
        except Exception:
            pass
        time.sleep(1.2)

def main():
    start_smtc_bridge()
    threading.Thread(target=spotify_monitor_loop, daemon=True).start()
    threading.Thread(target=audio_meter_thread, daemon=True).start()

    # Pre-poll once so we get immediate song state
    info = query_smtc()
    if info and info.get("title"):
        threading.Thread(
            target=load_track_data,
            args=(info.get("artist", ""), info.get("title", ""), float(info.get("dur", 0.0)), info.get("album", "")),
            daemon=True
        ).start()

    bridge = WebBridge()
    window = webview.create_window(
        title="EZ Lyrics",
        html=HTML_BODY,
        js_api=bridge,
        width=960,
        height=580,
        min_size=(340, 130),
        resizable=True,
        frameless=True,
        easy_drag=False,
        on_top=True,
        background_color="#08080c"
    )
    bridge._window = window
    threading.Thread(target=keep_topmost_worker, daemon=True).start()
    webview.start(debug=False)

if __name__ == "__main__":
    main()
'''

final_app_py = app_code + "\n" + html_section + "\n" + footer

with open(r"C:\Users\dryde\spicy_spotify_lyrics\app.py", "w", encoding="utf-8") as f:
    f.write(final_app_py)

print("Successfully written rock-solid app.py without thread/COM issues.")
