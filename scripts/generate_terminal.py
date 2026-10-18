#!/usr/bin/env python3
"""
Enigmuz // neofetch-style animated terminal SVG generator.

Turns a portrait into colour ASCII art that "types itself" onto a terminal
window line by line, next to a neofetch-style identity panel.

Usage:
    pip install pillow
    python scripts/generate_terminal.py --image assets/avatar.png --out assets/terminal.svg
"""
import argparse
import colorsys
import html
import math

from PIL import Image, ImageOps

# dark -> dense (portrait is light-on-white, so darkness carries the detail)
RAMP = " .:-=+*#%@"

ACCENT = "#39ff14"      # matrix green
ACCENT2 = "#00e5ff"     # cyan
MUTED = "#7d8590"
TEXT = "#e6edf3"
BG = "#0d1117"
BAR = "#161b22"

INFO = [
    ("nimantha", "@", "enigmuz"),
    None,  # separator
    ("Name", "Nimantha Perera"),
    ("Alias", "Enigmuz"),
    ("Role", "Associate Engineer - DevSecOps"),
    ("Ops", "SOC · MSSP · Incident Response"),
    ("Mode", "Builder · Defender · Researcher"),
    ("Focus", "Agentic AI · Security Automation"),
    ("Kernel", "Threat Hunting · Detection Engineering"),
    ("Shell", "Python · FastAPI · React · Bash"),
    ("SIEM", "Chronicle · Sentinel · FortiSIEM"),
    ("EDR", "CrowdStrike Falcon · Stellar Cyber"),
    ("SOAR", "Shuffle · n8n · Ansible"),
    ("Cloud", "AWS · Azure · GCP · K8s · Docker"),
    ("Edu", "BSc (Hons) CN & Cyber Security — KIU"),
]
PALETTE = ["#0d1117", "#ff5555", "#39ff14", "#f1fa8c", "#00e5ff", "#bd93f9", "#ff79c6", "#e6edf3"]


def ascii_rows(path, cols, char_aspect):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    rows = int(cols * (h / w) / char_aspect)
    small = im.resize((cols, rows), Image.LANCZOS)
    gray = ImageOps.equalize(small.convert("L"))
    cx, cy, r = cols / 2, rows / 2, cols / 2 - 0.5
    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            # circular avatar mask (account for char aspect)
            dx, dy = (x + 0.5 - cx), (y + 0.5 - cy) * char_aspect
            if math.hypot(dx, dy) > r:
                line.append((" ", None))
                continue
            lum = gray.getpixel((x, y)) / 255
            dark = (1 - lum) ** 0.8
            if dark < 0.12:
                line.append((" ", None))
                continue
            ch = RAMP[min(len(RAMP) - 1, int(dark * (len(RAMP) - 1)))]
            rr, gg, bb = small.getpixel((x, y))
            hh, ss, vv = colorsys.rgb_to_hsv(rr / 255, gg / 255, bb / 255)
            if ss > 0.35 and vv > 0.35:  # keep the neon visor colours
                r2, g2, b2 = colorsys.hsv_to_rgb(hh, min(1, ss + 0.2), 1)
                col = "#%02x%02x%02x" % (int(r2 * 255), int(g2 * 255), int(b2 * 255))
            else:  # map shading onto green -> cyan
                t = min(1, dark * 1.3)
                col = ACCENT if t > 0.55 else (ACCENT2 if t > 0.25 else "#2ea043")
            line.append((ch, col))
        out.append(line)
    return out


def esc(s):
    return html.escape(s, quote=False)


