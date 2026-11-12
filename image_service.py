"""Imagen del plato con qwen-image (generación síncrona de imágenes)."""
from __future__ import annotations

import logging

import config
import model_studio_client
import prompts
from models import ImageResult, Recipe

logger = logging.getLogger(__name__)


def build_prompt(recipe: Recipe) -> str:
    """Construye el prompt en inglés a partir de la receta."""
    dish = recipe.visual_description_en or recipe.name
    return prompts.IMAGE_PROMPT.format(dish=dish)


def generate_dish_image(
    recipe: Recipe,
    api_key: str,
    model: str = config.IMAGE_MODEL_ID,
    size: str = config.IMAGE_SIZE_DEFAULT,
    prompt_extend: bool = True,
) -> ImageResult:
    """Genera la imagen del plato y descarga sus bytes (la URL firmada expira)."""
    prompt = build_prompt(recipe)
    url = model_studio_client.generate_image(api_key, model, prompt, size, prompt_extend)
    logger.info("Imagen generada (%s), descargando bytes…", model)
    image_bytes = model_studio_client.download_bytes(url)
    if not image_bytes:
        raise model_studio_client.ModelStudioError("La imagen generada llegó vacía.")
    return ImageResult(image_bytes=image_bytes, prompt=prompt)
