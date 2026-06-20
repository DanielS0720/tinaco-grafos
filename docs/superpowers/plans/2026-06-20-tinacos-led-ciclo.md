# LED de bombas y ciclo continuo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir LED de estado (encendida/reposo/fallo) por bomba, fallo aleatorio con autorrecuperación, consumo que vacía los tinacos, y loop infinito, en ambas vistas.

**Architecture:** Se extiende el núcleo `simulacion.py` con una máquina de estados en `Bomba` y consumo en `Tinaco`; `Grafo.paso` actualiza estados, aporta agua de las bombas encendidas y resta consumo. Las vistas dibujan el LED y corren sin fin.

**Tech Stack:** Python 3, pytest, matplotlib, networkx, `random` (stdlib).

**Regla del proyecto:** todas las variables, funciones y comentarios en ESPAÑOL.

---

## File Structure

- `simulacion.py` — constantes de estado + `Tinaco` (consumo), `Bomba` (estado/fallo), `Grafo` (paso reescrito), `crear_grafo_default` (consumo, semilla).
- `vista_terminal.py` — LED ANSI + estado en `render`, loop infinito en `correr`.
- `vista_matplotlib.py` — LED de color + leyenda, animación sin fin.
- `main.py` — argumento `--semilla`.
- `README.md` — instrucciones actualizadas.
- `tests/test_simulacion.py`, `tests/test_vista_terminal.py`, `tests/test_vista_matplotlib.py`, `tests/test_main.py` — actualizados.

Comandos: shell Git Bash. Pytest: `cd "C:/Users/suare/OneDrive/Desktop/Github/tinaco-grafos" && python -m pytest ...`.

---

### Task 1: Consumo en `Tinaco`

**Files:**
- Modify: `simulacion.py` (clase `Tinaco`)
- Test: `tests/test_simulacion.py`

- [ ] **Step 1: Escribir los tests que fallan**

Agregar al final de `tests/test_simulacion.py`:

```python
def test_tinaco_consumo_default_cero():
    t = Tinaco("T1", 1000)
    assert t.consumo == 0.0


def test_tinaco_consumir_baja_nivel():
    t = Tinaco("T1", 1000, nivel=500)
    t.consumir(200)
    assert t.nivel == 300


def test_tinaco_consumir_no_baja_de_cero():
    t = Tinaco("T1", 1000, nivel=100)
    t.consumir(250)
    assert t.nivel == 0


def test_tinaco_consumir_negativo_invalido():
    t = Tinaco("T1", 1000, nivel=100)
    with pytest.raises(ValueError):
        t.consumir(-5)
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: FAIL con `AttributeError: 'Tinaco' object has no attribute 'consumo'` (y `consumir`).

- [ ] **Step 3: Modificar `Tinaco`**

Reemplazar el `__init__` y agregar `consumir`. En `simulacion.py`, la clase `Tinaco` queda así:

```python
class Tinaco:
    """Nodo destino del grafo: un tinaco con capacidad, nivel y consumo (L/s)."""

    def __init__(self, nombre, capacidad, nivel=0.0, consumo=0.0):
        if capacidad <= 0:
            raise ValueError("la capacidad debe ser positiva")
        if consumo < 0:
            raise ValueError("el consumo no puede ser negativo")
        self.nombre = nombre
        self.capacidad = float(capacidad)
        self.nivel = float(nivel)
        self.consumo = float(consumo)

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

    def consumir(self, litros):
        if litros < 0:
            raise ValueError("los litros a consumir no pueden ser negativos")
        self.nivel = max(0.0, self.nivel - litros)
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: PASS (18 tests: 14 previos + 4 nuevos).

- [ ] **Step 5: Commit**

```bash
git add simulacion.py tests/test_simulacion.py
git commit -m "feat: consumo y metodo consumir en Tinaco"
```

---

### Task 2: Máquina de estados en `Bomba`

**Files:**
- Modify: `simulacion.py` (constantes nuevas + clase `Bomba`)
- Test: `tests/test_simulacion.py`

