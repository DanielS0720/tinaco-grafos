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


import random as _random
from simulacion import Bomba, ENCENDIDA, REPOSO, FALLO


def test_bomba_estado_inicial_reposo():
    t = Tinaco("T1", 1000)
    b = Bomba("B1", 50, [t])
    assert b.estado == REPOSO
    assert not b.activa


def test_actualizar_estado_arranque_por_histeresis():
    t = Tinaco("T1", 1000)  # vacío: 0% < 30%
    b = Bomba("B1", 50, [t])
    b.actualizar_estado(1.0, 0.0, 5.0, 0.30, 0.95, _random.Random(0))
    assert b.estado == ENCENDIDA
    assert b.activa


def test_actualizar_estado_paro_por_histeresis():
    t = Tinaco("T1", 1000, nivel=1000)  # lleno
    b = Bomba("B1", 50, [t])
    b.estado = ENCENDIDA
    b.actualizar_estado(1.0, 0.0, 5.0, 0.30, 0.95, _random.Random(0))
    assert b.estado == REPOSO


def test_actualizar_estado_paro_con_tinaco_casi_lleno_por_consumo():
    # Por el consumo, un tinaco topado nunca llega al 100%, pero al superar el
    # umbral de paro (95%) la bomba debe apagarse igualmente.
    t = Tinaco("T1", 1000, nivel=992)  # 99.2%, NO está 'lleno'
    b = Bomba("B1", 50, [t])
    b.estado = ENCENDIDA
    assert not t.lleno
    b.actualizar_estado(1.0, 0.0, 5.0, 0.30, 0.95, _random.Random(0))
    assert b.estado == REPOSO


def test_actualizar_estado_fallo_forzado_y_recuperacion():
    t = Tinaco("T1", 1000)
    b = Bomba("B1", 50, [t])
    b.actualizar_estado(1.0, 1.0, 5.0, 0.30, 0.95, _random.Random(0))  # prob 1.0 -> falla
    assert b.estado == FALLO
    assert b.tiempo_falla_restante == 5.0
    for _ in range(5):  # 5 segundos sin volver a fallar
        b.actualizar_estado(1.0, 0.0, 5.0, 0.30, 0.95, _random.Random(0))
    assert b.estado != FALLO
    assert b.estado in (REPOSO, ENCENDIDA)


def test_bomba_caudal_invalido():
    t = Tinaco("T1", 1000)
    with pytest.raises(ValueError):
        Bomba("B1", 0, [t])


from simulacion import Grafo


def test_paso_reparte_caudal_entre_destinos_no_llenos():
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2], prob_falla=0.0)
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
    g = Grafo([b1, b2], [t1, t2, t3], prob_falla=0.0)
    g.paso(1.0)
    assert t2.nivel == 45
    assert t1.nivel == 25
    assert t3.nivel == 20


def test_paso_todo_el_caudal_al_unico_destino_no_lleno():
    t1 = Tinaco("T1", 1000, nivel=1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2], prob_falla=0.0)
    g.paso(1.0)
    assert t2.nivel == 50


def test_terminado_cuando_todos_llenos():
    t1 = Tinaco("T1", 100)
    b1 = Bomba("B1", 1000, [t1])
    g = Grafo([b1], [t1], prob_falla=0.0)
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


def test_tinaco_consumo_default_cero():
    t = Tinaco("T1", 1000)
    assert t.consumo == 0.0


def test_tinaco_consumir_baja_nivel():
    t = Tinaco("T1", 1000, nivel=500)
    t.consumir(200)
    assert t.nivel == 300


def test_tinaco_consumir_no_baja_de_cero():
    t = Tinaco("T1", 1000, nivel=100)
    t.consumir(250)
    assert t.nivel == 0


def test_tinaco_consumir_negativo_invalido():
    t = Tinaco("T1", 1000, nivel=100)
    with pytest.raises(ValueError):
        t.consumir(-5)


def test_paso_bomba_en_fallo_no_aporta():
    t = Tinaco("T1", 1000)
    b = Bomba("B1", 50, [t])
    b.estado = FALLO
    b.tiempo_falla_restante = 5.0
    g = Grafo([b], [t], prob_falla=0.0)
    g.paso(1.0)
    assert t.nivel == 0          # en fallo no aporta y no hay consumo
    assert b.estado == FALLO     # sigue averiada (5 - 1 = 4 s)


def test_paso_aplica_consumo_a_los_tinacos():
    t = Tinaco("T1", 1000, nivel=500, consumo=10.0)
    b = Bomba("B1", 50, [t])
    b.estado = REPOSO  # no aporta; solo se ve el consumo
    g = Grafo([b], [t], prob_falla=0.0, umbral_arranque=0.30)
    g.paso(1.0)
    assert t.nivel == 490
    assert b.estado == REPOSO


def test_grafo_default_tinacos_con_consumo():
    g = crear_grafo_default()
    assert all(t.consumo == 8.0 for t in g.tinacos)


def test_ciclo_vaciado_y_reencendido():
    t = Tinaco("T1", 100, nivel=100, consumo=10.0)
    b = Bomba("B1", 50, [t])
    g = Grafo([b], [t], prob_falla=0.0, umbral_arranque=0.30)
    for _ in range(8):  # 100 -> 20 (30% no es < 30%, sigue en reposo)
        g.paso(1.0)
    assert b.estado == REPOSO
    assert t.nivel == 20
    g.paso(1.0)  # 20% < 30% -> arranca
    assert b.estado == ENCENDIDA
    assert t.nivel == 60  # 20 + 50 (aporte) - 10 (consumo)


def test_grafo_default_sin_fallos_drena_y_reactiva():
    # Sin fallos, las bombas deben apagarse al llenar (paro por umbral) y luego
    # el consumo debe vaciar los tinacos hasta reactivar alguna bomba.
    g = crear_grafo_default(semilla=0)
    g.prob_falla = 0.0
    for _ in range(500):  # llenar hasta que todas las bombas se apaguen
        g.paso(1.0)
        if all(b.estado == REPOSO for b in g.bombas):
            break
    assert all(b.estado == REPOSO for b in g.bombas)
    nivel_al_apagar = max(t.nivel for t in g.tinacos)
    for _ in range(500):  # el consumo vacía hasta reactivar
        g.paso(1.0)
        if any(b.estado == ENCENDIDA for b in g.bombas):
            break
    assert any(b.estado == ENCENDIDA for b in g.bombas)
    assert min(t.nivel for t in g.tinacos) < nivel_al_apagar  # bajó de nivel
