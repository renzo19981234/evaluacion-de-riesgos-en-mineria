import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# --- Configuración de la app ---
st.set_page_config(page_title="Evaluación de Riesgos Mineros", layout="wide")

# --- Contraseña para acceso de carga ---
PASSWORD = "renzo2025"

st.title("🛠️ Evaluación de Riesgos por Área - Seguridad e Higiene Minera")
st.markdown("Esta aplicación permite visualizar los niveles de riesgo por área y analizar los indicadores de seguridad minera.")

# --- Carga del archivo Excel ---
st.sidebar.header("🔐 Subida de archivo (solo para administrador)")

password_input = st.sidebar.text_input("Introduce la contraseña:", type="password")
uploaded_file = None

if password_input == PASSWORD:
    uploaded_file = st.sidebar.file_uploader("Sube un archivo Excel con los datos de riesgos", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ Archivo cargado correctamente.")
else:
    st.sidebar.info("Introduce la contraseña para subir nuevos datos.")

# Si no se sube archivo, usar datos por defecto
if uploaded_file is None:
    df = pd.read_excel("datos_riesgos_mineros.xlsx")

# --- Mostrar tabla general ---
st.markdown("## 📋 Datos Generales de Riesgos")
st.dataframe(df)

# --- Filtro por área ---
areas = df["Área"].unique()
area_seleccionada = st.selectbox("Selecciona el área a analizar:", areas)
df_filtrado = df[df["Área"] == area_seleccionada]

# --- Indicadores principales ---
promedio_riesgo = df_filtrado["Nivel de riesgo"].mean()

if promedio_riesgo >= 15:
    clasificacion_global = "ALTO"
    color = "red"
elif promedio_riesgo >= 8:
    clasificacion_global = "MEDIO"
    color = "orange"
else:
    clasificacion_global = "BAJO"
    color = "green"

st.markdown(f"### 🔍 Resultados del Área: **{area_seleccionada}**")
st.metric("Nivel de Riesgo Promedio", f"{promedio_riesgo:.2f}")
st.markdown(
    f"<h4 style='color:{color};'>Clasificación Global: {clasificacion_global}</h4>",
    unsafe_allow_html=True
)

# --- Gráfico circular ---
st.markdown("### 📊 Distribución de Riesgos por Área")

df_pie = df.groupby("Área")["Nivel de riesgo"].mean().reset_index()

fig_pie = px.pie(
    df_pie,
    names="Área",
    values="Nivel de riesgo",
    title="Porcentaje de Nivel de Riesgo por Área",
    color_discrete_sequence=px.colors.sequential.RdYlGn_r
)

st.plotly_chart(fig_pie, use_container_width=True)

# --- Botón para descargar los datos filtrados ---
st.markdown("### 💾 Descargar Datos Filtrados")

def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Riesgos")
    buffer.seek(0)
    return buffer

excel_data = convertir_a_excel(df_filtrado)

st.download_button(
    label="📥 Descargar Excel del área seleccionada",
    data=excel_data,
    file_name=f"Riesgos_{area_seleccionada}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
