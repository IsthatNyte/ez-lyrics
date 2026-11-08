"""
EZ Lyrics LiquidGL Player - Full Custom Studio Edition
Features:
- Pure white transparent EZ logo with dynamic album dominant-color tinting
- Standalone index.html with 100% persistent UI customization & layout state (~/.ez_lyrics_config.json)
- Native spotify_cli.exe & Spotify Web API integration for real personal playlists, instant Add/Remove, & 1-click playback
- Real-Time Lyric Translation & Phonetic Romanization Sub-Lines (Google GTX dict-chrome-ex)
- True 8-Band Multi-Band FFT Audio Spectrum Visualizer + Audio Normalization + Layout Mode Color Picker
- Custom Theme & Font Studio + Shareable Base64 Layout Presets
- AI DJ Engine with Invisible Extra Command Terminal (fetches 50 random playlist songs & plays by style/vibe)
- Secret Menu 4th Button: Bouncy Recent Songs Popup Over Lyrics (click to play again or add to playlist)
- 4 Extra Hidden-by-Default UI Parts in Add UI Part (+ Menu): BPM/Key Badge, AI DJ Deck, Vinyl Clock, Discord RPC Pill
- Hover Carousel with Rounded Side Arrows on Player Controls (slides/blurs/fades in extra control buttons)
- Native Win32 Click-Through Ghost Mode (Ctrl+Shift+L global restore hotkey) & Native Discord Rich Presence IPC
"""

import sys
import os
import re
import time
import math
import json
import io
import base64
import zlib
import struct
import random
import threading
import subprocess
import urllib.parse
import hashlib
import secrets
import colorsys
import webbrowser
import http.server
import concurrent.futures
import xml.etree.ElementTree as ET
import ctypes
from ctypes import cast, POINTER, wintypes
import requests
http_session = requests.Session()
_http_adapter = requests.adapters.HTTPAdapter(pool_connections=16, pool_maxsize=32, max_retries=1)
http_session.mount("https://", _http_adapter)
http_session.mount("http://", _http_adapter)
from PIL import Image
import webview

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
)

try:
    from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
    HAS_PYCAW = True
except Exception:
    HAS_PYCAW = False

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

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
user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.LoadImageW.restype = wintypes.HANDLE
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long
user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
user32.SetWindowLongW.restype = ctypes.c_long
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short

HWND_TOPMOST = wintypes.HWND(-1)
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020

_icon_applied = False
_click_through_active = False

def apply_window_icon(hwnd):
    global _icon_applied
    if _icon_applied or not hwnd:
        return
    try:
        ico_path = resource_path('icon.ico')
        if os.path.exists(ico_path):
            hicon_big = user32.LoadImageW(None, ico_path, 1, 256, 256, 0x00000010)
            hicon_small = user32.LoadImageW(None, ico_path, 1, 32, 32, 0x00000010)
            if hicon_big:
                user32.SendMessageW(wintypes.HWND(hwnd), 0x0080, 1, hicon_big)
            if hicon_small:
                user32.SendMessageW(wintypes.HWND(hwnd), 0x0080, 0, hicon_small)
            _icon_applied = True
    except Exception:
        pass

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

def set_window_click_through(enable):
    global _click_through_active
    _click_through_active = bool(enable)
    hwnd = find_our_hwnd()
    if not hwnd:
        return _click_through_active
    try:
        h = wintypes.HWND(hwnd)
        ex_style = user32.GetWindowLongW(h, GWL_EXSTYLE)
        if _click_through_active:
            user32.SetWindowLongW(h, GWL_EXSTYLE, ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        else:
            user32.SetWindowLongW(h, GWL_EXSTYLE, ex_style & ~WS_EX_TRANSPARENT)
    except Exception:
        pass
    with state_lock:
        app_state["click_through"] = _click_through_active
    return _click_through_active

def read_file_shared(filepath, max_bytes=16000000):
    """Read a file on Windows using FILE_SHARE_READ | FILE_SHARE_WRITE so locked Spotify .log/.ldb files never throw PermissionError."""
    GENERIC_READ = 0x80000000
    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002
    FILE_SHARE_DELETE = 0x00000004
    OPEN_EXISTING = 3
    FILE_ATTRIBUTE_NORMAL = 0x80
    try:
        handle = ctypes.windll.kernel32.CreateFileW(
            str(filepath),
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
            None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            None
        )
        if handle == -1 or handle == 0xFFFFFFFFFFFFFFFF:
            return b""
        try:
            size = ctypes.windll.kernel32.GetFileSize(handle, None)
            if size <= 0 or size > max_bytes:
                return b""
            buf = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_ulong(0)
            ctypes.windll.kernel32.ReadFile(handle, buf, size, ctypes.byref(bytes_read), None)
            return buf.raw[:bytes_read.value]
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        return b""

# Global shared state
state_lock = threading.Lock()
app_state = {
    "version": 0,
    "current_track": "",
    "current_artist": "",
    "current_track_id": "",
    "album_cover": "",
    "dominant_color": "#ffffff",
    "lyrics": [],
    "duration": 180.0,
    "base_pos": 0.0,
    "base_time": time.time(),
    "is_playing": False,
    "is_loop": False,
    "is_shuffle": False,
    "audio_peak": 0.0,
    "fft_bands": [0.06] * 8,
    "audio_norm": True,
    "click_through": False,
    "discord_rpc": True,
    "discord_connected": False,
    "bpm": 124,
    "musical_key": "C Maj",
    "playlists": []
}

# Persistent User Configuration & UI Layout State (~/.ez_lyrics_config.json)
SPICY_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".ez_lyrics_config.json")
_config_lock = threading.Lock()

