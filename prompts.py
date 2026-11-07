"""Plantillas de prompts (todo el texto generado debe estar en español)."""

VISION_SYSTEM = (
    "Eres un asistente de visión experto en alimentos. Identificas únicamente "
    "ingredientes comestibles claramente visibles en la imagen. No inventes. "
    "Responde SOLO con JSON válido, sin texto adicional ni markdown."
)

VISION_USER = (
    "Identifica los ingredientes comestibles visibles en esta imagen. "
    "Devuelve SOLO este JSON: "
    '{"ingredientes": [{"nombre": "tomate", "confianza": "alta|media|baja"}]}. '
    "Nombres en español, en singular, sin marcas. Si no hay alimentos, devuelve "
    '{"ingredientes": []}.'
)

RECIPE_SCHEMA = """{
  "nombre": "string",
  "descripcion": "string breve (1-2 frases)",
  "porciones": 2,
  "tiempo_preparacion_min": 10,
  "tiempo_coccion_min": 20,
  "dificultad": "Fácil | Media | Difícil",
  "ingredientes": [{"nombre": "string", "cantidad": "string con unidad", "basico_asumido": false}],
  "pasos": [{"numero": 1, "instruccion": "string", "tiempo_min": 5}],
  "consejos": ["string"],
  "descripcion_visual_en": "one English sentence describing how the finished plated dish looks"
}"""

RECIPE_SYSTEM = (
    "Eres un chef profesional que crea recetas prácticas y seguras. Respondes "
    "SOLO con JSON válido que cumpla exactamente el esquema pedido, sin markdown, "
    "sin comentarios y con todo el contenido en español (excepto 'descripcion_visual_en')."
)

RECIPE_USER = (
    "Ingredientes disponibles: {ingredients}.\n"
    "Básicos de despensa que puedes asumir (márcalos con basico_asumido=true): {pantry}.\n"
    "Crea UNA receta viable priorizando los ingredientes disponibles; no agregues "
    "ingredientes principales que no estén en la lista. Incluye pasos numerados claros "
    "con tiempos aproximados.\n"
    "Esquema JSON requerido:\n{schema}"
)

RECIPE_RETRY = (
    "Tu respuesta anterior no fue JSON válido o no cumplió el esquema ({error}). "
    "Responde de nuevo SOLO con el JSON correcto."
)

IMAGE_PROMPT = (
    "Professional food photography of {dish}, plated, natural light, shallow depth "
    "of field, appetizing, top-down 45 degrees, restaurant menu style, "
    "slow subtle camera movement"
)
