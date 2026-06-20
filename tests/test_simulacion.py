import pytest
from simulacion import Tinaco


def test_tinaco_nuevo_esta_vacio():
    t = Tinaco("T1", 1000)
    assert t.nivel == 0.0
    assert t.porcentaje == 0.0
    assert not t.lleno


def test_tinaco_agregar_sube_nivel():
    t = Tinaco("T1", 1000)
    t.agregar(250)
    assert t.nivel == 250
    assert t.porcentaje == 0.25


def test_tinaco_no_desborda():
    t = Tinaco("T1", 1000)
    t.agregar(1500)
    assert t.nivel == 1000
    assert t.lleno
    assert t.porcentaje == 1.0


def test_tinaco_capacidad_invalida():
    with pytest.raises(ValueError):
        Tinaco("T1", 0)


def test_tinaco_agregar_negativo_invalido():
    t = Tinaco("T1", 1000)
    with pytest.raises(ValueError):
        t.agregar(-5)


from simulacion import Bomba


def test_bomba_activa_con_destino_no_lleno():
    t = Tinaco("T1", 1000)
    b = Bomba("B1", 50, [t])
    assert b.activa
    assert b.destinos_no_llenos() == [t]


def test_bomba_inactiva_cuando_destinos_llenos():
    t = Tinaco("T1", 1000)
    t.agregar(1000)
    b = Bomba("B1", 50, [t])
    assert not b.activa
    assert b.destinos_no_llenos() == []


def test_bomba_caudal_invalido():
    t = Tinaco("T1", 1000)
    with pytest.raises(ValueError):
        Bomba("B1", 0, [t])