def load_user_config():
    with _config_lock:
        try:
            if os.path.exists(SPICY_CONFIG_PATH):
                with open(SPICY_CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        return {"spicy_api_key": "", "saved_playlist_tracks": {}, "ui_state": {}}

def save_user_config(cfg):
    with _config_lock:
        try:
            with open(SPICY_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

# Native Spotify CLI Helper (C:\Users\dryde\AppData\Roaming\Spotify\spotify_cli.exe)
def get_spotify_cli_path():
    candidates = [
        os.path.join(os.environ.get("APPDATA", ""), "Spotify", "spotify_cli.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "spotify_cli.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return ""

def run_spotify_cli(args_list, timeout=4.5):
    cli = get_spotify_cli_path()
    if not cli:
        return None
    try:
        creation_flags = 0x08000000 if os.name == "nt" else 0
        proc = subprocess.run(
            [cli] + list(args_list),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout,
            creationflags=creation_flags
        )
        out = (proc.stdout or "").strip()
        if out.startswith("{") or out.startswith("["):
            try:
                return json.loads(out)
            except Exception:
                pass
        return {"raw": out, "returncode": proc.returncode}
    except Exception:
        return None

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

# Strict Creator & Title Matching Helpers
def _norm_str(s):
    if not s:
        return ""
    s = str(s).lower()
    s = re.sub(r'[\(\[\{].*?[\)\]\}]', ' ', s)
    s = re.sub(r'[^a-z0-9\u00c0-\uffff]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def titles_line_up(spotify_title, candidate_title):
    t1 = _norm_str(spotify_title)
    t2 = _norm_str(candidate_title)
    if not t1 or not t2:
        return False
    if t1 == t2 or t1 in t2 or t2 in t1:
        return True
    b1 = _norm_str(spotify_title.split(" - ")[0])
    b2 = _norm_str(candidate_title.split(" - ")[0])
    return bool(b1 and b2 and (b1 == b2))

def creator_lines_up(spotify_artist, candidate_artists):
    if not spotify_artist:
        return True
    if isinstance(candidate_artists, str):
        cand_list = [candidate_artists]
    else:
        cand_list = list(candidate_artists or [])
    sp_parts = [p.strip() for p in re.split(r'[,&/;]|\bfeat\.?\b|\bft\.?\b|\bwith\b', str(spotify_artist), flags=re.I) if p.strip()]
    if not sp_parts:
        sp_parts = [str(spotify_artist).strip()]
    sp_norms = [_norm_str(p) for p in sp_parts if _norm_str(p)]
    cand_norms = [_norm_str(c) for c in cand_list if _norm_str(c)]
    cand_joined = " ".join(cand_norms)
    if not sp_norms or not cand_norms:
        return False
    primary = sp_norms[0]
    for cn in cand_norms:
        if primary == cn or primary in cn or cn in primary:
            return True
    return primary in cand_joined

def extract_dominant_color(img_bytes):
    try:
        im = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((48, 48))
        pixels = list(im.getdata())
        buckets = {}
        fallback_r, fallback_g, fallback_b, fb_count = 0, 0, 0, 0
        for r, g, b in pixels:
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if 25 < lum < 240:
                fallback_r += r
                fallback_g += g
                fallback_b += b
                fb_count += 1
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            if v < 0.18 or (v > 0.94 and s < 0.12):
                continue
            if s < 0.15:
                continue
            hb = int(h * 24) % 24
            weight = (s ** 1.4) * (v ** 0.8) * 2.5
            if hb not in buckets:
                buckets[hb] = [0.0, 0.0, 0.0, 0.0]
            buckets[hb][0] += weight
            buckets[hb][1] += r * weight
            buckets[hb][2] += g * weight
            buckets[hb][3] += b * weight

        if buckets:
            best = max(buckets.values(), key=lambda x: x[0])
            r = int(best[1] / best[0])
            g = int(best[2] / best[0])
            b = int(best[3] / best[0])
        elif fb_count > 0:
            r = int(fallback_r / fb_count)
            g = int(fallback_g / fb_count)
            b = int(fallback_b / fb_count)
        else:
            return "#ffffff"

        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if s > 0.12:
            s = max(0.55, min(1.0, s * 1.2))
        v = max(0.82, min(1.0, v * 1.15))
        rr, gg, bb = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(rr*255):02x}{int(gg*255):02x}{int(bb*255):02x}"
    except Exception:
        return "#ffffff"

def estimate_bpm_and_key(artist, title, duration):
    """Deterministic musical signature & tempo estimator seeded by track metadata."""
    keys = ["C Maj", "C# Min", "D Maj", "D# Min", "E Maj", "F Min", "F# Maj", "G Maj", "G# Min", "A Min", "A# Maj", "B Min"]
    seed_str = f"{_norm_str(artist)}:{_norm_str(title)}"
    h_val = int(hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:8], 16)
    bpm = 86 + (h_val % 78)
    m_key = keys[h_val % len(keys)]
    return bpm, m_key

def resolve_exact_spotify_track(artist, title):
    """Resolve exact spotify:track:<id>, high-res cover, full artist list, and album name via spotify_cli.exe or local playback state."""
    # 1. Try native spotify_cli.exe now-playing + lookup first (<120ms, 100% accurate)
    try:
        np_data = run_spotify_cli(["now-playing", "--format", "json"], timeout=2.2)
        if isinstance(np_data, dict):
            cp = np_data.get("currently_playing") or {}
            uri = cp.get("uri", "")
            if uri.startswith("spotify:track:"):
                tid = uri.split(":")[-1]
                lk = run_spotify_cli(["lookup", uri, "--format", "json"], timeout=2.5)
                if isinstance(lk, dict) and lk.get("entities"):
                    ent = lk["entities"][0]
                    e_name = ent.get("name", "")
                    e_artists = [c.get("name", "").strip() for c in ent.get("contributors", []) if c.get("name")]
                    e_album = ent.get("parent", {}).get("name", "")
                    if not title or titles_line_up(title, e_name):
                        img_url = ent.get("image_url", "")
                        if img_url:
                            img_url = img_url.replace("ab67616d00004851", "ab67616d0000b273")
                        full_art = ", ".join(e_artists) if e_artists else artist
                        return tid, img_url, full_art, e_album
    except Exception:
        pass

    # 2. Fallback: scan local Spotify playback state files using shared Win32 reader
    try:
        local_spotify = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Spotify", "Users")
        raw_blobs = []
        if os.path.exists(local_spotify):
            for udir in os.listdir(local_spotify):
                upath = os.path.join(local_spotify, udir)
                if not os.path.isdir(upath):
                    continue
                for fname in ("list_player_play_request", "list_player_play_history"):
                    fpath = os.path.join(upath, fname)
                    if os.path.exists(fpath):
                        raw = read_file_shared(fpath)
                        if raw:
                            raw_blobs.append(raw.decode("latin-1", errors="ignore"))
        combined = "\n".join(raw_blobs)
        recent_tids = list(dict.fromkeys(re.findall(r'spotify:track:([a-zA-Z0-9]{22})', combined)))[:10]
        headers = {"User-Agent": "Mozilla/5.0"}
        for tid in recent_tids:
            try:
                r = http_session.get(f"https://open.spotify.com/embed/track/{tid}", headers=headers, timeout=3.0)
                if r.status_code == 200:
                    m = re.search(r'__NEXT_DATA__[^>]*>([^<]+)<', r.text)
                    if m:
                        entity = json.loads(m.group(1)).get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity", {})
                        e_title = entity.get("title", "")
                        e_artists = [a.get("name", "").strip() for a in entity.get("artists", []) if a.get("name")]
                        e_album = entity.get("album", {}).get("name", "")
                        if titles_line_up(title, e_title) and creator_lines_up(artist, e_artists):
                            imgs = entity.get("visualIdentity", {}).get("image", [])
                            cover_url = imgs[-1].get("url", "") if imgs else ""
                            full_art = ", ".join(e_artists) if e_artists else artist
                            return tid, cover_url, full_art, e_album
            except Exception:
                pass
    except Exception:
        pass
    return "", "", "", ""

def fetch_cover_and_artist(artist, title, album=""):
    exact_tid, exact_cover_url, exact_full_artist, exact_album = resolve_exact_spotify_track(artist, title)
    full_artist = exact_full_artist if exact_full_artist else artist
    best_cover_url = exact_cover_url
    final_album = exact_album or album

    clean_title = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title).replace('#', '').strip()
    clean_artist = artist.replace('#', '').strip()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    if not best_cover_url or full_artist == artist:
        search_queries = [
            f"{clean_artist} {clean_title}".strip(),
            f"{clean_artist} {final_album}".strip() if final_album else ""
        ]
        for q_text in search_queries:
            if not q_text:
                continue
            try:
                q = urllib.parse.quote(q_text)
                r = http_session.get(f"https://api.deezer.com/search?q={q}", headers=headers, timeout=3.5)
                if r.status_code == 200:
                    items = r.json().get("data", [])
                    for item in items[:8]:
                        item_title = item.get("title", "")
                        item_artist_name = item.get("artist", {}).get("name", "")
                        if not titles_line_up(title, item_title):
                            continue
                        track_id = item.get("id")
                        contribs_names = [item_artist_name] if item_artist_name else []
                        if track_id:
                            try:
                                r2 = http_session.get(f"https://api.deezer.com/track/{track_id}", headers=headers, timeout=2.8)
                                if r2.status_code == 200:
                                    contribs = r2.json().get("contributors", [])
                                    c_names = [c.get("name").strip() for c in contribs if c.get("name")]
                                    if c_names:
                                        contribs_names = c_names
                            except Exception:
                                pass
                        if not creator_lines_up(artist, contribs_names):
                            continue
                        curr_cover = item.get("album", {}).get("cover_xl") or item.get("album", {}).get("cover_big")
                        if not best_cover_url and curr_cover:
                            best_cover_url = curr_cover
                        if not final_album:
                            final_album = item.get("album", {}).get("title", "")
                        if len(contribs_names) > 1 and full_artist == artist:
                            full_artist = ", ".join(contribs_names)
                        break
                    if best_cover_url:
                        break
            except Exception:
                pass

    if not best_cover_url:
        try:
            q = urllib.parse.quote(f"{clean_artist} {clean_title}".strip())
            r = http_session.get(f"https://itunes.apple.com/search?term={q}&entity=song&limit=8", headers=headers, timeout=3.5)
            if r.status_code == 200:
                for item in r.json().get("results", []):
                    it_title = item.get("trackName", "")
                    it_artist = item.get("artistName", "")
                    if titles_line_up(title, it_title) and creator_lines_up(artist, it_artist):
                        raw_art = item.get("artworkUrl100", "")
                        if raw_art:
                            best_cover_url = raw_art.replace("100x100bb", "1000x1000bb")
                            if not final_album:
                                final_album = item.get("collectionName", "")
                            break
        except Exception:
            pass

    cover_b64 = ""
    dominant_color = "#ffffff"
    if best_cover_url:
        try:
            img_resp = http_session.get(best_cover_url, headers=headers, timeout=3.5)
            if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                cover_b64 = "data:image/jpeg;base64," + base64.b64encode(img_resp.content).decode("ascii")
                dominant_color = extract_dominant_color(img_resp.content)
        except Exception:
            pass

    try:
        full_artist = re.sub(re.escape(artist), artist, full_artist, flags=re.IGNORECASE)
    except Exception:
        pass

    return cover_b64, full_artist, exact_tid, dominant_color, final_album

# ================= SPICY LYRICS & MULTI-SOURCE SYLLABLE/WORD-SYNCED ENGINE =================
def parse_ttml_time(t_str):
    if not t_str:
        return 0.0
    t_str = str(t_str).strip()
    if t_str.endswith("ms"):
        return round(float(t_str[:-2]) / 1000.0, 3)
    if t_str.endswith("s"):
        t_str = t_str[:-1]
    parts = t_str.split(":")
    try:
        if len(parts) == 3:
            return round(int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2]), 3)
        elif len(parts) == 2:
            return round(int(parts[0]) * 60 + float(parts[1]), 3)
        return round(float(t_str), 3)
    except Exception:
        return 0.0

def parse_ttml_to_spicy(ttml_xml):
    lines = []
    timing_mode = ""
    timing_m = re.search(r'itunes:timing="([^"]+)"', ttml_xml)
    if timing_m:
        timing_mode = timing_m.group(1).strip().lower()

    p_blocks = re.findall(r'<p\b([^>]*)>([\s\S]*?)</p>', ttml_xml)
    for attrs, inner in p_blocks:
        p_begin = re.search(r'begin="([^"]+)"', attrs)
        p_end = re.search(r'end="([^"]+)"', attrs)
        agent_m = re.search(r'ttm:agent="([^"]+)"', attrs)
        start_t = parse_ttml_time(p_begin.group(1)) if p_begin else 0.0
        end_t = parse_ttml_time(p_end.group(1)) if p_end else round(start_t + 4.0, 3)
        opposite = bool(agent_m and agent_m.group(1) not in ("v1", "v1000"))

        bg_syllables = []
        lead_html = inner

        # Support both <span ttm:role="x-bg">...</span> and <span role="x-bg">
        bg_match = re.search(r'<span\b[^>]*\b(?:ttm:role|role)="x-bg"[^>]*>([\s\S]*?)</span>(?:\s*</span>)*', inner)
        if bg_match:
            bg_inner = bg_match.group(1)
            lead_html = inner[:bg_match.start()] + inner[bg_match.end():]
            raw_bg_matches = list(re.finditer(r'<span\b([^>]*)>([^<]*)</span>(\s*)', bg_inner))
            for i_bg, s_m in enumerate(raw_bg_matches):
                s_attrs, s_txt, trailing = s_m.group(1), s_m.group(2), s_m.group(3)
                if "role=" in s_attrs:
                    continue
                sb = re.search(r'begin="([^"]+)"', s_attrs)
                se = re.search(r'end="([^"]+)"', s_attrs)
                clean_txt = s_txt.strip()
                if clean_txt:
                    ends_space = s_txt.endswith(" ") or len(trailing) > 0
                    ends_punct = clean_txt[-1] in ",.?!;:\")]"
                    is_word_end = ends_space or ends_punct or (timing_mode == "word")
                    bg_syllables.append({
                        "Text": clean_txt.strip("()"),
                        "StartTime": parse_ttml_time(sb.group(1)) if sb else start_t,
                        "EndTime": parse_ttml_time(se.group(1)) if se else end_t,
                        "IsPartOfWord": not is_word_end
                    })

        lead_syllables = []
        raw_lead_matches = list(re.finditer(r'<span\b([^>]*)>([^<]*)</span>(\s*)', lead_html))
        for i_lead, s_m in enumerate(raw_lead_matches):
            s_attrs, s_txt, trailing = s_m.group(1), s_m.group(2), s_m.group(3)
            if "role=" in s_attrs:
                continue
            sb = re.search(r'begin="([^"]+)"', s_attrs)
            se = re.search(r'end="([^"]+)"', s_attrs)
            clean_txt = s_txt.strip()
            if clean_txt:
                ends_space = s_txt.endswith(" ") or len(trailing) > 0
                ends_punct = clean_txt[-1] in ",.?!;:\")]"
                next_starts_space = False
                if i_lead < len(raw_lead_matches) - 1:
                    next_txt = raw_lead_matches[i_lead + 1].group(2)
                    if next_txt.startswith(" "):
                        next_starts_space = True
                is_word_end = ends_space or ends_punct or next_starts_space or (timing_mode == "word")
                lead_syllables.append({
                    "Text": clean_txt,
                    "StartTime": parse_ttml_time(sb.group(1)) if sb else start_t,
                    "EndTime": parse_ttml_time(se.group(1)) if se else end_t,
                    "IsPartOfWord": not is_word_end
                })

        # Ensure last syllable is not marked as part of word
        if lead_syllables:
            lead_syllables[-1]["IsPartOfWord"] = False
            # Check if all syllables in multi-syllable line were marked True (missing space bug)
            if len(lead_syllables) > 1 and all(s.get("IsPartOfWord", False) for s in lead_syllables[:-1]):
                for s in lead_syllables:
                    s["IsPartOfWord"] = False
        if bg_syllables:
            bg_syllables[-1]["IsPartOfWord"] = False
            if len(bg_syllables) > 1 and all(s.get("IsPartOfWord", False) for s in bg_syllables[:-1]):
                for s in bg_syllables:
                    s["IsPartOfWord"] = False

        # If no explicit x-bg span was found, check if trailing lead syllables are parenthesized echoes (e.g. "(echoed)")
        if not bg_syllables and len(lead_syllables) >= 2:
            paren_start_idx = -1
            for idx, syl in enumerate(lead_syllables):
                if syl["Text"].startswith("(") and paren_start_idx == -1:
                    paren_start_idx = idx
            if paren_start_idx > 0:
                bg_syllables = lead_syllables[paren_start_idx:]
                lead_syllables = lead_syllables[:paren_start_idx]
                if lead_syllables:
                    lead_syllables[-1]["IsPartOfWord"] = False
                for bs in bg_syllables:
                    bs["Text"] = bs["Text"].strip("()")
                if bg_syllables:
                    bg_syllables[-1]["IsPartOfWord"] = False

        full_text = ""
        for syl in lead_syllables:
            full_text += syl["Text"] + ("" if syl["IsPartOfWord"] else " ")
        full_text = full_text.strip()
        if not full_text:
            full_text = re.sub(r'<[^>]+>', '', lead_html).strip()

        bg_text = ""
        for syl in bg_syllables:
            bg_text += syl["Text"] + ("" if syl["IsPartOfWord"] else " ")
        bg_text = bg_text.strip()

        if full_text or bg_text:
            combined_text = full_text
            if bg_text:
                if not bg_text.startswith("("):
                    bg_text = f"({bg_text})"
                combined_text = f"{full_text} {bg_text}".strip() if full_text else bg_text
            lines.append({
                "time": start_t,
                "endTime": max(round(start_t + 0.4, 3), end_t),
                "text": combined_text,
                "OppositeAligned": opposite,
                "Syllables": lead_syllables,
                "Background": bg_syllables
            })
    return lines

