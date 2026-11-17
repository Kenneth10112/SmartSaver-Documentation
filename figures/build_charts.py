from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import html

OUT = Path(__file__).resolve().parent
FONT = r"C:\Windows\Fonts\arial.ttf"
FONT_B = r"C:\Windows\Fonts\arialbd.ttf"


class Chart:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.img = Image.new("RGB", (w, h), "white")
        self.d = ImageDraw.Draw(self.img)
        self.svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            '<defs><pattern id="hatch" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="12" height="12" fill="white"/><line x1="0" y1="0" x2="0" y2="12" stroke="black" stroke-width="3"/></pattern></defs>',
        ]

    def font(self, size, bold=False):
        return ImageFont.truetype(FONT_B if bold else FONT, size)

    def text(self, x, y, s, size=20, bold=False, anchor="start", fill="black"):
        f = self.font(size, bold)
        amap = {"start": "lm", "middle": "mm", "end": "rm"}
        smap = {"start": "start", "middle": "middle", "end": "end"}
        self.d.text((x, y), s, font=f, fill=fill, anchor=amap[anchor])
        self.svg.append(
            f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
            f'font-weight="{700 if bold else 400}" text-anchor="{smap[anchor]}" fill="{fill}" '
            f'dominant-baseline="middle">{html.escape(s)}</text>'
        )

    def textlines(self, x, y, lines, size=20, bold=False, anchor="start", fill="black", lh=None):
        lh = lh or int(size * 1.25)
        for i, s in enumerate(lines):
            self.text(x, y + i * lh, s, size, bold, anchor, fill)

    def rect(self, x, y, w, h, fill="white", stroke="black", width=3, hatch=False):
        if hatch:
            # SVG pattern; PNG tile with mask
            self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#hatch)" stroke="{stroke}" stroke-width="{width}"/>')
            tile = Image.new("RGB", (int(w), int(h)), "white")
            td = ImageDraw.Draw(tile)
            for k in range(-int(h), int(w) + int(h), 12):
                td.line([(k, 0), (k + int(h), int(h))], fill="black", width=3)
            mask = Image.new("L", (int(w), int(h)), 0)
            md = ImageDraw.Draw(mask)
            md.rectangle([0, 0, int(w), int(h)], fill=255)
            self.img.paste(tile, (int(x), int(y)), mask)
            self.d.rectangle([x, y, x + w, y + h], outline=stroke, width=width)
        elif fill == "none":
            self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{stroke}" stroke-width="{width}"/>')
            self.d.rectangle([x, y, x + w, y + h], outline=stroke, width=width)
        else:
            self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
            self.d.rectangle([x, y, x + w, y + h], fill=fill, outline=stroke, width=width)

    def line(self, pts, width=2, dash=False, color="black"):
        pstr = " ".join(f"{x},{y}" for x, y in pts)
        dashattr = ' stroke-dasharray="10 7"' if dash else ""
        self.svg.append(f'<polyline points="{pstr}" fill="none" stroke="{color}" stroke-width="{width}"{dashattr}/>')
        if dash:
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                L = math.hypot(x2 - x1, y2 - y1)
                if L == 0:
                    continue
                ux, uy = (x2 - x1) / L, (y2 - y1) / L
                t = 0
                while t < L:
                    a, b = t, min(t + 10, L)
                    self.d.line([(x1 + ux * a, y1 + uy * a), (x1 + ux * b, y1 + uy * b)], fill=color, width=width)
                    t += 17
        else:
            self.d.line(pts, fill=color, width=width, joint="curve")

    def save(self, name):
        self.svg.append("</svg>")
        self.img.save(OUT / f"{name}.png", "PNG")
        (OUT / f"{name}.svg").write_text("\n".join(self.svg), encoding="utf-8")
        print(name)


def frame(c, title, subtitle=""):
    c.text(c.W / 2, 42, title, 42, True, "middle")
    if subtitle:
        c.text(c.W / 2, 86, subtitle, 20, False, "middle")


# 3.1 Functional test summary
def chart_31():
    c = Chart(1600, 650)
    frame(c, "FUNCTIONAL TEST OUTCOMES", "24 test cases; 2 server-dependent cases not executed")
    x, y, w, h = 220, 220, 1160, 130
    total = 24
    passed = 22
    failed = 0
    not_tested = 2
    wp = w * passed / total
    wf = w * failed / total
    wn = w - wp - wf
    c.rect(x, y, wp, h, fill="black")
    c.rect(x + wp, y, wf, h, fill="white")
    c.rect(x + wp + wf, y, wn, h, hatch=True)
    c.text(x + wp / 2, y + h / 2, "22 passed", 26, True, "middle", "white")
    # legend
    lx, ly = 320, 430
    c.rect(lx, ly - 16, 34, 32, fill="black")
    c.text(lx + 48, ly, "Passed (22)", 21)
    c.rect(lx + 280, ly - 16, 34, 32, fill="white")
    c.text(lx + 328, ly, "Failed (0)", 21)
    c.rect(lx + 530, ly - 16, 34, 32, hatch=True)
    c.text(lx + 578, ly, "Not tested (2)", 21)
    c.text(800, 555, "The two untested cases are server-dependent, not failures.", 20, False, "middle")
    c.save("figure-3.1-functional-test-summary")


