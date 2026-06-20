_FALTAN_DEPS = (
    "Faltan dependencias para la vista gráfica. Instálalas con:\n"
    "    pip install matplotlib networkx"
)


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
    pos = {}
    for i, b in enumerate(grafo.bombas):
        y = 1 - (i + 1) / (len(grafo.bombas) + 1)
        pos[b.nombre] = (0.0, y)
    for i, t in enumerate(grafo.tinacos):
        y = 1 - (i + 1) / (len(grafo.tinacos) + 1)
        pos[t.nombre] = (1.0, y)
    return pos


def correr(grafo, dt=1.0, intervalo_ms=200, max_pasos=10000):
    """Anima la simulación en una ventana de matplotlib."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from matplotlib.animation import FuncAnimation
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(_FALTAN_DEPS) from exc

    red = construir_red(grafo)
    pos = _posiciones(grafo)
    fig, ax = plt.subplots(figsize=(8, 5))

    def dibujar(_frame):
        ax.clear()
        ax.set_title(f"Llenado de tinacos — t = {grafo.tiempo:.0f} s")
        ax.axis("off")

        colores, etiquetas, formas = [], {}, []
        for nodo in red.nodes:
            tipo = red.nodes[nodo]["tipo"]
            if tipo == "tinaco":
                t = next(x for x in grafo.tinacos if x.nombre == nodo)
                colores.append(cm.Blues(0.2 + 0.8 * t.porcentaje))
                etiquetas[nodo] = f"{nodo}\n{t.porcentaje * 100:.0f}%"
                formas.append("o")
            else:
                b = next(x for x in grafo.bombas if x.nombre == nodo)
                colores.append("tab:green" if b.activa else "tab:gray")
                etiquetas[nodo] = f"{nodo}\n{'ON' if b.activa else 'OFF'}"
                formas.append("s")

        nx.draw_networkx_edges(red, pos, ax=ax, arrows=True,
                               arrowstyle="-|>", min_target_margin=20)
        nx.draw_networkx_nodes(red, pos, ax=ax, node_size=3000,
                               node_color=colores, edgecolors="black")
        nx.draw_networkx_labels(red, pos, labels=etiquetas, ax=ax,
                                font_size=9)

        if not grafo.terminado and dibujar.pasos < max_pasos:
            grafo.paso(dt)
            dibujar.pasos += 1

    dibujar.pasos = 0
    _anim = FuncAnimation(fig, dibujar, interval=intervalo_ms,
                          cache_frame_data=False)
    plt.show()
