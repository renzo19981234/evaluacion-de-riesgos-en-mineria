import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- Título ---
st.title("Evaluación de Riesgos por Área - Mina Simulada 🪨")

# --- Cargar datos ---
df = pd.read_excel("riesgos_mineria_simulada.xlsx")

# --- Calcular Nivel de Riesgo y Clasificación ---
df["Nivel de riesgo"] = df["Probabilidad (1-5)"] * df["Severidad (1-5)"]

def clasificar_riesgo(valor):
    if valor <= 4:
        return "Bajo"
    elif valor <= 12:
        return "Medio"
    else:
        return "Alto"

df["Categoría de Riesgo"] = df["Nivel de riesgo"].apply(clasificar_riesgo)

# --- Mostrar datos completos ---
st.subheader("📋 Base de Datos de Riesgos")
st.dataframe(df)

# --- Filtro por Área ---
area = st.selectbox("Selecciona el área:", df["Área"].unique())
df_filtrado = df[df["Área"] == area]

st.subheader(f"Riesgos detectados en el área: {area}")
st.dataframe(df_filtrado)

# --- Gráfico de niveles de riesgo ---
fig = px.histogram(
    df_filtrado,
    x="Categoría de Riesgo",
    color="Categoría de Riesgo",
    color_discrete_map={"Bajo": "green", "Medio": "yellow", "Alto": "red"},
    category_orders={"Categoría de Riesgo": ["Bajo", "Medio", "Alto"]},
    title="Distribución de niveles de riesgo"
)
st.plotly_chart(fig)

# --- Indicadores clave mejorados ---
st.subheader("📊 Indicadores Clave")

# Número total de riesgos
st.metric("Número total de riesgos", len(df_filtrado))

if not df_filtrado.empty:
    # Riesgo más frecuente
    st.metric("Riesgo más frecuente", df_filtrado["Categoría de Riesgo"].mode()[0])
    # Nivel de riesgo promedio
    riesgo_promedio = round(df_filtrado["Nivel de riesgo"].mean(), 2)
    st.metric("Nivel de riesgo promedio", riesgo_promedio)
    
    # Porcentaje de riesgos por categoría
    porcentaje = df_filtrado["Categoría de Riesgo"].value_counts(normalize=True) * 100
    bajo = round(porcentaje.get("Bajo", 0), 1)
    medio = round(porcentaje.get("Medio", 0), 1)
    alto = round(porcentaje.get("Alto", 0), 1)
    
    st.write(f"Porcentaje de riesgos: 🟢 Bajo: {bajo}% | 🟡 Medio: {medio}% | 🔴 Alto: {alto}%")
else:
    st.metric("Riesgo más frecuente", "N/A")
    st.metric("Nivel de riesgo promedio", "N/A")
    st.write("Porcentaje de riesgos: 🟢 Bajo: 0% | 🟡 Medio: 0% | 🔴 Alto: 0%")

# --- Botón para descargar Excel ---
def convertir_a_excel(df):
    output = io.BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

excel_data = convertir_a_excel(df_filtrado)

st.download_button(
    label="📥 Descargar datos filtrados",
    data=excel_data,
    file_name=f"riesgos_{area}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
