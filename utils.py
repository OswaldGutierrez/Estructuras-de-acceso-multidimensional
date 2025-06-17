# utils.py

import random

# Genera una lista de puntos aleatorios dentro del rango dado, con un decimal
def generarPuntosAleatorios(cantidad, xMin, xMax, yMin, yMax):
    puntos = []
    for _ in range(cantidad):
        # Redondea a 1 decimal los valores generados
        x = round(random.uniform(xMin, xMax), 1)
        y = round(random.uniform(yMin, yMax), 1)
        puntos.append((x, y))
    return puntos

# Valida si un punto es una tupla con dos elementos numéricos
def esPuntoValido(punto):
    return isinstance(punto, tuple) and len(punto) == 2 and all(isinstance(coord, (int, float)) for coord in punto)
