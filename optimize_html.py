import re

path = r"C:\Users\dryde\spicy_spotify_lyrics\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace the entire script block in index.html with the optimized version
script_start = html.find("<script>")
script_end = html.find("</script>")
assert script_start != -1 and script_end != -1, "Script tags not found"

new_script = """<script>
  const LOGO_B64 = "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";
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
    audio_peak: 0.0
  };

  let activeIndex = -1;
  let userScrolling = false;
  let scrollTimer = null;
  let currentCoverUrl = "";
  let activeLayer = 'A';
  let isCompactMode = false;
  let isMiniMode = false;

  // Cached DOM elements for 60fps loop (Zero layout thrashing)
  let cachedMainChars = [];
  let cachedAdlibChars = [];
  let cachedAdlibRow = null;
  let cachedLineItem = null;

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

  // Decoupled Canvas Resizing: called ONLY on window resize, never in 60fps loop!
  function resizeCanvases() {
    const dpr = window.devicePixelRatio || 1;
    if (canvas && canvas.clientWidth > 0 && canvas.clientHeight > 0) {
      const tw = Math.round(canvas.clientWidth * dpr);
      const th = Math.round(canvas.clientHeight * dpr);
      if (canvas.width !== tw || canvas.height !== th) {
        canvas.width = tw;
        canvas.height = th;
      }
    }
    if (miniCanvas && miniCanvas.clientWidth > 0 && miniCanvas.clientHeight > 0) {
      const tw = Math.round(miniCanvas.clientWidth * dpr);
      const th = Math.round(miniCanvas.clientHeight * dpr);
      if (miniCanvas.width !== tw || miniCanvas.height !== th) {
        miniCanvas.width = tw;
        miniCanvas.height = th;
      }
    }
    if (fxCanvas) {
      fxCanvas.width = Math.round(window.innerWidth * dpr);
      fxCanvas.height = Math.round(window.innerHeight * dpr);
    }
  }
  window.addEventListener('resize', resizeCanvases);
  setTimeout(resizeCanvases, 50);

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
      gain.gain.setValueAtTime(0.04, now);
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

  // Smooth Window Dragging Throttled with rAF (Zero IPC queue congestion)
  let isDraggingWindow = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let pendingDx = 0;
  let pendingDy = 0;
  let moveRafId = null;

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
    pendingDx += (e.screenX - dragStartX);
    pendingDy += (e.screenY - dragStartY);
    dragStartX = e.screenX;
    dragStartY = e.screenY;

    if (!moveRafId) {
      moveRafId = requestAnimationFrame(() => {
        if (pendingDx !== 0 || pendingDy !== 0) {
          if (window.pywebview && window.pywebview.api && window.pywebview.api.move_window) {
            window.pywebview.api.move_window(pendingDx, pendingDy);
          }
          pendingDx = 0;
          pendingDy = 0;
        }
        moveRafId = null;
      });
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

  // Main Wave Visualizer (Lightweight, No Layout Thrashing, No Software ShadowBlur)
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
    setTimeout(resizeCanvases, 40);
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.set_mode(isMiniMode ? 'mini' : 'restore').then(newMode => {
        if (newMode === 'compact') {
          isCompactMode = true;
          document.body.classList.add('no-lyrics-mode');
        } else if (newMode === 'expanded') {
          isCompactMode = false;
          document.body.classList.remove('no-lyrics-mode');
        }
        setTimeout(resizeCanvases, 40);
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

  let lastSecFloor = -1;
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
    resizeCanvases();
  }

  // Animation Loop (60fps Optimized, Zero querySelector or reflows)
  let localPos = 0;
  function animFrame() {
    const now = performance.now() / 1000;
    if (state.is_playing) {
      localPos = Math.max(0, Math.min(state.duration, state.base_pos + (now - state.base_time)));
    } else {
      localPos = Math.max(0, Math.min(state.duration, state.base_pos));
    }

    const curSec = Math.floor(localPos);
    if (curSec !== lastSecFloor) {
      lastSecFloor = curSec;
      timeCurrent.textContent = formatTime(localPos);
      timeDuration.textContent = formatTime(state.duration);
    }

    if (isMiniMode) {
      drawMiniWave();
    } else {
      drawWave();
    }

    // Karaoke Engine with Cached Character Elements
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
            el.querySelectorAll('.karaoke-char').forEach(c => {
              c.classList.remove('singing');
              c.classList.add('lit');
            });
          } else if (idx === activeIdx) {
            el.className = 'lyric-line active';
            if (adlib) adlib.classList.remove('revealed');
            el.querySelectorAll('.karaoke-char').forEach(c => {
              c.classList.remove('singing', 'lit');
            });
          } else {
            el.className = 'lyric-line';
            if (adlib) adlib.classList.remove('revealed');
            el.querySelectorAll('.karaoke-char').forEach(c => {
              c.classList.remove('singing', 'lit');
            });
          }
        });

        // Cache active characters once per line transition
        if (activeIdx >= 0) {
          const activeLineEl = lyricsScroller.querySelector(`.lyric-line[data-index="${activeIdx}"]`);
          if (activeLineEl) {
            cachedLineItem = state.lyrics[activeIdx];
            cachedMainChars = Array.from(activeLineEl.querySelectorAll('.main-char'));
            cachedAdlibChars = Array.from(activeLineEl.querySelectorAll('.adlib-char'));
            cachedAdlibRow = activeLineEl.querySelector('.adlib-lyric-row');

            if (!userScrolling) {
              const scrollerH = lyricsScroller.clientHeight;
              const targetTop = activeLineEl.offsetTop;
              const targetH = activeLineEl.clientHeight;
              lyricsScroller.scrollTo({
                top: targetTop - (scrollerH / 2) + (targetH / 2),
                behavior: 'smooth'
              });
            }
          }
        } else {
          cachedMainChars = [];
          cachedAdlibChars = [];
          cachedAdlibRow = null;
          cachedLineItem = null;
        }
      }

      // Animate Cached Characters (Direct array access, zero DOM querying!)
      if (activeIdx >= 0 && cachedLineItem) {
        const lineDur = Math.max(0.5, cachedLineItem.endTime - cachedLineItem.time);
        const lineElapsed = Math.max(0, localPos - cachedLineItem.time);
        const ratio = Math.min(1.0, lineElapsed / lineDur);

        if (cachedAdlibChars.length === 0) {
          const currentProgress = ratio * cachedMainChars.length;
          cachedMainChars.forEach((charEl, cIdx) => {
            if (cIdx < Math.floor(currentProgress)) {
              charEl.classList.remove('singing');
              charEl.classList.add('lit');
            } else if (cIdx === Math.floor(currentProgress)) {
              charEl.classList.remove('lit');
              charEl.classList.add('singing');
            } else {
              charEl.classList.remove('singing', 'lit');
            }
          });
        } else if (cachedMainChars.length === 0) {
          if (cachedAdlibRow) cachedAdlibRow.classList.add('revealed');
          const currentProgress = ratio * cachedAdlibChars.length;
          cachedAdlibChars.forEach((charEl, cIdx) => {
            if (cIdx < Math.floor(currentProgress)) {
              charEl.classList.remove('singing');
              charEl.classList.add('lit');
            } else if (cIdx === Math.floor(currentProgress)) {
              charEl.classList.remove('lit');
              charEl.classList.add('singing');
            } else {
              charEl.classList.remove('singing', 'lit');
            }
          });
        } else {
          // Main lyrics progress across first 58% of line duration
          const mainProgress = Math.min(1.0, ratio / 0.58) * cachedMainChars.length;
          cachedMainChars.forEach((charEl, cIdx) => {
            if (cIdx < Math.floor(mainProgress)) {
              charEl.classList.remove('singing');
              charEl.classList.add('lit');
            } else if (cIdx === Math.floor(mainProgress) && ratio < 0.58) {
              charEl.classList.remove('lit');
              charEl.classList.add('singing');
            } else {
              if (ratio >= 0.58) {
                charEl.classList.remove('singing');
                charEl.classList.add('lit');
              } else {
                charEl.classList.remove('singing', 'lit');
              }
            }
          });

          // Ad-lib in parentheses: slides in from left, unblurs and fades in at ratio 0.45, lights up slowly from 0.50 to 0.95
          if (ratio >= 0.45) {
            if (cachedAdlibRow) cachedAdlibRow.classList.add('revealed');
            const adlibRatio = Math.min(1.0, Math.max(0.0, (ratio - 0.50) / 0.45));
            const adlibProgress = adlibRatio * cachedAdlibChars.length;
            cachedAdlibChars.forEach((charEl, cIdx) => {
              if (cIdx < Math.floor(adlibProgress)) {
                charEl.classList.remove('singing');
                charEl.classList.add('lit');
              } else if (cIdx === Math.floor(adlibProgress) && adlibRatio < 1.0) {
                charEl.classList.remove('lit');
                charEl.classList.add('singing');
              } else {
                if (adlibRatio >= 1.0) {
                  charEl.classList.remove('singing');
                  charEl.classList.add('lit');
                } else {
                  charEl.classList.remove('singing', 'lit');
                }
              }
            });
          } else {
            if (cachedAdlibRow) cachedAdlibRow.classList.remove('revealed');
            cachedAdlibChars.forEach(charEl => {
              charEl.classList.remove('singing', 'lit');
            });
          }
        }
      }
    }

    requestAnimationFrame(animFrame);
  }
  requestAnimationFrame(animFrame);

  // Highly Efficient Telemetry Polling (80 bytes per poll, ZERO base64 serialization!)
  function pollBridge() {
    if (window.pywebview && window.pywebview.api) {
      const api = window.pywebview.api;
      if (api.get_telemetry) {
        api.get_telemetry().then(t => {
          if (!t) return;
          state.is_playing = t.is_playing;
          state.duration = t.dur || 180;
          state.audio_peak = t.peak || 0.0;

          const currentCalculated = state.base_pos + (state.is_playing ? (performance.now() / 1000 - state.base_time) : 0);
          if (Math.abs(currentCalculated - t.pos) > 0.6) {
            state.base_pos = t.pos;
            state.base_time = performance.now() / 1000;
          }

          if (state.is_playing) {
            playBtn.classList.add('is-playing');
            miniPlayBtn.classList.add('is-playing');
          } else {
            playBtn.classList.remove('is-playing');
            miniPlayBtn.classList.remove('is-playing');
          }

          if (t.version !== state.version) {
            state.version = t.version;
            // Fetch heavy payload ONLY once per song change!
            api.get_track_details().then(d => {
              if (!d) return;
              applyTrackDetails(d);
            });
          }
        }).catch(err => {});
      } else if (api.get_state) {
        // Fallback for compatibility
        api.get_state().then(s => {
          if (!s) return;
          if (s.version !== state.version) {
            state.version = s.version;
            applyTrackDetails({
              title: s.current_track,
              artist: s.current_artist,
              cover: s.album_cover,
              lyrics: s.lyrics
            });
          }
        });
      }
    }
  }

  function applyTrackDetails(d) {
    const trackChanged = (state.current_track !== d.title || state.current_artist !== d.artist);
    state.current_track = d.title;
    state.current_artist = d.artist;
    state.album_cover = d.cover;
    state.lyrics = d.lyrics || [];

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

    if (d.cover && d.cover !== currentCoverUrl) {
      currentCoverUrl = d.cover;
      albumCoverImg.src = d.cover;
      miniCoverImg.src = d.cover;
      albumCoverImg.style.opacity = '1';
      miniCoverImg.style.opacity = '1';
      if (activeLayer === 'A') {
        bgLayerB.style.backgroundImage = `url("${d.cover}")`;
        bgLayerB.style.opacity = '1';
        bgLayerA.style.opacity = '0';
        activeLayer = 'B';
      } else {
        bgLayerA.style.backgroundImage = `url("${d.cover}")`;
        bgLayerA.style.opacity = '1';
        bgLayerB.style.opacity = '0';
        activeLayer = 'A';
      }
    }

    // Build Lyrics
    lyricsScroller.innerHTML = "";
    activeIndex = -1;
    cachedMainChars = [];
    cachedAdlibChars = [];
    cachedAdlibRow = null;
    cachedLineItem = null;

    if (state.lyrics && state.lyrics.length > 0) {
      state.lyrics.forEach((item, idx) => {
        const lineDiv = document.createElement('div');
        lineDiv.className = 'lyric-line';
        lineDiv.dataset.index = idx;

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

  setInterval(pollBridge, 90);
</script>"""

html = html[:script_start] + new_script + html[script_end + len("</script>"):]

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: index.html fully optimized!")
