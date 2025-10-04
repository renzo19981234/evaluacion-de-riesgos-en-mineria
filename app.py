import streamlit as st
import pandas as pd
import plotly.express as px

# ======== CONFIGURACIÓN ========
st.set_page_config(page_title="Evaluación de Riesgos en Minería", layout="wide")

PASSWORD = "Mineria2024"
FILE_NAME = "riesgos_mineria_simulada.xlsx"

# ======== FUNCIÓN DE AUTENTICACIÓN ========
def autenticar():
    st.title("🔒 Acceso restringido")
    password = st.text_input("Introduce la contraseña:", type="password")
    if password == PASSWORD:
        st.session_state["autenticado"] = True
        st.success("Acceso concedido ✅")
    elif password:
        st.error("Contraseña incorrecta ❌")

# ======== APLICACIÓN PRINCIPAL ========
def app():
    st.title("⛏️ Evaluación de Riesgos en Minería")

    # Cargar datos
    try:
        df = pd.read_excel(FILE_NAME)
        df.columns = df.columns.str.strip()  # Elimina espacios extra en los nombres
        df.columns = df.columns.str.replace("á", "a").str.replace("é", "e").str.replace("í", "i").str.replace("ó", "o").str.replace("ú", "u")
    except FileNotFoundError:
        st.error(f"No se encontró el archivo **{FILE_NAME}** en el directorio.")
        return

    # Mostrar columnas originales para verificar
    with st.expander("📋 Ver columnas del archivo"):
        st.write(list(df.columns))

    # Verificar que existan las columnas necesarias
    columnas_necesarias = ["Area", "Nivel de riesgo", "Gravedad (1-5)", "Probabilidad (1-5)"]
    if not all(col in df.columns for col in columnas_necesarias):
        st.error(f"⚠️ El archivo no tiene las columnas requeridas: {', '.join(columnas_necesarias)}")
        return

    # Seleccionar área
    area_seleccionada = st.selectbox("Selecciona el área que deseas analizar:", sorted(df["Area"].unique()))

    # Filtrar datos por área
    df_filtrado = df[df["Area"] == area_seleccionada]

    # Calcular riesgo cuantificado
    df_filtrado["Riesgo Cuantificado"] = df_filtrado["Gravedad (1-5)"] * df_filtrado["Probabilidad (1-5)"]

    # Mostrar resumen
    st.subheader(f"📊 Resultados del Área: {area_seleccionada}")

    riesgo_promedio = df_filtrado["Riesgo Cuantificado"].mean()

    if riesgo_promedio < 6:
        nivel_texto = "Bajo 🟢"
    elif riesgo_promedio < 12:
        nivel_texto = "Medio 🟡"
    else:
        nivel_texto = "Alto 🔴"

    st.markdown(f"**Nivel de Riesgo General:** {nivel_texto}")
    st.markdown(f"**Riesgo Cuantificado Promedio:** {riesgo_promedio:.2f}")

    # ======== GRÁFICO CIRCULAR ========
    st.subheader("📈 Porcentaje de Riesgo por Área")

    df["Riesgo Cuantificado"] = df["Gravedad (1-5)"] * df["Probabilidad (1-5)"]
    riesgo_por_area = df.groupby("Area")["Riesgo Cuantificado"].mean().reset_index()

    fig = px.pie(riesgo_por_area, values="Riesgo Cuantificado", names="Area",
                 title="Distribución porcentual de riesgo por área",
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar tabla
    st.subheader("📋 Datos del área seleccionada")
    st.dataframe(df_filtrado)

# ======== FLUJO PRINCIPAL ========
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    autenticar()
else:
    app()
