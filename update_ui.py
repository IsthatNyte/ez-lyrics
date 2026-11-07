import os

with open(r"C:\Users\dryde\spicy_spotify_lyrics\logo_pure_b64.txt", "r", encoding="utf-8") as f:
    pure_logo_b64 = f.read().strip()

with open(r"C:\Users\dryde\spicy_spotify_lyrics\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace corrupted LOGO_B64 with pure_logo_b64
import re
html = re.sub(r'const LOGO_B64 = "[^"]+";', f'const LOGO_B64 = "{pure_logo_b64}";', html)

# 2. Inject CSS for Secret Buttons, Snapping Grid, Bouncy UI Parts, Hover Buttons, Variations, and Spinning Music Disc
custom_css = """
  /* Interactive Logo & 3 Secret Buttons */
  .titlebar-left {
    display: flex;
    align-items: center;
    gap: 8px;
    pointer-events: auto !important;
    position: relative;
    z-index: 50;
  }
  .app-logo, .mini-logo {
    pointer-events: auto !important;
    cursor: pointer !important;
    transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.25s ease;
  }
  .app-logo:hover, .mini-logo:hover {
    transform: scale(1.09);
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.65));
  }
  .app-logo:active, .mini-logo:active {
    transform: scale(0.92);
  }

  .secret-bar {
    display: flex;
    align-items: center;
    gap: 6px;
    pointer-events: none;
    position: relative;
  }
  .secret-bar.open {
    pointer-events: auto;
  }

  .secret-btn {
    width: 26px;
    height: 26px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    background: rgba(255, 255, 255, 0.10);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    color: rgba(255, 255, 255, 0.92);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0;
    filter: blur(10px);
    transform: translateX(-18px) scale(0.72);
    transition:
      opacity 0.36s cubic-bezier(0.25, 1, 0.5, 1),
      filter 0.36s cubic-bezier(0.25, 1, 0.5, 1),
      transform 0.42s cubic-bezier(0.34, 1.56, 0.64, 1),
      background 0.2s ease,
      border-color 0.2s ease,
      box-shadow 0.2s ease;
  }
  .mini-header .secret-btn {
    width: 21px;
    height: 21px;
    border-radius: 6px;
  }
  .secret-bar.open .secret-btn {
    opacity: 1;
    filter: blur(0px);
    transform: translateX(0px) scale(1);
  }
  .secret-bar.open .secret-btn:nth-child(1) { transition-delay: 0.00s; }
  .secret-bar.open .secret-btn:nth-child(2) { transition-delay: 0.05s; }
  .secret-bar.open .secret-btn:nth-child(3) { transition-delay: 0.10s; }

  .secret-btn:hover {
    background: rgba(255, 255, 255, 0.24);
    border-color: rgba(255, 255, 255, 0.48);
    transform: translateX(0px) scale(1.12) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
  }
  .secret-btn.active {
    background: #ffffff;
    color: #08080c;
    border-color: #ffffff;
    box-shadow: 0 0 16px rgba(255, 255, 255, 0.65);
  }
  .secret-btn.danger-active {
    background: #ff3b5c;
    color: #ffffff;
    border-color: #ff6b84;
    box-shadow: 0 0 16px rgba(255, 59, 92, 0.7);
  }

  /* Smooth Animated Add-Part Dropdown & Variations Dropdown */
  .smooth-dropdown {
    position: fixed;
    min-width: 175px;
    padding: 6px;
    border-radius: 13px;
    background: rgba(16, 16, 22, 0.92);
    backdrop-filter: blur(28px) saturate(190%);
    -webkit-backdrop-filter: blur(28px) saturate(190%);
    border: 1px solid rgba(255, 255, 255, 0.22);
    box-shadow: 0 16px 38px rgba(0, 0, 0, 0.75), inset 0 1px 1px rgba(255, 255, 255, 0.28);
    z-index: 99999;
    opacity: 0;
    filter: blur(10px);
    transform: translateY(-10px) scale(0.90);
    transform-origin: top left;
    pointer-events: none;
    transition:
      opacity 0.28s cubic-bezier(0.25, 1, 0.5, 1),
      filter 0.28s cubic-bezier(0.25, 1, 0.5, 1),
      transform 0.34s cubic-bezier(0.34, 1.56, 0.64, 1);
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .smooth-dropdown.open {
    opacity: 1;
    filter: blur(0px);
    transform: translateY(0px) scale(1);
    pointer-events: auto;
  }
  .dropdown-header {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: rgba(255, 255, 255, 0.45);
    padding: 4px 8px 3px 8px;
  }
  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 7px 10px;
    border-radius: 8px;
    border: none;
    background: transparent;
    color: rgba(255, 255, 255, 0.88);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    text-align: left;
    transition: all 0.16s ease;
  }
  .dropdown-item:hover {
    background: rgba(255, 255, 255, 0.15);
    color: #ffffff;
    transform: translateX(2px);
  }
  .dropdown-item.selected {
    background: rgba(255, 255, 255, 0.22);
    color: #ffffff;
  }
  .dropdown-item .badge {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 5px;
    background: rgba(255, 255, 255, 0.14);
    color: rgba(255, 255, 255, 0.8);
  }

  /* Snapping Grid Overlay in Wrench Edit Mode */
  .snap-grid-overlay {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 2;
    opacity: 0;
    background-image:
      linear-gradient(to right, rgba(255, 255, 255, 0.06) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255, 255, 255, 0.06) 1px, transparent 1px),
      radial-gradient(circle, rgba(255, 255, 255, 0.20) 1px, transparent 1px);
    background-size: 12px 12px, 12px 12px, 24px 24px;
    transition: opacity 0.32s ease;
  }
  body.edit-mode .snap-grid-overlay {
    opacity: 1;
  }

  /* Customizable UI Parts */
  .ui-part {
    position: relative;
    transition:
      transform 0.38s cubic-bezier(0.34, 1.56, 0.64, 1),
      opacity 0.28s ease,
      filter 0.28s ease,
      box-shadow 0.25s ease;
    transform-origin: center center;
  }
  .ui-part.dragging-part {
    transition: none !important;
    z-index: 80 !important;
  }
  .ui-part.part-hidden {
    display: none !important;
  }
  .ui-part.part-imploding {
    animation: partImplodeAnim 0.30s cubic-bezier(0.55, 0, 1, 0.45) forwards !important;
    pointer-events: none !important;
  }
  .ui-part.part-spawning {
    animation: partSpawnAnim 0.42s cubic-bezier(0.34, 1.56, 0.64, 1) forwards !important;
  }
  @keyframes partImplodeAnim {
    0% { transform: scale(1); opacity: 1; filter: blur(0px); }
    100% { transform: scale(0.05) rotate(10deg); opacity: 0; filter: blur(10px); }
  }
  @keyframes partSpawnAnim {
    0% { transform: scale(0.15); opacity: 0; filter: blur(10px); }
    70% { transform: scale(1.06); opacity: 1; filter: blur(0px); }
    100% { transform: scale(1); opacity: 1; filter: blur(0px); }
  }

  body.edit-mode .ui-part {
    outline: 1.5px dashed rgba(255, 255, 255, 0.35);
    outline-offset: 4px;
    border-radius: 14px;
    cursor: grab !important;
  }
  body.edit-mode .ui-part:active {
    cursor: grabbing !important;
  }
  body.remove-mode .ui-part {
    outline: 1.5px dashed rgba(255, 59, 92, 0.75) !important;
    outline-offset: 4px;
    cursor: pointer !important;
  }
  body.remove-mode .ui-part:hover {
    background: rgba(255, 59, 92, 0.14);
    box-shadow: 0 0 20px rgba(255, 59, 92, 0.35);
  }

  /* 2 Blur-Fade Hover Buttons on UI Part */
  .part-hover-bar {
    position: absolute;
    top: 6px;
    right: 6px;
    display: flex;
    align-items: center;
    gap: 5px;
    z-index: 95;
    opacity: 0;
    filter: blur(8px);
    transform: translateY(-4px) scale(0.88);
    pointer-events: none;
    transition:
      opacity 0.24s cubic-bezier(0.25, 1, 0.5, 1),
      filter 0.24s cubic-bezier(0.25, 1, 0.5, 1),
      transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .ui-part:hover .part-hover-bar,
  body.edit-mode .ui-part .part-hover-bar {
    opacity: 1;
    filter: blur(0px);
    transform: translateY(0px) scale(1);
    pointer-events: auto;
  }
  .part-hover-btn {
    width: 24px;
    height: 24px;
    border-radius: 7px;
    border: 1px solid rgba(255, 255, 255, 0.28);
    background: rgba(14, 14, 20, 0.82);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    transition: all 0.18s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .part-hover-btn:hover {
    background: #ffffff;
    color: #08080c;
    transform: scale(1.14);
  }

  /* Corner Rescale Handle in Wrench Edit Mode */
  .part-scale-handle {
    position: absolute;
    bottom: -5px;
    right: -5px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #ffffff;
    border: 2px solid #08080c;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
    cursor: nwse-resize !important;
    z-index: 96;
    opacity: 0;
    transform: scale(0.5);
    pointer-events: none;
    transition: all 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  body.edit-mode .ui-part .part-scale-handle {
    opacity: 1;
    transform: scale(1);
    pointer-events: auto;
  }
  body.edit-mode .ui-part .part-scale-handle:hover {
    transform: scale(1.3);
  }

  /* ================= VARIATIONS STYLING ================= */

  /* 1. Album Cover Variations */
  /* Variation: Spinning Music Disc (Vinyl Record) */
  .cover-box.var-disc,
  .mini-cover-wrap.var-disc {
    border-radius: 50% !important;
    border: 3px solid rgba(25, 25, 30, 0.95) !important;
    box-shadow:
      0 14px 34px rgba(0, 0, 0, 0.75),
      inset 0 0 0 8px rgba(15, 15, 18, 0.85),
      inset 0 0 0 9px rgba(255, 255, 255, 0.12),
      inset 0 0 0 18px rgba(15, 15, 18, 0.82),
      inset 0 0 0 19px rgba(255, 255, 255, 0.08) !important;
    overflow: hidden;
  }
  .cover-box.var-disc::before,
  .mini-cover-wrap.var-disc::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background:
      repeating-radial-gradient(
        circle at center,
        rgba(0, 0, 0, 0) 0px,
        rgba(0, 0, 0, 0) 4px,
        rgba(0, 0, 0, 0.28) 5px,
        rgba(255, 255, 255, 0.06) 6px
      ),
      conic-gradient(
        from 0deg,
        transparent 0deg,
        rgba(255, 255, 255, 0.18) 35deg,
        transparent 70deg,
        transparent 180deg,
        rgba(255, 255, 255, 0.18) 215deg,
        transparent 250deg
      );
    z-index: 3;
    pointer-events: none;
  }
  .cover-box.var-disc::after,
  .mini-cover-wrap.var-disc::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 22%;
    height: 22%;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    background: radial-gradient(circle, #08080c 0%, #08080c 42%, rgba(255, 255, 255, 0.85) 45%, #16161d 52%, #0e0e14 100%);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.75);
    z-index: 4;
    pointer-events: none;
  }
  .cover-box.var-disc .cover-img,
  .mini-cover-wrap.var-disc .mini-cover-img {
    border-radius: 50%;
    will-change: transform;
  }

  /* Variation: Soft Circle Halo */
  .cover-box.var-circle,
  .mini-cover-wrap.var-circle {
    border-radius: 50% !important;
    border: 2px solid rgba(255, 255, 255, 0.38) !important;
    box-shadow: 0 0 32px rgba(255, 255, 255, 0.22), 0 16px 36px rgba(0, 0, 0, 0.6) !important;
  }

  /* Variation: 3D Vinyl Sleeve */
  .cover-box.var-vinyl3d,
  .mini-cover-wrap.var-vinyl3d {
    border-radius: 10px 26px 10px 26px !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    box-shadow: -10px 14px 28px rgba(0, 0, 0, 0.7), inset 0 0 18px rgba(255, 255, 255, 0.18) !important;
  }

  /* 2. Track Info Variations */
  .track-info.var-centered,
  .mini-meta-text.var-centered {
    align-items: center !important;
    text-align: center !important;
  }
  .track-info.var-badge,
  .mini-meta-text.var-badge {
    background: rgba(255, 255, 255, 0.09);
    border: 1px solid rgba(255, 255, 255, 0.18);
    padding: 8px 14px;
    border-radius: 14px;
    backdrop-filter: blur(16px);
  }
  .track-info.var-neon .track-title,
  .mini-meta-text.var-neon .mini-title {
    color: #ffffff;
    text-shadow: 0 0 12px rgba(255, 255, 255, 0.9), 0 0 24px rgba(120, 200, 255, 0.7);
    letter-spacing: 0.6px;
  }

  /* 3. Player Card / Controls Variations */
  .player-card.var-minimal {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    padding: 6px 0 !important;
  }
  .player-card.var-capsule {
    border-radius: 36px !important;
    background: rgba(12, 12, 18, 0.78) !important;
    border: 1px solid rgba(255, 255, 255, 0.32) !important;
    padding: 14px 24px !important;
  }
  .player-card.var-neon .play-morph-btn,
  .mini-controls.var-neon .mini-play-btn {
    box-shadow: 0 0 18px rgba(255, 255, 255, 0.9), 0 0 32px rgba(255, 255, 255, 0.45) !important;
  }

  /* 4. Lyrics Variations */
  .right-panel.var-centered .lyric-line {
    align-items: center !important;
    text-align: center !important;
  }
  .right-panel.var-centered .main-lyric-row,
  .right-panel.var-centered .adlib-lyric-row {
    justify-content: center !important;
  }
  .right-panel.var-cards .lyric-line {
    padding: 12px 16px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }
  .right-panel.var-cards .lyric-line.active {
    background: rgba(255, 255, 255, 0.11);
    border-color: rgba(255, 255, 255, 0.24);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.38);
  }
"""

html = html.replace("</style>", custom_css + "\n</style>")

# 3. Inject Secret Buttons into Main Titlebar and Mini Header
old_titlebar_left = """      <div class="titlebar-left">
        <img class="app-logo" id="logoMain" src="" alt="EZ Lyrics" />
      </div>"""

new_titlebar_left = """      <div class="titlebar-left">
        <img class="app-logo" id="logoMain" src="" alt="EZ Lyrics" onclick="toggleSecretMenu(event)" title="Click for Secret UI Customizer" />
        <div class="secret-bar" id="secretBarMain">
          <button class="secret-btn" id="wrenchBtnMain" onclick="toggleEditMode(event)" title="Customize, Move, Scale & Rotate UI Parts">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
          </button>
          <button class="secret-btn" id="addPartBtnMain" onclick="openAddPartMenu(event, this)" title="Add UI Part">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
          <button class="secret-btn" id="removePartBtnMain" onclick="toggleRemoveMode(event)" title="Remove UI Part">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
        </div>
      </div>"""

assert old_titlebar_left in html, "old_titlebar_left not found"
html = html.replace(old_titlebar_left, new_titlebar_left)

old_mini_header_logo = """    <div class="mini-header" id="miniHeader">
      <img class="mini-logo" id="logoMini" src="" alt="EZ" />"""

new_mini_header_logo = """    <div class="mini-header" id="miniHeader">
      <div class="titlebar-left" style="gap: 5px;">
        <img class="mini-logo" id="logoMini" src="" alt="EZ" onclick="toggleSecretMenu(event)" title="Click for Secret UI Customizer" />
        <div class="secret-bar" id="secretBarMini">
          <button class="secret-btn" id="wrenchBtnMini" onclick="toggleEditMode(event)" title="Customize UI">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
          </button>
          <button class="secret-btn" id="addPartBtnMini" onclick="openAddPartMenu(event, this)" title="Add UI Part">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
          <button class="secret-btn" id="removePartBtnMini" onclick="toggleRemoveMode(event)" title="Remove UI Part">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
        </div>
      </div>"""

assert old_mini_header_logo in html, "old_mini_header_logo not found"
html = html.replace(old_mini_header_logo, new_mini_header_logo)

# 4. Add data-part attributes to UI parts in Main and Mini layouts
html = html.replace('<div class="cover-box">', '<div class="cover-box ui-part" id="partCover" data-part="cover" data-label="Album Cover">')
html = html.replace('<div class="track-info">', '<div class="track-info ui-part" id="partTrackInfo" data-part="trackinfo" data-label="Song Title & Artist">')
html = html.replace('<div class="player-card">', '<div class="player-card ui-part" id="partPlayerCard" data-part="controls" data-label="Player Dock">')
html = html.replace('<div class="vocalizer-wrap">', '<div class="vocalizer-wrap ui-part" id="partVisualizer" data-part="visualizer" data-label="Audio Visualizer">')
html = html.replace('<div class="right-panel">', '<div class="right-panel ui-part" id="partLyrics" data-part="lyrics" data-label="Karaoke Lyrics">')

# Mini parts
old_mini_body = """    <div class="mini-body" id="miniBody">
      <div class="mini-cover-wrap">
        <img class="mini-cover-img" id="miniCoverImg" src="" alt="" onerror="this.style.opacity='0'" onload="this.style.opacity='1'" />
      </div>
      <div class="mini-meta">
        <div class="mini-title" id="miniTrackTitle">Track Title</div>
        <div class="mini-artist" id="miniTrackArtist">Artist</div>
        <div class="mini-vocalizer-box" id="miniVocalizerBox" title="Click to seek">
          <canvas id="miniWaveCanvas"></canvas>
        </div>
        <div class="mini-controls">"""

new_mini_body = """    <div class="mini-body" id="miniBody">
      <div class="mini-cover-wrap ui-part" id="partMiniCover" data-part="cover" data-label="Mini Cover">
        <img class="mini-cover-img" id="miniCoverImg" src="" alt="" onerror="this.style.opacity='0'" onload="this.style.opacity='1'" />
      </div>
      <div class="mini-meta">
        <div class="mini-meta-text ui-part" id="partMiniTrackInfo" data-part="trackinfo" data-label="Mini Track Info" style="display:flex;flex-direction:column;gap:2px;">
          <div class="mini-title" id="miniTrackTitle">Track Title</div>
          <div class="mini-artist" id="miniTrackArtist">Artist</div>
        </div>
        <div class="mini-vocalizer-box ui-part" id="miniVocalizerBox" data-part="visualizer" data-label="Mini Visualizer" title="Click to seek">
          <canvas id="miniWaveCanvas"></canvas>
        </div>
        <div class="mini-controls ui-part" id="partMiniControls" data-part="controls" data-label="Mini Controls">"""

assert old_mini_body in html, "old_mini_body not found"
html = html.replace(old_mini_body, new_mini_body)

# 5. Add Snapping Grid Overlay & Dropdown Containers right before <canvas id="fxCanvas">
overlay_html = """
  <div class="snap-grid-overlay" id="snapGridOverlay"></div>
  <div class="smooth-dropdown" id="addPartDropdown"></div>
  <div class="smooth-dropdown" id="variationsDropdown"></div>
"""
html = html.replace('<canvas id="fxCanvas"></canvas>', overlay_html + '\n  <canvas id="fxCanvas"></canvas>')

# 6. Update Particle System to support gravity + add/remove part bursts, plus Visualizer Variations, Spinning Disc Physics, and Full UI Customization Engine
old_particle_code = """  // Implosion & White Particle Pop Animation
  let particles = [];
  function spawnPopParticles(cx, cy) {
    if (!fxCanvas || !fxCtx) return;
    resizeCanvases();
    particles = [];
    const count = 48;
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = (4.0 + Math.random() * 9.0) * window.devicePixelRatio;
      particles.push({
        x: cx * window.devicePixelRatio,
        y: cy * window.devicePixelRatio,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: (3.5 + Math.random() * 5.5) * window.devicePixelRatio,
        alpha: 1.0,
        decay: 0.018 + Math.random() * 0.022
      });
    }
  }

  function renderParticles() {
    if (!fxCtx) return;
    fxCtx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);
    if (particles.length === 0) return;

    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.94;
      p.vy *= 0.94;
      p.size = Math.max(0.2, p.size * 0.94);
      p.alpha -= p.decay;
      if (p.alpha <= 0 || p.size <= 0.3) {
        particles.splice(i, 1);
        continue;
      }
      fxCtx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
      fxCtx.beginPath();
      fxCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      fxCtx.fill();
    }
    requestAnimationFrame(renderParticles);
  }"""

new_particle_code = """  // Implosion & White Particle Pop Animation with Gravity Physics
  let particles = [];
  let particleLoopActive = false;

  function spawnPopParticles(cx, cy, withGravity = true, count = 44) {
    if (!fxCanvas || !fxCtx) return;
    resizeCanvases();
    const dpr = window.devicePixelRatio || 1;
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = (3.2 + Math.random() * 8.5) * dpr;
      particles.push({
        x: cx * dpr,
        y: cy * dpr,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - (withGravity ? (2.2 + Math.random() * 3.0) * dpr : 0),
        gravity: withGravity ? (0.36 * dpr) : (0.14 * dpr),
        size: (3.2 + Math.random() * 5.2) * dpr,
        alpha: 1.0,
        decay: 0.015 + Math.random() * 0.018
      });
    }
    if (!particleLoopActive) {
      particleLoopActive = true;
      requestAnimationFrame(renderParticles);
    }
  }

  function renderParticles() {
    if (!fxCtx) {
      particleLoopActive = false;
      return;
    }
    fxCtx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);
    if (particles.length === 0) {
      particleLoopActive = false;
      return;
    }

    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.vy += p.gravity;
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.96;
      p.size = Math.max(0.15, p.size * 0.955);
      p.alpha -= p.decay;
      if (p.alpha <= 0 || p.size <= 0.25) {
        particles.splice(i, 1);
        continue;
      }
      fxCtx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
      fxCtx.beginPath();
      fxCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      fxCtx.fill();
    }
    requestAnimationFrame(renderParticles);
  }"""

assert old_particle_code in html, "old_particle_code not found"
html = html.replace(old_particle_code, new_particle_code)

# 7. Update makeDraggable so dragging a UI part in Edit Mode or clicking secret/hover menus does not drag the OS window
old_draggable_check = "if (e.button === 0 && !e.target.closest('button, input, .win-btn, .mini-btn, .ctrl-btn, .play-morph-btn, .mini-ctrl-btn, .mini-play-btn, .resize-grip, #vocalizerBox, #miniVocalizerBox, .lyric-line')) {"
new_draggable_check = "if (e.button === 0 && !isEditMode && !isRemoveMode && !e.target.closest('button, input, .app-logo, .mini-logo, .secret-bar, .smooth-dropdown, .part-hover-bar, .part-scale-handle, .win-btn, .mini-btn, .ctrl-btn, .play-morph-btn, .mini-ctrl-btn, .mini-play-btn, .resize-grip, #vocalizerBox, #miniVocalizerBox, .lyric-line')) {"
assert old_draggable_check in html, "old_draggable_check not found"
html = html.replace(old_draggable_check, new_draggable_check)

# 8. Upgrade drawWave & drawMiniWave to support Visualizer Variations (Center Capsule Wave, Bottom Rising EQ Pillars, Liquid Sine Ribbon)
old_draw_waves = """  // Main Wave Visualizer (Lightweight, No Layout Thrashing, No Software ShadowBlur)
  function drawWave() {
    const w = canvas.width;
    const h = canvas.height;
    if (w <= 0 || h <= 0) return;
    ctx.clearRect(0, 0, w, h);

    const midY = h / 2;
    const numBars = 22;
    const barWidth = 7.0 * window.devicePixelRatio;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const progressRatio = state.duration > 0 ? (localPos / state.duration) : 0;

    waveTick += state.is_playing ? 0.09 : 0.01;
    const dynamicPeak = getDynamicIntensity(state.audio_peak || 0.0, state.is_playing);

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const waveEnvelope = 1.0 - (centerDist * 0.28);

      const freq1 = Math.sin(waveTick * 3.6 + i * 0.55);
      const freq2 = Math.cos(waveTick * 2.1 - i * 0.45);
      const osc = (freq1 * 0.5 + 0.5) * 0.55 + (freq2 * 0.5 + 0.5) * 0.45;

      let amp = 0.06;
      if (state.is_playing) {
        const bounce = (0.22 + 0.78 * osc) * dynamicPeak * waveEnvelope;
        amp = Math.max(0.05, Math.min(0.96, bounce * 1.45));
      }
      const barHeight = Math.max(4 * window.devicePixelRatio, Math.min(h - 2, amp * (h - 2)));

      const barProgress = (x + barWidth / 2) / w;
      if (barProgress <= progressRatio) {
        ctx.fillStyle = '#ffffff';
      } else {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.28)';
      }

      ctx.beginPath();
      ctx.roundRect(x, midY - barHeight / 2, barWidth, barHeight, 3);
      ctx.fill();
    }
  }

  // Mini Wave Visualizer (Identical to Expanded Visualizer with Waveform & Progress)
  function drawMiniWave() {
    const w = miniCanvas.width;
    const h = miniCanvas.height;
    if (w <= 0 || h <= 0) return;
    miniCtx.clearRect(0, 0, w, h);

    const midY = h / 2;
    const numBars = 18;
    const barWidth = 6.0 * window.devicePixelRatio;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const progressRatio = state.duration > 0 ? (localPos / state.duration) : 0;

    waveTick += state.is_playing ? 0.09 : 0.01;
    const dynamicPeak = getDynamicIntensity(state.audio_peak || 0.0, state.is_playing);

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const env = 1.0 - (centerDist * 0.28);

      const freq1 = Math.sin(waveTick * 3.6 + i * 0.55);
      const freq2 = Math.cos(waveTick * 2.1 - i * 0.45);
      const osc = (freq1 * 0.5 + 0.5) * 0.55 + (freq2 * 0.5 + 0.5) * 0.45;

      let amp = 0.08;
      if (state.is_playing) {
        const bounce = (0.24 + 0.76 * osc) * dynamicPeak * env;
        amp = Math.max(0.06, Math.min(0.96, bounce * 1.45));
      }
      const barHeight = Math.max(3 * window.devicePixelRatio, Math.min(h - 2, amp * (h - 2)));

      const barProgress = (x + barWidth / 2) / w;
      if (barProgress <= progressRatio) {
        miniCtx.fillStyle = '#ffffff';
      } else {
        miniCtx.fillStyle = 'rgba(255, 255, 255, 0.28)';
      }

      miniCtx.beginPath();
      miniCtx.roundRect(x, midY - barHeight / 2, barWidth, barHeight, 2.5);
      miniCtx.fill();
    }
  }"""

new_draw_waves = """  let currentVisualizerVariation = 'bars'; // 'bars', 'pillars', 'wave'

  function renderVisualizerOnCanvas(targetCtx, w, h, numBars, baseBarW, radius) {
    if (w <= 0 || h <= 0) return;
    targetCtx.clearRect(0, 0, w, h);

    const dpr = window.devicePixelRatio || 1;
    const midY = h / 2;
    const barWidth = baseBarW * dpr;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const progressRatio = state.duration > 0 ? (localPos / state.duration) : 0;

    waveTick += state.is_playing ? 0.09 : 0.01;
    const dynamicPeak = getDynamicIntensity(state.audio_peak || 0.0, state.is_playing);

    if (currentVisualizerVariation === 'wave') {
      // Variation 3: Liquid Sine Ribbon
      const points = 42;
      targetCtx.lineWidth = 2.8 * dpr;
      targetCtx.lineCap = 'round';
      for (let pass = 0; pass < 2; pass++) {
        targetCtx.beginPath();
        for (let i = 0; i <= points; i++) {
          const ratioX = i / points;
          const x = ratioX * w;
          const env = Math.sin(ratioX * Math.PI);
          const osc = Math.sin(waveTick * 4.2 + i * 0.35 + pass * 1.3) * Math.cos(waveTick * 2.3 - i * 0.22);
          const amp = state.is_playing ? (osc * dynamicPeak * env * (h * 0.44)) : (Math.sin(i * 0.3) * 1.5 * dpr);
          const y = midY + amp;
          if (i === 0) targetCtx.moveTo(x, y);
          else targetCtx.lineTo(x, y);
        }
        targetCtx.strokeStyle = pass === 0 ? '#ffffff' : 'rgba(255, 255, 255, 0.35)';
        targetCtx.stroke();
      }
      return;
    }

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const waveEnvelope = 1.0 - (centerDist * 0.28);

      const freq1 = Math.sin(waveTick * 3.6 + i * 0.55);
      const freq2 = Math.cos(waveTick * 2.1 - i * 0.45);
      const osc = (freq1 * 0.5 + 0.5) * 0.55 + (freq2 * 0.5 + 0.5) * 0.45;

      let amp = 0.07;
      if (state.is_playing) {
        const bounce = (0.22 + 0.78 * osc) * dynamicPeak * waveEnvelope;
        amp = Math.max(0.05, Math.min(0.96, bounce * 1.45));
      }
      const barHeight = Math.max(3.5 * dpr, Math.min(h - 2, amp * (h - 2)));

      const barProgress = (x + barWidth / 2) / w;
      if (barProgress <= progressRatio) {
        targetCtx.fillStyle = '#ffffff';
      } else {
        targetCtx.fillStyle = 'rgba(255, 255, 255, 0.28)';
      }

      targetCtx.beginPath();
      if (currentVisualizerVariation === 'pillars') {
        // Variation 2: Bottom Rising EQ Pillars
        targetCtx.roundRect(x, h - barHeight, barWidth, barHeight, radius);
      } else {
        // Variation 1: Symmetric Center Bars
        targetCtx.roundRect(x, midY - barHeight / 2, barWidth, barHeight, radius);
      }
      targetCtx.fill();
    }
  }

  function drawWave() {
    renderVisualizerOnCanvas(ctx, canvas.width, canvas.height, 22, 7.0, 3);
  }

  function drawMiniWave() {
    renderVisualizerOnCanvas(miniCtx, miniCanvas.width, miniCanvas.height, 18, 6.0, 2.5);
  }"""

assert old_draw_waves in html, "old_draw_waves not found"
html = html.replace(old_draw_waves, new_draw_waves)

# 9. Inject the Secret Menu, Wrench Edit Mode, Bouncy Grid Snapping, Add/Remove Parts, Hover Variations, and Spinning Vinyl Disc Physics into animFrame & script end
custom_js = """
  // ================= SECRET CUSTOMIZATION SUITE & SPINNING DISC ENGINE =================
  let isSecretMenuOpen = false;
  let isEditMode = false;
  let isRemoveMode = false;
  const GRID_SNAP = 12;

  // Spinning Music Disc Physics (Spins smoothly when playing, gradually decelerates when paused)
  let discAngle = 0;
  let discVelocity = 0;

  function updateSpinningDisc() {
    const isDiscActive = (currentVariations.cover === 'disc');
    if (!isDiscActive) {
      if (discAngle !== 0) {
        discAngle = 0;
        albumCoverImg.style.transform = '';
        miniCoverImg.style.transform = '';
      }
      return;
    }
    const targetVel = state.is_playing ? 1.35 : 0.0;
    // Smooth acceleration & gradual inertia deceleration when paused
    discVelocity += (targetVel - discVelocity) * (state.is_playing ? 0.05 : 0.025);
    if (Math.abs(discVelocity) < 0.002 && !state.is_playing) {
      discVelocity = 0;
    }
    if (discVelocity > 0) {
      discAngle = (discAngle + discVelocity) % 360;
      const rotStr = `rotate(${discAngle.toFixed(2)}deg)`;
      albumCoverImg.style.transform = rotStr;
      miniCoverImg.style.transform = rotStr;
    }
  }

  // Per-Mode Layout Configurations (expanded, compact, mini)
  const defaultPartState = () => ({
    cover:      { x: 0, y: 0, scale: 1, rot: 0, hidden: false },
    trackinfo:  { x: 0, y: 0, scale: 1, rot: 0, hidden: false },
    visualizer: { x: 0, y: 0, scale: 1, rot: 0, hidden: false },
    controls:   { x: 0, y: 0, scale: 1, rot: 0, hidden: false },
    lyrics:     { x: 0, y: 0, scale: 1, rot: 0, hidden: false }
  });

  let layoutState = {
    expanded: defaultPartState(),
    compact:  defaultPartState(),
    mini:     defaultPartState()
  };

  let currentVariations = {
    cover: 'rounded',      // 'rounded', 'disc', 'circle', 'vinyl3d'
    trackinfo: 'classic',  // 'classic', 'centered', 'badge', 'neon'
    visualizer: 'bars',    // 'bars', 'pillars', 'wave'
    controls: 'glass',     // 'glass', 'minimal', 'capsule', 'neon'
    lyrics: 'karaoke'      // 'karaoke', 'centered', 'cards'
  };

  try {
    const savedLayouts = localStorage.getItem('ez_lyrics_layouts_v2');
    if (savedLayouts) layoutState = Object.assign(layoutState, JSON.parse(savedLayouts));
    const savedVars = localStorage.getItem('ez_lyrics_vars_v2');
    if (savedVars) currentVariations = Object.assign(currentVariations, JSON.parse(savedVars));
  } catch (e) {}

  function saveCustomizations() {
    try {
      localStorage.setItem('ez_lyrics_layouts_v2', JSON.stringify(layoutState));
      localStorage.setItem('ez_lyrics_vars_v2', JSON.stringify(currentVariations));
    } catch (e) {}
  }

  function getActiveModeKey() {
    if (isMiniMode) return 'mini';
    if (isCompactMode) return 'compact';
    return 'expanded';
  }

  const VARIATION_CATALOG = {
    cover: [
      { id: 'rounded', name: 'Rounded Square' },
      { id: 'disc',    name: 'Spinning Music Disc' },
      { id: 'circle',  name: 'Soft Circle Halo' },
      { id: 'vinyl3d', name: '3D Floating Sleeve' }
    ],
    trackinfo: [
      { id: 'classic',  name: 'Classic Stacked' },
      { id: 'centered', name: 'Centered Spotlight' },
      { id: 'badge',    name: 'Frosted Glass Pill' },
      { id: 'neon',     name: 'Neon Glow Title' }
    ],
    visualizer: [
      { id: 'bars',    name: 'Center Capsule Wave' },
      { id: 'pillars', name: 'Rising EQ Pillars' },
      { id: 'wave',    name: 'Liquid Sine Ribbon' }
    ],
    controls: [
      { id: 'glass',   name: 'LiquidGL Glass Dock' },
      { id: 'minimal', name: 'Minimal Floating' },
      { id: 'capsule', name: 'Retro Capsule Deck' },
      { id: 'neon',    name: 'Neon Pulse Controls' }
    ],
    lyrics: [
      { id: 'karaoke',  name: 'Left Karaoke Bounce' },
      { id: 'centered', name: 'Centered Cinema' },
      { id: 'cards',    name: 'Frosted Lyric Cards' }
    ]
  };

  const PART_NAMES = {
    cover: 'Album Cover',
    trackinfo: 'Song Title & Artist',
    visualizer: 'Audio Visualizer',
    controls: 'Player Controls',
    lyrics: 'Karaoke Lyrics'
  };

  function applyAllVariations() {
    // 1. Cover
    const coverEls = [document.getElementById('partCover'), document.getElementById('partMiniCover')];
    coverEls.forEach(el => {
      if (!el) return;
      el.classList.remove('var-disc', 'var-circle', 'var-vinyl3d');
      if (currentVariations.cover !== 'rounded') {
        el.classList.add('var-' + currentVariations.cover);
      }
    });
    if (currentVariations.cover !== 'disc') {
      albumCoverImg.style.transform = '';
      miniCoverImg.style.transform = '';
    }

    // 2. Track Info
    const infoEls = [document.getElementById('partTrackInfo'), document.getElementById('partMiniTrackInfo')];
    infoEls.forEach(el => {
      if (!el) return;
      el.classList.remove('var-centered', 'var-badge', 'var-neon');
      if (currentVariations.trackinfo !== 'classic') {
        el.classList.add('var-' + currentVariations.trackinfo);
      }
    });

    // 3. Visualizer
    currentVisualizerVariation = currentVariations.visualizer || 'bars';

    // 4. Controls
    const ctrlEls = [document.getElementById('partPlayerCard'), document.getElementById('partMiniControls')];
    ctrlEls.forEach(el => {
      if (!el) return;
      el.classList.remove('var-minimal', 'var-capsule', 'var-neon');
      if (currentVariations.controls !== 'glass') {
        el.classList.add('var-' + currentVariations.controls);
      }
    });

    // 5. Lyrics
    const lyricsEl = document.getElementById('partLyrics');
    if (lyricsEl) {
      lyricsEl.classList.remove('var-centered', 'var-cards');
      if (currentVariations.lyrics !== 'karaoke') {
        lyricsEl.classList.add('var-' + currentVariations.lyrics);
      }
    }
  }

  function applyModeLayout() {
    const modeKey = getActiveModeKey();
    const modeConfig = layoutState[modeKey] || defaultPartState();
    document.querySelectorAll('.ui-part').forEach(el => {
      const partKey = el.dataset.part;
      const cfg = modeConfig[partKey];
      if (!cfg) return;
      if (cfg.hidden) {
        el.classList.add('part-hidden');
      } else {
        el.classList.remove('part-hidden');
      }
      el.style.transform = `translate3d(${cfg.x || 0}px, ${cfg.y || 0}px, 0) scale(${cfg.scale || 1}) rotate(${cfg.rot || 0}deg)`;
    });
    setTimeout(resizeCanvases, 30);
  }

  function toggleSecretMenu(e) {
    if (e) e.stopPropagation();
    playClickSound();
    isSecretMenuOpen = !isSecretMenuOpen;
    document.getElementById('secretBarMain').classList.toggle('open', isSecretMenuOpen);
    document.getElementById('secretBarMini').classList.toggle('open', isSecretMenuOpen);
    if (!isSecretMenuOpen) {
      isEditMode = false;
      isRemoveMode = false;
      document.body.classList.remove('edit-mode', 'remove-mode');
      syncSecretButtonStates();
      closeAllDropdowns();
    }
  }

  function syncSecretButtonStates() {
    ['wrenchBtnMain', 'wrenchBtnMini'].forEach(id => {
      const b = document.getElementById(id);
      if (b) b.classList.toggle('active', isEditMode);
    });
    ['removePartBtnMain', 'removePartBtnMini'].forEach(id => {
      const b = document.getElementById(id);
      if (b) b.classList.toggle('danger-active', isRemoveMode);
    });
  }

  function toggleEditMode(e) {
    if (e) e.stopPropagation();
    playClickSound();
    isEditMode = !isEditMode;
    if (isEditMode) isRemoveMode = false;
    document.body.classList.toggle('edit-mode', isEditMode);
    document.body.classList.remove('remove-mode');
    syncSecretButtonStates();
    closeAllDropdowns();
  }

  function toggleRemoveMode(e) {
    if (e) e.stopPropagation();
    playClickSound();
    isRemoveMode = !isRemoveMode;
    if (isRemoveMode) isEditMode = false;
    document.body.classList.toggle('remove-mode', isRemoveMode);
    document.body.classList.remove('edit-mode');
    syncSecretButtonStates();
    closeAllDropdowns();
  }

  function closeAllDropdowns() {
    document.getElementById('addPartDropdown').classList.remove('open');
    document.getElementById('variationsDropdown').classList.remove('open');
  }

  function positionDropdown(dropdown, anchorRect) {
    const dw = 190;
    const dh = 190;
    let left = Math.min(window.innerWidth - dw - 8, Math.max(8, anchorRect.left));
    let top = anchorRect.bottom + 6;
    if (top + dh > window.innerHeight - 8) {
      top = Math.max(8, anchorRect.top - dh - 6);
    }
    dropdown.style.left = left + 'px';
    dropdown.style.top = top + 'px';
  }

  // Button 2 (+): Smooth Animated Add Part Dropdown
  function openAddPartMenu(e, btnEl) {
    if (e) e.stopPropagation();
    playClickSound();
    const dd = document.getElementById('addPartDropdown');
    document.getElementById('variationsDropdown').classList.remove('open');

    if (dd.classList.contains('open')) {
      dd.classList.remove('open');
      return;
    }

    const modeKey = getActiveModeKey();
    const modeConfig = layoutState[modeKey];
    const availableParts = modeKey === 'mini'
      ? ['cover', 'trackinfo', 'visualizer', 'controls']
      : (modeKey === 'compact' ? ['cover', 'trackinfo', 'visualizer', 'controls'] : ['cover', 'trackinfo', 'visualizer', 'controls', 'lyrics']);

    dd.innerHTML = `<div class="dropdown-header">Add / Restore UI Part</div>`;

    availableParts.forEach(partKey => {
      const cfg = modeConfig[partKey] || { hidden: false };
      const item = document.createElement('button');
      item.className = 'dropdown-item';
      item.innerHTML = `
        <span>+ ${PART_NAMES[partKey]}</span>
        <span class="badge">${cfg.hidden ? 'Hidden' : 'Active'}</span>
      `;
      item.onmouseenter = playHoverSound;
      item.onclick = (ev) => {
        ev.stopPropagation();
        addOrRestorePart(partKey);
        dd.classList.remove('open');
      };
      dd.appendChild(item);
    });

    // Reset Layout Option
    const resetBtn = document.createElement('button');
    resetBtn.className = 'dropdown-item';
    resetBtn.style.borderTop = '1px solid rgba(255,255,255,0.1)';
    resetBtn.style.marginTop = '4px';
    resetBtn.innerHTML = `<span>&#x21BA; Reset ${modeKey.toUpperCase()} Layout</span>`;
    resetBtn.onmouseenter = playHoverSound;
    resetBtn.onclick = (ev) => {
      ev.stopPropagation();
      layoutState[modeKey] = defaultPartState();
      saveCustomizations();
      applyModeLayout();
      playPopSound();
      spawnPopParticles(window.innerWidth / 2, window.innerHeight / 2, true, 40);
      dd.classList.remove('open');
    };
    dd.appendChild(resetBtn);

    positionDropdown(dd, btnEl.getBoundingClientRect());
    dd.classList.add('open');
  }

  function getActivePartElement(partKey) {
    const scope = isMiniMode ? document.getElementById('miniCard') : document.getElementById('appLayout');
    return scope ? scope.querySelector(`.ui-part[data-part="${partKey}"]`) : null;
  }

  function addOrRestorePart(partKey) {
    const modeKey = getActiveModeKey();
    const cfg = layoutState[modeKey][partKey];
    if (!cfg) return;
    cfg.hidden = false;
    cfg.x = 0;
    cfg.y = 0;
    cfg.scale = 1;
    cfg.rot = 0;
    saveCustomizations();

    const el = getActivePartElement(partKey);
    if (el) {
      el.classList.remove('part-hidden', 'part-imploding');
      el.classList.add('part-spawning');
      applyModeLayout();
      setTimeout(() => {
        const r = el.getBoundingClientRect();
        const cx = r.left + r.width / 2;
        const cy = r.top + r.height / 2;
        playPopSound();
        spawnPopParticles(cx, cy, true, 42);
      }, 20);
      setTimeout(() => el.classList.remove('part-spawning'), 450);
    }
  }

  function removePartWithImplosion(partKey, el) {
    const modeKey = getActiveModeKey();
    const cfg = layoutState[modeKey][partKey];
    if (!cfg || !el) return;

    const r = el.getBoundingClientRect();
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;

    playPopSound();
    spawnPopParticles(cx, cy, true, 46);
    el.classList.add('part-imploding');

    setTimeout(() => {
      cfg.hidden = true;
      saveCustomizations();
      el.classList.remove('part-imploding');
      el.classList.add('part-hidden');
    }, 280);
  }

  // Hover 2 Buttons (3-Dots Variations + Rotate/Reset) & Wrench Drag/Rescale Setup
  function initCustomizableParts() {
    document.querySelectorAll('.ui-part').forEach(el => {
      const partKey = el.dataset.part;

      // Create 2 Blur-Fade Hover Buttons
      const hoverBar = document.createElement('div');
      hoverBar.className = 'part-hover-bar';

      // Hover Button 1: 3-Dots Variations Menu Button
      const dotsBtn = document.createElement('button');
      dotsBtn.className = 'part-hover-btn';
      dotsBtn.title = 'Part Variations';
      dotsBtn.innerHTML = `
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="5" cy="12" r="2.2"/>
          <circle cx="12" cy="12" r="2.2"/>
          <circle cx="19" cy="12" r="2.2"/>
        </svg>
      `;
      dotsBtn.onmouseenter = playHoverSound;
      dotsBtn.onclick = (e) => {
        e.stopPropagation();
        openVariationsMenu(partKey, dotsBtn);
      };

      // Hover Button 2: Rotate 15° (or Reset on Right-Click/Shift-Click)
      const rotBtn = document.createElement('button');
      rotBtn.className = 'part-hover-btn';
      rotBtn.title = 'Rotate 15° (Shift+Click to Reset)';
      rotBtn.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
      `;
      rotBtn.onmouseenter = playHoverSound;
      rotBtn.onclick = (e) => {
        e.stopPropagation();
        playClickSound();
        const modeKey = getActiveModeKey();
        const cfg = layoutState[modeKey][partKey];
        if (e.shiftKey) {
          cfg.x = 0; cfg.y = 0; cfg.scale = 1; cfg.rot = 0;
        } else {
          cfg.rot = ((cfg.rot || 0) + 15) % 360;
          if (cfg.rot > 180) cfg.rot -= 360;
        }
        saveCustomizations();
        applyModeLayout();
      };

      hoverBar.appendChild(dotsBtn);
      hoverBar.appendChild(rotBtn);
      el.appendChild(hoverBar);

      // Corner Scale Handle for Wrench Edit Mode
      const scaleHandle = document.createElement('div');
      scaleHandle.className = 'part-scale-handle';
      scaleHandle.title = 'Drag to Rescale on Grid';
      el.appendChild(scaleHandle);

      // Rescaling Interaction
      scaleHandle.addEventListener('mousedown', (e) => {
        if (!isEditMode) return;
        e.stopPropagation();
        e.preventDefault();
        playClickSound();
        const modeKey = getActiveModeKey();
        const cfg = layoutState[modeKey][partKey];
        const startX = e.clientX;
        const startY = e.clientY;
        const startScale = cfg.scale || 1;

        function onScaleMove(ev) {
          const delta = (ev.clientX - startX + ev.clientY - startY) * 0.0045;
          const rawScale = Math.max(0.45, Math.min(1.85, startScale + delta));
          // Snap scale to 0.05 increments
          cfg.scale = Math.round(rawScale * 20) / 20;
          el.style.transform = `translate3d(${cfg.x || 0}px, ${cfg.y || 0}px, 0) scale(${cfg.scale}) rotate(${cfg.rot || 0}deg)`;
        }
        function onScaleUp() {
          document.removeEventListener('mousemove', onScaleMove);
          document.removeEventListener('mouseup', onScaleUp);
          saveCustomizations();
          applyModeLayout();
        }
        document.addEventListener('mousemove', onScaleMove);
        document.addEventListener('mouseup', onScaleUp);
      });

      // Click-to-Remove or Drag-to-Move on Snapping Grid
      el.addEventListener('mousedown', (e) => {
        if (e.target.closest('.part-hover-bar, .part-scale-handle')) return;

        if (isRemoveMode) {
          e.stopPropagation();
          e.preventDefault();
          removePartWithImplosion(partKey, el);
          return;
        }

        if (!isEditMode) return;
        e.stopPropagation();
        e.preventDefault();
        playClickSound();

        const modeKey = getActiveModeKey();
        const cfg = layoutState[modeKey][partKey];
        const startX = e.clientX;
        const startY = e.clientY;
        const origX = cfg.x || 0;
        const origY = cfg.y || 0;

        el.classList.add('dragging-part');

        function onPartMove(ev) {
          const dx = ev.clientX - startX;
          const dy = ev.clientY - startY;
          // Fluid grid snapping to 12px increments
          const snappedX = Math.round((origX + dx) / GRID_SNAP) * GRID_SNAP;
          const snappedY = Math.round((origY + dy) / GRID_SNAP) * GRID_SNAP;
          if (snappedX !== cfg.x || snappedY !== cfg.y) {
            cfg.x = snappedX;
            cfg.y = snappedY;
            playHoverSound();
          }
          el.style.transform = `translate3d(${cfg.x}px, ${cfg.y}px, 0) scale(${cfg.scale || 1}) rotate(${cfg.rot || 0}deg)`;
        }

        function onPartUp() {
          document.removeEventListener('mousemove', onPartMove);
          document.removeEventListener('mouseup', onPartUp);
          el.classList.remove('dragging-part');
          saveCustomizations();
          applyModeLayout();
        }

        document.addEventListener('mousemove', onPartMove);
        document.addEventListener('mouseup', onPartUp);
      });
    });
  }

  function openVariationsMenu(partKey, btnEl) {
    playClickSound();
    const dd = document.getElementById('variationsDropdown');
    document.getElementById('addPartDropdown').classList.remove('open');

    if (dd.classList.contains('open') && dd.dataset.activePart === partKey) {
      dd.classList.remove('open');
      return;
    }
    dd.dataset.activePart = partKey;

    const options = VARIATION_CATALOG[partKey] || [];
    dd.innerHTML = `<div class="dropdown-header">${PART_NAMES[partKey]} Style</div>`;

    options.forEach(opt => {
      const item = document.createElement('button');
      const isSelected = currentVariations[partKey] === opt.id;
      item.className = 'dropdown-item' + (isSelected ? ' selected' : '');
      item.innerHTML = `
        <span>${opt.name}</span>
        <span class="badge">${isSelected ? '&#x2713;' : ''}</span>
      `;
      item.onmouseenter = playHoverSound;
      item.onclick = (ev) => {
        ev.stopPropagation();
        playPopSound();
        currentVariations[partKey] = opt.id;
        saveCustomizations();
        applyAllVariations();
        const partEl = getActivePartElement(partKey);
        if (partEl) {
          const r = partEl.getBoundingClientRect();
          spawnPopParticles(r.left + r.width / 2, r.top + r.height / 2, true, 28);
        }
        dd.classList.remove('open');
      };
      dd.appendChild(item);
    });

    positionDropdown(dd, btnEl.getBoundingClientRect());
    dd.classList.add('open');
  }

  document.addEventListener('mousedown', (e) => {
    if (!e.target.closest('.smooth-dropdown, .part-hover-bar, .secret-bar')) {
      closeAllDropdowns();
    }
  });

  setTimeout(() => {
    initCustomizableParts();
    applyAllVariations();
    applyModeLayout();
  }, 60);
"""

# Hook updateSpinningDisc() into animFrame()
html = html.replace("if (isMiniMode) {\n      drawMiniWave();\n    } else {\n      drawWave();\n    }",
                    "updateSpinningDisc();\n    if (isMiniMode) {\n      drawMiniWave();\n    } else {\n      drawWave();\n    }")

# Also call applyModeLayout() whenever mode changes (mini / compact / expanded)
html = html.replace("setTimeout(resizeCanvases, 40);", "applyModeLayout(); setTimeout(resizeCanvases, 40);")
html = html.replace("window.pywebview.api.set_mode('compact');", "window.pywebview.api.set_mode('compact'); applyModeLayout();")
html = html.replace("window.pywebview.api.set_mode('expanded');", "window.pywebview.api.set_mode('expanded'); applyModeLayout();")

# Inject custom_js before setInterval(pollBridge, 90);
html = html.replace("setInterval(pollBridge, 90);", custom_js + "\n  setInterval(pollBridge, 90);")

with open(r"C:\Users\dryde\spicy_spotify_lyrics\index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html updated successfully! Length:", len(html))
