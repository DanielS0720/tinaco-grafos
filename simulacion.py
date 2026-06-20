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
