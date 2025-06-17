# gridFile.py

import math

class Bucket:
    def __init__(self, capacity):
        self.points = []
        self.capacity = capacity

    def add_point(self, point):
        # Si el bucket tiene espacio, añade el punto
        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        return False

    def contains_point(self, point):
        return point in self.points

class GridFile:
    def __init__(self, x_min, x_max, y_min, y_max, grid_size_x, grid_size_y, bucket_capacity=4):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.grid_size_x = max(1, grid_size_x) # Asegura que sea al menos 1
        self.grid_size_y = max(1, grid_size_y) # Asegura que sea al menos 1
        self.bucket_capacity = bucket_capacity

        # Calcula el tamaño de cada celda en X e Y
        # Asegúrate de que el divisor no sea cero para evitar errores
        self.x_step = (x_max - x_min) / self.grid_size_x
        self.y_step = (y_max - y_min) / self.grid_size_y
        
        # Inicializa la cuadrícula con buckets vacíos
        self.grid = self._initialize_grid()

    def _initialize_grid(self):
        # Crea una matriz 2D de Buckets
        return [[Bucket(self.bucket_capacity) for _ in range(self.grid_size_y)]
                for _ in range(self.grid_size_x)]

    def _get_grid_coordinates(self, point):
        # Calcula las coordenadas de la celda para un punto dado
        # Ajuste para manejar puntos exactamente en el límite superior
        x_idx = int((point[0] - self.x_min) / self.x_step)
        y_idx = int((point[1] - self.y_min) / self.y_step)

        # Si un punto está exactamente en el límite superior, colócalo en la última celda.
        # Esto es importante para puntos como (20.0, 5.0) en un rango de 0-20.
        if point[0] == self.x_max and self.x_step != 0:
            x_idx = self.grid_size_x - 1
        if point[1] == self.y_max and self.y_step != 0:
            y_idx = self.grid_size_y - 1

        # Asegura que las coordenadas estén dentro de los límites de la cuadrícula
        x_idx = max(0, min(x_idx, self.grid_size_x - 1))
        y_idx = max(0, min(y_idx, self.grid_size_y - 1))
        return x_idx, y_idx

    def insertar(self, point):
        # Verifica si el punto está dentro del rango general del Grid File
        if not (self.x_min <= point[0] <= self.x_max and
                self.y_min <= point[1] <= self.y_max):
            return False

        x_idx, y_idx = self._get_grid_coordinates(point)
        # Intenta añadir el punto al bucket correspondiente
        return self.grid[x_idx][y_idx].add_point(point)

    def buscarPunto(self, point):
        # Verifica si el punto está dentro del rango general del Grid File
        if not (self.x_min <= point[0] <= self.x_max and
                self.y_min <= point[1] <= self.y_max):
            return False
        x_idx, y_idx = self._get_grid_coordinates(point)
        # Busca el punto en el bucket de la celda correspondiente
        return self.grid[x_idx][y_idx].contains_point(point)

    def buscarEnRango(self, xMin, xMax, yMin, yMax):
        results = []
        
        # Determina las celdas de la cuadrícula que se intersectan con el rango de consulta
        # Es crucial usar floor para el inicio y ceil para el final (o int y ajuste)
        
        # Calcular los índices de las celdas que contienen los límites del rango de consulta
        # Limitar a los bordes de la cuadrícula
        start_x_idx = max(0, int(math.floor((xMin - self.x_min) / self.x_step)))
        # Para el final, floor(xMax / step) podría dar un índice menor si xMax es un límite exacto.
        # Por eso, se calcula a dónde caería el punto y se ajusta al último índice si es necesario.
        end_x_idx = min(self.grid_size_x - 1, int(math.floor((xMax - self.x_min) / self.x_step)))
        # Si xMax coincide exactamente con el límite superior de la última celda, el floor
        # lo dejará en grid_size_x - 1, lo cual es correcto. Si lo excede, min lo recorta.

        start_y_idx = max(0, int(math.floor((yMin - self.y_min) / self.y_step)))
        end_y_idx = min(self.grid_size_y - 1, int(math.floor((yMax - self.y_min) / self.y_step)))
        
        # Iterar sobre las celdas que se superponen con el rango.
        # Se suma 1 a los índices finales en `range` para incluir la última celda.
        for i in range(start_x_idx, end_x_idx + 1):
            for j in range(start_y_idx, end_y_idx + 1):
                # Para cada punto en el bucket de la celda, verifica si está DENTRO del rango de consulta
                for p in self.grid[i][j].points:
                    if xMin <= p[0] <= xMax and yMin <= p[1] <= yMax:
                        results.append(p)
        return results

    def buscarVecinoMasCercano(self, punto_objetivo):
        if not self.grid_size_x > 0 or not self.grid_size_y > 0:
            return None

        closest_point = None
        min_dist = float('inf')
        
        for i in range(self.grid_size_x):
            for j in range(self.grid_size_y):
                for p in self.grid[i][j].points:
                    dist = math.dist(p, punto_objetivo)
                    if dist < min_dist:
                        min_dist = dist
                        closest_point = p
        
        return closest_point

    def get_grid_cells_boundaries(self):
        # Devuelve los límites de todas las celdas de la cuadrícula para visualización
        boundaries = []
        # Solo procede si los pasos no son cero y las dimensiones de la cuadrícula son válidas
        if self.x_step == 0 or self.y_step == 0 or self.grid_size_x == 0 or self.grid_size_y == 0:
            return boundaries
            
        for i in range(self.grid_size_x):
            for j in range(self.grid_size_y):
                x_start = self.x_min + i * self.x_step
                y_start = self.y_min + j * self.y_step
                x_end = x_start + self.x_step
                y_end = y_start + self.y_step
                boundaries.append(((x_start, y_start), (x_end, y_end)))
        return boundaries