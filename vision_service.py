"""Detección de ingredientes a partir de una imagen usando un VLM de NVIDIA."""
from __future__ import annotations

import logging

import config
import image_utils
import json_utils
import nvidia_client
import prompts
from models import Ingredient

logger = logging.getLogger(__name__)


def detect_ingredients(image_bytes: bytes, api_key: str, model: str = config.VISION_MODEL_ID) -> list[Ingredient]:
    """Devuelve los ingredientes detectados (sin duplicados)."""
    data_uri = image_utils.prepare_for_model(image_bytes)
    messages = [
        {"role": "system", "content": prompts.VISION_SYSTEM},
        {"role": "user", "content": [
            {"type": "text", "text": prompts.VISION_USER},
            {"type": "image_url", "image_url": {"url": data_uri}},
        ]},
    ]
    text = nvidia_client.chat_completion(
        api_key, model, messages, config.LLM_TEMPERATURE_VISION, config.LLM_MAX_TOKENS_VISION
    )
    try:
        parsed = json_utils.extract_json(text)
    except ValueError as exc:
        raise nvidia_client.NvidiaAPIError("No se pudo interpretar la respuesta de visión.") from exc

    raw = parsed.get("ingredientes", []) if isinstance(parsed, dict) else parsed
    seen: set[str] = set()
    result: list[Ingredient] = []
    for item in raw if isinstance(raw, list) else []:
        name = str(item.get("nombre", "") if isinstance(item, dict) else item).strip().lower()
        if name and name not in seen:
            seen.add(name)
            conf = str(item.get("confianza", "media")) if isinstance(item, dict) else "media"
            result.append(Ingredient(name=name, confidence=conf))
    logger.info("Ingredientes detectados: %d", len(result))
    return result
