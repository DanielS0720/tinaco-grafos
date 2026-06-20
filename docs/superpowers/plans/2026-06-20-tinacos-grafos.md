# Simulación de tinacos con grafos — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simular el llenado de tres tinacos por dos bombas modelado como grafo, con vista en terminal (ASCII) y vista gráfica (matplotlib + networkx) sobre un núcleo de simulación común.

**Architecture:** Un núcleo puro (`simulacion.py`) con las clases `Tinaco`, `Bomba`, `Grafo` y el método `paso(dt)`. Dos vistas (`vista_terminal.py`, `vista_matplotlib.py`) que solo leen y dibujan el estado. `main.py` arma el grafo por defecto y elige la vista por línea de comandos.

**Tech Stack:** Python 3, pytest, matplotlib, networkx.

---

## File Structure

- `simulacion.py` — núcleo: `Tinaco`, `Bomba`, `Grafo`, `crear_grafo_default()`.
- `vista_terminal.py` — `barra()`, `render()`, `correr()`.
- `vista_matplotlib.py` — `construir_red()`, `correr()`.
- `main.py` — `construir_parser()`, `main()`.
- `conftest.py` — vacío; pone la raíz del repo en `sys.path` para pytest.
- `requirements.txt`, `.gitignore`, `README.md`.
- `tests/test_simulacion.py`, `tests/test_vista_terminal.py`, `tests/test_vista_matplotlib.py`, `tests/test_main.py`.

---

### Task 1: Setup del proyecto

**Files:**
- Create: `conftest.py`
- Create: `requirements.txt`
- Create: `.gitignore`

- [ ] **Step 1: Crear `conftest.py` vacío**

Archivo vacío en la raíz. Hace que pytest agregue la raíz del repo a `sys.path`, de modo que `from simulacion import ...` funcione desde `tests/`.

```python
```

(Contenido: archivo vacío.)

- [ ] **Step 2: Crear `requirements.txt`**

```
matplotlib>=3.5
networkx>=2.6
pytest>=7.0
```

- [ ] **Step 3: Crear `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
```

- [ ] **Step 4: Commit**

```bash
git add conftest.py requirements.txt .gitignore
git commit -m "chore: setup proyecto tinacos (deps, gitignore, conftest)"
```

---

### Task 2: Clase `Tinaco`

**Files:**
- Create: `simulacion.py`
- Test: `tests/test_simulacion.py`

- [ ] **Step 1: Escribir el test que falla**

```python
# tests/test_simulacion.py
import pytest
from simulacion import Tinaco


def test_tinaco_nuevo_esta_vacio():
    t = Tinaco("T1", 1000)
    assert t.nivel == 0.0
    assert t.porcentaje == 0.0
    assert not t.lleno


def test_tinaco_agregar_sube_nivel():
    t = Tinaco("T1", 1000)
    t.agregar(250)
    assert t.nivel == 250
    assert t.porcentaje == 0.25


def test_tinaco_no_desborda():
    t = Tinaco("T1", 1000)
    t.agregar(1500)
    assert t.nivel == 1000
    assert t.lleno
    assert t.porcentaje == 1.0


def test_tinaco_capacidad_invalida():
    with pytest.raises(ValueError):
        Tinaco("T1", 0)


def test_tinaco_agregar_negativo_invalido():
    t = Tinaco("T1", 1000)
    with pytest.raises(ValueError):
        t.agregar(-5)
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `pytest tests/test_simulacion.py -v`
Expected: FAIL con `ImportError: cannot import name 'Tinaco'`.

- [ ] **Step 3: Implementar `Tinaco`**

```python
# simulacion.py


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
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `pytest tests/test_simulacion.py -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add simulacion.py tests/test_simulacion.py
git commit -m "feat: clase Tinaco con nivel, porcentaje y tope de capacidad"
```

---

### Task 3: Clase `Bomba`

**Files:**
- Modify: `simulacion.py`
- Test: `tests/test_simulacion.py`

