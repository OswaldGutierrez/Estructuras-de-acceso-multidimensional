# visualizadorQuadTree.py

import matplotlib.pyplot as plt
from quadTree import Rectangle # Se usa para el tipo de dato del rango

def _dibujar_divisiones_quadtree(ax, quadtree):
    """Función auxiliar para dibujar los límites del quadtree en un eje."""
    if not quadtree:
        return
    
    limites = quadtree.obtener_limites()
    for b in limites:
        rect = plt.Rectangle(
            (b.x - b.w, b.y - b.h), 2 * b.w, 2 * b.h,
            linewidth=0.8, edgecolor='gray', facecolor='none', linestyle='--'
        )
        ax.add_patch(rect)

# Dibuja los puntos y las divisiones del Quadtree
def graficarConQuadTree(listaPuntos, quadtree, xMax=10, yMax=10):
    fig, ax = plt.subplots()
    ax.set_xlim(0, xMax)
    ax.set_ylim(0, yMax)
    ax.set_title("Puntos y divisiones del Quadtree")
    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y")
    ax.grid(True)

    if listaPuntos:
        x, y = zip(*listaPuntos)
        ax.scatter(x, y, color='blue', label="Puntos")
        for px, py in listaPuntos:
            ax.annotate(f"({px}, {py})", (px, py), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9, color='black')

    _dibujar_divisiones_quadtree(ax, quadtree)
    
    ax.legend()
    return fig

# Dibuja puntos, divisiones y resultados de consulta para Quadtree
def graficarConsultaQuadTree(puntos, quadtree, puntosResultado=[], puntoConsulta=None, rect=None, vecinoCercano=None, xMax=10, yMax=10):
    fig, ax = plt.subplots()

    # Puntos base en azul
    for punto in puntos:
        ax.plot(punto[0], punto[1], 'o', color='blue')
        ax.annotate(f"({punto[0]}, {punto[1]})", (punto[0], punto[1]), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9)

    # Dibujar las divisiones del Quadtree
    _dibujar_divisiones_quadtree(ax, quadtree)
    
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

    # Rectángulo de rango (tipo Rectangle)
    if rect:
        ancho = rect.w * 2
        alto = rect.h * 2
        rect_plot = plt.Rectangle((rect.x - rect.w, rect.y - rect.h), ancho, alto, linewidth=1.5, edgecolor='orange', facecolor='none', linestyle='--')
        ax.add_patch(rect_plot)

    ax.set_xlim(0, xMax)
    ax.set_ylim(0, yMax)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True)
    ax.set_title('Resultado de la consulta Quadtree')
    return fig