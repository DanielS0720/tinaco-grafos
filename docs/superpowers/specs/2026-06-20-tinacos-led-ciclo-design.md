# LED de bombas y ciclo de llenado/vaciado continuo

Fecha: 2026-06-20

## Objetivo

Extender la simulación de tinacos para que: (1) cada bomba tenga un **LED** que
indique su estado (encendida, en reposo o en fallo); (2) la simulación corra en
**loop infinito** hasta que se cierre la ejecución; (3) los tinacos se **vacíen**
por consumo y se **vuelvan a llenar**, en ciclo perpetuo. Ambas vistas (terminal
y matplotlib) reflejan estos cambios.

Parte del repo existente (`simulacion.py`, `vista_terminal.py`,
`vista_matplotlib.py`, `main.py`). Mantiene la regla del proyecto: variables,
funciones y comentarios en español.

## Máquina de estados de la bomba

Cada `Bomba` tiene un atributo `estado` con tres valores (constantes de módulo):

- `ENCENDIDA` ("encendida") — LED **verde**: la bomba está bombeando agua.
- `REPOSO` ("reposo") — LED **amarillo**: bomba sana pero inactiva.
- `FALLO` ("fallo") — LED **rojo**: bomba averiada; no bombea.

Estado inicial: `REPOSO` (la histéresis la enciende en el primer paso si hace
falta).

### Histéresis (arranque/paro)

Evita que la bomba prenda y apague continuamente:

- `REPOSO → ENCENDIDA`: si **algún** destino baja del umbral de arranque
  (`umbral_arranque`, default 0.30 = 30%).
- `ENCENDIDA → REPOSO`: cuando **todos** los destinos están llenos.
- Entre 30% y 100% el estado se mantiene (banda de histéresis).

### Fallo aleatorio y autorrecuperación

- Cada paso, una bomba **sana** (ENCENDIDA o REPOSO) tiene probabilidad
  `prob_falla` (default 0.005 por paso) de pasar a `FALLO`.
- Al fallar, arranca un temporizador `tiempo_falla_restante = duracion_falla`
  (default 5.0 s). Mientras está en FALLO no bombea y descuenta `dt` cada paso.
- Cuando el temporizador llega a 0, vuelve a `REPOSO`; la histéresis decide en
  ese mismo paso si debe encenderse.
- La aleatoriedad usa un `random.Random(semilla)` inyectado en el `Grafo`, para
  que los tests sean deterministas. Con `prob_falla=0` el fallo se desactiva.

### Método `Bomba.actualizar_estado(dt, prob_falla, duracion_falla, umbral_arranque, aleatorio)`

Orden de evaluación en cada paso:

1. Si está en `FALLO`: descontar `dt` del temporizador. Si sigue > 0, termina
   (sigue averiada). Si llegó a 0, pasar a `REPOSO` y continuar.
2. Si está sana: con probabilidad `prob_falla` pasar a `FALLO`
   (`tiempo_falla_restante = duracion_falla`) y terminar.
3. Histéresis: aplicar las transiciones REPOSO↔ENCENDIDA descritas arriba.

`Bomba.activa` se redefine como propiedad: `estado == ENCENDIDA`.

## Consumo y ciclo de vaciado

- `Tinaco` gana el atributo `consumo` (L/s, default 0.0; en el grafo por defecto
  = 8.0) y el método `consumir(litros)` que baja el nivel sin pasar de 0:
  `nivel = max(0, nivel - litros)`.
- Con caudal de bomba (B1=50, B2=40) mayor que el consumo, un tinaco alimentado
  sube hasta llenarse; en reposo, el consumo lo vacía hasta cruzar el 30% y la
  bomba reenciende. Ciclo perpetuo.

## `Grafo`

Constructor: `Grafo(bombas, tinacos, prob_falla=0.005, duracion_falla=5.0,
umbral_arranque=0.30, semilla=None)`. Guarda esos parámetros y crea
`self.aleatorio = random.Random(semilla)`.

