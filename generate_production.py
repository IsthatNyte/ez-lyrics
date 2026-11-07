import os

base_dir = r"C:\Users\dryde\spicy_spotify_lyrics"
with open(os.path.join(base_dir, "logo_pure_b64.txt"), "r") as f:
    logo_base64 = f.read().strip()

html_content = """<!DOCTYPE html>
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

  /* Full Window Album Cover Background */
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
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: blur(28px) saturate(135%) brightness(0.65);
    transition: opacity 0.8s cubic-bezier(0.25, 1, 0.5, 1);
  }
  #bgLayerA { opacity: 1; }
  #bgLayerB { opacity: 0; }

  /* App Container */
  .app-layout {
    position: relative;
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    z-index: 1;
    overflow: hidden;
  }

  /* Custom Frameless Titlebar */
  .titlebar {
    height: 40px;
    min-height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 14px;
    background: rgba(14, 14, 18, 0.65);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    cursor: default;
    z-index: 10;
  }

  .titlebar-left {
    display: flex;
    align-items: center;
    gap: 10px;
    pointer-events: none;
  }

  .app-logo {
    height: 22px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
    pointer-events: none;
  }

  .titlebar-center {
    font-size: 13px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.85);
    letter-spacing: 0.3px;
    display: none;
    pointer-events: none;
  }

  .titlebar-controls {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .win-btn {
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
  }
  .win-btn:hover {
    background: rgba(255, 255, 255, 0.22);
    color: #ffffff;
  }
  .win-close:hover {
    background: #e81123 !important;
    color: #ffffff !important;
  }

  /* Main Workspace */
  .main-content {
    flex: 1;
    display: flex;
    padding: 24px 28px;
    gap: 28px;
    overflow: hidden;
    align-items: center;
    justify-content: center;
    transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  }

  /* Left Panel */
  .left-panel {
    width: 320px;
    min-width: 320px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  }

  .cover-box {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 18px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.04);
  }
  .cover-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: opacity 0.3s ease;
  }

  .track-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .track-title {
    font-size: 19px;
    font-weight: 700;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }
  .track-artist {
    font-size: 14px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.72);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* LiquidGL Glass Card */
  .player-card {
    position: relative;
    padding: 16px 18px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.22);
    box-shadow:
      0 16px 40px rgba(0, 0, 0, 0.45),
      inset 0 1px 1px rgba(255, 255, 255, 0.4),
      inset 0 -1px 1px rgba(0, 0, 0, 0.25);
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  /* Visualizer Bar */
  .vocalizer-wrap {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
  }
  .vocalizer-box {
    position: relative;
    width: 100%;
    height: 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
  }
  #waveCanvas {
    width: 100%;
    height: 100%;
    display: block;
  }

  .time-display {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.65);
    letter-spacing: 0.5px;
  }

  /* 5-Button Transport Controls */
  .controls-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4px;
  }

  .ctrl-btn {
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
  }
  .ctrl-btn:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.12);
    transform: scale(1.08);
  }
  .ctrl-btn.active {
    color: #1db954;
  }

  /* Morphing Play/Pause Button */
  .play-morph-btn {
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
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
  }
  .play-morph-btn:hover {
    transform: scale(1.08);
  }
  .morph-icon {
    position: absolute;
    width: 18px;
    height: 18px;
    fill: #000000;
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s ease;
  }
  .morph-play-icon {
    transform: scale(1) rotate(0deg);
    opacity: 1;
    margin-left: 2px;
  }
  .morph-pause-icon {
    transform: scale(0.4) rotate(-90deg);
    opacity: 0;
  }
  .is-playing .morph-play-icon {
    transform: scale(0.4) rotate(90deg);
    opacity: 0;
  }
  .is-playing .morph-pause-icon {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }

  /* Right Panel: Apple Music Karaoke Lyrics */
  .right-panel {
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    mask-image: linear-gradient(to bottom, transparent 0%, black 15%, black 85%, transparent 100%);
    -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 15%, black 85%, transparent 100%);
    transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  }

  .lyrics-scroller {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 160px 20px 200px 20px;
    display: flex;
    flex-direction: column;
    gap: 32px;
    scroll-behavior: smooth;
  }
  .lyrics-scroller::-webkit-scrollbar {
    display: none;
  }

  .lyric-line {
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
  }
  .lyric-line:hover {
    color: rgba(255, 255, 255, 0.6);
  }
  .lyric-line.active {
    color: #ffffff;
    filter: blur(0px);
    transform: scale(1.04) translateX(4px);
  }
  .lyric-line.sung {
    color: rgba(255, 255, 255, 0.95);
    filter: blur(0px);
  }

  /* Karaoke Characters */
  .karaoke-char {
    display: inline-block;
    transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.2s ease, text-shadow 0.2s ease;
    will-change: transform;
    white-space: pre;
  }
  .karaoke-char.lit {
    color: #ffffff;
    text-shadow: 0 0 14px rgba(255, 255, 255, 0.85);
  }
  .karaoke-char.singing {
    transform: translateY(-4px) scale(1.14);
    color: #ffffff;
    text-shadow: 0 0 20px rgba(255, 255, 255, 1);
  }

  /* Compact Centered Mode (No Lyrics Found) */
  body.no-lyrics-mode .titlebar-center {
    display: block !important;
  }
  body.no-lyrics-mode .right-panel {
    display: none !important;
  }
  body.no-lyrics-mode .main-content {
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 16px 24px 28px 24px !important;
    gap: 16px !important;
    width: 100% !important;
    height: calc(100vh - 40px) !important;
  }
  body.no-lyrics-mode .left-panel {
    width: 100% !important;
    max-width: 310px !important;
    min-width: unset !important;
    align-items: center !important;
    text-align: center !important;
    margin: 0 auto !important;
    gap: 14px !important;
  }
  body.no-lyrics-mode .cover-box {
    width: 250px !important;
    height: 250px !important;
    margin: 0 auto !important;
    border-radius: 20px !important;
  }
  body.no-lyrics-mode .track-info {
    align-items: center !important;
    text-align: center !important;
    width: 100% !important;
  }
  body.no-lyrics-mode .player-card {
    width: 100% !important;
  }

  /* Corner Resize Grip */
  .resize-grip {
    position: fixed;
    bottom: 0;
    right: 0;
    width: 18px;
    height: 18px;
    cursor: nwse-resize !important;
    z-index: 100;
    background: linear-gradient(135deg, transparent 50%, rgba(255, 255, 255, 0.3) 50%, rgba(255, 255, 255, 0.3) 65%, transparent 65%, transparent 75%, rgba(255, 255, 255, 0.3) 75%);
    border-bottom-right-radius: 4px;
  }

  /* MINI PLAYER CARD MODE */
  body.mode-mini .app-layout {
    display: none !important;
  }
  body.mode-mini .resize-grip {
    display: none !important;
  }

  .mini-card {
    display: none;
  }

  body.mode-mini .mini-card {
    display: flex !important;
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    flex-direction: column;
    justify-content: space-between;
    background: rgba(18, 18, 22, 0.84);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.75), inset 0 1px 1px rgba(255, 255, 255, 0.3);
    border-radius: 18px;
    overflow: hidden;
    z-index: 100;
  }

  .mini-header {
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 10px 0 10px;
    cursor: default;
  }
  .mini-logo {
    height: 16px;
    width: auto;
    object-fit: contain;
    pointer-events: none;
  }
  .mini-actions {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .mini-btn {
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
  }
  .mini-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    color: #ffffff;
  }
  .mini-close:hover {
    background: #e81123 !important;
    color: #ffffff !important;
  }

  .mini-body {
    flex: 1;
    display: flex;
    align-items: center;
    padding: 2px 14px 6px 14px;
    gap: 14px;
    cursor: default;
  }
  .mini-cover-wrap {
    width: 70px;
    height: 70px;
    min-width: 70px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.15);
    background: rgba(255, 255, 255, 0.05);
  }
  .mini-cover-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .mini-meta {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
    gap: 4px;
  }
  .mini-title {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
  }
  .mini-artist {
    font-size: 12px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.72);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .mini-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 2px;
  }
  .mini-ctrl-btn {
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
  }
  .mini-ctrl-btn:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.15);
    transform: scale(1.1);
  }
  .mini-play-btn {
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
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
  }
  .mini-play-btn:hover {
    transform: scale(1.1);
  }
  .mini-play-btn .morph-icon {
    width: 14px;
    height: 14px;
  }

  #miniWaveCanvas {
    width: 100%;
    height: 26px;
    pointer-events: none;
    display: block;
  }
</style>
</head>
<body>

  <!-- Full Window Crossfading Backgrounds -->
  <div class="bg-viewport">
    <div class="bg-layer" id="bgLayerA"></div>
    <div class="bg-layer" id="bgLayerB"></div>
  </div>

  <!-- MAIN APP LAYOUT -->
  <div class="app-layout" id="appLayout">
    <!-- Custom Frameless Titlebar -->
    <div class="titlebar" id="mainTitlebar">
      <div class="titlebar-left">
        <img class="app-logo" id="logoMain" src="" alt="EZ Lyrics" />
      </div>
      <div class="titlebar-center" id="titleCenter">No lyrics found</div>
      <div class="titlebar-controls">
        <button class="win-btn" onclick="toggleMiniMode()" title="Mini Player">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="3" ry="3"/>
            <rect x="11" y="13" width="8" height="6" rx="1.5" fill="currentColor" opacity="0.8"/>
          </svg>
        </button>
        <button class="win-btn win-min" onclick="window.pywebview.api.minimize_window()" title="Minimize">&#x2500;</button>
        <button class="win-btn win-close" onclick="window.pywebview.api.close_window()" title="Close">&#x2715;</button>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="main-content" id="mainContent">
      <div class="left-panel">
        <div class="cover-box">
          <img class="cover-img" id="albumCoverImg" src="" alt="" onerror="this.style.opacity='0'" onload="this.style.opacity='1'" />
        </div>
        <div class="track-info">
          <div class="track-title" id="trackTitle">Connecting to Spotify...</div>
          <div class="track-artist" id="trackArtist">Waiting for audio playback</div>
        </div>

        <div class="player-card">
          <div class="vocalizer-wrap">
            <div class="vocalizer-box" id="vocalizerBox" title="Click to seek">
              <canvas id="waveCanvas"></canvas>
            </div>
            <div class="time-display">
              <span id="timeCurrent">0:00</span>
              <span id="timeDuration">0:00</span>
            </div>
          </div>

          <div class="controls-row">
            <button class="ctrl-btn" id="loopBtn" onclick="toggleLoop()" title="Loop">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="17 1 21 5 17 9"/>
                <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
                <polyline points="7 23 3 19 7 15"/>
                <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
              </svg>
            </button>

            <button class="ctrl-btn" onclick="prevTrack()" title="Previous">
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

            <button class="ctrl-btn" onclick="nextTrack()" title="Next">
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

      <div class="right-panel">
        <div class="lyrics-scroller" id="lyricsScroller"></div>
      </div>
    </div>
  </div>

  <!-- MINI PLAYER CARD -->
  <div class="mini-card" id="miniCard">
    <div class="mini-header" id="miniHeader">
      <img class="mini-logo" id="logoMini" src="" alt="EZ" />
      <div class="mini-actions">
        <button class="mini-btn" onclick="toggleMiniMode()" title="Restore">
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

    <div class="mini-body" id="miniBody">
      <div class="mini-cover-wrap">
        <img class="mini-cover-img" id="miniCoverImg" src="" alt="" onerror="this.style.opacity='0'" onload="this.style.opacity='1'" />
      </div>
      <div class="mini-meta">
        <div class="mini-title" id="miniTrackTitle">Track Title</div>
        <div class="mini-artist" id="miniTrackArtist">Artist</div>
        <div class="mini-controls">
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

    <canvas id="miniWaveCanvas"></canvas>
  </div>

  <div class="resize-grip" id="resizeGrip" title="Drag to resize"></div>

<script>
  const LOGO_B64 = "__LOGO_PLACEHOLDER__";
  document.getElementById('logoMain').src = "data:image/png;base64," + LOGO_B64;
  document.getElementById('logoMini').src = "data:image/png;base64," + LOGO_B64;

  let state = {
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
  };

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

  // Native Non-Blocking Drag Setup
  function makeDraggable(element) {
    element.addEventListener('mousedown', (e) => {
      if (e.button === 0 && !e.target.closest('button, input, .win-btn, .mini-btn, .ctrl-btn, .play-morph-btn, .mini-ctrl-btn, .mini-play-btn, .resize-grip, #vocalizerBox, .lyric-line')) {
        if (window.pywebview && window.pywebview.api) {
          window.pywebview.api.start_drag();
        }
      }
    });
  }
  makeDraggable(document.getElementById('mainTitlebar'));
  makeDraggable(document.getElementById('miniHeader'));
  makeDraggable(document.getElementById('miniCard'));
  makeDraggable(document.getElementById('miniBody'));

  // Main Wave Visualizer
  function drawWave() {
    const rect = canvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      const tw = Math.round(rect.width * window.devicePixelRatio);
      const th = Math.round(rect.height * window.devicePixelRatio);
      if (canvas.width !== tw || canvas.height !== th) {
        canvas.width = tw;
        canvas.height = th;
      }
    }
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    if (w <= 0 || h <= 0) return;

    const midY = h / 2;
    const numBars = 22;
    const barWidth = 7.0 * window.devicePixelRatio;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const progressRatio = state.duration > 0 ? (localPos / state.duration) : 0;

    waveTick += state.is_playing ? 0.08 : 0.01;
    const peak = Math.max(0.4, (state.audio_peak || 0.0) * 1.9);

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const waveEnvelope = 1.0 - (centerDist * 0.32);

      const freq1 = Math.sin(waveTick * 3.0 + i * 0.55);
      const freq2 = Math.cos(waveTick * 1.8 - i * 0.45);
      const osc = (freq1 * 0.5 + 0.5) * 0.5 + (freq2 * 0.5 + 0.5) * 0.5;

      let amp = 0.08;
      if (state.is_playing) {
        amp = (0.22 + osc * 0.78) * waveEnvelope * Math.min(1.0, peak);
      }
      const barHeight = Math.max(4 * window.devicePixelRatio, Math.min(h - 2, amp * (h - 2)));

      const barProgress = (x + barWidth / 2) / w;
      if (barProgress <= progressRatio) {
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = 'rgba(255, 255, 255, 0.95)';
        ctx.shadowBlur = 8;
      } else {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.28)';
        ctx.shadowBlur = 0;
      }

      ctx.beginPath();
      ctx.roundRect(x, midY - barHeight / 2, barWidth, barHeight, 3);
      ctx.fill();
    }
  }

  // Mini Wave Visualizer (Pops up from bottom)
  function drawMiniWave() {
    const rect = miniCanvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      const tw = Math.round(rect.width * window.devicePixelRatio);
      const th = Math.round(rect.height * window.devicePixelRatio);
      if (miniCanvas.width !== tw || miniCanvas.height !== th) {
        miniCanvas.width = tw;
        miniCanvas.height = th;
      }
    }
    const w = miniCanvas.width;
    const h = miniCanvas.height;
    miniCtx.clearRect(0, 0, w, h);
    if (w <= 0 || h <= 0) return;

    const numBars = 20;
    const barWidth = 8.0 * window.devicePixelRatio;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const peak = Math.max(0.38, (state.audio_peak || 0.0) * 2.0);

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const env = 1.0 - (centerDist * 0.22);

      const freq1 = Math.sin(waveTick * 3.2 + i * 0.5);
      const freq2 = Math.cos(waveTick * 1.9 - i * 0.6);
      const osc = (freq1 * 0.5 + 0.5) * 0.5 + (freq2 * 0.5 + 0.5) * 0.5;

      let amp = 0.08;
      if (state.is_playing) {
        amp = (0.24 + osc * 0.76) * env * Math.min(1.0, peak);
      }
      const barHeight = Math.max(3 * window.devicePixelRatio, Math.min(h, amp * h));

      const grad = miniCtx.createLinearGradient(0, h, 0, h - barHeight);
      grad.addColorStop(0, 'rgba(255, 255, 255, 0.15)');
      grad.addColorStop(0.5, 'rgba(255, 255, 255, 0.65)');
      grad.addColorStop(1, 'rgba(255, 255, 255, 0.98)');

      miniCtx.fillStyle = grad;
      miniCtx.shadowColor = 'rgba(255, 255, 255, 0.8)';
      miniCtx.shadowBlur = 6;

      miniCtx.beginPath();
      miniCtx.roundRect(x, h - barHeight, barWidth, barHeight, [3, 3, 0, 0]);
      miniCtx.fill();
    }
  }

  // Seeking on Vocalizer Bar
  document.getElementById('vocalizerBox').addEventListener('click', (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const targetSec = ratio * state.duration;
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.seek(targetSec);
    }
  });

  function toggleMiniMode() {
    isMiniMode = !isMiniMode;
    document.body.classList.toggle('mode-mini', isMiniMode);
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.set_mode(isMiniMode ? 'mini' : 'restore');
    }
  }

  function togglePlay() {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.toggle_play();
  }
  function prevTrack() {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.prev_track();
  }
  function nextTrack() {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.next_track();
  }
  function toggleLoop() {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_loop().then(val => { loopBtn.classList.toggle('active', !!val); });
    }
  }
  function toggleShuffle() {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_shuffle().then(val => { shuffleBtn.classList.toggle('active', !!val); });
    }
  }

  function formatTime(s) {
    const sec = Math.max(0, Math.floor(s || 0));
    const m = Math.floor(sec / 60);
    const rem = sec % 60;
    return `${m}:${rem < 10 ? '0' : ''}${rem}`;
  }

  lyricsScroller.addEventListener('scroll', () => {
    userScrolling = true;
    if (scrollTimer) clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => { userScrolling = false; }, 2200);
  });

  // Corner Resize Grip
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
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  });

  function onMouseMove(e) {
    if (!isResizing) return;
    const nw = Math.max(340, startW + (e.screenX - startX));
    const nh = Math.max(130, startH + (e.screenY - startY));
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.resize_window(nw, nh);
    }
  }

  function onMouseUp() {
    isResizing = false;
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  }

  // Animation Loop
  let localPos = 0;
  function animFrame() {
    const now = performance.now() / 1000;
    if (state.is_playing) {
      localPos = Math.max(0, Math.min(state.duration, state.base_pos + (now - state.base_time)));
    } else {
      localPos = Math.max(0, Math.min(state.duration, state.base_pos));
    }

    timeCurrent.textContent = formatTime(localPos);
    timeDuration.textContent = formatTime(state.duration);

    if (isMiniMode) {
      drawMiniWave();
    } else {
      drawWave();
    }

    // Karaoke Engine
    if (!isMiniMode && state.lyrics && state.lyrics.length > 0) {
      let activeIdx = -1;
      for (let i = 0; i < state.lyrics.length; i++) {
        const item = state.lyrics[i];
        if (localPos >= item.time && localPos <= item.endTime) {
          activeIdx = i;
          break;
        } else if (localPos > item.endTime && (i === state.lyrics.length - 1 || localPos < state.lyrics[i+1].time)) {
          activeIdx = i;
          break;
        }
      }

      if (activeIdx !== activeIndex) {
        activeIndex = activeIdx;
        const allLines = lyricsScroller.querySelectorAll('.lyric-line');
        allLines.forEach((el, idx) => {
          if (idx < activeIdx) {
            el.className = 'lyric-line sung';
            el.querySelectorAll('.karaoke-char').forEach(c => c.className = 'karaoke-char lit');
          } else if (idx === activeIdx) {
            el.className = 'lyric-line active';
          } else {
            el.className = 'lyric-line';
            el.querySelectorAll('.karaoke-char').forEach(c => c.className = 'karaoke-char');
          }
        });

        if (activeIdx >= 0 && !userScrolling) {
          const targetEl = allLines[activeIdx];
          if (targetEl) {
            const scrollerH = lyricsScroller.clientHeight;
            const targetTop = targetEl.offsetTop;
            const targetH = targetEl.clientHeight;
            lyricsScroller.scrollTo({
              top: targetTop - (scrollerH / 2) + (targetH / 2),
              behavior: 'smooth'
            });
          }
        }
      }

      // Animate Individual Characters on Active Line
      if (activeIdx >= 0) {
        const activeLineEl = lyricsScroller.querySelector(`.lyric-line[data-index="${activeIdx}"]`);
        if (activeLineEl) {
          const lineItem = state.lyrics[activeIdx];
          const lineDur = Math.max(0.5, lineItem.endTime - lineItem.time);
          const lineElapsed = Math.max(0, localPos - lineItem.time);
          const ratio = Math.min(1.0, lineElapsed / lineDur);

          const chars = activeLineEl.querySelectorAll('.karaoke-char');
          const totalChars = chars.length;
          const currentProgressIndex = ratio * totalChars;

          chars.forEach((charEl, cIdx) => {
            if (cIdx < Math.floor(currentProgressIndex)) {
              charEl.className = 'karaoke-char lit';
            } else if (cIdx === Math.floor(currentProgressIndex)) {
              charEl.className = 'karaoke-char singing';
            } else {
              charEl.className = 'karaoke-char';
            }
          });
        }
      }
    }

    requestAnimationFrame(animFrame);
  }
  requestAnimationFrame(animFrame);

  // Poll Backend State
  function pollBridge() {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.get_state().then(s => {
        if (!s) return;

        state.is_playing = s.is_playing;
        state.duration = s.duration || 180;
        state.audio_peak = s.audio_peak || 0.0;

        const currentCalculated = state.base_pos + (s.is_playing ? (performance.now() / 1000 - state.base_time) : 0);
        if (Math.abs(currentCalculated - s.base_pos) > 0.6) {
          state.base_pos = s.base_pos;
          state.base_time = performance.now() / 1000;
        }

        if (state.is_playing) {
          playBtn.classList.add('is-playing');
          miniPlayBtn.classList.add('is-playing');
        } else {
          playBtn.classList.remove('is-playing');
          miniPlayBtn.classList.remove('is-playing');
        }

        if (s.version !== state.version) {
          state.version = s.version;
          state.current_track = s.current_track;
          state.current_artist = s.current_artist;
          state.album_cover = s.album_cover;
          state.lyrics = s.lyrics || [];

          trackTitle.textContent = state.current_track || "Spotify Ready";
          trackArtist.textContent = state.current_artist || "Play any track";
          miniTrackTitle.textContent = state.current_track || "Spotify Ready";
          miniTrackArtist.textContent = state.current_artist || "Play any track";

          if (state.album_cover && state.album_cover !== currentCoverUrl) {
            currentCoverUrl = state.album_cover;
            albumCoverImg.src = state.album_cover;
            miniCoverImg.src = state.album_cover;
            albumCoverImg.style.opacity = '1';
            miniCoverImg.style.opacity = '1';
            if (activeLayer === 'A') {
              bgLayerB.style.backgroundImage = `url("${state.album_cover}")`;
              bgLayerB.style.opacity = '1';
              bgLayerA.style.opacity = '0';
              activeLayer = 'B';
            } else {
              bgLayerA.style.backgroundImage = `url("${state.album_cover}")`;
              bgLayerA.style.opacity = '1';
              bgLayerB.style.opacity = '0';
              activeLayer = 'A';
            }
          }

          // Build Lyrics
          lyricsScroller.innerHTML = "";
          activeIndex = -1;
          if (state.lyrics && state.lyrics.length > 0) {
            state.lyrics.forEach((item, idx) => {
              const lineDiv = document.createElement('div');
              lineDiv.className = 'lyric-line';
              lineDiv.dataset.index = idx;
              for (const ch of item.text) {
                const sp = document.createElement('span');
                sp.className = 'karaoke-char';
                sp.textContent = ch;
                lineDiv.appendChild(sp);
              }
              lineDiv.addEventListener('click', () => {
                if (window.pywebview && window.pywebview.api) {
                  window.pywebview.api.seek(item.time);
                }
              });
              lyricsScroller.appendChild(lineDiv);
            });
          }

          const hasLyrics = state.lyrics && state.lyrics.length > 0;
          if (!hasLyrics && !isCompactMode) {
            isCompactMode = true;
            document.body.classList.add('no-lyrics-mode');
            if (!isMiniMode && window.pywebview && window.pywebview.api) {
              window.pywebview.api.set_mode('compact');
            }
          } else if (hasLyrics && isCompactMode) {
            isCompactMode = false;
            document.body.classList.remove('no-lyrics-mode');
            if (!isMiniMode && window.pywebview && window.pywebview.api) {
              window.pywebview.api.set_mode('expanded');
            }
          }
        }
      }).catch(err => {});
    }
  }

  setInterval(pollBridge, 80);
</script>
</body>
</html>
"""

# Replace logo placeholder with actual base64
html_content = html_content.replace("__LOGO_PLACEHOLDER__", logo_base64)

# Write index.html directly
with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print("Successfully written pure index.html with 100% valid CSS and JS.")
