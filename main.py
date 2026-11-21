#!/usr/bin/env python3
"""AURELIA TERMINUS — a travel poster for a place that isn't there.

Renders one 768x1024 travel poster, fully procedural, no network, no
downloaded assets. The place: the last station on Earth, where the aurora
comes down out of the sky and rests on the platform. One landmark (the
art-deco clock-tower station), one promise (a warm-lit night under the
aurora), one name set in large serif type at the top.

Deterministic: fixed seed, no time, no randomness from the environment.
Writes /output/entry.png (PNG, <= 1 MiB, <= 1024x1024).
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 768, 1024
SEED = 20261121
OUT_PATH = "/output/entry.png"

# Palette — purposeful, 4 families only:
#   deep indigo night, teal/green aurora, warm amber lamplight, cream type.
INK_TOP = (9, 13, 42)        # night sky, top
INK_MID = (24, 38, 84)       # night sky, middle
HORIZON = (38, 96, 104)      # teal glow at the horizon
AURORA_1 = (70, 242, 192)    # bright aurora green
AURORA_2 = (125, 255, 154)   # pale aurora green
AURORA_3 = (143, 123, 255)   # violet aurora edge
AMBER = (255, 190, 92)       # lamplight / windows
AMBER_DEEP = (232, 148, 52)
CREAM = (247, 234, 208)      # type
GOLD = (212, 175, 105)
SNOW_TOP = (214, 228, 242)
SNOW_BOT = (168, 186, 214)
MOUNT_FAR = (28, 43, 82)
MOUNT_NEAR = (20, 31, 61)
PINE = (13, 24, 48)
STATION = (74, 53, 80)       # plum stone of the station
STATION_DARK = (52, 36, 58)
TOWER = (88, 62, 92)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vertical_gradient(w, h, stops):
    """stops: list of (position 0..1, rgb). Returns an RGB image."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = lerp(c0, c1, f)
                break
        else:
            col = stops[-1][1]
        for x in range(w):
            px[x, y] = col
    return img


def glow_spot(layer, cx, cy, r, color, alpha):
    """Soft radial glow: filled circle on an RGBA layer, blurred later."""
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))