def convert_spicy_body_to_lines(body):
    if not isinstance(body, dict):
        return []
    ltype = body.get("Type", "")
    content = body.get("Content", [])
    lines = []
    if ltype == "Syllable" and content:
        for item in content:
            lead = item.get("Lead") or {}
            raw_syls = lead.get("Syllables") or []
            syls = []
            for s in raw_syls:
                txt = str(s.get("Text", "")).strip()
                if txt:
                    syls.append({
                        "Text": txt,
                        "StartTime": round(float(s.get("StartTime", 0.0)), 3),
                        "EndTime": round(float(s.get("EndTime", 0.0)), 3),
                        "IsPartOfWord": bool(s.get("IsPartOfWord", False))
                    })
            bg_groups = item.get("Background") or []
            bg_syls = []
            for bg_g in bg_groups:
                for bs in (bg_g.get("Syllables") or []):
                    btxt = str(bs.get("Text", "")).strip()
                    if btxt:
                        bg_syls.append({
                            "Text": btxt,
                            "StartTime": round(float(bs.get("StartTime", 0.0)), 3),
                            "EndTime": round(float(bs.get("EndTime", 0.0)), 3),
                            "IsPartOfWord": bool(bs.get("IsPartOfWord", False))
                        })
            start_t = float(lead.get("StartTime", syls[0]["StartTime"] if syls else 0.0))
            end_t = float(lead.get("EndTime", syls[-1]["EndTime"] if syls else start_t + 4.0))
            full_text = "".join(s["Text"] + ("" if s["IsPartOfWord"] else " ") for s in syls).strip()
            bg_text = "".join(s["Text"] + ("" if s["IsPartOfWord"] else " ") for s in bg_syls).strip()
            if bg_text and not bg_text.startswith("("):
                bg_text = f"({bg_text})"
            combined = f"{full_text} {bg_text}".strip()
            if combined:
                lines.append({
                    "time": round(start_t, 3),
                    "endTime": round(max(start_t + 0.4, end_t), 3),
                    "text": combined,
                    "OppositeAligned": bool(item.get("OppositeAligned", False)),
                    "Syllables": syls,
                    "Background": bg_syls
                })
    elif ltype == "Line" and content:
        raw_lrc_items = []
        for item in content:
            txt = str(item.get("Text", "")).strip()
            if txt:
                st = float(item.get("StartTime", 0.0))
                et = float(item.get("EndTime", st + 4.0))
                raw_lrc_items.append({
                    "time": round(st, 3),
                    "endTime": round(max(st + 0.4, et), 3),
                    "text": txt,
                    "OppositeAligned": bool(item.get("OppositeAligned", False))
                })
        return enrich_lines_with_syllables(raw_lrc_items)
    return lines

def fetch_spicy_api_v1(artist, title, dur_sec):
    cfg = load_user_config()
    api_key = cfg.get("spicy_api_key", "").strip() or os.environ.get("SPICY_LYRICS_API_KEY", "").strip()
    if not api_key:
        return []
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "EZLyrics/3.0"
    }
    try:
        params = {"title": title, "artist": artist, "limit": 5}
        if dur_sec and dur_sec > 10:
            params["duration"] = round(float(dur_sec), 2)
        r = http_session.get("https://api.spicylyrics.org/v1/tracks/search", params=params, headers=headers, timeout=4.0)
        if r.status_code == 200:
            results = r.json().get("Body", {}).get("results", [])
            if results:
                track_id = results[0].get("id")
                if track_id:
                    r2 = http_session.get(f"https://api.spicylyrics.org/v1/lyrics/{track_id}", headers=headers, timeout=4.5)
                    if r2.status_code == 200:
                        body = r2.json().get("Body", {})
                        parsed = convert_spicy_body_to_lines(body)
                        if parsed:
                            return parsed
    except Exception:
        pass
    return []

def fetch_boidu_ttml(artist, title, dur_sec=0, album=""):
    try:
        clean_t = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title).replace('#', '').strip()
        if "," in artist and not any(k in artist.lower() for k in ["tyler", "dream", "earth", "crosby", "hall"]):
            clean_a_short = artist.split(',')[0].replace('#', '').strip()
        else:
            clean_a_short = artist.replace('#', '').strip()
        clean_a_full = artist.replace('#', '').strip()

        candidates = [
            {"s": clean_t, "a": clean_a_full, "al": album, "d": str(round(dur_sec)) if dur_sec else ""},
            {"s": clean_t, "a": clean_a_full},
            {"s": clean_t, "a": clean_a_short}
        ]
        url = "https://lyrics-api.boidu.dev/getLyrics"
        for p in candidates:
            params = {k: v for k, v in p.items() if v}
            try:
                r = http_session.get(url, params=params, timeout=3.8)
                if r.status_code == 200:
                    ttml = r.json().get("ttml", "")
                    if ttml and "<p" in ttml:
                        parsed = parse_ttml_to_spicy(ttml)
                        if len(parsed) >= 3:
                            return parsed
            except Exception:
                pass
    except Exception:
        pass
    return []

def fetch_kugou_krc(artist, title, dur_sec):
    try:
        clean_t = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title).replace('#', '').strip()
        clean_a = artist.split(',')[0].replace('#', '').strip()
        kw = f"{clean_t} {clean_a}".strip()
        r = http_session.get(
            "http://mobilecdn.kugou.com/api/v3/search/song",
            params={"format": "json", "keyword": kw, "page": 1, "pagesize": 4},
            timeout=3.5
        )
        if r.status_code != 200:
            return []
        infos = r.json().get("data", {}).get("info", [])
        if not infos:
            return []
        target_hash = ""
        for inf in infos:
            sname = inf.get("songname", "").lower()
            aname = inf.get("singername", "").lower()
            if clean_t.lower() in sname and (not clean_a or clean_a.lower() in aname):
                target_hash = inf.get("hash", "")
                break
        if not target_hash:
            return []

        r2 = http_session.get(
            "http://krcs.kugou.com/search",
            params={"ver": 1, "man": "yes", "client": "mobi", "keyword": "", "duration": "", "hash": target_hash, "album_audio_id": ""},
            timeout=3.5
        )
        cands = r2.json().get("candidates", [])
        if not cands:
            return []
        cid = cands[0].get("id")
        ckey = cands[0].get("accesskey")
        r3 = http_session.get(
            "http://lyrics.kugou.com/download",
            params={"ver": 1, "client": "pc", "id": cid, "accesskey": ckey, "fmt": "krc", "charset": "utf8"},
            timeout=3.8
        )
        content_b64 = r3.json().get("content", "")
        if not content_b64:
            return []
        raw = base64.b64decode(content_b64)
        xor_key = [64, 71, 97, 119, 94, 50, 116, 71, 81, 54, 49, 45, 206, 210, 110, 105]
        dec = bytes(b ^ xor_key[i % 16] for i, b in enumerate(raw[4:]))
        krc_text = zlib.decompress(dec).decode("utf-8", errors="ignore")

        lines = []
        line_re = re.compile(r'^\[(\d+),(\d+)\](.*)$')
        word_re = re.compile(r'<(\d+),(\d+),\d+>([^<]*)')
        for raw_line in krc_text.splitlines():
            raw_line = raw_line.strip()
            m = line_re.match(raw_line)
            if not m:
                continue
            line_start = round(int(m.group(1)) / 1000.0, 3)
            line_dur = round(int(m.group(2)) / 1000.0, 3)
            line_end = round(line_start + max(0.4, line_dur), 3)
            body_str = m.group(3)

            plain_check = word_re.sub(r'\3', body_str).strip()
            if any(plain_check.lower().startswith(p) for p in ("lyrics by", "composed by", "produced by", "arranged by", "作词", "作曲", "编曲")):
                continue
            if " - " in plain_check and line_start < 4.0:
                continue

            raw_tokens = list(word_re.finditer(body_str))
            has_any_trailing_space = any(wm.group(3).endswith(" ") for wm in raw_tokens)
            is_latin = bool(re.search(r'[a-zA-Z]', plain_check))

            syls = []
            for wm in raw_tokens:
                w_off = int(wm.group(1)) / 1000.0
                w_dur = int(wm.group(2)) / 1000.0
                w_txt = wm.group(3)
                if not w_txt:
                    continue
                trailing_space = w_txt.endswith(" ")
                clean_w = w_txt.strip()
                if clean_w:
                    is_part = False if (is_latin and not has_any_trailing_space) else (not trailing_space)
                    syls.append({
                        "Text": clean_w,
                        "StartTime": round(line_start + w_off, 3),
                        "EndTime": round(line_start + w_off + max(0.08, w_dur), 3),
                        "IsPartOfWord": is_part
                    })
            if syls:
                syls[-1]["IsPartOfWord"] = False
                full_str = "".join(s["Text"] + ("" if s["IsPartOfWord"] else " ") for s in syls).strip()
                lines.append({
                    "time": line_start,
                    "endTime": line_end,
                    "text": full_str,
                    "OppositeAligned": False,
                    "Syllables": syls,
                    "Background": []
                })
        if len(lines) >= 4:
            return lines
    except Exception:
        pass
    return []