- [ ] **Step 1: Escribir el test que falla**

Agregar al final de `tests/test_simulacion.py`:

```python
from simulacion import Bomba


def test_bomba_activa_con_destino_no_lleno():
    t = Tinaco("T1", 1000)
    b = Bomba("B1", 50, [t])
    assert b.activa
    assert b.destinos_no_llenos() == [t]


def test_bomba_inactiva_cuando_destinos_llenos():
    t = Tinaco("T1", 1000)
    t.agregar(1000)
    b = Bomba("B1", 50, [t])
    assert not b.activa
    assert b.destinos_no_llenos() == []


def test_bomba_caudal_invalido():
    t = Tinaco("T1", 1000)
    with pytest.raises(ValueError):
        Bomba("B1", 0, [t])
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `pytest tests/test_simulacion.py -v`
Expected: FAIL con `ImportError: cannot import name 'Bomba'`.

- [ ] **Step 3: Implementar `Bomba`**

Agregar a `simulacion.py`:

```python
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
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `pytest tests/test_simulacion.py -v`
Expected: PASS (8 tests).

- [ ] **Step 5: Commit**

```bash
git add simulacion.py tests/test_simulacion.py
git commit -m "feat: clase Bomba con estado activa y destinos no llenos"
```

---

### Task 4: Clase `Grafo` y `paso(dt)`

**Files:**
- Modify: `simulacion.py`
- Test: `tests/test_simulacion.py`

- [ ] **Step 1: Escribir el test que falla**

Agregar al final de `tests/test_simulacion.py`:

```python
from simulacion import Grafo


def test_paso_reparte_caudal_entre_destinos_no_llenos():
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2])
    g.paso(1.0)
    # 50 L/s repartidos entre 2 destinos = 25 L cada uno
    assert t1.nivel == 25
    assert t2.nivel == 25
    assert g.tiempo == 1.0


def test_paso_tinaco_compartido_recibe_de_dos_bombas():
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    t3 = Tinaco("T3", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    b2 = Bomba("B2", 40, [t2, t3])
    g = Grafo([b1, b2], [t1, t2, t3])
    g.paso(1.0)
    # T2 recibe 25 (de B1) + 20 (de B2) = 45
    assert t2.nivel == 45
    assert t1.nivel == 25
    assert t3.nivel == 20


def test_paso_todo_el_caudal_al_unico_destino_no_lleno():
    t1 = Tinaco("T1", 1000, nivel=1000)  # ya lleno
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2])
    g.paso(1.0)
    # todo el caudal va a T2
    assert t2.nivel == 50


def test_terminado_cuando_todos_llenos():
    t1 = Tinaco("T1", 100)
    b1 = Bomba("B1", 1000, [t1])
    g = Grafo([b1], [t1])
    assert not g.terminado
    g.paso(1.0)  # 1000 L > 100, se topa
    assert t1.nivel == 100
    assert g.terminado


def test_paso_dt_invalido():
    t1 = Tinaco("T1", 1000)
    b1 = Bomba("B1", 50, [t1])
    g = Grafo([b1], [t1])
    with pytest.raises(ValueError):
        g.paso(0)
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `pytest tests/test_simulacion.py -v`
Expected: FAIL con `ImportError: cannot import name 'Grafo'`.

- [ ] **Step 3: Implementar `Grafo`**

Agregar a `simulacion.py`:

```python
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
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `pytest tests/test_simulacion.py -v`
Expected: PASS (13 tests).

- [ ] **Step 5: Commit**

```bash
git add simulacion.py tests/test_simulacion.py
git commit -m "feat: Grafo.paso reparte caudal y suma en tinaco compartido"
```

---

### Task 5: Factory `crear_grafo_default`

**Files:**
- Modify: `simulacion.py`
- Test: `tests/test_simulacion.py`

- [ ] **Step 1: Escribir el test que falla**

Agregar al final de `tests/test_simulacion.py`:

