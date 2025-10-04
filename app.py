import streamlit as st
import pandas as pd

# Intentar usar plotly si está disponible, si no, usar matplotlib
try:
    import plotly.express as px
    usar_plotly = True
except ImportError:
    import matplotlib.pyplot as plt
    usar_plotly = False

# --- Seguridad básica ---
st.title("🛡️ Evaluación de Riesgos en Minería")
password = st.text_input("🔒 Ingrese la contraseña para acceder:", type="password")

if password != "Riesgo2025":
    st.warning("Ingrese la contraseña correcta para continuar.")
    st.stop()

# --- Cargar datos ---
try:
    df = pd.read_excel("riesgos_mineria_simulada.xlsx")
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'riesgos_mineria_simulada.xlsx'.")
    st.stop()

st.success("✅ Datos cargados correctamente.")
st.write("### Vista general de los datos:")
st.dataframe(df)

# --- Selección de área ---
areas = df["Área"].unique().tolist()
area_seleccionada = st.selectbox("Seleccione un área para analizar:", areas)

df_filtrado = df[df["Área"] == area_seleccionada]

# --- Mostrar indicadores clave ---
st.subheader(f"📊 Indicadores del área: {area_seleccionada}")

riesgos_totales = len(df_filtrado)
riesgo_promedio = df_filtrado["Nivel de riesgo"].mean()
riesgo_maximo = df_filtrado["Nivel de riesgo"].max()

col1, col2, col3 = st.columns(3)
col1.metric("Total de riesgos detectados", riesgos_totales)
col2.metric("Nivel de riesgo promedio", round(riesgo_promedio, 2))
col3.metric("Nivel de riesgo máximo", riesgo_maximo)

# --- Gráfico circular de riesgos por clasificación ---
st.subheader("🌀 Distribución de riesgos por clasificación")

conteo = df_filtrado["Clasificación"].value_counts().reset_index()
conteo.columns = ["Clasificación", "Cantidad"]

if usar_plotly:
    fig = px.pie(conteo, values="Cantidad", names="Clasificación", title="Distribución de Clasificación de Riesgos")
    st.plotly_chart(fig)
else:
    fig, ax = plt.subplots()
    ax.pie(conteo["Cantidad"], labels=conteo["Clasificación"], autopct="%1.1f%%")
    ax.set_title("Distribución de Clasificación de Riesgos")
    st.pyplot(fig)

# --- Gráfico de nivel de riesgo promedio por área ---
st.subheader("📈 Comparativa de riesgo promedio por área")

riesgo_por_area = df.groupby("Área")["Nivel de riesgo"].mean().reset_index()

if usar_plotly:
    fig_area = px.bar(riesgo_por_area, x="Área", y="Nivel de riesgo",
                      title="Nivel de Riesgo Promedio por Área",
                      color="Nivel de riesgo", color_continuous_scale="viridis")
    st.plotly_chart(fig_area)
else:
    fig, ax = plt.subplots()
    ax.bar(riesgo_por_area["Área"], riesgo_por_area["Nivel de riesgo"], color="orange")
    ax.set_xlabel("Área")
    ax.set_ylabel("Nivel de riesgo promedio")
    ax.set_title("Nivel de Riesgo Promedio por Área")
    st.pyplot(fig)

# --- Descarga de datos filtrados ---
st.subheader("📥 Descargar datos del área seleccionada")

@st.cache_data
def convertir_a_excel(df):
    from io import BytesIO
    import openpyxl
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos Filtrados')
    return output.getvalue()

excel_data = convertir_a_excel(df_filtrado)
st.download_button(
    label="📂 Descargar Excel del área seleccionada",
    data=excel_data,
    file_name=f"riesgos_{area_seleccionada}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
