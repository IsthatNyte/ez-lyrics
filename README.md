# EZ Lyrics

> Floating LiquidGL real-time synchronized lyrics HUD and companion overlay for Spotify Desktop.

EZ Lyrics is an ultra-low resource floating companion overlay for Spotify. It tracks Spotify's live playback state via Windows System Media Transport Controls (SMTC) and local process bridges, rendering millisecond-accurate synchronized lyrics in a customizable frosted-glass LiquidGL interface.

---

## Key Features

- **Spotify Companion Overlay**: Seamlessly syncs with your desktop Spotify client without requiring premium developer API tokens.
- **Real-Time Synced Lyrics**: Precision line-by-line scrolling lyrics powered by multi-provider scrapers (LRCLIB, NetEase, Musixmatch).
- **Phonetic & Romanization Sub-Lines**: Instant phonetic Romanization sub-lines for Japanese (Romaji), Korean, and other languages.
- **8-Band Audio Spectrum FFT**: Built-in audio spectrum visualizer reacting dynamically to audio output.
- **LiquidGL Glassmorphism Interface**: Real-time album artwork color tinting, draggable floating window, customizable typography, and size grips.
- **Ghost Click-Through Mode**: Press `Ctrl+Shift+L` to lock the overlay on screen and click right through it into your underlying game or workspace.
- **Discord Rich Presence**: Native IPC status broadcasting the song you are currently listening to on Discord.

---

## How It Works

1. **Media State Tracking**: EZ Lyrics connects to Windows 10/11 SMTC (System Media Transport Controls) and the local Spotify Desktop process to detect playback events, track title, artist, and timeline position with sub-second latency.
2. **Scraping & Lyric Matching**: The engine queries lyric providers using cleaned metadata and fuzzy string matching to deliver accurate LRC timestamped lines.
3. **Hardware Acceleration**: Built with Python and `pywebview`, the UI renders with the native Microsoft Edge WebView2 runtime for smooth 60fps animations at minimal CPU and RAM usage.
4. **Win32 Window Management**: Win32 user32 APIs control window transparency, topmost layering, and click-through window styles (`WS_EX_TRANSPARENT`).

---

## Frequently Asked Questions (FAQ)

### Does original EZ Lyrics require the Spotify desktop app?
Yes. Original EZ Lyrics acts as a lightweight HUD overlay for Spotify Desktop. If you want a standalone player that does not require Spotify at all, check out [EZ Lyrics Player](https://github.com/IsthatNyte/ez-lyrics-player).

### Does this require a Spotify Premium account?
No. EZ Lyrics reads track metadata through the local Windows Media session, working with both Free and Premium Spotify accounts.

### How do I enable Ghost (Click-Through) Mode?
Press `Ctrl+Shift+L` or click the Ghost Mode icon in the settings menu. When enabled, your mouse clicks pass through the lyrics overlay directly to the windows behind it.

### How do I customize colors and typography?
Click the Settings gear icon on the overlay to open the Theme Studio, where you can select accent colors, font styles, blur strength, and layout presets.

---

## Installation & Running from Source

### Prerequisites
- Windows 10 or Windows 11
- Spotify Desktop app
- Python 3.10+ (if running from source)

### Run from Source
```bash
git clone https://github.com/IsthatNyte/ez-lyrics.git
cd ez-lyrics
pip install -r requirements.txt
python app.py
```

### Pre-Built Executable
Download the standalone `EZ Lyrics.exe` from the Releases tab and run it alongside Spotify Desktop.
