# Simulacion Tinacos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simular el llenado de 3 tinacos por 2 bombas modelado como grafo, siguiendo TDD estricto con todos los nombres en español.

**Architecture:** El módulo `simulacion.py` define tres clases (`Tinaco`, `Bomba`, `Grafo`) y una factory (`crear_grafo_default`). Los tinacos son nodos destino, las bombas son nodos fuente, y el grafo conecta fuentes con destinos repartiendo caudal proporcionalmente entre destinos no llenos.

**Tech Stack:** Python 3, pytest>=7.0, networkx>=2.6, matplotlib>=3.5

---

## File Map

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `conftest.py` | Crear (vacío) | Permite que pytest ponga la raíz en sys.path |
| `requirements.txt` | Crear | Dependencias del proyecto |
| `.gitignore` | Crear | Excluir cachés y entornos virtuales |
| `simulacion.py` | Crear | Clases Tinaco, Bomba, Grafo y factory crear_grafo_default |
| `tests/test_simulacion.py` | Crear | Todos los tests TDD (14 en total) |

---

### Task 1: Setup del proyecto

**Files:**
- Create: `conftest.py` (vacío)
- Create: `requirements.txt`
- Create: `.gitignore`

- [ ] **Step 1: Crear conftest.py vacío**

```bash
touch conftest.py
```

- [ ] **Step 2: Crear requirements.txt**

```
matplotlib>=3.5
networkx>=2.6
pytest>=7.0
```

- [ ] **Step 3: Crear .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
```

- [ ] **Step 4: Instalar dependencias (si pytest no está)**

```bash
python -m pip install pytest
```

- [ ] **Step 5: Commit**

```bash
git add conftest.py requirements.txt .gitignore
git commit -m "chore: setup proyecto tinacos (deps, gitignore, conftest)"
```

---

### Task 2: clase Tinaco

**Files:**
- Create: `tests/test_simulacion.py`
- Create: `simulacion.py`

- [ ] **Step 1: Crear tests/test_simulacion.py con tests de Tinaco**

```python
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

- [ ] **Step 2: Verificar que los tests fallan (ImportError esperado)**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: FAIL con `ImportError: cannot import name 'Tinaco' from 'simulacion'` o `ModuleNotFoundError`

- [ ] **Step 3: Crear simulacion.py con clase Tinaco**

```python
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

- [ ] **Step 4: Verificar que los 5 tests pasan**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add tests/test_simulacion.py simulacion.py
git commit -m "feat: clase Tinaco con nivel, porcentaje y tope de capacidad"
```

---

### Task 3: clase Bomba

**Files:**
- Modify: `tests/test_simulacion.py` (agregar al final)
- Modify: `simulacion.py` (agregar al final)

- [ ] **Step 1: Agregar tests de Bomba al final de tests/test_simulacion.py**

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

- [ ] **Step 2: Verificar que los nuevos tests fallan**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: 5 PASSED + 3 FAILED (ImportError o NameError en Bomba)

- [ ] **Step 3: Agregar clase Bomba al final de simulacion.py**

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

- [ ] **Step 4: Verificar que los 8 tests pasan**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: 8 PASSED

- [ ] **Step 5: Commit**

```bash
git add tests/test_simulacion.py simulacion.py
git commit -m "feat: clase Bomba con estado activa y destinos no llenos"
```

---

### Task 4: clase Grafo y paso(dt)

**Files:**
- Modify: `tests/test_simulacion.py` (agregar al final)
- Modify: `simulacion.py` (agregar al final)

- [ ] **Step 1: Agregar tests de Grafo al final de tests/test_simulacion.py**

```python
from simulacion import Grafo


def test_paso_reparte_caudal_entre_destinos_no_llenos():
    t1 = Tinaco("T1", 1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2])
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
    g = Grafo([b1, b2], [t1, t2, t3])
    g.paso(1.0)
    assert t2.nivel == 45
    assert t1.nivel == 25
    assert t3.nivel == 20


def test_paso_todo_el_caudal_al_unico_destino_no_lleno():
    t1 = Tinaco("T1", 1000, nivel=1000)
    t2 = Tinaco("T2", 1000)
    b1 = Bomba("B1", 50, [t1, t2])
    g = Grafo([b1], [t1, t2])
    g.paso(1.0)
    assert t2.nivel == 50


def test_terminado_cuando_todos_llenos():
    t1 = Tinaco("T1", 100)
    b1 = Bomba("B1", 1000, [t1])
    g = Grafo([b1], [t1])
    assert not g.terminado
    g.paso(1.0)
    assert t1.nivel == 100
    assert g.terminado


def test_paso_dt_invalido():
    t1 = Tinaco("T1", 1000)
    b1 = Bomba("B1", 50, [t1])
    g = Grafo([b1], [t1])
    with pytest.raises(ValueError):
        g.paso(0)
```

- [ ] **Step 2: Verificar que los nuevos tests fallan**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: 8 PASSED + 5 FAILED

- [ ] **Step 3: Agregar clase Grafo al final de simulacion.py**

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

- [ ] **Step 4: Verificar que los 13 tests pasan**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: 13 PASSED

- [ ] **Step 5: Commit**

```bash
git add tests/test_simulacion.py simulacion.py
git commit -m "feat: Grafo.paso reparte caudal y suma en tinaco compartido"
```

---

### Task 5: factory crear_grafo_default

**Files:**
- Modify: `tests/test_simulacion.py` (agregar al final)
- Modify: `simulacion.py` (agregar al final)

- [ ] **Step 1: Agregar test de factory al final de tests/test_simulacion.py**

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

    t2_b1 = next(t for t in b1.destinos if t.nombre == "T2")
    t2_b2 = next(t for t in b2.destinos if t.nombre == "T2")
    assert t2_b1 is t2_b2
```

- [ ] **Step 2: Verificar que el nuevo test falla**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: 13 PASSED + 1 FAILED

- [ ] **Step 3: Agregar factory crear_grafo_default al final de simulacion.py**

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

- [ ] **Step 4: Verificar que los 14 tests pasan**

Run: `python -m pytest tests/test_simulacion.py -v`
Expected: 14 PASSED

- [ ] **Step 5: Commit**

```bash
git add tests/test_simulacion.py simulacion.py
git commit -m "feat: factory crear_grafo_default con T2 compartido"
```