- [ ] **Step 1: Reemplazar los tests viejos de `Bomba` y agregar los nuevos**

En `tests/test_simulacion.py`, BORRAR estas dos funciones completas:

```python
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
```

Y en su lugar agregar (junto al `import` de estados):

```python
import random as _random
from simulacion import ENCENDIDA, REPOSO, FALLO


def test_bomba_estado_inicial_reposo():
    t = Tinaco("T1", 1000)
    b = Bomba("B1", 50, [t])
    assert b.estado == REPOSO
    assert not b.activa


def test_actualizar_estado_arranque_por_histeresis():
    t = Tinaco("T1", 1000)  # vacío: 0% < 30%
    b = Bomba("B1", 50, [t])
    b.actualizar_estado(1.0, 0.0, 5.0, 0.30, _random.Random(0))
    assert b.estado == ENCENDIDA
    assert b.activa


def test_actualizar_estado_paro_por_histeresis():
    t = Tinaco("T1", 1000, nivel=1000)  # lleno
    b = Bomba("B1", 50, [t])
    b.estado = ENCENDIDA
    b.actualizar_estado(1.0, 0.0, 5.0, 0.30, _random.Random(0))
    assert b.estado == REPOSO


def test_actualizar_estado_fallo_forzado_y_recuperacion():
    t = Tinaco("T1", 1000)
    b = Bomba("B1", 50, [t])
    b.actualizar_estado(1.0, 1.0, 5.0, 0.30, _random.Random(0))  # prob 1.0 -> falla
    assert b.estado == FALLO
    assert b.tiempo_falla_restante == 5.0
    for _ in range(5):  # 5 segundos sin volver a fallar
        b.actualizar_estado(1.0, 0.0, 5.0, 0.30, _random.Random(0))
    assert b.estado != FALLO
    assert b.estado in (REPOSO, ENCENDIDA)
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: FAIL con `ImportError: cannot import name 'ENCENDIDA'`.

- [ ] **Step 3: Agregar constantes y reescribir `Bomba`**

En `simulacion.py`, agregar al inicio del archivo (antes de la clase `Tinaco`):

```python
# Estados posibles de una bomba (color del LED en las vistas).
ENCENDIDA = "encendida"  # LED verde: bombeando
REPOSO = "reposo"        # LED amarillo: sana pero inactiva
FALLO = "fallo"          # LED rojo: averiada
```

Y reemplazar la clase `Bomba` completa por:

```python
class Bomba:
    """Nodo fuente del grafo: bombea agua a sus tinacos destino.

    Tiene una máquina de estados (encendida/reposo/fallo) controlada por
    histéresis de nivel y por fallos aleatorios con autorrecuperación.
    """

    def __init__(self, nombre, caudal, destinos):
        if caudal <= 0:
            raise ValueError("el caudal debe ser positivo")
        self.nombre = nombre
        self.caudal = float(caudal)
        self.destinos = list(destinos)
        self.estado = REPOSO
        self.tiempo_falla_restante = 0.0

    def destinos_no_llenos(self):
        return [t for t in self.destinos if not t.lleno]

    @property
    def activa(self):
        return self.estado == ENCENDIDA

    def actualizar_estado(self, dt, prob_falla, duracion_falla,
                          umbral_arranque, aleatorio):
        # 1. Si está averiada, descontar el temporizador de recuperación.
        if self.estado == FALLO:
            self.tiempo_falla_restante -= dt
            if self.tiempo_falla_restante > 0:
                return
            self.tiempo_falla_restante = 0.0
            self.estado = REPOSO
        # 2. Una bomba sana puede averiarse al azar.
        if aleatorio.random() < prob_falla:
            self.estado = FALLO
            self.tiempo_falla_restante = duracion_falla
            return
        # 3. Histéresis de arranque/paro.
        if self.estado == REPOSO and any(
            t.porcentaje < umbral_arranque for t in self.destinos
        ):
            self.estado = ENCENDIDA
        elif self.estado == ENCENDIDA and all(t.lleno for t in self.destinos):
            self.estado = REPOSO
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: PASS (20 tests: 18 - 2 borrados + 4 nuevos).

