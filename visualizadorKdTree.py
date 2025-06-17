import matplotlib.pyplot as plt

# Dibuja solamente los puntos actuales sin consultas
def graficarPuntos(listaPuntos, xMax=10, yMax=10):
    fig, ax = plt.subplots()
    ax.set_xlim(0, xMax)
    ax.set_ylim(0, yMax)
    ax.set_title("Puntos en el espacio")
    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y")
    ax.grid(True)

    if listaPuntos:
        x, y = zip(*listaPuntos)
        ax.scatter(x, y, color='blue', label="Puntos")
        # Mostrar coordenadas al lado de cada punto
        for px, py in listaPuntos:
            ax.annotate(f"({px}, {py})", (px, py), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9, color='black')

    ax.legend()
    return fig


# Dibuja puntos más resultados de consulta
def graficarConsulta(puntos, puntosResultado=[], puntoConsulta=None, rect=None, vecinoCercano=None, xMax=10, yMax=10):
    fig, ax = plt.subplots()

    # Puntos base en azul
    for punto in puntos:
        ax.plot(punto[0], punto[1], 'o', color='blue')
        ax.annotate(f"({punto[0]}, {punto[1]})", (punto[0], punto[1]), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9)

    # Resultados en verde
    for punto in puntosResultado:
        ax.plot(punto[0], punto[1], 'o', color='green')
        ax.annotate(f"({punto[0]}, {punto[1]})", (punto[0], punto[1]), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9)

    # Punto de consulta
    if puntoConsulta:
        ax.plot(puntoConsulta[0], puntoConsulta[1], 'x', color='black', markersize=10)
        ax.annotate(f"({puntoConsulta[0]}, {puntoConsulta[1]})", (puntoConsulta[0], puntoConsulta[1]), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9)

    # Vecino más cercano
    if vecinoCercano:
        ax.plot(vecinoCercano[0], vecinoCercano[1], 'o', color='red', markersize=10)
        ax.annotate(f"({vecinoCercano[0]}, {vecinoCercano[1]})", (vecinoCercano[0], vecinoCercano[1]), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9)

    # Rectángulo de rango
    if rect:
        xMin, xMaxR, yMin, yMaxR = rect
        ancho = xMaxR - xMin
        alto = yMaxR - yMin
        rectangulo = plt.Rectangle((xMin, yMin), ancho, alto, linewidth=1.5, edgecolor='orange', facecolor='none', linestyle='--')
        ax.add_patch(rectangulo)

    ax.set_xlim(0, xMax)
    ax.set_ylim(0, yMax)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True)
    ax.set_title('Resultado de la consulta')
    return fig
