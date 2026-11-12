"""Modelos de datos (dataclasses) sin dependencias del resto de la app."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Ingredient:
    name: str
    confidence: str = "media"  # alta | media | baja


@dataclass
class RecipeIngredient:
    name: str
    quantity: str
    assumed_basic: bool = False


@dataclass
class RecipeStep:
    number: int
    instruction: str
    minutes: int | None = None


@dataclass
class Recipe:
    name: str
    description: str
    servings: int
    prep_minutes: int
    cook_minutes: int
    difficulty: str
    ingredients: list[RecipeIngredient] = field(default_factory=list)
    steps: list[RecipeStep] = field(default_factory=list)
    tips: list[str] = field(default_factory=list)
    visual_description_en: str = ""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Recipe":
        """Valida y construye una receta desde el JSON del LLM. Lanza ValueError si es inválido."""
        if not isinstance(data, dict):
            raise ValueError("La receta debe ser un objeto JSON.")
        for key in ("nombre", "ingredientes", "pasos"):
            if key not in data:
                raise ValueError(f"Falta el campo obligatorio '{key}'.")

        def _int(value: Any, default: int = 0) -> int:
            try:
                return max(0, int(float(value)))
            except (TypeError, ValueError):
                return default

        ings_raw, steps_raw = data["ingredientes"], data["pasos"]
        if not isinstance(ings_raw, list) or not ings_raw:
            raise ValueError("'ingredientes' debe ser una lista no vacía.")
        if not isinstance(steps_raw, list) or not steps_raw:
            raise ValueError("'pasos' debe ser una lista no vacía.")

        ingredients = []
        for item in ings_raw:
            if not isinstance(item, dict) or not str(item.get("nombre", "")).strip():
                raise ValueError("Ingrediente inválido.")
            ingredients.append(RecipeIngredient(
                name=str(item["nombre"]).strip(),
                quantity=str(item.get("cantidad", "")).strip(),
                assumed_basic=bool(item.get("basico_asumido", False)),
            ))

        steps = []
        for idx, item in enumerate(steps_raw, start=1):
            text = item.get("instruccion") if isinstance(item, dict) else item
            if not str(text or "").strip():
                raise ValueError("Paso inválido.")
            minutes = _int(item.get("tiempo_min"), 0) if isinstance(item, dict) else 0
            steps.append(RecipeStep(number=idx, instruction=str(text).strip(), minutes=minutes or None))

        tips = data.get("consejos") or []
        return Recipe(
            name=str(data["nombre"]).strip(),
            description=str(data.get("descripcion", "")).strip(),
            servings=_int(data.get("porciones"), 2) or 2,
            prep_minutes=_int(data.get("tiempo_preparacion_min")),
            cook_minutes=_int(data.get("tiempo_coccion_min")),
            difficulty=str(data.get("dificultad", "Media")).strip() or "Media",
            ingredients=ingredients,
            steps=steps,
            tips=[str(t).strip() for t in tips if str(t).strip()] if isinstance(tips, list) else [],
            visual_description_en=str(data.get("descripcion_visual_en", "")).strip(),
        )


@dataclass
class ImageResult:
    image_bytes: bytes
    prompt: str
