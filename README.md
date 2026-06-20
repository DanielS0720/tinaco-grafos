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
