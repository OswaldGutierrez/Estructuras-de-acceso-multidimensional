# quadTree.py

import math

class Rectangle:
    """Define un área rectangular en el plano."""
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w  # Ancho
        self.h = h  # Alto

    def contiene_punto(self, punto):
        """Verifica si un punto está dentro de este rectángulo."""
        return (self.x - self.w <= punto[0] < self.x + self.w and
                self.y - self.h <= punto[1] < self.y + self.h)

    def intersecta(self, rango):
        """Verifica si otro rectángulo se superpone con este."""
        return not (rango.x - rango.w > self.x + self.w or
                    rango.x + rango.w < self.x - self.w or
                    rango.y - rango.h > self.y + self.h or
                    rango.y + rango.h < self.y - self.h)

class QuadTree:
    """Estructura de datos Quadtree."""
    def __init__(self, boundary, capacidad):
        self.boundary = boundary
        self.capacidad = capacidad
        self.puntos = []
        self.dividido = False
        self.noreste = None
        self.noroeste = None
        self.sureste = None
        self.suroeste = None

    def subdividir(self):
        """Divide el quadtree en cuatro sub-quadtrees."""
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.w / 2
        h = self.boundary.h / 2

        ne = Rectangle(x + w, y - h, w, h)
        self.noreste = QuadTree(ne, self.capacidad)
        nw = Rectangle(x - w, y - h, w, h)
        self.noroeste = QuadTree(nw, self.capacidad)
        se = Rectangle(x + w, y + h, w, h)
        self.sureste = QuadTree(se, self.capacidad)
        sw = Rectangle(x - w, y + h, w, h)
        self.suroeste = QuadTree(sw, self.capacidad)

        self.dividido = True

    def insertar(self, punto):
        """Inserta un punto en el Quadtree."""
        if not self.boundary.contiene_punto(punto):
            return False

        if len(self.puntos) < self.capacidad:
            self.puntos.append(punto)
            return True
        else:
            if not self.dividido:
                self.subdividir()

            if self.noreste.insertar(punto):
                return True
            elif self.noroeste.insertar(punto):
                return True
            elif self.sureste.insertar(punto):
                return True
            elif self.suroeste.insertar(punto):
                return True
    
    def buscarPunto(self, punto):
        """Busca un punto exacto en el Quadtree."""
        if not self.boundary.contiene_punto(punto):
            return None

        for p in self.puntos:
            if p == punto:
                return p
        
        if self.dividido:
            if (res := self.noroeste.buscarPunto(punto)) is not None: return res
            if (res := self.noreste.buscarPunto(punto)) is not None: return res
            if (res := self.suroeste.buscarPunto(punto)) is not None: return res
            if (res := self.sureste.buscarPunto(punto)) is not None: return res
        
        return None

    def buscarEnRango(self, rango):
        """Encuentra todos los puntos dentro de un rango rectangular."""
        puntos_encontrados = []
        if not self.boundary.intersecta(rango):
            return puntos_encontrados

        for p in self.puntos:
            if rango.contiene_punto(p):
                puntos_encontrados.append(p)

        if self.dividido:
            puntos_encontrados.extend(self.noroeste.buscarEnRango(rango))
            puntos_encontrados.extend(self.noreste.buscarEnRango(rango))
            puntos_encontrados.extend(self.suroeste.buscarEnRango(rango))
            puntos_encontrados.extend(self.sureste.buscarEnRango(rango))

        return puntos_encontrados

    def buscarVecinoMasCercano(self, punto_consulta, mejor_dist=float('inf'), vecino_cercano=None):
        """Encuentra el vecino más cercano a un punto dado."""
        if not self.boundary.contiene_punto(punto_consulta) and \
           math.dist((self.boundary.x, self.boundary.y), punto_consulta) > mejor_dist:
             return vecino_cercano, mejor_dist

        for p in self.puntos:
            dist = math.dist(p, punto_consulta)
            if dist < mejor_dist:
                mejor_dist = dist
                vecino_cercano = p

        if self.dividido:
            # Ordenar los hijos por proximidad al punto de consulta
            hijos = [self.noroeste, self.noreste, self.suroeste, self.sureste]
            hijos.sort(key=lambda quad: math.dist((quad.boundary.x, quad.boundary.y), punto_consulta))

            for hijo in hijos:
                vecino_cercano, mejor_dist = hijo.buscarVecinoMasCercano(punto_consulta, mejor_dist, vecino_cercano)

        return vecino_cercano, mejor_dist
    
    def obtener_limites(self):
        """Recopila todos los límites de los quadtree para visualización."""
        limites = [self.boundary]
        if self.dividido:
            limites.extend(self.noroeste.obtener_limites())
            limites.extend(self.noreste.obtener_limites())
            limites.extend(self.suroeste.obtener_limites())
            limites.extend(self.sureste.obtener_limites())
        return limites