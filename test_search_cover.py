import urllib.parse
import requests

artist = "Skyte"
title = "#opia"
album = "lovekills"
clean_title = title.replace("#", "").strip()

print("--- DEEZER ---")
for q in [f"{artist} {clean_title}", clean_title, f"{artist} {album}", album]:
    r = requests.get(f"https://api.deezer.com/search?q={urllib.parse.quote(q)}")
    data = r.json()
    print("Q:", q, "total:", data.get("total", 0))
    if data.get("data"):
        item = data["data"][0]
        print("  Found:", item.get("title"), "by", item.get("artist", {}).get("name"))
        print("  Cover:", item.get("album", {}).get("cover_xl") or item.get("album", {}).get("cover_big"))

print("--- DEEZER ARTIST SEARCH ---")
r_art = requests.get(f"https://api.deezer.com/search/artist?q={urllib.parse.quote(artist)}")
d_art = r_art.json()
print("Artist total:", d_art.get("total", 0))
if d_art.get("data"):
    for a in d_art["data"][:3]:
        print("  Artist:", a.get("name"), "picture:", a.get("picture_xl"))
