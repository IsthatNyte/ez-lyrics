import re

path = r"C:\Users\dryde\spicy_spotify_lyrics\index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update track title & artist CSS transitions
old_css = """.track-title {
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
  }"""

new_css = """.track-title {
    font-size: 19px;
    font-weight: 700;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    transition: opacity 0.35s ease, filter 0.35s ease, transform 0.35s ease;
  }
  .track-artist {
    font-size: 14px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.72);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: opacity 0.35s ease, filter 0.35s ease, transform 0.35s ease;
  }
  .text-blur-out {
    opacity: 0 !important;
    filter: blur(8px) !important;
    transform: translateY(2px) scale(0.98);
  }"""

if old_css in content:
    content = content.replace(old_css, new_css, 1)

# 2. Update mini track title & artist CSS
old_mini_css = """.mini-title {
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
  }"""

new_mini_css = """.mini-title {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
    transition: opacity 0.35s ease, filter 0.35s ease, transform 0.35s ease;
  }
  .mini-artist {
    font-size: 12px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.72);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: opacity 0.35s ease, filter 0.35s ease, transform 0.35s ease;
  }"""

if old_mini_css in content:
    content = content.replace(old_mini_css, new_mini_css, 1)

# 3. Update play-morph-btn size
old_btn_css = """.play-morph-btn {
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
  }"""

new_btn_css = """.play-morph-btn {
    width: 52px;
    height: 52px;
    background: #ffffff;
    color: #000000;
    border: none;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
  }
  .play-morph-btn:hover {
    transform: scale(1.08);
  }
  .morph-icon {
    position: absolute;
    width: 24px;
    height: 24px;
    fill: #000000;
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s ease;
  }"""

if old_btn_css in content:
    content = content.replace(old_btn_css, new_btn_css, 1)

# 4. Update mini-play-btn size
old_mini_btn_css = """.mini-play-btn {
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
  }"""

new_mini_btn_css = """.mini-play-btn {
    width: 34px;
    height: 34px;
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
    width: 17px;
    height: 17px;
  }"""

if old_mini_btn_css in content:
    content = content.replace(old_mini_btn_css, new_mini_btn_css, 1)

# 5. Play button SVGs (enlarged, rounded path and rounded pause rectangles)
content = re.sub(
    r'<button class="play-morph-btn" id="playBtn".*?</button>',
    '''<button class="play-morph-btn" id="playBtn" onclick="togglePlay()" title="Play / Pause">
              <svg class="morph-icon morph-play-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 4.5 C7 3.5 8.1 3 8.9 3.5 L19.8 10.6 C20.6 11.1 20.6 12.3 19.8 12.8 L8.9 19.9 C8.1 20.4 7 19.8 7 18.8 Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
              </svg>
              <svg class="morph-icon morph-pause-icon" viewBox="0 0 24 24" fill="currentColor">
                <rect x="5.5" y="3.5" width="4.5" height="17" rx="2.25"/>
                <rect x="14" y="3.5" width="4.5" height="17" rx="2.25"/>
              </svg>
            </button>''',
    content,
    flags=re.DOTALL
)

# 6. Mini play button SVGs
content = re.sub(
    r'<button class="mini-play-btn" id="miniPlayBtn".*?</button>',
    '''<button class="mini-play-btn" id="miniPlayBtn" onclick="togglePlay()" title="Play / Pause">
            <svg class="morph-icon morph-play-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 4.5 C7 3.5 8.1 3 8.9 3.5 L19.8 10.6 C20.6 11.1 20.6 12.3 19.8 12.8 L8.9 19.9 C8.1 20.4 7 19.8 7 18.8 Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
            </svg>
            <svg class="morph-icon morph-pause-icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="5.5" y="3.5" width="4.5" height="17" rx="2.25"/>
              <rect x="14" y="3.5" width="4.5" height="17" rx="2.25"/>
            </svg>
          </button>''',
    content,
    flags=re.DOTALL
)

