import argparse

from simulacion import crear_grafo_default


def construir_parser():
    analizador = argparse.ArgumentParser(
        description="Simulación de llenado de tres tinacos con dos bombas (grafos)."
    )
    analizador.add_argument(
        "--vista",
        choices=["terminal", "matplotlib"],
        default="terminal",
        help="Cómo mostrar la simulación (default: terminal).",
    )
    analizador.add_argument(
        "--dt",
        type=float,
        default=1.0,
        help="Paso de tiempo en segundos (default: 1.0).",
    )
    return analizador


def main(argumentos=None):
    opciones = construir_parser().parse_args(argumentos)
    grafo = crear_grafo_default()
    if opciones.vista == "terminal":
        import vista_terminal

        vista_terminal.correr(grafo, dt=opciones.dt)
    else:
        import vista_matplotlib

        vista_matplotlib.correr(grafo, dt=opciones.dt)


if __name__ == "__main__":
    main()
