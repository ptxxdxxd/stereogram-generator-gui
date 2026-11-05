"""Rebuild the README demo images: python docs/make_demo.py

The depth map is drawn here (a ring with a square inside), the texture is
seeded random dots, and the stereogram comes from stereogram_core with the
GUI's default settings.
"""

from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from stereogram_core import stereogram_from_depth_texture  # noqa: E402

W, H = 600, 360

depth = Image.new("L", (W, H), 255)  # black-on-white, like the GUI expects
draw = ImageDraw.Draw(depth)
draw.ellipse((170, 50, 430, 310), fill=0)
draw.ellipse((220, 100, 380, 260), fill=255)
draw.rectangle((265, 145, 335, 215), fill=0)
depth.save(HERE / "demo-depth.png")

arr = np.array(depth)
arr = 255 - arr  # same auto-invert the GUI applies to mostly-white maps

rng = np.random.default_rng(7)
texture = Image.fromarray(rng.integers(0, 256, (H, W, 3), dtype=np.uint8))

out = stereogram_from_depth_texture(arr, texture, pattern_width=80, depth_strength=20)
out.save(HERE / "demo-stereogram.png")
print("wrote", HERE / "demo-depth.png", "and", HERE / "demo-stereogram.png")
