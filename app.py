# app.py

import streamlit as st
from kdTree import ArbolKD
from quadTree import QuadTree, Rectangle
from gridFile import GridFile # Importa la clase GridFile
# Importaciones de visualizadores separados
from visualizadorKdTree import graficarPuntos as graficarPuntosKd, graficarConsulta as graficarConsultaKd
from visualizadorQuadTree import graficarConQuadTree, graficarConsultaQuadTree
from visualizadorGridFile import graficarConGridFile, graficarConsultaGridFile # Importa las funciones de visualización para GridFile
from utils import generarPuntosAleatorios, esPuntoValido

# Inicializa el estado de sesión
if 'puntos' not in st.session_state:
    st.session_state.puntos = []
if 'estructura' not in st.session_state:
    st.session_state.estructura = "KD-Tree"
# Nuevos estados para la configuración del Grid File
if 'grid_size_x' not in st.session_state:
    st.session_state.grid_size_x = 5
if 'grid_size_y' not in st.session_state:
    st.session_state.grid_size_y = 5
if 'bucket_capacity' not in st.session_state:
    st.session_state.bucket_capacity = 4


# Título principal
st.title("Visualizador de Estructuras de Datos Espaciales")
st.markdown("---")

# ======================== SECCIÓN: SELECCIÓN DE ESTRUCTURA ========================
st.subheader("1. Elige la estructura de datos")
st.session_state.estructura = st.radio(
    "Selecciona la estructura a utilizar:",
    ("KD-Tree", "Quadtree", "Grid File"), # Asegúrate de que "Grid File" esté aquí
    horizontal=True,
    key="selector_estructura"
)
st.markdown("---")

# Mover la configuración del Grid File a la barra lateral, ligada a la selección de estructura
if st.session_state.estructura == "Grid File":
    st.sidebar.header("Configuración de Grid File")
    st.session_state.grid_size_x = st.sidebar.slider("Celdas X (Grid)", 2, 20, st.session_state.grid_size_x, key="grid_x_global_slider")
    st.session_state.grid_size_y = st.sidebar.slider("Celdas Y (Grid)", 2, 20, st.session_state.grid_size_y, key="grid_y_global_slider")
    st.session_state.bucket_capacity = st.sidebar.slider("Capacidad Bucket (Grid)", 1, 10, st.session_state.bucket_capacity, key="grid_bucket_global_slider")


# ======================== SECCIÓN: AGREGAR PUNTOS ========================

st.subheader("2. Agrega o genera puntos")

# ----------- Agregar punto manualmente -----------
col1, col2, col3 = st.columns([1, 1, 1.5])
with col1:
    xManual = st.number_input("Coordenada X", key="xManual", value=0.0, step=0.5)
with col2:
    yManual = st.number_input("Coordenada Y", key="yManual", value=0.0, step=0.5)
with col3:
    st.write("") # Espaciador
    st.write("") # Espaciador
    if st.button("Agregar punto"):
        nuevo = (round(xManual, 1), round(yManual, 1))
        if esPuntoValido(nuevo):
            st.session_state.puntos.append(nuevo)
            st.success(f"Agregado punto {nuevo}")
            st.rerun()

# ----------- Generar puntos aleatorios -----------
col4, col5 = st.columns([3, 1])
with col4:
    cantidad = st.slider("Cantidad de puntos a generar:", 1, 50, 5)
with col5:
    st.write("") # Espaciador
    st.write("") # Espaciador
    if st.button("Generar"):
        nuevos = generarPuntosAleatorios(cantidad, 0, 20, 0, 20)
        st.session_state.puntos.extend(nuevos)
        st.success(f"{cantidad} puntos generados")
        st.rerun()
st.markdown("---")


# ======================== SECCIÓN: GRÁFICO DINÁMICO ========================

st.subheader("3. Visualización del espacio y la estructura")

if st.session_state.puntos:
    maxX = max(p[0] for p in st.session_state.puntos)
    maxY = max(p[1] for p in st.session_state.puntos)
    limX = max(10, int(maxX + 5))
    limY = max(10, int(maxY + 5))
else:
    limX = limY = 10

# Dibuja el gráfico según la estructura seleccionada
if st.session_state.estructura == "Quadtree" and st.session_state.puntos:
    boundary = Rectangle(limX / 2, limY / 2, limX / 2, limY / 2)
    qtree = QuadTree(boundary, 4)
    for p in st.session_state.puntos:
        qtree.insertar(p)
    fig = graficarConQuadTree(st.session_state.puntos, qtree, xMax=limX, yMax=limY)
