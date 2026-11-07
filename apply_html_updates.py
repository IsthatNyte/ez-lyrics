import re

path = r"C:\Users\dryde\spicy_spotify_lyrics\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Mini-card CSS clipping fix
old_mini_css = """  body.mode-mini .mini-card {
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
  }"""

new_mini_css = """  body.mode-mini .mini-card {
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
    clip-path: inset(0 round 18px);
    -webkit-clip-path: inset(0 round 18px);
    z-index: 100;
  }"""

if old_mini_css in html:
    html = html.replace(old_mini_css, new_mini_css, 1)

# Ensure #miniWaveCanvas has border-radius: 18px;
old_mwc_css = """  #miniWaveCanvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    display: block;
    z-index: 1;
  }"""

new_mwc_css = """  #miniWaveCanvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    border-radius: 18px;
    pointer-events: none;
    display: block;
    z-index: 1;
  }

  /* Implosion Exit Animation */
  .imploding {
    animation: implodePopAnim 0.34s cubic-bezier(0.55, 0, 1, 0.45) forwards !important;
    pointer-events: none !important;
  }
  @keyframes implodePopAnim {
    0% { transform: scale(1); opacity: 1; filter: blur(0px); }
    70% { transform: scale(0.12) rotate(3deg); opacity: 0.92; filter: blur(2px); }
    100% { transform: scale(0.0); opacity: 0; filter: blur(8px); }
  }

  #fxCanvas {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 99999;
    display: none;
  }"""

if old_mwc_css in html:
    html = html.replace(old_mwc_css, new_mwc_css, 1)

# 2. Add fxCanvas in body
if '<canvas id="fxCanvas"></canvas>' not in html:
    html = html.replace('</body>', '  <canvas id="fxCanvas"></canvas>\n</body>', 1)

# 3. Update titlebar and mini buttons to use hideWindow() and exitWindow()
html = re.sub(
    r'onclick="window\.pywebview\.api\.minimize_window\(\)"',
    'onclick="hideWindow()"',
    html
)
html = re.sub(
    r'onclick="window\.pywebview\.api\.close_window\(\)"',
    'onclick="exitWindow()"',
    html
)

# 4. Update JavaScript in index.html (AudioContext sound effects, draggable move_window, implosion particles, and dynamic visualizer)
old_js_block = html[html.find("let state = {"):html.find("setInterval(pollBridge, 80);")]

