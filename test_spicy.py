import os, re, requests, json, base64, zlib
import urllib.parse

def parse_ttml_time(t_str):
    if not t_str:
        return 0.0
    t_str = str(t_str).strip()
    if t_str.endswith('ms'):
        return round(float(t_str[:-2]) / 1000.0, 3)
    if t_str.endswith('s'):
        t_str = t_str[:-1]
    parts = t_str.split(':')
    if len(parts) == 3:
        return round(int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2]), 3)
    elif len(parts) == 2:
        return round(int(parts[0]) * 60 + float(parts[1]), 3)
    try:
        return round(float(t_str), 3)
    except Exception:
        return 0.0

def parse_ttml_to_spicy(ttml_xml):
    lines = []
    # Extract all <p ...>...</p> blocks
    p_blocks = re.findall(r'<p\b([^>]*)>([\s\S]*?)</p>', ttml_xml)
    for attrs, inner in p_blocks:
        p_begin = re.search(r'begin="([^"]+)"', attrs)
        p_end = re.search(r'end="([^"]+)"', attrs)
        agent_m = re.search(r'ttm:agent="([^"]+)"', attrs)
        start_t = parse_ttml_time(p_begin.group(1)) if p_begin else 0.0
        end_t = parse_ttml_time(p_end.group(1)) if p_end else start_t + 4.0
        opposite = bool(agent_m and agent_m.group(1) not in ('v1', 'v1000'))

        # Separate background vocal <span ttm:role="x-bg" ...>...</span>
        bg_Syllables = []
        bg_match = re.search(r'<span\b[^>]*ttm:role="x-bg"[^>]*>([\s\S]*?)</span>\s*(?:</span>|$)', inner)
        lead_html = inner
        if bg_match:
            bg_inner = bg_match.group(1)
            lead_html = inner[:bg_match.start()] + inner[bg_match.end():]
            for s_m in re.finditer(r'<span\b([^>]*)>([^<]*)</span>(\s*)', bg_inner):
                s_attrs, s_txt, trailing = s_m.group(1), s_m.group(2), s_m.group(3)
                if 'ttm:role=' in s_attrs:
                    continue
                sb = re.search(r'begin="([^"]+)"', s_attrs)
                se = re.search(r'end="([^"]+)"', s_attrs)
                bg_Syllables.append({
                    "Text": s_txt,
                    "StartTime": parse_ttml_time(sb.group(1)) if sb else start_t,
                    "EndTime": parse_ttml_time(se.group(1)) if se else end_t,
                    "IsPartOfWord": (len(trailing) == 0)
                })

        lead_Syllables = []
        for s_m in re.finditer(r'<span\b([^>]*)>([^<]*)</span>(\s*)', lead_html):
            s_attrs, s_txt, trailing = s_m.group(1), s_m.group(2), s_m.group(3)
            if 'ttm:role=' in s_attrs:
                continue
            sb = re.search(r'begin="([^"]+)"', s_attrs)
            se = re.search(r'end="([^"]+)"', s_attrs)
            if s_txt.strip():
                lead_Syllables.append({
                    "Text": s_txt,
                    "StartTime": parse_ttml_time(sb.group(1)) if sb else start_t,
                    "EndTime": parse_ttml_time(se.group(1)) if se else end_t,
                    "IsPartOfWord": (len(trailing) == 0)
                })

        if lead_Syllables:
            lead_Syllables[-1]["IsPartOfWord"] = False
        if bg_Syllables:
            bg_Syllables[-1]["IsPartOfWord"] = False

        # Reconstruct full text for compatibility
        full_text = ""
        for syl in lead_Syllables:
            full_text += syl["Text"] + ("" if syl["IsPartOfWord"] else " ")
        full_text = full_text.strip()
        if not full_text:
            plain = re.sub(r'<[^>]+>', '', lead_html).strip()
            full_text = plain

        bg_text = ""
        for syl in bg_Syllables:
            bg_text += syl["Text"] + ("" if syl["IsPartOfWord"] else " ")
        bg_text = bg_text.strip()

        if full_text or bg_text:
            lines.append({
                "time": start_t,
                "endTime": end_t,
                "text": full_text + (f" ({bg_text})" if bg_text and not bg_text.startswith("(") else (f" {bg_text}" if bg_text else "")),
                "OppositeAligned": opposite,
                "Syllables": lead_Syllables,
                "Background": bg_Syllables
            })
    return lines

r = requests.get('https://lyrics-api.boidu.dev/getLyrics?s=Blinding%20Lights&a=The%20Weeknd', timeout=5)
parsed = parse_ttml_to_spicy(r.json()['ttml'])
print('Parsed TTML lines:', len(parsed))
print('Sample line 1:', parsed[1])
