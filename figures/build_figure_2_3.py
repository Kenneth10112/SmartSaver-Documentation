from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import html

W, H = 1500, 1550
OUT = Path(__file__).resolve().parent
png_path = OUT / "figure-2.3-logical-data-flow.png"
svg_path = OUT / "figure-2.3-logical-data-flow.svg"

FONT = r"C:\Windows\Fonts\arial.ttf"
FONT_B = r"C:\Windows\Fonts\arialbd.ttf"
FONT_I = r"C:\Windows\Fonts\ariali.ttf"

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#000"/></marker>'
    '<marker id="arrow-both" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#000"/></marker></defs>',
]


def font(size, bold=False, italic=False):
    return ImageFont.truetype(FONT_B if bold else (FONT_I if italic else FONT), size)


def tw(text, f):
    b = d.textbbox((0, 0), text, font=f)
    return b[2] - b[0]


def wrap(text, f, maxw):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if tw(test, f) <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, text, size=20, bold=False, italic=False, anchor="left", maxw=340, lh=None):
    f = font(size, bold, italic)
    lines = []
    for paragraph in text.split("\n"):
        if maxw:
            lines.extend(wrap(paragraph, f, maxw))
        else:
            lines.append(paragraph)
    lh = lh or int(size * 1.30)
    for i, line in enumerate(lines):
        yy = y + i * lh
        if anchor == "middle":
            d.text((x, yy), line, font=f, fill="black", anchor="ma")
            svg.append(
                f'<text x="{x}" y="{yy}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
                f'font-weight="{700 if bold else 400}" font-style="{"italic" if italic else "normal"}" '
                f'text-anchor="middle" fill="black" dominant-baseline="hanging">{html.escape(line)}</text>'
            )
        else:
            d.text((x, yy), line, font=f, fill="black")
            svg.append(
                f'<text x="{x}" y="{yy}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
                f'font-weight="{700 if bold else 400}" font-style="{"italic" if italic else "normal"}" '
                f'fill="black" dominant-baseline="hanging">{html.escape(line)}</text>'
            )
    return len(lines) * lh


def arrow_head(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    ang = math.atan2(y2 - y1, x2 - x1)
    length, width = 16, 8
    bx = x2 - length * math.cos(ang)
    by = y2 - length * math.sin(ang)
    left = (bx + width * math.sin(ang), by - width * math.cos(ang))
    right = (bx - width * math.sin(ang), by + width * math.cos(ang))
    d.polygon([(x2, y2), left, right], fill="black")
    svg.append(f'<polygon points="{x2},{y2} {left[0]},{left[1]} {right[0]},{right[1]}" fill="black"/>')


def solid_line(pts, dashed=False):
    pstr = " ".join(f"{x},{y}" for x, y in pts)
    dash = ' stroke-dasharray="12 8"' if dashed else ""
    svg.append(f'<polyline points="{pstr}" fill="none" stroke="black" stroke-width="3"{dash} marker-end="url(#arrow)"/>')
    if dashed:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            length = math.hypot(x2 - x1, y2 - y1)
            if length == 0:
                continue
            ux, uy = (x2 - x1) / length, (y2 - y1) / length
            t = 0
            while t < length:
                a, b = t, min(t + 12, length)
                d.line([(x1 + ux * a, y1 + uy * a), (x1 + ux * b, y1 + uy * b)], fill="black", width=3)
                t += 20
    else:
        d.line(pts, fill="black", width=3, joint="curve")
    arrow_head(pts[-2], pts[-1])


def double_line(pts):
    pstr = " ".join(f"{x},{y}" for x, y in pts)
    svg.append(f'<polyline points="{pstr}" fill="none" stroke="black" stroke-width="3" marker-start="url(#arrow-both)" marker-end="url(#arrow-both)"/>')
    d.line(pts, fill="black", width=3, joint="curve")
    arrow_head(pts[-2], pts[-1])
    arrow_head(pts[1], pts[0])


def label(x, y, text, size=17):
    f = font(size, italic=True)
    b = d.textbbox((x, y), text, font=f, anchor="mm")
    pad = 4
    d.rectangle([b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad], fill="white")
    d.text((x, y), text, font=f, fill="black", anchor="mm")
    svg.append(f'<rect x="{b[0]-pad}" y="{b[1]-pad}" width="{b[2]-b[0]+2*pad}" height="{b[3]-b[1]+2*pad}" fill="white"/>')
    svg.append(
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-style="italic" '
        f'text-anchor="middle" fill="black" dominant-baseline="middle">{html.escape(text)}</text>'
    )


def external(x, y, w, h, title, sub=""):
    d.rectangle([x, y, x + w, y + h], outline="black", fill="white", width=3)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="3"/>')
    text_block(x + 12, y + 10, title, 22, True, maxw=w - 24)
    if sub:
        text_block(x + 12, y + 40, sub, 18, maxw=w - 24)


def process(x, y, w, h, title, sub=""):
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, outline="black", fill="white", width=3)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="white" stroke="black" stroke-width="3"/>')
    text_block(x + 14, y + 12, title, 22, True, maxw=w - 28)
    if sub:
        text_block(x + 14, y + 44, sub, 18, maxw=w - 28)