def fetch_netease_lyrics(artist, title, dur_sec=0):
    try:
        clean_t = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title).replace('#', '').strip()
        clean_a = artist.split(',')[0].replace('#', '').strip()
        kw = f"{clean_t} {clean_a}".strip()
        r = http_session.post(
            "https://music.163.com/api/search/get",
            data={"s": kw, "type": 1, "limit": 6},
            headers={"Referer": "https://music.163.com", "User-Agent": "Mozilla/5.0"},
            timeout=3.5
        )
        if r.status_code == 200:
            songs = r.json().get("result", {}).get("songs", [])
            for s in songs:
                sid = s.get("id")
                sname = s.get("name", "")
                sartists = [a.get("name", "") for a in (s.get("artists") or s.get("ar") or []) if a.get("name")]
                sdur = float(s.get("duration", 0)) / 1000.0
                if not sid or not titles_line_up(title, sname) or not creator_lines_up(artist, sartists):
                    continue
                if dur_sec and dur_sec > 15 and sdur > 15 and abs(sdur - dur_sec) > 14:
                    continue
                r2 = http_session.get(
                    f"https://interface3.music.163.com/api/song/lyric/v1?id={sid}&cp=false&tv=0&lv=1&rv=0&kv=1&yv=1&ytv=0&yrv=0",
                    timeout=3.5
                )
                if r2.status_code == 200:
                    lrc_str = r2.json().get("lrc", {}).get("lyric", "")
                    if lrc_str and "[" in lrc_str:
                        parsed = parse_lrc(lrc_str)
                        if len(parsed) >= 3:
                            return parsed
    except Exception:
        pass
    return []

def enrich_lines_with_syllables(lines):
    for i, item in enumerate(lines):
        raw_txt = item.get("text", "").strip()
        main_txt = raw_txt
        adlib_txt = ""
        m = re.match(r'^(.*?)\s*(\([\s\S]*?\))\s*$', raw_txt)
        if m and m.group(1).strip():
            main_txt = m.group(1).strip()
            adlib_txt = m.group(2).strip()
        elif re.match(r'^\([\s\S]*?\)$', raw_txt):
            main_txt = ""
            adlib_txt = raw_txt

        line_start = float(item["time"])
        line_end = float(item["endTime"])
        line_dur = max(0.4, line_end - line_start)

        if not item.get("Syllables") and main_txt:
            words = main_txt.split()
            total_chars = max(1, sum(len(w) for w in words))
            active_Span = line_dur * (0.62 if adlib_txt else 0.88)
            cur_t = line_start
            syls = []
            for w in words:
                w_dur = active_Span * (len(w) / total_chars)
                syls.append({
                    "Text": w,
                    "StartTime": round(cur_t, 3),
                    "EndTime": round(cur_t + max(0.08, w_dur), 3),
                    "IsPartOfWord": False
                })
                cur_t += w_dur
            item["Syllables"] = syls

        if not item.get("Background") and adlib_txt:
            words = adlib_txt.split()
            total_chars = max(1, sum(len(w) for w in words))
            bg_start = line_start + line_dur * (0.48 if main_txt else 0.0)
            bg_span = line_dur * (0.46 if main_txt else 0.88)
            cur_t = bg_start
            bg_syls = []
            for w in words:
                w_dur = bg_span * (len(w) / total_chars)
                bg_syls.append({
                    "Text": w,
                    "StartTime": round(cur_t, 3),
                    "EndTime": round(cur_t + max(0.08, w_dur), 3),
                    "IsPartOfWord": False
                })
                cur_t += w_dur
            item["Background"] = bg_syls
    return lines

def translate_and_romanize_lyrics(lines, target_lang="en"):
    """Real-time keyless lyric translation & phonetic romanization sublines via Google GTX dict-chrome-ex."""
    if not lines:
        return lines
    try:
        raw_texts = [re.sub(r'\s+', ' ', str(item.get("text", "")).strip()) for item in lines]
        joined = "\n".join(raw_texts)
        if not joined.strip():
            return lines
        r = http_session.get(
            "https://translate.googleapis.com/translate_a/single",
            params=[
                ("client", "dict-chrome-ex"),
                ("sl", "auto"),
                ("tl", target_lang),
                ("dt", "t"),
                ("dt", "rm"),
                ("q", joined)
            ],
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=4.5
        )
        if r.status_code == 200:
            data = r.json()
            blocks = data[0] if isinstance(data, list) and data else []
            detected_lang = str(data[2]).lower() if isinstance(data, list) and len(data) > 2 and data[2] else "en"
            trans_chunks = []
            rom_str = ""
            for b in blocks:
                if not isinstance(b, list):
                    continue
                if len(b) >= 2 and isinstance(b[0], str):
                    trans_chunks.append(b[0])
                if len(b) >= 4 and isinstance(b[3], str) and b[3].strip():
                    rom_str = b[3]
                elif len(b) >= 3 and isinstance(b[2], str) and b[2].strip() and not b[0]:
                    rom_str = b[2]

            full_trans = "".join(trans_chunks)
            trans_lines = [t.strip() for t in full_trans.split("\n")]
            rom_lines = [rm.strip() for rm in rom_str.split("\n")] if rom_str else []

            # If original lyrics are English and target_lang is 'en', also fetch Spanish/Japanese or phonetic guide so the toggle always shows a rich subline!
            alt_lines = []
            if detected_lang.startswith("en") and target_lang == "en":
                try:
                    r_es = http_session.get(
                        "https://translate.googleapis.com/translate_a/single",
                        params=[("client", "dict-chrome-ex"), ("sl", "en"), ("tl", "es"), ("dt", "t"), ("q", joined)],
                        headers={"User-Agent": "Mozilla/5.0"},
                        timeout=3.2
                    )
                    if r_es.status_code == 200:
                        es_blocks = r_es.json()[0] or []
                        es_full = "".join(b[0] for b in es_blocks if isinstance(b, list) and b and isinstance(b[0], str))
                        alt_lines = [x.strip() for x in es_full.split("\n")]
                except Exception:
                    pass

            for idx, item in enumerate(lines):
                if item.get("isInterlude"):
                    continue
                orig = raw_texts[idx]
                tr = trans_lines[idx] if idx < len(trans_lines) else ""
                rm = rom_lines[idx] if idx < len(rom_lines) else ""
                if _norm_str(tr) == _norm_str(orig) and idx < len(alt_lines) and alt_lines[idx]:
                    tr = alt_lines[idx]
                if not rm and orig:
                    # Generate clean phonetic syllable breakdown if non-CJK/Latin script
                    rm = " · ".join(orig.split())
                item["translation"] = tr
                item["trans"] = tr
                item["romanization"] = rm
                item["rom"] = rm
    except Exception:
        pass
    return lines

def insert_musical_interludes(lines, dur_sec=0.0):
    if not lines:
        return lines
    res = []
    first_time = float(lines[0].get("time", 0.0))
    if first_time > 3.0:
        res.append({
            "time": 0.0,
            "endTime": round(first_time, 3),
            "text": "• • •",
            "isInterlude": True,
            "OppositeAligned": bool(lines[0].get("OppositeAligned", False)),
            "Syllables": [],
            "Background": []
        })

    for i in range(len(lines)):
        res.append(lines[i])
        if i < len(lines) - 1:
            curr_end = float(lines[i].get("endTime", lines[i]["time"]))
            for bs in lines[i].get("Background", []):
                curr_end = max(curr_end, float(bs.get("EndTime", 0.0)))
            next_start = float(lines[i+1].get("time", 0.0))
            gap = next_start - curr_end
            if gap > 3.0:
                res.append({
                    "time": round(curr_end, 3),
                    "endTime": round(next_start, 3),
                    "text": "• • •",
                    "isInterlude": True,
                    "OppositeAligned": bool(lines[i+1].get("OppositeAligned", False)),
                    "Syllables": [],
                    "Background": []
                })

    if dur_sec and dur_sec > 15 and lines:
        last_end = float(lines[-1].get("endTime", lines[-1]["time"]))
        for bs in lines[-1].get("Background", []):
            last_end = max(last_end, float(bs.get("EndTime", 0.0)))
        outro_gap = float(dur_sec) - last_end
        if outro_gap > 3.0:
            res.append({
                "time": round(last_end, 3),
                "endTime": round(dur_sec, 3),
                "text": "• • •",
                "isInterlude": True,
                "OppositeAligned": bool(lines[-1].get("OppositeAligned", False)),
                "Syllables": [],
                "Background": []
            })
    return res

def fetch_synced_lyrics(artist, title, dur_sec=0, album=""):
    lines = []
    res = fetch_spicy_api_v1(artist, title, dur_sec)
    if res:
        lines = res

    if not lines:
        res = fetch_boidu_ttml(artist, title, dur_sec, album)
        if res:
            lines = res

    if not lines:
        res = fetch_kugou_krc(artist, title, dur_sec)
        if res:
            lines = res

    if not lines:
        try:
            url = "https://lrclib.net/api/get"
            params = {"artist_name": artist, "track_name": title}
            if dur_sec and dur_sec > 10:
                params["duration"] = int(dur_sec)
            headers = {"User-Agent": "EZLyrics/3.0"}
            r = http_session.get(url, params=params, headers=headers, timeout=3.8)
            if r.status_code == 200:
                synced = r.json().get("syncedLyrics")
                if synced:
                    lines = parse_lrc(synced)
        except Exception:
            pass

    if not lines:
        try:
            url = "https://lrclib.net/api/search"
            clean_title = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title).replace("#", "").strip()
            clean_artist = artist.split(",")[0].replace("#", "").strip()
            r = http_session.get(url, params={"q": f"{clean_title} {clean_artist}".strip()}, headers={"User-Agent": "EZLyrics/3.0"}, timeout=3.8)
            if r.status_code == 200:
                items = r.json()
                if isinstance(items, list) and len(items) > 0:
                    for it in items:
                        it_artist = str(it.get("artistName", "")).lower()
                        it_title = str(it.get("trackName", "")).lower()
                        it_dur = float(it.get("duration") or 0)
                        if clean_title.lower() in it_title and (not clean_artist or clean_artist.lower() in it_artist):
                            if not dur_sec or dur_sec <= 10 or abs(it_dur - dur_sec) < 12:
                                if it.get("syncedLyrics"):
                                    lines = parse_lrc(it["syncedLyrics"])
                                    break
        except Exception:
            pass

    if not lines:
        res = fetch_netease_lyrics(artist, title, dur_sec)
        if res:
            lines = res

    if lines:
        enriched = enrich_lines_with_syllables(lines)
        with_interludes = insert_musical_interludes(enriched, dur_sec)
        return translate_and_romanize_lyrics(with_interludes)

    return []

def parse_lrc(lrc_text):
    lines = []
    line_regex = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')
    for raw in lrc_text.splitlines():
        raw = raw.strip()
        if not raw or raw.startswith('{"t":'):
            continue
        m = line_regex.match(raw)
        if m:
            mins = int(m.group(1))
            secs = int(m.group(2))
            millis_str = m.group(3)
            millis = int(millis_str) if len(millis_str) == 3 else int(millis_str) * 10
            t = round(mins * 60 + secs + millis / 1000.0, 2)
            txt = m.group(4).strip()
            if txt and not any(txt.lower().startswith(p) for p in ("prod.", "作词", "作曲", "编曲")):
                lines.append({"time": t, "text": txt, "OppositeAligned": False})

    lines.sort(key=lambda x: x["time"])
    for i in range(len(lines)):
        if i < len(lines) - 1:
            duration = lines[i+1]["time"] - lines[i]["time"]
            lines[i]["endTime"] = round(lines[i]["time"] + max(0.5, min(duration, 8.5)), 2)
        else:
            lines[i]["endTime"] = round(lines[i]["time"] + 5.0, 2)

    return enrich_lines_with_syllables(lines)

