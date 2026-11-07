import re

path = r"C:\Users\dryde\spicy_spotify_lyrics\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update CSS: remove color from .lyric-line.active, style .karaoke-char, update .adlib-lyric-row with slide-in, blur and fade
old_css_block = html[html.find(".lyric-line {"):html.find("/* Compact Centered Mode (No Lyrics Found) */")]

new_css_block = """.lyric-line {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.35;
    color: rgba(255, 255, 255, 0.32);
    cursor: pointer;
    transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1), filter 0.4s ease;
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
    transform: translateX(-24px);
    filter: blur(8px);
    transition: opacity 0.4s cubic-bezier(0.25, 1, 0.5, 1), transform 0.45s cubic-bezier(0.25, 1, 0.5, 1), filter 0.4s cubic-bezier(0.25, 1, 0.5, 1);
  }
  .adlib-lyric-row.revealed {
    opacity: 1 !important;
    transform: translateX(0px) !important;
    filter: blur(0px) !important;
  }
  .lyric-line:hover {
    color: rgba(255, 255, 255, 0.6);
  }
  .lyric-line.active {
    filter: blur(0px);
    transform: scale(1.04) translateX(4px);
  }
  .lyric-line.sung {
    filter: blur(0px);
  }
  .lyric-line.sung .karaoke-char {
    color: rgba(255, 255, 255, 0.95);
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.65);
  }

  /* Karaoke Characters - Letter-by-Letter Highlighting & Spring Bouncing */
  .karaoke-char {
    display: inline-block;
    color: rgba(255, 255, 255, 0.32);
    transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.18s ease, text-shadow 0.18s ease;
    will-change: transform;
    white-space: pre;
  }
  .karaoke-char.lit {
    transform: translateY(0px) scale(1);
    color: #ffffff !important;
    text-shadow: 0 0 12px rgba(255, 255, 255, 0.85);
  }
  .karaoke-char.singing {
    transform: translateY(-6px) scale(1.22);
    color: #ffffff !important;
    text-shadow: 0 0 20px rgba(255, 255, 255, 1), 0 0 35px rgba(255, 255, 255, 0.85);
  }

  """

if old_css_block:
    html = html.replace(old_css_block, new_css_block, 1)

# 2. Update JavaScript: fix character classes preservation, timing, and active line handling
old_karaoke_loop = html[html.find("// Karaoke Engine with Parentheses Ad-Lib Timing"):html.find("requestAnimationFrame(animFrame);")]

new_karaoke_loop = """// Karaoke Engine with Parentheses Ad-Lib Timing
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

      // Animate Active Line & Parentheses Ad-Libs Letter-by-Letter
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
            // No parentheses adlib: entire duration lights up main chars
            const currentProgress = ratio * mainChars.length;
            mainChars.forEach((charEl, cIdx) => {
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
          } else if (mainChars.length === 0) {
            // Line is purely parentheses
            if (adlibRow) adlibRow.classList.add('revealed');
            const currentProgress = ratio * adlibChars.length;
            adlibChars.forEach((charEl, cIdx) => {
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
            // Line has both main lyrics and parentheses adlib:
            // Main lyrics progress across first 58% of the line
            const mainProgress = Math.min(1.0, ratio / 0.58) * mainChars.length;
            mainChars.forEach((charEl, cIdx) => {
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

            // Parentheses adlib: reveals at ratio 0.45 (sliding in from left, unblurring, fading in)
            // Plays letter-by-letter slowly from 0.50 to 0.95 (before line ends!)
            if (ratio >= 0.45) {
              if (adlibRow) adlibRow.classList.add('revealed');
              const adlibRatio = Math.min(1.0, Math.max(0.0, (ratio - 0.50) / 0.45));
              const adlibProgress = adlibRatio * adlibChars.length;
              adlibChars.forEach((charEl, cIdx) => {
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
              if (adlibRow) adlibRow.classList.remove('revealed');
              adlibChars.forEach(charEl => {
                charEl.classList.remove('singing', 'lit');
              });
            }
          }
        }
      }
    }

    """

if old_karaoke_loop:
    html = html.replace(old_karaoke_loop, new_karaoke_loop, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: Karaoke and ad-libs updated!")
