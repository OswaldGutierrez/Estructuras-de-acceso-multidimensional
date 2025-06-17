# kdTree.py

import math

class NodoKD:
    def __init__(self, punto, profundidad=0):
        self.punto = punto
        self.izquierdo = None
        self.derecho = None
        self.profundidad = profundidad

class ArbolKD:
    def __init__(self):
        self.raiz = None

    # Insertar un nuevo punto en el árbol KD
    def insertar(self, punto):
        self.raiz = self._insertarRecursivo(self.raiz, punto, 0)

    def _insertarRecursivo(self, nodo, punto, profundidad):
        if nodo is None:
            return NodoKD(punto, profundidad)

        eje = profundidad % 2

        if punto[eje] < nodo.punto[eje]:
            nodo.izquierdo = self._insertarRecursivo(nodo.izquierdo, punto, profundidad + 1)
        else:
            nodo.derecho = self._insertarRecursivo(nodo.derecho, punto, profundidad + 1)

        return nodo

    # Consulta puntual: verificar si un punto exacto está en el árbol
    def buscarPunto(self, punto):
        return self._buscarRecursivo(self.raiz, punto, 0)

    def _buscarRecursivo(self, nodo, punto, profundidad):
        if nodo is None:
            return False

        if nodo.punto == punto:
            return True

        eje = profundidad % 2

        if punto[eje] < nodo.punto[eje]:
            return self._buscarRecursivo(nodo.izquierdo, punto, profundidad + 1)
        else:
            return self._buscarRecursivo(nodo.derecho, punto, profundidad + 1)

    # Consulta por rango: obtener puntos dentro de un rectángulo [xMin, xMax, yMin, yMax]
    def buscarEnRango(self, xMin, xMax, yMin, yMax):
        resultado = []
        self._buscarEnRangoRecursivo(self.raiz, xMin, xMax, yMin, yMax, 0, resultado)
        return resultado

    def _buscarEnRangoRecursivo(self, nodo, xMin, xMax, yMin, yMax, profundidad, resultado):
        if nodo is None:
            return

        x, y = nodo.punto
        if xMin <= x <= xMax and yMin <= y <= yMax:
            resultado.append(nodo.punto)

        eje = profundidad % 2

        if eje == 0:  # Comparar en X
            if nodo.punto[0] >= xMin:
                self._buscarEnRangoRecursivo(nodo.izquierdo, xMin, xMax, yMin, yMax, profundidad + 1, resultado)
            if nodo.punto[0] <= xMax:
                self._buscarEnRangoRecursivo(nodo.derecho, xMin, xMax, yMin, yMax, profundidad + 1, resultado)
        else:  # Comparar en Y
            if nodo.punto[1] >= yMin:
                self._buscarEnRangoRecursivo(nodo.izquierdo, xMin, xMax, yMin, yMax, profundidad + 1, resultado)
            if nodo.punto[1] <= yMax:
                self._buscarEnRangoRecursivo(nodo.derecho, xMin, xMax, yMin, yMax, profundidad + 1, resultado)

    # Consulta de vecino más cercano
    def buscarVecinoMasCercano(self, puntoObjetivo):
        return self._buscarNN(self.raiz, puntoObjetivo, 0, None, float('inf'))

    def _buscarNN(self, nodo, puntoObjetivo, profundidad, mejorNodo, mejorDistancia):
        if nodo is None:
            return mejorNodo

        distancia = math.dist(nodo.punto, puntoObjetivo)
        if distancia < mejorDistancia:
            mejorNodo = nodo
            mejorDistancia = distancia

        eje = profundidad % 2

        # Elegir el subárbol relevante
        if puntoObjetivo[eje] < nodo.punto[eje]:
            siguiente = nodo.izquierdo
            otro = nodo.derecho
        else:
            siguiente = nodo.derecho
            otro = nodo.izquierdo

        mejorNodo = self._buscarNN(siguiente, puntoObjetivo, profundidad + 1, mejorNodo, mejorDistancia)

        # Verificar si es necesario revisar el otro subárbol
        if abs(puntoObjetivo[eje] - nodo.punto[eje]) < mejorDistancia:
            mejorNodo = self._buscarNN(otro, puntoObjetivo, profundidad + 1, mejorNodo, mejorDistancia)

        return mejorNodo
