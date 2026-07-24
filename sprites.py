"""
Pixel-art sprite generator.

Every sprite is drawn on a tiny low-resolution canvas (BASE x BASE) using
simple shapes, then scaled up with NEAREST-neighbor resampling. That's what
gives the chunky "Minecraft" pixel-art look instead of smooth vector shapes.
"""

from PIL import Image, ImageDraw
import math

BASE = 40          # low-res drawing canvas (the "pixel grid")
SCALE = 6           # upscale factor -> final sprite is BASE*SCALE px
FINAL = BASE * SCALE


def _canvas():
    img = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _finish(img):
    return img.resize((FINAL, FINAL), Image.NEAREST)


def _eyes(draw, cx, ly_x, ly_y, ry_x, ry_y, mood, color="#1a1a1a"):
    """Draw a pair of eyes; mood changes their shape."""
    if mood == "grumpy":
        # angry slanted red eyes
        draw.line((ly_x - 2, ly_y - 2, ly_x + 2, ly_y + 1), fill="#c0281c", width=2)
        draw.line((ry_x + 2, ry_y - 2, ry_x - 2, ry_y + 1), fill="#c0281c", width=2)
    elif mood == "happy":
        draw.arc((ly_x - 2, ly_y - 2, ly_x + 2, ly_y + 3), 200, 340, fill=color, width=2)
        draw.arc((ry_x - 2, ry_y - 2, ry_x + 2, ry_y + 3), 200, 340, fill=color, width=2)
    elif mood == "sad":
        # droopy half-lidded eyes (opposite curve of the happy smile-eyes)
        draw.arc((ly_x - 2, ly_y - 3, ly_x + 2, ly_y + 2), 20, 160, fill=color, width=2)
        draw.arc((ry_x - 2, ry_y - 3, ry_x + 2, ry_y + 2), 20, 160, fill=color, width=2)
        # a little tear
        draw.ellipse((ly_x - 1, ly_y + 3, ly_x + 1, ly_y + 6), fill="#6fa8e0")
    else:
        draw.rectangle((ly_x - 1, ly_y - 1, ly_x + 1, ly_y + 1), fill=color)
        draw.rectangle((ry_x - 1, ry_y - 1, ry_x + 1, ry_y + 1), fill=color)


