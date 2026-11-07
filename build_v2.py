import os

with open(r"C:\Users\dryde\spicy_spotify_lyrics\logo_pure_b64.txt", "r") as f:
    logo_base64 = f.read().strip()

parts = []

parts.append(r'''"""
EZ Lyrics LiquidGL Player
Features:
- Pure white transparent EZ logo
- Hardware WASAPI audio visualizer (ultra-responsive power boost)
- Smooth animated window transitions between expanded, compact, and mini modes
- Sliding to bottom-left corner mini tab with bottom-edge visualizer
- Letter-by-letter floating karaoke animation
- Topmost window persistence across fullscreen applications
- Accurate album artwork & synchronized LRCLIB lyrics
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

# Persistent PowerShell SMTC Bridge with Accurate Elapsed Time Calculation
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

        $hasCover = $false
        if ($props -and $props.Thumbnail) {
            try {
                $thumbStreamOp = $props.Thumbnail.OpenReadAsync()
                $thumbStream = Await-Async $thumbStreamOp ([Windows.Storage.Streams.IRandomAccessStreamWithContentType])
                if ($thumbStream) {
                    $stream = $thumbStream.AsStreamForRead()
                    $bytes = New-Object byte[] $stream.Length
                    $stream.Read($bytes, 0, $stream.Length) | Out-Null
                    [IO.File]::WriteAllBytes("$env:TEMP\\smtc_cover.jpg", $bytes)
                    $hasCover = $true
                }
            } catch {}
        }

        $cleanTitle = ($title -replace '[\\r\\n\\t"]', ' ').Trim()
        $cleanArtist = ($artist -replace '[\\r\\n\\t"]', ' ').Trim()
        $cleanAlbum = ($album -replace '[\\r\\n\\t"]', ' ').Trim()

        $json = [string]::Format(
            '{{"title":"{0}","artist":"{1}","album":"{2}","status":"{3}","pos":{4:F2},"dur":{5:F2},"has_cover":{6}}}',
            $cleanTitle, $cleanArtist, $cleanAlbum, $status, $pos, $dur, $(if ($hasCover) { "true" } else { "false" })
        )
        Write-Host $json
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

# Artwork fetcher
def fetch_highres_cover(artist, title):
    try:
        q = urllib.parse.quote(f"{title} {artist}")
        r = requests.get(f"https://itunes.apple.com/search?term={q}&entity=song&limit=5", timeout=3.5)
        if r.status_code == 200:
            results = r.json().get("results", [])
            for item in results:
                raw_art = item.get("artworkUrl100", "")
                if raw_art:
                    art_1000 = raw_art.replace("100x100bb", "1000x1000bb")
                    img_resp = requests.get(art_1000, timeout=3.5)
                    if img_resp.status_code == 200:
                        return f"data:image/jpeg;base64,{requests.utils.base64.b64encode(img_resp.content).decode('ascii')}"
    except Exception:
        pass

    temp_cover = os.path.join(os.environ["TEMP"], "smtc_cover.jpg")
    if os.path.exists(temp_cover):
        try:
            with open(temp_cover, "rb") as f:
                raw_bytes = f.read()
            if len(raw_bytes) > 500:
                return f"data:image/jpeg;base64,{requests.utils.base64.b64encode(raw_bytes).decode('ascii')}"
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
        params = {"q": f"{title} {artist}"}
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

def load_track_data(artist, title, duration):
    global current_loading_track
    track_key = f"{artist} - {title}"
    current_loading_track = track_key

    cover_b64 = fetch_highres_cover(artist, title)
    lyrics = fetch_synced_lyrics(artist, title, duration)

    if current_loading_track == track_key:
        with state_lock:
            app_state["album_cover"] = cover_b64
            app_state["lyrics"] = lyrics
            app_state["version"] += 1

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
                threading.Thread(target=load_track_data, args=(artist, title, dur), daemon=True).start()
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

# Hardware Audio Meter Loop (Ultra-Responsive Non-Linear Power Curve)
def audio_meter_thread():
    if not HAS_PYCAW:
        return
    try:
        dev = AudioUtilities.GetSpeakers()
        if dev and hasattr(dev, "_dev"):
            inter = dev._dev.Activate(IAudioMeterInformation._iid_, 7, None)
            meter = cast(inter, POINTER(IAudioMeterInformation))
            cur_peak = 0.0
            while True:
                try:
                    p = float(meter.GetPeakValue())
                    # Lift quiet and moderate volumes into prominent bouncing peaks
                    if p > 0.002:
                        boosted = min(1.0, (p ** 0.35) * 1.9)
                    else:
                        boosted = 0.0
                    # Instant snap attack, smooth organic decay
                    if boosted > cur_peak:
                        cur_peak = boosted
                    else:
                        cur_peak = cur_peak * 0.88 + boosted * 0.12
                    with state_lock:
                        app_state["audio_peak"] = round(cur_peak, 3)
                except Exception:
                    pass
                time.sleep(0.016) # ~60Hz sampling rate
    except Exception:
        pass

# Screen Work Area & Window Helpers
def get_screen_work_area():
    r = wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0)
    return r.left, r.top, r.right, r.bottom

def get_window_rect(hwnd):
    r = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right - r.left, r.bottom - r.top

# Python WebBridge Interface
class WebBridge:
    def __init__(self, win_ref=None):
        self._window = win_ref
        self._hwnd = None
        self.current_mode = "expanded" # "expanded", "compact", "mini"
        self.pending_restore_mode = "expanded"
        self.saved_rect = None
        self._anim_lock = threading.Lock()

    def get_hwnd(self):
        if self._hwnd:
            return self._hwnd
        if self._window and hasattr(self._window, "native") and hasattr(self._window.native, "Handle"):
            try:
                self._hwnd = int(self._window.native.Handle)
                return self._hwnd
            except Exception:
                pass
        h = ctypes.windll.user32.FindWindowW(None, "EZ Lyrics")
        if h:
            self._hwnd = h
        return self._hwnd

    def get_state(self):
        with state_lock:
            return app_state

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

    def _run_animation(self, target_w, target_h, target_x=None, target_y=None, duration=0.26):
        hwnd = self.get_hwnd()
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

            steps = 22
            dt = duration / steps
            for i in range(1, steps + 1):
                p = i / steps
                # ease-out cubic
                e = 1.0 - (1.0 - p) ** 3
                nx = int(cur_x + (target_x - cur_x) * e)
                ny = int(cur_y + (target_y - cur_y) * e)
                nw = int(cur_w + (target_w - cur_w) * e)
                nh = int(cur_h + (target_h - cur_h) * e)
                ctypes.windll.user32.SetWindowPos(hwnd, -1, nx, ny, nw, nh, 0x0010 | 0x0004 | 0x0040)
                time.sleep(dt)

            ctypes.windll.user32.SetWindowPos(hwnd, -1, int(target_x), int(target_y), int(target_w), int(target_h), 0x0010 | 0x0004 | 0x0040)

    def set_mode(self, mode_name):
        hwnd = self.get_hwnd()
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
                threading.Thread(target=self._run_animation, args=(tw, th, tx, ty, 0.28), daemon=True).start()
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
                threading.Thread(target=self._run_animation, args=(tw, th, tx, ty, 0.28), daemon=True).start()
                return mode_target
        elif mode_name == "compact":
            self.pending_restore_mode = "compact"
            if self.current_mode != "mini":
                self.current_mode = "compact"
                threading.Thread(target=self._run_animation, args=(380, 620, None, None, 0.26), daemon=True).start()
                return "compact"
        elif mode_name == "expanded":
            self.pending_restore_mode = "expanded"
            if self.current_mode != "mini":
                self.current_mode = "expanded"
                threading.Thread(target=self._run_animation, args=(960, 580, None, None, 0.26), daemon=True).start()
                return "expanded"
        return self.current_mode
''')

