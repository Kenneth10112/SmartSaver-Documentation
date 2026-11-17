from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import html

W, H = 1500, 1580
OUT = Path(__file__).resolve().parent
png_path = OUT / "figure-2.1-data-gathering-procedure.png"
svg_path = OUT / "figure-2.1-data-gathering-procedure.svg"

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


def text_block(x, y, text, size=22, bold=False, italic=False, anchor="left", maxw=1100, fill="black", lh=None):
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


def label(x, y, text, size=18):
    f = font(size, italic=True)
    b = d.textbbox((x, y), text, font=f, anchor="mm")
    pad = 4
    d.rectangle([b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad], fill="white")
    d.text((x, y), text, font=f, fill="black", anchor="mm")
    svg.append(
        f'<rect x="{b[0] - pad}" y="{b[1] - pad}" width="{b[2] - b[0] + 2 * pad}" height="{b[3] - b[1] + 2 * pad}" fill="white"/>'
    )
    svg.append(
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
        f'font-style="italic" text-anchor="middle" fill="black" dominant-baseline="middle">{html.escape(text)}</text>'
    )


def rotated_text(cx, cy, text, size=19):
    f = font(size, True)
    b = d.textbbox((0, 0), text, font=f)
    tw_, th_ = b[2] - b[0], b[3] - b[1]
    tmp = Image.new("RGBA", (tw_ + 10, th_ + 10), (255, 255, 255, 0))
    td = ImageDraw.Draw(tmp)
    td.text((5, 5), text, font=f, fill="black")
    tmp = tmp.rotate(90, expand=True)
    img.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)
    svg.append(
        f'<text x="{cx}" y="{cy}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
        f'font-weight="700" text-anchor="middle" fill="black" transform="rotate(-90 {cx} {cy})" '
        f'dominant-baseline="middle">{html.escape(text)}</text>'
    )


def stage(y, h, number, title, lines, separate=False):
    x, w = 160, 1180
    rect(x, y, w, h, dash=separate)
    # header strip
    d.rectangle([x, y, x + w, y + 48], fill="black")
    d.text((x + 18, y + 24), f"{number}. {title}", font=font(28, True), fill="white", anchor="lm")
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="48" fill="black"/>')
    svg.append(
        f'<text x="{x + 18}" y="{y + 24}" font-family="Arial, Helvetica, sans-serif" font-size="28" '
        f'font-weight="700" fill="white" dominant-baseline="middle">{html.escape(number + ". " + title)}</text>'
    )
    text_block(x + 20, y + 64, lines, 21, maxw=w - 40)


# Title
text_block(W / 2, 26, "DATA GATHERING PROCEDURE", 42, True, anchor="middle", maxw=1440)
text_block(
    W / 2,
    82,
    "Preparation and consent → household testing → non-household adult testing → expert evaluation → data handling",
    20,
    italic=True,
    anchor="middle",
    maxw=1420,
)

stage(145, 225, "1", "PREPARATION AND CONSENT",
      "Explain the purpose, voluntary participation, and the 18+ requirement\nSecure informed consent and assign anonymous response codes\nDisclose that the History Server is not deployed; savings items are planned, not observed")

stage(410, 225, "2", "HOUSEHOLD TESTING",
      "6 household occupants in their own homes in Bocaue, Bulacan\nEveryday rooms, appliances, and routines\n15-step guide and TAM questionnaire")

stage(675, 225, "3", "NON-HOUSEHOLD ADULT TESTING",
      "20 adults recruited from outside the household\nNeutral community setting; single guided session\n15-step guide and TAM questionnaire")

stage(940, 225, "4", "EXPERT EVALUATION — SEPARATE PANEL",
      "5 IT professionals working in the industry\nInspection, demonstration, and documentation review\n46-item ISO/IEC 25010:2023 instrument")

stage(1205, 225, "5", "DATA HANDLING",
      "Anonymize and code the responses\nCheck completeness; separate the TAM and ISO datasets\nPrepare the data for descriptive and inferential analysis")

# Flow arrows
for y1, y2 in [(370, 410), (635, 675), (900, 940), (1165, 1205)]:
    solid_line([(750, y1), (750, y2)])

label(770, 390, "consent")
label(770, 655, "next group")
label(770, 920, "separate panel")
label(770, 1185, "encoded data")

# Footer
text_block(
    W / 2,
    1495,
    "All stages used the same prototype. The History Server was not deployed, so server-side savings and analytics were not evaluated.",
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
