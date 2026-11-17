from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import html

W, H = 1500, 2100
OUT = Path(__file__).resolve().parent
png_path = OUT / "figure-1.1-conceptual-framework.png"
svg_path = OUT / "figure-1.1-conceptual-framework.svg"

FONT = r"C:\Windows\Fonts\arial.ttf"
FONT_B = r"C:\Windows\Fonts\arialbd.ttf"
FONT_I = r"C:\Windows\Fonts\ariali.ttf"

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#000"/></marker></defs>',
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


def text_block(x, y, text, size=22, bold=False, italic=False, anchor="left", maxw=500, fill="black", lh=None):
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
            d.text((x, yy), line, font=f, fill=fill, anchor="ma")
            svg.append(
                f'<text x="{x}" y="{yy}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
                f'font-weight="{700 if bold else 400}" font-style="{"italic" if italic else "normal"}" '
                f'text-anchor="middle" fill="{fill}" dominant-baseline="hanging">{html.escape(line)}</text>'
            )
        else:
            d.text((x, yy), line, font=f, fill=fill)
            svg.append(
                f'<text x="{x}" y="{yy}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
                f'font-weight="{700 if bold else 400}" font-style="{"italic" if italic else "normal"}" '
                f'fill="{fill}" dominant-baseline="hanging">{html.escape(line)}</text>'
            )
    return len(lines) * lh


def rect(x, y, w, h, dash=False):
    d.rectangle([x, y, x + w, y + h], outline="black", fill="white", width=3)
    svg.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="3"'
        + (' stroke-dasharray="12 8"' if dash else "")
        + "/>"
    )


def header(x, y, w, h, label):
    d.rectangle([x, y, x + w, y + h], fill="black")
    d.text((x + w / 2, y + h / 2), label, font=font(30, True), fill="white", anchor="mm")
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="black" stroke="black" stroke-width="3"/>')
    svg.append(
        f'<text x="{x + w / 2}" y="{y + h / 2}" font-family="Arial, Helvetica, sans-serif" font-size="30" '
        f'font-weight="700" text-anchor="middle" fill="white" dominant-baseline="middle">{html.escape(label)}</text>'
    )


