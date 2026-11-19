"""Renders the Modrinth icon and banners for Vault Reset from vanilla textures.

Textures and the font are read straight from an official Minecraft client.jar, so none of
Mojang's files are stored in this repo:

    python modrinth/render.py --client-jar path/to/26.3/client.jar

The client.jar is listed in Mojang's version manifest
(https://piston-meta.mojang.com/mc/game/version_manifest_v2.json -> 26.3 -> downloads.client).
Everything is scaled with NEAREST so pixels stay crisp. Output lands next to this script.
"""
from __future__ import annotations

import argparse
import io
import math
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE


def _client_jar() -> zipfile.ZipFile:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--client-jar", required=True, type=Path)
    return zipfile.ZipFile(ap.parse_args().client_jar)


JAR = _client_jar() if __name__ == "__main__" else None


def tex(name: str) -> Image.Image:
    data = JAR.read(f"assets/minecraft/textures/{name}.png")
    return Image.open(io.BytesIO(data)).convert("RGBA")


def shade(img: Image.Image, f: float) -> Image.Image:
    r, g, b, a = img.split()
    r, g, b = (ch.point(lambda v: min(255, int(v * f))) for ch in (r, g, b))
    return Image.merge("RGBA", (r, g, b, a))


def up(img: Image.Image, k: int) -> Image.Image:
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


# ---------------------------------------------------------------- iso block
def _face(canvas_size, texture, origin, U, V, f):
    """Draws a texture as the parallelogram origin + u*U + v*V."""
    t = shade(texture, f)
    tw, th = t.size
    (ux, uy), (vx, vy) = U, V
    det = ux * vy - vx * uy
    p, q, r, s = vy / det, -vx / det, -uy / det, ux / det
    ox, oy = origin
    a, b = tw * p, tw * q
    c = -tw * (p * ox + q * oy)
    d, e = th * r, th * s
    ff = -th * (r * ox + s * oy)
    return t.transform(canvas_size, Image.AFFINE, (a, b, c, d, e, ff), resample=Image.NEAREST)


