# visualizadorRTree.py

import matplotlib.pyplot as plt
from rTree import Rectangle # Importa la clase Rectangle del rTree.py

def _dibujar_mbrs_r_tree(ax, rtree):
    """Función auxiliar para dibujar los MBRs de los nodos del R-Tree."""
    if not rtree or not rtree.root or not rtree.root.entries:
        return
    
    # Obtener todos los MBRs para dibujar
    mbrs = rtree.get_all_mbrs() # Este método debe existir en rTree.py

    for mbr in mbrs:
        if mbr: # Asegurarse de que el MBR no sea None
            # plt.Rectangle toma (x,y) de la esquina inferior izquierda, ancho, alto
            rect = plt.Rectangle(
                (mbr.min_x, mbr.min_y), 
                mbr.max_x - mbr.min_x, 
                mbr.max_y - mbr.min_y,
                linewidth=1, edgecolor='purple', facecolor='none', linestyle='-'
            )
            ax.add_patch(rect)
    
    # Opcional: Dibujar los MBRs de las entradas en nodos hoja (los puntos mismos)
    # Esto puede ser mucho si hay muchos puntos y MBRs pequeños.
    # Podríamos añadir una opción para mostrar esto o no. Por ahora, solo los MBRs de los nodos.
    # Si quisieras ver los MBRs de las entradas de hoja, tendrías que modificar rTree.get_all_mbrs()
    # o añadir una función específica para ello.

# Dibuja los puntos y los MBRs del R-Tree
def graficarConRTree(listaPuntos, rtree, xMax=10, yMax=10):
    fig, ax = plt.subplots()
    ax.set_xlim(0, xMax)
    ax.set_ylim(0, yMax)
    ax.set_title("Puntos y MBRs del R-Tree")
    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y")
    ax.grid(True, linestyle='dotted')

    if listaPuntos:
        x, y = zip(*listaPuntos)
        ax.scatter(x, y, color='blue', label="Puntos")
        for px, py in listaPuntos:
            ax.annotate(f"({px}, {py})", (px, py), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9, color='black')

    _dibujar_mbrs_r_tree(ax, rtree)
    
    ax.legend()
    return fig

# Dibuja puntos, MBRs y resultados de consulta para R-Tree
def graficarConsultaRTree(puntos, rtree, puntosResultado=[], puntoConsulta=None, rect=None, vecinoCercano=None, xMax=10, yMax=10):
    fig, ax = plt.subplots()

    # Puntos base en azul
    for punto in puntos:
        ax.plot(punto[0], punto[1], 'o', color='blue')
        ax.annotate(f"({punto[0]}, {punto[1]})", (punto[0], punto[1]), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9)

    # Dibujar los MBRs del R-Tree
    _dibujar_mbrs_r_tree(ax, rtree)
    
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

    # Rectángulo de rango (para R-Tree, es un objeto Rectangle)
    if rect:
        # Asegúrate de que 'rect' es un objeto Rectangle con min_x, min_y, max_x, max_y
        if isinstance(rect, Rectangle):
            xMin = rect.min_x
            yMin = rect.min_y
            ancho = rect.max_x - rect.min_x
            alto = rect.max_y - rect.min_y
            rect_plot = plt.Rectangle((xMin, yMin), ancho, alto, linewidth=1.5, edgecolor='orange', facecolor='none', linestyle='--')
            ax.add_patch(rect_plot)

    ax.set_xlim(0, xMax)
    ax.set_ylim(0, yMax)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True, linestyle='dotted')
    ax.set_title('Resultado de la consulta R-Tree')
    return fig