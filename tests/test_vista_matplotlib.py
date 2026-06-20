import pytest

pytest.importorskip("networkx")

from simulacion import crear_grafo_default
from vista_matplotlib import construir_red


def test_construir_red_nodos_y_aristas():
    g = crear_grafo_default()
    red = construir_red(g)
    assert set(red.nodes) == {"B1", "B2", "T1", "T2", "T3"}
    assert set(red.edges) == {
        ("B1", "T1"),
        ("B1", "T2"),
        ("B2", "T2"),
        ("B2", "T3"),
    }


def test_construir_red_marca_tipo_de_nodo():
    g = crear_grafo_default()
    red = construir_red(g)
    assert red.nodes["B1"]["tipo"] == "bomba"
    assert red.nodes["T1"]["tipo"] == "tinaco"


from vista_matplotlib import _color_led
from simulacion import ENCENDIDA, REPOSO, FALLO


def test_color_led_por_estado():
    assert _color_led(ENCENDIDA) == "limegreen"
    assert _color_led(REPOSO) == "gold"
    assert _color_led(FALLO) == "red"