```python
from simulacion import crear_grafo_default


def test_grafo_default_topologia():
    g = crear_grafo_default()
    nombres_tinacos = sorted(t.nombre for t in g.tinacos)
    nombres_bombas = sorted(b.nombre for b in g.bombas)
    assert nombres_tinacos == ["T1", "T2", "T3"]
    assert nombres_bombas == ["B1", "B2"]

    b1 = next(b for b in g.bombas if b.nombre == "B1")
    b2 = next(b for b in g.bombas if b.nombre == "B2")
    assert sorted(t.nombre for t in b1.destinos) == ["T1", "T2"]
    assert sorted(t.nombre for t in b2.destinos) == ["T2", "T3"]

    # T2 es el mismo objeto compartido por ambas bombas
    t2_b1 = next(t for t in b1.destinos if t.nombre == "T2")
    t2_b2 = next(t for t in b2.destinos if t.nombre == "T2")
    assert t2_b1 is t2_b2
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `pytest tests/test_simulacion.py -v`
Expected: FAIL con `ImportError: cannot import name 'crear_grafo_default'`.

- [ ] **Step 3: Implementar el factory**

Agregar a `simulacion.py`:

```python
def crear_grafo_default():
    """Grafo del ejercicio: B1->T1,T2  y  B2->T2,T3 (T2 compartido)."""
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    t3 = Tinaco("T3", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    b2 = Bomba("B2", 40, [t2, t3])
    return Grafo([b1, b2], [t1, t2, t3])
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `pytest tests/test_simulacion.py -v`
Expected: PASS (14 tests).

- [ ] **Step 5: Commit**

```bash
git add simulacion.py tests/test_simulacion.py
git commit -m "feat: factory crear_grafo_default con T2 compartido"
```

---

### Task 6: Vista terminal

**Files:**
- Create: `vista_terminal.py`
- Test: `tests/test_vista_terminal.py`

- [ ] **Step 1: Escribir el test que falla**

```python
# tests/test_vista_terminal.py
from simulacion import crear_grafo_default
from vista_terminal import barra, render


def test_barra_vacia():
    assert barra(0.0, ancho=10) == "[..........]"


def test_barra_llena():
    assert barra(1.0, ancho=10) == "[##########]"


def test_barra_mitad():
    assert barra(0.5, ancho=10) == "[#####.....]"


def test_render_incluye_tinacos_bombas_y_tiempo():
    g = crear_grafo_default()
    salida = render(g)
    assert "T1" in salida
    assert "T2" in salida
    assert "T3" in salida
    assert "B1" in salida
    assert "B2" in salida
    assert "Tiempo" in salida


def test_render_muestra_bomba_off_cuando_inactiva():
    g = crear_grafo_default()
    for t in g.tinacos:
        t.agregar(t.capacidad)  # llenar todo
    salida = render(g)
    assert "OFF" in salida
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `pytest tests/test_vista_terminal.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'vista_terminal'`.

- [ ] **Step 3: Implementar `vista_terminal.py`**

```python
# vista_terminal.py
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
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `pytest tests/test_vista_terminal.py -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add vista_terminal.py tests/test_vista_terminal.py
git commit -m "feat: vista terminal con barras ASCII y estado de bombas"
```

---

### Task 7: Vista matplotlib

**Files:**
- Create: `vista_matplotlib.py`
- Test: `tests/test_vista_matplotlib.py`

- [ ] **Step 1: Escribir el test que falla**

```python
# tests/test_vista_matplotlib.py
import pytest

pytest.importorskip("networkx")

from simulacion import crear_grafo_default
from vista_matplotlib import construir_red


def test_construir_red_nodos_y_aristas():
    g = crear_grafo_default()
    red = construir_red(g)
    assert set(red.nodes) == {"B1", "B2", "T1", "T2", "T3"}
    assert set(red.edges) == {
        ("B1", "T1"),
        ("B1", "T2"),
        ("B2", "T2"),
        ("B2", "T3"),
    }


def test_construir_red_marca_tipo_de_nodo():
    g = crear_grafo_default()
    red = construir_red(g)
    assert red.nodes["B1"]["tipo"] == "bomba"
    assert red.nodes["T1"]["tipo"] == "tinaco"
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `pytest tests/test_vista_matplotlib.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'vista_matplotlib'` (o skip si networkx no está instalado — instálalo con `pip install networkx`).

- [ ] **Step 3: Implementar `vista_matplotlib.py`**

```python
# vista_matplotlib.py

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
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `pytest tests/test_vista_matplotlib.py -v`
Expected: PASS (2 tests). (`correr()` no se testea porque abre una ventana; se valida a mano en Task 9.)

- [ ] **Step 5: Commit**

```bash
git add vista_matplotlib.py tests/test_vista_matplotlib.py
git commit -m "feat: vista matplotlib con networkx y animacion del llenado"
```

---

### Task 8: Entrada `main.py`

**Files:**
- Create: `main.py`
- Test: `tests/test_main.py`

- [ ] **Step 1: Escribir el test que falla**

```python
# tests/test_main.py
from main import construir_parser


def test_parser_valores_por_defecto():
    args = construir_parser().parse_args([])
    assert args.vista == "terminal"
    assert args.dt == 1.0


def test_parser_elige_matplotlib():
    args = construir_parser().parse_args(["--vista", "matplotlib"])
    assert args.vista == "matplotlib"


def test_parser_dt_personalizado():
    args = construir_parser().parse_args(["--dt", "2.5"])
    assert args.dt == 2.5


def test_parser_vista_invalida():
    import pytest
    with pytest.raises(SystemExit):
        construir_parser().parse_args(["--vista", "web"])
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `pytest tests/test_main.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'main'`.

- [ ] **Step 3: Implementar `main.py`**

```python
# main.py
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
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `pytest tests/test_main.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Correr la suite completa**

Run: `pytest -v`
Expected: PASS (todos: 14 + 5 + 2 + 4 = 25 tests).

- [ ] **Step 6: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: main.py con CLI para elegir vista terminal o matplotlib"
```

---

### Task 9: README y verificación manual

**Files:**
- Create: `README.md`

- [ ] **Step 1: Escribir `README.md`**

````markdown
# Simulación de tinacos con grafos

Simula el llenado de tres tinacos por dos bombas, modelado como grafo.
La bomba B1 alimenta T1 y T2; la bomba B2 alimenta T2 y T3 (T2 es compartido).

## Instalar

```bash
pip install -r requirements.txt
```

## Correr

Vista en terminal (sin dependencias gráficas):

```bash
python main.py --vista terminal
```

Vista gráfica con networkx + matplotlib:

```bash
python main.py --vista matplotlib
```

Opcional: `--dt 2.0` cambia el paso de tiempo en segundos.

## Pruebas

```bash
pytest -v
```
````

- [ ] **Step 2: Verificación manual de la vista terminal**

Run: `python main.py --vista terminal`
Expected: las barras de T1, T2, T3 suben hasta 100%; B1 y B2 pasan de ON a OFF; termina con "¡Todos los tinacos están llenos!".

- [ ] **Step 3: Verificación manual de la vista matplotlib**

Run: `python main.py --vista matplotlib`
Expected: ventana con el grafo; los círculos de los tinacos se llenan de azul y muestran el %; los cuadros de las bombas pasan de verde (ON) a gris (OFF).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: README con instrucciones de uso y pruebas"
```

---

## Notas de verificación

- T2 se llena más rápido (recibe de B1 y B2): con defaults, T2 sube 45 L/s mientras T1 sube 25 L/s y T3 sube 20 L/s.
- Cuando T2 se llena, B1 manda todo su caudal a T1 y B2 todo a T3.
- B1 se apaga al llenar T1 y T2; B2 al llenar T2 y T3.
