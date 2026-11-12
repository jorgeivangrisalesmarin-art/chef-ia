"""Generación de la receta con deepseek-v4-pro-0813 (salida JSON validada)."""
from __future__ import annotations

import logging

import config
import json_utils
import model_studio_client
import prompts
from models import Recipe

logger = logging.getLogger(__name__)


def parse_recipe_json(text: str) -> Recipe:
    """Limpia, parsea y valida el JSON de la receta. Lanza ValueError si es inválido."""
    return Recipe.from_dict(json_utils.extract_json(text))


def generate_recipe(ingredients: list[str], api_key: str, model: str = config.TEXT_MODEL_ID) -> Recipe:
    """Genera una receta; reintenta una vez si el JSON es inválido."""
    if len(ingredients) < config.MIN_INGREDIENTS:
        raise ValueError(f"Se necesitan al menos {config.MIN_INGREDIENTS} ingredientes.")
    messages = [
        {"role": "system", "content": prompts.RECIPE_SYSTEM},
        {"role": "user", "content": prompts.RECIPE_USER.format(
            ingredients=", ".join(ingredients),
            pantry=", ".join(config.DEFAULT_PANTRY_BASICS),
            schema=prompts.RECIPE_SCHEMA,
        )},
    ]
    last_error: Exception | None = None
    for attempt in range(config.LLM_JSON_RETRIES + 1):
        text = model_studio_client.chat_completion(
            api_key, model, messages, config.LLM_TEMPERATURE_RECIPE, config.LLM_MAX_TOKENS_RECIPE,
            enable_thinking=False,
        )
        try:
            return parse_recipe_json(text)
        except ValueError as exc:
            last_error = exc
            logger.warning("JSON de receta inválido (intento %d)", attempt + 1)
            messages += [
                {"role": "assistant", "content": text},
                {"role": "user", "content": prompts.RECIPE_RETRY.format(error=exc)},
            ]
    raise model_studio_client.ModelStudioError(f"El modelo no devolvió una receta válida: {last_error}")
