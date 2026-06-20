import argparse

from simulacion import crear_grafo_default


def construir_parser():
    parser = argparse.ArgumentParser(
        description="Simulación de llenado de tres tinacos con dos bombas (grafos)."
    )
    parser.add_argument(
        "--vista",
        choices=["terminal", "matplotlib"],
        default="terminal",
        help="Cómo mostrar la simulación (default: terminal).",
    )
    parser.add_argument(
        "--dt",
        type=float,
        default=1.0,
        help="Paso de tiempo en segundos (default: 1.0).",
    )
    return parser


def main(argv=None):
    args = construir_parser().parse_args(argv)
    grafo = crear_grafo_default()
    if args.vista == "terminal":
        import vista_terminal

        vista_terminal.correr(grafo, dt=args.dt)
    else:
        import vista_matplotlib

        vista_matplotlib.correr(grafo, dt=args.dt)


if __name__ == "__main__":
    main()
