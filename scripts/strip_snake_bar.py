#!/usr/bin/env python3
"""Remove the progress bar Platane/snk draws under the grid and crop the canvas to fit."""
import re
import sys

for path in sys.argv[1:]:
    svg = open(path, encoding="utf-8").read()
    svg = re.sub(r'<rect class="u u\d+"[^>]*/>', "", svg)
    m = re.search(r'viewBox="(-?[\d.]+) (-?[\d.]+) ([\d.]+) ([\d.]+)"', svg)
    if m:
        x, y, w, h = map(float, m.groups())
        new_h = h - 32  # bar row (y=144, 12px) plus its gap
        svg = svg.replace(m.group(0), f'viewBox="{x:g} {y:g} {w:g} {new_h:g}"', 1)
        svg = re.sub(r'(<svg[^>]*?)height="[\d.]+"', rf'\g<1>height="{new_h:g}"', svg, count=1)
    open(path, "w", encoding="utf-8").write(svg)
    print("stripped", path)