# ---------------------------------------------------------------- PIG -----
def draw_pig(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    r = 11 if baby else 15
    cx, cy = 20, 22 if baby else 21
    body = "#f3aab2"
    shade = "#dd8b95"
    ear = "#e79aa4"
    snout = "#ffc7cf"
    dark = "#7a4e52"

    # ears
    d.polygon([(cx - r + 2, cy - r + 4), (cx - r - 2, cy - r - 6), (cx - r + 8, cy - r)], fill=ear)
    d.polygon([(cx + r - 2, cy - r + 4), (cx + r + 2, cy - r - 6), (cx + r - 8, cy - r)], fill=ear)

    # body/head blob
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=body)
    d.ellipse((cx - r, cy + r // 2, cx + r, cy + r + 4), fill=shade)  # bottom shading

    # legs
    leg_w = 3 if baby else 4
    for lx in (cx - r + 4, cx - 2, cx + 1, cx + r - 6):
        d.rectangle((lx, cy + r - 3, lx + leg_w, cy + r + 5), fill=body)

    # eyes
    ex = 6 if baby else 7
    _eyes(d, cx, cx - ex, cy - 2, cx + ex, cy - 2, mood)

    # snout
    sw, sh = (7, 5) if baby else (9, 6)
    d.rounded_rectangle((cx - sw, cy + 3, cx + sw, cy + 3 + sh), radius=2, fill=snout)
    d.ellipse((cx - 3, cy + 5, cx - 1, cy + 7), fill=dark)
    d.ellipse((cx + 1, cy + 5, cx + 3, cy + 7), fill=dark)

    return img


# ------------------------------------------------------------- CHICKEN ---
def draw_chicken(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    r = 10 if baby else 14
    cx, cy = 20, 23 if baby else 21
    body = "#fbf6e8" if not baby else "#fff9e3"
    shade = "#e7dfc4"
    beak = "#f2a63d"
    comb = "#d63a2e"

    # wing shading
    d.ellipse((cx - r, cy - 2, cx + r, cy + r), fill=shade)
    # body
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=body)

    # comb
    for i, dx in enumerate((-4, 0, 4)):
        d.polygon(
            [(cx + dx - 2, cy - r + 1), (cx + dx + 2, cy - r + 1), (cx + dx, cy - r - 5)],
            fill=comb,
        )
    # wattle
    d.polygon([(cx - 2, cy + 2), (cx + 2, cy + 2), (cx, cy + 7)], fill=comb)

    # beak
    d.polygon([(cx - 5, cy - 1), (cx + 5, cy - 1), (cx, cy + 4)], fill=beak)

    # eyes
    ex = 6 if baby else 8
    _eyes(d, cx, cx - ex, cy - 6, cx + ex, cy - 6, mood)

    # legs
    leg_col = "#f2a63d"
    for lx in (cx - 5, cx + 3):
        d.line((lx, cy + r - 2, lx, cy + r + 6), fill=leg_col, width=2)
        d.line((lx - 2, cy + r + 6, lx + 2, cy + r + 6), fill=leg_col, width=1)

    return img


# ------------------------------------------------------------- CREEPER ---
# ------------------------------------------------------------- CREEPER ---
def draw_creeper(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    charging = mood == "charge"
    green = "#f2f2f2" if charging else "#5bb552"
    dark_green = "#e0524a" if charging else "#3f8a3a"
    leg_green = "#e0524a" if charging else "#39793a"
    face = "#c0281c" if charging else "#1c1c1c"

    if baby:
        w, h = 18, 15
        x0, y0 = 20 - w // 2, 27 - h
    else:
        w, h = 24, 20
        x0, y0 = 20 - w // 2, 30 - h

    # torso/head block
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=3, fill=green)
    d.rectangle((x0, y0 + h - 5, x0 + w, y0 + h), fill=dark_green)  # lower-body shading

    # four stubby legs so it reads as a standing body, not a floating head
    leg_w = 3 if baby else 4
    leg_h = 4 if baby else 6
    gap = (w - leg_w * 4) // 3
    for i in range(4):
        lx = x0 + i * (leg_w + gap)
        d.rectangle((lx, y0 + h - 1, lx + leg_w, y0 + h - 1 + leg_h), fill=leg_green)

    cx = x0 + w // 2
    fy = y0 + h // 4

    if charging:
        # wide shocked/furious eyes right before it pops
        eye = 5 if baby else 6
        d.rectangle((cx - 9, fy - 1, cx - 9 + eye, fy - 1 + eye), fill=face)
        d.rectangle((cx + 9 - eye, fy - 1, cx + 9, fy - 1 + eye), fill=face)
        d.rectangle((cx - 3, fy + eye + 4, cx + 3, fy + eye + 9), fill=face)
    elif mood == "grumpy":
        # furious red squinting eyes + frown
        d.line((cx - 7, fy - 1, cx - 2, fy + 2), fill="#c0281c", width=3)
        d.line((cx + 7, fy - 1, cx + 2, fy + 2), fill="#c0281c", width=3)
        d.line((cx - 5, fy + 9, cx + 5, fy + 9), fill=face, width=3)
    elif mood == "sad":
        # droopy eyes + downturned mouth + a little tear
        d.arc((cx - 9, fy - 1, cx - 4, fy + 5), 20, 160, fill=face, width=2)
        d.arc((cx + 4, fy - 1, cx + 9, fy + 5), 20, 160, fill=face, width=2)
        d.arc((cx - 5, fy + 9, cx + 5, fy + 14), 200, 340, fill=face, width=2)
        d.ellipse((cx - 8, fy + 5, cx - 6, fy + 8), fill="#6fa8e0")
    else:
        # big friendly round eyes (this creeper is happy, not hostile!)
        eye = 4 if baby else 5
        d.rectangle((cx - 8, fy, cx - 8 + eye, fy + eye), fill=face)
        d.rectangle((cx + 8 - eye, fy, cx + 8, fy + eye), fill=face)
        if mood == "happy":
            d.arc((cx - 6, fy + eye + 1, cx + 6, fy + eye + 9), 20, 160, fill=face, width=2)
        else:
            d.rectangle((cx - 4, fy + eye + 3, cx + 4, fy + eye + 5), fill=face)
        # little mouth notch
        d.rectangle((cx - 2, fy + eye + 6, cx + 2, fy + eye + 8), fill=face)

    return img


# ------------------------------------------------------- ZOMBIE VILLAGER -
def draw_zombie_villager(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    skin = "#6aa06a"
    skin_shade = "#578a57"
    robe = "#8a6a4c"
    robe_shade = "#6f5339"

    r = 9 if baby else 12
    cx, cy_head = 20, 16 if baby else 14

    # robe/body
    rw, rh = (14, 12) if baby else (18, 16)
    d.rounded_rectangle(
        (cx - rw // 2, cy_head + r - 3, cx + rw // 2, cy_head + r - 3 + rh),
        radius=2,
        fill=robe,
    )
    d.rectangle(
        (cx - rw // 2, cy_head + r - 3 + rh - 4, cx + rw // 2, cy_head + r - 3 + rh),
        fill=robe_shade,
    )

    # head
    d.ellipse((cx - r, cy_head - r, cx + r, cy_head + r), fill=skin)
    d.ellipse((cx - r, cy_head + r // 3, cx + r, cy_head + r + 3), fill=skin_shade)

    # unibrow
    d.rectangle((cx - r + 3, cy_head - 3, cx + r - 3, cy_head - 1), fill="#2e3d22")

    # eyes
    ex = 5 if baby else 6
    _eyes(d, cx, cx - ex, cy_head + 1, cx + ex, cy_head + 1, mood, color="#111")

    # big villager nose
    nose_w = 3 if baby else 4
    d.polygon(
        [
            (cx - nose_w, cy_head + 2),
            (cx + nose_w, cy_head + 2),
            (cx, cy_head + 8 if not baby else cy_head + 6),
        ],
        fill=skin_shade,
    )

    return img


# -------------------------------------------------------------- SKELETON -
def draw_skeleton(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    bone = "#e8e2d0"
    bone_shade = "#c9c1a8"
    dark = "#2a2a2a"

    r = 9 if baby else 12
    cx, cy_head = 20, 16 if baby else 14

    # ribcage body
    rw, rh = (12, 11) if baby else (16, 15)
    bx0, by0 = cx - rw // 2, cy_head + r - 3
    d.rounded_rectangle((bx0, by0, bx0 + rw, by0 + rh), radius=2, fill=bone)
    for i in range(3 if baby else 4):
        ry = by0 + 3 + i * 3
        d.line((bx0 + 2, ry, bx0 + rw - 2, ry), fill=bone_shade, width=1)

    # skull
    d.ellipse((cx - r, cy_head - r, cx + r, cy_head + r), fill=bone)
    d.ellipse((cx - r, cy_head + r // 3, cx + r, cy_head + r + 2), fill=bone_shade)

    # eye sockets
    ex = 5 if baby else 6
    if mood == "grumpy":
        d.line((cx - ex - 2, cy_head - 1, cx - ex + 2, cy_head + 2), fill="#c0281c", width=2)
        d.line((cx + ex + 2, cy_head - 1, cx + ex - 2, cy_head + 2), fill="#c0281c", width=2)
    elif mood == "sad":
        d.arc((cx - ex - 2, cy_head - 2, cx - ex + 2, cy_head + 3), 20, 160, fill=dark, width=2)
        d.arc((cx + ex - 2, cy_head - 2, cx + ex + 2, cy_head + 3), 20, 160, fill=dark, width=2)
    else:
        d.rectangle((cx - ex - 1, cy_head - 1, cx - ex + 2, cy_head + 2), fill=dark)
        d.rectangle((cx + ex - 2, cy_head - 1, cx + ex + 1, cy_head + 2), fill=dark)

    # nose triangle
    d.polygon([(cx - 1, cy_head + 3), (cx + 1, cy_head + 3), (cx, cy_head + 6)], fill=dark)
    # teeth
    d.line((cx - 4, cy_head + 8, cx + 4, cy_head + 8), fill=dark, width=1)

    return img


# ----------------------------------------------------------------- SPIDER -
def draw_spider(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    body = "#241f2e"
    body_shade = "#151220"
    red = "#8a1c1c"

    r = 10 if baby else 14
    cx, cy = 20, 22 if baby else 21

    # legs (behind body)
    n_legs = 3
    leg_col = "#1a1620"
    for side in (-1, 1):
        for i in range(n_legs):
            lx0 = cx + side * (r - 3)
            ly0 = cy - 4 + i * 5
            lx1 = cx + side * (r + 9)
            ly1 = ly0 - 4 + i * 4
            d.line((lx0, ly0, lx1, ly1), fill=leg_col, width=3 if not baby else 2)

    # abdomen + head
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=body)
    d.ellipse((cx - r, cy + r // 2, cx + r, cy + r + 3), fill=body_shade)
    hr = r - 4
    d.ellipse((cx - hr, cy - r - hr + 3, cx + hr, cy - r + hr + 3), fill=body)

    # eyes (multiple small red dots = spider vibes; dim + droopy when sad)
    if mood == "grumpy":
        eye_color = "#ff6a3d"
    elif mood == "sad":
        eye_color = "#8a7aa0"
    else:
        eye_color = "#ff2c2c"
    ey = cy - r + 2
    for dx in (-6, -2, 2, 6):
        rad = 2 if abs(dx) <= 2 else 1
        droop = 2 if mood == "sad" else 0
        d.ellipse((cx + dx - rad, ey - rad + droop, cx + dx + rad, ey + rad + droop), fill=eye_color)

    return img


# -------------------------------------------------------------- ENDERMAN -
def draw_enderman(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    body = "#151317"
    body_shade = "#0a090b"
    purple = "#c86bff"

    r = 8 if baby else 10
    cx, cy_head = 20, 15 if baby else 12

    # long body
    bw, bh = (11, 15) if baby else (13, 20)
    bx0, by0 = cx - bw // 2, cy_head + r - 2
    d.rounded_rectangle((bx0, by0, bx0 + bw, by0 + bh), radius=2, fill=body)
    d.rectangle((bx0, by0 + bh - 4, bx0 + bw, by0 + bh), fill=body_shade)

    # head
    d.rounded_rectangle((cx - r, cy_head - r, cx + r, cy_head + r), radius=2, fill=body)

    # glowing purple eyes (dim when sad)
    ex = 4 if baby else 5
    if mood == "grumpy":
        eye_color = "#ff5d5d"
    elif mood == "sad":
        eye_color = "#6a4a8a"
    else:
        eye_color = purple
    droop = 2 if mood == "sad" else 0
    d.rectangle((cx - ex - 2, cy_head - 1 + droop, cx - ex + 1, cy_head + 2 + droop), fill=eye_color)
    d.rectangle((cx + ex - 1, cy_head - 1 + droop, cx + ex + 2, cy_head + 2 + droop), fill=eye_color)
    if mood == "happy":
        d.arc((cx - 5, cy_head + 2, cx + 5, cy_head + 9), 20, 160, fill=purple, width=1)
    elif mood == "sad":
        d.arc((cx - 5, cy_head + 7, cx + 5, cy_head + 14), 200, 340, fill=eye_color, width=1)

    return img


# ------------------------------------------------------------------ WITCH -
def draw_witch(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    skin = "#6aa06a"
    skin_shade = "#578a57"
    robe = "#3a2f4d"
    robe_shade = "#2b2239"
    hat = "#241c33"

    r = 9 if baby else 12
    cx, cy_head = 20, 18 if baby else 16

    # robe/body
    rw, rh = (14, 12) if baby else (18, 16)
    d.rounded_rectangle(
        (cx - rw // 2, cy_head + r - 3, cx + rw // 2, cy_head + r - 3 + rh),
        radius=2, fill=robe,
    )
    d.rectangle(
        (cx - rw // 2, cy_head + r - 3 + rh - 4, cx + rw // 2, cy_head + r - 3 + rh),
        fill=robe_shade,
    )

    # head
    d.ellipse((cx - r, cy_head - r, cx + r, cy_head + r), fill=skin)
    d.ellipse((cx - r, cy_head + r // 3, cx + r, cy_head + r + 3), fill=skin_shade)

    # witch hat
    brim_y = cy_head - r + 3
    d.ellipse((cx - r - 3, brim_y - 2, cx + r + 3, brim_y + 3), fill=hat)
    d.polygon([(cx - 6, brim_y), (cx + 6, brim_y), (cx, brim_y - 18)], fill=hat)

    # eyes
    ex = 5 if baby else 6
    _eyes(d, cx, cx - ex, cy_head + 1, cx + ex, cy_head + 1, mood, color="#111")

    # wart nose
    nose_w = 2 if baby else 3
    d.ellipse((cx - nose_w, cy_head + 3, cx + nose_w, cy_head + 3 + nose_w * 2), fill=skin_shade)
    d.ellipse((cx - 1, cy_head + 5, cx + 1, cy_head + 7), fill="#3f6b3f")

    return img


# ------------------------------------------------------- PIGLIN (Nether) -
def draw_piglin(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    skin = "#d9a679"
    skin_shade = "#c08e60"
    gold = "#f2c14e"
    tusk = "#f5f0e6"

    r = 10 if baby else 13
    cx, cy = 20, 21 if baby else 19

    # ears
    ear = skin_shade
    d.polygon([(cx - r + 1, cy - r + 3), (cx - r - 4, cy - r - 5), (cx - r + 7, cy - r + 2)], fill=ear)
    d.polygon([(cx + r - 1, cy - r + 3), (cx + r + 4, cy - r - 5), (cx + r - 7, cy - r + 2)], fill=ear)

    # head/body
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=skin)
    d.ellipse((cx - r, cy + r // 2, cx + r, cy + r + 4), fill=skin_shade)

    # gold earring
    d.ellipse((cx - r - 1, cy - 2, cx - r + 3, cy + 2), outline=gold, width=1)

    # snout
    sw, sh = (6, 4) if baby else (8, 5)
    d.rounded_rectangle((cx - sw, cy + 2, cx + sw, cy + 2 + sh), radius=2, fill=skin_shade)
    d.ellipse((cx - 3, cy + 4, cx - 1, cy + 6), fill="#7a5236")
    d.ellipse((cx + 1, cy + 4, cx + 3, cy + 6), fill="#7a5236")

    # tusks
    d.polygon([(cx - sw + 1, cy + 5), (cx - sw - 2, cy + 9), (cx - sw + 3, cy + 7)], fill=tusk)
    d.polygon([(cx + sw - 1, cy + 5), (cx + sw + 2, cy + 9), (cx + sw - 3, cy + 7)], fill=tusk)

    # eyes
    ex = 6 if baby else 7
    _eyes(d, cx, cx - ex, cy - 3, cx + ex, cy - 3, mood)

    return img


# --------------------------------------------------------- GHAST (Nether) -
def draw_ghast(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    white = "#f2f0f5"
    shade = "#d9d5e0"
    dark = "#2b2b2b"

    w = 18 if baby else 24
    h = 14 if baby else 18
    x0, y0 = 20 - w // 2, (16 if baby else 13) - h // 2

    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=5, fill=white)
    d.rectangle((x0, y0 + h - 4, x0 + w, y0 + h), fill=shade)

    cx = x0 + w // 2
    fy = y0 + h // 2 - 2

    if mood == "grumpy":
        for dx in (-6, -2, 2, 6):
            d.line((cx + dx - 1, fy - 1, cx + dx + 1, fy + 1), fill="#c0281c", width=1)
        d.line((cx - 4, fy + 6, cx + 4, fy + 6), fill=dark, width=2)
    elif mood == "sad":
        for dx in (-6, -2, 2, 6):
            d.rectangle((cx + dx - 1, fy - 1, cx + dx + 1, fy + 1), fill=dark)
        d.arc((cx - 5, fy + 8, cx + 5, fy + 15), 200, 340, fill=dark, width=2)
        d.ellipse((cx - 7, fy + 2, cx - 5, fy + 5), fill="#7fb8e6")
        d.ellipse((cx + 5, fy + 2, cx + 7, fy + 5), fill="#7fb8e6")
    else:
        for dx in (-6, -2, 2, 6):
            d.rectangle((cx + dx - 1, fy - 1, cx + dx + 1, fy + 1), fill=dark)
        if mood == "happy":
            d.arc((cx - 4, fy + 3, cx + 4, fy + 9), 20, 160, fill=dark, width=1)
        else:
            d.rectangle((cx - 3, fy + 5, cx + 3, fy + 7), fill=dark)

    # dangling tentacles
    n_tent = 6 if not baby else 4
    span = w - 6
    start = cx - span // 2
    for i in range(n_tent):
        tx = start + i * (span // (n_tent - 1))
        tl = 8 + (i % 3) * 3
        d.line((tx, y0 + h, tx, y0 + h + tl), fill=white, width=2)

    return img


# ---------------------------------------------------------- SHULKER (End) -
def draw_shulker(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    shell = "#b07fc4"
    shell_dark = "#8a5aa3"
    trim = "#e0c8ea"
    eye = "#3a2b40"

    w = 20 if baby else 26
    h = 12 if baby else 15
    cx = 20
    top_y = 24 - h if baby else 26 - h

    # bottom box (the "foot")
    d.rectangle((cx - w // 2, top_y + h - 4, cx + w // 2, top_y + h + 4), fill=shell_dark)
    # shell lid
    d.rounded_rectangle((cx - w // 2, top_y, cx + w // 2, top_y + h), radius=3, fill=shell)
    for i in range(4):
        lx = cx - w // 2 + 4 + i * (w - 8) // 3
        d.rectangle((lx, top_y, lx + 3, top_y + 3), fill=trim)

    # single central eye peeking out (dim + downcast when sad, like it's sulking)
    er = 4 if baby else 5
    if mood == "grumpy":
        eye_col = "#c0281c"
    elif mood == "sad":
        eye_col = "#5a4a68"
    else:
        eye_col = eye
    eye_dy = 2 if mood == "sad" else 0
    d.ellipse((cx - er, top_y + h // 2 - er, cx + er, top_y + h // 2 + er), fill="#1c1420")
    d.ellipse((cx - er + 2, top_y + h // 2 - 2 + eye_dy, cx - er + 5, top_y + h // 2 + 1 + eye_dy), fill=eye_col)

    return img


# -------------------------------------------------- AXOLOTL (Lush Caves) --
def draw_axolotl(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    body = "#f2a9c6"
    shade = "#df8fb0"
    gill = "#e6739a"

    r = 9 if baby else 12
    cx, cy = 20, 23 if baby else 21

    # tail
    d.polygon([(cx + r - 2, cy), (cx + r + 10, cy - 5), (cx + r + 10, cy + 5)], fill=body)

    # frilly gills
    for side in (-1, 1):
        for i in range(3):
            gx = cx + side * (r - 1)
            gy = cy - 4 + i * 4
            d.polygon(
                [(gx, gy), (gx + side * 7, gy - 3), (gx + side * 7, gy + 3)],
                fill=gill,
            )

    # body/head
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=body)
    d.ellipse((cx - r, cy + r // 2, cx + r, cy + r + 3), fill=shade)

    # legs
    for lx in (cx - r + 2, cx + r - 5):
        d.ellipse((lx, cy + r - 2, lx + 4, cy + r + 3), fill=body)

    # eyes + smile
    ex = 5 if baby else 6
    _eyes(d, cx, cx - ex, cy - 3, cx + ex, cy - 3, mood, color="#3a1c24")
    if mood != "grumpy":
        d.arc((cx - 4, cy + 1, cx + 4, cy + 7), 20, 160, fill="#3a1c24", width=1)

    return img


# ------------------------------------------------- POLAR BEAR (Snowy) -----
def draw_polar_bear(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    fur = "#f2f2ee"
    shade = "#d8d8d0"
    nose = "#2b2b2b"

    r = 10 if baby else 14
    cx, cy = 20, 22 if baby else 21

    # ears
    er = 3 if baby else 4
    d.ellipse((cx - r + 1, cy - r - 1, cx - r + 1 + er * 2, cy - r - 1 + er * 2), fill=fur)
    d.ellipse((cx + r - 1 - er * 2, cy - r - 1, cx + r - 1, cy - r - 1 + er * 2), fill=fur)

    # body/head
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fur)
    d.ellipse((cx - r, cy + r // 2, cx + r, cy + r + 4), fill=shade)

    # snout
    sw, sh = (6, 5) if baby else (8, 6)
    d.ellipse((cx - sw, cy + 2, cx + sw, cy + 2 + sh), fill="#fbfbf8")
    d.ellipse((cx - 2, cy + 4, cx + 2, cy + 7), fill=nose)

    # eyes
    ex = 6 if baby else 7
    _eyes(d, cx, cx - ex, cy - 3, cx + ex, cy - 3, mood, color="#1a1a1a")

    return img


# ---------------------------------------------------------- BLAZE (Nether) -
def draw_blaze(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    gold = "#f2c14e"
    gold_dark = "#c9932e"
    flame = "#ff9d3d"
    dark = "#2b1a0a"

    r = 7 if baby else 9
    cx, cy = 20, 20 if baby else 18

    # radiating rods
    n_rods = 5 if baby else 7
    for i in range(n_rods):
        angle = (i / n_rods) * 2 * math.pi
        rx = cx + math.cos(angle) * (r + 6)
        ry = cy + math.sin(angle) * (r + 6)
        d.line((cx, cy, rx, ry), fill=flame, width=2)
        d.ellipse((rx - 2, ry - 2, rx + 2, ry + 2), fill=gold)

    # flame spikes on top
    for dx in (-6, -2, 2, 6):
        d.polygon([(cx + dx - 2, cy - r + 2), (cx + dx + 2, cy - r + 2), (cx + dx, cy - r - 8)], fill=flame)

    # head/body core
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=gold)
    d.ellipse((cx - r, cy + r // 2, cx + r, cy + r + 3), fill=gold_dark)

    # eyes
    ex = 4 if baby else 5
    _eyes(d, cx, cx - ex, cy - 1, cx + ex, cy - 1, mood, color=dark)

    return img


# --------------------------------------------------------------- SNIFFER --
def draw_sniffer(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    skin = "#8fae6a"
    skin_shade = "#749457"
    spot = "#d97a3d"
    dark = "#2b2b1a"

    r = 10 if baby else 13
    cx, cy = 20, 20 if baby else 18

    # body
    bw, bh = (16, 10) if baby else (20, 13)
    d.rounded_rectangle((cx - bw // 2, cy + r - 4, cx + bw // 2, cy + r - 4 + bh), radius=3, fill=skin)
    d.rectangle((cx - bw // 2, cy + r - 4 + bh - 3, cx + bw // 2, cy + r - 4 + bh), fill=skin_shade)

    # head
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=skin)

    # spots
    for sx, sy in [(-5, -2), (4, -4), (-2, 3), (6, 2)]:
        d.ellipse((cx + sx, cy + sy, cx + sx + 2, cy + sy + 2), fill=spot)

    # big sniffer snout hanging down
    sw, sh = (5, 8) if baby else (6, 11)
    d.rounded_rectangle((cx - sw, cy + 3, cx + sw, cy + 3 + sh), radius=3, fill=skin_shade)
    d.ellipse((cx - 2, cy + sh - 1, cx, cy + sh + 1), fill=dark)
    d.ellipse((cx + 1, cy + sh - 1, cx + 3, cy + sh + 1), fill=dark)

    # small eyes
    ex = 6 if baby else 7
    _eyes(d, cx, cx - ex, cy - 4, cx + ex, cy - 4, mood, color=dark)

    return img


# ------------------------------------------------------------------ SLIME -
def draw_slime(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    outer = "#7ec850"
    inner = "#5aa838"
    dark = "#1c1c1c"

    s = 11 if baby else 15
    cx, cy = 20, 24 if baby else 22

    d.rounded_rectangle((cx - s, cy - s, cx + s, cy + s), radius=4, fill=outer)
    pad = s // 3
    d.rounded_rectangle((cx - s + pad, cy - s + pad, cx + s - pad, cy + s - pad), radius=3, fill=inner)

    ex = s // 2
    if mood == "grumpy":
        d.line((cx - ex - 2, cy - 2, cx - ex + 2, cy + 1), fill="#c0281c", width=2)
        d.line((cx + ex + 2, cy - 2, cx + ex - 2, cy + 1), fill="#c0281c", width=2)
    elif mood == "sad":
        d.arc((cx - ex - 2, cy - 3, cx - ex + 2, cy + 2), 20, 160, fill=dark, width=2)
        d.arc((cx + ex - 2, cy - 3, cx + ex + 2, cy + 2), 20, 160, fill=dark, width=2)
    else:
        d.rectangle((cx - ex - 1, cy - 1, cx - ex + 2, cy + 2), fill=dark)
        d.rectangle((cx + ex - 2, cy - 1, cx + ex + 1, cy + 2), fill=dark)
    if mood == "happy":
        d.arc((cx - 4, cy + 3, cx + 4, cy + 9), 20, 160, fill=dark, width=1)
    elif mood == "sad":
        d.arc((cx - 4, cy + 6, cx + 4, cy + 12), 200, 340, fill=dark, width=1)
    elif mood != "grumpy":
        d.line((cx - 3, cy + 5, cx + 3, cy + 5), fill=dark, width=1)

    return img


# ------------------------------------------------------ MAGMA CUBE (Nether) -
def draw_magma_cube(stage, mood):
    img, d = _canvas()
    baby = stage == "baby"
    outer = "#c9481f"
    inner = "#ffb02e"
    crack = "#2b1208"
    dark = "#1a0d05"

    s = 11 if baby else 15
    cx, cy = 20, 24 if baby else 22

    d.rounded_rectangle((cx - s, cy - s, cx + s, cy + s), radius=3, fill=outer)
    pad = s // 3
    d.rounded_rectangle((cx - s + pad, cy - s + pad, cx + s - pad, cy + s - pad), radius=2, fill=inner)
    # cracks
    d.line((cx - s + 2, cy - 2, cx - pad, cy - pad), fill=crack, width=1)
    d.line((cx + s - 2, cy + 3, cx + pad, cy + pad), fill=crack, width=1)

    ex = s // 2
    if mood == "grumpy":
        d.line((cx - ex - 2, cy - 2, cx - ex + 2, cy + 1), fill="#ffe066", width=2)
        d.line((cx + ex + 2, cy - 2, cx + ex - 2, cy + 1), fill="#ffe066", width=2)
    elif mood == "sad":
        d.arc((cx - ex - 2, cy - 3, cx - ex + 2, cy + 2), 20, 160, fill=dark, width=2)
        d.arc((cx + ex - 2, cy - 3, cx + ex + 2, cy + 2), 20, 160, fill=dark, width=2)
    else:
        d.rectangle((cx - ex - 1, cy - 1, cx - ex + 2, cy + 2), fill=dark)
        d.rectangle((cx + ex - 2, cy - 1, cx + ex + 1, cy + 2), fill=dark)
    if mood == "happy":
        d.arc((cx - 4, cy + 3, cx + 4, cy + 9), 20, 160, fill=dark, width=1)
    elif mood == "sad":
        d.arc((cx - 4, cy + 6, cx + 4, cy + 12), 200, 340, fill=dark, width=1)
    elif mood != "grumpy":
        d.line((cx - 3, cy + 5, cx + 3, cy + 5), fill=dark, width=1)

    return img


# --------------------------------------------------- SULFUR CUBE (Nether-ish) -
def draw_sulfur_cube(stage, mood):
    """The Sulfur Cube -- a real Minecraft mob added in the 2026 Chaos Cubed
    update: a pale yellow, passive slime-like cube found in Sulfur Caves."""
    img, d = _canvas()
    baby = stage == "baby"
    outer = "#f2e6a8"
    inner = "#fff6d9"
    dark = "#5c4a1a"

    s = 11 if baby else 15
    cx, cy = 20, 24 if baby else 22

    d.rounded_rectangle((cx - s, cy - s, cx + s, cy + s), radius=4, fill=outer)
    pad = s // 3
    d.rounded_rectangle((cx - s + pad, cy - s + pad, cx + s - pad, cy + s - pad), radius=3, fill=inner)

    # wide-set "clueless" eyes, extra far apart for that derpy sulfur-cube look
    ex = s // 2 + 2
    if mood == "grumpy":
        d.line((cx - ex - 2, cy - 2, cx - ex + 2, cy + 1), fill="#c0281c", width=2)
        d.line((cx + ex + 2, cy - 2, cx + ex - 2, cy + 1), fill="#c0281c", width=2)
    elif mood == "sad":
        d.arc((cx - ex - 2, cy - 3, cx - ex + 2, cy + 2), 20, 160, fill=dark, width=2)
        d.arc((cx + ex - 2, cy - 3, cx + ex + 2, cy + 2), 20, 160, fill=dark, width=2)
        d.ellipse((cx - ex - 1, cy + 2, cx - ex + 1, cy + 5), fill="#6fa8e0")
    else:
        d.ellipse((cx - ex - 1, cy - 1, cx - ex + 2, cy + 2), fill=dark)
        d.ellipse((cx + ex - 2, cy - 1, cx + ex + 1, cy + 2), fill=dark)
    # small flat "clueless" mouth, no expression change even when happy or sad
    d.line((cx - 2, cy + 5, cx + 2, cy + 5), fill=dark, width=1)

    return img


BIOME_OF_MOB = {
    "pig": "plains",
    "chicken": "plains",
    "creeper": "cave",
    "zombie_villager": "village_night",
    "skeleton": "cave",
    "spider": "cave",
    "enderman": "end",
    "witch": "swamp",
    "piglin": "nether_waste",
    "ghast": "nether_soul",
    "shulker": "end",
    "axolotl": "lush_cave",
    "polar_bear": "snowy",
    "blaze": "nether_waste",
    "sniffer": "beach",
    "slime": "swamp",
    "magma_cube": "nether_waste",
    "sulfur_cube": "sulfur_cave",
}

_SKY = {
    "plains": "#7fc7f2", "cave": "#2b2b2e", "village_night": "#141428",
    "end": "#170e26", "swamp": "#6f7d63", "nether_waste": "#c9531f",
    "nether_soul": "#1c3235", "lush_cave": "#1f3d40", "snowy": "#bcd9ec",
    "beach": "#8fd6f0", "sulfur_cave": "#2b1810",
}
_GROUND = {
    "plains": "#5b9c3e", "cave": "#242427", "village_night": "#6b5a3d",
    "end": "#cfc37a", "swamp": "#3f4a2c", "nether_waste": "#5c2a1e",
    "nether_soul": "#2b4a4a", "lush_cave": "#355c3d", "snowy": "#eef3f7",
    "beach": "#e8d29a", "sulfur_cave": "#7a3320",
}

_BG_CACHE = {}


def _draw_background(kind):
    if kind in _BG_CACHE:
        return _BG_CACHE[kind].copy()

    img = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    horizon = 30
    d.rectangle((0, 0, BASE, horizon), fill=_SKY[kind])
    d.rectangle((0, horizon, BASE, BASE), fill=_GROUND[kind])

    if kind == "plains":
        d.ellipse((30, 3, 37, 10), fill="#fff2b0")
        for x in range(1, BASE, 4):
            d.line((x, horizon, x, horizon - 2), fill="#4a8a34")
    elif kind == "cave":
        for i, x in enumerate(range(1, BASE, 5)):
            y = horizon + 3 + (i % 3) * 3
            d.rectangle((x, y, x + 2, y + 2), fill="#4a4a4e")
        for x in range(0, BASE, 7):
            d.rectangle((x, 0, x + 3, 2), fill="#1c1c1e")
    elif kind == "village_night":
        d.ellipse((5, 4, 11, 10), fill="#f2ecc9")
        for sx, sy in [(15, 5), (22, 9), (30, 4), (36, 8), (9, 12)]:
            d.point((sx, sy), fill="#f5f5e0")
        for x in range(0, BASE, 6):
            d.rectangle((x, horizon, x + 3, horizon + 1), fill="#8a7550")
    elif kind == "end":
        for sx, sy in [(4, 4), (12, 8), (20, 3), (28, 10), (34, 5), (8, 14), (37, 15)]:
            d.point((sx, sy), fill="#e8e0f5")
        for i, x in enumerate(range(0, BASE, 5)):
            y = horizon + 2 + (i % 2) * 2
            d.rectangle((x, y, x + 3, y + 2), fill="#b6aa66")
    elif kind == "swamp":
        for i, x in enumerate(range(2, BASE, 6)):
            d.ellipse((x, horizon + 2 + (i % 2) * 3, x + 3, horizon + 5 + (i % 2) * 3), fill="#333d24")
        for sx, sy in [(6, 6), (20, 10), (32, 5)]:
            d.ellipse((sx, sy, sx + 2, sy + 2), fill="#8a9a7a")
    elif kind == "nether_waste":
        for i, x in enumerate(range(1, BASE, 5)):
            y = horizon + 2 + (i % 3) * 3
            d.rectangle((x, y, x + 2, y + 2), fill="#3a1710")
        for sx, sy in [(8, 33), (18, 36), (28, 34), (34, 37)]:
            d.ellipse((sx, sy, sx + 2, sy + 2), fill="#ff8a2e")
    elif kind == "nether_soul":
        for i, x in enumerate(range(1, BASE, 5)):
            y = horizon + 2 + (i % 3) * 3
            d.rectangle((x, y, x + 2, y + 2), fill="#3d5c58")
        for sx, sy in [(6, 21), (16, 24), (26, 20), (34, 25)]:
            d.ellipse((sx, sy, sx + 3, sy + 2), fill="#4fd6c4")
    elif kind == "lush_cave":
        for i, x in enumerate(range(1, BASE, 6)):
            d.ellipse((x, horizon + 1 + (i % 2) * 2, x + 4, horizon + 4 + (i % 2) * 2), fill="#2a4a30")
        for sx, sy in [(5, 10), (14, 6), (24, 12), (33, 7), (10, 18)]:
            d.ellipse((sx, sy, sx + 1, sy + 1), fill="#7fe6c9")
    elif kind == "snowy":
        d.ellipse((28, 3, 35, 10), fill="#ffffff")
        for i, x in enumerate(range(1, BASE, 5)):
            y = horizon + 1 + (i % 2) * 2
            d.ellipse((x, y, x + 3, y + 2), fill="#d8e6ef")
        for sx, sy in [(4, 5), (14, 9), (24, 4), (32, 12)]:
            d.ellipse((sx, sy, sx + 1, sy + 1), fill="#ffffff")
    elif kind == "beach":
        d.ellipse((4, 3, 11, 10), fill="#fff2b0")
        d.rectangle((0, horizon - 3, BASE, horizon), fill="#5ab3d8")
        for x in range(0, BASE, 6):
            d.line((x, horizon - 2, x + 3, horizon - 2), fill="#bfe8f5", width=1)
        for sx, sy in [(6, 34), (16, 36), (26, 33), (34, 37)]:
            d.ellipse((sx, sy, sx + 2, sy + 1), fill="#d8bd7a")
    elif kind == "sulfur_cave":
        for i, x in enumerate(range(1, BASE, 5)):
            y = horizon + 2 + (i % 3) * 3
            d.rectangle((x, y, x + 2, y + 2), fill="#4a2018")
        for sx, sy in [(6, 33), (16, 36), (26, 34), (34, 37)]:
            d.ellipse((sx, sy, sx + 3, sy + 2), fill="#e6c94a")
        for sx, sy in [(5, 5), (15, 10), (25, 4), (33, 9)]:
            d.polygon([(sx, sy + 5), (sx + 2, sy), (sx + 4, sy + 5)], fill="#f2d95c")

    _BG_CACHE[kind] = img
    return img.copy()


DRAW_FUNCS = {
    "pig": draw_pig,
    "chicken": draw_chicken,
    "creeper": draw_creeper,
    "zombie_villager": draw_zombie_villager,
    "skeleton": draw_skeleton,
    "spider": draw_spider,
    "enderman": draw_enderman,
    "witch": draw_witch,
    "piglin": draw_piglin,
    "ghast": draw_ghast,
    "shulker": draw_shulker,
    "axolotl": draw_axolotl,
    "polar_bear": draw_polar_bear,
    "blaze": draw_blaze,
    "sniffer": draw_sniffer,
    "slime": draw_slime,
    "magma_cube": draw_magma_cube,
    "sulfur_cube": draw_sulfur_cube,
}

MOB_NAMES = {
    "pig": "Pig",
    "chicken": "Chicken",
    "creeper": "Creeper",
    "zombie_villager": "Zombie Villager",
    "skeleton": "Skeleton",
    "spider": "Spider",
    "enderman": "Enderman",
    "witch": "Witch",
    "piglin": "Piglin",
    "ghast": "Ghast",
    "shulker": "Shulker",
    "axolotl": "Axolotl",
    "polar_bear": "Polar Bear",
    "blaze": "Blaze",
    "sniffer": "Sniffer",
    "slime": "Slime",
    "magma_cube": "Magma Cube",
    "sulfur_cube": "Sulfur Cube",
}


def get_sprite(mob, stage, mood="neutral"):
    """mob: any key in DRAW_FUNCS
       stage: baby/adult
       mood: neutral/happy/grumpy/charge
       Returns the mob composited onto its biome/dimension background,
       scaled up to the final chunky pixel-art size."""
    raw = DRAW_FUNCS[mob](stage, mood)  # unscaled, transparent bg
    bg = _draw_background(BIOME_OF_MOB[mob])  # unscaled, opaque
    bg.alpha_composite(raw)
    return _finish(bg)


if __name__ == "__main__":
    # quick contact sheet for visual review
    mobs = list(DRAW_FUNCS)
    sheet = Image.new("RGBA", (FINAL * 4, FINAL * len(mobs)), (40, 40, 40, 255))
    moods = ["neutral", "happy", "grumpy"]
    for row, mob in enumerate(mobs):
        for col, stage in enumerate(["baby", "adult"]):
            sprite = get_sprite(mob, stage, "neutral")
            sheet.paste(sprite, (col * FINAL, row * FINAL), sprite)
        sprite_g = get_sprite(mob, "adult", "grumpy")
        sheet.paste(sprite_g, (2 * FINAL, row * FINAL), sprite_g)
        sprite_h = get_sprite(mob, "adult", "happy")
        sheet.paste(sprite_h, (3 * FINAL, row * FINAL), sprite_h)
    sheet.save("/home/claude/minecraft_pet/contact_sheet.png")
    print("saved contact sheet")
