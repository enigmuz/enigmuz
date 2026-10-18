#!/usr/bin/env python3
"""
Enigmuz // animated "constellation" skill graph.

Centre node -> domain hubs -> skills & projects, drawn as a star network with
flowing data links, travelling packets, pulsing hubs and twinkling stars.

Usage:
    python scripts/generate_skill_graph.py --out assets/skill-graph.svg
Edit GRAPH below to add or remove hubs, skills and projects (project=True).
"""
import argparse
import math
import random

W, H = 980, 680
CX, CY = W / 2, H / 2 + 6
BG = "#0d1117"

# (hub label, colour, [(leaf label, is_project), ...])
GRAPH = [
    ("Agentic AI", "#bd93f9", [("MCP Agents", False), ("Albino RedTeaming", True), ("Tool Gating", False)]),
    ("RAG Systems", "#ff79c6", [("Embeddings", False), ("Vector Search", False), ("Grounded LLMs", False)]),
    ("Security Automation", "#39ff14", [("Shuffle SOAR", False), ("n8n", False), ("Ansible", False)]),
    ("Docker & DevSecOps", "#00e5ff", [("Docker", False), ("Kubernetes", False), ("Secure CI/CD", False)]),
    ("Dark Web Investigations", "#ff5555", [("Breach Monitoring", False), ("Leak-Site Intel", False), ("Telegram Intel", False)]),
    ("Threat Intel", "#f1fa8c", [("ThreatScry", True), ("Nexo Sentinel", True), ("IOC Enrichment", False)]),
    ("Threat Hunting", "#ffb86c", [("SIEM", False), ("EDR", False), ("MITRE ATT&CK", False)]),
    ("Brand Protection", "#8be9fd", [("PhantomEye", True), ("Takedowns", False), ("Visual AI", False)]),
    ("Secure App Dev", "#50fa7b", [("Uptime-E", True), ("RxGuard", True), ("TapCard", True)]),
]

HUB_RX, HUB_RY = 250, 175
LEAF_RX, LEAF_RY = 400, 278
FAN = 0.28  # radians between sibling leaves


def pt(a, rx, ry):
    return CX + rx * math.cos(a), CY + ry * math.sin(a)