elif st.session_state.estructura == "Grid File" and st.session_state.puntos:
    # Usar los valores guardados en st.session_state
    grid_file = GridFile(0, limX, 0, limY, st.session_state.grid_size_x, st.session_state.grid_size_y, st.session_state.bucket_capacity)
    for p in st.session_state.puntos:
        grid_file.insertar(p) # Los puntos que no caben no se insertan
    fig = graficarConGridFile(st.session_state.puntos, grid_file, xMax=limX, yMax=limY)
else: # KD-Tree o no hay puntos
    fig = graficarPuntosKd(st.session_state.puntos, xMax=limX, yMax=limY)

st.pyplot(fig)

# ======================== SECCIÓN: CONSULTAS ========================

if st.session_state.puntos:
    st.markdown("---")
    st.subheader(f"4. Consultas en {st.session_state.estructura}")

    # -------- Lógica para KD-Tree --------
    if st.session_state.estructura == "KD-Tree":
        arbol = ArbolKD()
        for p in st.session_state.puntos:
            arbol.insertar(p)

        tipoConsulta = st.selectbox("Selecciona tipo de consulta", ["Consulta puntual", "Consulta por rango", "Vecino más cercano"], key="kd_consulta")

        if tipoConsulta == "Consulta puntual":
            colx, coly = st.columns(2)
            with colx:
                x = st.number_input("X", key="busqX_kd", step=0.5)
            with coly:
                y = st.number_input("Y", key="busqY_kd", step=0.5)
            if st.button("Buscar punto exacto", key="btn_punto_kd"):
                punto = (x, y)
                encontrado = arbol.buscarPunto(punto)
                resultado = [punto] if encontrado else []
                fig = graficarConsultaKd(st.session_state.puntos, puntosResultado=resultado, puntoConsulta=punto, xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success("Punto encontrado." if encontrado else "Punto no encontrado.")

        elif tipoConsulta == "Consulta por rango":
            col1, col2 = st.columns(2)
            with col1:
                xMin = st.number_input("X Min", value=2.0, step=0.5, key="rangoXmin_kd")
                xMax = st.number_input("X Max", value=8.0, step=0.5, key="rangoXmax_kd")
            with col2:
                yMin = st.number_input("Y Min", value=2.0, step=0.5, key="rangoYmin_kd")
                yMax = st.number_input("Y Max", value=8.0, step=0.5, key="rangoYmax_kd")
            if st.button("Buscar en rango", key="btn_rango_kd"):
                resultados = arbol.buscarEnRango(xMin, xMax, yMin, yMax)
                fig = graficarConsultaKd(st.session_state.puntos, puntosResultado=resultados, rect=(xMin, xMax, yMin, yMax), xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success(f"{len(resultados)} punto(s) en el rango.")

        elif tipoConsulta == "Vecino más cercano":
            colx, coly = st.columns(2)
            with colx:
                x = st.number_input("X consulta", key="nnX_kd", step=0.5)
            with coly:
                y = st.number_input("Y consulta", key="nnY_kd", step=0.5)
            if st.button("Buscar vecino más cercano", key="btn_nn_kd"):
                puntoRef = (x, y)
                nodo = arbol.buscarVecinoMasCercano(puntoRef)
                fig = graficarConsultaKd(st.session_state.puntos, puntoConsulta=puntoRef, vecinoCercano=nodo.punto if nodo else None, xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success(f"Vecino más cercano: {nodo.punto}" if nodo else "No hay puntos en el árbol.")

    # -------- Lógica para Quadtree --------
    elif st.session_state.estructura == "Quadtree":
        boundary = Rectangle(limX / 2, limY / 2, limX / 2, limY / 2)
        qtree = QuadTree(boundary, 4)
        for p in st.session_state.puntos:
            qtree.insertar(p)

        tipoConsulta = st.selectbox("Selecciona tipo de consulta", ["Consulta puntual", "Consulta por rango", "Vecino más cercano"], key="qt_consulta")

        if tipoConsulta == "Consulta puntual":
            colx, coly = st.columns(2)
            with colx:
                x = st.number_input("X", key="busqX_qt", step=0.5)
            with coly:
                y = st.number_input("Y", key="busqY_qt", step=0.5)
            if st.button("Buscar punto exacto", key="btn_punto_qt"):
                punto = (x, y)
                encontrado = qtree.buscarPunto(punto)
                resultado = [punto] if encontrado else []
                fig = graficarConsultaQuadTree(st.session_state.puntos, qtree, puntosResultado=resultado, puntoConsulta=punto, xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success("Punto encontrado." if encontrado else "Punto no encontrado.")

        elif tipoConsulta == "Consulta por rango":
            col1, col2 = st.columns(2)
            with col1:
                xMin = st.number_input("X Min", value=2.0, step=0.5, key="rangoXmin_qt")
                ancho = st.number_input("Ancho", value=6.0, step=0.5, key="rangoW_qt")
            with col2:
                yMin = st.number_input("Y Min", value=2.0, step=0.5, key="rangoYmin_qt")
                alto = st.number_input("Alto", value=6.0, step=0.5, key="rangoH_qt")
            if st.button("Buscar en rango", key="btn_rango_qt"):
                rango_rect = Rectangle(xMin + ancho / 2, yMin + alto / 2, ancho / 2, alto / 2)
                resultados = qtree.buscarEnRango(rango_rect)
                fig = graficarConsultaQuadTree(st.session_state.puntos, qtree, puntosResultado=resultados, rect=rango_rect, xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success(f"{len(resultados)} punto(s) en el rango.")

        elif tipoConsulta == "Vecino más cercano":
            colx, coly = st.columns(2)
            with colx:
                x = st.number_input("X consulta", key="nnX_qt", step=0.5)
            with coly:
                y = st.number_input("Y consulta", key="nnY_qt", step=0.5)
            if st.button("Buscar vecino más cercano", key="btn_nn_qt"):
                puntoRef = (x, y)
                vecino, _ = qtree.buscarVecinoMasCercano(puntoRef)
                fig = graficarConsultaQuadTree(st.session_state.puntos, qtree, puntoConsulta=puntoRef, vecinoCercano=vecino, xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success(f"Vecino más cercano: {vecino}" if vecino else "No hay puntos en el árbol.")

    # -------- Lógica para Grid File --------
    elif st.session_state.estructura == "Grid File":
        # Usar los valores guardados en st.session_state para construir el Grid File
        grid_file = GridFile(0, limX, 0, limY, st.session_state.grid_size_x, st.session_state.grid_size_y, st.session_state.bucket_capacity)
        for p in st.session_state.puntos:
            grid_file.insertar(p)

        tipoConsulta = st.selectbox("Selecciona tipo de consulta", ["Consulta puntual", "Consulta por rango", "Vecino más cercano"], key="gf_consulta")

        if tipoConsulta == "Consulta puntual":
            colx, coly = st.columns(2)
            with colx:
                x = st.number_input("X", key="busqX_gf", step=0.5)
            with coly:
                y = st.number_input("Y", key="busqY_gf", step=0.5)
            if st.button("Buscar punto exacto", key="btn_punto_gf"):
                punto = (x, y)
                encontrado = grid_file.buscarPunto(punto)
                resultado = [punto] if encontrado else []
                fig = graficarConsultaGridFile(st.session_state.puntos, grid_file, puntosResultado=resultado, puntoConsulta=punto, xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success("Punto encontrado." if encontrado else "Punto no encontrado.")

        elif tipoConsulta == "Consulta por rango":
            col1, col2 = st.columns(2)
            with col1:
                xMin = st.number_input("X Min", value=2.0, step=0.5, key="rangoXmin_gf")
                xMax = st.number_input("X Max", value=8.0, step=0.5, key="rangoXmax_gf")
            with col2:
                yMin = st.number_input("Y Min", value=2.0, step=0.5, key="rangoYmin_gf")
                yMax = st.number_input("Y Max", value=8.0, step=0.5, key="rangoYmax_gf")
            if st.button("Buscar en rango", key="btn_rango_gf"):
                resultados = grid_file.buscarEnRango(xMin, xMax, yMin, yMax)
                fig = graficarConsultaGridFile(st.session_state.puntos, grid_file, puntosResultado=resultados, rect=(xMin, xMax, yMin, yMax), xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success(f"{len(resultados)} punto(s) en el rango.")

        elif tipoConsulta == "Vecino más cercano":
            colx, coly = st.columns(2)
            with colx:
                x = st.number_input("X consulta", key="nnX_gf", step=0.5)
            with coly:
                y = st.number_input("Y consulta", key="nnY_gf", step=0.5)
            if st.button("Buscar vecino más cercano", key="btn_nn_gf"):
                puntoRef = (x, y)
                vecino = grid_file.buscarVecinoMasCercano(puntoRef)
                fig = graficarConsultaGridFile(st.session_state.puntos, grid_file, puntoConsulta=puntoRef, vecinoCercano=vecino, xMax=limX, yMax=limY)
                st.pyplot(fig)
                st.success(f"Vecino más cercano: {vecino}" if vecino else "No hay puntos en el Grid File.")


# ======================== BOTÓN: LIMPIAR ========================
st.markdown("---")
if st.button("Limpiar todo"):
    st.session_state.puntos = []
    # Restablecer los valores por defecto del Grid File al limpiar todo
    st.session_state.grid_size_x = 5
    st.session_state.grid_size_y = 5
    st.session_state.bucket_capacity = 4
    st.rerun()