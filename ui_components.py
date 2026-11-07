"""Componentes de interfaz reutilizables."""
from __future__ import annotations

import streamlit as st

from models import Recipe


def render_recipe_header(recipe: Recipe) -> None:
    st.subheader(recipe.name)
    if recipe.description:
        st.write(recipe.description)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Porciones", recipe.servings)
    c2.metric("Preparación", f"{recipe.prep_minutes} min")
    c3.metric("Cocción", f"{recipe.cook_minutes} min")
    c4.metric("Dificultad", recipe.difficulty)


def render_recipe_ingredients(recipe: Recipe) -> None:
    st.markdown("#### 🧾 Ingredientes")
    for ing in recipe.ingredients:
        tag = " _(básico asumido)_" if ing.assumed_basic else ""
        st.markdown(f"- **{ing.name}**: {ing.quantity}{tag}")


def render_steps(recipe: Recipe) -> None:
    st.markdown("#### 👩‍🍳 Paso a paso")
    for step in recipe.steps:
        time_txt = f" _(~{step.minutes} min)_" if step.minutes else ""
        st.checkbox(f"**Paso {step.number}.** {step.instruction}{time_txt}", key=f"step_{step.number}")
    if recipe.tips:
        st.markdown("#### 💡 Consejos")
        for tip in recipe.tips:
            st.markdown(f"- {tip}")


def recipe_to_markdown(recipe: Recipe) -> str:
    """Convierte la receta a Markdown descargable."""
    lines = [f"# {recipe.name}", "", recipe.description, "",
             f"**Porciones:** {recipe.servings} · **Preparación:** {recipe.prep_minutes} min · "
             f"**Cocción:** {recipe.cook_minutes} min · **Dificultad:** {recipe.difficulty}",
             "", "## Ingredientes"]
    for ing in recipe.ingredients:
        lines.append(f"- {ing.name}: {ing.quantity}" + (" (básico asumido)" if ing.assumed_basic else ""))
    lines += ["", "## Preparación"]
    for step in recipe.steps:
        extra = f" (~{step.minutes} min)" if step.minutes else ""
        lines.append(f"{step.number}. {step.instruction}{extra}")
    if recipe.tips:
        lines += ["", "## Consejos"] + [f"- {t}" for t in recipe.tips]
    return "\n".join(lines) + "\n"