- [ ] **Step 5: Commit**

```bash
git add simulacion.py tests/test_simulacion.py
git commit -m "feat: maquina de estados (LED) y fallo aleatorio en Bomba"
```

---

### Task 3: `Grafo.paso` con estados y consumo

**Files:**
- Modify: `simulacion.py` (import `random`, clase `Grafo`)
- Test: `tests/test_simulacion.py`

- [ ] **Step 1: Actualizar tests de `paso` y agregar los nuevos**

En `tests/test_simulacion.py`, reemplazar estas cuatro funciones por sus versiones con `prob_falla=0.0` (las que arman un `Grafo` y verifican niveles exactos):

```python
def test_paso_reparte_caudal_entre_destinos_no_llenos():
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2], prob_falla=0.0)
    g.paso(1.0)
    assert t1.nivel == 25
    assert t2.nivel == 25
    assert g.tiempo == 1.0


def test_paso_tinaco_compartido_recibe_de_dos_bombas():
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    t3 = Tinaco("T3", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    b2 = Bomba("B2", 40, [t2, t3])
    g = Grafo([b1, b2], [t1, t2, t3], prob_falla=0.0)
    g.paso(1.0)
    assert t2.nivel == 45
    assert t1.nivel == 25
    assert t3.nivel == 20


def test_paso_todo_el_caudal_al_unico_destino_no_lleno():
    t1 = Tinaco("T1", 1000, nivel=1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2], prob_falla=0.0)
    g.paso(1.0)
    assert t2.nivel == 50


def test_terminado_cuando_todos_llenos():
    t1 = Tinaco("T1", 100)
    b1 = Bomba("B1", 1000, [t1])
    g = Grafo([b1], [t1], prob_falla=0.0)
    assert not g.terminado
    g.paso(1.0)
    assert t1.nivel == 100
    assert g.terminado
```

Y agregar al final del archivo:

```python
def test_paso_bomba_en_fallo_no_aporta():
    t = Tinaco("T1", 1000)
    b = Bomba("B1", 50, [t])
    b.estado = FALLO
    b.tiempo_falla_restante = 5.0
    g = Grafo([b], [t], prob_falla=0.0)
    g.paso(1.0)
    assert t.nivel == 0          # en fallo no aporta y no hay consumo
    assert b.estado == FALLO     # sigue averiada (5 - 1 = 4 s)


def test_paso_aplica_consumo_a_los_tinacos():
    t = Tinaco("T1", 1000, nivel=500, consumo=10.0)
    b = Bomba("B1", 50, [t])
    b.estado = REPOSO  # no aporta; solo se ve el consumo
    g = Grafo([b], [t], prob_falla=0.0, umbral_arranque=0.30)
    g.paso(1.0)
    # 50% sigue por encima del 30%, así que la bomba no arranca: solo consumo
    assert t.nivel == 490
    assert b.estado == REPOSO
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: FAIL — `Grafo.__init__()` no acepta `prob_falla` (`TypeError`).

- [ ] **Step 3: Reescribir `Grafo` y agregar `import random`**

En `simulacion.py`, agregar como PRIMERA línea del archivo (antes de las constantes de estado):

```python
import random
```

Reemplazar la clase `Grafo` completa por:

```python
class Grafo:
    """Grafo de la simulación: bombas (fuentes) y tinacos (destinos)."""

    def __init__(self, bombas, tinacos, prob_falla=0.005, duracion_falla=5.0,
                 umbral_arranque=0.30, semilla=None):
        self.bombas = list(bombas)
        self.tinacos = list(tinacos)
        self.tiempo = 0.0
        self.prob_falla = prob_falla
        self.duracion_falla = duracion_falla
        self.umbral_arranque = umbral_arranque
        self.aleatorio = random.Random(semilla)

    @property
    def terminado(self):
        return all(t.lleno for t in self.tinacos)

    def paso(self, dt):
        if dt <= 0:
            raise ValueError("dt debe ser positivo")
        # 1. Actualizar el estado (LED) de cada bomba.
        for bomba in self.bombas:
            bomba.actualizar_estado(dt, self.prob_falla, self.duracion_falla,
                                    self.umbral_arranque, self.aleatorio)
        # 2. Acumular los aportes de las bombas encendidas. El tinaco
        #    compartido suma los caudales de varias bombas.
        aportes = {id(t): 0.0 for t in self.tinacos}
        for bomba in self.bombas:
            if bomba.estado != ENCENDIDA:
                continue
            objetivos = bomba.destinos_no_llenos()
            if not objetivos:
                continue
            litros = bomba.caudal * dt / len(objetivos)
            for t in objetivos:
                aportes[id(t)] += litros
        # 3. Aplicar el aporte y luego el consumo de cada tinaco.
        for t in self.tinacos:
            t.agregar(aportes[id(t)])
            t.consumir(t.consumo * dt)
        self.tiempo += dt
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: PASS (22 tests).