def store(x, y, w, h, title):
    # open-ended data store: top and bottom lines, label inside
    d.rectangle([x, y, x + w, y + h], outline="black", fill="white", width=3)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="3"/>')
    text_block(x + 10, y + 10, title, 18, True, maxw=w - 20)


# Title
text_block(W / 2, 26, "LOGICAL DATA-FLOW DIAGRAM", 40, True, anchor="middle", maxw=1440)
text_block(
    W / 2,
    80,
    "Dashboard, Hub, wired parts, wireless modules, local stores, and the optional History Server",
    19,
    italic=True,
    anchor="middle",
    maxw=1420,
)

# External entities
external(120, 145, 310, 90, "WIRED SENSORS", "RTC · DHT11 · LM393 · RCWL-0516")
external(900, 145, 320, 90, "WIRELESS MODULES", "motion · relay · last-seen")
external(50, 470, 300, 110, "HOUSEHOLD OCCUPANT", "login · commands · rules")

# Processes
process(410, 455, 290, 150, "DASHBOARD", "UI · session · setup")
process(760, 425, 380, 220, "HUB CONTROLLER", "track · monitor · command\nrelay / buzzer / module")
process(1180, 455, 260, 150, "RULE ENGINE", "priority · override")

# Stores
store(410, 850, 220, 90, "PARTS & DEVICES")
store(650, 850, 180, 90, "RULES")
store(850, 850, 210, 90, "PREFERENCES")
store(1080, 850, 300, 90, "READINGS / LOG")

# History server
d.rectangle([1090, 1120, 1390, 1240], outline="black", fill="white", width=3)
svg.append('<rect x="1090" y="1120" width="300" height="120" fill="white" stroke="black" stroke-width="3" stroke-dasharray="12 8"/>')
text_block(1106, 1132, "HISTORY SERVER", 22, True, maxw=270)
text_block(1106, 1166, "future reporting\nnot deployed", 19, maxw=270)

# Flows: sensor readings
solid_line([(430, 195), (700, 195), (700, 425)])
label(565, 182, "sensor readings")
# module state reports
solid_line([(1060, 235), (1060, 330), (980, 330), (980, 425)])
label(1060, 300, "state reports")
# commands to module
solid_line([(940, 425), (940, 330), (1100, 330), (1100, 235)])
label(1120, 355, "commands")

# occupant <-> dashboard
double_line([(350, 525), (410, 525)])
# dashboard <-> hub
double_line([(700, 520), (760, 520)])
# hub <-> rule engine
double_line([(1140, 520), (1180, 520)])

# Hub -> local stores bus
solid_line([(950, 645), (950, 790)])
d.line([(530, 790), (1230, 790)], fill="black", width=3)
svg.append('<path d="M 530 790 L 1230 790" fill="none" stroke="black" stroke-width="3"/>')
for cx in (520, 740, 955, 1230):
    solid_line([(cx, 790), (cx, 850)])
label(950, 772, "read / write local records")

# Hub -> future server, route around right
solid_line([(1140, 620), (1450, 620), (1450, 1180), (1390, 1180)], dashed=True)
label(1270, 1085, "future: readings / transitions")

# Local-control note
text_block(120, 700, "Local control continues when the server is offline.", 17, italic=True, maxw=430)

# Legend
ly = 1335
d.rectangle([120, ly, 160, ly + 34], outline="black", fill="white", width=2)
svg.append(f'<rect x="120" y="{ly}" width="40" height="34" fill="white" stroke="black" stroke-width="2"/>')
text_block(170, ly + 5, "External entity", 17, maxw=220)
d.rounded_rectangle([430, ly, 500, ly + 34], radius=8, outline="black", fill="white", width=2)
svg.append(f'<rect x="430" y="{ly}" width="70" height="34" rx="8" fill="white" stroke="black" stroke-width="2"/>')
text_block(510, ly + 5, "Process", 17, maxw=160)
d.rectangle([670, ly, 740, ly + 34], outline="black", fill="white", width=2)
svg.append(f'<rect x="670" y="{ly}" width="70" height="34" fill="white" stroke="black" stroke-width="2"/>')
text_block(750, ly + 5, "Data store", 17, maxw=180)
d.line([(960, ly + 17), (1050, ly + 17)], fill="black", width=3)
arrow_head((960, ly + 17), (1050, ly + 17))
text_block(1060, ly + 5, "Solid: implemented", 17, maxw=180)
d.line([(1200, ly + 17), (1290, ly + 17)], fill="black", width=3, joint="curve")
for x in range(1200, 1290, 20):
    d.line([(x, ly + 17), (min(x + 12, 1290), ly + 17)], fill="black", width=3)
text_block(1300, ly + 5, "Dashed: planned", 17, maxw=180)

text_block(W / 2, 1460, "Double arrows indicate request/response. Data flow is logical; physical wiring and pin assignments are specified separately.", 17, italic=True, anchor="middle", maxw=1400)

svg.append("</svg>")
img.save(png_path, "PNG")
svg_path.write_text("\n".join(svg), encoding="utf-8")
print(png_path)
print(svg_path)
