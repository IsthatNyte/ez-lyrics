import re

# 1. Update app.py
app_path = r"C:\Users\dryde\spicy_spotify_lyrics\app.py"
with open(app_path, "r", encoding="utf-8") as f:
    app_text = f.read()

# Add move_window to WebBridge
old_wb = """    def start_drag(self):
        # Native drag executed on background thread prevents freezing the WebBridge callback
        def _drag():
            hwnd = find_our_hwnd()
            if hwnd:
                user32.ReleaseCapture()
                user32.SendMessageW(wintypes.HWND(hwnd), 0x0112, 0xF012, 0)
        threading.Thread(target=_drag, daemon=True).start()
        return True"""

new_wb = """    def start_drag(self):
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
            user32.SetWindowPos(wintypes.HWND(hwnd), HWND_TOPMOST, cur_x + int(dx), cur_y + int(dy), cur_w, cur_h, 0x0010 | 0x0001 | 0x0040)
            return True
        return False"""

if old_wb in app_text:
    app_text = app_text.replace(old_wb, new_wb, 1)

# Fix audio_meter_thread so cur_peak decays naturally and doesn't get stuck at 1.0
old_audio = """                    val = float(_audio_meter.GetPeakValue())
                    if val > 0.001:
                        boosted = min(1.0, (val ** 0.28) * 2.2)
                    else:
                        boosted = 0.0

                    if boosted > cur_peak:
                        cur_peak = boosted
                    else:
                        cur_peak = cur_peak * 0.82 + boosted * 0.18

                    with state_lock:
                        app_state["audio_peak"] = round(cur_peak, 3)"""

new_audio = """                    val = float(_audio_meter.GetPeakValue())
                    target_peak = min(1.0, val * 1.55)
                    if target_peak > cur_peak:
                        cur_peak = target_peak
                    else:
                        cur_peak = cur_peak * 0.76 + target_peak * 0.24

                    with state_lock:
                        app_state["audio_peak"] = round(cur_peak, 3)"""

if old_audio in app_text:
    app_text = app_text.replace(old_audio, new_audio, 1)

# Update fetch_cover_and_artist in app.py to support multiple creators
old_fetch = app_text[app_text.find("# Multi-Source Artwork Fetcher"):app_text.find("# Synced lyrics fetcher")]

new_fetch = """# Multi-Source Artwork & Multi-Creator Metadata Fetcher
def fetch_cover_and_artist(artist, title, album=""):
    clean_title = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title).replace('#', '').strip()
    clean_artist = artist.replace('#', '').strip()

    search_queries = [
        f"{clean_artist} {clean_title}",
        clean_title,
        f"{clean_artist} {album}".strip() if album else "",
        f"{clean_artist}"
    ]

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    full_artist = artist
    best_cover_url = ""

    for q_text in search_queries:
        if not q_text.strip():
            continue
        try:
            q = urllib.parse.quote(q_text)
            r = requests.get(f"https://api.deezer.com/search?q={q}", headers=headers, timeout=3.5)
            if r.status_code == 200:
                items = r.json().get("data", [])
                if items:
                    for item in items[:6]:
                        track_id = item.get("id")
                        curr_cover = item.get("album", {}).get("cover_xl") or item.get("album", {}).get("cover_big")
                        if not best_cover_url and curr_cover:
                            best_cover_url = curr_cover

                        if track_id:
                            try:
                                r2 = requests.get(f"https://api.deezer.com/track/{track_id}", headers=headers, timeout=3.0)
                                if r2.status_code == 200:
                                    contribs = r2.json().get("contributors", [])
                                    if len(contribs) > 1:
                                        names = [c.get("name").strip() for c in contribs if c.get("name")]
                                        if names:
                                            full_artist = ", ".join(names)
                                            if curr_cover:
                                                best_cover_url = curr_cover
                                            break
                            except Exception:
                                pass

                        raw_title = item.get("title", "")
                        m = re.search(r'[\(\[](?:feat\.|featuring|with)\s+([^\)\]]+)[\)\]]', raw_title, re.IGNORECASE)
                        if m and full_artist == artist:
                            full_artist = f"{artist}, {m.group(1).strip()}"
                            if curr_cover:
                                best_cover_url = curr_cover
                            break

                    if full_artist != artist:
                        break
        except Exception:
            pass

    # iTunes fallback for cover
    if not best_cover_url:
        for q_text in search_queries[:3]:
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
                            best_cover_url = raw_art.replace("100x100bb", "1000x1000bb")
                            break
                    if best_cover_url:
                        break
            except Exception:
                pass

    cover_b64 = ""
    if best_cover_url:
        try:
            img_resp = requests.get(best_cover_url, headers=headers, timeout=3.5)
            if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                cover_b64 = "data:image/jpeg;base64," + base64.b64encode(img_resp.content).decode("ascii")
        except Exception:
            pass

    # Normalize casing of original artist in full_artist
    try:
        full_artist = re.sub(re.escape(artist), artist, full_artist, flags=re.IGNORECASE)
    except Exception:
        pass

    return cover_b64, full_artist

"""

if old_fetch:
    app_text = app_text.replace(old_fetch, new_fetch, 1)

# Update load_track_data in app.py
old_load = """def load_track_data(artist, title, duration, album=""):
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
        pass"""

new_load = """def load_track_data(artist, title, duration, album=""):
    global current_loading_track
    track_key = f"{artist} - {title}"
    current_loading_track = track_key

    try:
        cover_b64, full_artist = fetch_cover_and_artist(artist, title, album)
        lyrics = fetch_synced_lyrics(artist, title, duration)

        if current_loading_track == track_key:
            with state_lock:
                app_state["album_cover"] = cover_b64
                if full_artist:
                    app_state["current_artist"] = full_artist
                app_state["lyrics"] = lyrics
                app_state["version"] += 1
    except Exception:
        pass"""

if old_load in app_text:
    app_text = app_text.replace(old_load, new_load, 1)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_text)

print("SUCCESS: app.py updated!")
