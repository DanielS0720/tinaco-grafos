class Tinaco:
    """Nodo destino del grafo: un tinaco con capacidad y nivel en litros."""

    def __init__(self, nombre, capacidad, nivel=0.0):
        if capacidad <= 0:
            raise ValueError("la capacidad debe ser positiva")
        self.nombre = nombre
        self.capacidad = float(capacidad)
        self.nivel = float(nivel)

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


class Bomba:
    """Nodo fuente del grafo: bombea agua a una lista de tinacos destino."""

    def __init__(self, nombre, caudal, destinos):
        if caudal <= 0:
            raise ValueError("el caudal debe ser positivo")
        self.nombre = nombre
        self.caudal = float(caudal)
        self.destinos = list(destinos)

    def destinos_no_llenos(self):
        return [t for t in self.destinos if not t.lleno]

    @property
    def activa(self):
        return len(self.destinos_no_llenos()) > 0


class Grafo:
    """Grafo de la simulación: bombas (fuentes) y tinacos (destinos)."""

    def __init__(self, bombas, tinacos):
        self.bombas = list(bombas)
        self.tinacos = list(tinacos)
        self.tiempo = 0.0

    @property
    def terminado(self):
        return all(t.lleno for t in self.tinacos)

    def paso(self, dt):
        if dt <= 0:
            raise ValueError("dt debe ser positivo")
        # Acumular los aportes antes de aplicarlos, para que un tinaco
        # compartido (alimentado por varias bombas) sume todos los caudales.
        aportes = {id(t): 0.0 for t in self.tinacos}
        for bomba in self.bombas:
            objetivos = bomba.destinos_no_llenos()
            if not objetivos:
                continue
            litros = bomba.caudal * dt / len(objetivos)
            for t in objetivos:
                aportes[id(t)] += litros
        for t in self.tinacos:
            t.agregar(aportes[id(t)])
        self.tiempo += dt


def crear_grafo_default():
    """Grafo del ejercicio: B1->T1,T2  y  B2->T2,T3 (T2 compartido)."""
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    t3 = Tinaco("T3", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    b2 = Bomba("B2", 40, [t2, t3])
    return Grafo([b1, b2], [t1, t2, t3])
