"""Image functions behind the stereogram GUI, kept free of tkinter so they can be tested."""

import numpy as np
from PIL import Image, ImageOps


def stereogram_from_depth_texture(depth_map, texture_img, pattern_width=80, depth_strength=20):
    h, w = depth_map.shape
    texture_img = texture_img.resize((w, h), Image.LANCZOS)
    texture = np.array(texture_img.convert('RGB'))
    # Start from the texture so pixels with no earlier match keep texture
    # instead of staying black (they used to show up as black bands).
    sgram = texture.copy()
    for y in range(h):
        indices = np.arange(w)
        for x in range(pattern_width, w):
            z = int(depth_strength * (1.0 - depth_map[y, x] / 255.0))
            left = x - pattern_width
            if left - z >= 0:
                indices[x] = indices[left - z]
        sgram[y, :pattern_width] = texture[y, :pattern_width]
        for x in range(pattern_width, w):
            sgram[y, x] = sgram[y, indices[x]]
    return Image.fromarray(sgram)

def load_and_resize(path, max_dim=600):
    img = Image.open(path)
    img = ImageOps.grayscale(img)
    # Shrink so the longer side is at most max_dim, keeping the aspect ratio
    scale = min(1.0, max_dim / max(img.width, img.height))
    w = max(1, round(img.width * scale))
    h = max(1, round(img.height * scale))
    img = img.resize((w, h), Image.LANCZOS)
    arr = np.array(img)
    # Auto-invert if mostly white (to help user error)
    if np.mean(arr) > 200: arr = 255 - arr
    return arr

def load_and_resize_texture(path, width, height):
    img = Image.open(path)
    img = img.convert('RGB').resize((width, height), Image.LANCZOS)
    return img