new_js_block = """let state = {
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
  const fxCanvas = document.getElementById('fxCanvas');
  const fxCtx = fxCanvas ? fxCanvas.getContext('2d') : null;
  let waveTick = 0;

  // Web Audio API Synthesized Sound Effects
  let audioCtx = null;
  function getAudioCtx() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playHoverSound() {
    try {
      const actx = getAudioCtx();
      const osc = actx.createOscillator();
      const gain = actx.createGain();
      osc.type = 'sine';
      const now = actx.currentTime;
      osc.frequency.setValueAtTime(800, now);
      osc.frequency.exponentialRampToValueAtTime(1400, now + 0.032);
      gain.gain.setValueAtTime(0.045, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.032);
      osc.connect(gain);
      gain.connect(actx.destination);
      osc.start(now);
      osc.stop(now + 0.035);
    } catch (e) {}
  }

  function playClickSound() {
    try {
      const actx = getAudioCtx();
      const osc = actx.createOscillator();
      const gain = actx.createGain();
      osc.type = 'sine';
      const now = actx.currentTime;
      osc.frequency.setValueAtTime(640, now);
      osc.frequency.exponentialRampToValueAtTime(160, now + 0.065);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.065);
      osc.connect(gain);
      gain.connect(actx.destination);
      osc.start(now);
      osc.stop(now + 0.07);
    } catch (e) {}
  }

  function playPopSound() {
    try {
      const actx = getAudioCtx();
      const osc = actx.createOscillator();
      const gain = actx.createGain();
      osc.type = 'triangle';
      const now = actx.currentTime;
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(110, now + 0.095);
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.095);
      osc.connect(gain);
      gain.connect(actx.destination);
      osc.start(now);
      osc.stop(now + 0.1);
    } catch (e) {}
  }

  function bindSounds() {
    const btns = document.querySelectorAll('button, .win-btn, .mini-btn, .ctrl-btn, .play-morph-btn, .mini-ctrl-btn, .mini-play-btn');
    btns.forEach(b => {
      b.addEventListener('mouseenter', playHoverSound);
      b.addEventListener('mousedown', playClickSound);
    });
  }
  setTimeout(bindSounds, 100);

  // Implosion & White Particle Pop Animation
  let particles = [];
  function spawnPopParticles(cx, cy) {
    if (!fxCanvas || !fxCtx) return;
    fxCanvas.style.display = 'block';
    fxCanvas.width = Math.round(window.innerWidth * window.devicePixelRatio);
    fxCanvas.height = Math.round(window.innerHeight * window.devicePixelRatio);
    particles = [];
    const count = isMiniMode ? 28 : 45;
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = (3.0 + Math.random() * 8.5) * window.devicePixelRatio;
      particles.push({
        x: cx * window.devicePixelRatio,
        y: cy * window.devicePixelRatio,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: (3.0 + Math.random() * 5.0) * window.devicePixelRatio,
        alpha: 1.0,
        decay: 0.025 + Math.random() * 0.03
      });
    }
  }

  function renderParticles() {
    if (particles.length === 0) {
      if (fxCanvas) fxCanvas.style.display = 'none';
      return;
    }
    fxCtx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.94;
      p.vy *= 0.94;
      p.size = Math.max(0.1, p.size * 0.93);
      p.alpha -= p.decay;
      if (p.alpha <= 0 || p.size <= 0.2) {
        particles.splice(i, 1);
        continue;
      }
      fxCtx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
      fxCtx.shadowColor = 'rgba(255, 255, 255, 0.95)';
      fxCtx.shadowBlur = 8;
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
    }, 320);
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
        setTimeout(() => activeEl.classList.remove('imploding'), 400);
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
      if (e.button === 0 && !e.target.closest('button, input, .win-btn, .mini-btn, .ctrl-btn, .play-morph-btn, .mini-ctrl-btn, .mini-play-btn, .resize-grip, #vocalizerBox, .lyric-line')) {
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

    // Automatic Gain Control: lowers intensity on loud tracks, boosts intensity on quiet tracks
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

  // Mini Wave Visualizer (Reaches all the way up to top of minimizer pill)
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

    const numBars = 26;
    const barWidth = 9.0 * window.devicePixelRatio;
    const spacing = (w - (numBars * barWidth)) / (numBars - 1);
    const dynamicPeak = getDynamicIntensity(state.audio_peak || 0.0, state.is_playing);

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const env = 1.0 - (centerDist * 0.18);

      const freq1 = Math.sin(waveTick * 4.2 + i * 0.65);
      const freq2 = Math.cos(waveTick * 2.7 - i * 0.55);
      const osc = (freq1 * 0.5 + 0.5) * 0.55 + (freq2 * 0.5 + 0.5) * 0.45;

      let amp = 0.04;
      if (state.is_playing) {
        // Dynamic bounce up and down to the music reaching up to 1.0
        const barBounce = (0.24 + 0.76 * osc) * dynamicPeak * env;
        amp = Math.max(0.04, Math.min(1.0, barBounce * 1.55));
      }
      const barHeight = Math.max(3 * window.devicePixelRatio, Math.min(h, amp * h));

      const grad = miniCtx.createLinearGradient(0, h, 0, 0);
      grad.addColorStop(0, 'rgba(255, 255, 255, 0.12)');
      grad.addColorStop(0.35, 'rgba(255, 255, 255, 0.32)');
      grad.addColorStop(0.75, 'rgba(255, 255, 255, 0.65)');
      grad.addColorStop(1, 'rgba(255, 255, 255, 0.95)');

      miniCtx.fillStyle = grad;
      miniCtx.shadowColor = 'rgba(255, 255, 255, 0.8)';
      miniCtx.shadowBlur = 8;

      const r = Math.min(4, barHeight / 2);
      miniCtx.beginPath();
      miniCtx.roundRect(x, h - barHeight, barWidth, barHeight, r);
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
          const trackChanged = (state.current_track !== s.current_track || state.current_artist !== s.current_artist);
          state.current_track = s.current_track;
          state.current_artist = s.current_artist;
          state.album_cover = s.album_cover;
          state.lyrics = s.lyrics || [];

          if (trackChanged) {
            trackTitle.classList.add('text-blur-out');
            trackArtist.classList.add('text-blur-out');
            miniTrackTitle.classList.add('text-blur-out');
            miniTrackArtist.classList.add('text-blur-out');
            setTimeout(() => {
              trackTitle.textContent = state.current_track || "Spotify Ready";
              trackArtist.textContent = state.current_artist || "Play any track";
              miniTrackTitle.textContent = state.current_track || "Spotify Ready";
              miniTrackArtist.textContent = state.current_artist || "Play any track";
              trackTitle.classList.remove('text-blur-out');
              trackArtist.classList.remove('text-blur-out');
              miniTrackTitle.classList.remove('text-blur-out');
              miniTrackArtist.classList.remove('text-blur-out');
            }, 220);
          } else {
            trackTitle.textContent = state.current_track || "Spotify Ready";
            trackArtist.textContent = state.current_artist || "Play any track";
            miniTrackTitle.textContent = state.current_track || "Spotify Ready";
            miniTrackArtist.textContent = state.current_artist || "Play any track";
          }

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

  """

if old_js_block:
    html = html.replace(old_js_block, new_js_block, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: index.html fully updated!")
