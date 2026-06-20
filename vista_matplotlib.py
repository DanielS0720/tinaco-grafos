from simulacion import ENCENDIDA, REPOSO, FALLO

_FALTAN_DEPS = (
    "Faltan dependencias para la vista gráfica. Instálalas con:\n"
    "    pip install matplotlib networkx"
)

# Color del LED (y del nodo) de la bomba según su estado.
_COLOR_LED = {
    ENCENDIDA: "limegreen",
    REPOSO: "gold",
    FALLO: "red",
}


def _color_led(estado):
    """Color del LED de la bomba según su estado."""
    return _COLOR_LED.get(estado, "gray")


def construir_red(grafo):
    """Construye un DiGraph de networkx con los nodos y aristas del grafo."""
    import networkx as nx

    red = nx.DiGraph()
    for b in grafo.bombas:
        red.add_node(b.nombre, tipo="bomba")
    for t in grafo.tinacos:
        red.add_node(t.nombre, tipo="tinaco")
    for b in grafo.bombas:
        for t in b.destinos:
            red.add_edge(b.nombre, t.nombre)
    return red


def _posiciones(grafo):
    """Coloca bombas a la izquierda y tinacos a la derecha, repartidos en Y."""
    posiciones = {}
    for i, b in enumerate(grafo.bombas):
        y = 1 - (i + 1) / (len(grafo.bombas) + 1)
        posiciones[b.nombre] = (0.0, y)
    for i, t in enumerate(grafo.tinacos):
        y = 1 - (i + 1) / (len(grafo.tinacos) + 1)
        posiciones[t.nombre] = (1.0, y)
    return posiciones


def correr(grafo, dt=1.0, intervalo_ms=200):
    """Anima la simulación en una ventana de matplotlib (hasta cerrar la ventana)."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from matplotlib.lines import Line2D
        from matplotlib.animation import FuncAnimation
        import networkx as nx
    except ImportError as excepcion:  # pragma: no cover
        raise SystemExit(_FALTAN_DEPS) from excepcion

    red = construir_red(grafo)
    posiciones = _posiciones(grafo)
    figura, eje = plt.subplots(figsize=(8, 5))

    leyenda = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="limegreen",
               markersize=12, label="Encendida"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gold",
               markersize=12, label="Reposo"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="red",
               markersize=12, label="Fallo"),
    ]

    def dibujar(_cuadro):
        eje.clear()
        eje.set_title(f"Llenado de tinacos — t = {grafo.tiempo:.0f} s")
        eje.axis("off")
        eje.set_xlim(-0.35, 1.2)

        colores, etiquetas = [], {}
        for nodo in red.nodes:
            tipo = red.nodes[nodo]["tipo"]
            if tipo == "tinaco":
                t = next(x for x in grafo.tinacos if x.nombre == nodo)
                colores.append(cm.Blues(0.2 + 0.8 * t.porcentaje))
                etiquetas[nodo] = f"{nodo}\n{t.porcentaje * 100:.0f}%"
            else:
                b = next(x for x in grafo.bombas if x.nombre == nodo)
                colores.append(_color_led(b.estado))
                etiquetas[nodo] = f"{nodo}\n{b.estado.upper()}"

        nx.draw_networkx_edges(red, posiciones, ax=eje, arrows=True,
                               arrowstyle="-|>", min_target_margin=20)
        nx.draw_networkx_nodes(red, posiciones, ax=eje, node_size=3000,
                               node_color=colores, edgecolors="black")
        nx.draw_networkx_labels(red, posiciones, labels=etiquetas, ax=eje,
                                font_size=9)

        # LED de cada bomba, a la izquierda de su nodo.
        for bomba in grafo.bombas:
            x, y = posiciones[bomba.nombre]
            eje.scatter([x - 0.15], [y], s=300, color=_color_led(bomba.estado),
                        edgecolors="black", zorder=3)

        eje.legend(handles=leyenda, loc="lower center", ncol=3,
                   title="LED de la bomba")

        grafo.paso(dt)

    _animacion = FuncAnimation(figura, dibujar, interval=intervalo_ms,
                               cache_frame_data=False)
    plt.show()
