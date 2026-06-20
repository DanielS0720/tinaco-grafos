# Simulación de llenado de tres tinacos con dos bombas (grafos)

Fecha: 2026-06-20

## Objetivo

Programa en Python que simula el llenado de **tres tinacos** mediante **dos
bombas**, modelado como un **grafo** y mostrado de forma **visual**. Dos vistas:
una en terminal (ASCII) y otra gráfica (matplotlib + networkx), ambas sobre el
mismo núcleo de simulación.

## Arquitectura

Núcleo de simulación puro (sin entrada/salida) separado de la presentación. Las
vistas leen el estado del núcleo y lo dibujan. Esto mantiene la lógica testeable
y evita duplicarla entre las dos vistas.

```
main.py                    # entrada: --vista terminal|matplotlib, arma grafo, corre el loop
simulacion.py              # núcleo: clases Tinaco, Bomba, Grafo; método paso(dt)
vista_terminal.py          # dibuja el estado en ASCII, refresca en vivo
vista_matplotlib.py        # networkx + FuncAnimation; nodos/aristas + barras de nivel
tests/test_simulacion.py   # pruebas del núcleo (pytest)
```

## Modelo de datos (grafo)

- **Tinaco** (nodo destino): `nombre`, `capacidad` (L), `nivel` (L).
  - `porcentaje` = nivel / capacidad.
  - `lleno` = nivel >= capacidad.
- **Bomba** (nodo fuente): `nombre`, `caudal` (L/s), `destinos` (lista de Tinaco).
  - `activa` = al menos un destino no lleno.
- **Grafo**: colección de bombas + tinacos. Las aristas son las relaciones
  bomba→tinaco implícitas en `destinos`.

### Topología fija

```
B1 -> T1
B1 -> T2 <- B2
B2 -> T3
```

T2 es compartido: recibe aporte de B1 y de B2.

## Lógica de simulación: `paso(dt)`

En cada paso de tiempo `dt` (segundos):

1. Por cada bomba **activa**, repartir su caudal en partes iguales entre sus
   destinos **no llenos**. Si una bomba tiene 2 destinos y ambos están sin
   llenar, cada uno recibe `caudal/2 * dt` litros; si solo uno está sin llenar,
   recibe `caudal * dt`.
2. Un tinaco compartido (T2) acumula los aportes de todas las bombas que lo
   alimentan en ese paso.
3. El nivel se topa en `capacidad` (nunca desborda). El exceso se descarta.
4. Una bomba se considera apagada cuando **todos** sus destinos están llenos.
5. La simulación termina cuando los tres tinacos están llenos.

### Parámetros por defecto

- Capacidad: 1000 L por tinaco.
- Caudal: B1 = 50 L/s, B2 = 40 L/s.
- dt = 1 s.

(Configurables en `main.py` o por argumentos de línea de comandos.)

## Vistas

### Terminal (`vista_terminal.py`)

- Limpia la pantalla en cada frame.
- Por cada tinaco: barra `[#####.....] 60%` y litros actuales/capacidad.
- Estado de cada bomba: ON / OFF y a qué destinos aporta.
- Tiempo transcurrido.
- Sin dependencias externas (solo librería estándar).

### matplotlib (`vista_matplotlib.py`)

- Dibuja el grafo con networkx: bombas como cuadros, tinacos como círculos.
- Color del tinaco según el llenado (de vacío a lleno).
- Etiqueta con el porcentaje en cada tinaco.
- Animación con `matplotlib.animation.FuncAnimation`, llamando a `paso(dt)`.
- Subplot opcional con barras de nivel.
- Requiere instalar `matplotlib` y `networkx` (pip).

## Manejo de errores / casos límite

- dt o caudal no positivos: validar y rechazar al construir.
- Capacidad cero o negativa: rechazar.
- Si una bomba no tiene destinos sin llenar, no aporta (no divide entre cero).
- Si falta matplotlib/networkx al elegir esa vista: mensaje claro pidiendo
  instalar dependencias, sin traza cruda.

## Pruebas (pytest)

- Un tinaco se llena exactamente hasta su capacidad, sin pasarse.
- Una bomba se apaga cuando todos sus destinos están llenos.
- T2 recibe aporte de ambas bombas en un mismo paso.
- Conservación: el volumen agregado en un paso es igual a la suma de aportes
  (salvo el recorte por capacidad).
- Reparto correcto del caudal cuando uno de los destinos ya está lleno.
```

## Fuera de alcance (YAGNI)

- Interfaz web o GUI más allá de matplotlib.
- Persistencia / guardado de la simulación.
- Configuración por archivo; basta con argumentos de línea de comandos.
- Más de dos bombas o tres tinacos (topología fija para este ejercicio).