# 7. DrawWave & DrawMiniWave replacement
old_wave_funcs = content[content.find("function drawWave()"):content.find("document.getElementById('vocalizerBox')")]

new_wave_funcs = """function drawWave() {
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
    const peak = state.audio_peak || 0.0;

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const waveEnvelope = 1.0 - (centerDist * 0.28);

      const freq1 = Math.sin(waveTick * 3.6 + i * 0.55);
      const freq2 = Math.cos(waveTick * 2.1 - i * 0.45);
      const osc = (freq1 * 0.5 + 0.5) * 0.5 + (freq2 * 0.5 + 0.5) * 0.5;

      let amp = 0.06;
      if (state.is_playing) {
        const dynamicPeak = Math.max(0.12, peak);
        amp = Math.min(1.0, 0.08 + (dynamicPeak * 1.55 * waveEnvelope * (0.60 + osc * 0.65)));
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

  // Mini Wave Visualizer (Pops up from bottom of mini tab)
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
    const peak = state.audio_peak || 0.0;

    for (let i = 0; i < numBars; i++) {
      const x = i * (barWidth + spacing);
      const centerDist = Math.abs(i - (numBars / 2)) / (numBars / 2);
      const env = 1.0 - (centerDist * 0.22);

      const freq1 = Math.sin(waveTick * 3.8 + i * 0.5);
      const freq2 = Math.cos(waveTick * 2.3 - i * 0.6);
      const osc = (freq1 * 0.5 + 0.5) * 0.5 + (freq2 * 0.5 + 0.5) * 0.5;

      let amp = 0.06;
      if (state.is_playing) {
        const dynamicPeak = Math.max(0.12, peak);
        amp = Math.min(1.0, 0.10 + (dynamicPeak * 1.65 * env * (0.60 + osc * 0.65)));
      }
      const barHeight = Math.max(3 * window.devicePixelRatio, Math.min(h, amp * h));

      const grad = miniCtx.createLinearGradient(0, h, 0, h - barHeight);
      grad.addColorStop(0, 'rgba(255, 255, 255, 0.25)');
      grad.addColorStop(0.5, 'rgba(255, 255, 255, 0.75)');
      grad.addColorStop(1, 'rgba(255, 255, 255, 1.0)');

      miniCtx.fillStyle = grad;
      miniCtx.shadowColor = 'rgba(255, 255, 255, 0.9)';
      miniCtx.shadowBlur = 6;

      const r = Math.min(3, barHeight / 2);
      miniCtx.beginPath();
      miniCtx.roundRect(x, h - barHeight, barWidth, barHeight, r);
      miniCtx.fill();
    }
  }

  // Seeking on Vocalizer Bar
  """

if old_wave_funcs:
    content = content.replace(old_wave_funcs, new_wave_funcs, 1)

# 8. Update toggleMiniMode
old_toggle_mini = """  function toggleMiniMode() {
    isMiniMode = !isMiniMode;
    document.body.classList.toggle('mode-mini', isMiniMode);
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.set_mode(isMiniMode ? 'mini' : 'restore');
    }
  }"""

new_toggle_mini = """  function toggleMiniMode() {
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
  }"""

if old_toggle_mini in content:
    content = content.replace(old_toggle_mini, new_toggle_mini, 1)

# 9. Update pollBridge for trackTitle and trackArtist crossfade blur
old_poll_change = """        if (s.version !== state.version) {
          state.version = s.version;
          state.current_track = s.current_track;
          state.current_artist = s.current_artist;
          state.album_cover = s.album_cover;
          state.lyrics = s.lyrics || [];

          trackTitle.textContent = state.current_track || "Spotify Ready";
          trackArtist.textContent = state.current_artist || "Play any track";
          miniTrackTitle.textContent = state.current_track || "Spotify Ready";
          miniTrackArtist.textContent = state.current_artist || "Play any track";"""

new_poll_change = """        if (s.version !== state.version) {
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
          }"""

if old_poll_change in content:
    content = content.replace(old_poll_change, new_poll_change, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: index.html updated!")