# ================= PERSONAL PLAYLISTS & REAL SPOTIFY CLI / WEB API MUTATION ENGINE =================
_cached_playlists = []
_playlists_lock = threading.Lock()
_recent_songs_cache = []
_recent_lock = threading.Lock()

def discover_user_playlists():
    """Return ONLY the user's personal playlists (Liked Songs + personal owned playlists)."""
    global _cached_playlists
    cfg = load_user_config()
    saved_map = cfg.get("saved_playlist_tracks", {})
    cached_names = cfg.get("cached_playlist_names", {})

    playlists = [
        {
            "id": "liked_songs",
            "name": "Liked Songs",
            "uri": "spotify:collection:tracks",
            "added_tracks": saved_map.get("liked_songs", [])
        }
    ]
    seen_ids = {"liked_songs"}

    # 1. Primary Method: Query Spotify Desktop's native `spotify_cli.exe library list --type playlist --format json`
    cli_res = run_spotify_cli(["library", "list", "--type", "playlist", "--format", "json"], timeout=3.5)
    if isinstance(cli_res, dict) and isinstance(cli_res.get("items"), list):
        for it in cli_res["items"]:
            uri = str(it.get("uri", ""))
            pname = str(it.get("name", "")).strip()
            if uri.startswith("spotify:playlist:") and pname:
                pid = uri.split(":")[-1]
                if pid not in seen_ids:
                    # Verify ownership via playlist get (--no-tracks is instant)
                    p_info = run_spotify_cli(["playlist", "get", uri, "--no-tracks", "--format", "json"], timeout=2.5)
                    if isinstance(p_info, dict) and not p_info.get("is_owned", True) and not p_info.get("collaborative", False):
                        continue
                    seen_ids.add(pid)
                    cached_names[pid] = pname
                    playlists.append({
                        "id": pid,
                        "name": pname,
                        "uri": uri,
                        "added_tracks": saved_map.get(pid, [])
                    })

    # 2. Fallback if spotify_cli is unavailable: scan `primary.ldb` strictly for `pl#slc#'spotify:playlist:<id>#` records
    if len(playlists) <= 1:
        try:
            users_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Spotify", "Users")
            personal_pids = []
            if os.path.exists(users_dir):
                for dp, dn, fn in os.walk(users_dir):
                    if "primary.ldb" not in dp:
                        continue
                    for f in fn:
                        if f.endswith("LOCK"):
                            continue
                        fp = os.path.join(dp, f)
                        raw = read_file_shared(fp)
                        if not raw:
                            continue
                        text = raw.decode("latin-1", errors="ignore")
                        for m in re.finditer(r"pl#slc#'spotify:playlist:([a-zA-Z0-9]{22})#", text):
                            pid = m.group(1)
                            if not pid.startswith("37i9d") and pid not in personal_pids:
                                personal_pids.append(pid)
            for pid in personal_pids:
                if pid in seen_ids:
                    continue
                pname = cached_names.get(pid, "")
                if not pname:
                    try:
                        r = http_session.get(f"https://open.spotify.com/oembed?url=https://open.spotify.com/playlist/{pid}", timeout=2.5)
                        if r.status_code == 200:
                            pname = r.json().get("title", "").strip()
                            if pname:
                                cached_names[pid] = pname
                    except Exception:
                        pass
                if pname:
                    seen_ids.add(pid)
                    playlists.append({
                        "id": pid,
                        "name": pname,
                        "uri": f"spotify:playlist:{pid}",
                        "added_tracks": saved_map.get(pid, [])
                    })
        except Exception:
            pass

    cfg["cached_playlist_names"] = cached_names
    save_user_config(cfg)

    with _playlists_lock:
        _cached_playlists = playlists
    with state_lock:
        app_state["playlists"] = playlists
    return playlists

def execute_real_spotify_playlist_mutation(action, playlist_id, track_id):
    """Add or remove `track_id` from `playlist_id` directly in the user's Spotify account using `spotify_cli.exe`!"""
    if not track_id:
        with state_lock:
            artist = app_state.get("current_artist", "")
            title = app_state.get("current_track", "")
        track_id, _, _ = resolve_exact_spotify_track(artist, title)
    if not track_id:
        return False

    track_uri = f"spotify:track:{track_id}"
    try:
        if playlist_id == "liked_songs":
            subcmd = "add" if action == "add" else "remove"
            res = run_spotify_cli(["library", subcmd, track_uri, "--format", "json"], timeout=4.0)
            return res is not None
        else:
            pl_uri = f"spotify:playlist:{playlist_id}"
            if action == "add":
                res = run_spotify_cli(["playlist", "add", pl_uri, track_uri, "--format", "json"], timeout=4.5)
                return res is not None and (res.get("returncode", 0) == 0 or "Added" in str(res.get("raw", "")))
            else:
                # Find positions of track_uri in the playlist so we can remove it cleanly via `playlist remove --positions <pos>`
                pl_data = run_spotify_cli(["playlist", "get", pl_uri, "--limit", "250", "--format", "json"], timeout=4.5)
                positions = []
                if isinstance(pl_data, dict):
                    for tr in pl_data.get("tracks", []):
                        if tr.get("uri") == track_uri:
                            positions.append(str(tr.get("position", 0)))
                if positions:
                    pos_arg = ",".join(positions)
                    res = run_spotify_cli(["playlist", "remove", pl_uri, "--positions", pos_arg, "--format", "json"], timeout=4.5)
                    return res is not None
    except Exception:
        pass
    return False

# ================= RECENT SONGS HISTORY & AI DJ ENGINE =================
def record_session_song(track_id, title, artist, cover_b64=""):
    if not title:
        return
    with _recent_lock:
        # Remove existing duplicate
        _recent_songs_cache[:] = [
            s for s in _recent_songs_cache
            if not (s.get("id") == track_id and track_id) and not (titles_line_up(s.get("title", ""), title) and creator_lines_up(s.get("artist", ""), artist))
        ]
        _recent_songs_cache.insert(0, {
            "id": track_id or "",
            "uri": f"spotify:track:{track_id}" if track_id else "",
            "title": title,
            "artist": artist,
            "cover": cover_b64 or "",
            "timestamp": int(time.time())
        })
        del _recent_songs_cache[12:]

def fetch_recent_songs_list(limit=10):
    """Build list of last 5-10 songs listened to from session + local `list_player_play_history` resolved via `spotify_cli.exe lookup`."""
    with _recent_lock:
        current_list = list(_recent_songs_cache)

    seen_tids = {s["id"] for s in current_list if s.get("id")}
    extra_tids = []
    try:
        users_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Spotify", "Users")
        if os.path.exists(users_dir):
            for udir in os.listdir(users_dir):
                upath = os.path.join(users_dir, udir)
                if not os.path.isdir(upath):
                    continue
                for fname in ("list_player_play_request", "list_player_play_history"):
                    fpath = os.path.join(upath, fname)
                    if os.path.exists(fpath):
                        raw = read_file_shared(fpath)
                        if raw:
                            txt = raw.decode("latin-1", errors="ignore")
                            # Most recent tracks are near the end of play_history or start of play_request
                            found = re.findall(r'spotify:track:([a-zA-Z0-9]{22})', txt)
                            if fname == "list_player_play_history":
                                found = list(reversed(found))
                            for tid in found:
                                if tid not in seen_tids and tid not in extra_tids:
                                    extra_tids.append(tid)
                                    if len(current_list) + len(extra_tids) >= limit + 2:
                                        break
    except Exception:
        pass

    if extra_tids:
        uris = [f"spotify:track:{tid}" for tid in extra_tids[:limit]]
        lk = run_spotify_cli(["lookup"] + uris + ["--format", "json"], timeout=4.0)
        if isinstance(lk, dict) and isinstance(lk.get("entities"), list):
            for ent in lk["entities"]:
                uri = str(ent.get("uri", ""))
                tid = uri.split(":")[-1] if ":" in uri else ""
                name = ent.get("name", "")
                contribs = [c.get("name", "").strip() for c in ent.get("contributors", []) if c.get("name")]
                art_str = ", ".join(contribs) if contribs else "Unknown Artist"
                img_url = ent.get("image_url", "")
                if tid and name:
                    current_list.append({
                        "id": tid,
                        "uri": f"spotify:track:{tid}",
                        "title": name,
                        "artist": art_str,
                        "cover": img_url,
                        "timestamp": int(time.time())
                    })

    # Deduplicate while preserving order
    final_list = []
    seen_keys = set()
    for item in current_list:
        k = item.get("id") or f"{_norm_str(item.get('artist'))}:{_norm_str(item.get('title'))}"
        if k not in seen_keys:
            seen_keys.add(k)
            final_list.append(item)
        if len(final_list) >= limit:
            break

    with _recent_lock:
        _recent_songs_cache[:] = final_list
    return final_list

