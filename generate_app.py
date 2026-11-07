import os

with open(r"C:\Users\dryde\spicy_spotify_lyrics\logo_b64.txt", "r") as f:
    logo_base64 = f.read().strip()

template = '''"""
EZ Lyrics LiquidGL Player
White custom EZ logo, true LiquidGL glass capsule, 5-button controls with warping play/pause,
wave visualizer, accurate elapsed SMTC real-time sync, and corner drag resize.
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
import requests
from PIL import Image
import webview

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
    "is_shuffle": False
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

    $sess = Get-SpotifySession
    if ($sess) {
        $timeline = $sess.GetTimelineProperties()
        $playback = $sess.GetPlaybackInfo()
        $props = Await-Async ($sess.TryGetMediaPropertiesAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
        $t = if ($props -and $props.Title) { $props.Title.Replace('"', '\"') } else { "" }
        $a = if ($props -and $props.Artist) { $props.Artist.Replace('"', '\"') } else { "" }
        $pos = if ($timeline) { [double]($timeline.Position.TotalSeconds) } else { 0.0 }
        $dur = if ($timeline) { [double]($timeline.EndTime.TotalSeconds) } else { 0.0 }
        $st = if ($playback) { $playback.PlaybackStatus.ToString() } else { "Closed" }

        # Add exact elapsed time since LastUpdatedTime for true real-time accuracy
        if ($st -eq "Playing" -and $timeline -and $timeline.LastUpdatedTime) {
            $elapsed = ([DateTimeOffset]::UtcNow - $timeline.LastUpdatedTime).TotalSeconds
            if ($elapsed -gt 0 -and $elapsed -lt 7200) {
                $pos = $pos + $elapsed
            }
        }
        $pos = [Math]::Round($pos, 2)
        $dur = [Math]::Round($dur, 2)

        Write-Host ('{"title":"' + $t + '","artist":"' + $a + '","pos":' + $pos + ',"dur":' + $dur + ',"status":"' + $st + '"}')
    } else {
        Write-Host "{}"
    }
}
"""

bridge_process = None
bridge_lock = threading.Lock()


def start_smtc_bridge():
    global bridge_process
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bridge.ps1")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(PS_BRIDGE_SCRIPT)

    bridge_process = subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        bufsize=1
    )


def query_smtc():
    global bridge_process
    if not bridge_process or bridge_process.poll() is not None:
        start_smtc_bridge()

    with bridge_lock:
        try:
            bridge_process.stdin.write("GET\\n")
            bridge_process.stdin.flush()
            line = bridge_process.stdout.readline()
            if line:
                return json.loads(line.strip())
        except Exception:
            pass
    return None


def smtc_send(cmd_str):
    global bridge_process
    if bridge_process and bridge_process.poll() is None:
        with bridge_lock:
            try:
                bridge_process.stdin.write(f"{cmd_str}\\n")
                bridge_process.stdin.flush()
                bridge_process.stdout.readline()
            except Exception:
                pass


def clean_track_name(name):
    t = re.sub(r"\\(feat\\.[^\\)]+\\)", "", name, flags=re.I)
    t = re.sub(r"\\[feat\\.[^\\]]+\\]", "", t, flags=re.I)
    t = re.sub(r"- .*Remaster.*", "", t, flags=re.I)
    t = re.sub(r"\\(.*Remaster.*\\)", "", t, flags=re.I)
    t = re.sub(r"- Single", "", t, flags=re.I)
    return t.strip()


def fetch_cover_art(artist, track):
    clean = clean_track_name(track)
    queries = [f"{artist} {track}", f"{artist} {clean}", clean]
    for q in queries:
        try:
            url = f"https://itunes.apple.com/search?term={urllib.parse.quote(q)}&entity=song&limit=1"
            res = requests.get(url, timeout=3).json()
            if res.get("results"):
                item = res["results"][0]
                art = item.get("artworkUrl100", "").replace("100x100bb", "600x600bb")
                dur = item.get("trackTimeMillis", 0) / 1000.0
                return art, dur
        except Exception:
            pass

    for q in queries:
        try:
            url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}&limit=1"
            res = requests.get(url, timeout=3).json()
            if res.get("data"):
                item = res["data"][0]
                art = item.get("album", {}).get("cover_xl", "")
                dur = float(item.get("duration", 0))
                return art, dur
        except Exception:
            pass

    return "", 0.0


def parse_synced_lyrics(lrc_text):
    lines = []
    for raw_line in lrc_text.splitlines():
        tags = re.findall(r"\\[(\\d+):(\\d+(?:\\.\\d+)?)\\]", raw_line)
        if tags:
            pure_text = re.sub(r"\\[\\d+:\\d+(?:\\.\\d+)?\\]", "", raw_line)
            pure_text = re.sub(r"<[^>]+>", "", pure_text).strip()
            display_text = pure_text if pure_text else "♪"
            for m, s in tags:
                t = round(int(m) * 60 + float(s), 2)
                lines.append({"time": t, "text": display_text})

    lines.sort(key=lambda x: x["time"])
    unique_lines = []
    last_t = -1
    for l in lines:
        if abs(l["time"] - last_t) > 0.05 or not unique_lines:
            unique_lines.append(l)
            last_t = l["time"]
        else:
            unique_lines[-1]["text"] += " " + l["text"]
    return unique_lines


def fetch_lyrics(artist, track):
    clean = clean_track_name(track)
    headers = {"User-Agent": "EZLyrics/8.0"}

    # 1. Exact match
    for q in [
        {"artist_name": artist, "track_name": track},
        {"artist_name": artist, "track_name": clean}
    ]:
        try:
            r = requests.get("https://lrclib.net/api/get", params=q, headers=headers, timeout=3)
            if r.ok:
                data = r.json()
                if data.get("syncedLyrics"):
                    return parse_synced_lyrics(data["syncedLyrics"])
        except Exception:
            pass

    # 2. Search match
    for term in [f"{artist} {track}", f"{artist} {clean}", clean]:
        try:
            r = requests.get("https://lrclib.net/api/search", params={"q": term}, headers=headers, timeout=3)
            if r.ok:
                results = r.json()
                for item in results:
                    if item.get("syncedLyrics"):
                        return parse_synced_lyrics(item["syncedLyrics"])
                if results and results[0].get("plainLyrics"):
                    plain = results[0]["plainLyrics"]
                    return [{"time": i * 4.0, "text": l} for i, l in enumerate(plain.splitlines()) if l.strip()]
        except Exception:
            pass

    return []


# Background Loader Thread
current_loading_key = ""

def load_track_data(artist, track, reported_dur=0.0):
    global current_loading_key
    load_key = f"{artist}::{track}"
    current_loading_key = load_key

    cover_url, itunes_dur = fetch_cover_art(artist, track)
    lyrics = fetch_lyrics(artist, track)

    with state_lock:
        if current_loading_key == load_key:
            app_state["current_track"] = track
            app_state["current_artist"] = artist
            app_state["album_cover"] = cover_url
            app_state["lyrics"] = lyrics
            app_state["duration"] = reported_dur if reported_dur > 0 else (itunes_dur if itunes_dur > 0 else 180.0)
            app_state["version"] += 1


def spotify_monitor_loop():
    last_track_key = ""
    last_stable_playing = False
    status_debounce = 0

    while True:
        time.sleep(0.10)
        info = query_smtc()
        if info and info.get("title"):
            t = info.get("title", "").strip()
            a = info.get("artist", "").strip()
            pos = float(info.get("pos", 0.0))
            dur = float(info.get("dur", 0.0))
            status = info.get("status", "")
            raw_playing = (status == "Playing")

            if raw_playing != last_stable_playing:
                status_debounce += 1
                if status_debounce >= 2:
                    last_stable_playing = raw_playing
                    status_debounce = 0
            else:
                status_debounce = 0

            track_key = f"{a} - {t}"
            if track_key != last_track_key and t != "":
                last_track_key = track_key
                threading.Thread(target=load_track_data, args=(a, t, dur), daemon=True).start()

            with state_lock:
                app_state["base_pos"] = pos
                app_state["base_time"] = time.time()
                if dur > 0:
                    app_state["duration"] = dur
                app_state["is_playing"] = last_stable_playing
        else:
            with state_lock:
                app_state["is_playing"] = False


class WebBridge:
    def __init__(self, win_ref=None):
        self._window = win_ref

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

    def resize_window(self, w, h):
        if self._window:
            self._window.resize(int(w), int(h))

    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def close_window(self):
        if self._window:
            self._window.destroy()


HTML_BODY = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>EZ Lyrics</title>
<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
    -webkit-user-select: none;
    -webkit-app-region: no-drag !important;
  }

  html, body {
    width: 100vw;
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #08080c;
    color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  }

  /* Full Window Album Cover Background with Light Vibrancy & Moderate Blur */
  .bg-viewport {
    position: fixed;
    inset: -15%;
    width: 130%;
    height: 130%;
    overflow: hidden;
    z-index: 0;
    pointer-events: none;
  }

  .bg-layer {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: blur(28px) brightness(0.80) saturate(135%);
    opacity: 0;
    transition: opacity 1.0s ease-in-out;
    transform: scale(1.06);
  }

  .bg-layer.active {
    opacity: 1;
  }

  .vignette {
    position: fixed;
    inset: 0;
    background: radial-gradient(circle at center, rgba(6, 6, 10, 0.1) 0%, rgba(3, 3, 5, 0.45) 100%);
    z-index: 1;
    pointer-events: none;
  }

  /* Flush Custom Titlebar Without Any Artifacts Sticking Out */
  .custom-titlebar {
    position: relative;
    z-index: 10;
    width: 100vw;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    background: rgba(12, 14, 22, 0.45);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
  }

  .drag-zone {
    flex: 1;
    height: 100%;
    display: flex;
    align-items: center;
    cursor: grab;
    -webkit-app-region: drag !important;
  }

  /* White EZ. lyrics. Logo */
  .app-logo {
    height: 24px;
    width: auto;
    object-fit: contain;
    pointer-events: none;
    filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.5));
  }

  .win-controls {
    display: flex;
    align-items: center;
    gap: 6px;
    -webkit-app-region: no-drag !important;
  }

  .win-btn {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.12);
    color: rgba(255, 255, 255, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.2s ease;
    -webkit-app-region: no-drag !important;
  }

  .win-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    color: #fff;
  }

  .win-btn.close:hover {
    background: #e11d48;
    color: #fff;
  }

  /* Main Container with Absolute Layout to Prevent Window Scrolling */
  .main-layout {
    position: relative;
    z-index: 2;
    width: 100vw;
    height: calc(100vh - 40px);
    overflow: hidden;
  }

  /* Fixed Left Column */
  .left-side {
    position: absolute;
    left: 36px;
    top: 24px;
    bottom: 24px;
    width: 280px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    pointer-events: auto;
    z-index: 5;
  }

  .album-card {
    width: 280px;
    height: 280px;
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    background: rgba(255, 255, 255, 0.05);
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.14);
    margin-bottom: 12px;
    flex-shrink: 0;
  }

  .album-img-layer {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0;
    transition: opacity 0.8s ease-in-out;
  }

  .album-img-layer.active {
    opacity: 1;
  }

  .meta-title {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.4px;
    line-height: 1.25;
    margin-bottom: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  }

  .meta-artist {
    font-size: 15px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.8);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 12px;
    text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4);
  }

  /* Authentic LiquidGL Glass Capsule */
  .liquidgl-capsule {
    position: relative;
    border-radius: 22px;
    padding: 14px 18px 16px 18px;
    background: rgba(255, 255, 255, 0.10);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    box-shadow: inset 0 0 0 1.5px rgba(255, 255, 255, 0.35),
                inset 0 2px 5px rgba(255, 255, 255, 0.5),
                inset 0 -2px 5px rgba(0, 0, 0, 0.25),
                0 16px 36px rgba(0, 0, 0, 0.4);
  }

  /* Waveform Visualizer Timebar */
  .vocalizer-container {
    width: 100%;
    height: 32px;
    position: relative;
    cursor: pointer;
    margin-bottom: 4px;
  }

  #waveCanvas {
    width: 100%;
    height: 100%;
    display: block;
  }

  .time-row {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.75);
    margin-bottom: 10px;
  }

  /* 5-Button Control Row */
  .controls-row-5 {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4px;
  }

  .capsule-btn {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.75);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px;
    transition: transform 0.18s ease, color 0.18s ease;
  }

  .capsule-btn:hover {
    color: #ffffff;
    transform: scale(1.15);
  }

  .capsule-btn.active-mode {
    color: #1ed760;
  }

  /* True Morphing / Warping Play/Stop Button */
  .morph-btn {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: #ffffff;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35),
                inset 0 2px 3px rgba(255, 255, 255, 0.9),
                inset 0 -2px 3px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  }

  .morph-btn:hover {
    transform: scale(1.08);
  }

  .morph-btn:active {
    transform: scale(0.96);
  }

  .morph-icon-layer {
    position: absolute;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.26s cubic-bezier(0.4, 0, 0.2, 1),
                transform 0.26s cubic-bezier(0.4, 0, 0.2, 1);
    color: #0b0f19;
  }

  .morph-play-icon {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }

  .morph-pause-icon {
    opacity: 0;
    transform: scale(0.4) rotate(-90deg);
  }

  .morph-btn.playing .morph-play-icon {
    opacity: 0;
    transform: scale(0.4) rotate(90deg);
  }

  .morph-btn.playing .morph-pause-icon {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }

  /* Isolated Right Column: Spicy Lyrics Stream */
  .lyrics-viewport {
    position: absolute;
    left: 350px;
    right: 36px;
    top: 0;
    bottom: 0;
    overflow: hidden;
    mask-image: linear-gradient(to bottom, transparent 0%, black 14%, black 86%, transparent 100%);
    -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 14%, black 86%, transparent 100%);
  }

  .lyrics-box {
    width: 100%;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 38vh 16px 38vh 16px;
    scrollbar-width: none;
  }

  .lyrics-box::-webkit-scrollbar {
    display: none;
  }

  .lyric-line {
    font-size: 30px;
    font-weight: 700;
    line-height: 1.45;
    letter-spacing: -0.5px;
    padding: 12px 16px;
    border-radius: 16px;
    cursor: pointer;
    color: rgba(255, 255, 255, 0.35);
    filter: blur(0.6px);
    transform-origin: left center;
    transform: scale(0.98);
    transition: color 0.35s ease, opacity 0.35s ease, transform 0.35s ease, filter 0.35s ease;
  }

  .lyric-line:hover {
    color: rgba(255, 255, 255, 0.75);
    filter: blur(0px);
  }

  .lyric-line.active {
    color: #ffffff;
    font-weight: 800;
    transform: scale(1.04);
    filter: blur(0px);
    opacity: 1;
    text-shadow: 0 0 28px rgba(255, 255, 255, 0.5);
  }

  .lyric-line.passed {
    color: rgba(255, 255, 255, 0.24);
    filter: blur(0.8px);
    transform: scale(0.97);
  }

  /* Interactive Resize Grip in Bottom-Right Corner */
  .resize-grip {
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
  }

  @media (max-width: 780px) {
    .left-side {
      width: 220px;
      left: 20px;
    }
    .lyrics-viewport {
      left: 260px;
      right: 20px;
    }
    .album-card {
      width: 220px;
      height: 220px;
    }
    .lyric-line {
      font-size: 24px;
      padding: 10px 12px;
    }
  }
</style>
</head>
<body>

  <!-- Full Window Crossfade Background Layers -->
  <div class="bg-viewport">
    <img id="bgA" class="bg-layer active" alt="Background" />
    <img id="bgB" class="bg-layer" alt="Background" />
  </div>

  <div class="vignette"></div>

  <!-- Flush Custom Titlebar -->
  <div class="custom-titlebar">
    <div class="drag-zone pywebview-drag-region">
      <!-- White EZ. lyrics. User Logo -->
      <img src="data:image/png;base64,__LOGO_BASE64__" class="app-logo" alt="EZ. lyrics." />
    </div>
    <div class="win-controls">
      <button class="win-btn" id="btnMin" title="Minimize">
        <svg width="10" height="2" viewBox="0 0 10 2" fill="currentColor"><rect width="10" height="2" rx="1"/></svg>
      </button>
      <button class="win-btn close" id="btnClose" title="Close">
        <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
          <path d="M1 1L9 9M9 1L1 9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </div>

  <!-- Main Layout -->
  <div class="main-layout">
    
    <!-- Left Column: Album Artwork & LiquidGL Capsule with Wave Visualizer -->
    <div class="left-side">
      <div>
        <div class="album-card">
          <img id="coverA" class="album-img-layer active" alt="Cover" />
          <img id="coverB" class="album-img-layer" alt="Cover" />
        </div>
        <div class="meta-title" id="trackTitle">Spotify</div>
        <div class="meta-artist" id="trackArtist">Playing music</div>
      </div>

      <!-- LiquidGL Glass Capsule with Wave Visualizer & 5 Control Buttons -->
      <div class="liquidgl-capsule">
        <div class="vocalizer-container" id="vocalizerBox">
          <canvas id="waveCanvas" width="244" height="32"></canvas>
        </div>

        <div class="time-row">
          <span id="txtCur">0:00</span>
          <span id="txtDur">0:00</span>
        </div>

        <!-- 5 Control Buttons: Loop, Prev, Morphing Play/Stop, Next, Shuffle -->
        <div class="controls-row-5">
          <!-- 1. Loop / Repeat -->
          <button class="capsule-btn" id="btnLoop" title="Repeat">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 2l4 4-4 4"/>
              <path d="M3 11v-1a4 4 0 0 1 4-4h14"/>
              <path d="M7 22l-4-4 4-4"/>
              <path d="M21 13v1a4 4 0 0 1-4 4H3"/>
            </svg>
          </button>

          <!-- 2. Previous Track -->
          <button class="capsule-btn" id="btnPrev" title="Previous">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 5a1 1 0 0 1 1 1v12a1 1 0 1 1-2 0V6a1 1 0 0 1 1-1zm12.2 1.4a1 1 0 0 0-1.5-.86l-9 6a1 1 0 0 0 0 1.72l9 6a1 1 0 0 0 1.5-.86V6.4z"/>
            </svg>
          </button>

          <!-- 3. Morphing Warping Play/Stop Button -->
          <button class="morph-btn" id="btnMorphPlay" title="Play/Pause">
            <div class="morph-icon-layer morph-play-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 4.5C6.4 4.1 5.5 4.6 5.5 5.3v13.4c0 .8.9 1.2 1.5.8l11.5-6.7c.6-.4.6-1.3 0-1.7L7 4.5z"/>
              </svg>
            </div>
            <div class="morph-icon-layer morph-pause-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <rect x="5.5" y="4" width="4.5" height="16" rx="2.25"/>
                <rect x="14" y="4" width="4.5" height="16" rx="2.25"/>
              </svg>
            </div>
          </button>

          <!-- 4. Next Track -->
          <button class="capsule-btn" id="btnNext" title="Next">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 5a1 1 0 0 1 1 1v12a1 1 0 1 1-2 0V6a1 1 0 0 1 1-1zM5.8 6.4A1 1 0 0 1 7.3 5.54l9 6a1 1 0 0 1 0 1.72l-9 6A1 1 0 0 1 5.8 17.6V6.4z"/>
            </svg>
          </button>

          <!-- 5. Shuffle -->
          <button class="capsule-btn" id="btnShuffle" title="Shuffle">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
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

    <!-- Isolated Right Column: Spicy Lyrics Stream -->
    <div class="lyrics-viewport">
      <div class="lyrics-box" id="lyricsBox"></div>
    </div>

  </div>

  <!-- Interactive Drag-to-Resize Corner Grip -->
  <div class="resize-grip" id="resizeGrip" title="Drag corner to resize"></div>

<script>
  let state = {
    version: 0,
    current_track: "",
    current_artist: "",
    album_cover: "",
    lyrics: [],
    duration: 180,
    base_pos: 0,
    base_time: performance.now() / 1000,
    is_playing: false,
    is_loop: false,
    is_shuffle: false
  };

  let localPos = 0.0;
  let lastTimestamp = performance.now();
  let activeIndex = -1;
  let userScrolling = false;
  let scrollTimer = null;
  let activeLayer = 'A';

  function fmt(s) {
    if (isNaN(s) || s < 0) s = 0;
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec < 10 ? '0' : ''}${sec}`;
  }

  // Crossfade Artwork across full background and album card
  function crossfadeArtwork(newUrl) {
    if (!newUrl) return;
    const nextLayer = activeLayer === 'A' ? 'B' : 'A';
    const nextBg = document.getElementById('bg' + nextLayer);
    const curBg = document.getElementById('bg' + activeLayer);
    const nextCover = document.getElementById('cover' + nextLayer);
    const curCover = document.getElementById('cover' + activeLayer);

    const loader = new Image();
    loader.onload = () => {
      nextBg.src = newUrl;
      nextCover.src = newUrl;
      nextBg.classList.add('active');
      nextCover.classList.add('active');
      curBg.classList.remove('active');
      curCover.classList.remove('active');
      activeLayer = nextLayer;
    };
    loader.src = newUrl;
  }

  // Render Spicy Lyrics Lines
  function renderLyrics(lines) {
    const box = document.getElementById('lyricsBox');
    box.innerHTML = '';
    if (!lines || lines.length === 0) {
      activeIndex = -1;
      return;
    }

    lines.forEach((l, idx) => {
      const div = document.createElement('div');
      div.className = 'lyric-line';
      div.textContent = l.text;
      div.dataset.time = l.time;
      div.dataset.idx = idx;

      div.addEventListener('click', () => {
        const t = parseFloat(l.time);
        state.base_pos = t;
        state.base_time = performance.now() / 1000;
        localPos = t;
        activeIndex = idx;
        if (window.pywebview && window.pywebview.api) {
          window.pywebview.api.seek(t);
        }
      });

      box.appendChild(div);
    });
    activeIndex = -1;
  }

  // Monotonic Real-Time Lyrics Sync (Zero Flutter, Pure Container Scroll)
  function updateLyricsSync(curTime) {
    if (!state.lyrics || state.lyrics.length === 0) return;

    let targetIdx = -1;
    for (let i = 0; i < state.lyrics.length; i++) {
      if (state.lyrics[i].time <= curTime) {
        targetIdx = i;
      } else {
        break;
      }
    }

    if (targetIdx !== activeIndex) {
      activeIndex = targetIdx;

      const lines = document.querySelectorAll('.lyric-line');
      lines.forEach((line, idx) => {
        if (idx === activeIndex) {
          line.classList.add('active');
          line.classList.remove('passed');
        } else if (idx < activeIndex) {
          line.classList.remove('active');
          line.classList.add('passed');
        } else {
          line.classList.remove('active', 'passed');
        }
      });

      // Direct container scroll: NEVER scrolls window or left panel!
      if (activeIndex >= 0 && !userScrolling) {
        const activeElem = lines[activeIndex];
        const box = document.getElementById('lyricsBox');
        if (activeElem && box) {
          const targetY = activeElem.offsetTop - (box.clientHeight / 2) + (activeElem.clientHeight / 2);
          box.scrollTo({ top: targetY, behavior: 'smooth' });
        }
      }
    }
  }

  // Wave Visualizer Timebar Canvas
  const canvas = document.getElementById('waveCanvas');
  const ctx = canvas.getContext('2d');
  let waveTick = 0;

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
    }
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  function drawWave() {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    if (w <= 0 || h <= 0) return;

    const midY = h / 2;
    const numBars = 38;
    const barWidth = 3.5 * window.devicePixelRatio;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const progressRatio = state.duration > 0 ? (localPos / state.duration) : 0;

    waveTick += state.is_playing ? 0.08 : 0.01;

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const waveEnvelope = 1.0 - (centerDist * 0.55);

      let amp = 0.16;
      if (state.is_playing) {
        amp = (Math.sin(waveTick * 2.2 + (1.0 - centerDist) * 4.5) * 0.5 + 0.5) *
              (Math.cos(waveTick * 1.5 - centerDist * 3.0) * 0.4 + 0.6) * waveEnvelope;
      }
      const barHeight = Math.max(3 * window.devicePixelRatio, amp * (h - 8));

      const barProgress = (x + barWidth / 2) / w;
      if (barProgress <= progressRatio) {
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
        ctx.shadowBlur = 6;
      } else {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
        ctx.shadowBlur = 0;
      }

      ctx.beginPath();
      ctx.roundRect(x, midY - barHeight / 2, barWidth, barHeight, 2);
      ctx.fill();
    }
  }

  // Wave Visualizer Click Seeking
  document.getElementById('vocalizerBox').addEventListener('click', (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const target = ratio * state.duration;
    state.base_pos = target;
    state.base_time = performance.now() / 1000;
    localPos = target;
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.seek(target);
    }
  });

  // Controls Handlers
  document.getElementById('btnMorphPlay').addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.toggle_play();
  });
  document.getElementById('btnPrev').addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.prev_track();
  });
  document.getElementById('btnNext').addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.next_track();
  });
  document.getElementById('btnLoop').addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_loop().then(val => {
        document.getElementById('btnLoop').classList.toggle('active-mode', val);
      });
    }
  });
  document.getElementById('btnShuffle').addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_shuffle().then(val => {
        document.getElementById('btnShuffle').classList.toggle('active-mode', val);
      });
    }
  });
  document.getElementById('btnMin').addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.minimize_window();
  });
  document.getElementById('btnClose').addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.close_window();
  });

  // User scrolling detection
  const box = document.getElementById('lyricsBox');
  box.addEventListener('wheel', () => {
    userScrolling = true;
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => { userScrolling = false; }, 2200);
  });

  // Interactive Drag-to-Resize Corner Grip Handler
  let isResizing = false;
  let startX = 0, startY = 0, startW = 0, startH = 0;
  const grip = document.getElementById('resizeGrip');

  grip.addEventListener('mousedown', (e) => {
    e.preventDefault();
    isResizing = true;
    startX = e.screenX;
    startY = e.screenY;
    startW = window.innerWidth;
    startH = window.innerHeight;

    const onMouseMove = (ev) => {
      if (!isResizing) return;
      const deltaX = ev.screenX - startX;
      const deltaY = ev.screenY - startY;
      const newW = Math.max(620, startW + deltaX);
      const newH = Math.max(420, startH + deltaY);
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.resize_window(newW, newH);
      }
    };

    const onMouseUp = () => {
      isResizing = false;
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  });

  // 60FPS UI Animation Loop with Monotonic Clock
  function tick(timestamp) {
    const nowSec = timestamp / 1000.0;

    // Monotonic Real-Time Calculation: Advances Steady, No Drift
    if (state.is_playing && state.duration > 0) {
      const elapsed = nowSec - state.base_time;
      localPos = Math.max(0, Math.min(state.duration, state.base_pos + elapsed));
    } else {
      localPos = state.base_pos;
    }

    document.getElementById('txtCur').textContent = fmt(localPos);
    document.getElementById('txtDur').textContent = fmt(state.duration);

    // True SVG Morphing Play/Stop Button State
    const morphBtn = document.getElementById('btnMorphPlay');
    morphBtn.classList.toggle('playing', state.is_playing);

    drawWave();
    updateLyricsSync(localPos);

    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  // Poll Spotify SMTC Bridge for Real-Time Sync
  function pollBridge() {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.get_state().then(s => {
        if (!s) return;

        state.is_playing = s.is_playing;
        state.duration = s.duration || 180;

        // If Spotify reported position differs from calculated position by > 0.6s, align
        const currentCalculated = state.base_pos + (s.is_playing ? (performance.now() / 1000 - state.base_time) : 0);
        if (Math.abs(currentCalculated - s.base_pos) > 0.6) {
          state.base_pos = s.base_pos;
          state.base_time = performance.now() / 1000;
        }

        if (s.version !== state.version) {
          state.version = s.version;
          state.current_track = s.current_track;
          state.current_artist = s.current_artist;
          state.album_cover = s.album_cover;
          state.lyrics = s.lyrics;

          document.getElementById('trackTitle').textContent = state.current_track || 'Spotify';
          document.getElementById('trackArtist').textContent = state.current_artist || 'Playing music';

          crossfadeArtwork(state.album_cover);
          renderLyrics(state.lyrics);
        }
      }).catch(err => {});
    }
  }

  setInterval(pollBridge, 100);
</script>
</body>
</html>
"""

final_code = template.replace("__LOGO_BASE64__", logo_base64)
with open(r"C:\Users\dryde\spicy_spotify_lyrics\app.py", "w", encoding="utf-8") as out:
    out.write(final_code)

print("Generated app.py with embedded white user logo successfully.")
