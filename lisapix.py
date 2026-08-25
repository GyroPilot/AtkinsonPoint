#!/usr/bin/env python3
"""lisapix.py -- PNG/JPG -> Lisa .PIX slide (680x300, 1-bit, 85 bytes/row).

Version 1.1 ("lisapix 2"): adds --par pixel-aspect prescale, dither
choices, and --preview.

The Lisa's pixels are not square: 680x300 displays about 1.40:1.  By
default the source image is prescaled by --par 1.40 so circles stay
circles on the CRT.  Use --par 1.0 to disable.

Output: exactly 25,500 bytes.  Row-major, 85 bytes per row, 300 rows,
MSB = leftmost pixel, 1 = black (QuickDraw ink convention).

Usage:
  python lisapix.py input.png output.PIX [--dither fs|atkinson|ordered|threshold]
                    [--par 1.40] [--window] [--preview preview.png]

--window letterboxes into 680x300 preserving aspect (recommended);
without it the image is stretched to fill.

Requires: Pillow  (pip install pillow)
"""

import sys
import argparse
from PIL import Image

W, H = 680, 300
ROWBYTES = 85
SIZE = ROWBYTES * H  # 25,500


def ordered_dither(img):
    m = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    g = img.convert('L')
    px = g.load()
    out = Image.new('1', g.size)
    op = out.load()
    for y in range(g.size[1]):
        for x in range(g.size[0]):
            t = (m[y % 4][x % 4] + 0.5) * 16
            op[x, y] = 0 if px[x, y] < t else 255
    return out


def atkinson_dither(img):
    g = img.convert('L')
    px = list(g.getdata())
    w, h = g.size
    buf = [float(v) for v in px]
    out = Image.new('1', (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            i = y * w + x
            old = buf[i]
            new = 255.0 if old >= 128 else 0.0
            op[x, y] = int(new)
            err = (old - new) / 8.0
            for dx, dy in ((1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    buf[ny * w + nx] += err
    return out


def convert(src, dst, dither, par, window, fill, preview):
    img = Image.open(src)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    if par and abs(par - 1.0) > 0.01:
        # Pre-squash vertically so the Lisa's tall pixels undo it.
        nw, nh = img.size[0], max(1, round(img.size[1] / par))
        img = img.resize((nw, nh), Image.LANCZOS)

    if fill:
        # scale to COVER 680x300, then center-crop: fills the frame,
        # trims the overflow.  Best for landscape photos.
        s = max(W / img.size[0], H / img.size[1])
        nw, nh = max(W, round(img.size[0] * s)), max(H, round(img.size[1] * s))
        img = img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - H) // 2
        img = img.crop((ox, oy, ox + W, oy + H)).convert('L')
    elif window:
        img.thumbnail((W, H), Image.LANCZOS)
        canvas = Image.new('L', (W, H), 255)
        ox = (W - img.size[0]) // 2
        oy = (H - img.size[1]) // 2
        canvas.paste(img.convert('L'), (ox, oy))
        img = canvas
    else:
        img = img.resize((W, H), Image.LANCZOS)

    if dither == 'fs':
        one = img.convert('1')                    # Pillow default = Floyd-Steinberg
    elif dither == 'atkinson':
        one = atkinson_dither(img)
    elif dither == 'ordered':
        one = ordered_dither(img)
    else:                                          # threshold
        one = img.convert('L').point(lambda v: 255 if v >= 128 else 0, mode='1')

    if preview:
        one.save(preview)

    px = one.load()
    out = bytearray(SIZE)
    for y in range(H):
        base = y * ROWBYTES
        for x in range(W):
            if px[x, y] == 0:                      # black pixel -> bit set
                out[base + (x >> 3)] |= 0x80 >> (x & 7)
    with open(dst, 'wb') as f:
        f.write(out)
    print(f'{dst}: {SIZE} bytes ({dither}, par {par}, '
          f'{"fill" if fill else "window" if window else "stretch"})')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--dither', default='atkinson',
                    choices=['fs', 'atkinson', 'ordered', 'threshold'])
    ap.add_argument('--par', type=float, default=1.40)
    ap.add_argument('--window', action='store_true')
    ap.add_argument('--fill', action='store_true',
                    help='scale to cover and center-crop: fills the frame')
    ap.add_argument('--preview', default=None)
    a = ap.parse_args()
    convert(a.src, a.dst, a.dither, a.par, a.window, a.fill, a.preview)


if __name__ == '__main__':
    main()
