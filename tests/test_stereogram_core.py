"""Tests for the image functions. They don't need a display or tkinter."""

import numpy as np
import pytest
from PIL import Image

from stereogram_core import load_and_resize, load_and_resize_texture, stereogram_from_depth_texture


def _texture(w, h, seed=0):
    rng = np.random.default_rng(seed)
    return Image.fromarray(rng.integers(30, 256, (h, w, 3), dtype=np.uint8))


@pytest.fixture
def save(tmp_path):
    def _save(img, name="img.png"):
        path = tmp_path / name
        img.save(path)
        return path
    return _save


def test_output_matches_the_depth_map_size():
    depth = np.full((40, 150), 128, dtype=np.uint8)
    out = stereogram_from_depth_texture(depth, _texture(64, 64), pattern_width=50, depth_strength=10)
    assert out.size == (150, 40)
    assert out.mode == "RGB"


@pytest.mark.parametrize("level", [0, 128, 255])
def test_flat_depth_repeats_with_period_pattern_width_plus_shift(level):
    pw, ds = 60, 20
    depth = np.full((30, 300), level, dtype=np.uint8)
    out = np.array(stereogram_from_depth_texture(depth, _texture(300, 30), pw, ds))
    period = pw + int(ds * (1.0 - level / 255.0))
    assert np.array_equal(out[:, period:], out[:, :-period])


def test_no_black_bands_where_the_texture_has_no_black():
    # Before the fix, far regions left a band of pure black after every pattern strip.
    depth = np.zeros((50, 300), dtype=np.uint8)
    out = np.array(stereogram_from_depth_texture(depth, _texture(300, 50), 80, 20))
    assert not (out == 0).all(axis=2).any()


def test_a_raised_shape_changes_the_repeat_inside_it():
    pw, ds = 60, 20
    depth = np.zeros((60, 300), dtype=np.uint8)
    depth[20:40, 150:220] = 255
    out = np.array(stereogram_from_depth_texture(depth, _texture(300, 60), pw, ds))
    row_far, row_near = out[5], out[30]
    x = 200
    assert np.array_equal(row_far[x], row_far[x - (pw + ds)])
    assert np.array_equal(row_near[x], row_near[x - pw])


def test_load_and_resize_keeps_the_aspect_ratio(save):
    path = save(Image.new("L", (1200, 300), 0))
    arr = load_and_resize(path, max_dim=600)
    assert arr.shape == (150, 600)


def test_load_and_resize_never_upscales(save):
    path = save(Image.new("L", (200, 100), 0))
    assert load_and_resize(path, max_dim=600).shape == (100, 200)


def test_mostly_white_depth_maps_are_inverted(save):
    img = Image.new("L", (100, 100), 255)
    img.paste(0, (40, 40, 60, 60))
    arr = load_and_resize(save(img))
    assert arr[0, 0] == 0
    assert arr[50, 50] == 255


def test_texture_is_resized_to_the_requested_size(save):
    path = save(_texture(64, 32))
    img = load_and_resize_texture(path, 300, 200)
    assert img.size == (300, 200)
    assert img.mode == "RGB"