def arrow_head(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    ang = math.atan2(y2 - y1, x2 - x1)
    length, width = 18, 9
    bx = x2 - length * math.cos(ang)
    by = y2 - length * math.sin(ang)
    left = (bx + width * math.sin(ang), by - width * math.cos(ang))
    right = (bx - width * math.sin(ang), by + width * math.cos(ang))
    d.polygon([(x2, y2), left, right], fill="black")
    svg.append(f'<polygon points="{x2},{y2} {left[0]},{left[1]} {right[0]},{right[1]}" fill="black"/>')


def dashed_line(pts):
    pstr = " ".join(f"{x},{y}" for x, y in pts)
    svg.append(
        f'<polyline points="{pstr}" fill="none" stroke="black" stroke-width="3" '
        'stroke-dasharray="12 8" marker-end="url(#arrow)"/>'
    )
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
    arrow_head(pts[-2], pts[-1])


def solid_line(pts):
    pstr = " ".join(f"{x},{y}" for x, y in pts)
    svg.append(f'<polyline points="{pstr}" fill="none" stroke="black" stroke-width="3" marker-end="url(#arrow)"/>')
    d.line(pts, fill="black", width=3, joint="curve")
    arrow_head(pts[-2], pts[-1])


def label(x, y, text, size=20):
    f = font(size, italic=True)
    b = d.textbbox((x, y), text, font=f, anchor="mm")
    pad = 4
    d.rectangle([b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad], fill="white")
    d.text((x, y), text, font=f, fill="black", anchor="mm")
    svg.append(
        f'<rect x="{b[0] - pad}" y="{b[1] - pad}" width="{b[2] - b[0] + 2 * pad}" '
        f'height="{b[3] - b[1] + 2 * pad}" fill="white"/>'
    )
    svg.append(
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
        f'font-style="italic" text-anchor="middle" fill="black" dominant-baseline="middle">{html.escape(text)}</text>'
    )


# Title
text_block(W / 2, 28, "SMARTSAVER CONCEPTUAL FRAMEWORK", 42, True, anchor="middle", maxw=1440)
text_block(
    W / 2,
    86,
    "Input–Process–Output–Feedback model for local household sensing, management, and automated control",
    22,
    italic=True,
    anchor="middle",
    maxw=1420,
)

# Input panel
PY, PH = 130, 450
d.rectangle([50, PY, 1450, PY + PH], outline="black", fill="white", width=3)
svg.append(f'<rect x="50" y="{PY}" width="1400" height="{PH}" fill="white" stroke="black" stroke-width="3"/>')
header(50, PY, 1400, 50, "INPUT")

rect(70, 195, 430, 250)
text_block(84, 207, "SENSING", 26, True, maxw=402)
text_block(84, 245, "Occupancy — wired RCWL + wireless RCWL-0516\nClimate — DHT11\nLight — LM393\nTime — DS3231 RTC", 21, maxw=400)

rect(530, 195, 370, 250)
text_block(544, 207, "DEVICE STATE", 26, True, maxw=342)
text_block(544, 245, "Relay and buzzer state reports\nWireless module last-seen", 21, maxw=338)

rect(930, 195, 500, 250)
text_block(944, 207, "HOUSEHOLD INTENT", 26, True, maxw=472)
text_block(944, 245, "Rule configuration and priority\nDevice names\nManual override commands", 21, maxw=468)

rect(70, 465, 1360, 95, dash=True)
text_block(84, 476, "PLANNED REPORTING INPUTS", 22, True, maxw=1330)
text_block(84, 510, "Power ratings · baseline · tariff  —  server-side only; not part of the local control loop", 18, maxw=1330)

# Input -> process
solid_line([(750, 580), (750, 660)])
label(765, 620, "data")

# Process panel
PY2, PH2 = 660, 570
d.rectangle([50, PY2, 1450, PY2 + PH2], outline="black", fill="white", width=3)
svg.append(f'<rect x="50" y="{PY2}" width="1400" height="{PH2}" fill="white" stroke="black" stroke-width="3"/>')
header(50, PY2, 1400, 50, "PROCESS")

for y, h, title, body in [
    (725, 100, "TRACK", "Sensor readings · actuator state reports · module last-seen"),
    (835, 100, "MONITOR", "Freshness and staleness · offline module detection · rule context"),
    (945, 130, "DECIDE", "One trigger → one action\nPriority resolves overlap; active override suppresses automation"),
    (1085, 100, "ACT", "Relay switching · buzzer alert · wireless module command"),
]:
    rect(70, y, 1360, h)
    text_block(84, y + 10, title, 26, True, maxw=1330)
    text_block(84, y + 46, body, 21, maxw=1320)

solid_line([(750, 825), (750, 835)])
solid_line([(750, 935), (750, 945)])
solid_line([(750, 1075), (750, 1085)])
# state confirmation loop inside left margin
solid_line([(70, 1135), (55, 1135), (55, 885), (70, 885)])

# Process -> output
solid_line([(750, 1230), (750, 1310)])
label(765, 1270, "command")

# Output panel
PY3, PH3 = 1310, 390
d.rectangle([50, PY3, 1450, PY3 + PH3], outline="black", fill="white", width=3)
svg.append(f'<rect x="50" y="{PY3}" width="1400" height="{PH3}" fill="white" stroke="black" stroke-width="3"/>')
header(50, PY3, 1400, 50, "OUTPUT")

rect(70, 1375, 650, 160)
text_block(84, 1387, "OPERATIONAL OUTPUT", 26, True, maxw=622)
text_block(84, 1425, "Appliance switching\nLive dashboard state\nOverride and device status", 21, maxw=620)

rect(740, 1375, 690, 160)
text_block(754, 1387, "EVALUATION OUTPUT", 26, True, maxw=662)
text_block(754, 1425, "TAM: Perceived Ease of Use + Perceived Usefulness\nISO/IEC 25010:2023: eight quality characteristics", 21, maxw=660)

rect(70, 1550, 1360, 120, dash=True)
text_block(84, 1562, "FUTURE OUTPUT — NOT DEPLOYED", 24, True, maxw=1330)
text_block(84, 1598, "History Server · estimated savings, payback, historical analytics\nDashed: designed, not evaluated", 20, maxw=1330)

# Household
hx, hy, hw, hh = 450, 1810, 600, 100
rect(hx, hy, hw, hh)
text_block(hx + 16, hy + 10, "HOUSEHOLD OCCUPANT", 26, True, maxw=hw - 32)
text_block(hx + 16, hy + 48, "Sets rules · issues manual commands · uses dashboard", 20, maxw=hw - 32)

# Output -> household, route right edge, horizontal aligned at household centre
solid_line([(1450, 1700), (1450, 1860), (1050, 1860)])
label(1225, 1842, "dashboard state, overrides, and state confirmation")
# household -> input, left edge, same horizontal level
solid_line([(450, 1860), (25, 1860), (25, 380), (50, 380)])
label(300, 1878, "rules / manual commands")
# future server -> household, outside right and bottom
dashed_line([(1430, 1610), (1490, 1610), (1490, 2040), (750, 2040), (750, 1910)])
label(1120, 2022, "future history → rule adjustment")

# Notes
text_block(50, 590, "Bounded rationality: limited attention and memory", 18, italic=True, maxw=680)
text_block(50, 1240, "Automation lowers cognitive load", 18, italic=True, maxw=680)
text_block(50, 1710, "TAM acceptance · ISO/IEC 25010 quality", 18, italic=True, maxw=680)

# Footer
text_block(
    W / 2,
    2060,
    "Solid lines: implemented local behavior.  Dashed lines: designed but not deployed or evaluated.",
    18,
    italic=True,
    anchor="middle",
    maxw=1400,
)

svg.append("</svg>")
img.save(png_path, "PNG")
svg_path.write_text("\n".join(svg), encoding="utf-8")
print(png_path)
print(svg_path)
