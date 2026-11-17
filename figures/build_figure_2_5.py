from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import html

W, H = 1600, 1280
OUT = Path(__file__).resolve().parent
png_path = OUT / "figure-2.5-entity-relationship-diagram.png"
svg_path = OUT / "figure-2.5-entity-relationship-diagram.svg"

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


def text_at(x, y, text, size=18, bold=False, italic=False, anchor="left", fill="black"):
    f = font(size, bold, italic)
    amap = {"left": "lm", "right": "rm", "middle": "mm"}
    smap = {"left": "start", "right": "end", "middle": "middle"}
    d.text((x, y), text, font=f, fill=fill, anchor=amap.get(anchor, anchor))
    svg.append(
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
        f'font-weight="{700 if bold else 400}" font-style="{"italic" if italic else "normal"}" '
        f'text-anchor="{smap.get(anchor, "start")}" fill="{fill}" dominant-baseline="middle">{html.escape(text)}</text>'
    )


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


def entity(x, y, w, h, title, attrs):
    d.rectangle([x, y, x + w, y + h], outline="black", fill="white", width=3)
    d.rectangle([x, y, x + w, y + 44], fill="black")
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="3"/>')
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="44" fill="black"/>')
    text_at(x + w / 2, y + 22, title, 22, True, anchor="middle", fill="white")
    for i, attr in enumerate(attrs):
        yy = y + 60 + i * 28
        prefix = ""
        rest = attr
        if attr.startswith("PK "):
            prefix, rest = "PK", attr[3:]
        elif attr.startswith("FK "):
            prefix, rest = "FK", attr[3:]
        if prefix:
            text_at(x + 12, yy, prefix, 16, True)
            text_at(x + 50, yy, rest, 20)
        else:
            text_at(x + 12, yy, rest, 20)


def line(pts):
    pstr = " ".join(f"{x},{y}" for x, y in pts)
    svg.append(f'<polyline points="{pstr}" fill="none" stroke="black" stroke-width="3"/>')
    d.line(pts, fill="black", width=3, joint="curve")


def one_mark(p, toward):
    # short perpendicular tick near the "one" end
    x, y = p
    dx, dy = toward[0] - x, toward[1] - y
    L = math.hypot(dx, dy)
    if L == 0:
        return
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    x += ux * 8
    y += uy * 8
    d.line([(x - px * 8, y - py * 8), (x + px * 8, y + py * 8)], fill="black", width=3)
    svg.append(f'<line x1="{x-px*8}" y1="{y-py*8}" x2="{x+px*8}" y2="{y+py*8}" stroke="black" stroke-width="3"/>')


def crow_foot(p, fromp):
    x, y = p
    dx, dy = x - fromp[0], y - fromp[1]
    L = math.hypot(dx, dy)
    if L == 0:
        return
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    # three prongs opening toward the entity
    for k in (-1, 0, 1):
        ex = x - ux * 14 + px * 10 * k
        ey = y - uy * 14 + py * 10 * k
        d.line([(x, y), (ex, ey)], fill="black", width=3)
        svg.append(f'<line x1="{x}" y1="{y}" x2="{ex}" y2="{ey}" stroke="black" stroke-width="3"/>')


def relation(pts, text, start_card="1", end_card="N", label_pos=None):
    line(pts)
    one_mark(pts[0], pts[1])
    if end_card == "N":
        crow_foot(pts[-1], pts[-2])
    text_at(pts[0][0] + (12 if pts[0][0] < pts[1][0] else -12), pts[0][1] - 12, start_card, 15, True,
            anchor="left" if pts[0][0] < pts[1][0] else "right")
    text_at(pts[-1][0] + (-12 if pts[-1][0] > pts[-2][0] else 12), pts[-1][1] - 12, end_card, 15, True,
            anchor="right" if pts[-1][0] > pts[-2][0] else "left")
    if label_pos:
        label(label_pos[0], label_pos[1], text, 18)


# Title
text_at(W / 2, 34, "ENTITY RELATIONSHIP DIAGRAM", 40, True, anchor="middle")
text_at(W / 2, 82, "Logical data model for the Hub and the planned History Server", 19, italic=True, anchor="middle")

# Entities
entity(60, 160, 340, 200, "DEVICE", ["PK device_id", "MAC address", "mod_id", "module_type", "last_seen"])
entity(630, 160, 340, 250, "PART", ["PK part_id", "FK device_id", "kind", "capability", "display_name", "enabled"])
entity(1200, 160, 340, 250, "RULE", ["PK rule_id", "FK trigger_part_id", "FK action_part_id", "priority", "enabled"])
entity(60, 480, 340, 200, "READING", ["PK reading_id", "FK part_id", "value", "timestamp"])
entity(630, 480, 340, 200, "TOPOLOGY", ["PK topology_id", "FK device_id", "FK part_id", "change_type", "timestamp"])
entity(1200, 480, 340, 220, "SETTINGS", ["PK settings_id", "time_zone", "tariff", "baseline", "buzzer", "UI preference"])
entity(1140, 780, 400, 230, "DERIVED SAVINGS", ["PK savings_id", "FK part_id", "FK settings_id", "runtime", "energy", "cost"])

# Relationships
relation([(400, 270), (630, 270)], "exposes", "1", "0..1", (515, 252))
relation([(630, 350), (520, 350), (520, 580), (400, 580)], "has", "1", "N", (520, 455))
relation([(970, 240), (1200, 240)], "trigger", "1", "N", (1085, 222))
relation([(970, 320), (1200, 320)], "action", "1", "N", (1085, 302))
relation([(800, 410), (800, 480)], "appears in", "1", "N", (820, 445))
relation([(60, 300), (30, 300), (30, 750), (560, 750), (560, 580), (630, 580)], "topology", "1", "N", (400, 733))
relation([(900, 380), (1000, 380), (1000, 830), (1140, 830)], "derives", "1", "N", (1030, 815))
relation([(1370, 700), (1370, 780)], "uses", "1", "N", (1390, 740))

# Planned note
text_at(1160, 1022, "Planned; not deployed.", 18, italic=True)

# Legend
ly = 1090
text_at(60, ly, "PK", 17, True)
text_at(100, ly, "primary key", 17)
text_at(250, ly, "FK", 17, True)
text_at(290, ly, "foreign key", 17)
text_at(470, ly, "1", 17, True)
text_at(490, ly, "one", 17)
text_at(590, ly, "N", 17, True)
text_at(610, ly, "many", 17)
text_at(730, ly, "0..1", 17, True)
text_at(780, ly, "optional one", 17)

text_at(W / 2, 1180, "Derived Savings is a planned reporting entity; local Hub records remain the operational source.", 17, italic=True, anchor="middle")

svg.append("</svg>")
img.save(png_path, "PNG")
svg_path.write_text("\n".join(svg), encoding="utf-8")
print(png_path)
print(svg_path)
