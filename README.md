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
