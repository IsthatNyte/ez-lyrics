import sys
sys.path.insert(0, r"C:\Users\dryde\spicy_spotify_lyrics")
import app
import traceback

try:
    res = app.fetch_highres_cover("Skyte", "#opia", "lovekills")
    print("Result len:", len(res))
except Exception as e:
    traceback.print_exc()