- [ ] **Step 5: Commit**

```bash
git add simulacion.py tests/test_simulacion.py
git commit -m "feat: Grafo.paso usa estados de bomba y aplica consumo"
```

---

### Task 4: `crear_grafo_default` con consumo y semilla + test de ciclo

**Files:**
- Modify: `simulacion.py` (`crear_grafo_default`)
- Test: `tests/test_simulacion.py`

- [ ] **Step 1: Escribir los tests que fallan**

Agregar al final de `tests/test_simulacion.py`:

```python
def test_grafo_default_tinacos_con_consumo():
    g = crear_grafo_default()
    assert all(t.consumo == 8.0 for t in g.tinacos)


def test_ciclo_vaciado_y_reencendido():
    # Tinaco lleno + consumo, sin fallos: se vacía hasta <30% y la bomba reenciende.
    t = Tinaco("T1", 100, nivel=100, consumo=10.0)
    b = Bomba("B1", 50, [t])
    g = Grafo([b], [t], prob_falla=0.0, umbral_arranque=0.30)
    for _ in range(8):  # 100 -> 20 (la bomba sigue en reposo: 30% no es < 30%)
        g.paso(1.0)
    assert b.estado == REPOSO
    assert t.nivel == 20
    g.paso(1.0)  # 20% < 30% -> arranca
    assert b.estado == ENCENDIDA
    assert t.nivel == 60  # 20 + 50 (aporte) - 10 (consumo)
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: FAIL en `test_grafo_default_tinacos_con_consumo` (`assert ... 0.0 == 8.0`).

- [ ] **Step 3: Modificar `crear_grafo_default`**

En `simulacion.py`, reemplazar la función `crear_grafo_default` por:

```python
def crear_grafo_default(semilla=None):
    """Grafo del ejercicio: B1->T1,T2  y  B2->T2,T3 (T2 compartido)."""
    t1 = Tinaco("T1", 1000, consumo=8.0)
    t2 = Tinaco("T2", 1000, consumo=8.0)
    t3 = Tinaco("T3", 1000, consumo=8.0)
    b1 = Bomba("B1", 50, [t1, t2])
    b2 = Bomba("B2", 40, [t2, t3])
    return Grafo([b1, b2], [t1, t2, t3], semilla=semilla)
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: PASS (24 tests).

- [ ] **Step 5: Commit**

```bash
git add simulacion.py tests/test_simulacion.py
git commit -m "feat: crear_grafo_default con consumo y semilla reproducible"
```

---

### Task 5: Vista terminal con LED y loop infinito

**Files:**
- Modify: `vista_terminal.py`
- Test: `tests/test_vista_terminal.py`

- [ ] **Step 1: Reemplazar el test de estado y agregar el de fallo**

En `tests/test_vista_terminal.py`, reemplazar el `import` de arriba y la función `test_render_muestra_bomba_off_cuando_inactiva`.

Cambiar el import inicial por:

```python
from simulacion import crear_grafo_default, ENCENDIDA, REPOSO, FALLO
from vista_terminal import barra, render
```

Y reemplazar `test_render_muestra_bomba_off_cuando_inactiva` por:

