import re

path = r"C:\Users\dryde\spicy_spotify_lyrics\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update CSS for lyrics (main-lyric-row & adlib-lyric-row), fxCanvas, and mini vocalizer
old_lyric_css = """.lyric-line {
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
  }"""

new_lyric_css = """.lyric-line {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.35;
    color: rgba(255, 255, 255, 0.32);
    cursor: pointer;
    transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1), color 0.4s ease, filter 0.4s ease;
    filter: blur(0.4px);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
  .main-lyric-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
  }
  .adlib-lyric-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    font-size: 17px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.36);
    margin-top: 4px;
    opacity: 0;
    pointer-events: none;
    transform: translateY(6px);
    transition: opacity 0.32s ease, transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .adlib-lyric-row.revealed {
    opacity: 1 !important;
    transform: translateY(0px) !important;
  }"""

if old_lyric_css in html:
    html = html.replace(old_lyric_css, new_lyric_css, 1)

# Update Mini Player CSS for vocalizer box (like expanded visualizer)
old_mini_meta_css = """  .mini-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 2px;
  }"""

new_mini_meta_css = """  .mini-vocalizer-box {
    position: relative;
    width: 100%;
    height: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    margin: 1px 0;
  }
  #miniWaveCanvas {
    width: 100%;
    height: 100%;
    display: block;
    border-radius: 4px;
  }

  .mini-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 2px;
  }"""

if old_mini_meta_css in html:
    html = html.replace(old_mini_meta_css, new_mini_meta_css, 1)

# Update #fxCanvas CSS to ensure it is always visible on top
old_fx_css = """  #fxCanvas {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 99999;
    display: none;
  }"""

new_fx_css = """  #fxCanvas {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 999999;
    display: block;
  }"""

if old_fx_css in html:
    html = html.replace(old_fx_css, new_fx_css, 1)

# 2. Update Mini Player Markup: place miniWaveCanvas inside mini-meta like expanded visualizer
old_mini_markup = """        <div class=\"mini-title\" id=\"miniTrackTitle\">Track Title</div>
        <div class=\"mini-artist\" id=\"miniTrackArtist\">Artist</div>
        <div class=\"mini-controls\">"""

new_mini_markup = """        <div class=\"mini-title\" id=\"miniTrackTitle\">Track Title</div>
        <div class=\"mini-artist\" id=\"miniTrackArtist\">Artist</div>
        <div class=\"mini-vocalizer-box\" id=\"miniVocalizerBox\" title=\"Click to seek\">
          <canvas id=\"miniWaveCanvas\"></canvas>
        </div>
        <div class=\"mini-controls\">"""

if old_mini_markup in html:
    html = html.replace(old_mini_markup, new_mini_markup, 1)

# Remove the old standalone miniWaveCanvas from bottom of miniCard if present
html = re.sub(r'\s*<canvas id="miniWaveCanvas"></canvas>\s*</div>\s*<!-- MINI PLAYER CARD -->', '</div>', html)
# also remove if at end of miniCard
html = re.sub(r'\s*<canvas id="miniWaveCanvas"></canvas>\s*</div>\s*<div class="resize-grip"', '</div>\n  <div class="resize-grip"', html)

# 3. Update JavaScript in index.html for:
# - parseLyricLine with adlib under main lyrics
# - karaoke animation with adlib playing slowly near end of line
# - drawMiniWave functioning identically to drawWave
# - spawnPopParticles with high visibility and 480ms implosion
old_js_start = html.find("// Implosion & White Particle Pop Animation")
old_js_end = html.find("// Poll Backend State")