# Now add HTML, CSS, and JS
parts.append(f'''
HTML_BODY = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>EZ Lyrics</title>
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
    -webkit-user-select: none;
    -webkit-app-region: no-drag !important;
  }}

  html, body {{
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #ffffff;
    border-radius: 0;
    margin: 0;
    padding: 0;
  }}

  /* Full Window Crossfading Backgrounds */
  .bg-layer {{
    position: fixed;
    top: -20px;
    left: -20px;
    width: calc(100vw + 40px);
    height: calc(100vh + 40px);
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: blur(28px) saturate(140%) brightness(0.72);
    transition: opacity 0.85s cubic-bezier(0.25, 1, 0.5, 1);
    z-index: 0;
    pointer-events: none;
  }}
  #bgLayerA {{ opacity: 1; }}
  #bgLayerB {{ opacity: 0; }}

  /* Full Mode App Container */
  .app-container {{
    position: relative;
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    z-index: 1;
    overflow: hidden;
  }}

  /* Custom Rounded Frameless Titlebar */
  .custom-titlebar {{
    height: 38px;
    min-height: 38px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 14px;
    background: rgba(18, 18, 22, 0.65);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    -webkit-app-region: drag !important;
    z-index: 20;
    cursor: default;
  }}

  .titlebar-left {{
    display: flex;
    align-items: center;
    gap: 8px;
    -webkit-app-region: drag !important;
  }}

  .app-logo-img {{
    height: 22px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));
    -webkit-app-region: no-drag !important;
    pointer-events: none;
  }}

  .titlebar-center {{
    font-size: 13px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.85);
    letter-spacing: 0.3px;
    display: none;
    -webkit-app-region: drag !important;
  }}

  .window-controls {{
    display: flex;
    align-items: center;
    gap: 6px;
    -webkit-app-region: no-drag !important;
  }}

  .win-btn {{
    width: 28px;
    height: 24px;
    border: none;
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.85);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s ease;
    -webkit-app-region: no-drag !important;
  }}
  .win-btn:hover {{
    background: rgba(255, 255, 255, 0.22);
    color: #ffffff;
  }}
  .win-close:hover {{
    background: #e81123 !important;
    color: #ffffff !important;
  }}

  /* Main Workspace */
  .main-container {{
    flex: 1;
    display: flex;
    padding: 24px 28px;
    gap: 28px;
    overflow: hidden;
    align-items: center;
    justify-content: center;
    transition: all 0.28s cubic-bezier(0.25, 1, 0.5, 1);
  }}

  /* Left Panel: Cover & LiquidGL Controls Card */
  .left-panel {{
    width: 330px;
    min-width: 330px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    transition: all 0.28s cubic-bezier(0.25, 1, 0.5, 1);
  }}

  .cover-container {{
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 18px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.12);
  }}
  .cover-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: opacity 0.4s ease;
  }}

  .track-meta {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .track-title {{
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }}
  .track-artist {{
    font-size: 14px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.72);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  /* Authentic LiquidGL Card */
  .liquidgl-card {{
    position: relative;
    padding: 16px 18px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.09);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.22);
    box-shadow:
      0 16px 40px rgba(0, 0, 0, 0.4),
      inset 0 1px 1px rgba(255, 255, 255, 0.4),
      inset 0 -1px 1px rgba(0, 0, 0, 0.25);
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  /* Hardware Vocalizer Wave Canvas */
  .vocalizer-container {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
  }}
  .vocalizer-box {{
    position: relative;
    width: 100%;
    height: 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
  }}
  #waveCanvas {{
    width: 100%;
    height: 100%;
    display: block;
  }}

  .time-row {{
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.65);
    letter-spacing: 0.5px;
  }}

  /* 5-Button Transport Controls */
  .controls-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4px;
  }}

  .ctrl-btn {{
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.75);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);
  }}
  .ctrl-btn:hover {{
    color: #ffffff;
    background: rgba(255, 255, 255, 0.12);
    transform: scale(1.08);
  }}
  .ctrl-btn.active {{
    color: #1db954;
  }}

  /* Morphing Play/Pause Button */
  .play-morph-btn {{
    width: 46px;
    height: 46px;
    background: #ffffff;
    color: #000000;
    border: none;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    transition: transform 0.2s cubic-bezier(0.25, 1, 0.5, 1);
    position: relative;
  }}
  .play-morph-btn:hover {{
    transform: scale(1.08);
  }}
  .morph-icon {{
    position: absolute;
    width: 18px;
    height: 18px;
    fill: #000000;
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s ease;
  }}
  .morph-play-icon {{
    transform: scale(1) rotate(0deg);
    opacity: 1;
    margin-left: 2px;
  }}
  .morph-pause-icon {{
    transform: scale(0.4) rotate(-90deg);
    opacity: 0;
  }}
  .is-playing .morph-play-icon {{
    transform: scale(0.4) rotate(90deg);
    opacity: 0;
  }}
  .is-playing .morph-pause-icon {{
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }}

  /* Right Panel: Time-Synced Apple Music Karaoke Lyrics */
  .right-panel {{
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    mask-image: linear-gradient(to bottom, transparent 0%, black 15%, black 85%, transparent 100%);
    -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 15%, black 85%, transparent 100%);
    transition: all 0.28s cubic-bezier(0.25, 1, 0.5, 1);
  }}

  .lyrics-scroller {{
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 160px 20px 200px 20px;
    display: flex;
    flex-direction: column;
    gap: 32px;
    scroll-behavior: smooth;
  }}
  .lyrics-scroller::-webkit-scrollbar {{
    display: none;
  }}

  .lyric-line {{
    font-size: 26px;
    font-weight: 700;
    line-height: 1.35;
    color: rgba(255, 255, 255, 0.32);
    cursor: pointer;
    transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1), color 0.4s ease, filter 0.4s ease;
    filter: blur(0.4px);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
  }}
  .lyric-line:hover {{
    color: rgba(255, 255, 255, 0.6);
  }}

  .lyric-line.active {{
    color: #ffffff;
    filter: blur(0px);
    transform: scale(1.04) translateX(4px);
  }}

  .lyric-line.sung {{
    color: rgba(255, 255, 255, 0.95);
    filter: blur(0px);
  }}

  /* Letter-by-Letter Floating Karaoke Characters */
  .karaoke-char {{
    display: inline-block;
    transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.2s ease, text-shadow 0.2s ease;
    will-change: transform;
    white-space: pre;
  }}
  .karaoke-char.lit {{
    color: #ffffff;
    text-shadow: 0 0 14px rgba(255, 255, 255, 0.85);
  }}
  .karaoke-char.singing {{
    transform: translateY(-4px) scale(1.14);
    color: #ffffff;
    text-shadow: 0 0 20px rgba(255, 255, 255, 1);
  }}

  /* Compact Mode (No Lyrics Found) */
  body.no-lyrics-mode .titlebar-center {{
    display: block !important;
  }}
  body.no-lyrics-mode .right-panel {{
    display: none !important;
  }}
  body.no-lyrics-mode .main-container {{
    flex-direction: column;
    padding: 18px 24px 28px 24px;
    gap: 16px;
  }}
  body.no-lyrics-mode .left-panel {{
    width: 290px;
    min-width: 290px;
    align-items: center;
    text-align: center;
  }}
  body.no-lyrics-mode .cover-container {{
    width: 250px;
    height: 250px;
    margin: 0 auto;
  }}
  body.no-lyrics-mode .liquidgl-card {{
    width: 100%;
  }}

  /* Corner Resize Grip */
  .resize-grip {{
    position: fixed;
    bottom: 0;
    right: 0;
    width: 18px;
    height: 18px;
    cursor: nwse-resize !important;
    z-index: 100;
    -webkit-app-region: no-drag !important;
    background: linear-gradient(135deg, transparent 50%, rgba(255, 255, 255, 0.3) 50%, rgba(255, 255, 255, 0.3) 65%, transparent 65%, transparent 75%, rgba(255, 255, 255, 0.3) 75%);
    border-bottom-right-radius: 4px;
  }}

  /* MINI PLAYER CARD MODE (Slid to Bottom-Left) */
  body.mode-mini .app-container {{
    display: none !important;
  }}
  body.mode-mini .resize-grip {{
    display: none !important;
  }}

  .mini-player-card {{
    display: none;
  }}

  body.mode-mini .mini-player-card {{
    display: flex !important;
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    flex-direction: column;
    background: rgba(18, 18, 22, 0.78);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7), inset 0 1px 1px rgba(255, 255, 255, 0.3);
    border-radius: 18px;
    overflow: hidden;
    -webkit-app-region: drag !important;
    z-index: 100;
  }}

  /* Mini Header */
  .mini-header {{
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 10px 0 10px;
    -webkit-app-region: drag !important;
  }}

  .mini-logo {{
    height: 16px;
    width: auto;
    object-fit: contain;
    -webkit-app-region: no-drag !important;
    pointer-events: none;
  }}

  .mini-header-btns {{
    display: flex;
    align-items: center;
    gap: 4px;
    -webkit-app-region: no-drag !important;
  }}

  .mini-btn {{
    width: 22px;
    height: 20px;
    border: none;
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.85);
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s ease;
    -webkit-app-region: no-drag !important;
  }}
  .mini-btn:hover {{
    background: rgba(255, 255, 255, 0.25);
    color: #ffffff;
  }}
  .mini-close:hover {{
    background: #e81123 !important;
    color: #ffffff !important;
  }}

  /* Mini Content Body */
  .mini-body {{
    flex: 1;
    display: flex;
    align-items: center;
    padding: 4px 14px 10px 14px;
    gap: 14px;
    -webkit-app-region: drag !important;
  }}

  .mini-cover-box {{
    width: 72px;
    height: 72px;
    min-width: 72px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.15);
    -webkit-app-region: no-drag !important;
  }}
  .mini-cover-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}

  .mini-info-col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
    gap: 6px;
    -webkit-app-region: drag !important;
  }}

  .mini-title {{
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
  }}

  .mini-artist {{
    font-size: 12px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.72);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: -3px;
  }}

  .mini-controls-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 2px;
    -webkit-app-region: no-drag !important;
  }}

  .mini-ctrl-btn {{
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.85);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);
    -webkit-app-region: no-drag !important;
  }}
  .mini-ctrl-btn:hover {{
    color: #ffffff;
    background: rgba(255, 255, 255, 0.15);
    transform: scale(1.1);
  }}

  .mini-play-btn {{
    width: 32px;
    height: 32px;
    background: #ffffff;
    color: #000000;
    border: none;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s cubic-bezier(0.25, 1, 0.5, 1);
    position: relative;
    -webkit-app-region: no-drag !important;
  }}
  .mini-play-btn:hover {{
    transform: scale(1.1);
  }}
  .mini-play-btn .morph-icon {{
    width: 14px;
    height: 14px;
  }}

  /* Mini Audio Visualizer Popping Up From Bottom */
  #miniWaveCanvas {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 26px;
    pointer-events: none;
    z-index: 10;
  }}
</style>
</head>
<body>

  <!-- Full Window Crossfading Backgrounds -->
  <div class="bg-layer" id="bgLayerA"></div>
  <div class="bg-layer" id="bgLayerB"></div>

  <!-- MAIN FULL-SIZED / COMPACT PLAYER -->
  <div class="app-container">
    <!-- Custom Rounded Frameless Titlebar -->
    <div class="custom-titlebar">
      <div class="titlebar-left">
        <img class="app-logo-img" src="data:image/png;base64,{logo_base64}" alt="EZ Lyrics" />
      </div>
      <div class="titlebar-center" id="titleCenter">No lyrics found</div>
      <div class="window-controls">
        <button class="win-btn" onclick="toggleMiniMode()" title="Mini Player">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="3" ry="3"/>
            <rect x="11" y="13" width="8" height="6" rx="1.5" fill="currentColor" opacity="0.8"/>
          </svg>
        </button>
        <button class="win-btn win-min" onclick="window.pywebview.api.minimize_window()" title="Minimize to Taskbar">&#x2500;</button>
        <button class="win-btn win-close" onclick="window.pywebview.api.close_window()" title="Close">&#x2715;</button>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="main-container">
      <!-- Left Panel: Album Art & LiquidGL Glass Card -->
      <div class="left-panel">
        <div class="cover-container">
          <img class="cover-img" id="albumCoverImg" src="" alt="Album Artwork" />
        </div>
        <div class="track-meta">
          <div class="track-title" id="trackTitle">Connecting to Spotify...</div>
          <div class="track-artist" id="trackArtist">Waiting for audio playback</div>
        </div>

        <!-- LiquidGL Refractive Glass Player Card -->
        <div class="liquidgl-card">
          <!-- Hardware Audio Visualizer Bar -->
          <div class="vocalizer-container">
            <div class="vocalizer-box" id="vocalizerBox" title="Click to seek">
              <canvas id="waveCanvas"></canvas>
            </div>
            <div class="time-row">
              <span id="timeCurrent">0:00</span>
              <span id="timeDuration">0:00</span>
            </div>
          </div>

          <!-- 5-Button Transport Controls -->
          <div class="controls-row">
            <button class="ctrl-btn" id="loopBtn" onclick="toggleLoop()" title="Loop">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="17 1 21 5 17 9"/>
                <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
                <polyline points="7 23 3 19 7 15"/>
                <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
              </svg>
            </button>

            <button class="ctrl-btn" onclick="prevTrack()" title="Previous Track">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="19 20 9 12 19 4 19 20"/>
                <line x1="5" y1="4" x2="5" y2="20" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
              </svg>
            </button>

            <button class="play-morph-btn" id="playBtn" onclick="togglePlay()" title="Play / Pause">
              <svg class="morph-icon morph-play-icon" viewBox="0 0 24 24">
                <polygon points="6 4 20 12 6 20 6 4"/>
              </svg>
              <svg class="morph-icon morph-pause-icon" viewBox="0 0 24 24">
                <rect x="5" y="4" width="4.5" height="16" rx="2"/>
                <rect x="14.5" y="4" width="4.5" height="16" rx="2"/>
              </svg>
            </button>

            <button class="ctrl-btn" onclick="nextTrack()" title="Next Track">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 4 15 12 5 20 5 4"/>
                <line x1="19" y1="4" x2="19" y2="20" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
              </svg>
            </button>

            <button class="ctrl-btn" id="shuffleBtn" onclick="toggleShuffle()" title="Shuffle">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="16 3 21 3 21 8"/>
                <line x1="4" y1="20" x2="21" y2="3"/>
                <polyline points="21 16 21 21 16 21"/>
                <line x1="15" y1="15" x2="21" y2="21"/>
                <line x1="4" y1="4" x2="9" y2="9"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Right Panel: Apple Music Karaoke Lyrics -->
      <div class="right-panel">
        <div class="lyrics-scroller" id="lyricsScroller"></div>
      </div>
    </div>
  </div>

  <!-- MINI PLAYER CARD MODE (Slid to Bottom-Left) -->
  <div class="mini-player-card" id="miniPlayerCard">
    <div class="mini-header">
      <img class="mini-logo" src="data:image/png;base64,{logo_base64}" alt="EZ" />
      <div class="mini-header-btns">
        <button class="mini-btn" onclick="toggleMiniMode()" title="Restore Full Player">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 3 21 3 21 9"/>
            <polyline points="9 21 3 21 3 15"/>
            <line x1="21" y1="3" x2="14" y2="10"/>
            <line x1="3" y1="21" x2="10" y2="14"/>
          </svg>
        </button>
        <button class="mini-btn mini-close" onclick="window.pywebview.api.close_window()" title="Close">&#x2715;</button>
      </div>
    </div>

    <div class="mini-body">
      <div class="mini-cover-box">
        <img class="mini-cover-img" id="miniCoverImg" src="" alt="Cover" />
      </div>
      <div class="mini-info-col">
        <div class="mini-title" id="miniTrackTitle">Track Title</div>
        <div class="mini-artist" id="miniTrackArtist">Artist</div>
        <div class="mini-controls-row">
          <button class="mini-ctrl-btn" onclick="prevTrack()" title="Previous">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="19 20 9 12 19 4 19 20"/>
              <line x1="5" y1="4" x2="5" y2="20" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            </svg>
          </button>
          <button class="mini-play-btn" id="miniPlayBtn" onclick="togglePlay()" title="Play / Pause">
            <svg class="morph-icon morph-play-icon" viewBox="0 0 24 24">
              <polygon points="6 4 20 12 6 20 6 4"/>
            </svg>
            <svg class="morph-icon morph-pause-icon" viewBox="0 0 24 24">
              <rect x="5" y="4" width="4.5" height="16" rx="2"/>
              <rect x="14.5" y="4" width="4.5" height="16" rx="2"/>
            </svg>
          </button>
          <button class="mini-ctrl-btn" onclick="nextTrack()" title="Next">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 4 15 12 5 20 5 4"/>
              <line x1="19" y1="4" x2="19" y2="20" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mini Visualizer Canvas (Pops Up From Bottom) -->
    <canvas id="miniWaveCanvas"></canvas>
  </div>

  <!-- Interactive Drag-to-Resize Corner Grip -->
  <div class="resize-grip" id="resizeGrip" title="Drag corner to resize"></div>

<script>
  let state = {{
    version: 0,
    current_track: "",
    current_artist: "",
    album_cover: "",
    lyrics: [],
    duration: 180.0,
    base_pos: 0.0,
    base_time: performance.now() / 1000,
    is_playing: false,
    is_loop: false,
    is_shuffle: false,
    audio_peak: 0.0
  }};

  let activeIndex = -1;
  let userScrolling = false;
  let scrollTimer = null;
  let currentCoverUrl = "";
  let activeLayer = 'A';
  let isCompactMode = false;
  let isMiniMode = false;

  const bgLayerA = document.getElementById('bgLayerA');
  const bgLayerB = document.getElementById('bgLayerB');
  const albumCoverImg = document.getElementById('albumCoverImg');
  const miniCoverImg = document.getElementById('miniCoverImg');
  const trackTitle = document.getElementById('trackTitle');
  const trackArtist = document.getElementById('trackArtist');
  const miniTrackTitle = document.getElementById('miniTrackTitle');
  const miniTrackArtist = document.getElementById('miniTrackArtist');
  const playBtn = document.getElementById('playBtn');
  const miniPlayBtn = document.getElementById('miniPlayBtn');
  const loopBtn = document.getElementById('loopBtn');
  const shuffleBtn = document.getElementById('shuffleBtn');
  const timeCurrent = document.getElementById('timeCurrent');
  const timeDuration = document.getElementById('timeDuration');
  const lyricsScroller = document.getElementById('lyricsScroller');
  const canvas = document.getElementById('waveCanvas');
  const ctx = canvas.getContext('2d');
  const miniCanvas = document.getElementById('miniWaveCanvas');
  const miniCtx = miniCanvas.getContext('2d');
  let waveTick = 0;

  function resizeCanvas() {{
    const rect = canvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {{
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
    }}
    const mRect = miniCanvas.getBoundingClientRect();
    if (mRect.width > 0 && mRect.height > 0) {{
      miniCanvas.width = mRect.width * window.devicePixelRatio;
      miniCanvas.height = mRect.height * window.devicePixelRatio;
    }}
  }}
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  // Draw Main Visualizer Wave Bar
  function drawWave() {{
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    if (w <= 0 || h <= 0) return;

    const midY = h / 2;
    const numBars = 36;
    const barWidth = 3.6 * window.devicePixelRatio;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const progressRatio = state.duration > 0 ? (localPos / state.duration) : 0;

    waveTick += state.is_playing ? 0.09 : 0.01;

    // Direct, ultra-responsive audio peak modulation
    const peak = Math.max(0.12, (state.audio_peak || 0.0) * 1.15);

    for (let i = 0; i < numBars; i++) {{
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const waveEnvelope = 1.0 - (centerDist * 0.35);

      const freq1 = Math.sin(waveTick * 3.2 + i * 0.45);
      const freq2 = Math.cos(waveTick * 2.2 - i * 0.55);
      const osc = (freq1 * 0.5 + 0.5) * 0.45 + (freq2 * 0.5 + 0.5) * 0.55;

      let amp = 0.08;
      if (state.is_playing) {{
        amp = (0.15 + osc * 0.85) * waveEnvelope * peak;
      }}
      const barHeight = Math.max(4 * window.devicePixelRatio, Math.min(h - 2, amp * (h - 2)));

      const barProgress = (x + barWidth / 2) / w;
      if (barProgress <= progressRatio) {{
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = 'rgba(255, 255, 255, 0.9)';
        ctx.shadowBlur = 8;
      }} else {{
        ctx.fillStyle = 'rgba(255, 255, 255, 0.28)';
        ctx.shadowBlur = 0;
      }}

      ctx.beginPath();
      ctx.roundRect(x, midY - barHeight / 2, barWidth, barHeight, 2);
      ctx.fill();
    }}
  }}

  // Draw Mini Mode Visualizer Popping Up From Bottom Border
  function drawMiniWave() {{
    const w = miniCanvas.width;
    const h = miniCanvas.height;
    miniCtx.clearRect(0, 0, w, h);
    if (w <= 0 || h <= 0) return;

    const numBars = 32;
    const barWidth = 4.2 * window.devicePixelRatio;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const peak = Math.max(0.1, (state.audio_peak || 0.0) * 1.25);

    for (let i = 0; i < numBars; i++) {{
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const env = 1.0 - (centerDist * 0.25);

      const freq1 = Math.sin(waveTick * 3.4 + i * 0.5);
      const freq2 = Math.cos(waveTick * 2.0 - i * 0.65);
      const osc = (freq1 * 0.5 + 0.5) * 0.5 + (freq2 * 0.5 + 0.5) * 0.5;

      let amp = 0.08;
      if (state.is_playing) {{
        amp = (0.18 + osc * 0.82) * env * peak;
      }}
      const barHeight = Math.max(3 * window.devicePixelRatio, Math.min(h, amp * h));

      const grad = miniCtx.createLinearGradient(0, h, 0, h - barHeight);
      grad.addColorStop(0, 'rgba(255, 255, 255, 0.15)');
      grad.addColorStop(0.5, 'rgba(255, 255, 255, 0.65)');
      grad.addColorStop(1, 'rgba(255, 255, 255, 0.95)');

      miniCtx.fillStyle = grad;
      miniCtx.shadowColor = 'rgba(255, 255, 255, 0.75)';
      miniCtx.shadowBlur = 6;

      miniCtx.beginPath();
      miniCtx.roundRect(x, h - barHeight, barWidth, barHeight, [2.5, 2.5, 0, 0]);
      miniCtx.fill();
    }}
  }}

  // Seeking on Vocalizer Bar
  document.getElementById('vocalizerBox').addEventListener('click', (e) => {{
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const targetSec = ratio * state.duration;
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api.seek(targetSec);
    }}
  }});

  // Toggle Mini Mode / PiP
  function toggleMiniMode() {{
    isMiniMode = !isMiniMode;
    document.body.classList.toggle('mode-mini', isMiniMode);
    resizeCanvas();
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api.set_mode(isMiniMode ? 'mini' : 'restore');
    }}
  }}

  function togglePlay() {{
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api.toggle_play();
    }}
  }}
  function prevTrack() {{
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api.prev_track();
    }}
  }}
  function nextTrack() {{
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api.next_track();
    }}
  }}
  function toggleLoop() {{
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api.toggle_loop().then(val => {{
        loopBtn.classList.toggle('active', !!val);
      }});
    }}
  }}
  function toggleShuffle() {{
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api.toggle_shuffle().then(val => {{
        shuffleBtn.classList.toggle('active', !!val);
      }});
    }}
  }}

  function formatTime(s) {{
    const sec = Math.max(0, Math.floor(s || 0));
    const m = Math.floor(sec / 60);
    const rem = sec % 60;
    return `${{m}}:${{rem < 10 ? '0' : ''}}${{rem}}`;
  }}

  lyricsScroller.addEventListener('scroll', () => {{
    userScrolling = true;
    if (scrollTimer) clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => {{ userScrolling = false; }}, 2200);
  }});

  // Drag-to-Resize Corner Grip
  let isResizing = false;
  let startX = 0, startY = 0, startW = 0, startH = 0;
  const grip = document.getElementById('resizeGrip');

  grip.addEventListener('mousedown', (e) => {{
    e.preventDefault();
    isResizing = true;
    startX = e.screenX;
    startY = e.screenY;
    startW = window.innerWidth;
    startH = window.innerHeight;
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }});

  function onMouseMove(e) {{
    if (!isResizing) return;
    const nw = Math.max(340, startW + (e.screenX - startX));
    const nh = Math.max(420, startH + (e.screenY - startY));
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api._run_animation(nw, nh, null, null, 0.0);
    }}
  }}

  function onMouseUp() {{
    isResizing = false;
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  }}

  // High-Performance Animation Loop
  let localPos = 0;
  function animFrame() {{
    const now = performance.now() / 1000;
    if (state.is_playing) {{
      localPos = Math.max(0, Math.min(state.duration, state.base_pos + (now - state.base_time)));
    }} else {{
      localPos = Math.max(0, Math.min(state.duration, state.base_pos));
    }}

    timeCurrent.textContent = formatTime(localPos);
    timeDuration.textContent = formatTime(state.duration);

    if (isMiniMode) {{
      drawMiniWave();
    }} else {{
      drawWave();
    }}

    // Letter-by-Letter Floating Karaoke Engine
    if (!isMiniMode && state.lyrics && state.lyrics.length > 0) {{
      let activeIdx = -1;
      for (let i = 0; i < state.lyrics.length; i++) {{
        const item = state.lyrics[i];
        if (localPos >= item.time && localPos <= item.endTime) {{
          activeIdx = i;
          break;
        }} else if (localPos > item.endTime && (i === state.lyrics.length - 1 || localPos < state.lyrics[i+1].time)) {{
          activeIdx = i;
          break;
        }}
      }}

      if (activeIdx !== activeIndex) {{
        activeIndex = activeIdx;
        const allLines = lyricsScroller.querySelectorAll('.lyric-line');
        allLines.forEach((el, idx) => {{
          if (idx < activeIdx) {{
            el.className = 'lyric-line sung';
            el.querySelectorAll('.karaoke-char').forEach(c => c.className = 'karaoke-char lit');
          }} else if (idx === activeIdx) {{
            el.className = 'lyric-line active';
          }} else {{
            el.className = 'lyric-line';
            el.querySelectorAll('.karaoke-char').forEach(c => c.className = 'karaoke-char');
          }}
        }});

        if (activeIdx >= 0 && !userScrolling) {{
          const targetEl = allLines[activeIdx];
          if (targetEl) {{
            const scrollerH = lyricsScroller.clientHeight;
            const targetTop = targetEl.offsetTop;
            const targetH = targetEl.clientHeight;
            lyricsScroller.scrollTo({{
              top: targetTop - (scrollerH / 2) + (targetH / 2),
              behavior: 'smooth'
            }});
          }}
        }}
      }}

      // Animate Individual Characters on Active Line
      if (activeIdx >= 0) {{
        const activeLineEl = lyricsScroller.querySelector(`.lyric-line[data-index="${{activeIdx}}"]`);
        if (activeLineEl) {{
          const lineItem = state.lyrics[activeIdx];
          const lineDur = Math.max(0.5, lineItem.endTime - lineItem.time);
          const lineElapsed = Math.max(0, localPos - lineItem.time);
          const ratio = Math.min(1.0, lineElapsed / lineDur);

          const chars = activeLineEl.querySelectorAll('.karaoke-char');
          const totalChars = chars.length;
          const currentProgressIndex = ratio * totalChars;

          chars.forEach((charEl, cIdx) => {{
            if (cIdx < Math.floor(currentProgressIndex)) {{
              charEl.className = 'karaoke-char lit';
            }} else if (cIdx === Math.floor(currentProgressIndex)) {{
              charEl.className = 'karaoke-char singing';
            }} else {{
              charEl.className = 'karaoke-char';
            }}
          }});
        }}
      }}
    }}

    requestAnimationFrame(animFrame);
  }}
  requestAnimationFrame(animFrame);

  // Poll Backend State
  function pollBridge() {{
    if (window.pywebview && window.pywebview.api) {{
      window.pywebview.api.get_state().then(s => {{
        if (!s) return;

        state.is_playing = s.is_playing;
        state.duration = s.duration || 180;
        state.audio_peak = s.audio_peak || 0.0;

        // Sync Spotify Position if Delta > 0.6s
        const currentCalculated = state.base_pos + (s.is_playing ? (performance.now() / 1000 - state.base_time) : 0);
        if (Math.abs(currentCalculated - s.base_pos) > 0.6) {{
          state.base_pos = s.base_pos;
          state.base_time = performance.now() / 1000;
        }}

        // Morphing Play Button Animation
        if (state.is_playing) {{
          playBtn.classList.add('is-playing');
          miniPlayBtn.classList.add('is-playing');
        }} else {{
          playBtn.classList.remove('is-playing');
          miniPlayBtn.classList.remove('is-playing');
        }}

        if (s.version !== state.version) {{
          state.version = s.version;
          state.current_track = s.current_track;
          state.current_artist = s.current_artist;
          state.album_cover = s.album_cover;
          state.lyrics = s.lyrics || [];

          trackTitle.textContent = state.current_track || "Spotify Ready";
          trackArtist.textContent = state.current_artist || "Play any track";
          miniTrackTitle.textContent = state.current_track || "Spotify Ready";
          miniTrackArtist.textContent = state.current_artist || "Play any track";

          // Crossfading Full Window Background & Cover Artwork
          if (state.album_cover && state.album_cover !== currentCoverUrl) {{
            currentCoverUrl = state.album_cover;
            albumCoverImg.src = state.album_cover;
            miniCoverImg.src = state.album_cover;
            if (activeLayer === 'A') {{
              bgLayerB.style.backgroundImage = `url("${{state.album_cover}}")`;
              bgLayerB.style.opacity = '1';
              bgLayerA.style.opacity = '0';
              activeLayer = 'B';
            }} else {{
              bgLayerA.style.backgroundImage = `url("${{state.album_cover}}")`;
              bgLayerA.style.opacity = '1';
              bgLayerB.style.opacity = '0';
              activeLayer = 'A';
            }}
          }}

          // Build Lyrics DOM with Individual Character Nodes
          lyricsScroller.innerHTML = "";
          activeIndex = -1;
          if (state.lyrics && state.lyrics.length > 0) {{
            state.lyrics.forEach((item, idx) => {{
              const lineDiv = document.createElement('div');
              lineDiv.className = 'lyric-line';
              lineDiv.dataset.index = idx;
              for (const ch of item.text) {{
                const sp = document.createElement('span');
                sp.className = 'karaoke-char';
                sp.textContent = ch;
                lineDiv.appendChild(sp);
              }}
              lineDiv.addEventListener('click', () => {{
                if (window.pywebview && window.pywebview.api) {{
                  window.pywebview.api.seek(item.time);
                }}
              }});
              lyricsScroller.appendChild(lineDiv);
            }});
          }}

          // Smooth Automatic Mode Switching:
          // Centered compact mode (380x620) if no lyrics, expanded wide mode (960x580) if lyrics
          const hasLyrics = state.lyrics && state.lyrics.length > 0;
          if (!hasLyrics && !isCompactMode) {{
            isCompactMode = true;
            document.body.classList.add('no-lyrics-mode');
            if (!isMiniMode && window.pywebview && window.pywebview.api) {{
              window.pywebview.api.set_mode('compact');
            }}
          }} else if (hasLyrics && isCompactMode) {{
            isCompactMode = false;
            document.body.classList.remove('no-lyrics-mode');
            if (!isMiniMode && window.pywebview && window.pywebview.api) {{
              window.pywebview.api.set_mode('expanded');
            }}
          }}
        }}
      }}).catch(err => {{}});
    }}
  }}

  setInterval(pollBridge, 80);
</script>
</body>
</html>
"""

# Keep-Topmost Worker Thread (Keeps Window in Front of Fullscreen Apps)
def keep_topmost_worker(bridge):
    time.sleep(1.0)
    while True:
        try:
            hwnd = bridge.get_hwnd()
            if hwnd:
                ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x0040)
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
            args=(info.get("artist", ""), info.get("title", ""), float(info.get("dur", 0.0))),
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
    threading.Thread(target=keep_topmost_worker, args=(bridge,), daemon=True).start()
    webview.start(debug=False)

if __name__ == "__main__":
    main()
''')

with open(r"C:\Users\dryde\spicy_spotify_lyrics\app.py", "w", encoding="utf-8") as f:
    f.write("".join(parts))

print("Successfully written updated app.py with smooth transitions and mini mode.")