def build(image, out_path, cols=50):
    fs, lh = 10, 10.6
    cw = fs * 0.6
    char_aspect = lh / cw
    art = ascii_rows(image, cols, char_aspect)

    pad, bar_h = 28, 34
    art_w = cols * cw
    info_x = pad + art_w + 36
    info_lh = 22
    width = 960
    art_h = len(art) * lh
    info_h = (len(INFO) + 4) * info_lh
    height = int(bar_h + pad + max(art_h, info_h) + pad)

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" role="img" aria-label="Enigmuz terminal">')
    p.append("""<style>
  .mono{font-family:'JetBrains Mono','Fira Code','Cascadia Code',Consolas,'Courier New',monospace}
  .art{font-size:%spx;white-space:pre}
  .k{fill:%s;font-weight:700}.v{fill:%s}.m{fill:%s}.h{fill:%s;font-weight:700}
  .fade{opacity:0;animation:in .35s ease forwards}
  @keyframes in{to{opacity:1}}
  .cur{animation:blink 1s steps(1) infinite}
  @keyframes blink{50%%{opacity:0}}
  .scan{animation:scan 6s linear infinite}
  @keyframes scan{0%%{transform:translateY(-40px)}100%%{transform:translateY(%spx)}}
</style>""" % (fs, ACCENT2, TEXT, MUTED, ACCENT, height))
    p.append(f'<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{ACCENT}" stop-opacity=".07"/></linearGradient>'
             f'<clipPath id="win"><rect width="{width}" height="{height}" rx="12"/></clipPath></defs>')
    p.append(f'<g clip-path="url(#win)">')
    p.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')
    p.append(f'<rect width="{width}" height="{bar_h}" fill="{BAR}"/>')
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{20 + i * 20}" cy="{bar_h / 2}" r="6" fill="{c}"/>')
    p.append(f'<text x="{width / 2}" y="{bar_h / 2 + 4}" text-anchor="middle" class="mono m" '
             f'font-size="12">enigmuz@sentinel: ~/neofetch</text>')

    # --- ASCII portrait, each row "typed" left->right via SMIL clip ---
    top = bar_h + pad
    t = 0.2
    for y, row in enumerate(art):
        ty = top + (y + 1) * lh
        cid = f"r{y}"
        p.append(f'<clipPath id="{cid}"><rect x="{pad}" y="{ty - lh}" width="0" height="{lh + 2}">'
                 f'<animate attributeName="width" from="0" to="{art_w}" begin="{t:.2f}s" dur="0.18s" '
                 f'fill="freeze"/></rect></clipPath>')
        spans, cur_col, buf = [], None, ""
        for ch, col in row:
            if col != cur_col and buf:
                spans.append((buf, cur_col))
                buf = ""
            cur_col = col if ch != " " else cur_col
            buf += ch
        if buf:
            spans.append((buf, cur_col))
        inner = "".join(f'<tspan fill="{c or BG}">{esc(s)}</tspan>' for s, c in spans)
        p.append(f'<text x="{pad}" y="{ty}" class="mono art" xml:space="preserve" '
                 f'clip-path="url(#{cid})">{inner}</text>')
        t += 0.045

    # --- neofetch info panel ---
    y = top + 16
    t += 0.15
    for item in INFO:
        if item is None:
            p.append(f'<text x="{info_x}" y="{y}" class="mono m fade" font-size="14" '
                     f'style="animation-delay:{t:.2f}s">{"─" * 38}</text>')
        elif len(item) == 3:
            p.append(f'<text x="{info_x}" y="{y}" class="mono fade" font-size="16" '
                     f'style="animation-delay:{t:.2f}s"><tspan class="h">{item[0]}</tspan>'
                     f'<tspan class="m">{item[1]}</tspan><tspan class="h">{item[2]}</tspan></text>')
        else:
            k, v = item
            p.append(f'<text x="{info_x}" y="{y}" class="mono fade" font-size="14" '
                     f'style="animation-delay:{t:.2f}s" xml:space="preserve">'
                     f'<tspan class="k">{esc(k):<8}</tspan><tspan class="m">: </tspan>'
                     f'<tspan class="v">{esc(v)}</tspan></text>')
        y += info_lh
        t += 0.12
    y += 6
    for i, c in enumerate(PALETTE):
        p.append(f'<rect x="{info_x + i * 30}" y="{y - 14}" width="26" height="16" rx="3" fill="{c}" '
                 f'stroke="#30363d" class="fade" style="animation-delay:{t + i * 0.05:.2f}s"/>')
    t += 0.6
    y += info_lh + 14
    cmd = "./hunt --mode agentic --scope authorized"
    p.append(f'<text x="{info_x}" y="{y}" class="mono fade" font-size="14" style="animation-delay:{t:.2f}s">'
             f'<tspan fill="{ACCENT}">❯ </tspan><tspan class="v">{esc(cmd)}</tspan>'
             f'<tspan fill="{ACCENT}" class="cur"> █</tspan></text>')

    p.append(f'<rect class="scan" x="0" y="0" width="{width}" height="40" fill="url(#sg)"/>')
    p.append("</g>")
    p.append(f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="#30363d"/>')
    p.append("</svg>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print(f"wrote {out_path} ({width}x{height}, {len(art)} art rows)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", default="assets/avatar.png")
    ap.add_argument("--out", default="assets/terminal.svg")
    ap.add_argument("--cols", type=int, default=50)
    a = ap.parse_args()
    build(a.image, a.out, a.cols)
