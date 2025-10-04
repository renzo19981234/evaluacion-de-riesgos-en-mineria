import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# ------------------------------
# CONFIGURACIÓN BÁSICA
# ------------------------------
st.set_page_config(page_title="Evaluación de Riesgos Mineros", layout="wide")
st.title("⛏️ Evaluación de Riesgos en Minería")
st.markdown("### Curso: Seguridad e Higiene Minera - Universidad Nacional de Piura")

# ------------------------------
# CONTRASEÑA
# ------------------------------
PASSWORD = "Riesgo2025"
password = st.text_input("🔒 Ingresa la contraseña para funciones avanzadas:", type="password")
acceso = password == PASSWORD

# ------------------------------
# CARGA DE DATOS
# ------------------------------
@st.cache_data
def cargar_datos():
    return pd.read_excel("riesgos_mineria_simulada.xlsx")

df = cargar_datos()

# ------------------------------
# FILTROS
# ------------------------------
st.sidebar.header("🎛️ Filtros de búsqueda")
areas = st.sidebar.multiselect("Selecciona área(s):", options=df["Área"].unique(), default=df["Área"].unique())
clasificaciones = st.sidebar.multiselect("Selecciona clasificación(es):", options=df["Clasificación"].unique(), default=df["Clasificación"].unique())

df_filtrado = df[df["Área"].isin(areas) & df["Clasificación"].isin(clasificaciones)]

# ------------------------------
# INDICADORES PRINCIPALES
# ------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total de Riesgos", len(df_filtrado))
col2.metric("Riesgos Altos", sum(df_filtrado["Clasificación"] == "Alto"))
col3.metric("Promedio de Severidad", round(df_filtrado["Severidad (1-5)"].mean(), 2))

st.markdown("---")

# ------------------------------
# GRÁFICOS
# ------------------------------
col_g1, col_g2 = st.columns(2)

# 1. Gráfico circular de clasificación
fig_pie = px.pie(df_filtrado, names="Clasificación", title="Distribución de Clasificación de Riesgo", hole=0.4)
col_g1.plotly_chart(fig_pie, use_container_width=True)

# 2. Gráfico de barras: promedio por área
df_area = df_filtrado.groupby("Área")[["Probabilidad (1-5)", "Severidad (1-5)"]].mean().reset_index()
fig_bar = px.bar(df_area, x="Área", y=["Probabilidad (1-5)", "Severidad (1-5)"], 
                 barmode="group", title="Promedio de Probabilidad y Severidad por Área")
col_g2.plotly_chart(fig_bar, use_container_width=True)

# 3. Gráfico de dispersión
st.markdown("### 📊 Mapa de Riesgo: Probabilidad vs Severidad")
fig_scatter = px.scatter(df_filtrado, x="Probabilidad (1-5)", y="Severidad (1-5)", 
                         color="Clasificación", hover_data=["Área", "Actividad", "Peligro"],
                         title="Mapa de Riesgo: Probabilidad vs Severidad")
st.plotly_chart(fig_scatter, use_container_width=True)

# 4. Conteo de riesgos por área
st.markdown("### ⚙️ Cantidad de Riesgos por Área")
fig_area = px.bar(df_filtrado["Área"].value_counts().reset_index(),
                  x="count", y="index", orientation="h",
                  title="Cantidad de Riesgos Detectados por Área")
st.plotly_chart(fig_area, use_container_width=True)

st.markdown("---")

# ------------------------------
# DESCARGA DE DATOS
# ------------------------------
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Riesgos")
    return output.getvalue()

excel_data = convertir_a_excel(df_filtrado)
st.download_button(label="📥 Descargar Datos Filtrados", data=excel_data, file_name="riesgos_filtrados.xlsx")

# ------------------------------
# SUBIDA DE NUEVOS DATOS
# ------------------------------
if acceso:
    st.success("✅ Acceso concedido. Puedes actualizar la base de datos.")
    archivo = st.file_uploader("Sube un nuevo archivo Excel (.xlsx):", type=["xlsx"])
    if archivo:
        nuevo_df = pd.read_excel(archivo)
        nuevo_df.to_excel("riesgos_mineria_simulada.xlsx", index=False)
        st.success("Archivo actualizado correctamente. Recarga la página para ver los cambios.")
else:
    st.info("🔐 Ingresa la contraseña para poder subir nuevos archivos.")