# 3.2 Non-functional summary matrix
def chart_32():
    c = Chart(1600, 850)
    frame(c, "NON-FUNCTIONAL TEST SUMMARY", "Observed checks; no numeric score")
    left, top, width = 60, 150, 1480
    row_h = 110
    cols = [0, 230, 800, 1140]
    headers = ["AREA", "CHECK", "RESULT", "LIMITATION"]
    for i, htxt in enumerate(headers):
        c.text(left + cols[i] + 12, top + 20, htxt, 22, True)
    c.line([(left, top + 42), (left + width, top + 42)], 3)
    rows = [
        ("Performance", ["Sensor update, rule evaluation,", "actuator response"], ["Responsive"], ["No quantitative benchmark"]),
        ("Security", ["Login, session, server API key"], ["Authentication passed"], ["ESP-NOW unencrypted;", "server not deployed"]),
        ("Compatibility", ["Desktop and phone-sized", "browser windows"], ["Observed"], ["No formal browser/device matrix"]),
        ("Reliability", ["Reboot, module removal,", "malformed backup"], ["Passed"], ["No long-duration soak test"]),
        ("Safety", ["Relay boot state, low-voltage load,", "connector polarity"], ["Passed"], ["Low-voltage test load only"]),
    ]
    for r, (area, check, result, limit) in enumerate(rows):
        yy = top + 42 + r * row_h
        c.line([(left, yy), (left + width, yy)], 2)
        c.text(left + 12, yy + 26, area, 21, True)
        c.textlines(left + cols[1] + 12, yy + 12, check, 18)
        c.textlines(left + cols[2] + 12, yy + 12, result, 18)
        c.textlines(left + cols[3] + 12, yy + 12, limit, 18)
    c.line([(left, top + 42 + len(rows) * row_h), (left + width, top + 42 + len(rows) * row_h)], 3)
    c.text(800, 800, "Passed means observed in the local workflow; it is not a certification.", 18, False, "middle")
    c.save("figure-3.2-nonfunctional-test-summary")


# 3.3 TAM grouped bars
def chart_33():
    c = Chart(1600, 1000)
    frame(c, "TAM CONSTRUCT MEANS BY PARTICIPANT GROUP", "4-point scale; 6 household and 20 non-household participants")
    groups = ["Feature\nprioritisation", "Perceived\nusefulness", "Perceived ease\nof use", "Attitude /\nintention", "Overall TAM"]
    hh = [3.57, 3.56, 3.44, 3.67, 3.55]
    nh = [3.27, 3.21, 3.04, 3.26, 3.19]
    x0, y0, w, h = 240, 170, 1240, 610
    ymin, ymax = 1.0, 4.0
    def yp(v): return y0 + h - (v - ymin) / (ymax - ymin) * h
    # grid/ticks
    for v in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
        yy = yp(v)
        c.line([(x0, yy), (x0 + w, yy)], 1, True)
        c.text(x0 - 18, yy, f"{v:.1f}", 18, False, "end")
    c.line([(x0, y0), (x0, y0 + h)], 3)
    c.line([(x0, y0 + h), (x0 + w, y0 + h)], 3)
    # threshold
    yt = yp(3.26)
    c.line([(x0, yt), (x0 + w, yt)], 2, True)
    gw = w / len(groups)
    bw = 72
    for i, (lab, a, b) in enumerate(zip(groups, hh, nh)):
        cx = x0 + gw * (i + 0.5)
        xa, xb = cx - bw - 8, cx + 8
        ya, yb = yp(a), yp(b)
        c.rect(xa, ya, bw, y0 + h - ya, fill="black")
        c.rect(xb, yb, bw, y0 + h - yb, hatch=True)
        c.rect(xa + bw / 2 - 34, ya - 34, 68, 24, fill="white", stroke="white", width=1)
        c.rect(xb + bw / 2 - 34, yb - 34, 68, 24, fill="white", stroke="white", width=1)
        c.text(xa + bw / 2, ya - 18, f"{a:.2f}", 18, True, "middle")
        c.text(xb + bw / 2, yb - 18, f"{b:.2f}", 18, True, "middle")
        c.textlines(cx, y0 + h + 22, lab.split("\n"), 18, True, "middle")
    # legend
    c.rect(1050, 120, 34, 30, fill="black")
    c.text(1094, 135, "Household", 20)
    c.rect(1250, 120, 34, 30, hatch=True)
    c.text(1294, 135, "Non-household", 20)
    c.text(800, 930, "Dashed line = 3.26, lower bound of Highly Acceptable.", 18, False, "middle")
    c.save("figure-3.4-tam-construct-means")


