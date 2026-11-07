import io

import pytest
from PIL import Image

import image_utils


def _png(w: int, h: int) -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", (w, h), (200, 50, 50, 255)).save(buf, format="PNG")
    return buf.getvalue()


def test_load_image_ok():
    assert image_utils.load_image(_png(10, 10)).mode == "RGB"


def test_load_image_invalid():
    with pytest.raises(image_utils.InvalidImageError):
        image_utils.load_image(b"no es imagen")


def test_load_image_empty():
    with pytest.raises(image_utils.InvalidImageError):
        image_utils.load_image(b"")


def test_resize_keeps_ratio():
    out = image_utils.resize_image(image_utils.load_image(_png(2000, 1000)), 1000)
    assert out.size == (1000, 500)


def test_resize_no_upscale():
    out = image_utils.resize_image(image_utils.load_image(_png(100, 50)), 1000)
    assert out.size == (100, 50)


def test_data_uri_prefix():
    assert image_utils.prepare_for_model(_png(50, 50)).startswith("data:image/jpeg;base64,")
