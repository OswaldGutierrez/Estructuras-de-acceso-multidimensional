# app.py

import streamlit as st
from kdTree import ArbolKD
from visualizador import graficarConsulta, graficarPuntos
from utils import generarPuntosAleatorios, esPuntoValido

# Inicializa el estado de sesión para los puntos si aún no existe
if 'puntos' not in st.session_state:
    st.session_state.puntos = []

# Título principal
st.title("Visualización de KD-Tree")
st.markdown("---")

# ======================== SECCIÓN: AGREGAR PUNTOS ========================

st.subheader("Agregar puntos")

# ----------- Agregar punto manualmente -----------
col1, col2, col3 = st.columns([1, 1, 1.5])
with col1:
    xManual = st.number_input("Coordenada X", key="xManual", value=0.0, step=0.5)
with col2:
    yManual = st.number_input("Coordenada Y", key="yManual", value=0.0, step=0.5)
with col3:
    if st.button("Agregar punto manual"):
        nuevo = (round(xManual, 1), round(yManual, 1))  # Asegura 1 decimal
        if esPuntoValido(nuevo):
            st.session_state.puntos.append(nuevo)
            st.success(f"Agregado punto {nuevo}")
            st.rerun()  # Redibuja el gráfico automáticamente

# ----------- Generar puntos aleatorios -----------
col4, col5 = st.columns([3, 1])
with col4:
    cantidad = st.slider("Generar puntos aleatorios", 1, 20, 5)
with col5:
    if st.button("Generar aleatorios"):
        nuevos = generarPuntosAleatorios(cantidad, 0, 20, 0, 20)
        st.session_state.puntos.extend(nuevos)
        st.success(f"{cantidad} puntos generados")
        st.rerun()  # Redibuja el gráfico automáticamente

st.markdown("---")

# ======================== SECCIÓN: GRÁFICO DINÁMICO ========================

st.subheader("Gráfico de puntos")

if st.session_state.puntos:
    maxX = max(p[0] for p in st.session_state.puntos)
    maxY = max(p[1] for p in st.session_state.puntos)
    limX = max(10, int(maxX + 1))
    limY = max(10, int(maxY + 1))
else:
    limX = limY = 10

fig = graficarPuntos(st.session_state.puntos, xMax=limX, yMax=limY)
st.pyplot(fig)

# ======================== SECCIÓN: CONSULTAS KD-TREE ========================

if st.session_state.puntos:
    st.markdown("---")
    st.subheader("Consultas en KD-Tree")

    arbol = ArbolKD()
    for p in st.session_state.puntos:
        arbol.insertar(p)

    tipoConsulta = st.selectbox("Selecciona tipo de consulta", ["Consulta puntual", "Consulta por rango", "Vecino más cercano"])

    if tipoConsulta == "Consulta puntual":
        colx, coly = st.columns(2)
        with colx:
            x = st.number_input("X", key="busqX", step=0.5)
        with coly:
            y = st.number_input("Y", key="busqY", step=0.5)
        if st.button("Buscar punto exacto"):
            punto = (x, y)
            encontrado = arbol.buscarPunto(punto)
            resultado = [punto] if encontrado else []
            fig = graficarConsulta(
                st.session_state.puntos,
                puntosResultado=resultado,
                puntoConsulta=punto,
                xMax=limX,
                yMax=limY
            )
            st.pyplot(fig)
            st.success("Punto encontrado." if encontrado else "Punto no encontrado.")

    elif tipoConsulta == "Consulta por rango":
        col1, col2 = st.columns(2)
        with col1:
            xMin = st.number_input("X Min", value=2.0, step=0.5)
            xMax = st.number_input("X Max", value=8.0, step=0.5)
        with col2:
            yMin = st.number_input("Y Min", value=2.0, step=0.5)
            yMax = st.number_input("Y Max", value=8.0, step=0.5)
        if st.button("Buscar en rango"):
            resultados = arbol.buscarEnRango(xMin, xMax, yMin, yMax)
            fig = graficarConsulta(
                st.session_state.puntos,
                puntosResultado=resultados,
                rect=(xMin, xMax, yMin, yMax),
                xMax=limX,
                yMax=limY
            )
            st.pyplot(fig)
            st.success(f"{len(resultados)} punto(s) en el rango.")

    elif tipoConsulta == "Vecino más cercano":
        colx, coly = st.columns(2)
        with colx:
            x = st.number_input("X consulta", key="nnX", step=0.5)
        with coly:
            y = st.number_input("Y consulta", key="nnY", step=0.5)
        if st.button("Buscar vecino más cercano"):
            puntoRef = (x, y)
            nodo = arbol.buscarVecinoMasCercano(puntoRef)
            fig = graficarConsulta(
                st.session_state.puntos,
                puntoConsulta=puntoRef,
                vecinoCercano=nodo.punto if nodo else None,
                xMax=limX,
                yMax=limY
            )
            st.pyplot(fig)
            st.success(f"Vecino más cercano: {nodo.punto}" if nodo else "No hay puntos en el árbol.")

# ======================== BOTÓN: LIMPIAR ========================

st.markdown("---")
if st.button("Limpiar todo"):
    st.session_state.puntos = []
    st.rerun()
