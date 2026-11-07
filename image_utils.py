"""Validación, redimensionado y conversión de imágenes."""
from __future__ import annotations

import base64
import io

from PIL import Image, UnidentifiedImageError

import config


class InvalidImageError(ValueError):
    """La imagen no es válida o excede los límites."""


def load_image(data: bytes) -> Image.Image:
    """Valida tamaño y formato; devuelve la imagen en RGB."""
    if not data:
        raise InvalidImageError("No se recibió ninguna imagen.")
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise InvalidImageError(f"La imagen supera {config.MAX_UPLOAD_MB} MB.")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("El archivo no es una imagen válida.") from exc
    return img.convert("RGB")


def resize_image(img: Image.Image, max_side: int = config.MAX_IMAGE_SIDE_PX) -> Image.Image:
    """Reduce la imagen manteniendo proporción si algún lado excede max_side."""
    w, h = img.size
    scale = max_side / max(w, h)
    if scale >= 1:
        return img.copy()
    return img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)


def to_jpeg_bytes(img: Image.Image, quality: int = 88) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def to_data_uri(img: Image.Image) -> str:
    """Convierte la imagen a data URI JPEG en base64."""
    b64 = base64.b64encode(to_jpeg_bytes(img)).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def prepare_for_model(data: bytes) -> str:
    """Pipeline completo: valida, redimensiona y devuelve data URI."""
    return to_data_uri(resize_image(load_image(data)))
