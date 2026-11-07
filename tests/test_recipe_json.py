import json

import pytest

import recipe_service

VALID = {
    "nombre": "Omelette de tomate",
    "descripcion": "Rápido y simple",
    "porciones": 2,
    "tiempo_preparacion_min": 5,
    "tiempo_coccion_min": 10,
    "dificultad": "Fácil",
    "ingredientes": [{"nombre": "huevo", "cantidad": "3 unidades", "basico_asumido": False},
                     {"nombre": "sal", "cantidad": "1 pizca", "basico_asumido": True}],
    "pasos": [{"numero": 1, "instruccion": "Bate los huevos", "tiempo_min": 2}],
    "consejos": ["Usa fuego medio"],
}


def test_valid_json():
    r = recipe_service.parse_recipe_json(json.dumps(VALID))
    assert r.name == "Omelette de tomate"
    assert r.ingredients[1].assumed_basic is True
    assert r.steps[0].minutes == 2


def test_markdown_fences():
    r = recipe_service.parse_recipe_json("```json\n" + json.dumps(VALID) + "\n```")
    assert len(r.steps) == 1


def test_text_around_json():
    r = recipe_service.parse_recipe_json("Aquí tienes:\n" + json.dumps(VALID) + "\nBuen provecho")
    assert r.servings == 2


def test_missing_field():
    bad = {k: v for k, v in VALID.items() if k != "pasos"}
    with pytest.raises(ValueError):
        recipe_service.parse_recipe_json(json.dumps(bad))


def test_not_json():
    with pytest.raises(ValueError):
        recipe_service.parse_recipe_json("lo siento, no puedo")


def test_empty_steps():
    with pytest.raises(ValueError):
        recipe_service.parse_recipe_json(json.dumps({**VALID, "pasos": []}))