# 3.4 ISO horizontal bars
def chart_34():
    c = Chart(1600, 1000)
    frame(c, "ISO/IEC 25010 CHARACTERISTIC MEANS", "Five IT professional evaluators; 4-point scale; axis starts at 3.0")
    labels = ["Functional suitability", "Performance efficiency", "Reliability", "Usability", "Security", "Compatibility", "Maintainability", "Portability"]
    vals = [3.60, 3.52, 3.87, 3.50, 3.50, 3.60, 3.56, 3.60]
    x0, y0, w, h = 500, 170, 1000, 650
    xmin, xmax = 3.0, 4.0
    def xp(v): return x0 + (v - xmin) / (xmax - xmin) * w
    for v in [3.0, 3.2, 3.4, 3.6, 3.8, 4.0]:
        xx = xp(v)
        c.line([(xx, y0), (xx, y0 + h)], 1, True)
        c.text(xx, y0 + h + 28, f"{v:.1f}", 18, False, "middle")
    c.line([(x0, y0), (x0, y0 + h)], 3)
    c.line([(x0, y0 + h), (x0 + w, y0 + h)], 3)
    bh = 52
    for i, (lab, v) in enumerate(zip(labels, vals)):
        yy = y0 + i * (h / len(labels)) + 12
        c.text(x0 - 18, yy + bh / 2, lab, 19, False, "end")
        c.rect(x0, yy, xp(v) - x0, bh, fill="black")
        c.text(xp(v) - 10, yy + bh / 2, f"{v:.2f}", 19, True, "end", "white")
    overall = 3.59
    xo = xp(overall)
    c.line([(xo, y0 - 10), (xo, y0 + h)], 2, True)
    c.text(xo + 8, y0 - 26, "Overall 3.59", 18, False)
    c.text(800, 930, "Axis starts at 3.0 to make differences visible; all values are in the Highly Acceptable range.", 18, False, "middle")
    c.save("figure-3.5-iso25010-means")


# 3.5 Runtime comparison
def chart_35():
    c = Chart(1600, 1000)
    frame(c, "UNNECESSARY ON-TIME: MANUAL VS AUTOMATIC", "Mean of 20 paired trials; error bars show standard deviation")
    x0, y0, w, h = 240, 170, 1120, 600
    ymax = 650
    def yp(v): return y0 + h - v / ymax * h
    for v in range(0, 651, 100):
        yy = yp(v)
        c.line([(x0, yy), (x0 + w, yy)], 1, True)
        c.text(x0 - 18, yy, str(v), 18, False, "end")
    c.line([(x0, y0), (x0, y0 + h)], 3)
    c.line([(x0, y0 + h), (x0 + w, y0 + h)], 3)
    c.text(x0 - 18, y0 - 28, "seconds", 18, False, "end")
    bars = [("Manual", 544.00, 43.76, "black", False), ("Automatic", 0.97, 0.17, "white", True)]
    centers = [x0 + w * 0.32, x0 + w * 0.68]
    bw = 180
    for cx, (lab, mean, sd, fill, hatch) in zip(centers, bars):
        top = yp(mean)
        c.rect(cx - bw / 2, top, bw, y0 + h - top, fill=fill, hatch=hatch)
        # error bar
        y1, y2 = yp(mean - sd), yp(mean + sd)
        c.line([(cx, y1), (cx, y2)], 3)
        c.line([(cx - 16, y1), (cx + 16, y1)], 3)
        c.line([(cx - 16, y2), (cx + 16, y2)], 3)
        c.text(cx, y0 + h + 28, lab, 22, True, "middle")
        if mean > 5:
            c.text(cx, top + 30, f"{mean:.2f} s", 22, True, "middle", "white")
        else:
            # callout for the near-zero bar
            c.line([(cx + 20, top - 8), (cx + 150, top - 70)], 2)
            c.text(cx + 160, top - 78, f"{mean:.2f} s", 22, True, "start")
    # difference annotation
    c.rect(1060, 178, 450, 74, fill="white", stroke="white", width=1)
    c.textlines(1080, 210, ["Mean difference 543.03 s", "99.82% reduction"], 20, True)
    c.text(800, 870, "Manual = 544.00 s; automatic = 0.97 s; n = 20 paired trials.", 19, False, "middle")
    c.save("figure-3.3-runtime-comparison")


if __name__ == "__main__":
    chart_31()
    chart_32()
    chart_33()
    chart_34()
    chart_35()
