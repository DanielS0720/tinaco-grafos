import os
import time


def barra(porcentaje, ancho=20):
    """Barra de progreso ASCII: '[####......]'."""
    llenos = int(round(porcentaje * ancho))
    llenos = max(0, min(ancho, llenos))
    return "[" + "#" * llenos + "." * (ancho - llenos) + "]"


def render(grafo):
    """Devuelve el estado del grafo como texto (no imprime)."""
    lineas = [f"Tiempo: {grafo.tiempo:.0f} s", ""]
    for t in grafo.tinacos:
        lineas.append(
            f"{t.nombre} {barra(t.porcentaje)} {t.porcentaje * 100:5.1f}%  "
            f"{t.nivel:7.1f}/{t.capacidad:.0f} L"
        )
    lineas.append("")
    for b in grafo.bombas:
        estado = "ON " if b.activa else "OFF"
        destinos = ", ".join(t.nombre for t in b.destinos)
        lineas.append(
            f"{b.nombre} [{estado}] caudal {b.caudal:.0f} L/s -> {destinos}"
        )
    return "\n".join(lineas)


def _limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def correr(grafo, dt=1.0, intervalo=0.2, max_pasos=10000):
    """Anima la simulación en la terminal hasta llenar todos los tinacos."""
    pasos = 0
    while not grafo.terminado and pasos < max_pasos:
        _limpiar()
        print(render(grafo))
        time.sleep(intervalo)
        grafo.paso(dt)
        pasos += 1
    _limpiar()
    print(render(grafo))
    print("\n¡Todos los tinacos están llenos!")