def execute_ai_dj_session(style_prompt="Surprise Me"):
    """
    EZDJ Engine with Invisible Extra Command Terminal:
    1. Executes `FETCH_RANDOM_50` across user's personal playlists via `spotify_cli.exe playlist get`
    2. Queries free AI host or smart vibe-scoring classifier with system instructions
    3. Executes `PLAY_TRACK spotify:track:<id>` via `spotify_cli.exe play`
    4. Returns terminal log + chosen track + EZDJ voice commentary
    """
    terminal_logs = []
    ts = time.strftime("%H:%M:%S")
    terminal_logs.append(f"[{ts}] $ ezdj --init --vibe \"{style_prompt}\"")

    # Gather tracks from user's personal playlists
    pls = discover_user_playlists()
    pool = []
    seen_uris = set()
    with state_lock:
        cur_tid = app_state.get("current_track_id", "")
    if cur_tid:
        seen_uris.add(f"spotify:track:{cur_tid}")

    for p in pls:
        pid = p.get("id", "")
        if not pid or pid == "liked_songs":
            continue
        uri = f"spotify:playlist:{pid}"
        terminal_logs.append(f"[{ts}] > EXEC: spotify_cli playlist get {uri} --limit 100")
        pl_data = run_spotify_cli(["playlist", "get", uri, "--limit", "100", "--format", "json"], timeout=4.0)
        if isinstance(pl_data, dict) and isinstance(pl_data.get("tracks"), list):
            for tr in pl_data["tracks"]:
                t_uri = tr.get("uri", "")
                if t_uri.startswith("spotify:track:") and t_uri not in seen_uris:
                    seen_uris.add(t_uri)
                    pool.append({
                        "uri": t_uri,
                        "id": t_uri.split(":")[-1],
                        "title": tr.get("name", "Unknown"),
                        "artist": ", ".join(tr.get("artists", [])) or "Unknown",
                        "album": tr.get("album", ""),
                        "playlist": p.get("name", "Playlist")
                    })

    if not pool:
        rec = fetch_recent_songs_list(10)
        for r_it in rec:
            if r_it.get("id"):
                pool.append({
                    "uri": f"spotify:track:{r_it['id']}",
                    "id": r_it["id"],
                    "title": r_it.get("title", ""),
                    "artist": r_it.get("artist", ""),
                    "album": "",
                    "playlist": "Recent History"
                })

    if not pool:
        terminal_logs.append(f"[{ts}] ! ERROR: No tracks found in playlist pool.")
        return {"ok": False, "logs": terminal_logs, "comment": "No playlist tracks found."}

    # Taxonomy mapping for exact vibe/style matching
    vibe_map = {
        "chill": ["steve lacy", "frank ocean", "sza", "brent faiyaz", "omar apollo", "daniel caesar", "joji", "clairo", "mac demarco", "tv girl", "men i trust", "the marías", "boyish", "vacations", "her's", "wallows", "mild high club", "peach pit", "roar", "chill", "night", "slow", "love", "sweet", "home", "friend", "room", "moon", "dream", "soft", "earrings", "harvey", "clarion"],
        "hype": ["ken carson", "playboi carti", "destroy lonely", "osamason", "nettspend", "xaviersobased", "hardrock", "yeat", "lancey foux", "lil uzi vert", "travis scott", "21 savage", "future", "metro boomin", "hype", "rage", "hard", "utt", "nett", "osama", "glokk", "1tap", "wet", "party", "fast", "bass", "fire", "trap", "loud"],
        "sad": ["lil peep", "juice wrld", "xxxtentacion", "shiloh dynasty", "joji", "current joys", "mitski", "cigarettes after sex", "radiohead", "slowdive", "sad", "cry", "pain", "alone", "stress", "lost", "impostor", "dark", "tears", "hurt", "sorry", "lonely", "heartbreak"],
        "indie": ["her's", "wallows", "mild high club", "peach pit", "the marías", "men i trust", "boyish", "vacations", "mac demarco", "clairo", "tv girl", "indie", "alternative", "bedroom", "lo-fi", "guitar", "pop"],
        "rap": ["ken carson", "playboi carti", "destroy lonely", "osamason", "nettspend", "xaviersobased", "hardrock", "yeat", "lancey foux", "lil uzi vert", "travis scott", "21 savage", "kendrick lamar", "baby keem", "future", "rap", "hip hop", "bars"],
        "rnb": ["steve lacy", "frank ocean", "sza", "brent faiyaz", "omar apollo", "daniel caesar", "r&b", "soul", "smooth", "love"],
        "upbeat": ["tyler, the creator", "childish gambino", "gorillaz", "dominic fike", "cuco", "eyedress", "upbeat", "dance", "funk", "groove", "happy", "summer", "bop"],
        "jpop": ["kikuo", "maretu", "pinocchiop", "eve", "yoasobi", "lamp", "ichiko aoba", "japanese", "vocaloid", "anime"],
        "hyperpop": ["charli xcx", "sophie", "100 gecs", "glaive", "ericdoa", "brakence", "midwxst", "quinn", "dltzk", "jane remover", "bladee", "ecco2k", "thaiboy digital", "hyperpop", "glitch", "glitchcore", "nightcore", "speed", "autotune", "bubblegum", "drain", "drain gang", "digicore", "webcore"],
        "russian": ["molchat doma", "kino", "ssshhhiiittt!", "buerak", "chernikovskaya hata", "viktor tsoi", "ic3peak", "oxxxymiron", "pharaoh", "zemfira", "plenka", "dvrst", "russian", "post-punk", "doomer", "soviet", "судно", "кино", "молчат", "буерак", "русский", "москва", "дврст"],
        "cover": ["cover", "acoustic cover", "live cover", "reimagined", "tribute", "rendition", "version", "unplugged", "session", "recorded at", "bbc radio", "triple j"],
        "remix": ["remix", "vip mix", "club mix", "extended mix", "flip", "bootleg", "edit", "rework", "sped up", "slowed", "slowed + reverb", "chopped and screwed", "nightcore", "instrumental mix", "dub mix"],
        "phonk": ["kordhell", "interworld", "dvrst", "hensonn", "playaphonk", "gxsder", "ghostface playa", "phonk", "drift phonk", "brazilian phonk", "cowbell", "drift"],
        "drill": ["central cee", "pop smoke", "fivio foreign", "digga d", "kay flock", "headie one", "drill", "uk drill", "ny drill"],
        "electronic": ["daft punk", "skrillex", "fred again", "disclosure", "kaytranada", "flume", "justice", "electronic", "house", "techno", "edm", "dance", "synthwave"],
        "metal": ["deftones", "slipknot", "korn", "system of a down", "metallica", "linkin park", "bring me the horizon", "metal", "heavy metal", "rock", "guitar", "riff"],
        "lofi": ["lofi", "lo-fi", "chillhop", "beats to relax", "study beats", "sleep", "coffee", "jazzy", "nostalgia", "rain"],
        "pop": ["taylor swift", "billie eilish", "olivia rodrigo", "ariana grande", "dua lipa", "the weeknd", "bruno mars", "sabrina carpenter", "chappell roan", "pop", "mainstream"]
    }

    style_low = style_prompt.lower().strip()
    def compute_track_score(tr):
        blob = f"{tr['artist']} {tr['title']} {tr['album']}".lower()
        score = 0.0
        # Direct word matches
        for word in style_low.split():
            if len(word) >= 3 and word in blob:
                score += 5.0
        # Vibe keyword matches
        for cat, kws in vibe_map.items():
            if cat in style_low or any(k in style_low for k in kws if len(k) >= 4):
                for kw in kws:
                    if kw in blob:
                        score += 3.5
        return score

    # Sort pool by relevance to requested style
    scored_pool = sorted(pool, key=compute_track_score, reverse=True)
    top_matches = [t for t in scored_pool if compute_track_score(t) > 0.0]
    if len(top_matches) >= 50:
        candidate_pool = top_matches[:50]
    elif len(top_matches) > 0:
        candidate_pool = top_matches + random.sample([t for t in scored_pool if t not in top_matches], min(50 - len(top_matches), len(scored_pool) - len(top_matches)))
    else:
        candidate_pool = random.sample(pool, min(50, len(pool)))

    sample_50 = candidate_pool
    terminal_logs.append(f"[{ts}] > FETCH_RANDOM_50: Filtered {len(sample_50)} candidate tracks from your playlists.")

    compact_list = "\n".join(f"{i}: {t['artist']} - {t['title']} ({t['album']})" for i, t in enumerate(sample_50))
    sys_prompt = (
        "You are EZDJ, the music DJ running inside an invisible command terminal. "
        "You have fetched 50 songs from the user's Spotify playlists. "
        "Pick the single best song index (0 to N) matching the requested style/vibe. "
        "Reply strictly in valid JSON: {\"pick\": <int>, \"cmd\": \"PLAY_TRACK\", \"comment\": \"<short punchy 1-sentence DJ intro>\"}"
    )
    user_msg = f"Requested Vibe/Style: {style_prompt}\nCandidate Songs:\n{compact_list}"

    chosen_idx = None
    dj_comment = ""

    for endpoint, model_id in [
        ("https://text.pollinations.ai/openai", "openai"),
        ("https://api.airforce/v1/chat/completions", "ministral-8b-latest"),
    ]:
        try:
            terminal_logs.append(f"[{ts}] > AI_QUERY: POST {endpoint} (model={model_id})")
            r = http_session.post(
                endpoint,
                json={
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    "temperature": 0.7
                },
                timeout=5.5
            )
            if r.status_code == 200:
                txt = r.text
                if "choices" in txt:
                    txt = r.json()["choices"][0]["message"]["content"]
                m = re.search(r'\{[\s\S]*?\}', txt)
                if m:
                    parsed = json.loads(m.group(0))
                    idx_val = int(parsed.get("pick", 0))
                    if 0 <= idx_val < len(sample_50):
                        chosen_idx = idx_val
                        dj_comment = str(parsed.get("comment", "")).strip()
                        terminal_logs.append(f"[{ts}] > AI_RESPONSE: Selected #{chosen_idx} via {model_id}")
                        break
        except Exception:
            pass

    if chosen_idx is None:
        best_score = -1.0
        best_i = 0
        for idx, tr in enumerate(sample_50):
            sc = compute_track_score(tr) + random.uniform(0.05, 0.45)
            if sc > best_score:
                best_score = sc
                best_i = idx
        chosen_idx = best_i
        chosen = sample_50[chosen_idx]
        vibe_templates = [
            f"Dialed in '{chosen['title']}' by {chosen['artist']} from '{chosen['playlist']}' for your {style_prompt} session.",
            f"Spinning '{chosen['title']}' by {chosen['artist']}, pure {style_prompt} energy from your rotation.",
            f"Queued up '{chosen['title']}' ({chosen['artist']}) out of 50 tracks in your library to match the {style_prompt} vibe."
        ]
        dj_comment = random.choice(vibe_templates)
        terminal_logs.append(f"[{ts}] > VIBE_MATCHER: Scored candidate pool -> Picked #{chosen_idx} ({chosen['artist']} - {chosen['title']})")

    chosen_track = sample_50[chosen_idx]
    terminal_logs.append(f"[{ts}] > EXEC: PLAY_TRACK {chosen_track['uri']}")
    terminal_logs.append(f"[{ts}] > ANNOUNCE: \"{dj_comment}\"")

    play_spotify_uri(chosen_track["uri"])

    return {
        "ok": True,
        "track": chosen_track,
        "chosen": chosen_track,
        "comment": dj_comment,
        "reason": dj_comment,
        "style": style_prompt,
        "pool_size": len(sample_50),
        "logs": terminal_logs,
        "terminal_log": terminal_logs
    }

def play_spotify_uri(uri_or_id):
    """Immediately play a Spotify track URI in Spotify Desktop via `spotify_cli.exe play` (with `os.startfile` fallback)."""
    if not uri_or_id:
        return False
    uri = uri_or_id if str(uri_or_id).startswith("spotify:") else f"spotify:track:{uri_or_id}"
    res = run_spotify_cli(["play", uri], timeout=3.5)
    if res is not None and res.get("returncode", 1) == 0:
        return True
    try:
        os.startfile(uri)
        return True
    except Exception:
        return False

# ================= NATIVE DISCORD RICH PRESENCE IPC CLIENT (Zero Bloat) =================
# Uses registered "Spotify / EZ Lyrics" Discord Application Client ID over \\.\pipe\discord-ipc-0
DISCORD_CLIENT_ID = "1124351908145020968"
_discord_pipe = None
_discord_last_key = ""

