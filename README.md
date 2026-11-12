# 🍳 Chef IA

App web responsive en Python + Streamlit: foto o imagen de ingredientes → ingredientes detectados (editables) → receta → paso a paso → imagen del plato.

## Proveedor de IA

**Alibaba Cloud Model Studio** (DashScope, región internacional Singapur) — endpoint OpenAI-compatible para texto/visión y API multimodal para imágenes. Cada usuario aporta su propia API key (`sk-…`) en la barra lateral; no hay clave en el código.

| Rol | Modelo por defecto | Alternativas en la barra lateral |
|---|---|---|
| Texto (receta y pasos) | `deepseek-v4-pro-0813` | `deepseek-v4-flash-0731`, `qwen3.8-flash` |
| Visión (detección de ingredientes) | `qwen3-vl-plus` | `qwen3.8-omni-flash` |
| Imagen del plato | `qwen-image-3.0-pro` | `qwen-image-3.0`, `z-image-turbo` |

Todos los IDs se verificaron con llamadas reales el 2026-11-12 contra `dashscope-intl.aliyuncs.com`.

## Arquitectura

| Archivo | Responsabilidad |
|---|---|
| `app.py` | UI y orquestación (único módulo que conoce a los demás) |
| `config.py` | URLs, IDs de modelos, valores por defecto |
| `models.py` | Dataclasses y validación de la receta |
| `prompts.py` | Plantillas de prompts |
| `json_utils.py` | Extracción de JSON de respuestas de LLM |
| `model_studio_client.py` | HTTP con reintentos y errores tipados (chat + imágenes) |
| `image_utils.py` | Validar, redimensionar y convertir imágenes |
| `vision_service.py` | Detección de ingredientes (VLM `qwen3-vl-plus`) |
| `recipe_service.py` | Receta con `deepseek-v4-pro-0813` |
| `image_service.py` | Imagen del plato con `qwen-image-3.0-pro` |
| `ui_components.py` | Componentes de render |

## Puntos importantes

1. **Tres llamadas diferenciadas**: la receta usa el endpoint OpenAI-compatible (`/compatible-mode/v1/chat/completions`) con `enable_thinking: false` para respuesta inmediata; la detección de ingredientes usa el mismo endpoint con la imagen como data URI (`image_url`); la imagen del plato usa la API multimodal nativa (`/api/v1/services/aigc/multimodal-generation/generation`), que responde síncrona con una URL firmada de la imagen.
2. **La URL de la imagen firmada expira en horas**: la app descarga los bytes inmediatamente y los guarda en `st.session_state`.
3. Los IDs de modelos son editables desde la barra lateral (opción "Otro…") por si Model Studio retira o renombra alguno.
4. Si falla la imagen, la receta se muestra igual.

## Ejecución local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py
pytest
```

## Despliegue en Streamlit Community Cloud

1. Sube el proyecto a un repositorio de GitHub.
2. En https://share.streamlit.io crea una app: archivo principal `app.py`.
3. En *Advanced settings* elige Python 3.11.
4. (Opcional) En *Secrets* agrega `DASHSCOPE_API_KEY = "sk-…"`. Si no, cada usuario ingresa su clave en la barra lateral.

Las claves solo viven en `st.session_state`; no se guardan ni se registran.

## Límites

- Imágenes de hasta 10 MB (se redimensionan a 1024 px).
- La calidad de detección depende del modelo de visión elegido.
- La generación de la imagen del plato tarda ~10–30 s (síncrona).
