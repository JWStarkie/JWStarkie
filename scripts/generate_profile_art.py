"""Generate the sakura terminal and scenic-route GIFs with still fallbacks.

Run on Windows with Python, Pillow, and Microsoft Edge:
    python scripts\\generate_profile_art.py
"""

import math
import os
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH, HEIGHT = 600, 220
FRAMES = 48
INK = "#211b38"


def font(size):
    return ImageFont.load_default(size=size)


def make_footer_frame(index):
    phase = index * math.tau / FRAMES
    image = Image.new("RGB", (WIDTH * 2, HEIGHT * 2), INK)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, 1199, 439), radius=32, fill="#fcf5f0")
    draw.rounded_rectangle((17, 17, 1182, 422), radius=23, outline="#e8dcd9", width=2)
    draw.text((57, 57), "LIFE BEYOND THE KEYBOARD", font=font(17), fill="#957b8d")
    draw.text((53, 113), "Taking the", font=font(51), fill="#5b4b64")
    draw.text((53, 174), "scenic route.", font=font(55), fill="#a76b87")
    draw.text((57, 258), "A little coffee. A little curiosity.", font=font(23), fill="#877080")
    draw.line((57, 325, 534, 325), fill="#e5d5d9", width=2)
    draw.text((57, 350), "JAPAN / TRAVEL / THE LITTLE THINGS", font=font(17), fill="#957b8d")

    # Clip the moving landscape to a rounded train-window shape.
    scene = Image.new("RGB", image.size, "#f3d9d4")
    landscape = ImageDraw.Draw(scene)
    for y in range(52, 338):
        t = (y - 52) / 286
        landscape.line((0, y, 1200, y), fill=(242 - int(20 * t), 208 - int(5 * t), 206 + int(22 * t)))
    landscape.ellipse((964, 94, 1030, 160), fill="#fff0d6")
    for cx, cy in [(817, 117), (1064, 177)]:
        drift = 11 * math.sin(phase + cy)
        landscape.rounded_rectangle((cx + drift, cy, cx + 76 + drift, cy + 10), radius=5, fill="#f9e9e3")
        landscape.ellipse((cx + 18 + drift, cy - 9, cx + 48 + drift, cy + 8), fill="#f9e9e3")
    landscape.polygon([(696, 302), (889, 150), (1074, 302)], fill="#aaa0bc")
    landscape.polygon([(854, 178), (889, 150), (925, 179), (903, 175), (889, 184), (872, 175)], fill="#f8eee9")
    landscape.polygon([(700, 318), (777, 246), (863, 294), (1009, 229), (1132, 301), (1132, 342), (700, 342)], fill="#b7a5bc")
    landscape.polygon([(700, 322), (846, 286), (962, 321), (1132, 278), (1132, 342), (700, 342)], fill="#93879f")
    landscape.line([(1150, 62), (1110, 81), (1075, 85), (1043, 69)], fill="#a88095", width=4, joint="curve")
    landscape.line([(1110, 81), (1119, 112), (1140, 130)], fill="#a88095", width=3)
    for bx, by, size in [(1123, 75, 8), (1083, 85, 9), (1054, 74, 7), (1120, 112, 8), (1140, 130, 6)]:
        for petal in range(5):
            angle = petal * math.tau / 5
            px = bx + math.sin(angle) * size * .65
            py = by + math.cos(angle) * size * .65
            landscape.ellipse((px - size / 2, py - size / 2, px + size / 2, py + size / 2), fill="#fbe0eb")
        landscape.ellipse((bx - 2, by - 2, bx + 2, by + 2), fill="#e2a8bf")
    for petal in range(5):
        px = 1038 + petal * 18 + 7 * math.sin(phase + petal)
        py = 142 + ((petal * 39 + index * 180 / FRAMES) % 180)
        landscape.ellipse((px, py, px + 4, py + 8), fill="#f9dfeb")
    mask = Image.new("L", image.size)
    ImageDraw.Draw(mask).rounded_rectangle((713, 48, 1133, 338), radius=85, fill=255)
    image.paste(scene, (0, 0), mask)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((706, 41, 1140, 345), radius=92, outline="#d9c6cf", width=6)
    draw.rounded_rectangle((699, 341, 1150, 357), radius=6, fill="#d9c6cf")

    # An open travel notebook and coffee sit on the windowsill.
    draw.ellipse((791, 379, 1141, 398), fill="#e5d6d5")
    draw.polygon([(806, 342), (894, 331), (935, 353), (1025, 344), (1034, 388), (938, 396), (812, 383)], fill="#dfc5cf")
    draw.polygon([(810, 337), (895, 327), (936, 348), (1021, 338), (1027, 379), (938, 387), (816, 374)], fill="#fffaf2")
    draw.line((936, 348, 938, 387), fill="#d2b9c5", width=2)
    for y in (347, 356, 365):
        draw.line((830, y, 888, y - 5), fill="#dfd0d1", width=2)
    draw.line((970, 352, 1003, 348), fill="#d8becd", width=2)
    draw.line((972, 361, 1005, 357), fill="#d8becd", width=2)
    draw.ellipse((1052, 320, 1111, 379), outline="#ba8ea5", width=9)
    draw.rounded_rectangle((1008, 311, 1074, 380), radius=17, fill="#e8bacc")
    draw.ellipse((1008, 305, 1074, 324), fill="#f7dce5")
    draw.ellipse((1015, 309, 1067, 321), fill="#96746b")
    for strand in range(2):
        points = []
        for step in range(30):
            y = 298 - step * 1.5
            x = 1028 + strand * 23 + 4 * math.sin(phase + step / 8 + strand)
            points.append((x, y))
        draw.line(points, fill="#e8dedf", width=3)
    return image