def arched_window(d, x, y, w, h, fill):
    """Window with a rounded top, plus a dark mullion cross."""
    d.rectangle([x, y + w // 2, x + w, y + h], fill=fill)
    d.pieslice([x, y, x + w, y + w], 180, 360, fill=fill)
    d.line([x + w // 2, y + 4, x + w // 2, y + h - 2], fill=(60, 35, 20), width=2)
    d.line([x + 2, y + h // 2, x + w - 2, y + h // 2], fill=(60, 35, 20), width=2)


def pine(d, x, base, h, color, rng):
    """A simple dark pine silhouette, trunk + 3 stacked triangles."""
    w = h * 0.42
    d.rectangle([x - 2, base - h * 0.12, x + 2, base], fill=color)
    for i, (frac, top) in enumerate([(0.62, 0.42), (0.78, 0.68), (1.0, 1.0)]):
        tw = w * frac
        ty = base - h * top
        by = base - h * (top - 0.34)
        d.polygon([(x - tw / 2, by), (x + tw / 2, by), (x, ty)], fill=color)


def mountain_range(d, rng, base_y, amp, color, seed_offset):
    pts = [(0, H)]
    x = 0
    y = base_y
    while x < W:
        step = rng.randint(50, 130)
        x += step
        y = base_y + rng.randint(-amp, amp)
        pts.append((min(x, W), y))
    pts.append((W, H))
    d.polygon(pts, fill=color)
    # snow caps on the higher peaks
    for (px, py) in pts[1:-1]:
        if py < base_y - amp * 0.45:
            cap = [(px - 26, py + 22), (px, py), (px + 26, py + 22),
                   (px + 12, py + 14), (px, py + 20), (px - 12, py + 14)]
            d.polygon(cap, fill=(205, 220, 238))


def draw_aurora(base, rng):
    """Three translucent ribbons sweeping down across the sky."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ribbons = [
        # (base_y, amplitude, wavelength, color, alpha, thickness)
        (210, 52, 300, AURORA_1, 165, 56),
        (270, 66, 380, AURORA_2, 130, 72),
        (170, 42, 240, AURORA_3, 85, 40),
    ]
    for base_y, amp, wave, color, alpha, thick in ribbons:
        phase = rng.uniform(0, 6.28)
        pts = []
        for x in range(-20, W + 21, 8):
            y = (base_y + amp * math.sin(x / wave * 6.283 + phase)
                 + 26 * math.sin(x / 97.0 + phase * 2.0))
            pts.append((x, y))
        d.line(pts, fill=color + (alpha,), width=thick, joint="curve")
        # bright core thread inside the ribbon
        core = [(x, y + 8) for (x, y) in pts]
        d.line(core, fill=(235, 255, 240, 150), width=5, joint="curve")
    # a few falling curtains where the aurora touches the station
    for cx in (300, 384, 468):
        for i in range(9):
            x0 = cx + rng.randint(-30, 30)
            y0 = 380 + rng.randint(0, 40)
            d.line([(x0, y0), (x0 + rng.randint(-8, 8), y0 + rng.randint(100, 190))],
                   fill=AURORA_1 + (70,), width=4)
    blurred = layer.filter(ImageFilter.GaussianBlur(20))
    base.alpha_composite(blurred)
    return base


def draw_station(d, glow):
    """The landmark: art-deco station with a clock tower, warm windows."""
    gx, gy = 210, 600          # main block top-left
    gw, gh = 348, 168          # main block size
    # main block
    d.rectangle([gx, gy, gx + gw, gy + gh], fill=STATION)
    d.rectangle([gx, gy, gx + gw, gy + 10], fill=STATION_DARK)
    # stepped parapet
    d.rectangle([gx + 24, gy - 14, gx + gw - 24, gy], fill=STATION_DARK)
    d.rectangle([gx + 60, gy - 26, gx + gw - 60, gy - 14], fill=STATION_DARK)
    # clock tower
    tx0, tx1 = 330, 438
    d.rectangle([tx0, 470, tx1, gy + gh], fill=TOWER)
    d.rectangle([tx0 - 6, 462, tx1 + 6, 474], fill=STATION_DARK)
    d.polygon([(tx0 + 8, 462), (tx1 - 8, 462), (384, 424)], fill=STATION_DARK)
    d.line([(384, 424), (384, 404)], fill=GOLD, width=4)  # spire
    glow_spot(glow, 384, 400, 10, (255, 220, 140), 200)
    # clock face
    d.ellipse([384 - 36, 512 - 36, 384 + 36, 512 + 36], fill=(250, 238, 205))
    d.ellipse([384 - 36, 512 - 36, 384 + 36, 512 + 36], outline=GOLD, width=4)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x0 = 384 + 30 * math.sin(a)
        y0 = 512 - 30 * math.cos(a)
        x1 = 384 + 34 * math.sin(a)
        y1 = 512 - 34 * math.cos(a)
        d.line([(x0, y0), (x1, y1)], fill=(60, 45, 30), width=2)
    # hands: ten past ten, the classic poster time
    d.line([(384, 512), (384 - 20, 512 - 16)], fill=(40, 30, 25), width=4)
    d.line([(384, 512), (384 + 22, 512 - 18)], fill=(40, 30, 25), width=4)
    d.ellipse([380, 508, 388, 516], fill=(40, 30, 25))
    # arched windows, warm lit
    for wx in (238, 292, 476, 530):
        arched_window(d, wx, 640, 34, 62, AMBER)
        glow_spot(glow, wx + 17, 672, 34, AMBER, 70)
    # doorway: open, light spilling out
    d.rectangle([352, 668, 416, 768], fill=(30, 20, 34))
    d.rectangle([360, 676, 408, 768], fill=AMBER)
    d.line([(384, 676), (384, 768)], fill=(60, 35, 20), width=3)
    glow_spot(glow, 384, 730, 60, AMBER, 90)
    # light spill on the platform
    d.polygon([(352, 768), (416, 768), (452, 800), (316, 800)], fill=(255, 205, 120))
    # platform edge
    d.rectangle([150, 768, 618, 782], fill=(226, 232, 242))
    d.rectangle([150, 782, 618, 788], fill=(150, 165, 190))


def draw_train(d, glow, rng):
    """A small train at rest beside the station, windows lit."""
    x0, y0, x1, y1 = 560, 700, 752, 768
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(22, 40, 63))
    d.rounded_rectangle([x0, y0, x1, y0 + 16], radius=8, fill=(16, 30, 50))
    for i in range(5):
        wx = x0 + 16 + i * 36
        d.rounded_rectangle([wx, y0 + 26, wx + 24, y0 + 52], radius=4, fill=AMBER)
        glow_spot(glow, wx + 12, y0 + 39, 18, AMBER, 60)
    # headlamp beam
    d.polygon([(x1, y0 + 58), (x1 + 16, y0 + 52), (x1 + 16, y0 + 66)], fill=AMBER)
    glow_spot(glow, x1 + 8, y0 + 59, 16, AMBER, 120)
    # wheels
    for wx in (x0 + 26, x0 + 96, x0 + 166):
        d.ellipse([wx - 9, y1 - 6, wx + 9, y1 + 10], fill=(10, 16, 28))
    # steam curls above the engine
    steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for i, (sx, sy, sr) in enumerate([(588, 668, 16), (606, 640, 22), (628, 612, 28)]):
        sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(235, 240, 250, 60))
    steam = steam.filter(ImageFilter.GaussianBlur(10))
    return steam


def draw_lamp(d, glow, x, base):
    d.rectangle([x - 3, base - 74, x + 3, base], fill=(25, 20, 30))
    d.polygon([(x - 10, base - 74), (x + 10, base - 74), (x + 5, base - 88),
               (x - 5, base - 88)], fill=(25, 20, 30))
    d.ellipse([x - 7, base - 86, x + 7, base - 72], fill=AMBER)
    glow_spot(glow, x, base - 79, 34, AMBER, 110)


def draw_type(img):
    """The place name, set with intent: large serif caps, letterspaced."""
    d = ImageDraw.Draw(img, "RGBA")
    serif = ImageFont.truetype("fonts/DejaVuSerif-Bold.ttf", 96)
    sans = ImageFont.truetype("fonts/DejaVuSans.ttf", 34)

    def tracked(text, font, cx, y, fill, tracking):
        widths = [d.textlength(ch, font=font) for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = cx - total / 2
        for ch, wch in zip(text, widths):
            d.text((x, y), ch, font=font, fill=fill)
            x += wch + tracking
        return total

    # soft shadow under the name so it reads over the aurora
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((W // 2 - 0, 66), "AURELIA", font=serif, fill=(0, 0, 0, 160),
            anchor="ma")
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(shadow)

    tracked("AURELIA", serif, W // 2, 58, CREAM + (255,), 10)
    # thin gold rules flanking the subtitle, BELOW the subtitle text
    # (never through it) with a small diamond on the line's centre.
    d.line([(150, 226), (292, 226)], fill=GOLD + (255,), width=2)
    d.line([(476, 226), (618, 226)], fill=GOLD + (255,), width=2)
    d.polygon([(384, 220), (390, 226), (384, 232), (378, 226)],
              fill=GOLD + (255,))
    tracked("TERMINUS", sans, W // 2, 176, GOLD + (255,), 14)


def main():
    rng = random.Random(SEED)
    img = vertical_gradient(W, H, [
        (0.0, INK_TOP), (0.45, INK_MID), (0.62, HORIZON), (0.66, HORIZON),
        (0.68, SNOW_TOP), (1.0, SNOW_BOT),
    ]).convert("RGBA")

    # stars
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(190):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, 560)
        r = rng.choice([1, 1, 1, 2])
        a = rng.randint(90, 235)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 240, 255, a))
    # a few bright stars with a cross sparkle
    for _ in range(7):
        x = rng.randint(30, W - 30)
        y = rng.randint(30, 420)
        d.line([(x - 7, y), (x + 7, y)], fill=(255, 255, 255, 220), width=1)
        d.line([(x, y - 7), (x, y + 7)], fill=(255, 255, 255, 220), width=1)

    # moon, upper right, soft glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_spot(glow, 648, 300, 90, (255, 236, 180), 60)
    d.ellipse([628, 280, 668, 320], fill=(250, 240, 205, 255))
    d.ellipse([640, 292, 652, 304], fill=(232, 220, 180, 255))
    d.ellipse([636, 306, 642, 312], fill=(232, 220, 180, 255))

    img = draw_aurora(img, rng)

    # mountains, far then near
    d = ImageDraw.Draw(img, "RGBA")
    mountain_range(d, rng, 660, 90, MOUNT_FAR, 0)
    mountain_range(d, rng, 700, 60, MOUNT_NEAR, 1)

    # snow field in the foreground: light ground so the station, pines and
    # train sit on snow, not on dark void (mountains above extend to the
    # bottom edge, so this band has to come after them).
    snow = vertical_gradient(W, H - 786, [(0.0, (226, 236, 246)),
                                           (1.0, (178, 194, 220))]).convert("RGBA")
    img.paste(snow, (0, 786))
    d = ImageDraw.Draw(img, "RGBA")
    drift = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(drift)
    for (dx, dy, dr) in [(140, 830, 90), (640, 880, 110), (420, 960, 130),
                         (80, 970, 100), (700, 990, 90)]:
        dd.ellipse([dx - dr, dy - dr // 3, dx + dr, dy + dr // 3],
                   fill=(240, 245, 252, 90))
    img.alpha_composite(drift.filter(ImageFilter.GaussianBlur(18)))

    # snow field with aurora-coloured reflections
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    for cx in (250, 384, 520):
        rd.polygon([(cx - 14, 790), (cx + 14, 790), (cx + 34, 1000),
                    (cx - 34, 1000)], fill=AURORA_1 + (26,))
    refl = refl.filter(ImageFilter.GaussianBlur(12))
    img.alpha_composite(refl)

    # pines framing the station
    d = ImageDraw.Draw(img, "RGBA")
    for (px, ph) in [(60, 190), (120, 150), (700, 200), (742, 150), (168, 110)]:
        pine(d, px, 800, ph, PINE, rng)
    for (px, ph) in [(96, 120), (676, 130)]:
        pine(d, px, 820, ph, PINE, rng)

    # a packed-snow path from the door to the viewer, with footprints,
    # and one small traveller with a suitcase walking up to the station:
    # scale, and the promise that you can actually go there.
    d.polygon([(352, 800), (416, 800), (470, 1024), (298, 1024)],
              fill=(196, 208, 228, 255))
    for i in range(9):
        fy = 830 + i * 20
        fx = 384 + (10 if i % 2 == 0 else -14)
        d.ellipse([fx - 4, fy - 2, fx + 4, fy + 3], fill=(140, 155, 185, 255))
    # traveller silhouette (dark against the lit path)
    tx, ty = 452, 930
    d.ellipse([tx - 16, ty + 22, tx + 16, ty + 28], fill=(120, 135, 165, 255))
    d.ellipse([tx - 6, ty - 34, tx + 6, ty - 22], fill=(16, 22, 40))       # head
    d.polygon([(tx - 9, ty - 22), (tx + 9, ty - 22), (tx + 12, ty + 18),
               (tx - 12, ty + 18)], fill=(16, 22, 40))                    # coat
    d.rectangle([tx - 8, ty + 18, tx - 3, ty + 24], fill=(16, 22, 40))     # legs
    d.rectangle([tx + 3, ty + 18, tx + 8, ty + 24], fill=(16, 22, 40))
    d.rectangle([tx + 16, ty + 2, tx + 30, ty + 20], fill=(24, 30, 52))    # suitcase
    d.line([(tx + 10, ty - 2), (tx + 17, ty + 4)], fill=(24, 30, 52), width=2)
    # a warm scarf: the one touch of colour on the traveller
    d.rectangle([tx - 7, ty - 24, tx + 7, ty - 19], fill=AMBER_DEEP)

    # station, train, lamps — the landmark and its warm light
    draw_station(d, glow)
    steam = draw_train(d, glow, rng)
    draw_lamp(d, glow, 176, 800)
    draw_lamp(d, glow, 592, 800)
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(steam)

    # gentle vignette so the eye stays centre
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], outline=(6, 8, 26, 110), width=46)
    img.alpha_composite(vig.filter(ImageFilter.GaussianBlur(24)))

    # poster frame
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([14, 14, W - 15, H - 15], outline=CREAM + (200,), width=2)
    d.rectangle([22, 22, W - 23, H - 23], outline=GOLD + (140,), width=1)

    draw_type(img)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    img.convert("RGB").save(OUT_PATH, "PNG", optimize=True)
    print(f"wrote {OUT_PATH} {os.path.getsize(OUT_PATH)} bytes")


if __name__ == "__main__":
    main()
