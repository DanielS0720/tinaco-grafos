import random

# Estados posibles de una bomba (color del LED en las vistas).
ENCENDIDA = "encendida"  # LED verde: bombeando
REPOSO = "reposo"        # LED amarillo: sana pero inactiva
FALLO = "fallo"          # LED rojo: averiada


class Tinaco:
    """Nodo destino del grafo: un tinaco con capacidad, nivel y consumo (L/s)."""

    def __init__(self, nombre, capacidad, nivel=0.0, consumo=0.0):
        if capacidad <= 0:
            raise ValueError("la capacidad debe ser positiva")
        if consumo < 0:
            raise ValueError("el consumo no puede ser negativo")
        self.nombre = nombre
        self.capacidad = float(capacidad)
        self.nivel = float(nivel)
        self.consumo = float(consumo)

    @property
    def porcentaje(self):
        return self.nivel / self.capacidad

    @property
    def lleno(self):
        return self.nivel >= self.capacidad

    def agregar(self, litros):
        if litros < 0:
            raise ValueError("los litros a agregar no pueden ser negativos")
        self.nivel = min(self.capacidad, self.nivel + litros)

    def consumir(self, litros):
        if litros < 0:
            raise ValueError("los litros a consumir no pueden ser negativos")
        self.nivel = max(0.0, self.nivel - litros)


class Bomba:
    """Nodo fuente del grafo: bombea agua a sus tinacos destino.

    Tiene una máquina de estados (encendida/reposo/fallo) controlada por
    histéresis de nivel y por fallos aleatorios con autorrecuperación.
    """

    def __init__(self, nombre, caudal, destinos):
        if caudal <= 0:
            raise ValueError("el caudal debe ser positivo")
        self.nombre = nombre
        self.caudal = float(caudal)
        self.destinos = list(destinos)
        self.estado = REPOSO
        self.tiempo_falla_restante = 0.0

    def destinos_no_llenos(self):
        return [t for t in self.destinos if not t.lleno]

    @property
    def activa(self):
        return self.estado == ENCENDIDA

    def actualizar_estado(self, dt, prob_falla, duracion_falla,
                          umbral_arranque, umbral_paro, aleatorio):
        # 1. Si está averiada, descontar el temporizador de recuperación.
        if self.estado == FALLO:
            self.tiempo_falla_restante -= dt
            if self.tiempo_falla_restante > 0:
                return
            self.tiempo_falla_restante = 0.0
            self.estado = REPOSO
        # 2. Una bomba sana puede averiarse al azar.
        if aleatorio.random() < prob_falla:
            self.estado = FALLO
            self.tiempo_falla_restante = duracion_falla
            return
        # 3. Histéresis de arranque/paro. El paro usa un umbral fraccional
        #    (no "lleno"): por el consumo un tinaco topado nunca llega al 100%,
        #    así que exigir 100% dejaría la bomba encendida para siempre.
        if self.estado == REPOSO and any(
            t.porcentaje < umbral_arranque for t in self.destinos
        ):
            self.estado = ENCENDIDA
        elif self.estado == ENCENDIDA and all(
            t.porcentaje >= umbral_paro for t in self.destinos
        ):
            self.estado = REPOSO


class Grafo:
    """Grafo de la simulación: bombas (fuentes) y tinacos (destinos)."""

    def __init__(self, bombas, tinacos, prob_falla=0.005, duracion_falla=5.0,
                 umbral_arranque=0.30, umbral_paro=0.95, semilla=None):
        self.bombas = list(bombas)
        self.tinacos = list(tinacos)
        self.tiempo = 0.0
        self.prob_falla = prob_falla
        self.duracion_falla = duracion_falla
        self.umbral_arranque = umbral_arranque
        self.umbral_paro = umbral_paro
        self.aleatorio = random.Random(semilla)

    @property
    def terminado(self):
        return all(t.lleno for t in self.tinacos)

    def paso(self, dt):
        if dt <= 0:
            raise ValueError("dt debe ser positivo")
        # 1. Actualizar el estado (LED) de cada bomba.
        for bomba in self.bombas:
            bomba.actualizar_estado(dt, self.prob_falla, self.duracion_falla,
                                    self.umbral_arranque, self.umbral_paro,
                                    self.aleatorio)
        # 2. Acumular los aportes de las bombas encendidas. El tinaco
        #    compartido suma los caudales de varias bombas.
        aportes = {id(t): 0.0 for t in self.tinacos}
        for bomba in self.bombas:
            if bomba.estado != ENCENDIDA:
                continue
            objetivos = bomba.destinos_no_llenos()
            if not objetivos:
                continue
            litros = bomba.caudal * dt / len(objetivos)
            for t in objetivos:
                aportes[id(t)] += litros
        # 3. Aplicar el aporte y luego el consumo de cada tinaco.
        for t in self.tinacos:
            t.agregar(aportes[id(t)])
            t.consumir(t.consumo * dt)
        self.tiempo += dt


def crear_grafo_default(semilla=None):
    """Grafo del ejercicio: B1->T1,T2  y  B2->T2,T3 (T2 compartido)."""
    t1 = Tinaco("T1", 1000, consumo=8.0)
    t2 = Tinaco("T2", 1000, consumo=8.0)
    t3 = Tinaco("T3", 1000, consumo=8.0)
    b1 = Bomba("B1", 50, [t1, t2])
    b2 = Bomba("B2", 40, [t2, t3])
    return Grafo([b1, b2], [t1, t2, t3], semilla=semilla)
