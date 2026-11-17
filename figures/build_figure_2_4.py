from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import html

W, H = 1500, 1300
OUT = Path(__file__).resolve().parent
png_path = OUT / "figure-2.4-physical-architecture.png"
svg_path = OUT / "figure-2.4-physical-architecture.svg"

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


def text_block(x, y, text, size=22, bold=False, italic=False, anchor="left", maxw=300, lh=None):
    f = font(size, bold, italic)
    lines = []
    for paragraph in text.split("\n"):
        if maxw:
            lines.extend(wrap(paragraph, f, maxw))
        else:
            lines.append(paragraph)
    lh = lh or int(size * 1.28)
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


def line(pts, dashed=False, both=False):
    pstr = " ".join(f"{x},{y}" for x, y in pts)
    dash = ' stroke-dasharray="12 8"' if dashed else ""
    marker = 'marker-start="url(#arrow-both)" ' if both else ""
    svg.append(f'<polyline points="{pstr}" fill="none" stroke="black" stroke-width="3"{dash} {marker}marker-end="url(#arrow)"/>')
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
    if both:
        arrow_head(pts[1], pts[0])


def label(x, y, text, size=18):
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


def box(x, y, w, h, title, header=False, dashed=False, center=False):
    d.rectangle([x, y, x + w, y + h], outline="black", fill="white", width=3)
    svg.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="3"'
        + (' stroke-dasharray="12 8"' if dashed else "")
        + "/>"
    )
    if header:
        d.rectangle([x, y, x + w, y + 46], fill="black")
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="46" fill="black"/>')
        d.text((x + w / 2, y + 23), title, font=font(24, True), fill="white", anchor="mm")
        svg.append(
            f'<text x="{x + w / 2}" y="{y + 23}" font-family="Arial, Helvetica, sans-serif" font-size="24" '
            f'font-weight="700" text-anchor="middle" fill="white" dominant-baseline="middle">{html.escape(title)}</text>'
        )
    elif center:
        d.text((x + w / 2, y + h / 2), title, font=font(24, True), fill="black", anchor="mm")
        svg.append(
            f'<text x="{x + w / 2}" y="{y + h / 2}" font-family="Arial, Helvetica, sans-serif" font-size="24" '
            f'font-weight="700" text-anchor="middle" fill="black" dominant-baseline="middle">{html.escape(title)}</text>'
        )
    else:
        text_block(x + 12, y + 10, title, 22, True, maxw=w - 24)


# Title
text_block(W / 2, 28, "PHYSICAL ARCHITECTURE", 40, True, anchor="middle", maxw=1440)
text_block(W / 2, 84, "Hub-and-module star topology", 20, italic=True, anchor="middle", maxw=1420)

# Wired parts
box(80, 400, 320, 350, "WIRED PARTS", header=True)
parts = ["DS3231 RTC", "DHT11", "LM393", "RCWL-0516", "Buzzer"]
for i, name in enumerate(parts):
    text_block(100, 470 + i * 52, name, 22, True, maxw=280)

# Hub
box(560, 420, 380, 190, "ESP32 HUB", center=True)

# Wireless modules
box(1060, 360, 340, 150, "WIRELESS MOTION", header=True)
text_block(1076, 420, "ESP32-C3 + RCWL-0516", 21, maxw=308)
box(1060, 550, 340, 150, "WIRELESS RELAY", header=True)
text_block(1076, 610, "ESP32-C3 + Relay", 21, maxw=308)

# Router and dashboard
box(1060, 160, 240, 70, "WI-FI ROUTER", center=True)
box(1060, 255, 240, 70, "DASHBOARD", center=True)
line([(1180, 230), (1180, 255)], dashed=True)
label(1200, 242, "Wi-Fi")

# Load
box(1100, 740, 250, 70, "LOAD", center=True)

# History server
box(1040, 900, 380, 100, "HISTORY SERVER", dashed=True, center=True)

# Connections
line([(400, 525), (560, 525)], both=True)
label(480, 508, "wired")
line([(940, 455), (1060, 455)], dashed=True)
label(1020, 480, "ESP-NOW")
line([(940, 625), (1060, 625)], dashed=True)
label(1000, 610, "ESP-NOW")
line([(1225, 700), (1225, 740)])
label(1245, 720, "switched")
line([(940, 430), (980, 430), (980, 195), (1060, 195)], dashed=True)
label(990, 300, "Wi-Fi")
line([(750, 610), (750, 850), (1100, 850), (1100, 900)], dashed=True)
label(920, 835, "Internet")

# Legend
ly = 1080
d.rectangle([80, ly, 120, ly + 30], outline="black", fill="white", width=2)
svg.append(f'<rect x="80" y="{ly}" width="40" height="30" fill="white" stroke="black" stroke-width="2"/>')
text_block(130, ly + 3, "Device", 18, maxw=180)
d.line([(360, ly + 15), (440, ly + 15)], fill="black", width=3)
arrow_head((360, ly + 15), (440, ly + 15))
text_block(450, ly + 3, "Wired", 18, maxw=160)
for x in range(650, 730, 18):
    d.line([(x, ly + 15), (min(x + 12, 730), ly + 15)], fill="black", width=3)
arrow_head((650, ly + 15), (730, ly + 15))
text_block(740, ly + 3, "Wireless / optional", 18, maxw=240)

text_block(W / 2, 1160, "The Hub is the single controller and configuration point.", 18, italic=True, anchor="middle", maxw=1400)

svg.append("</svg>")
img.save(png_path, "PNG")
svg_path.write_text("\n".join(svg), encoding="utf-8")
print(png_path)
print(svg_path)