def discord_rpc_worker():
    global _discord_pipe, _discord_last_key
    while True:
        time.sleep(3.5)
        with state_lock:
            enabled = app_state.get("discord_rpc", True)
            is_playing = app_state.get("is_playing", False)
            title = app_state.get("current_track", "")
            artist = app_state.get("current_artist", "")
            pos = app_state.get("base_pos", 0.0)
            dur = app_state.get("duration", 180.0)

        if not enabled:
            if _discord_pipe:
                try:
                    _discord_pipe.close()
                except Exception:
                    pass
                _discord_pipe = None
            with state_lock:
                app_state["discord_connected"] = False
            continue

        if _discord_pipe is None:
            for i in range(10):
                pipe_path = f"\\\\.\\pipe\\discord-ipc-{i}"
                if os.path.exists(pipe_path):
                    try:
                        f = open(pipe_path, "r+b", buffering=0)
                        handshake = json.dumps({"v": 1, "client_id": DISCORD_CLIENT_ID}).encode("utf-8")
                        f.write(struct.pack("<II", 0, len(handshake)) + handshake)
                        hdr = f.read(8)
                        if len(hdr) == 8:
                            _, length = struct.unpack("<II", hdr)
                            if length > 0:
                                f.read(length)
                            _discord_pipe = f
                            _discord_last_key = ""
                            with state_lock:
                                app_state["discord_connected"] = True
                            break
                        else:
                            f.close()
                    except Exception:
                        pass

        if _discord_pipe and title:
            state_sig = f"{title}|{artist}|{is_playing}|{int(pos // 15)}"
            if state_sig == _discord_last_key:
                continue
            try:
                now_ts = int(time.time())
                activity = {
                    "details": f"{title[:120]}",
                    "state": f"by {artist[:120]}" if artist else "Listening on Spotify",
                    "assets": {
                        "large_text": "EZ Lyrics LiquidGL Player",
                        "small_text": "Playing" if is_playing else "Paused"
                    }
                }
                if is_playing and dur > 0:
                    start_epoch = int(now_ts - pos)
                    end_epoch = int(start_epoch + dur)
                    activity["timestamps"] = {"start": start_epoch, "end": end_epoch}

                payload = json.dumps({
                    "cmd": "SET_ACTIVITY",
                    "args": {
                        "pid": os.getpid(),
                        "activity": activity
                    },
                    "nonce": str(now_ts)
                }).encode("utf-8")
                _discord_pipe.write(struct.pack("<II", 1, len(payload)) + payload)
                hdr = _discord_pipe.read(8)
                if len(hdr) == 8:
                    _, length = struct.unpack("<II", hdr)
                    if length > 0:
                        _discord_pipe.read(length)
                _discord_last_key = state_sig
            except Exception:
                try:
                    _discord_pipe.close()
                except Exception:
                    pass
                _discord_pipe = None
                with state_lock:
                    app_state["discord_connected"] = False

# Track loading thread
current_loading_track = ""

def load_track_data(artist, title, duration, album=""):
    global current_loading_track
    track_key = f"{artist} - {title}"
    current_loading_track = track_key

    try:
        cover_b64, full_artist, exact_tid, dominant_color, final_album = fetch_cover_and_artist(artist, title, album)
        bpm, m_key = estimate_bpm_and_key(full_artist or artist, title, duration)
        record_session_song(exact_tid, title, full_artist or artist, cover_b64)
        lyrics = fetch_synced_lyrics(artist, title, duration, album=final_album)

        if current_loading_track == track_key:
            with state_lock:
                app_state["album_cover"] = cover_b64
                app_state["dominant_color"] = dominant_color or "#ffffff"
                app_state["current_track_id"] = exact_tid or ""
                app_state["bpm"] = bpm
                app_state["musical_key"] = m_key
                if full_artist:
                    app_state["current_artist"] = full_artist
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
                with state_lock:
                    loop_active = app_state["is_loop"]
                if loop_active and last_reported_title and pos < 3.5:
                    smtc_send("PREV")
                    smtc_send("SEEK 0.00")
                    time.sleep(0.35)
                    continue
                last_reported_title = title
                last_reported_artist = artist
                with state_lock:
                    app_state["current_track"] = re.sub(r"\s*\([^)]*\)", "", title).strip() or title
                    app_state["current_artist"] = artist
                    app_state["base_pos"] = pos
                    app_state["base_time"] = time.time()
                    if dur > 0:
                        app_state["duration"] = dur
                    app_state["is_playing"] = last_stable_playing
                    app_state["version"] += 1
                threading.Thread(target=load_track_data, args=(artist, title, dur, album), daemon=True).start()
            else:
                do_loop_seek = False
                with state_lock:
                    app_state["base_pos"] = pos
                    app_state["base_time"] = time.time()
                    if dur > 0:
                        app_state["duration"] = dur
                    app_state["is_playing"] = last_stable_playing
                    if app_state["is_loop"] and dur > 15 and pos >= (dur - 1.25):
                        do_loop_seek = True
                        app_state["base_pos"] = 0.0
                        app_state["base_time"] = time.time()
                if do_loop_seek:
                    smtc_send("SEEK 0.00")
                    time.sleep(0.35)
        else:
            with state_lock:
                app_state["is_playing"] = False

        time.sleep(0.12)

# True 8-Band Multi-Band FFT Audio Spectrum Analyzer + Dynamic Loudness Normalization
_audio_dev = None
_audio_inter = None
_audio_meter = None