def render_terminal():
    edge = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft" / "Edge" / "Application" / "msedge.exe"
    if not edge.is_file():
        raise FileNotFoundError("Microsoft Edge is required to render the original SVG.")

    ET.register_namespace("", "http://www.w3.org/2000/svg")
    svg = ET.parse(ASSETS / "sakura-terminal.svg")
    root = svg.getroot()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    # Moving petals and the cursor are drawn per frame, not baked into the still.
    for group in root.findall("svg:g", namespace):
        if group.get("opacity") == ".85":
            root.remove(group)
        if group.get("font-family"):
            for path in group.findall("svg:path", namespace):
                group.remove(path)

    with tempfile.TemporaryDirectory(prefix="jo-profile-render-") as directory:
        temporary = Path(directory)
        page = temporary / "terminal.html"
        screenshot = temporary / "terminal.png"
        page.write_text(
            '<!doctype html><meta charset="utf-8">'
            '<style>html,body{margin:0;width:1200px;height:440px;overflow:hidden}'
            'svg{display:block}</style>'
            + ET.tostring(root, encoding="unicode"),
            encoding="utf-8",
        )
        subprocess.run(
            [
                str(edge),
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--window-size=1200,440",
                f"--user-data-dir={temporary / 'browser-profile'}",
                f"--screenshot={screenshot}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )
        with Image.open(screenshot) as image:
            if image.size != (1200, 440):
                raise ValueError(f"Unexpected terminal render dimensions: {image.size}")
            return image.convert("RGB")


def make_terminal_frames():
    base = render_terminal()
    frames = []
    for index in range(FRAMES):
        phase = index * math.tau / FRAMES
        image = base.copy()
        draw = ImageDraw.Draw(image)
        if index < FRAMES // 2:
            draw.rectangle((337, 325, 345, 340), fill="#f7b2d0")
        if 31 <= index <= 33:
            for x in (603, 639):
                draw.rectangle((x - 2, 256, x + 14, 267), fill="#f8d2e6")
                draw.line((x, 264, x + 12, 264), fill="#594069", width=3)
        for petal in range(8):
            x = 785 + petal * 49 + 8 * math.sin(phase + petal)
            y = 125 + ((petal * 43 + index * 300 / FRAMES) % 300)
            draw.ellipse((x, y, x + 5, y + 11), fill="#ffc4df")
        frames.append(image)
    return frames


def save_animation(name, frames):
    frames[0].save(ASSETS / f"{name}-still.png", optimize=True)
    # A shared palette prevents frame-to-frame colour shimmer.
    palette = frames[0].quantize(colors=128)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(
        ASSETS / f"{name}.gif",
        save_all=True,
        append_images=indexed[1:],
        duration=100,
        loop=0,
        optimize=True,
        disposal=1,
    )
    with Image.open(ASSETS / f"{name}.gif") as result:
        assert result.n_frames == FRAMES
        assert result.size == (WIDTH * 2, HEIGHT * 2)
        for frame in range(result.n_frames):
            result.seek(frame)
            result.load()
    print(f"Created {name}: {FRAMES} frames and reduced-motion still.")


def main():
    ASSETS.mkdir(exist_ok=True)
    save_animation("axolotl-sakura-terminal", make_terminal_frames())
    save_animation("scenic-route", [make_footer_frame(index) for index in range(FRAMES)])


if __name__ == "__main__":
    main()
