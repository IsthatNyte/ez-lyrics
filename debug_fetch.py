import sys
sys.path.insert(0, r"C:\Users\dryde\spicy_spotify_lyrics")
import app
import urllib.parse
import requests

artist = "Skyte"
title = "#opia"
album = "lovekills"

clean_title = title.replace("#", "").strip()
clean_artist = artist.replace("#", "").strip()

search_queries = [
    f"{clean_artist} {clean_title}",
    f"{artist} {title}".replace("#", "").strip(),
    f"{clean_artist} {album}".strip() if album else "",
    clean_title
]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for q_text in search_queries:
    q = urllib.parse.quote(q_text)
    url = f"https://api.deezer.com/search?q={q}"
    print("Checking Deezer URL:", url)
    r = requests.get(url, headers=headers, timeout=3.5)
    print("Status:", r.status_code)
    data = r.json()
    items = data.get("data", [])
    print("Items found:", len(items))
    for it in items:
        art_name = it.get("artist", {}).get("name", "").lower()
        print("  Item artist:", art_name, "title:", it.get("title"))
        if clean_artist.lower() in art_name or art_name in clean_artist.lower():
            cover = it.get("album", {}).get("cover_xl") or it.get("album", {}).get("cover_big")
            print("  MATCH! Cover:", cover)
            break