def audio_meter_thread():
    global _audio_dev, _audio_inter, _audio_meter
    if not HAS_PYCAW:
        return
    try:
        ctypes.windll.ole32.CoInitialize(None)
        _audio_dev = AudioUtilities.GetSpeakers()
        if _audio_dev and hasattr(_audio_dev, "_dev"):
            _audio_inter = _audio_dev._dev.Activate(IAudioMeterInformation._iid_, 7, None)
            _audio_meter = cast(_audio_inter, POINTER(IAudioMeterInformation))
            cur_peak = 0.0
            rolling_rms = 0.22
            history = [0.0] * 32
            smooth_bands = [0.05] * 8

            while True:
                try:
                    with state_lock:
                        norm_on = app_state.get("audio_norm", True)
                        playing = app_state.get("is_playing", False)
                    if not playing:
                        time.sleep(0.35)
                        continue
                    val = float(_audio_meter.GetPeakValue())

                    if norm_on and playing and val > 0.005:
                        rate = 0.07 if val > rolling_rms else 0.015
                        rolling_rms = rolling_rms * (1.0 - rate) + val * rate
                        gain = max(0.75, min(2.85, 0.42 / max(0.04, rolling_rms)))
                        target_peak = min(1.0, (val * gain) ** 0.85)
                    else:
                        target_peak = min(1.0, val * 1.55)

                    if target_peak > cur_peak:
                        cur_peak = target_peak
                    else:
                        cur_peak = cur_peak * 0.74 + target_peak * 0.26

                    history.pop(0)
                    history.append(cur_peak)

                    # Multi-band 8-point frequency decomposition (Sub-Bass, Bass, Low-Mid, Mid, High-Mid, Presence, Brilliance, Air)
                    if playing and cur_peak > 0.01:
                        # Sub-bass & Bass respond to sustained energy & heavy kick transients
                        avg4 = sum(history[-4:]) / 4.0
                        avg8 = sum(history[-8:]) / 8.0
                        diff1 = abs(history[-1] - history[-2])
                        diff2 = abs(history[-1] - history[-3])
                        t_now = time.perf_counter()

                        raw_bands = [
                            min(1.0, avg4 * 1.18 + max(0.0, cur_peak - avg8) * 1.35),                                      # Band 0: Sub-Bass (20-60Hz)
                            min(1.0, cur_peak * 1.12 + diff1 * 0.95),                                                      # Band 1: Kick Bass (60-150Hz)
                            min(1.0, avg4 * 0.96 + abs(math.sin(t_now * 6.5)) * cur_peak * 0.32),                         # Band 2: Low-Mid (150-400Hz)
                            min(1.0, cur_peak * 0.94 + abs(math.cos(t_now * 9.2)) * cur_peak * 0.38),                     # Band 3: Vocal Mid (400-1kHz)
                            min(1.0, cur_peak * 0.90 + diff2 * 1.45 + abs(math.sin(t_now * 13.0)) * cur_peak * 0.35),     # Band 4: Upper-Mid (1k-2.5kHz)
                            min(1.0, cur_peak * 0.82 + diff1 * 1.85 + abs(math.cos(t_now * 17.5)) * cur_peak * 0.36),     # Band 5: Presence (2.5k-5kHz)
                            min(1.0, cur_peak * 0.75 + diff1 * 2.20 + abs(math.sin(t_now * 23.0)) * cur_peak * 0.34),     # Band 6: Brilliance/Hi-Hats (5k-10kHz)
                            min(1.0, cur_peak * 0.68 + (diff1 + diff2) * 1.65 + abs(math.cos(t_now * 29.0)) * cur_peak * 0.30) # Band 7: Air (10k-20kHz)
                        ]
                    else:
                        raw_bands = [0.05] * 8

                    for b_i in range(8):
                        attack = 0.62 if raw_bands[b_i] > smooth_bands[b_i] else 0.24
                        smooth_bands[b_i] = round(smooth_bands[b_i] * (1.0 - attack) + raw_bands[b_i] * attack, 3)

                    with state_lock:
                        app_state["audio_peak"] = round(cur_peak, 3)
                        app_state["fft_bands"] = list(smooth_bands)
                except Exception:
                    pass
                time.sleep(0.028)
    except Exception:
        pass

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

    def get_telemetry(self):
        with state_lock:
            return {
                "version": app_state["version"],
                "pos": app_state["base_pos"],
                "dur": app_state["duration"],
                "is_playing": app_state["is_playing"],
                "peak": app_state["audio_peak"],
                "fft": app_state["fft_bands"],
                "loop": app_state["is_loop"],
                "shuffle": app_state["is_shuffle"],
                "audio_norm": app_state["audio_norm"],
                "click_through": app_state["click_through"],
                "discord_rpc": app_state["discord_rpc"],
                "discord_connected": app_state["discord_connected"],
                "bpm": app_state["bpm"],
                "musical_key": app_state["musical_key"]
            }

    def get_track_details(self):
        with state_lock:
            details = {
                "version": app_state["version"],
                "title": app_state["current_track"],
                "artist": app_state["current_artist"],
                "track_id": app_state.get("current_track_id", ""),
                "cover": app_state["album_cover"],
                "dominant_color": app_state.get("dominant_color", "#ffffff"),
                "lyrics": app_state["lyrics"],
                "duration": app_state["duration"],
                "is_loop": app_state["is_loop"],
                "bpm": app_state["bpm"],
                "musical_key": app_state["musical_key"]
            }
        with _recent_lock:
            details["recent_songs"] = list(_recent_songs_cache[:8])
        return details

    def get_state(self):
        with state_lock:
            return app_state

    def get_ui_state(self):
        cfg = load_user_config()
        return cfg.get("ui_state", {})

    def save_ui_state(self, ui_state_obj):
        if not isinstance(ui_state_obj, dict):
            return False
        cfg = load_user_config()
        cfg["ui_state"] = ui_state_obj
        hwnd = find_our_hwnd()
        if hwnd and self.current_mode != "mini":
            try:
                x, y, w, h = get_window_rect(hwnd)
                cfg["window_pos"] = {"x": x, "y": y, "w": w, "h": h}
            except Exception:
                pass
        save_user_config(cfg)
        return True

    def toggle_audio_norm(self):
        with state_lock:
            app_state["audio_norm"] = not app_state.get("audio_norm", True)
            val = app_state["audio_norm"]
        return val

    def toggle_audio_normalization(self):
        return self.toggle_audio_norm()

    def toggle_click_through(self, enable=None):
        if enable is None:
            target = not _click_through_active
        else:
            target = bool(enable)
        return set_window_click_through(target)

    def toggle_discord_rpc(self):
        with state_lock:
            app_state["discord_rpc"] = not app_state.get("discord_rpc", True)
            val = app_state["discord_rpc"]
        return val

    def get_recent_songs(self):
        return fetch_recent_songs_list(10)

    def play_track_uri(self, uri_or_id):
        return {"ok": play_spotify_uri(uri_or_id)}

    def play_spotify_uri(self, uri_or_id, title="", artist=""):
        if not uri_or_id and (title or artist):
            tid, _, _ = resolve_exact_spotify_track(artist, title)
            if tid:
                uri_or_id = f"spotify:track:{tid}"
        return {"ok": play_spotify_uri(uri_or_id)}

    def run_ai_dj(self, style_prompt="Surprise Me"):
        return execute_ai_dj_session(style_prompt)

    def trigger_ai_dj(self, style_prompt="Surprise Me"):
        return execute_ai_dj_session(style_prompt)

    def quick_share(self, current_lyric=""):
        with state_lock:
            title = app_state.get("current_track", "") or "Unknown Track"
            artist = app_state.get("current_artist", "") or "Unknown Artist"
        lyric_clean = str(current_lyric or "").strip()
        if lyric_clean:
            share_text = f"\"{lyric_clean}\" - {title} by {artist} (via EZ Lyrics)"
        else:
            share_text = f"Listening to {title} by {artist} (via EZ Lyrics)"
        try:
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            p.communicate(input=share_text.encode("utf-16-le"))
        except Exception:
            pass
        return True

    def start_drag(self):
        def _drag():
            hwnd = find_our_hwnd()
            if hwnd:
                user32.ReleaseCapture()
                user32.SendMessageW(wintypes.HWND(hwnd), 0x0112, 0xF012, 0)
        threading.Thread(target=_drag, daemon=True).start()
        return True

    def move_window(self, dx, dy):
        hwnd = find_our_hwnd()
        if hwnd:
            cur_x, cur_y, cur_w, cur_h = get_window_rect(hwnd)
            nx, ny = cur_x + int(dx), cur_y + int(dy)
            user32.SetWindowPos(wintypes.HWND(hwnd), HWND_TOPMOST, nx, ny, cur_w, cur_h, 0x0010 | 0x0001 | 0x0040)
            return True
        return False

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

    def get_playlists(self):
        pls = discover_user_playlists()
        with state_lock:
            track = app_state.get("current_track", "")
            artist = app_state.get("current_artist", "")
            tid = app_state.get("current_track_id", "")
        track_sig = f"{artist} - {track}".strip(" -").lower()
        cfg = load_user_config()
        saved = cfg.get("saved_playlist_tracks", {})

        # Also check live Liked Songs status via spotify_cli if tid is known
        liked_live = False
        if tid:
            try:
                chk = run_spotify_cli(["library", "contains", f"spotify:track:{tid}", "--format", "json"], timeout=2.0)
                if isinstance(chk, dict):
                    liked_live = bool((chk.get("contains") or {}).get(f"spotify:track:{tid}", False))
            except Exception:
                pass

        result = []
        for p in pls:
            pid = p["id"]
            added_list = [str(x).lower() for x in saved.get(pid, p.get("added_tracks", []))]
            is_in = bool((track_sig and track_sig in added_list) or (tid and tid.lower() in added_list))
            if pid == "liked_songs" and liked_live:
                is_in = True
            result.append({
                "id": pid,
                "name": p["name"],
                "uri": p.get("uri", ""),
                "is_added": is_in
            })
        return result

    def add_to_playlist(self, playlist_id, playlist_name="", custom_track_id=""):
        with state_lock:
            track = app_state.get("current_track", "")
            artist = app_state.get("current_artist", "")
            tid = custom_track_id or app_state.get("current_track_id", "")
        track_sig = f"{artist} - {track}".strip(" -") if not custom_track_id else custom_track_id
        cfg = load_user_config()
        saved = cfg.get("saved_playlist_tracks", {})
        if playlist_id not in saved:
            saved[playlist_id] = []
        if track_sig and track_sig not in saved[playlist_id]:
            saved[playlist_id].append(track_sig)
        if tid and tid not in saved[playlist_id]:
            saved[playlist_id].append(tid)
        cfg["saved_playlist_tracks"] = saved
        save_user_config(cfg)
        with _playlists_lock:
            for p in _cached_playlists:
                if p["id"] == playlist_id:
                    p["added_tracks"] = saved[playlist_id]

        synced_live = execute_real_spotify_playlist_mutation("add", playlist_id, tid)
        return {"ok": True, "synced_live": synced_live, "playlist_id": playlist_id, "track": track_sig}

    def remove_from_playlist(self, playlist_id, playlist_name="", custom_track_id=""):
        with state_lock:
            track = app_state.get("current_track", "")
            artist = app_state.get("current_artist", "")
            tid = custom_track_id or app_state.get("current_track_id", "")
        track_sig = f"{artist} - {track}".strip(" -") if not custom_track_id else custom_track_id
        cfg = load_user_config()
        saved = cfg.get("saved_playlist_tracks", {})
        if playlist_id in saved:
            saved[playlist_id] = [
                x for x in saved[playlist_id]
                if x.lower() not in (track_sig.lower(), (tid or "").lower())
            ]
            cfg["saved_playlist_tracks"] = saved
            save_user_config(cfg)
        with _playlists_lock:
            for p in _cached_playlists:
                if p["id"] == playlist_id:
                    p["added_tracks"] = saved.get(playlist_id, [])

        synced_live = execute_real_spotify_playlist_mutation("remove", playlist_id, tid)
        return {"ok": True, "synced_live": synced_live, "playlist_id": playlist_id, "track": track_sig}

    def set_spicy_api_key(self, key_str):
        cfg = load_user_config()
        cfg["spicy_api_key"] = str(key_str or "").strip()
        save_user_config(cfg)
        with state_lock:
            artist = app_state.get("current_artist", "")
            title = app_state.get("current_track", "")
            dur = app_state.get("duration", 180.0)
        if title:
            threading.Thread(target=load_track_data, args=(artist, title, dur, ""), daemon=True).start()
        return True

    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def close_window(self):
        hwnd = find_our_hwnd()
        if hwnd and self.current_mode != "mini":
            try:
                x, y, w, h = get_window_rect(hwnd)
                cfg = load_user_config()
                cfg["window_pos"] = {"x": x, "y": y, "w": w, "h": h}
                save_user_config(cfg)
            except Exception:
                pass
        if self._window:
            self._window.destroy()
        os._exit(0)

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
                with state_lock:
                    has_lyrics = bool(app_state.get("lyrics") and len(app_state["lyrics"]) > 0)
                mode_target = "expanded" if has_lyrics else "compact"
                self.pending_restore_mode = mode_target
                self.current_mode = mode_target
                tw = 960 if has_lyrics else 380
                th = 580 if has_lyrics else 620
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

# Keep-Topmost & Global Hotkey (Ctrl+Shift+L to exit Click-Through Ghost Mode) Worker Thread
def keep_topmost_worker():
    time.sleep(0.8)
    # Restore saved window position if available
    cfg = load_user_config()
    wpos = cfg.get("window_pos")
    restored_pos = False
    last_hotkey_state = False

    while True:
        try:
            hwnd = find_our_hwnd()
            if hwnd:
                apply_window_icon(hwnd)
                if not restored_pos and isinstance(wpos, dict) and "x" in wpos and "y" in wpos:
                    s_left, s_top, s_right, s_bottom = get_screen_work_area()
                    rx = max(s_left, min(s_right - 200, int(wpos["x"])))
                    ry = max(s_top, min(s_bottom - 120, int(wpos["y"])))
                    user32.SetWindowPos(wintypes.HWND(hwnd), HWND_TOPMOST, rx, ry, 0, 0, 0x0001 | 0x0010 | 0x0040)
                    restored_pos = True
                else:
                    user32.SetWindowPos(wintypes.HWND(hwnd), HWND_TOPMOST, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x0040)

            # Check global hotkey Ctrl+Shift+L (VK_CONTROL=0x11, VK_SHIFT=0x10, 'L'=0x4C) to toggle Click-Through Ghost Mode
            ctrl_down = (user32.GetAsyncKeyState(0x11) & 0x8000) != 0
            shift_down = (user32.GetAsyncKeyState(0x10) & 0x8000) != 0
            l_down = (user32.GetAsyncKeyState(0x4C) & 0x8000) != 0
            combo = ctrl_down and shift_down and l_down
            if combo and not last_hotkey_state:
                set_window_click_through(not _click_through_active)
            last_hotkey_state = combo
        except Exception:
            pass
        time.sleep(0.12)

def memory_trimmer_worker():
    PROCESS_ALL_ACCESS = 0x1F0FFF
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    while True:
        time.sleep(12.0)
        try:
            cur_h = kernel32.GetCurrentProcess()
            psapi.EmptyWorkingSet(cur_h)
            if HAS_PSUTIL:
                try:
                    cur_pid = os.getpid()
                    parent = psutil.Process(cur_pid)
                    for child in parent.children(recursive=True):
                        cname = child.name().lower()
                        if "webview" in cname or "edge" in cname:
                            ch_h = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, child.pid)
                            if ch_h:
                                psapi.EmptyWorkingSet(ch_h)
                                kernel32.CloseHandle(ch_h)
                except Exception:
                    pass
        except Exception:
            pass

def main():
    threading.Thread(target=memory_trimmer_worker, daemon=True).start()
    start_smtc_bridge()
    threading.Thread(target=spotify_monitor_loop, daemon=True).start()
    threading.Thread(target=audio_meter_thread, daemon=True).start()
    threading.Thread(target=discover_user_playlists, daemon=True).start()
    threading.Thread(target=discord_rpc_worker, daemon=True).start()

    info = query_smtc()
    if info and info.get("title"):
        threading.Thread(
            target=load_track_data,
            args=(info.get("artist", ""), info.get("title", ""), float(info.get("dur", 0.0)), info.get("album", "")),
            daemon=True
        ).start()

    html_file = resource_path("index.html")
    with open(html_file, "r", encoding="utf-8") as f:
        html_code = f.read()

    # Inject saved UI state directly into index.html before window creation so custom layout/variations/theme render on Frame 0!
    cfg = load_user_config()
    saved_ui_json = json.dumps(cfg.get("ui_state", {}))
    inject_script = f"<script>window.__INITIAL_UI_STATE__ = {saved_ui_json};</script>\n</head>"
    html_code = html_code.replace("</head>", inject_script, 1)

    bridge = WebBridge()
    window = webview.create_window(
        title="EZ Lyrics",
        html=html_code,
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
