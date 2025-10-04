import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# -------- Configuración --------
PASSWORD = "mi123contraseña"  # Cambia esta contraseña si quieres
DEFAULT_FILE = "riesgos_mineria_simulada.xlsx"

st.title("Dashboard de Evaluación de Riesgos Minera")

# -------- Autenticación --------
user_input = st.text_input("Ingresa la contraseña para actualizar datos", type="password")

# Cargar Excel por defecto
df = pd.read_excel(DEFAULT_FILE)

# Permitir subir nuevo Excel solo si la contraseña es correcta
if user_input == PASSWORD:
    st.success("Contraseña correcta. Puedes actualizar los datos.")
    uploaded_file = st.file_uploader("Sube un archivo Excel con nuevos datos", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("Datos actualizados correctamente")
else:
    if user_input:
        st.warning("Contraseña incorrecta. Solo puedes ver los datos existentes.")

# -------- Limpieza y normalización de datos --------
df['Área'] = df['Área'].astype(str).str.strip().str.title()          # Primera letra de cada palabra en mayúscula
df['Nivel de riesgo'] = df['Nivel de riesgo'].astype(str).str.strip().str.capitalize()  # Alto, Medio, Bajo

# -------- Filtros --------
st.sidebar.header("Filtros")
area_seleccionada = st.sidebar.multiselect(
    "Selecciona Área(s)",
    options=sorted(df['Área'].unique()),
    default=sorted(df['Área'].unique())
)

nivel_seleccionado = st.sidebar.multiselect(
    "Selecciona Nivel de Riesgo",
    options=sorted(df['Nivel de riesgo'].unique()),
    default=sorted(df['Nivel de riesgo'].unique())
)

# -------- Filtrado del DataFrame --------
df_filtrado = df[
    (df['Área'].isin(area_seleccionada)) &
    (df['Nivel de riesgo'].isin(nivel_seleccionado))
]

# -------- Mostrar tabla filtrada --------
st.subheader("Datos Filtrados")
st.dataframe(df_filtrado)

# -------- Gráfico de distribución --------
if not df_filtrado.empty and "Nivel de riesgo" in df_filtrado.columns:
    fig = px.histogram(
        df_filtrado,
        x="Nivel de riesgo",
        color="Nivel de riesgo",
        title="Distribución de Niveles de Riesgo",
        text_auto=True
    )
    st.plotly_chart(fig)
else:
    st.info("No hay datos para mostrar en el gráfico.")

# -------- Función para descargar Excel --------
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Datos Filtrados")
    processed_data = output.getvalue()
    return processed_data

st.subheader("Descargar Datos Filtrados")
excel_data = convertir_a_excel(df_filtrado)
st.download_button(
    label="Descargar Excel",
    data=excel_data,
    file_name="datos_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
