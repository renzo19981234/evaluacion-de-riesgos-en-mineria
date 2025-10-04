import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# -------- Configuración --------
PASSWORD = "mi123contraseña"
DEFAULT_FILE = "riesgos_mineria_simulada.xlsx"

st.title("Dashboard de Evaluación de Riesgos Minera")

# -------- Autenticación --------
user_input = st.text_input("Ingresa la contraseña para actualizar datos", type="password")

# Cargar Excel por defecto
df = pd.read_excel(DEFAULT_FILE)

# Subir nuevo Excel solo si la contraseña es correcta
if user_input == PASSWORD:
    st.success("Contraseña correcta. Puedes actualizar los datos.")
    uploaded_file = st.file_uploader("Sube un archivo Excel con nuevos datos", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("Datos actualizados correctamente")
else:
    if user_input:
        st.warning("Contraseña incorrecta. Solo puedes ver los datos existentes.")

# -------- Normalización de datos --------
def normalizar_texto(columna):
    return columna.astype(str).str.strip().str.title()

df['Área'] = normalizar_texto(df['Área'])
df['Nivel de riesgo'] = normalizar_texto(df['Nivel de riesgo'])

# -------- Selección de Área --------
area_seleccionada = st.selectbox(
    "Selecciona un Área",
    options=sorted(df['Área'].unique())
)

# -------- Filtrado del DataFrame --------
df_filtrado = df[df['Área'] == area_seleccionada]

# -------- Mostrar tabla filtrada --------
st.subheader(f"Riesgos detectados en el área: {area_seleccionada}")
st.dataframe(df_filtrado)

# -------- Gráfico de barras --------
if not df_filtrado.empty and "Nivel de riesgo" in df_filtrado.columns:
    fig = px.histogram(
        df_filtrado,
        x="Nivel de riesgo",
        color="Nivel de riesgo",
        title=f"Distribución de Niveles de Riesgo en {area_seleccionada}",
        text_auto=True
    )
    st.plotly_chart(fig)
else:
    st.info("No hay datos para mostrar en el gráfico.")

# -------- Función para descargar Excel filtrado --------
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Datos Filtrados")
    return output.getvalue()

st.subheader("Descargar Excel filtrado por Área")
excel_data = convertir_a_excel(df_filtrado)
st.download_button(
    label="Descargar Excel",
    data=excel_data,
    file_name=f"datos_{area_seleccionada}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
