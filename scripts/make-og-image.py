#!/usr/bin/env python3
"""
Regenerate static/og-image.png — the 1200x630 card used for og:image.

The Terminal theme ships its own static/og-image.png (an orange abstract
graphic); a file of the same name in the project's static/ wins over it.

Usage:
    python3 -m venv /tmp/og && /tmp/og/bin/pip install Pillow
    /tmp/og/bin/python scripts/make-og-image.py

Source photo is scripts/avatar.jpg, taken from the GitHub avatar:
    curl -L "https://avatars.githubusercontent.com/u/2327491?v=4&s=800" -o scripts/avatar.jpg

Menlo is used because it ships with macOS and covers Latin Extended-A, which
the theme's bundled Fira Code does not offer in a Pillow-loadable format
(woff2 only) — the shapes are close enough for a share card.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "scripts" / "avatar.jpg"
TARGET = ROOT / "static" / "og-image.png"

W, H = 1200, 630
SS = 4  # supersample factor, for a smooth circular mask

BG = "#1a1b26"
FG = "#c0caf5"
ACCENT = "#7aa2f7"
GREEN = "#9ece6a"
MUTED = "#565f89"
PANEL = "#24283b"

MENLO = "/System/Library/Fonts/Menlo.ttc"

# Must match `subtitle` in hugo.yaml, wrapped by hand to fit the text column.
SUBTITLE = ["Backend Systems,", "Automation & AI Tooling"]


def font(size, bold=False):
    return ImageFont.truetype(MENLO, size, index=1 if bold else 0)


def circle_mask(size):
    mask = Image.new("L", (size * SS, size * SS), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * SS - 1, size * SS - 1], fill=255)
    return mask.resize((size, size), Image.LANCZOS)


card = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(card)

# Header bar motif, echoing the ||||| pattern beside the site logo.
for x in range(0, W, 13):
    draw.rectangle([x, 0, x + 3, 10], fill=ACCENT)

# Circular avatar with an accent ring.
AV, RING = 330, 5
AX, AY = 96, (H - AV) // 2

avatar = Image.open(SOURCE).convert("RGB").resize((AV, AV), Image.LANCZOS)
ring = Image.new("RGB", (AV + 2 * RING, AV + 2 * RING), ACCENT)
card.paste(ring, (AX - RING, AY - RING), circle_mask(AV + 2 * RING))
card.paste(avatar, (AX, AY), circle_mask(AV))

# Text column.
TX = 500

f_logo = font(30, bold=True)
logo = "~/sneberger"
lw = draw.textlength(logo, font=f_logo)
pad_x, pad_y = 14, 9
draw.rounded_rectangle(
    [TX, 150, TX + lw + pad_x * 2, 150 + 30 + pad_y * 2], radius=6, fill=GREEN
)
draw.text((TX + pad_x, 150 + pad_y), logo, font=f_logo, fill=BG)

draw.text((TX, 250), "Šneberger Marek", font=font(56, bold=True), fill=FG)
for i, line in enumerate(SUBTITLE):
    draw.text((TX, 330 + i * 42), line, font=font(30), fill=ACCENT)

draw.line([TX, 440, TX + 120, 440], fill=PANEL, width=3)
draw.text((TX, 466), "sneberger.cz", font=font(26), fill=MUTED)

card.save(TARGET, optimize=True)
print(f"wrote {TARGET.relative_to(ROOT)} {card.size}")
