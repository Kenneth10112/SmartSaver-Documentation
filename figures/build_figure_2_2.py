from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import html

W, H = 1500, 1550
OUT = Path(__file__).resolve().parent
png_path = OUT / "figure-2.2-iterative-waterfall.png"
svg_path = OUT / "figure-2.2-iterative-waterfall.svg"

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


def text_block(x, y, text, size=22, bold=False, italic=False, anchor="left", maxw=950, fill="black", lh=None):
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


def solid_line(pts):
    pstr = " ".join(f"{x},{y}" for x, y in pts)
    svg.append(f'<polyline points="{pstr}" fill="none" stroke="black" stroke-width="3" marker-end="url(#arrow)"/>')
    d.line(pts, fill="black", width=3, joint="curve")
    arrow_head(pts[-2], pts[-1])


def stage(y, number, title, body):
    x, w, h = 250, 1000, 190
    d.rectangle([x, y, x + w, y + h], outline="black", fill="white", width=3)
    d.rectangle([x, y, x + w, y + 50], fill="black")
    d.text((x + 18, y + 25), f"{number}. {title}", font=font(28, True), fill="white", anchor="lm")
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="3"/>')
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="50" fill="black"/>')
    svg.append(
        f'<text x="{x + 18}" y="{y + 25}" font-family="Arial, Helvetica, sans-serif" font-size="28" '
        f'font-weight="700" fill="white" dominant-baseline="middle">{html.escape(number + ". " + title)}</text>'
    )
    text_block(x + 20, y + 68, body, 22, maxw=w - 40)


# Title
text_block(W / 2, 26, "ITERATIVE WATERFALL MODEL", 42, True, anchor="middle", maxw=1440)
text_block(
    W / 2,
    82,
    "Structured phases with feedback from testing and a next-increment loop from deployment",
    20,
    italic=True,
    anchor="middle",
    maxw=1420,
)

stage(145, "1", "REQUIREMENTS ANALYSIS",
      "Scope, users, and data requirements\nFunctional and non-functional requirements\nEvaluation instruments and test criteria")
stage(385, "2", "SYSTEM DESIGN",
      "Physical and logical architecture\nData model, rule model, and interface\nHardware and firmware design")
stage(625, "3", "IMPLEMENTATION",
      "Hub firmware and ESP32-C3 modules\nDashboard, local storage, and pairing\nHistory Server design")
stage(865, "4", "TESTING",
      "Unit, integration, and system tests\nHousehold and non-household UAT\nExpert ISO/IEC 25010 review")
stage(1105, "5", "DEPLOYMENT",
      "Household pilot deployment\nCommunity session deployment\nFinal evaluation and documentation")

# Downward phase arrows
for y in (335, 575, 815, 1055):
    solid_line([(750, y), (750, y + 30)])

# Testing feedback rail
# From testing right edge to rail; then up to requirements, design, implementation.
solid_line([(1250, 960), (1360, 960), (1360, 240), (1250, 240)])
solid_line([(1360, 480), (1250, 480)])
solid_line([(1360, 720), (1250, 720)])

# Next increment loop from deployment to requirements, outside left
solid_line([(250, 1200), (120, 1200), (120, 240), (250, 240)])

# Rail captions
text_block(1300, 147, "TESTING FEEDBACK", 18, True, maxw=190)
text_block(1300, 174, "returns to any earlier phase", 16, italic=True, maxw=190)
text_block(140, 1265, "NEXT INCREMENT", 18, True, maxw=300)
text_block(140, 1292, "deployment feeds the next pass", 16, italic=True, maxw=300)

# Footer
text_block(
    W / 2,
    1400,
    "Each pass through testing may return to requirements, design, or implementation. Deployment starts the next increment.",
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