new_js = """// Implosion & White Particle Pop Animation
  let particles = [];
  function spawnPopParticles(cx, cy) {
    if (!fxCanvas || !fxCtx) return;
    fxCanvas.width = Math.round(window.innerWidth * window.devicePixelRatio);
    fxCanvas.height = Math.round(window.innerHeight * window.devicePixelRatio);
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
      fxCtx.shadowColor = '#ffffff';
      fxCtx.shadowBlur = 10;
      fxCtx.beginPath();
      fxCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      fxCtx.fill();
    }
    requestAnimationFrame(renderParticles);
  }

  function triggerImplodePop(callback) {
    playPopSound();
    const activeEl = isMiniMode ? document.getElementById('miniCard') : document.getElementById('appLayout');
    if (activeEl) {
      activeEl.classList.add('imploding');
    }
    const cx = window.innerWidth / 2;
    const cy = window.innerHeight / 2;
    spawnPopParticles(cx, cy);
    renderParticles();
    setTimeout(() => {
      if (callback) callback();
    }, 460);
  }

  function exitWindow() {
    triggerImplodePop(() => {
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.close_window();
      }
    });
  }

  function hideWindow() {
    triggerImplodePop(() => {
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.minimize_window();
      }
      const activeEl = isMiniMode ? document.getElementById('miniCard') : document.getElementById('appLayout');
      if (activeEl) {
        setTimeout(() => activeEl.classList.remove('imploding'), 450);
      }
    });
  }

  // Smooth Cross-Platform Window Dragging
  let isDraggingWindow = false;
  let dragStartX = 0;
  let dragStartY = 0;

  function makeDraggable(element) {
    if (!element) return;
    element.addEventListener('mousedown', (e) => {
      if (e.button === 0 && !e.target.closest('button, input, .win-btn, .mini-btn, .ctrl-btn, .play-morph-btn, .mini-ctrl-btn, .mini-play-btn, .resize-grip, #vocalizerBox, #miniVocalizerBox, .lyric-line')) {
        isDraggingWindow = true;
        dragStartX = e.screenX;
        dragStartY = e.screenY;
        document.addEventListener('mousemove', onDragWindowMove);
        document.addEventListener('mouseup', onDragWindowUp);
      }
    });
  }

  function onDragWindowMove(e) {
    if (!isDraggingWindow) return;
    const dx = e.screenX - dragStartX;
    const dy = e.screenY - dragStartY;
    if (dx !== 0 || dy !== 0) {
      dragStartX = e.screenX;
      dragStartY = e.screenY;
      if (window.pywebview && window.pywebview.api && window.pywebview.api.move_window) {
        window.pywebview.api.move_window(dx, dy);
      }
    }
  }

  function onDragWindowUp() {
    isDraggingWindow = false;
    document.removeEventListener('mousemove', onDragWindowMove);
    document.removeEventListener('mouseup', onDragWindowUp);
  }

  makeDraggable(document.getElementById('mainTitlebar'));
  makeDraggable(document.getElementById('miniHeader'));
  makeDraggable(document.getElementById('miniBody'));
  makeDraggable(document.getElementById('miniCard'));
  makeDraggable(document.getElementById('mainContent'));

  // Adaptive Gain Control (AGC) for Audio Visualizer
  let rollingVolume = 0.22;

  function getDynamicIntensity(rawPeak, isPlaying) {
    if (!isPlaying) {
      rollingVolume = 0.22;
      return 0.05;
    }
    const rate = rawPeak > rollingVolume ? 0.08 : 0.02;
    rollingVolume = rollingVolume * (1.0 - rate) + rawPeak * rate;

    const safeVolume = Math.max(0.04, Math.min(0.95, rollingVolume));
    const targetGain = Math.max(0.48, Math.min(2.80, 0.35 / safeVolume));

    return Math.max(0.06, Math.min(1.0, rawPeak * targetGain));
  }

  // Main Wave Visualizer with Dynamic Gain Control
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

  // Mini Wave Visualizer (Identical to Expanded Visualizer with Waveform & Progress)
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
        miniCtx.shadowColor = 'rgba(255, 255, 255, 0.95)';
        miniCtx.shadowBlur = 6;
      } else {
        miniCtx.fillStyle = 'rgba(255, 255, 255, 0.28)';
        miniCtx.shadowBlur = 0;
      }

      miniCtx.beginPath();
      miniCtx.roundRect(x, midY - barHeight / 2, barWidth, barHeight, 2.5);
      miniCtx.fill();
    }
  }

  // Seeking on Vocalizer Bars
  document.getElementById('vocalizerBox').addEventListener('click', (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const targetSec = ratio * state.duration;
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.seek(targetSec);
    }
  });

  const miniVocalizerBox = document.getElementById('miniVocalizerBox');
  if (miniVocalizerBox) {
    miniVocalizerBox.addEventListener('click', (e) => {
      const rect = e.currentTarget.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      const targetSec = ratio * state.duration;
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.seek(targetSec);
      }
    });
  }

  function toggleMiniMode() {
    isMiniMode = !isMiniMode;
    document.body.classList.toggle('mode-mini', isMiniMode);
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.set_mode(isMiniMode ? 'mini' : 'restore').then(newMode => {
        if (newMode === 'compact') {
          isCompactMode = true;
          document.body.classList.add('no-lyrics-mode');
        } else if (newMode === 'expanded') {
          isCompactMode = false;
          document.body.classList.remove('no-lyrics-mode');
        }
      });
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

    // Karaoke Engine with Parentheses Ad-Lib Timing
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
          const adlib = el.querySelector('.adlib-lyric-row');
          if (idx < activeIdx) {
            el.className = 'lyric-line sung';
            if (adlib) adlib.classList.add('revealed');
            el.querySelectorAll('.karaoke-char').forEach(c => c.className = 'karaoke-char lit');
          } else if (idx === activeIdx) {
            el.className = 'lyric-line active';
          } else {
            el.className = 'lyric-line';
            if (adlib) adlib.classList.remove('revealed');
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

      // Animate Active Line & Parentheses Ad-Libs
      if (activeIdx >= 0) {
        const activeLineEl = lyricsScroller.querySelector(`.lyric-line[data-index="${activeIdx}"]`);
        if (activeLineEl) {
          const lineItem = state.lyrics[activeIdx];
          const lineDur = Math.max(0.5, lineItem.endTime - lineItem.time);
          const lineElapsed = Math.max(0, localPos - lineItem.time);
          const ratio = Math.min(1.0, lineElapsed / lineDur);

          const mainChars = activeLineEl.querySelectorAll('.main-char');
          const adlibRow = activeLineEl.querySelector('.adlib-lyric-row');
          const adlibChars = activeLineEl.querySelectorAll('.adlib-char');

          if (adlibChars.length === 0) {
            const currentProgressIndex = ratio * mainChars.length;
            mainChars.forEach((charEl, cIdx) => {
              if (cIdx < Math.floor(currentProgressIndex)) {
                charEl.className = 'karaoke-char lit';
              } else if (cIdx === Math.floor(currentProgressIndex)) {
                charEl.className = 'karaoke-char singing';
              } else {
                charEl.className = 'karaoke-char';
              }
            });
          } else {
            // Main lyrics progress through first 65% of line duration
            const mainProgress = Math.min(1.0, ratio / 0.65) * mainChars.length;
            mainChars.forEach((charEl, cIdx) => {
              if (cIdx < Math.floor(mainProgress)) {
                charEl.className = 'karaoke-char lit';
              } else if (cIdx === Math.floor(mainProgress) && ratio < 0.65) {
                charEl.className = 'karaoke-char singing';
              } else {
                charEl.className = 'karaoke-char' + (ratio >= 0.65 ? ' lit' : '');
              }
            });

            // Ad-lib in parentheses stays invisible until 65% of line, then plays slowly to 100%
            if (ratio >= 0.62) {
              if (adlibRow) adlibRow.classList.add('revealed');
              const adlibRatio = Math.min(1.0, Math.max(0.0, (ratio - 0.65) / 0.35));
              const adlibProgress = adlibRatio * adlibChars.length;
              adlibChars.forEach((charEl, cIdx) => {
                if (cIdx < Math.floor(adlibProgress)) {
                  charEl.className = 'karaoke-char lit';
                } else if (cIdx === Math.floor(adlibProgress)) {
                  charEl.className = 'karaoke-char singing';
                } else {
                  charEl.className = 'karaoke-char';
                }
              });
            } else {
              if (adlibRow) adlibRow.classList.remove('revealed');
              adlibChars.forEach(charEl => {
                charEl.className = 'karaoke-char';
              });
            }
          }
        }
      }
    }

    requestAnimationFrame(animFrame);
  }
  requestAnimationFrame(animFrame);

  """