def build(out):
    random.seed(7)
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'role="img" aria-label="Enigmuz skill constellation: Agentic AI, RAG systems, security automation, '
             f'Docker and DevSecOps, dark web investigations, threat intelligence, threat hunting, brand protection, '
             f'secure application development">')
    s.append("""<style>
  .f{font-family:'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace}
  .tw{animation:tw 3s ease-in-out infinite}
  @keyframes tw{0%,100%{opacity:.15}50%{opacity:.9}}
  .flow{stroke-dasharray:3 7;animation:flow 1.6s linear infinite}
  .flow2{stroke-dasharray:2 6;animation:flow 2.8s linear infinite}
  @keyframes flow{to{stroke-dashoffset:-20}}
  .in{opacity:0;animation:in .6s ease forwards}
  @keyframes in{to{opacity:1}}
  .pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}
  @keyframes pulse{0%{transform:scale(1);opacity:.7}100%{transform:scale(2.3);opacity:0}}
  .bob{animation:bob 6s ease-in-out infinite}
  @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
</style>""")
    s.append('<defs>'
             '<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="4" result="b"/>'
             '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
             '<radialGradient id="core"><stop offset="0" stop-color="#39ff14"/><stop offset=".55" stop-color="#0b3d2e"/>'
             '<stop offset="1" stop-color="#0d1117"/></radialGradient>'
             '<radialGradient id="neb" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#39ff14" stop-opacity=".10"/>'
             '<stop offset="1" stop-color="#0d1117" stop-opacity="0"/></radialGradient>'
             f'<clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath>'
             '</defs>')
    s.append('<g clip-path="url(#win)">')
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{W * 0.45}" ry="{H * 0.45}" fill="url(#neb)"/>')

    # twinkling background stars
    for _ in range(110):
        x, y = random.uniform(0, W), random.uniform(0, H)
        r = random.choice([0.6, 0.8, 1, 1.2, 1.5])
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#e6edf3" class="tw" '
                 f'style="animation-delay:{random.uniform(0, 3):.2f}s;animation-duration:{random.uniform(2, 5):.1f}s"/>')

    # orbit rings
    for rx, ry in [(HUB_RX, HUB_RY), (LEAF_RX, LEAF_RY)]:
        s.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" stroke="#30363d" '
                 f'stroke-width="1" stroke-dasharray="2 6" opacity=".7"/>')

    n = len(GRAPH)
    edges, nodes, labels, packets = [], [], [], []
    hubs = []
    for i, (hub, col, leaves) in enumerate(GRAPH):
        a = -math.pi / 2 + i * 2 * math.pi / n
        hx, hy = pt(a, HUB_RX, HUB_RY)
        hubs.append((hx, hy, col))
        d = 0.4 + i * 0.18
        edges.append(f'<line x1="{CX}" y1="{CY}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{col}" stroke-width="1.6" '
                     f'opacity=".75" class="flow in" style="animation-delay:{d:.2f}s,{d:.2f}s"/>')
        # packet travelling core -> hub
        packets.append(f'<circle r="2.6" fill="{col}" filter="url(#glow)"><animateMotion dur="{2.2 + (i % 3) * 0.5:.1f}s" '
                       f'repeatCount="indefinite" begin="{d:.2f}s" path="M{CX},{CY} L{hx:.1f},{hy:.1f}"/></circle>')
        m = len(leaves)
        for j, (leaf, proj) in enumerate(leaves):
            la = a + (j - (m - 1) / 2) * FAN
            lx, ly = pt(la, LEAF_RX, LEAF_RY)
            ld = d + 0.5 + j * 0.12
            edges.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" stroke="{col}" '
                         f'stroke-width="1" opacity=".45" class="flow2 in" style="animation-delay:{ld:.2f}s,{ld:.2f}s"/>')
            if proj:
                packets.append(f'<circle r="1.8" fill="#ffffff"><animateMotion dur="1.8s" repeatCount="indefinite" '
                               f'begin="{ld + 0.3:.2f}s" path="M{hx:.1f},{hy:.1f} L{lx:.1f},{ly:.1f}"/></circle>')
                k = 6.5  # diamond = project
                nodes.append(f'<g class="in" style="animation-delay:{ld:.2f}s">'
                             f'<path d="M{lx:.1f},{ly - k:.1f} L{lx + k:.1f},{ly:.1f} L{lx:.1f},{ly + k:.1f} '
                             f'L{lx - k:.1f},{ly:.1f}Z" fill="{BG}" stroke="{col}" stroke-width="2" filter="url(#glow)"/>'
                             f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="2" fill="#fff"/></g>')
            else:
                nodes.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="{col}" class="in" '
                             f'style="animation-delay:{ld:.2f}s" filter="url(#glow)"/>')
            # label placement: push outward from centre
            ox = math.cos(la)
            oy = math.sin(la)
            anchor = "middle" if abs(ox) < 0.02 else ("start" if ox > 0 else "end")
            tx = lx + (10 if anchor == "start" else -10 if anchor == "end" else 0)
            ty = ly + (4 if anchor != "middle" else (17 if oy > 0 else -11))
            weight = "700" if proj else "400"
            fill = "#ffffff" if proj else "#c9d1d9"
            labels.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" class="f in" font-size="11.5" '
                          f'font-weight="{weight}" fill="{fill}" style="animation-delay:{ld:.2f}s">'
                          f'{leaf.replace("&", "&amp;")}</text>')
        # hub node + pulse + label
        nodes.append(f'<g class="in" style="animation-delay:{d:.2f}s">'
                     f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="11" fill="none" stroke="{col}" stroke-width="1.5" '
                     f'class="pulse" style="animation-delay:{i * 0.27:.2f}s"/>'
                     f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="11" fill="{BG}" stroke="{col}" stroke-width="2.5" '
                     f'filter="url(#glow)"/><circle cx="{hx:.1f}" cy="{hy:.1f}" r="4.5" fill="{col}"/></g>')
        tw = len(hub) * 7.6 + 16
        by = hy + (22 if math.sin(a) >= -0.2 else -34)
        labels.append(f'<g class="in" style="animation-delay:{d:.2f}s">'
                      f'<rect x="{hx - tw / 2:.1f}" y="{by:.1f}" width="{tw:.1f}" height="19" rx="9.5" '
                      f'fill="#0d1117" fill-opacity=".9" stroke="{col}" stroke-opacity=".8"/>'
                      f'<text x="{hx:.1f}" y="{by + 13.5:.1f}" text-anchor="middle" class="f" font-size="12" '
                      f'font-weight="700" fill="{col}">{hub.replace("&", "&amp;")}</text></g>')

    # cross-links between neighbouring hubs (the "mesh")
    for i in range(n):
        (x1, y1, c1), (x2, y2, _) = hubs[i], hubs[(i + 1) % n]
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#30363d" '
                 f'stroke-width="1" class="flow2"/>')

    s += edges + packets

    # core
    s.append(f'<g class="bob"><circle cx="{CX}" cy="{CY}" r="58" fill="url(#core)" opacity=".55"/>'
             f'<circle cx="{CX}" cy="{CY}" r="44" fill="none" stroke="#39ff14" stroke-width="1.5" '
             f'stroke-dasharray="6 5" opacity=".9"><animateTransform attributeName="transform" type="rotate" '
             f'from="0 {CX} {CY}" to="360 {CX} {CY}" dur="18s" repeatCount="indefinite"/></circle>'
             f'<circle cx="{CX}" cy="{CY}" r="36" fill="{BG}" stroke="#39ff14" stroke-width="2.5" filter="url(#glow)"/>'
             f'<text x="{CX}" y="{CY - 1}" text-anchor="middle" class="f" font-size="14" font-weight="800" '
             f'fill="#39ff14">ENIGMUZ</text>'
             f'<text x="{CX}" y="{CY + 14}" text-anchor="middle" class="f" font-size="7.4" fill="#7d8590">'
             f'NIMANTHA PERERA</text></g>')
    s += nodes + labels

    # legend
    ly = H - 20
    s.append(f'<g class="f" font-size="11" fill="#7d8590">'
             f'<circle cx="24" cy="{ly - 4}" r="4" fill="#c9d1d9"/><text x="34" y="{ly}">skill</text>'
             f'<path d="M86,{ly - 10} L92,{ly - 4} L86,{ly + 2} L80,{ly - 4}Z" fill="none" stroke="#fff" stroke-width="1.6"/>'
             f'<text x="99" y="{ly}">project</text>'
             f'<text x="{W - 20}" y="{ly}" text-anchor="end">enigmuz://skill-constellation</text></g>')
    s.append("</g>")
    s.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#30363d"/>')
    s.append("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    print(f"wrote {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/skill-graph.svg")
    build(ap.parse_args().out)
