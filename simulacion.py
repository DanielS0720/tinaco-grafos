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
