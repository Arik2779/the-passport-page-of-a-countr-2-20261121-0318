#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Deterministic, stdlib-only generator. Draws one open passport spread for the
invented Republic of Valdoria (capital Tarnova) and writes it to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Layout (1024x704): left page = data page (portrait, holder fields, MRZ with
real ICAO check digits); right page = visa/stamp page (Dunvar visa sticker,
six entry/exit stamps, alpine transit fee stamp, mountain-pass note).

Country / holder / travel history (consistency-checked):
  Holder:      Mara Ilves, born 14 MAR 1992, Tarnova, F
  Passport:    VLD 482 913, issued 03 FEB 2025, expires 03 FEB 2035
  Visa:        Dunvar type C, single entry, issued Tarnova 10 APR 2025,
               valid 10 APR 2025 - 10 JUL 2025, employment prohibited
  Travel:      18 APR 2025 depart Valdoria (Tarnova Intl) / arrive Kestrelia
               02 MAY 2025 depart Kestrelia
               03 MAY 2025 arrive Dunvar (Sareen)
               17 MAY 2025 depart Dunvar / arrive Valdoria (Tarnova Intl)
  Every stamp is dated after the 03 FEB 2025 issue date.
"""
import math
import os
import struct
import zlib

W, H = 1024, 704

# ---------------------------------------------------------------- palette
CREAM   = (246, 241, 222)   # passport paper
INK     = (26, 26, 26)      # main text
LABEL   = (90, 107, 90)     # small field labels
GREEN   = (31, 77, 46)      # Valdoria green (headers, seal, own stamps)
BLUE    = (43, 74, 143)     # Kestrelia / visa blue
PLUM    = (122, 46, 109)    # Dunvar plum
RED     = (160, 48, 40)     # fee stamp red
SKIN    = (232, 185, 143)
SKIN_D  = (205, 160, 120)
HAIR    = (74, 50, 38)
JACKET  = (43, 58, 85)
PHOTO_BG = (185, 199, 214)
VISA_BG = (221, 231, 238)
GOLD    = (198, 158, 62)
FAINT   = (232, 224, 200)   # watermark

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 chars ('#' = on). All-caps document font.
FONT = {
' ': (".....",".....",".....",".....",".....",".....","....."),
'A': (".###.","#...#","#...#","#####","#...#","#...#","#...#"),
'B': ("####.","#...#","#...#","####.","#...#","#...#","####."),
'C': (".####","#....","#....","#....","#....","#....",".####"),
'D': ("####.","#...#","#...#","#...#","#...#","#...#","####."),
'E': ("#####","#....","#....","####.","#....","#....","#####"),
'F': ("#####","#....","#....","####.","#....","#....","#...."),
'G': (".####","#....","#....","#.###","#...#","#...#",".###."),
'H': ("#...#","#...#","#...#","#####","#...#","#...#","#...#"),
'I': ("#####","..#..","..#..","..#..","..#..","..#..","#####"),
'J': ("..###","...#.","...#.","...#.","...#.","#..#.",".##.."),
'K': ("#...#","#..#.","#.#..","##...","#.#..","#..#.","#...#"),
'L': ("#....","#....","#....","#....","#....","#....","#####"),
'M': ("#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#"),
'N': ("#...#","##..#","##..#","#.#.#","#..##","#..##","#...#"),
'O': (".###.","#...#","#...#","#...#","#...#","#...#",".###."),
'P': ("####.","#...#","#...#","####.","#....","#....","#...."),
'Q': (".###.","#...#","#...#","#...#","#.#.#","#..#.",".##.#"),
'R': ("####.","#...#","#...#","####.","#.#..","#..#.","#...#"),
'S': (".####","#....","#....",".###.","....#","....#","####."),
'T': ("#####","..#..","..#..","..#..","..#..","..#..","..#.."),
'U': ("#...#","#...#","#...#","#...#","#...#","#...#",".###."),
'V': ("#...#","#...#","#...#","#...#","#...#",".#.#.","..#.."),
'W': ("#...#","#...#","#...#","#.#.#","#.#.#","##.##","#...#"),
'X': ("#...#","#...#",".#.#.","..#..",".#.#.","#...#","#...#"),
'Y': ("#...#","#...#",".#.#.","..#..","..#..","..#..","..#.."),
'Z': ("#####","....#","...#.","..#..",".#...","#....","#####"),
'0': (".###.","#...#","#..##","#.#.#","##..#","#...#",".###."),
'1': ("..#..",".##..","..#..","..#..","..#..","..#..",".###."),
'2': (".###.","#...#","....#","...#.","..#..",".#...","#####"),
'3': ("####.","....#","....#",".###.","....#","....#","####."),
'4': ("...#.","..##.",".#.#.","#..#.","#####","...#.","...#."),
'5': ("#####","#....","####.","....#","....#","#...#",".###."),
'6': (".###.","#....","#....","####.","#...#","#...#",".###."),
'7': ("#####","....#","...#.","...#.","..#..","..#..","..#.."),
'8': (".###.","#...#","#...#",".###.","#...#","#...#",".###."),
'9': (".###.","#...#","#...#",".####","....#","....#",".###."),
'-': (".....",".....",".....","#####",".....",".....","....."),
'.': (".....",".....",".....",".....",".....",".##..",".##.."),
',': (".....",".....",".....",".....",".##..",".##..",".#..."),
'/': ("....#","...#.","...#.","..#..","..#..",".#...","#...."),
'(': ("...##","..#..",".#...",".#...",".#...","..#..","...##"),
')': ("##...","..#..","...#.","...#.","...#.","..#..","##..."),
'<': ("...#.","..#..",".#...","#....",".#...","..#..","...#."),
'>': (".#...","..#..","...#.","....#","...#.","..#..",".#..."),
':': (".....",".##..",".##..",".....",".##..",".##..","....."),
"'": ("..#..","..#..",".#...",".....",".....",".....","....."),
'!': ("..#..","..#..","..#..","..#..","..#..",".....","..#.."),
}

def text_width(text, scale, spacing=None):
    if spacing is None:
        spacing = scale
    if not text:
        return 0
    return len(text) * (5 * scale + spacing) - spacing

# ---------------------------------------------------------------- canvas
class Img:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x0, y0, x1, y1, c):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            for x in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x0, x1, y, c, t=1):
        for yy in range(y, y + t):
            for x in range(x0, x1):
                self.set(x, yy, c)

    def vline(self, x, y0, y1, c, t=1):
        for xx in range(x, x + t):
            for y in range(y0, y1):
                self.set(xx, y, c)

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.hline(x0, x1, y0, c, t)
        self.hline(x0, x1, y1 - t, c, t)
        self.vline(x0, y0, y1, c, t)
        self.vline(x1 - t, y0, y1, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def circle(self, cx, cy, r, c, t=1):
        for k in range(t):
            rr = r - k
            x, y, d = 0, rr, 3 - 2 * rr
            while y >= x:
                for px, py in ((cx+x, cy+y), (cx-x, cy+y), (cx+x, cy-y),
                               (cx-x, cy-y), (cx+y, cy+x), (cx-y, cy+x),
                               (cx+y, cy-x), (cx-y, cy-x)):
                    self.set(px, py, c)
                x += 1
                if d > 0:
                    y -= 1; d += 4 * (x - y) + 10
                else:
                    d += 4 * x + 6

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            dy = (y - cy) / ry
            if abs(dy) > 1:
                continue
            dx = int(rx * math.sqrt(1 - dy * dy))
            self.hline(cx - dx, cx + dx + 1, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        # outline via parametric sampling
        steps = max(8, int(2 * math.pi * max(rx, ry)))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            self.set(int(round(cx + rx * math.cos(a))),
                     int(round(cy + ry * math.sin(a))), c)

    def fill_poly(self, pts, c):
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(math.ceil(xs[i])), int(xs[i + 1]) + 1, y, c)

# ---------------------------------------------------------------- text
def draw_glyph(img, x, y, ch, scale, color):
    g = FONT.get(ch)
    if g is None:
        return
    for gy, row in enumerate(g):
        for gx, bit in enumerate(row):
            if bit == '#':
                img.fill_rect(x + gx * scale, y + gy * scale,
                              x + gx * scale + scale, y + gy * scale + scale,
                              color)

def draw_text(img, x, y, text, scale, color, spacing=None, bold=False):
    if spacing is None:
        spacing = scale
    cx = x
    for ch in text:
        draw_glyph(img, cx, y, ch, scale, color)
        if bold:
            draw_glyph(img, cx + 1, y, ch, scale, color)
        cx += 5 * scale + spacing
    return cx - spacing

def draw_text_c(img, cx, y, text, scale, color, spacing=None, bold=False):
    w = text_width(text, scale, spacing)
    return draw_text(img, cx - w // 2, y, text, scale, color, spacing, bold)

def blit_rotated(img, ch, cx, cy, angle_deg, scale, color):
    """Draw one glyph rotated clockwise by angle_deg around (cx, cy)."""
    g = FONT.get(ch)
    if g is None:
        return
    w, h = 5 * scale, 7 * scale
    rad = math.radians(angle_deg)
    co, si = math.cos(rad), math.sin(rad)
    r = int(math.ceil(math.hypot(w, h) / 2)) + 2
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            sx = dx * co + dy * si
            sy = -dx * si + dy * co
            gx = int((sx + w / 2) // scale)
            gy = int((sy + h / 2) // scale)
            if 0 <= gx < 5 and 0 <= gy < 7 and g[gy][gx] == '#':
                img.set(cx + dx, cy + dy, color)

def arc_text(img, cx, cy, r, text, top, scale, color):
    """Text along a circular arc. top=True: along the top (tops outward);
    top=False: along the bottom (tops toward centre, reads left to right)."""
    n = len(text)
    if n == 0:
        return
    pitch = 6 * scale
    step = math.degrees(pitch / r)
    span = (n - 1) * step
    for i, ch in enumerate(text):
        a = -span / 2 + i * step
        ar = math.radians(a)
        if top:
            px = cx + r * math.sin(ar)
            py = cy - r * math.cos(ar)
            rot = a
        else:
            px = cx + r * math.sin(ar)
            py = cy + r * math.cos(ar)
            rot = -a  # tops point toward the centre: upright at the bottom
        blit_rotated(img, ch, int(round(px)), int(round(py)), rot, scale, color)

# ---------------------------------------------------------------- PNG
def write_png(img, path):
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)  # filter: none
        raw += img.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- MRZ
def mrz_check(s):
    vals = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
    total = 0
    for i, ch in enumerate(s):
        v = 0 if ch == "<" else vals[ch]
        total += v * (7, 3, 1)[i % 3]
    return str(total % 10)

def mrz_lines():
    line1 = ("P<VAL" + "ILVES<<MARA").ljust(44, "<")
    doc, dob, exp = "VLD482913", "920314", "350203"
    pers = "<" * 14
    body = (doc + mrz_check(doc) + "VAL" + dob + mrz_check(dob) + "F"
            + exp + mrz_check(exp) + pers + mrz_check(pers))
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2

# ---------------------------------------------------------------- portrait
def draw_portrait(img, x0, y0, x1, y1):
    img.fill_rect(x0, y0, x1, y1, PHOTO_BG)
    # faint oval backdrop
    img.ellipse((x0 + x1) // 2, (y0 + y1) // 2 - 30, 52, 66, (200, 211, 222))
    cx = (x0 + x1) // 2
    # shoulders / jacket
    img.fill_poly([(x0 + 6, y1), (x0 + 26, y1 - 52), (cx - 16, y1 - 64),
                   (cx + 16, y1 - 64), (x1 - 26, y1 - 52), (x1 - 6, y1)],
                  JACKET)
    # blouse collar
    img.fill_poly([(cx - 16, y1 - 64), (cx, y1 - 38), (cx + 16, y1 - 64)],
                  (240, 240, 235))
    # gold pin on the jacket
    img.fill_ellipse(cx + 24, y1 - 52, 3, 3, GOLD)
    # neck
    img.fill_rect(cx - 11, y1 - 96, cx + 11, y1 - 60, SKIN)
    img.hline(cx - 11, cx + 11, y1 - 62, SKIN_D, 2)
    # hair (back mass + side strands)
    img.fill_ellipse(cx, y1 - 128, 40, 46, HAIR)
    img.fill_rect(x0 + 20, y1 - 138, x0 + 33, y1 - 58, HAIR)
    img.fill_rect(x1 - 33, y1 - 138, x1 - 20, y1 - 58, HAIR)
    # ears
    img.fill_ellipse(cx - 33, y1 - 122, 5, 9, SKIN)
    img.fill_ellipse(cx + 33, y1 - 122, 5, 9, SKIN)
    # face
    img.fill_ellipse(cx, y1 - 122, 32, 40, SKIN)
    # hair fringe over the forehead
    img.fill_ellipse(cx, y1 - 158, 33, 22, HAIR)
    img.fill_ellipse(cx, y1 - 122, 32, 40, SKIN)
    img.fill_ellipse(cx, y1 - 166, 34, 20, HAIR)
    # brows
    img.hline(cx - 19, cx - 8, y1 - 128, HAIR, 2)
    img.hline(cx + 8, cx + 19, y1 - 128, HAIR, 2)
    # eyes
    img.fill_rect(cx - 15, y1 - 124, cx - 11, y1 - 120, INK)
    img.fill_rect(cx + 11, y1 - 124, cx + 15, y1 - 120, INK)
    # nose
    img.vline(cx, y1 - 120, y1 - 108, SKIN_D, 2)
    img.hline(cx - 3, cx + 3, y1 - 108, SKIN_D, 2)
    # mouth
    img.hline(cx - 7, cx + 7, y1 - 98, (150, 90, 80), 2)

# ---------------------------------------------------------------- coat of arms
def draw_shield(img, cx, top):
    # green shield, gold edge, white peaks, gold star
    pts = [(cx - 20, top), (cx + 20, top), (cx + 20, top + 32),
           (cx, top + 56), (cx - 20, top + 32)]
    img.fill_poly(pts, GREEN)
    img.line(cx - 20, top, cx + 20, top, GOLD)
    img.line(cx + 20, top, cx + 20, top + 32, GOLD)
    img.line(cx - 20, top, cx - 20, top + 32, GOLD)
    img.line(cx + 20, top + 32, cx, top + 56, GOLD)
    img.line(cx - 20, top + 32, cx, top + 56, GOLD)
    # mountains
    img.fill_poly([(cx - 14, top + 42), (cx - 6, top + 24), (cx + 2, top + 42)],
                  (246, 241, 222))
    img.fill_poly([(cx - 2, top + 42), (cx + 7, top + 28), (cx + 15, top + 42)],
                  GOLD)
    # star
    img.fill_poly([(cx, top + 8), (cx + 2, top + 13), (cx + 7, top + 13),
                   (cx + 3, top + 16), (cx + 4, top + 21), (cx, top + 18),
                   (cx - 4, top + 21), (cx - 3, top + 16), (cx - 7, top + 13),
                   (cx - 2, top + 13)], GOLD)

def draw_star4(img, cx, cy, r, c):
    img.fill_poly([(cx, cy - r), (cx + r // 3, cy - r // 3), (cx + r, cy),
                   (cx + r // 3, cy + r // 3), (cx, cy + r),
                   (cx - r // 3, cy + r // 3), (cx - r, cy),
                   (cx - r // 3, cy - r // 3)], c)

# ---------------------------------------------------------------- stamps
def round_stamp(img, cx, cy, r, color, top_text, bottom_text, mid1, mid2):
    img.circle(cx, cy, r, color, 3)
    img.circle(cx, cy, r - 6, color, 1)
    arc_text(img, cx, cy, r - 13, top_text, True, 1, color)
    arc_text(img, cx, cy, r - 13, bottom_text, False, 1, color)
    draw_text_c(img, cx, cy - 18, mid1, 2, color, spacing=0)
    img.hline(cx - 28, cx + 28, cy - 1, color, 1)
    draw_text_c(img, cx, cy + 2, mid2, 2, color, spacing=0)

def rect_stamp(img, x0, y0, x1, y1, color, line1, line2):
    img.rect(x0, y0, x1, y1, color, 2)
    img.rect(x0 + 4, y0 + 4, x1 - 4, y1 - 4, color, 1)
    draw_text_c(img, (x0 + x1) // 2, y0 + 8, line1, 1, color)
    draw_text_c(img, (x0 + x1) // 2, y0 + 20, line2, 1, color)

def official_seal(img, cx, cy, r):
    img.circle(cx, cy, r, GREEN, 2)
    img.circle(cx, cy, r - 5, GREEN, 1)
    draw_star4(img, cx, cy, 7, GREEN)

# ---------------------------------------------------------------- build
def field(img, x, y, label, value, vscale=2, bold=True):
    draw_text(img, x, y, label, 1, LABEL)
    draw_text(img, x, y + 10, value, vscale, INK, bold=bold)

def build():
    img = Img(W, H, GREEN)
    # two cream pages
    img.fill_rect(14, 14, 500, 690, CREAM)
    img.fill_rect(524, 14, 1010, 690, CREAM)
    img.vline(512, 14, 690, (20, 40, 25), 2)  # gutter

    # faint watermark on the data page
    img.circle(257, 400, 120, FAINT, 1)
    draw_star4(img, 257, 400, 14, FAINT)

    # ---- left page: header
    draw_shield(img, 257, 24)
    draw_text_c(img, 257, 92, "REPUBLIC OF VALDORIA", 3, GREEN, bold=True)
    draw_text_c(img, 257, 118, "PASSPORT", 2, INK, bold=True)
    img.hline(34, 480, 138, GREEN, 2)

    # ---- portrait
    draw_portrait(img, 34, 150, 168, 330)
    img.rect(34, 150, 168, 330, GREEN, 2)
    # official seal overlapping the portrait corner
    official_seal(img, 160, 318, 30)

    # ---- data fields (two columns)
    field(img, 188, 150, "SURNAME", "ILVES", vscale=3)
    field(img, 188, 200, "GIVEN NAMES", "MARA")
    field(img, 400, 200, "SEX", "F")
    field(img, 188, 244, "NATIONALITY", "VALDORIAN")
    field(img, 360, 244, "DATE OF BIRTH", "14 MAR 1992")
    field(img, 188, 288, "PLACE OF BIRTH", "TARNOVA")
    field(img, 360, 288, "DATE OF ISSUE", "03 FEB 2025")
    field(img, 188, 332, "DATE OF EXPIRY", "03 FEB 2035")
    field(img, 360, 332, "PASSPORT NO.", "VLD 482 913")
    field(img, 188, 376, "AUTHORITY", "MINISTRY OF INTERIOR")

    # ---- holder signature
    img.line(190, 452, 212, 440, INK)
    img.line(212, 440, 228, 456, INK)
    img.line(228, 456, 250, 442, INK)
    img.line(250, 442, 268, 454, INK)
    img.line(268, 454, 292, 444, INK)
    img.line(300, 448, 330, 448, INK)
    img.line(330, 448, 344, 440, INK)
    img.hline(188, 360, 458, INK, 1)
    draw_text(img, 188, 464, "HOLDER'S SIGNATURE", 1, LABEL)

    draw_text_c(img, 257, 500,
                "THE HOLDER IS A CITIZEN OF THE REPUBLIC OF VALDORIA",
                1, LABEL)
    img.hline(24, 490, 530, GREEN, 1)

    # ---- MRZ (ICAO TD3, real check digits)
    l1, l2 = mrz_lines()
    draw_text(img, 16, 556, l1, 2, INK, spacing=1)
    draw_text(img, 16, 580, l2, 2, INK, spacing=1)
    draw_text_c(img, 257, 640,
                "IF FOUND, PLEASE RETURN TO THE NEAREST VALDORIAN CONSULATE",
                1, LABEL)

    # ---- right page: header
    draw_text_c(img, 767, 92, "VISAS", 3, GREEN, bold=True)
    img.hline(544, 990, 138, GREEN, 2)

    # ---- Dunvar visa sticker
    img.fill_rect(544, 150, 800, 356, VISA_BG)
    img.rect(544, 150, 800, 356, BLUE, 3)
    img.fill_rect(547, 153, 797, 186, BLUE)
    draw_text_c(img, 672, 158, "VISA", 3, (255, 255, 255), bold=True)
    draw_text_c(img, 672, 194, "REPUBLIC OF DUNVAR", 2, BLUE, bold=True)
    field(img, 558, 216, "TYPE", "C - SINGLE ENTRY")
    field(img, 558, 246, "VALID FROM", "10 APR 2025")
    field(img, 558, 276, "UNTIL", "10 JUL 2025")
    field(img, 558, 306, "ISSUED", "TARNOVA, 10 APR 2025")
    draw_text(img, 558, 336, "CONDITION: EMPLOYMENT PROHIBITED", 1, RED)
    draw_text(img, 558, 346, "TOURISM ONLY - MAX. STAY 90 DAYS", 1, RED)

    # ---- alpine transit fee stamp (the telling paperwork detail)
    rect_stamp(img, 544, 376, 800, 426, RED,
               "ALPINE TRANSIT FEE", "15 VK - PAID")
    draw_text(img, 544, 436, "MOUNTAIN PASSES CLOSED 01 NOV - 31 MAR", 1, INK)
    draw_text(img, 544, 448, "HOLDERS MUST CARRY THIS PASSPORT", 1, INK)
    draw_text(img, 544, 460, "AT ALL TIMES IN THE BORDER ZONE", 1, INK)

    # ---- circular stamps
    round_stamp(img, 898, 232, 58, GREEN, "VALDORIA", "DEPARTURE",
                "TARNOVA", "18 APR 2025")
    round_stamp(img, 672, 524, 54, BLUE, "KESTRELIA", "ARRIVAL",
                "VELKA", "18 APR 2025")
    round_stamp(img, 898, 524, 54, BLUE, "KESTRELIA", "DEPARTURE",
                "VELKA", "02 MAY 2025")
    round_stamp(img, 672, 632, 54, PLUM, "DUNVAR", "ARRIVAL",
                "SAREEN", "03 MAY 2025")

    # ---- rectangular exit / entry stamps, 17 MAY 2025
    rect_stamp(img, 810, 592, 990, 632, PLUM,
               "DUNVAR - DEPARTURE", "SAREEN - 17 MAY 2025")
    rect_stamp(img, 810, 644, 990, 684, GREEN,
               "VALDORIA - ARRIVAL", "TARNOVA INTL - 17 MAY 2025")
    return img

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img = build()
    n = write_png(img, path)
    print(f"wrote {path} ({img.w}x{img.h}, {n} bytes)")

if __name__ == "__main__":
    main()
