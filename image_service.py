"""Imagen del plato con cosmos3-nano (genera video; se extrae un fotograma)."""
from __future__ import annotations

import base64
import binascii
import logging
import os
import tempfile
from typing import Any, Callable

import cv2

import config
import nvidia_client
import prompts
from models import ImageResult, Recipe

logger = logging.getLogger(__name__)


def build_prompt(recipe: Recipe) -> str:
    """Construye el prompt en inglés a partir de la receta."""
    dish = recipe.visual_description_en or recipe.name
    return prompts.IMAGE_PROMPT.format(dish=dish)


def extract_frame(video_mp4: bytes, position: float = 0.5) -> bytes:
    """Extrae un fotograma (0..1 de la duración) como PNG."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video_mp4)
        path = tmp.name
    try:
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total > 1:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int((total - 1) * position))
        ok, frame = cap.read()
        cap.release()
        if not ok:
            raise nvidia_client.NvidiaAPIError("No se pudo extraer un fotograma del video.")
        ok, buf = cv2.imencode(".png", frame)
        if not ok:
            raise nvidia_client.NvidiaAPIError("No se pudo codificar el fotograma.")
        return buf.tobytes()
    finally:
        os.unlink(path)


def generate_dish_media(
    recipe: Recipe,
    api_key: str,
    params: dict[str, Any] | None = None,
    poll_timeout: int = config.POLL_TIMEOUT_S,
    on_progress: Callable[[str], None] | None = None,
) -> ImageResult:
    """Genera el clip, lo decodifica y extrae el fotograma representativo."""
    prompt = build_prompt(recipe)
    payload = {"model_mode": config.COSMOS_MODEL_MODE, "prompt": prompt,
               **{**config.COSMOS_DEFAULTS, **(params or {})}}
    data = nvidia_client.post_json(
        config.COSMOS_URL, api_key, payload, poll_timeout=poll_timeout, on_progress=on_progress
    )
    b64 = data.get("b64_video")
    if not b64:
        raise nvidia_client.NvidiaAPIError("La respuesta de Cosmos no incluye 'b64_video'.")
    try:
        video = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise nvidia_client.NvidiaAPIError("El video recibido está corrupto.") from exc
    return ImageResult(frame_png=extract_frame(video), video_mp4=video, prompt=prompt)