if old_js_start != -1 and old_js_end != -1:
    html = html[:old_js_start] + new_js + html[old_js_end:]

# 4. Update the lyrics parsing logic inside pollBridge
old_build_lyrics = """          // Build Lyrics
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
          }"""

new_build_lyrics = """          // Build Lyrics with Parentheses Ad-Lib Support
          lyricsScroller.innerHTML = "";
          activeIndex = -1;
          if (state.lyrics && state.lyrics.length > 0) {
            state.lyrics.forEach((item, idx) => {
              const lineDiv = document.createElement('div');
              lineDiv.className = 'lyric-line';
              lineDiv.dataset.index = idx;

              // Parse parentheses ad-lib
              let mainText = item.text.trim();
              let adlibText = "";
              const match = item.text.match(/^(.*?)\\s*(\\([\\s\\S]*?\\))\\s*$/);
              if (match && match[1].trim()) {
                mainText = match[1].trim();
                adlibText = match[2].trim();
              } else if (/^\\([\\s\\S]*?\\)$/.test(item.text.trim())) {
                mainText = "";
                adlibText = item.text.trim();
              }

              if (mainText) {
                const mainRow = document.createElement('div');
                mainRow.className = 'main-lyric-row';
                for (const ch of mainText) {
                  const sp = document.createElement('span');
                  sp.className = 'karaoke-char main-char';
                  sp.textContent = ch;
                  mainRow.appendChild(sp);
                }
                lineDiv.appendChild(mainRow);
              }

              if (adlibText) {
                const adlibRow = document.createElement('div');
                adlibRow.className = 'adlib-lyric-row';
                for (const ch of adlibText) {
                  const sp = document.createElement('span');
                  sp.className = 'karaoke-char adlib-char';
                  sp.textContent = ch;
                  adlibRow.appendChild(sp);
                }
                lineDiv.appendChild(adlibRow);
              }

              lineDiv.addEventListener('click', () => {
                if (window.pywebview && window.pywebview.api) {
                  window.pywebview.api.seek(item.time);
                }
              });
              lyricsScroller.appendChild(lineDiv);
            });
          }"""

if old_build_lyrics in html:
    html = html.replace(old_build_lyrics, new_build_lyrics, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: index.html updated with parentheses ad-libs, mini vocalizer, and particle fx!")
