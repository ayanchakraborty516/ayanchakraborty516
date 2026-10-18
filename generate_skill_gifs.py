"""
generate_skill_gifs.py
======================
Generates real animated multi-frame GIF files for every technology logo
used in the GitHub profile README Tech Arsenal section.

All logos are drawn programmatically with Pillow using authentic brand
colors.  Each GIF has 20â€“30 frames and loops seamlessly.

Run:
    python generate_skill_gifs.py

Output: assets/skills/<name>.gif  (96x96 px, transparent background)
"""

import math
import os
import struct
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "assets", "skills")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SIZE = 96          # px square
FRAMES = 24        # frames per GIF
DURATION = 60      # ms per frame  (â‰ˆ16 fps)


# â”€â”€â”€ helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def new_frame(bg=(0, 0, 0, 0)):
    """Return a fresh RGBA frame."""
    img = Image.new("RGBA", (SIZE, SIZE), bg)
    return img


def save_gif(frames, name):
    """Save a list of RGBA PIL images as a looping GIF."""
    path = os.path.join(OUTPUT_DIR, name)
    rgb_frames = []
    for f in frames:
        # Composite onto a fully transparent base then convert
        base = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        base.paste(f, (0, 0), f)
        rgb_frames.append(base.convert("RGBA"))

    # Use palette mode with transparency for small file sizes
    pal_frames = []
    for f in rgb_frames:
        pf = f.convert("P", palette=Image.ADAPTIVE, colors=255)
        pal_frames.append(pf)

    pal_frames[0].save(
        path,
        format="GIF",
        save_all=True,
        append_images=pal_frames[1:],
        loop=0,
        duration=DURATION,
        disposal=2,
        transparency=0,
    )
    # Quick verification
    with Image.open(path) as check:
        n = getattr(check, "n_frames", 1)
    print(f"  âœ“  {name}  ({n} frames, {os.path.getsize(path)//1024} KB)")
    return path


def ease_in_out(t):
    """Smooth ease-in-out for 0â†’1."""
    return t * t * (3 - 2 * t)


def pulse(frame_i, total, lo=0.75, hi=1.0):
    """Sinusoidal pulse between lo and hi."""
    t = frame_i / total
    return lo + (hi - lo) * (0.5 + 0.5 * math.sin(2 * math.pi * t))


def glow_color(base_color, strength):
    """Blend base_color toward white by strength (0-1)."""
    r, g, b = base_color[:3]
    w = int(strength * 255)
    return (
        min(255, r + int((255 - r) * strength * 0.5)),
        min(255, g + int((255 - g) * strength * 0.5)),
        min(255, b + int((255 - b) * strength * 0.5)),
    )


def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                           outline=outline, width=width)


