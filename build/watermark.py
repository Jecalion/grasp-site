"""The Grasp lockup, drawn once as a translucent PNG for the corner of every web clip.

    python build/watermark.py      -> build/watermark.png

Same strokes as the header logo in index.html; white, half see-through, lime accent.
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), 'watermark.png')
K = 8                      # draw big, shrink once: smooth edges
WIDTH = 120                # px on a 720 px wide clip
WHITE = (255, 255, 255, 150)
LIME = (198, 248, 78, 190)
LINES = [[(10, 30), (10, 70)], [(25, 30), (25, 70)], [(40, 30), (40, 70)], [(55, 30), (55, 70)],
         [(112, 30), (93, 30), (93, 70), (112, 70), (112, 52), (103, 52)],
         [(129, 70), (129, 30), (147, 30), (147, 48), (129, 48)], [(137, 48), (148, 70)],
         [(165, 70), (165, 38), (174, 30), (183, 38), (183, 70)], [(165, 54), (183, 54)],
         [(220, 30), (201, 30), (201, 50), (219, 50), (219, 70), (200, 70)],
         [(237, 70), (237, 30), (255, 30), (255, 50), (237, 50)]]
ACCENT = [(1, 64), (64, 36)]
X0, Y0, W, H, SW = -4, 25, 264, 50, 8.5   # the SVG's viewBox and stroke width


def stroke(img, pts, colour):
    """One round-capped polyline on its own layer, so overlaps don't double the alpha."""
    layer = Image.new('RGBA', img.size)
    d = ImageDraw.Draw(layer)
    p = [((x - X0) * K, (y - Y0) * K) for x, y in pts]
    r = SW * K / 2
    d.line(p, fill=colour, width=round(SW * K), joint='curve')
    for x, y in p:
        d.ellipse([x - r, y - r, x + r, y + r], fill=colour)
    return Image.alpha_composite(img, layer)


def main():
    img = Image.new('RGBA', (W * K, H * K))
    white = Image.new('RGBA', img.size)
    d = ImageDraw.Draw(white)
    for pts in LINES:                      # all white strokes as one shape, one alpha
        p = [((x - X0) * K, (y - Y0) * K) for x, y in pts]
        r = SW * K / 2
        d.line(p, fill=WHITE, width=round(SW * K), joint='curve')
        for x, y in p:
            d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE)
    img = Image.alpha_composite(img, white)
    img = stroke(img, ACCENT, LIME)
    img = img.resize((WIDTH, round(WIDTH * H / W)), Image.LANCZOS)
    img.save(OUT)
    print(OUT, img.size)


if __name__ == '__main__':
    main()
