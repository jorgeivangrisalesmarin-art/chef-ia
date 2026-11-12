"""Configuración central: URLs, IDs de modelos y valores por defecto."""

# --- Alibaba Cloud Model Studio (DashScope, región internacional Singapur) ---
CHAT_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
MULTIMODAL_URL = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

# --- Modelos (verificados con llamadas reales el 2026-11-12) ---
# Modelo de texto (receta y pasos). Editable desde la barra lateral.
TEXT_MODEL_ID = "deepseek-v4-pro-0813"
TEXT_MODEL_OPTIONS = [
    "deepseek-v4-pro-0813",
    "deepseek-v4-flash-0731",
    "qwen3.8-flash",
]

# Modelo de visión (detección de ingredientes en la foto).
VISION_MODEL_ID = "qwen3-vl-plus"
VISION_MODEL_OPTIONS = [
    "qwen3-vl-plus",
    "qwen3.8-omni-flash",
]

# Modelo de generación de imágenes (imagen del plato).
IMAGE_MODEL_ID = "qwen-image-3.0-pro"
IMAGE_MODEL_OPTIONS = [
    "qwen-image-3.0-pro",
    "qwen-image-3.0",
    "z-image-turbo",
]

# --- Parámetros por defecto de generación de imágenes ---
IMAGE_SIZE_DEFAULT = "1024*1024"
IMAGE_SIZE_OPTIONS = ["1024*1024", "1280*720", "720*1280"]

# --- Red ---
HTTP_TIMEOUT_S = 120
HTTP_MAX_RETRIES = 3
BACKOFF_BASE_S = 2.0
IMAGE_TIMEOUT_S = 300  # La generación de imágenes puede tardar más que el texto

# --- Generación de texto ---
LLM_TEMPERATURE_VISION = 0.1
LLM_TEMPERATURE_RECIPE = 0.6
LLM_MAX_TOKENS_VISION = 600
LLM_MAX_TOKENS_RECIPE = 2000
LLM_JSON_RETRIES = 1

# --- Imágenes ---
MAX_IMAGE_SIDE_PX = 1024
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]
MAX_UPLOAD_MB = 10
MIN_INGREDIENTS = 2

# --- Receta ---
DEFAULT_PANTRY_BASICS = ["sal", "aceite", "agua", "pimienta"]
