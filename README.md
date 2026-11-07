# 🍳 Chef IA

App web responsive en Python + Streamlit: foto o imagen de ingredientes → ingredientes detectados (editables) → receta → paso a paso → imagen del plato.

## Arquitectura

| Archivo | Responsabilidad |
|---|---|
| `app.py` | UI y orquestación (único módulo que conoce a los demás) |
| `config.py` | URLs, IDs de modelos, valores por defecto |
| `models.py` | Dataclasses y validación de la receta |
| `prompts.py` | Plantillas de prompts |
| `json_utils.py` | Extracción de JSON de respuestas de LLM |
| `nvidia_client.py` | HTTP con reintentos, errores tipados y polling (202) |
| `image_utils.py` | Validar, redimensionar y convertir imágenes |
| `vision_service.py` | Detección de ingredientes (VLM) |
| `recipe_service.py` | Receta con deepseek-v4.1-flash |
| `image_service.py` | cosmos3-nano + extracción de fotograma |
| `ui_components.py` | Componentes de render |

## Puntos importantes

1. **DeepSeek es solo texto**: la detección de ingredientes usa un modelo de visión de build.nvidia.com (por defecto `meta/llama-3.2-90b-vision-instruct`, editable en la barra lateral).
2. **Cosmos3-nano genera video**: se muestra el video y un fotograma central como "imagen del plato".
3. **Verifica los IDs de modelo** en https://build.nvidia.com. Si `deepseek-v4.1-flash` responde 404, prueba con el prefijo de organización que muestre el catálogo (campo editable en la barra lateral, o `config.py`).
4. Cosmos puede tardar minutos; la receta se muestra aunque falle la imagen.

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
4. (Opcional) En *Secrets* agrega `NVIDIA_API_KEY` y `COSMOS_API_KEY`. Si no, cada usuario ingresa su clave en la barra lateral.

Las claves solo viven en `st.session_state`; no se guardan ni se registran.

## Límites

- Imágenes de hasta 10 MB (se redimensionan a 1024 px).
- La calidad de detección depende del modelo de visión elegido.
