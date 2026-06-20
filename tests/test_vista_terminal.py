from simulacion import crear_grafo_default
from vista_terminal import barra, render


def test_barra_vacia():
    assert barra(0.0, ancho=10) == "[..........]"


def test_barra_llena():
    assert barra(1.0, ancho=10) == "[##########]"


def test_barra_mitad():
    assert barra(0.5, ancho=10) == "[#####.....]"


def test_render_incluye_tinacos_bombas_y_tiempo():
    g = crear_grafo_default()
    salida = render(g)
    assert "T1" in salida
    assert "T2" in salida
    assert "T3" in salida
    assert "B1" in salida
    assert "B2" in salida
    assert "Tiempo" in salida


def test_render_muestra_bomba_off_cuando_inactiva():
    g = crear_grafo_default()
    for t in g.tinacos:
        t.agregar(t.capacidad)
    salida = render(g)
    assert "OFF" in salida
