# visualizadorGridFile.py

import matplotlib.pyplot as plt

def _dibujar_grid_boundaries(ax, grid_file):
    """Función auxiliar para dibujar los límites de las celdas del Grid File."""
    if not grid_file:
        return
    
    boundaries = grid_file.get_grid_cells_boundaries()
    for ((x_start, y_start), (x_end, y_end)) in boundaries:
        rect = plt.Rectangle(
            (x_start, y_start), x_end - x_start, y_end - y_start,
            linewidth=0.8, edgecolor='gray', facecolor='none', linestyle=':'
        )
        ax.add_patch(rect)

# Dibuja los puntos y las celdas del Grid File
def graficarConGridFile(listaPuntos, grid_file, xMax=10, yMax=10):
    fig, ax = plt.subplots()
    ax.set_xlim(0, xMax)
    ax.set_ylim(0, yMax)
    ax.set_title("Puntos y celdas del Grid File")
    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y")
    ax.grid(True, linestyle='dotted') # Cuadrícula principal del plot

    if listaPuntos:
        x, y = zip(*listaPuntos)
        ax.scatter(x, y, color='blue', label="Puntos")
        for px, py in listaPuntos:
            ax.annotate(f"({px}, {py})", (px, py), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9, color='black')

    _dibujar_grid_boundaries(ax, grid_file)
    
    ax.legend()
    return fig

# Dibuja puntos, celdas y resultados de consulta para Grid File
def graficarConsultaGridFile(puntos, grid_file, puntosResultado=[], puntoConsulta=None, rect=None, vecinoCercano=None, xMax=10, yMax=10):
    fig, ax = plt.subplots()

    # Puntos base en azul
    for punto in puntos:
        ax.plot(punto[0], punto[1], 'o', color='blue')
        ax.annotate(f"({punto[0]}, {punto[1]})", (punto[0], punto[1]), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9)

    # Dibujar las divisiones del Grid File
    _dibujar_grid_boundaries(ax, grid_file)
    
    # Resultados en verde
    for punto in puntosResultado:
        ax.plot(punto[0], punto[1], 'o', color='green', markersize=8)

    # Punto de consulta
    if puntoConsulta:
        ax.plot(puntoConsulta[0], puntoConsulta[1], 'x', color='black', markersize=10, label="Punto de Consulta")

    # Vecino más cercano
    if vecinoCercano:
        ax.plot(vecinoCercano[0], vecinoCercano[1], 'o', color='red', markersize=10, label="Vecino Cercano")
        if puntoConsulta:
            ax.plot([puntoConsulta[0], vecinoCercano[0]], [puntoConsulta[1], vecinoCercano[1]], 'r--', linewidth=1)

    # Rectángulo de rango (para Grid File, es xMin, xMax, yMin, yMax)
    if rect:
        xMin, xMaxR, yMin, yMaxR = rect
        ancho = xMaxR - xMin
        alto = yMaxR - yMin
        rect_plot = plt.Rectangle((xMin, yMin), ancho, alto, linewidth=1.5, edgecolor='orange', facecolor='none', linestyle='--')
        ax.add_patch(rect_plot)

    ax.set_xlim(0, xMax)
    ax.set_ylim(0, yMax)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True, linestyle='dotted')
    ax.set_title('Resultado de la consulta Grid File')
    return fig