```python
def test_render_muestra_estado_reposo():
    g = crear_grafo_default(semilla=0)
    for b in g.bombas:
        b.estado = REPOSO
    salida = render(g)
    assert "REPOSO" in salida


def test_render_muestra_estado_fallo():
    g = crear_grafo_default(semilla=0)
    g.bombas[0].estado = FALLO
    salida = render(g)
    assert "FALLO" in salida


def test_render_muestra_estado_encendida():
    g = crear_grafo_default(semilla=0)
    g.bombas[0].estado = ENCENDIDA
    salida = render(g)
    assert "ENCENDIDA" in salida
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `python -m pytest tests/test_vista_terminal.py -v`
Expected: FAIL — `render` aún muestra "ON"/"OFF", no "REPOSO"/"FALLO"/"ENCENDIDA".

- [ ] **Step 3: Modificar `vista_terminal.py`**

Reemplazar el archivo `vista_terminal.py` completo por:

```python
import os
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


def correr(grafo, dt=1.0, intervalo=0.5):
    """Anima la simulación en la terminal en loop infinito (Ctrl+C para salir)."""
    try:
        while True:
            _limpiar()
            print(render(grafo))
            print("\n(Ctrl+C para salir)")
            time.sleep(intervalo)
            grafo.paso(dt)
    except KeyboardInterrupt:
        print("\nSimulación detenida.")
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `python -m pytest tests/test_vista_terminal.py -v`
Expected: PASS (7 tests: barra x3, incluye x1, estados x3).

- [ ] **Step 5: Commit**

```bash
git add vista_terminal.py tests/test_vista_terminal.py
git commit -m "feat: vista terminal con LED de estado y loop infinito"
```

---

### Task 6: Vista matplotlib con LED y leyenda

**Files:**
- Modify: `vista_matplotlib.py`
- Test: `tests/test_vista_matplotlib.py`

- [ ] **Step 1: Escribir el test del helper de color**

Agregar al final de `tests/test_vista_matplotlib.py`:

```python
from vista_matplotlib import _color_led
from simulacion import ENCENDIDA, REPOSO, FALLO


def test_color_led_por_estado():
    assert _color_led(ENCENDIDA) == "limegreen"
    assert _color_led(REPOSO) == "gold"
    assert _color_led(FALLO) == "red"
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `python -m pytest tests/test_vista_matplotlib.py -v`
Expected: FAIL con `ImportError: cannot import name '_color_led'`.

- [ ] **Step 3: Reemplazar `vista_matplotlib.py`**

Reemplazar el archivo `vista_matplotlib.py` completo por:

```python
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
```

- [ ] **Step 4: Correr y verificar que pasa + smoke test**

Run: `python -m pytest tests/test_vista_matplotlib.py -v`
Expected: PASS (3 tests).

Smoke test (no abre ventana, valida la API de dibujo):

```bash
cd "C:/Users/suare/OneDrive/Desktop/Github/tinaco-grafos" && MPLBACKEND=Agg python -c "
import matplotlib; matplotlib.use('Agg')
from simulacion import crear_grafo_default, ENCENDIDA
import vista_matplotlib as vm
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.lines import Line2D
import networkx as nx
g = crear_grafo_default(semilla=0)
g.bombas[0].estado = ENCENDIDA
red = vm.construir_red(g); posiciones = vm._posiciones(g)
figura, eje = plt.subplots()
nx.draw_networkx_edges(red, posiciones, ax=eje, arrows=True, arrowstyle='-|>', min_target_margin=20)
nx.draw_networkx_nodes(red, posiciones, ax=eje, node_size=3000, node_color=[vm._color_led(b.estado) for b in g.bombas]+['tab:blue']*3, edgecolors='black')
for b in g.bombas:
    x,y = posiciones[b.nombre]; eje.scatter([x-0.15],[y], s=300, color=vm._color_led(b.estado))