def draw_circle_glow(img, cx, cy, r, color, alpha_max=180):
    """Draw a soft radial glow circle on an RGBA image."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for dr in range(r, 0, -1):
        a = int(alpha_max * (1 - dr / r) ** 2)
        d = ImageDraw.Draw(overlay)
        d.ellipse([cx - dr, cy - dr, cx + dr, cy + dr],
                  fill=(*color[:3], a))
    img.alpha_composite(overlay)


# â”€â”€â”€ individual logo generators â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def gen_javascript():
    """Yellow square with JS, floating + glow pulse."""
    JS_YELLOW = (247, 223, 30)
    JS_BLACK  = (35, 35, 35)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.82, 1.0)
        glow_s = pulse(i, FRAMES, 0.0, 0.55)
        offset_y = int(3 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        d = ImageDraw.Draw(img)

        sq = int(SIZE * 0.78 * scale)
        x0 = (SIZE - sq) // 2
        y0 = (SIZE - sq) // 2 + offset_y
        x1, y1 = x0 + sq, y0 + sq

        # Glow behind square
        if glow_s > 0:
            draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                             int(sq * 0.6), JS_YELLOW, alpha_max=int(glow_s * 160))

        d2 = ImageDraw.Draw(img)
        draw_rounded_rect(d2, [x0, y0, x1, y1], radius=6,
                          fill=(*JS_YELLOW, 255))

        # "JS" text
        font_size = max(8, int(sq * 0.38))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font = font_b = ImageFont.load_default()

        text = "JS"
        bbox = d2.textbbox((0, 0), text, font=font_b)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x0 + sq - tw - int(sq * 0.06)
        ty = y0 + sq - th - int(sq * 0.06)
        d2.text((tx, ty), text, font=font_b, fill=(*JS_BLACK, 255))
        frames.append(img)
    save_gif(frames, "javascript.gif")


def gen_html5():
    """Orange pentagon-ish shield with HTML5 text, rotating glow."""
    H_ORANGE = (228, 77, 38)
    H_DARK   = (196, 56, 19)
    WHITE    = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        glow_s = pulse(i, FRAMES, 0.0, 0.5)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()

        if glow_s > 0:
            draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                             int(SIZE * 0.4 * scale), H_ORANGE,
                             alpha_max=int(glow_s * 140))

        d = ImageDraw.Draw(img)
        sq = int(SIZE * 0.76 * scale)
        x0 = (SIZE - sq) // 2
        y0 = (SIZE - sq) // 2 + offset_y

        # Shield: rounded rect for body
        draw_rounded_rect(d, [x0, y0, x0 + sq, y0 + sq], radius=4,
                          fill=(*H_ORANGE, 255))

        # "5" badge
        font_size = max(8, int(sq * 0.42))
        try:
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font_b = ImageFont.load_default()

        for txt, col, dy in [("HTML", WHITE, -0.22), ("5", WHITE, 0.22)]:
            bbox = d.textbbox((0, 0), txt, font=font_b)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = x0 + (sq - tw) // 2
            ty = y0 + sq // 2 + int(dy * sq) - th // 2
            d.text((tx, ty), txt, font=font_b, fill=(*col, 255))

        frames.append(img)
    save_gif(frames, "html5.gif")


def gen_css3():
    """Blue shield CSS3 logo with sweep animation."""
    C_BLUE  = (21, 114, 182)
    C_DARK  = (13, 80, 136)
    WHITE   = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        sweep  = (i / FRAMES)          # 0â†’1 sweep position
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.4 * scale), C_BLUE,
                         alpha_max=int(pulse(i, FRAMES, 0, 0.5) * 140))

        d = ImageDraw.Draw(img)
        sq = int(SIZE * 0.76 * scale)
        x0 = (SIZE - sq) // 2
        y0 = (SIZE - sq) // 2 + offset_y

        draw_rounded_rect(d, [x0, y0, x0 + sq, y0 + sq], radius=4,
                          fill=(*C_BLUE, 255))

        # light sweep
        sx = x0 + int(sweep * sq * 1.3) - int(sq * 0.15)
        overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle([sx, y0, sx + int(sq * 0.12), y0 + sq],
                     fill=(255, 255, 255, 40))
        img.alpha_composite(overlay)

        d2 = ImageDraw.Draw(img)
        font_size = max(8, int(sq * 0.42))
        try:
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font_b = ImageFont.load_default()

        for txt, dy in [("CSS", -0.22), ("3", 0.22)]:
            bbox = d2.textbbox((0, 0), txt, font=font_b)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = x0 + (sq - tw) // 2
            ty = y0 + sq // 2 + int(dy * sq) - th // 2
            d2.text((tx, ty), txt, font=font_b, fill=(*WHITE, 255))

        frames.append(img)
    save_gif(frames, "css3.gif")


def gen_java():
    """Java cup logo with steam animation."""
    J_RED    = (237, 84, 44)
    J_ORANGE = (250, 125, 0)
    J_DARK   = (80, 40, 10)
    WHITE    = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.85, 1.0)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))
        steam_phase = (i / FRAMES)

        img = new_frame()
        d = ImageDraw.Draw(img)

        cx, cy = SIZE // 2, SIZE // 2 + offset_y
        sq = int(SIZE * 0.74 * scale)

        draw_circle_glow(img, cx, cy, int(sq * 0.55), J_RED, alpha_max=100)

        d2 = ImageDraw.Draw(img)
        # Cup body
        cup_w = int(sq * 0.6)
        cup_h = int(sq * 0.55)
        cx0 = cx - cup_w // 2
        cy0 = cy - cup_h // 2 + int(sq * 0.08)

        # Cup trapezoid (wider at top)
        pts = [
            (cx0, cy0),
            (cx0 + cup_w, cy0),
            (cx0 + cup_w - int(cup_w * 0.12), cy0 + cup_h),
            (cx0 + int(cup_w * 0.12), cy0 + cup_h),
        ]
        d2.polygon(pts, fill=(*J_RED, 255))

        # Handle
        hx = cx0 + cup_w
        hy = cy0 + int(cup_h * 0.2)
        d2.arc([hx, hy, hx + int(cup_w * 0.35), hy + int(cup_h * 0.5)],
               start=-90, end=90, fill=(*J_ORANGE, 255), width=int(cup_w * 0.08))

        # Coffee inside
        d2.rectangle([cx0 + 3, cy0 + 3, cx0 + cup_w - 3, cy0 + int(cup_h * 0.35)],
                     fill=(*J_DARK, 200))

        # Steam wisps
        for wi in range(3):
            wx = cx0 + int(cup_w * (0.25 + wi * 0.25))
            for seg in range(4):
                t = (steam_phase + wi * 0.33 + seg * 0.1) % 1.0
                wy_base = cy0 - int(sq * 0.18) - int(seg * sq * 0.06)
                wave_x = int(4 * math.sin(2 * math.pi * t + seg))
                alpha = max(0, int(180 * (1 - seg * 0.25) * t))
                d2.ellipse([wx + wave_x - 2, wy_base - 2,
                            wx + wave_x + 2, wy_base + 2],
                           fill=(255, 255, 255, alpha))

        # JAVA text below cup
        font_size = max(7, int(sq * 0.22))
        try:
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font_b = ImageFont.load_default()

        txt = "JAVA"
        bbox = d2.textbbox((0, 0), txt, font=font_b)
        tw = bbox[2] - bbox[0]
        tx = cx - tw // 2
        ty = cy0 + cup_h + int(sq * 0.04)
        d2.text((tx, ty), txt, font=font_b, fill=(*J_ORANGE, 255))

        frames.append(img)
    save_gif(frames, "java.gif")


def gen_python():
    """Python two-snake logo with color-cycling glow."""
    PY_BLUE   = (55, 118, 171)
    PY_YELLOW = (255, 212, 59)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        glow_s = pulse(i, FRAMES, 0.0, 0.6)
        offset_y = int(3 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.42 * scale), PY_BLUE,
                         alpha_max=int(glow_s * 130))

        d = ImageDraw.Draw(img)
        sq = int(SIZE * 0.70 * scale)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y

        # Draw two interleaved snake-body blobs
        r = int(sq * 0.28)

        # Blue snake (top-left quadrant)
        d.ellipse([cx - r - int(r * 0.3), cy - r - int(r * 0.3),
                   cx + int(r * 0.3), cy + int(r * 0.3)],
                  fill=(*PY_BLUE, 255))
        # Yellow snake (bottom-right quadrant)
        d.ellipse([cx - int(r * 0.3), cy - int(r * 0.3),
                   cx + r + int(r * 0.3), cy + r + int(r * 0.3)],
                  fill=(*PY_YELLOW, 255))

        # Snake head bumps
        d.ellipse([cx - r * 2 + int(r * 0.1), cy - int(r * 0.4),
                   cx - r + int(r * 0.5), cy + int(r * 0.4)],
                  fill=(*PY_BLUE, 255))
        d.ellipse([cx + r - int(r * 0.5), cy - int(r * 0.4),
                   cx + r * 2 - int(r * 0.1), cy + int(r * 0.4)],
                  fill=(*PY_YELLOW, 255))

        # Eyes
        d.ellipse([cx - r + int(r * 0.05), cy - int(r * 0.15),
                   cx - r + int(r * 0.25), cy + int(r * 0.15)],
                  fill=(255, 255, 255, 220))
        d.ellipse([cx + r - int(r * 0.25), cy - int(r * 0.15),
                   cx + r - int(r * 0.05), cy + int(r * 0.15)],
                  fill=(255, 255, 255, 220))

        frames.append(img)
    save_gif(frames, "python.gif")


def gen_react():
    """React atom logo with rotating orbits."""
    R_CYAN  = (97, 218, 251)
    R_DARK  = (32, 35, 42)
    frames = []
    for i in range(FRAMES):
        angle = 2 * math.pi * i / FRAMES
        glow_s = pulse(i, FRAMES, 0.3, 0.8)

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2, int(SIZE * 0.38),
                         R_CYAN, alpha_max=int(glow_s * 120))

        d = ImageDraw.Draw(img)
        cx, cy = SIZE // 2, SIZE // 2
        rx, ry = int(SIZE * 0.4), int(SIZE * 0.18)

        # 3 elliptic orbits at 60Â° apart
        for orbit_angle in [0, math.pi / 3 * 2, math.pi / 3 * 4]:
            oa = orbit_angle + angle
            # draw orbit ellipse (rotated by oa)
            pts = []
            for t in range(36):
                ta = 2 * math.pi * t / 36
                px = cx + rx * math.cos(ta) * math.cos(oa) - ry * math.sin(ta) * math.sin(oa)
                py = cy + rx * math.cos(ta) * math.sin(oa) + ry * math.sin(ta) * math.cos(oa)
                pts.append((px, py))
            if len(pts) > 1:
                d.line(pts + [pts[0]], fill=(*R_CYAN, 220), width=2)

            # electron dot on orbit
            et = (i / FRAMES) % 1.0
            ta = 2 * math.pi * et
            ex = cx + rx * math.cos(ta) * math.cos(oa) - ry * math.sin(ta) * math.sin(oa)
            ey = cy + rx * math.cos(ta) * math.sin(oa) + ry * math.sin(ta) * math.cos(oa)
            d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(*R_CYAN, 255))

        # nucleus
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(*R_CYAN, 255))

        frames.append(img)
    save_gif(frames, "react.gif")


def gen_vite():
    """Vite lightning-bolt logo with electric pulse."""
    V_PURPLE = (100, 65, 165)
    V_YELLOW = (255, 188, 0)
    V_CYAN   = (66, 211, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        glow_s = pulse(i, FRAMES, 0.2, 0.8)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.38 * scale), V_PURPLE,
                         alpha_max=int(glow_s * 150))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y

        sq = int(SIZE * 0.7 * scale)
        half = sq // 2

        # Vite "V" outer diamond
        diamond_pts = [
            (cx, cy - half),
            (cx + half, cy),
            (cx, cy + half),
            (cx - half, cy),
        ]
        d.polygon(diamond_pts, fill=(*V_PURPLE, 220))

        # Lightning bolt (simple polygon)
        bw = int(sq * 0.22)
        bolt = [
            (cx + int(bw * 0.3), cy - int(half * 0.65)),
            (cx - int(bw * 0.2), cy - int(half * 0.05)),
            (cx + int(bw * 0.2), cy - int(half * 0.05)),
            (cx - int(bw * 0.3), cy + int(half * 0.65)),
            (cx + int(bw * 0.5), cy + int(half * 0.1)),
            (cx - int(bw * 0.1), cy + int(half * 0.1)),
        ]
        d.polygon(bolt, fill=(*V_YELLOW, 255))

        # Electric sparks at tip
        spark_a = glow_s
        for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
            sx = cx + int(half * 0.72 * math.cos(angle + 2 * math.pi * i / FRAMES))
            sy = cy + int(half * 0.72 * math.sin(angle + 2 * math.pi * i / FRAMES))
            alpha = int(spark_a * 200)
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2],
                      fill=(*V_CYAN, alpha))

        frames.append(img)
    save_gif(frames, "vite.gif")


def gen_tailwind():
    """Tailwind CSS wind-whoosh logo."""
    TW_CYAN  = (14, 165, 233)
    TW_DARK  = (6, 95, 130)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        sweep  = (i / FRAMES)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.4 * scale), TW_CYAN,
                         alpha_max=int(pulse(i, FRAMES, 20, 110)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        sq = int(SIZE * 0.74 * scale)

        # Draw a rounded badge background
        x0 = cx - sq // 2
        y0 = cy - sq // 2
        draw_rounded_rect(d, [x0, y0, x0 + sq, y0 + sq], radius=10,
                          fill=(15, 23, 42, 240))

        # Tailwind "T" droplet curves â€” two cloud-like blobs
        curve_col = (*TW_CYAN, 255)
        r1 = int(sq * 0.20)
        # Left blob
        d.ellipse([cx - int(sq * 0.35), cy - r1,
                   cx + int(sq * 0.05), cy + r1],
                  fill=curve_col)
        d.ellipse([cx - int(sq * 0.22), cy - r1 * 2,
                   cx + int(sq * 0.08), cy],
                  fill=curve_col)
        # Right blob
        d.ellipse([cx - int(sq * 0.05), cy - r1,
                   cx + int(sq * 0.35), cy + r1],
                  fill=curve_col)
        d.ellipse([cx - int(sq * 0.08), cy,
                   cx + int(sq * 0.22), cy + r1 * 2],
                  fill=curve_col)

        # Sweep shine
        overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        sx = x0 + int(sweep * (sq + int(sq * 0.2)))
        od.rectangle([sx - int(sq * 0.08), y0,
                      sx + int(sq * 0.08), y0 + sq],
                     fill=(255, 255, 255, 35))
        img.alpha_composite(overlay)

        frames.append(img)
    save_gif(frames, "tailwind.gif")


def gen_sass():
    """Sass pink logo with orbital glow."""
    S_PINK  = (207, 100, 154)
    S_DARK  = (160, 65, 115)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        offset_y = int(3 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.42 * scale), S_PINK,
                         alpha_max=int(pulse(i, FRAMES, 30, 120)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        sq = int(SIZE * 0.70 * scale)
        r = sq // 2

        # Pink circle badge
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*S_PINK, 255))

        # "Sass" swash text
        font_size = max(7, int(sq * 0.32))
        try:
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font_b = ImageFont.load_default()

        txt = "Sass"
        bbox = d.textbbox((0, 0), txt, font=font_b)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        d.text((cx - tw // 2, cy - th // 2), txt, font=font_b,
               fill=(255, 255, 255, 255))

        frames.append(img)
    save_gif(frames, "sass.gif")


def gen_nodejs():
    """Node.js green hexagon with pulse."""
    N_GREEN  = (104, 160, 99)
    N_DARK   = (50, 90, 45)
    WHITE    = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.42 * scale), N_GREEN,
                         alpha_max=int(pulse(i, FRAMES, 30, 130)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        r = int(SIZE * 0.38 * scale)

        # Hexagon
        hex_pts = []
        for k in range(6):
            angle = math.pi / 6 + k * math.pi / 3
            hx = cx + int(r * math.cos(angle))
            hy = cy + int(r * math.sin(angle))
            hex_pts.append((hx, hy))
        d.polygon(hex_pts, fill=(*N_GREEN, 255))

        font_size = max(6, int(r * 0.46))
        try:
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font_b = ImageFont.load_default()

        for txt, dy_f in [("Node", -0.28), (".js", 0.26)]:
            bbox = d.textbbox((0, 0), txt, font=font_b)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            ty = cy + int(dy_f * r * 2) - th // 2
            d.text((cx - tw // 2, ty), txt, font=font_b, fill=(*WHITE, 255))

        frames.append(img)
    save_gif(frames, "nodejs.gif")


def gen_express():
    """Express.js dark badge with sequential light sweep."""
    EX_DARK  = (25, 25, 25)
    EX_WHITE = (240, 240, 240)
    EX_GRAY  = (150, 150, 150)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        sweep  = (i / FRAMES)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        d = ImageDraw.Draw(img)
        sq = int(SIZE * 0.76 * scale)
        x0 = (SIZE - sq) // 2
        y0 = (SIZE - sq) // 2 + offset_y

        draw_rounded_rect(d, [x0, y0, x0 + sq, y0 + sq], radius=8,
                          fill=(*EX_DARK, 255),
                          outline=(*EX_GRAY, 100), width=1)

        font_size = max(7, int(sq * 0.30))
        try:
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font_b = ImageFont.load_default()

        for txt, dy_f in [("Express", -0.20), (".js", 0.24)]:
            bbox = d.textbbox((0, 0), txt, font=font_b)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            cx = x0 + sq // 2
            cy = y0 + sq // 2
            ty = cy + int(dy_f * sq) - th // 2
            d.text((cx - tw // 2, ty), txt, font=font_b,
                   fill=(*EX_WHITE, 255))

        # Light sweep
        overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        sx = x0 + int(sweep * (sq + int(sq * 0.2)))
        od.rectangle([sx - int(sq * 0.07), y0,
                      sx + int(sq * 0.07), y0 + sq],
                     fill=(255, 255, 255, 28))
        img.alpha_composite(overlay)

        frames.append(img)
    save_gif(frames, "express.gif")


def gen_mongodb():
    """MongoDB green leaf with scale pulse."""
    M_GREEN  = (0, 237, 100)
    M_DARK   = (19, 170, 82)
    M_LEAF   = (58, 191, 113)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        offset_y = int(3 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.40 * scale), M_GREEN,
                         alpha_max=int(pulse(i, FRAMES, 20, 120)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        sq = int(SIZE * 0.68 * scale)

        # MongoDB leaf: tapered oval
        lw = int(sq * 0.28)
        lh = int(sq * 0.72)
        lx0 = cx - lw // 2
        ly0 = cy - lh // 2
        d.ellipse([lx0, ly0, lx0 + lw, ly0 + lh], fill=(*M_LEAF, 255))

        # Stem
        sw = max(2, int(lw * 0.15))
        d.rectangle([cx - sw // 2, cy + lh // 2 - int(lh * 0.15),
                     cx + sw // 2, cy + lh // 2 + int(lh * 0.12)],
                    fill=(*M_DARK, 255))

        # White highlight on leaf
        hl_w = max(2, int(lw * 0.3))
        hl_h = int(lh * 0.6)
        d.ellipse([cx - hl_w // 2 - int(lw * 0.06),
                   ly0 + int(lh * 0.08),
                   cx - hl_w // 2 - int(lw * 0.06) + hl_w,
                   ly0 + int(lh * 0.08) + hl_h],
                  fill=(255, 255, 255, 60))

        frames.append(img)
    save_gif(frames, "mongodb.gif")


def gen_postgresql():
    """PostgreSQL blue elephant head."""
    PG_BLUE   = (51, 103, 145)
    PG_DARK   = (31, 71, 110)
    PG_LIGHT  = (120, 170, 210)
    WHITE     = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.40 * scale), PG_BLUE,
                         alpha_max=int(pulse(i, FRAMES, 30, 130)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        sq = int(SIZE * 0.68 * scale)
        r = sq // 2

        # Head circle
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*PG_BLUE, 255))

        # Ears
        ear_r = int(r * 0.30)
        d.ellipse([cx - r - ear_r // 2, cy - r + ear_r // 2,
                   cx - r + ear_r, cy - r + ear_r * 2],
                  fill=(*PG_DARK, 255))
        d.ellipse([cx + r - ear_r, cy - r + ear_r // 2,
                   cx + r + ear_r // 2, cy - r + ear_r * 2],
                  fill=(*PG_DARK, 255))

        # Trunk
        trunk_w = int(r * 0.22)
        trunk_h = int(r * 0.55)
        d.rounded_rectangle([cx - trunk_w // 2, cy + r - int(r * 0.15),
                              cx + trunk_w // 2, cy + r + trunk_h],
                             radius=trunk_w // 2, fill=(*PG_LIGHT, 255))

        # Eyes
        eye_r = max(2, int(r * 0.10))
        d.ellipse([cx - int(r * 0.30) - eye_r, cy - int(r * 0.1) - eye_r,
                   cx - int(r * 0.30) + eye_r, cy - int(r * 0.1) + eye_r],
                  fill=(*WHITE, 255))
        d.ellipse([cx + int(r * 0.30) - eye_r, cy - int(r * 0.1) - eye_r,
                   cx + int(r * 0.30) + eye_r, cy - int(r * 0.1) + eye_r],
                  fill=(*WHITE, 255))

        frames.append(img)
    save_gif(frames, "postgresql.gif")


def gen_git():
    """Git branching logo with animated merge flow."""
    G_RED    = (240, 80, 51)
    G_WHITE  = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        flow   = (i / FRAMES)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.40 * scale), G_RED,
                         alpha_max=int(pulse(i, FRAMES, 30, 130)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        r = int(SIZE * 0.38 * scale)

        # Circle background
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*G_RED, 255))

        # Git diamond icon (simplified)
        dm = int(r * 0.55)
        # Rotated square (diamond)
        pts = [
            (cx, cy - dm),
            (cx + dm, cy),
            (cx, cy + dm),
            (cx - dm, cy),
        ]
        d.polygon(pts, fill=None, outline=(*G_WHITE, 255))
        d.line([(cx - dm, cy), (cx + dm, cy)], fill=(*G_WHITE, 255), width=2)
        d.line([(cx, cy - dm), (cx, cy + dm)], fill=(*G_WHITE, 255), width=2)

        # Animated flow dot
        angle = 2 * math.pi * flow
        fx = cx + int(dm * math.cos(angle + math.pi / 4))
        fy = cy + int(dm * math.sin(angle + math.pi / 4))
        d.ellipse([fx - 3, fy - 3, fx + 3, fy + 3],
                  fill=(*G_WHITE, 200))

        frames.append(img)
    save_gif(frames, "git.gif")


def gen_github():
    """GitHub Octocat logo with glowing orbit."""
    GH_DARK  = (36, 41, 47)
    GH_WHITE = (255, 255, 255)
    GH_GRAY  = (180, 190, 200)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        angle  = 2 * math.pi * i / FRAMES
        glow_s = pulse(i, FRAMES, 0.2, 0.7)
        offset_y = int(2 * math.sin(angle))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.42 * scale), GH_GRAY,
                         alpha_max=int(glow_s * 110))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        r  = int(SIZE * 0.40 * scale)

        # Main circle
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*GH_DARK, 255))

        # Octocat head (simplified)
        head_r = int(r * 0.45)
        d.ellipse([cx - head_r, cy - head_r - int(r * 0.05),
                   cx + head_r, cy + head_r - int(r * 0.05)],
                  fill=(*GH_WHITE, 255))

        # Ears
        ear_r = int(r * 0.14)
        d.ellipse([cx - head_r + int(r * 0.05),
                   cy - head_r - ear_r - int(r * 0.05),
                   cx - head_r + int(r * 0.05) + ear_r * 2,
                   cy - head_r - int(r * 0.05)],
                  fill=(*GH_WHITE, 255))
        d.ellipse([cx + head_r - int(r * 0.05) - ear_r * 2,
                   cy - head_r - ear_r - int(r * 0.05),
                   cx + head_r - int(r * 0.05),
                   cy - head_r - int(r * 0.05)],
                  fill=(*GH_WHITE, 255))

        # Eyes
        ey = cy - int(r * 0.05)
        er = max(2, int(head_r * 0.15))
        d.ellipse([cx - int(head_r * 0.4) - er, ey - er,
                   cx - int(head_r * 0.4) + er, ey + er],
                  fill=(*GH_DARK, 255))
        d.ellipse([cx + int(head_r * 0.4) - er, ey - er,
                   cx + int(head_r * 0.4) + er, ey + er],
                  fill=(*GH_DARK, 255))

        # Tentacles (octocat)
        for ti in range(4):
            tx_off = int(r * (-0.30 + ti * 0.20))
            ty_start = cy + int(r * 0.38)
            ty_end   = cy + int(r * 0.80)
            d.line([(cx + tx_off, ty_start),
                    (cx + tx_off + int(r * 0.08), ty_end)],
                   fill=(*GH_WHITE, 200), width=max(1, int(r * 0.05)))

        # Orbiting star
        sx = cx + int(r * 1.0 * math.cos(angle))
        sy = cy + int(r * 1.0 * math.sin(angle))
        alpha = max(0, int(glow_s * 200))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2],
                  fill=(*GH_WHITE, alpha))

        frames.append(img)
    save_gif(frames, "github.gif")


def gen_vscode():
    """VS Code blue logo with animated cursor blink."""
    VS_BLUE   = (0, 122, 204)
    VS_DARK   = (0, 75, 140)
    VS_WHITE  = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        blink = (i % 8) < 4   # cursor blink at ~2 Hz
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.40 * scale), VS_BLUE,
                         alpha_max=int(pulse(i, FRAMES, 30, 130)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        sq = int(SIZE * 0.68 * scale)

        # Outer rounded square
        x0 = cx - sq // 2
        y0 = cy - sq // 2
        draw_rounded_rect(d, [x0, y0, x0 + sq, y0 + sq], radius=10,
                          fill=(*VS_BLUE, 255))

        # "<" bracket left
        brace_x = x0 + int(sq * 0.20)
        brace_y = cy
        brace_h = int(sq * 0.28)
        brace_w = int(sq * 0.12)
        brace_pts = [
            (brace_x + brace_w, brace_y - brace_h),
            (brace_x, brace_y),
            (brace_x + brace_w, brace_y + brace_h),
        ]
        d.line(brace_pts, fill=(*VS_WHITE, 220), width=max(2, int(sq * 0.06)))

        # ">" bracket right
        brace_x2 = x0 + int(sq * 0.80)
        brace_pts2 = [
            (brace_x2 - brace_w, brace_y - brace_h),
            (brace_x2, brace_y),
            (brace_x2 - brace_w, brace_y + brace_h),
        ]
        d.line(brace_pts2, fill=(*VS_WHITE, 220), width=max(2, int(sq * 0.06)))

        # Blinking cursor
        if blink:
            cur_x = cx - int(sq * 0.05)
            cur_y = cy - int(sq * 0.15)
            cur_h = int(sq * 0.30)
            d.rectangle([cur_x, cur_y, cur_x + max(2, int(sq * 0.05)), cur_y + cur_h],
                        fill=(*VS_WHITE, 220))

        frames.append(img)
    save_gif(frames, "vscode.gif")


def gen_postman():
    """Postman orange logo with rocket launch animation."""
    PM_ORANGE = (255, 108, 55)
    PM_DARK   = (200, 75, 30)
    PM_WHITE  = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        launch = (i / FRAMES)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.40 * scale), PM_ORANGE,
                         alpha_max=int(pulse(i, FRAMES, 30, 140)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        r = int(SIZE * 0.38 * scale)

        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*PM_ORANGE, 255))

        # Postman "P" letter (rounded)
        font_size = max(8, int(r * 1.0))
        try:
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font_b = ImageFont.load_default()

        txt = "P"
        bbox = d.textbbox((0, 0), txt, font=font_b)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        d.text((cx - tw // 2, cy - th // 2), txt, font=font_b,
               fill=(*PM_WHITE, 255))

        # Animated API arrow
        arr_y = cy + int(r * 0.55)
        arr_x_start = cx - int(r * 0.45)
        arr_x_end   = cx + int(r * 0.45)
        arr_prog    = int(arr_x_start + (arr_x_end - arr_x_start) * launch)
        d.line([(arr_x_start, arr_y), (arr_prog, arr_y)],
               fill=(*PM_WHITE, 200), width=2)
        # Arrowhead
        if arr_prog > arr_x_start + 6:
            d.polygon([(arr_prog, arr_y),
                       (arr_prog - 5, arr_y - 3),
                       (arr_prog - 5, arr_y + 3)],
                      fill=(*PM_WHITE, 200))

        frames.append(img)
    save_gif(frames, "postman.gif")


def gen_vercel():
    """Vercel triangle logo with deploy-beam animation."""
    VC_WHITE = (255, 255, 255)
    VC_DARK  = (10, 10, 10)
    VC_BEAM  = (200, 200, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        beam_h = (i / FRAMES)
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        d = ImageDraw.Draw(img)

        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        sq = int(SIZE * 0.72 * scale)

        # Dark rounded bg
        x0 = cx - sq // 2
        y0 = cy - sq // 2
        draw_rounded_rect(d, [x0, y0, x0 + sq, y0 + sq], radius=10,
                          fill=(*VC_DARK, 255))

        # Vercel triangle
        tri_h = int(sq * 0.55)
        tri_w = int(sq * 0.65)
        tri_top = (cx, cy - int(sq * 0.22))
        tri_bl  = (cx - tri_w // 2, cy - int(sq * 0.22) + tri_h)
        tri_br  = (cx + tri_w // 2, cy - int(sq * 0.22) + tri_h)
        d.polygon([tri_top, tri_bl, tri_br], fill=(*VC_WHITE, 255))

        # Deploy beam (animated vertical line rising from triangle)
        beam_start = tri_top[1]
        beam_end   = y0 + int((beam_start - y0) * (1 - beam_h))
        if beam_start > beam_end:
            for bx_off in [-1, 0, 1]:
                alpha = max(0, 200 - abs(bx_off) * 80)
                d.line([(cx + bx_off, beam_end),
                        (cx + bx_off, beam_start)],
                       fill=(*VC_BEAM, alpha), width=1)

        frames.append(img)
    save_gif(frames, "vercel.gif")


def gen_render():
    """Render.com purple cloud logo with cloud-fill animation."""
    R_PURPLE = (70, 20, 190)
    R_LIGHT  = (130, 80, 240)
    R_WHITE  = (255, 255, 255)
    frames = []
    for i in range(FRAMES):
        scale = pulse(i, FRAMES, 0.84, 1.0)
        fill_frac = (0.5 + 0.5 * math.sin(2 * math.pi * i / FRAMES))
        offset_y = int(2 * math.sin(2 * math.pi * i / FRAMES))

        img = new_frame()
        draw_circle_glow(img, SIZE // 2, SIZE // 2 + offset_y,
                         int(SIZE * 0.40 * scale), R_PURPLE,
                         alpha_max=int(pulse(i, FRAMES, 30, 130)))

        d = ImageDraw.Draw(img)
        cx = SIZE // 2
        cy = SIZE // 2 + offset_y
        sq = int(SIZE * 0.68 * scale)

        # Rounded bg badge
        x0 = cx - sq // 2
        y0 = cy - sq // 2
        draw_rounded_rect(d, [x0, y0, x0 + sq, y0 + sq], radius=10,
                          fill=(*R_PURPLE, 255))

        # Cloud shape (3 circles + base rect)
        cloud_y = cy - int(sq * 0.05)
        cr = int(sq * 0.18)
        # Left bump
        d.ellipse([cx - int(sq * 0.30), cloud_y - cr,
                   cx - int(sq * 0.30) + cr * 2, cloud_y + cr],
                  fill=(*R_LIGHT, 255))
        # Center bump
        d.ellipse([cx - cr, cloud_y - cr - int(cr * 0.3),
                   cx + cr, cloud_y + cr - int(cr * 0.3)],
                  fill=(*R_LIGHT, 255))
        # Right bump
        d.ellipse([cx + int(sq * 0.30) - cr * 2, cloud_y - cr,
                   cx + int(sq * 0.30), cloud_y + cr],
                  fill=(*R_LIGHT, 255))
        # Base rect
        d.rectangle([cx - int(sq * 0.38), cloud_y,
                     cx + int(sq * 0.38), cloud_y + cr + int(cr * 0.3)],
                    fill=(*R_LIGHT, 255))

        # Fill animation line (upload indicator)
        fill_y = cloud_y + cr + int(cr * 0.3) - int((cr + int(cr * 0.3)) * fill_frac)
        overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle([cx - int(sq * 0.38), fill_y,
                      cx + int(sq * 0.38), cloud_y + cr + int(cr * 0.3)],
                     fill=(*R_WHITE, 40))
        img.alpha_composite(overlay)

        # "R" letter
        font_size = max(7, int(sq * 0.28))
        try:
            font_b = ImageFont.truetype("arialbd.ttf", font_size)
        except Exception:
            font_b = ImageFont.load_default()
        txt = "R"
        bbox = d.textbbox((0, 0), txt, font=font_b)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        d.text((cx - tw // 2, cloud_y + int(sq * 0.22) - th // 2), txt,
               font=font_b, fill=(*R_WHITE, 255))

        frames.append(img)
    save_gif(frames, "render.gif")


# â”€â”€â”€ main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

GENERATORS = [
    ("javascript", gen_javascript),
    ("html5",      gen_html5),
    ("css3",       gen_css3),
    ("java",       gen_java),
    ("python",     gen_python),
    ("react",      gen_react),
    ("vite",       gen_vite),
    ("tailwind",   gen_tailwind),
    ("sass",       gen_sass),
    ("nodejs",     gen_nodejs),
    ("express",    gen_express),
    ("mongodb",    gen_mongodb),
    ("postgresql", gen_postgresql),
    ("git",        gen_git),
    ("github",     gen_github),
    ("vscode",     gen_vscode),
    ("postman",    gen_postman),
    ("vercel",     gen_vercel),
    ("render",     gen_render),
]


def verify_all():
    """Re-open every GIF and confirm frame count > 1."""
    print("\nâ”€â”€ Verification â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
    ok = []
    fail = []
    for name, _ in GENERATORS:
        path = os.path.join(OUTPUT_DIR, f"{name}.gif")
        if not os.path.exists(path):
            fail.append(name)
            print(f"  âœ—  {name}.gif  MISSING")
            continue
        try:
            with Image.open(path) as img:
                n = getattr(img, "n_frames", 1)
            if n > 1:
                ok.append(name)
                print(f"  âœ“  {name}.gif  ({n} frames)")
            else:
                fail.append(name)
                print(f"  âœ—  {name}.gif  only {n} frame â€” NOT animated")
        except Exception as e:
            fail.append(name)
            print(f"  âœ—  {name}.gif  error: {e}")
    print(f"\nResult: {len(ok)}/{len(ok)+len(fail)} GIFs verified as animated.")
    return fail


def main():
    print(f"Generating {len(GENERATORS)} animated GIF logos -> {OUTPUT_DIR}\n")
    errors = []
    for name, fn in GENERATORS:
        try:
            print(f"  â†’ {name} â€¦", end=" ", flush=True)
            fn()
        except Exception as e:
            print(f"  ERROR: {e}")
            errors.append((name, str(e)))

    failures = verify_all()

    if errors:
        print("\nâ”€â”€ Generation errors â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
        for name, err in errors:
            print(f"  {name}: {err}")

    if failures:
        sys.exit(1)
    print("\nâœ…  All animated GIFs generated successfully.")


if __name__ == "__main__":
    main()