def iso_block(top, left, right, W: int, shades=(1.0, 0.86, 0.62)) -> Image.Image:
    H = round(W * 0.577)
    size = (W, W // 2 + H + 1)
    L, B, R = (0, W / 4), (W / 2, W / 2), (W, W / 4)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    # small overlap against seams between faces
    eps = 1.0
    faces = [
        _face(size, left, (L[0], L[1]), (W / 2 + eps, W / 4 + eps / 2), (0, H + eps), shades[1]),
        _face(size, right, (B[0] - eps, B[1]), (W / 2 + eps, -W / 4 - eps / 2), (0, H + eps), shades[2]),
        _face(size, top, (L[0], L[1]), (W / 2, -W / 4), (W / 2, W / 4), shades[0]),
    ]
    for f in faces:
        out = Image.alpha_composite(out, f)
    return out


# ---------------------------------------------------------------- pixel arrow
def reset_arrow(grid=20, k=8, color=(108, 229, 232), outline=(20, 52, 58)) -> Image.Image:
    """Clockwise circular arrow on a small grid, then scaled up."""
    big = 8  # draw finely first, then reduce to the grid
    G = grid * big
    m = Image.new("L", (G, G), 0)
    d = ImageDraw.Draw(m)
    c = G / 2
    r_out, r_in = G * 0.36, G * 0.20
    a0, a1 = 25, 290  # arc from bottom right, clockwise, to the top
    d.pieslice((c - r_out, c - r_out, c + r_out, c + r_out), a0, a1, fill=255)
    d.pieslice((c - r_in, c - r_in, c + r_in, c + r_in), a0 - 5, a1 + 5, fill=0)
    th = math.radians(a1)
    mid = (r_in + r_out) / 2
    ex, ey = c + mid * math.cos(th), c + mid * math.sin(th)
    tx, ty = -math.sin(th), math.cos(th)  # direction of travel (clockwise, y points down)
    nx, ny = math.cos(th), math.sin(th)
    hw = (r_out - r_in) * 1.05
    tip = (ex + tx * hw * 1.25, ey + ty * hw * 1.25)
    b1 = (ex + nx * hw - tx * 2, ey + ny * hw - ty * 2)
    b2 = (ex - nx * hw - tx * 2, ey - ny * hw - ty * 2)
    d.polygon([tip, b1, b2], fill=255)
    small = m.resize((grid, grid), Image.BOX).point(lambda v: 255 if v > 110 else 0)
    shape = {(x, y) for y in range(grid) for x in range(grid) if small.getpixel((x, y))}
    g = Image.new("RGBA", (grid, grid), (0, 0, 0, 0))
    px = g.load()
    for (x, y) in shape:
        px[x, y] = color + (255,)
        if (x - 1, y) not in shape or (x, y - 1) not in shape:
            px[x, y] = tuple(min(255, v + 60) for v in color) + (255,)
        elif (x + 1, y) not in shape or (x, y + 1) not in shape:
            px[x, y] = tuple(int(v * 0.72) for v in color) + (255,)
    for y in range(grid):
        for x in range(grid):
            if (x, y) not in shape and any((x + ax, y + ay) in shape for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = outline + (255,)
    return up(g, k)


# ---------------------------------------------------------------- MC font
class McFont:
    def __init__(self):
        sheet = tex("font/ascii")
        self.glyphs = {}
        for code in range(256):
            gx, gy = (code % 16) * 8, (code // 16) * 8
            g = sheet.crop((gx, gy, gx + 8, gy + 8))
            alpha = g.split()[3]
            bbox = alpha.getbbox()
            width = (bbox[2] if bbox else 0)
            self.glyphs[chr(code)] = (g, width)

    def measure(self, text: str) -> int:
        w = 0
        for ch in text:
            if ch == " ":
                w += 4
            else:
                w += self.glyphs.get(ch, self.glyphs["?"])[1] + 1
        return w - 1

    def render(self, text: str, color=(255, 255, 255), shadow=True, bold=False) -> Image.Image:
        w = self.measure(text) + (1 if bold else 0) + 1
        img = Image.new("RGBA", (w + 1, 9), (0, 0, 0, 0))

        def draw(col, off):
            x = 0
            for ch in text:
                if ch == " ":
                    x += 4
                    continue
                g, gw = self.glyphs.get(ch, self.glyphs["?"])
                tint = Image.new("RGBA", g.size, col + (255,))
                tint.putalpha(g.split()[3])
                for b in ((0, 1) if bold else (0,)):
                    img.alpha_composite(tint, (x + off[0] + b, off[1]))
                x += gw + 1 + (1 if bold else 0)

        if shadow:
            draw(tuple(v // 4 for v in color), (1, 1))
        draw(color, (0, 0))
        return img


FONT = McFont()


def text_img(s, k, color=(255, 255, 255), bold=False, shadow=True):
    return up(FONT.render(s, color, shadow=shadow, bold=bold), k)


# ---------------------------------------------------------------- backgrounds
def tiled(texture: Image.Image, k: int, size, f=1.0) -> Image.Image:
    t = shade(up(texture, k), f)
    out = Image.new("RGBA", size)
    for y in range(0, size[1], t.height):
        for x in range(0, size[0], t.width):
            out.paste(t, (x, y))
    return out


def vignette(size, strength=0.75, color=(8, 10, 12)) -> Image.Image:
    w, h = size
    mask = Image.new("L", (w // 8, h // 8), 0)
    mp = mask.load()
    for y in range(mask.height):
        for x in range(mask.width):
            dx = (x / (mask.width - 1) - 0.5) * 2
            dy = (y / (mask.height - 1) - 0.5) * 2
            d = min(1.0, math.hypot(dx * 0.85, dy))
            mp[x, y] = int(255 * strength * d ** 1.8)
    mask = mask.resize(size, Image.BILINEAR)
    layer = Image.new("RGBA", size, color + (255,))
    layer.putalpha(mask)
    return layer


def glow(size, center, radius, color, alpha=170) -> Image.Image:
    g = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    cx, cy = center
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color + (alpha,))
    return g.filter(ImageFilter.GaussianBlur(radius * 0.45))


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    return m


def drop_shadow(img: Image.Image, off=(0, 18), blur=18, alpha=150) -> Image.Image:
    a = img.split()[3].point(lambda v: alpha if v > 0 else 0)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(a)
    pad = blur * 3
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    canvas.alpha_composite(sh, (pad + off[0], pad + off[1]))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(img, (pad, pad))
    return canvas, pad


# ---------------------------------------------------------------- textures
VAULT_FRONT = tex("block/vault_front_on")
VAULT_SIDE = tex("block/vault_side_on")
VAULT_TOP = tex("block/vault_top")
OM_FRONT = tex("block/vault_front_on_ominous")
OM_SIDE = tex("block/vault_side_on_ominous")
OM_TOP = tex("block/vault_top_ominous")
TUFF_BRICKS = tex("block/tuff_bricks")
CH_TUFF_BRICKS = tex("block/chiseled_tuff_bricks")
POL_TUFF = tex("block/polished_tuff")
CH_TUFF = tex("block/chiseled_tuff")
BULB = tex("block/copper_bulb_lit")
GRATE = tex("block/copper_grate")
CH_COPPER = tex("block/chiseled_copper")
KEY = tex("item/trial_key")
CLOCK = tex("item/clock_16")

S = 512


def icon_backdrop(texture=TUFF_BRICKS, k=8, f=0.42):
    bg = tiled(texture, k, (S, S), f)
    bg.alpha_composite(vignette((S, S), 0.8))
    return bg


def finish_icon(img: Image.Image, name: str):
    img = img.copy()
    img.putalpha(Image.composite(img.split()[3], Image.new("L", img.size, 0), rounded_mask(img.size, 64)))
    img.save(OUT / f"{name}.png")
    return img


def icon_a():
    """Isometric vault with a reset arrow badge at the bottom right (the chosen icon)."""
    img = icon_backdrop()
    img.alpha_composite(glow((S, S), (256, 280), 170, (255, 150, 40), 120))
    blk = iso_block(VAULT_TOP, VAULT_FRONT, VAULT_SIDE, 330)
    blk, pad = drop_shadow(blk, (0, 16), 14, 160)
    img.alpha_composite(blk, (256 - blk.width // 2, 262 - blk.height // 2))
    arr = reset_arrow(20, 8)
    img.alpha_composite(arr, (S - arr.width - 18, S - arr.height - 18))
    return finish_icon(img, "icon")


def icon_b():
    """Isometric vault with a trial key and a clock badge (alternative)."""
    img = icon_backdrop(CH_TUFF_BRICKS, 8, 0.36)
    img.alpha_composite(glow((S, S), (256, 250), 180, (255, 160, 60), 110))
    blk = iso_block(VAULT_TOP, VAULT_FRONT, VAULT_SIDE, 300)
    blk, pad = drop_shadow(blk, (0, 14), 12, 150)
    img.alpha_composite(blk, (256 - blk.width // 2, 236 - blk.height // 2))
    key = up(KEY, 11)
    key, _ = drop_shadow(key, (0, 8), 8, 170)
    img.alpha_composite(key, (2, S - key.height + 2))
    clock = up(CLOCK, 10)
    clock, _ = drop_shadow(clock, (0, 8), 8, 170)
    img.alpha_composite(clock, (S - clock.width - 2, S - clock.height - 2))
    return finish_icon(img, "icon-b")


def icon_c():
    """Full-size vault front with a reset arrow (alternative)."""
    face = up(VAULT_FRONT, 32)  # 512
    img = face.copy()
    img.alpha_composite(vignette((S, S), 0.35))
    arr = reset_arrow(20, 9)
    img.alpha_composite(glow((S, S), (S - 120, S - 120), 110, (108, 229, 232), 90))
    img.alpha_composite(arr, (S - arr.width - 6, S - arr.height - 6))
    return finish_icon(img, "icon-c")


def icon_d():
    """Normal and ominous vault side by side (alternative)."""
    img = icon_backdrop(TUFF_BRICKS, 8, 0.38)
    img.alpha_composite(glow((S, S), (170, 300), 130, (255, 150, 40), 110))
    img.alpha_composite(glow((S, S), (345, 230), 130, (90, 220, 255), 110))
    b2 = iso_block(OM_TOP, OM_FRONT, OM_SIDE, 230)
    b2, _ = drop_shadow(b2, (0, 12), 10, 150)
    img.alpha_composite(b2, (345 - b2.width // 2, 205 - b2.height // 2))
    b1 = iso_block(VAULT_TOP, VAULT_FRONT, VAULT_SIDE, 250)
    b1, _ = drop_shadow(b1, (0, 12), 10, 160)
    img.alpha_composite(b1, (175 - b1.width // 2, 300 - b1.height // 2))
    arr = reset_arrow(20, 6)
    img.alpha_composite(arr, (S - arr.width - 20, S - arr.height - 20))
    return finish_icon(img, "icon-d")


# ---------------------------------------------------------------- banners
def chamber_wall(size, k=8, f=0.5):
    """Tuff brick wall with chiseled pillars, copper bulbs and a grate floor."""
    w, h = size
    bs = 16 * k
    wall = Image.new("RGBA", size)
    cols = math.ceil(w / bs) + 1
    rows = math.ceil(h / bs) + 1
    for row in range(rows):
        for col in range(cols):
            t = TUFF_BRICKS
            if col % 4 == 0:
                t = CH_TUFF_BRICKS if row % 3 else BULB
            if row == rows - 2:
                t = CH_COPPER if col % 4 == 0 else POL_TUFF
            if row == rows - 1:
                t = GRATE
            wall.paste(shade(up(t, k), f), (col * bs - bs // 3, row * bs - bs // 2))
    return wall


def banner(size, name, title_k, sub_k, block_w, layout="right"):
    w, h = size
    img = chamber_wall(size, 8, 0.55)
    # darken the edges
    img.alpha_composite(vignette(size, 0.85))
    # dark area behind the title
    grad = Image.new("L", (w, 1))
    for x in range(w):
        t = x / w
        grad.putpixel((x, 0), int(235 * max(0.0, 1 - t * 1.45)) if layout == "right" else int(150))
    grad = grad.resize(size)
    dark = Image.new("RGBA", size, (10, 12, 14, 255))
    dark.putalpha(grad)
    img.alpha_composite(dark)

    bx = int(w * 0.74) if layout == "right" else w // 2
    by = int(h * 0.52)
    img.alpha_composite(glow(size, (bx, by), int(block_w * 0.75), (255, 150, 40), 140))
    blk = iso_block(VAULT_TOP, VAULT_FRONT, VAULT_SIDE, block_w)
    blk, pad = drop_shadow(blk, (0, 24), 22, 170)
    img.alpha_composite(blk, (bx - blk.width // 2, by - blk.height // 2))
    key = up(KEY, max(6, block_w // 40))
    key, _ = drop_shadow(key, (0, 10), 10, 170)
    img.alpha_composite(key, (bx - block_w // 2 - key.width // 2 - 40, by + block_w // 4 - key.height // 2 + 40))
    arr = reset_arrow(20, max(5, block_w // 70))
    img.alpha_composite(arr, (bx + block_w // 2 - arr.width // 2 + 20, by - block_w // 2 - arr.height // 2 + 30))

    title = text_img("Vault Reset", title_k, (255, 255, 255))
    sub1 = text_img("Vaults reopen after a cooldown.", sub_k, (255, 214, 120))
    sub2 = text_img("Per player, per vault.", sub_k, (255, 214, 120))
    tags = text_img("Datapack  Fabric  NeoForge  Quilt", max(3, sub_k - 2), (170, 190, 200))
    if layout == "right":
        x = int(w * 0.07)
        ty = int(h * 0.5) - (title.height + sub1.height * 2 + tags.height + 60) // 2
        img.alpha_composite(title, (x, ty))
        img.alpha_composite(sub1, (x, ty + title.height + 24))
        img.alpha_composite(sub2, (x, ty + title.height + 24 + sub1.height + 4))
        img.alpha_composite(tags, (x, ty + title.height + 24 + sub1.height * 2 + 40))
    img.convert("RGB").save(OUT / f"{name}.png")
    return img


VAULT_FRONT_OFF = tex("block/vault_front_off")
VAULT_SIDE_OFF = tex("block/vault_side_off")


def banner_story(size, name, title_k, sub_k, block_w):
    """Looted -> cooldown -> open again (the chosen banner)."""
    w, h = size
    img = chamber_wall(size, 8, 0.5)
    img.alpha_composite(vignette(size, 0.9))
    band = Image.new("RGBA", size, (10, 12, 14, 150))
    img.alpha_composite(band)
    title = text_img("Vault Reset", title_k, (255, 255, 255))
    sub = text_img("Vaults reopen after a cooldown. Per player, per vault.", sub_k, (255, 214, 120))
    gap = int(h * 0.05)
    blk_h = block_w // 2 + round(block_w * 0.577)
    total = title.height + gap // 2 + sub.height + gap + blk_h
    y0 = (h - total) // 2
    img.alpha_composite(title, ((w - title.width) // 2, y0))
    img.alpha_composite(sub, ((w - sub.width) // 2, y0 + title.height + gap // 2))
    by = y0 + title.height + gap // 2 + sub.height + gap + blk_h // 2
    cx = w // 2
    off_x, on_x = cx - int(block_w * 1.45), cx + int(block_w * 1.45)
    img.alpha_composite(glow(size, (on_x, by), int(block_w * 0.8), (255, 150, 40), 150))
    used = iso_block(VAULT_TOP, VAULT_FRONT_OFF, VAULT_SIDE_OFF, block_w, (0.7, 0.6, 0.45))
    used, _ = drop_shadow(used, (0, 18), 16, 170)
    img.alpha_composite(used, (off_x - used.width // 2, by - used.height // 2))
    fresh = iso_block(VAULT_TOP, VAULT_FRONT, VAULT_SIDE, block_w)
    fresh, _ = drop_shadow(fresh, (0, 18), 16, 170)
    img.alpha_composite(fresh, (on_x - fresh.width // 2, by - fresh.height // 2))
    clock = up(CLOCK, max(6, block_w // 26))
    clock, _ = drop_shadow(clock, (0, 10), 10, 170)
    img.alpha_composite(glow(size, (cx, by), int(block_w * 0.45), (108, 229, 232), 70))
    img.alpha_composite(clock, (cx - clock.width // 2, by - clock.height // 2))
    # arrows left and right of the clock
    for ax in (cx - int(block_w * 0.72), cx + int(block_w * 0.72)):
        arr = text_img(">", max(4, block_w // 50), (108, 229, 232))
        img.alpha_composite(arr, (ax - arr.width // 2, by - arr.height // 2))
    lk = max(3, sub_k - 2)
    for x, label, col in ((off_x, "looted", (170, 170, 170)), (cx, "cooldown", (108, 229, 232)), (on_x, "open again", (255, 214, 120))):
        t = text_img(label, lk, col)
        img.alpha_composite(t, (x - t.width // 2, by + blk_h // 2 + int(h * 0.03)))
    img.convert("RGB").save(OUT / f"{name}.png")
    return img


if __name__ == "__main__":
    icon_a()
    banner_story((1920, 1080), "banner-16x9", 14, 5, 380)
    banner_story((1920, 960), "banner-2x1", 13, 5, 340)
    banner_story((1920, 640), "banner-3x1", 10, 4, 230)
    print("ok:", ", ".join(sorted(p.name for p in OUT.glob("*.png"))))
