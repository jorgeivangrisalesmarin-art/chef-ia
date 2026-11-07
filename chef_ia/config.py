"""Configuración central: URLs, IDs de modelos y valores por defecto."""

# --- NVIDIA build.nvidia.com ---
NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
COSMOS_URL = "https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano"
NVCF_STATUS_URL = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/status/{reqid}"

# --- Modelos ---
# Modelo de texto (receta y pasos). Editable desde la barra lateral.
# TODO: verifica en build.nvidia.com el ID exacto vigente (puede requerir prefijo
# de organización, p. ej. "deepseek-ai/...").
TEXT_MODEL_ID = "deepseek-v4.1-flash"

# Modelo de visión (DeepSeek es solo texto y no puede analizar imágenes).
# TODO: verifica en build.nvidia.com que el ID siga disponible.
VISION_MODEL_ID = "meta/llama-3.2-90b-vision-instruct"
VISION_MODEL_OPTIONS = [
    "meta/llama-3.2-90b-vision-instruct",
    "meta/llama-3.2-11b-vision-instruct",
]

# --- Parámetros por defecto de Cosmos3-nano (según el ejemplo oficial) ---
COSMOS_MODEL_MODE = "text2video"
COSMOS_DEFAULTS = {
    "resolution": "480_16_9",
    "num_frames": 25,
    "num_inference_steps": 35,
    "fps": 24,
    "seed": 42,
}
COSMOS_RESOLUTIONS = ["480_16_9", "480_9_16", "480_1_1"]  # TODO: verificar opciones vigentes

# --- Red ---
HTTP_TIMEOUT_S = 120
HTTP_MAX_RETRIES = 3
BACKOFF_BASE_S = 2.0
POLL_INTERVAL_S = 3.0
POLL_MAX_INTERVAL_S = 10.0
POLL_TIMEOUT_S = 600  # tiempo máximo esperando a Cosmos

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
