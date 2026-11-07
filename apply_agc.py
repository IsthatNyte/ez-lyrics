import re

path = r"C:\Users\dryde\spicy_spotify_lyrics\index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update mini-header, mini-body, and #miniWaveCanvas CSS
old_css_part = """.mini-header {
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 10px 0 10px;
    cursor: default;
  }"""

new_css_part = """.mini-header {
    position: relative;
    z-index: 2;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 10px 0 10px;
    cursor: default;
  }"""

if old_css_part in content:
    content = content.replace(old_css_part, new_css_part, 1)

old_body_css = """.mini-body {
    flex: 1;
    display: flex;
    align-items: center;
    padding: 2px 14px 6px 14px;
    gap: 14px;
    cursor: default;
  }"""

new_body_css = """.mini-body {
    position: relative;
    z-index: 2;
    flex: 1;
    display: flex;
    align-items: center;
    padding: 2px 14px 6px 14px;
    gap: 14px;
    cursor: default;
  }"""

if old_body_css in content:
    content = content.replace(old_body_css, new_body_css, 1)

old_canvas_css = """  #miniWaveCanvas {
    width: 100%;
    height: 26px;
    pointer-events: none;
    display: block;
  }"""

new_canvas_css = """  #miniWaveCanvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    display: block;
    z-index: 1;
  }"""

if old_canvas_css in content:
    content = content.replace(old_canvas_css, new_canvas_css, 1)

# 2. Update visualizer wave functions with dynamic AGC (Automatic Gain Control)
old_wave_block = content[content.find("function drawWave()"):content.find("document.getElementById('vocalizerBox')")]

new_wave_block = """let rollingVolume = 0.25;

  function getDynamicIntensity(rawPeak, isPlaying) {
    if (!isPlaying) {
      rollingVolume = 0.25;
      return 0.05;
    }
    const rate = rawPeak > rollingVolume ? 0.06 : 0.015;
    rollingVolume = rollingVolume * (1.0 - rate) + rawPeak * rate;

    // Automatic Gain Control: lowers intensity on loud tracks, boosts intensity on quiet tracks
    const safeVolume = Math.max(0.04, Math.min(0.95, rollingVolume));
    const targetGain = Math.max(0.50, Math.min(2.70, 0.36 / safeVolume));

    const dynamicPeak = Math.max(0.08, Math.min(1.0, rawPeak * targetGain));
    return dynamicPeak;
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
      const osc = (freq1 * 0.5 + 0.5) * 0.5 + (freq2 * 0.5 + 0.5) * 0.5;

      let amp = 0.06;
      if (state.is_playing) {
        amp = Math.min(0.95, 0.08 + (dynamicPeak * 1.35 * waveEnvelope * (0.55 + osc * 0.60)));
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

      const freq1 = Math.sin(waveTick * 3.8 + i * 0.5);
      const freq2 = Math.cos(waveTick * 2.3 - i * 0.6);
      const osc = (freq1 * 0.5 + 0.5) * 0.5 + (freq2 * 0.5 + 0.5) * 0.5;

      let amp = 0.05;
      if (state.is_playing) {
        // Can reach all the way up to 1.0 (top of the minimizer pill)
        amp = Math.min(1.0, 0.06 + (dynamicPeak * 1.55 * env * (0.60 + osc * 0.65)));
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
  """

if old_wave_block:
    content = content.replace(old_wave_block, new_wave_block, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: index.html updated with AGC and full-height mini visualizer!")