`paso(dt)` (reescrito, valida `dt > 0`):

1. Para cada bomba: `bomba.actualizar_estado(dt, self.prob_falla,
   self.duracion_falla, self.umbral_arranque, self.aleatorio)`.
2. Calcular aportes: por cada bomba con `estado == ENCENDIDA`, repartir
   `caudal * dt` en partes iguales entre sus `destinos_no_llenos()`; acumular por
   tinaco (el compartido suma los aportes de varias bombas).
3. Por cada tinaco: aplicar su aporte (`agregar`) y luego restar el consumo
   (`consumir(tinaco.consumo * dt)`).
4. `self.tiempo += dt`.

La propiedad `terminado` se conserva (todos llenos) por compatibilidad, pero ya
no controla el fin del loop.

## Vistas

### Terminal (`vista_terminal.py`)

- `render(grafo)` añade, por bomba, un LED `●` coloreado con códigos ANSI
  (verde/amarillo/rojo) seguido de la palabra del estado en mayúsculas
  (`ENCENDIDA`/`REPOSO`/`FALLO`). El texto del estado debe estar siempre presente
  (los tests lo verifican); el color ANSI es decorativo.
- `correr(grafo, dt, intervalo)` corre en **loop infinito**; sale limpio al
  recibir `KeyboardInterrupt` (Ctrl+C), imprimiendo un mensaje de cierre.

### matplotlib (`vista_matplotlib.py`)

- Por cada bomba se dibuja un **LED**: un punto/círculo pequeño junto al nodo de
  la bomba, coloreado verde/amarillo/rojo según el estado. El nodo de la bomba
  también se colorea según el estado.
- Se añade una **leyenda** que explica los tres colores del LED.
- La animación ya **no se detiene** por `terminado`; corre hasta que se cierra la
  ventana. `construir_red` y `_posiciones` no cambian.

## `main.py`

- Añade el argumento opcional `--semilla` (int, default `None`) que se pasa a
  `crear_grafo_default` / `Grafo` para reproducir una corrida.
- `crear_grafo_default(semilla=None)` setea `consumo=8.0` en los tres tinacos y
  pasa la semilla al `Grafo`.

## Errores / casos límite

- `consumir(litros)` con litros negativos: rechazar con `ValueError`.
- `dt <= 0` en `paso`: `ValueError` (igual que hoy).
- Bomba en FALLO o REPOSO no aporta agua aunque tenga destinos sin llenar.
- Histéresis no toca una bomba en FALLO.

## Pruebas (pytest)

Tests nuevos / actualizados:

- `Tinaco.consumir` baja el nivel y se topa en 0; litros negativos → `ValueError`.
- Histéresis: bomba en REPOSO con un destino < 30% pasa a ENCENDIDA tras
  `actualizar_estado` (con `prob_falla=0`); bomba ENCENDIDA con todos los
  destinos llenos pasa a REPOSO.
- Fallo forzado (`prob_falla=1.0`): la bomba pasa a FALLO y no aporta agua en el
  paso; tras `duracion_falla` segundos vuelve a estado sano.
- Ciclo: partiendo de un tinaco lleno con consumo > 0 y `prob_falla=0`, tras
  varios pasos el nivel baja por debajo del umbral y la bomba reenciende.
- Reparto y tinaco compartido (tests existentes) actualizados a `prob_falla=0`
  para ser deterministas; siguen verificando 25/25/45 L, etc.
- `render` incluye las palabras `ENCENDIDA`, `REPOSO` y `FALLO` según el estado.
- `construir_red` sin cambios (test existente sigue válido).

## Fuera de alcance (YAGNI)

- Control por teclado (forzar fallo manual): se descartó; el fallo es solo
  aleatorio.
- Configurar consumo/umbral/probabilidad por línea de comandos (más allá de
  `--semilla`): valores por defecto en código.
- Persistencia o registro histórico de la simulación.
