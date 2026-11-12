"""Chef IA: foto de ingredientes -> receta, paso a paso e imagen del plato."""
from __future__ import annotations

import logging

import streamlit as st

import config
import image_service
import image_utils
import model_studio_client
import recipe_service
import ui_components
import vision_service

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Chef IA", page_icon="🍳", layout="wide")


def _secret(name: str) -> str:
    """Lee un secreto de st.secrets si existe."""
    try:
        return str(st.secrets.get(name, ""))
    except Exception:  # noqa: BLE001 - no hay archivo de secretos
        return ""


def _friendly(exc: Exception) -> str:
    if isinstance(exc, model_studio_client.AuthError):
        return "🔑 La clave de API es inválida o no tiene permisos."
    if isinstance(exc, model_studio_client.RateLimitError):
        return "⏳ Límite de solicitudes alcanzado. Espera un momento e intenta de nuevo."
    if isinstance(exc, (model_studio_client.ModelStudioError, image_utils.InvalidImageError, ValueError)):
        return f"⚠️ {exc}"
    return "⚠️ Ocurrió un error inesperado. Intenta de nuevo."


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Configuración")
    llm_key = st.text_input("API key Model Studio", type="password", key="llm_key",
                            value=_secret("DASHSCOPE_API_KEY"),
                            help="Clave de Alibaba Cloud Model Studio (formato sk-…)")

    st.subheader("Modelos")
    text_model = st.selectbox("Modelo de texto (receta)", config.TEXT_MODEL_OPTIONS + ["Otro…"],
                              help="Genera la receta y el paso a paso.")
    if text_model == "Otro…":
        text_model = st.text_input("ID del modelo de texto", value=config.TEXT_MODEL_ID)
    vision_model = st.selectbox("Modelo de visión (ingredientes)", config.VISION_MODEL_OPTIONS + ["Otro…"])
    if vision_model == "Otro…":
        vision_model = st.text_input("ID del modelo de visión", value=config.VISION_MODEL_ID)
    image_model = st.selectbox("Modelo de imagen (plato)", config.IMAGE_MODEL_OPTIONS + ["Otro…"],
                               help="Genera la imagen del plato final.")
    if image_model == "Otro…":
        image_model = st.text_input("ID del modelo de imagen", value=config.IMAGE_MODEL_ID)

    with st.expander("Imagen del plato (avanzado)"):
        image_size = st.selectbox("Tamaño", config.IMAGE_SIZE_OPTIONS)
        prompt_extend = st.checkbox("Ampliar el prompt automáticamente", value=True)

# ---------------- Estado ----------------
for key, default in (("ingredients", None), ("recipe", None), ("media", None), ("media_error", "")):
    st.session_state.setdefault(key, default)

st.title("🍳 Chef IA")
st.caption("Toma una foto de tus ingredientes y obtén una receta, el paso a paso y una imagen del plato.")

# ---------------- 1. Imagen ----------------
tab_cam, tab_up = st.tabs(["📷 Tomar foto", "🖼️ Subir imagen"])
with tab_cam:
    cam = st.camera_input("Fotografía tus ingredientes")
with tab_up:
    upl = st.file_uploader("Sube una imagen", type=config.ALLOWED_IMAGE_TYPES)

source = cam or upl
image_bytes = source.getvalue() if source else None
if image_bytes:
    try:
        st.image(image_utils.load_image(image_bytes), caption="Imagen seleccionada", use_container_width=True)
    except image_utils.InvalidImageError as exc:
        st.error(_friendly(exc))
        image_bytes = None

# ---------------- 2. Ingredientes ----------------
if st.button("🔍 Analizar ingredientes", disabled=not image_bytes, use_container_width=True):
    if not llm_key:
        st.warning("Ingresa tu API key en la barra lateral.")
    else:
        st.session_state.update(recipe=None, media=None, media_error="")
        for k in [k for k in st.session_state if str(k).startswith("step_")]:
            del st.session_state[k]
        try:
            with st.spinner("Identificando ingredientes…"):
                found = vision_service.detect_ingredients(image_bytes, llm_key, vision_model)
            st.session_state.ingredients = [i.name for i in found]
        except Exception as exc:  # noqa: BLE001
            st.error(_friendly(exc))

if st.session_state.ingredients is not None:
    st.markdown("### 🥕 Ingredientes detectados")
    st.caption("Puedes corregir, agregar o quitar filas antes de continuar.")
    edited = st.data_editor(
        [{"Ingrediente": n} for n in st.session_state.ingredients],
        num_rows="dynamic", use_container_width=True, key="ing_editor",
        column_config={"Ingrediente": st.column_config.TextColumn(required=True)},
    )
    names = [str(r.get("Ingrediente", "")).strip().lower() for r in edited if str(r.get("Ingrediente", "")).strip()]
    names = list(dict.fromkeys(names))

    if len(names) < config.MIN_INGREDIENTS:
        st.warning(f"Se detectaron menos de {config.MIN_INGREDIENTS} ingredientes. "
                   "Agrega más manualmente o toma otra foto.")

    # ---------------- 3. Receta + imagen ----------------
    if st.button("👩‍🍳 Generar receta", type="primary",
                 disabled=len(names) < config.MIN_INGREDIENTS, use_container_width=True):
        if not llm_key:
            st.warning("Ingresa tu API key en la barra lateral.")
        else:
            st.session_state.update(recipe=None, media=None, media_error="")
            try:
                with st.status("Creando tu receta…", expanded=True) as status:
                    st.write("Generando receta y pasos…")
                    st.session_state.recipe = recipe_service.generate_recipe(names, llm_key, text_model)
                    st.write("Generando imagen del plato…")
                    try:
                        st.session_state.media = image_service.generate_dish_image(
                            st.session_state.recipe, llm_key, model=image_model,
                            size=image_size, prompt_extend=prompt_extend,
                        )
                    except Exception as exc:  # noqa: BLE001 - la receta se muestra igual
                        st.session_state.media_error = _friendly(exc)
                    status.update(label="¡Listo!", state="complete", expanded=False)
            except Exception as exc:  # noqa: BLE001
                st.error(_friendly(exc))

# ---------------- 4. Resultados ----------------
recipe = st.session_state.recipe
if recipe:
    st.divider()
    col_img, col_info = st.columns([1, 1.2])
    with col_img:
        media = st.session_state.media
        if media:
            st.image(media.image_bytes, caption=f"Así podría verse: {recipe.name}", use_container_width=True)
        else:
            st.warning(st.session_state.media_error or "No se pudo generar la imagen del plato.")
    with col_info:
        ui_components.render_recipe_header(recipe)
        ui_components.render_recipe_ingredients(recipe)
    ui_components.render_steps(recipe)
    st.download_button("⬇️ Descargar receta (Markdown)", ui_components.recipe_to_markdown(recipe),
                       file_name="receta.md", mime="text/markdown", use_container_width=True)