eje.legend(handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor='limegreen',label='Encendida')])
print('SMOKE_OK')
"
```
Expected: imprime `SMOKE_OK`. Si la API falla por versión, ajustar el código a la API instalada y repetir.

- [ ] **Step 5: Commit**

```bash
git add vista_matplotlib.py tests/test_vista_matplotlib.py
git commit -m "feat: vista matplotlib con LED de estado, leyenda y animacion sin fin"
```

---

### Task 7: Argumento `--semilla` en `main.py`

**Files:**
- Modify: `main.py`
- Test: `tests/test_main.py`

- [ ] **Step 1: Escribir los tests que fallan**

Agregar al final de `tests/test_main.py`:

```python
def test_parser_semilla_default_none():
    args = construir_parser().parse_args([])
    assert args.semilla is None


def test_parser_semilla_personalizada():
    args = construir_parser().parse_args(["--semilla", "7"])
    assert args.semilla == 7
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `python -m pytest tests/test_main.py -v`
Expected: FAIL con `AttributeError: 'Namespace' object has no attribute 'semilla'`.

- [ ] **Step 3: Modificar `main.py`**

Reemplazar el archivo `main.py` completo por:

```python
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
    analizador.add_argument(
        "--semilla",
        type=int,
        default=None,
        help="Semilla aleatoria para reproducir la simulación (default: None).",
    )
    return analizador


def main(argumentos=None):
    opciones = construir_parser().parse_args(argumentos)
    grafo = crear_grafo_default(semilla=opciones.semilla)
    if opciones.vista == "terminal":
        import vista_terminal

        vista_terminal.correr(grafo, dt=opciones.dt)
    else:
        import vista_matplotlib

        vista_matplotlib.correr(grafo, dt=opciones.dt)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `python -m pytest -v`
Expected: PASS (suite completa: 24 + 7 + 3 + 6 = 40 tests).

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: argumento --semilla para reproducir la simulacion"
```

---

### Task 8: README y verificación manual

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Reemplazar `README.md`**

````markdown
# Simulación de tinacos con grafos

Simula el llenado de tres tinacos por dos bombas, modelado como grafo.
La bomba B1 alimenta T1 y T2; la bomba B2 alimenta T2 y T3 (T2 es compartido).

Cada bomba tiene un **LED** de estado:

- 🟢 **Encendida** — está bombeando agua.
- 🟡 **Reposo** — sana pero inactiva (sus tinacos por encima del 30%).
- 🔴 **Fallo** — averiada (fallo aleatorio); se recupera sola tras unos segundos.

Los tinacos consumen agua, así que se vacían y se vuelven a llenar en un ciclo
continuo. La simulación corre en loop hasta que la cierras.

## Instalar

```bash
pip install -r requirements.txt
```

## Correr

Vista en terminal (sin dependencias gráficas, Ctrl+C para salir):

```bash
python main.py --vista terminal
```

Vista gráfica con networkx + matplotlib (cierra la ventana para salir):

```bash
python main.py --vista matplotlib
```

Opciones: `--dt 2.0` cambia el paso de tiempo; `--semilla 7` hace la corrida
reproducible.

## Pruebas

```bash
pytest -v
```
````

- [ ] **Step 2: Verificación manual de la vista terminal**

Run: `python main.py --vista terminal --semilla 1`
Expected: las barras suben y bajan en ciclo; los LED de las bombas alternan entre ENCENDIDA/REPOSO y a veces FALLO; Ctrl+C imprime "Simulación detenida.".

- [ ] **Step 3: Verificación manual de la vista matplotlib**

Run: `python main.py --vista matplotlib --semilla 1`
Expected: ventana con el grafo; los tinacos suben/bajan de azul; el LED de cada bomba cambia de verde a amarillo a rojo; hay leyenda. Cerrar la ventana termina el programa.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: README con LED, ciclo continuo y opcion --semilla"
```

---

## Notas de verificación

- Sin fallos (`prob_falla=0`), una bomba en reposo deja que el consumo vacíe sus
  tinacos hasta < 30%, momento en que arranca (ENCENDIDA) y los rellena.
- El LED rojo (FALLO) dura `duracion_falla` segundos (default 5 s) y luego la
  bomba vuelve a reposo/encendida según el nivel.
- Con `--semilla` fija, la secuencia de fallos es reproducible.
