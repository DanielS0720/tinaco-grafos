import os
import sys
import time

from simulacion import ENCENDIDA, REPOSO, FALLO

# Códigos ANSI de color para el LED de cada bomba.
_COLOR_LED = {
    ENCENDIDA: "\033[92m",  # verde
    REPOSO: "\033[93m",     # amarillo
    FALLO: "\033[91m",      # rojo
}
_RESET = "\033[0m"


def barra(porcentaje, ancho=20):
    """Barra de progreso ASCII: '[####......]'."""
    llenos = int(round(porcentaje * ancho))
    llenos = max(0, min(ancho, llenos))
    return "[" + "#" * llenos + "." * (ancho - llenos) + "]"


def _led(estado):
    """Símbolo del LED coloreado (ANSI) según el estado de la bomba."""
    color = _COLOR_LED.get(estado, "")
    return f"{color}●{_RESET}"


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
        destinos = ", ".join(t.nombre for t in b.destinos)
        lineas.append(
            f"{b.nombre} {_led(b.estado)} {b.estado.upper():9} "
            f"caudal {b.caudal:.0f} L/s -> {destinos}"
        )
    return "\n".join(lineas)


def _limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def _preparar_consola():
    """Configura la consola para UTF-8 y colores ANSI (necesario en Windows)."""
    if os.name == "nt":
        os.system("")  # habilita el procesamiento de secuencias ANSI en Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def correr(grafo, dt=1.0, intervalo=0.5):
    """Anima la simulación en la terminal en loop infinito (Ctrl+C para salir)."""
    _preparar_consola()
    try:
        while True:
            _limpiar()
            print(render(grafo))
            print("\n(Ctrl+C para salir)")
            time.sleep(intervalo)
            grafo.paso(dt)
    except KeyboardInterrupt:
        print("\nSimulación detenida.")
