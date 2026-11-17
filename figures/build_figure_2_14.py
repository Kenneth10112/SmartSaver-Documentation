from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import html

W, H = 1600, 1320
OUT = Path(__file__).resolve().parent
png_path = OUT / "figure-2.14-verification-validation-flow.png"
svg_path = OUT / "figure-2.14-verification-validation-flow.svg"

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


def text_block(x, y, text, size=18, bold=False, italic=False, anchor="left", maxw=300, lh=None, fill="black"):
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


def line(pts, dashed=False):
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


def label(x, y, text, size=16):
    f = font(size, italic=True)
    b = d.textbbox((x, y), text, font=f, anchor="mm")
    pad = 3
    d.rectangle([b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad], fill="white")
    d.text((x, y), text, font=f, fill="black", anchor="mm")
    svg.append(f'<rect x="{b[0]-pad}" y="{b[1]-pad}" width="{b[2]-b[0]+2*pad}" height="{b[3]-b[1]+2*pad}" fill="white"/>')
    svg.append(
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
        f'font-style="italic" text-anchor="middle" fill="black" dominant-baseline="middle">{html.escape(text)}</text>'
    )


def box(x, y, w, h, title, body="", header=False, dashed=False):
    d.rectangle([x, y, x + w, y + h], outline="black", fill="white", width=3)
    svg.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="3"'
        + (' stroke-dasharray="12 8"' if dashed else "")
        + "/>"
    )
    if header:
        d.rectangle([x, y, x + w, y + 42], fill="black")
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="42" fill="black"/>')
        d.text((x + 12, y + 21), title, font=font(20, True), fill="white", anchor="lm")
        svg.append(
            f'<text x="{x+12}" y="{y+21}" font-family="Arial, Helvetica, sans-serif" font-size="20" '
            f'font-weight="700" fill="white" dominant-baseline="middle">{html.escape(title)}</text>'
        )
        if body:
            text_block(x + 12, y + 52, body, 17, maxw=w - 24)
    else:
        text_block(x + 12, y + 10, title, 20, True, maxw=w - 24)
        if body:
            text_block(x + 12, y + 38, body, 17, maxw=w - 24)


# Title
text_block(W / 2, 26, "VERIFICATION AND VALIDATION FLOW", 40, True, anchor="middle", maxw=1500)
text_block(W / 2, 80, "Verification asks whether the system was built correctly; validation asks whether it meets the users’ needs.", 18, italic=True, anchor="middle", maxw=1500)

# Lane headers
d.rectangle([70, 135, 670, 180], fill="black")
svg.append('<rect x="70" y="135" width="600" height="45" fill="black"/>')
text_block(370, 146, "VERIFICATION", 24, True, anchor="middle", maxw=560, fill="white")
d.rectangle([840, 135, 1540, 180], fill="black")
svg.append('<rect x="840" y="135" width="700" height="45" fill="black"/>')
text_block(1190, 146, "VALIDATION", 24, True, anchor="middle", maxw=660, fill="white")

# Verification boxes
verify = [
    ("1. Requirements traceability", "Each function checked against a requirement"),
    ("2. Inspection", "Wiring, polarity, relay state, configuration"),
    ("3. Serial diagnostics", "Boot, pairing, sensor read, command log"),
    ("4. Unit testing", "Function-level cases with expected results"),
    ("5. Integration testing", "Hub ↔ sensor / module / dashboard / storage"),
    ("6. System testing", "Complete workflow and failure cases"),
]
for i, (title, body) in enumerate(verify):
    box(70, 200 + i * 130, 600, 110, title, body)

for i in range(5):
    line([(370, 310 + i * 130), (370, 330 + i * 130)])

# Validation user lane
user = [
    ("HOUSEHOLD SESSION", "6 occupants · representative tasks"),
    ("NON-HOUSEHOLD SESSION", "20 adults · guided tasks"),
    ("TAM ANALYSIS", "26 users · PEOU + PU"),
]
for i, (title, body) in enumerate(user):
    box(840, 200 + i * 130, 300, 110, title, body, header=True)

for i in range(2):
    line([(990, 310 + i * 130), (990, 330 + i * 130)])

box(840, 600, 300, 85, "TAM DATA", "PEOU and PU results")
line([(990, 570), (990, 600)])

# Expert lane
expert = [
    ("EXPERT INSPECTION", "5 IT professionals"),
    ("ISO/IEC 25010 RATING", "Eight quality characteristics"),
]
for i, (title, body) in enumerate(expert):
    box(1190, 200 + i * 130, 350, 110, title, body, header=True)

line([(1365, 310), (1365, 330)])
box(1190, 470, 350, 85, "ISO DATA", "Quality ratings")
line([(1365, 440), (1365, 470)])

# Defect log
box(200, 1030, 600, 145, "DEFECT LOG / PASS–FAIL", "Failed cases return to the originating phase for correction.\nRegression repeats unit and integration testing.", header=True)

# Defect rail from unit, integration, system
line([(720, 665), (720, 1030)])
line([(670, 665), (720, 665)])
line([(670, 795), (720, 795)])
line([(670, 925), (720, 925)])
label(735, 845, "failed cases")

# Correction and regression
line([(200, 1102), (30, 1102), (30, 255), (70, 255)])
label(70, 1118, "correction")
line([(800, 1102), (800, 1102), (800, 620), (670, 620)])
line([(800, 750), (670, 750)])
label(815, 1000, "regression")

# Footer
text_block(W / 2, 1225, "Verification evidence: pass/fail record and defect list.  Validation evidence: TAM data and ISO ratings.", 17, italic=True, anchor="middle", maxw=1500)

svg.append("</svg>")
img.save(png_path, "PNG")
svg_path.write_text("\n".join(svg), encoding="utf-8")
print(png_path)
print(svg_path)
