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


from simulacion import Grafo


def test_paso_reparte_caudal_entre_destinos_no_llenos():
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2])
    g.paso(1.0)
    assert t1.nivel == 25
    assert t2.nivel == 25
    assert g.tiempo == 1.0


def test_paso_tinaco_compartido_recibe_de_dos_bombas():
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    t3 = Tinaco("T3", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    b2 = Bomba("B2", 40, [t2, t3])
    g = Grafo([b1, b2], [t1, t2, t3])
    g.paso(1.0)
    assert t2.nivel == 45
    assert t1.nivel == 25
    assert t3.nivel == 20


def test_paso_todo_el_caudal_al_unico_destino_no_lleno():
    t1 = Tinaco("T1", 1000, nivel=1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2])
    g.paso(1.0)
    assert t2.nivel == 50


def test_terminado_cuando_todos_llenos():
    t1 = Tinaco("T1", 100)
    b1 = Bomba("B1", 1000, [t1])
    g = Grafo([b1], [t1])
    assert not g.terminado
    g.paso(1.0)
    assert t1.nivel == 100
    assert g.terminado


def test_paso_dt_invalido():
    t1 = Tinaco("T1", 1000)
    b1 = Bomba("B1", 50, [t1])
    g = Grafo([b1], [t1])
    with pytest.raises(ValueError):
        g.paso(0)


from simulacion import crear_grafo_default


def test_grafo_default_topologia():
    g = crear_grafo_default()
    nombres_tinacos = sorted(t.nombre for t in g.tinacos)
    nombres_bombas = sorted(b.nombre for b in g.bombas)
    assert nombres_tinacos == ["T1", "T2", "T3"]
    assert nombres_bombas == ["B1", "B2"]

    b1 = next(b for b in g.bombas if b.nombre == "B1")
    b2 = next(b for b in g.bombas if b.nombre == "B2")
    assert sorted(t.nombre for t in b1.destinos) == ["T1", "T2"]
    assert sorted(t.nombre for t in b2.destinos) == ["T2", "T3"]

    t2_b1 = next(t for t in b1.destinos if t.nombre == "T2")
    t2_b2 = next(t for t in b2.destinos if t.nombre == "T2")
    assert t2_b1 is t2_b2
