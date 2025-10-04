import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título principal
st.title("Evaluación de Riesgos en Minería ⛏️")

# Cargar el archivo Excel
try:
    df = pd.read_excel("riesgos_mineria_simulada.xlsx")
except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo 'riesgos_mineria_simulada.xlsx'. Sube uno nuevo para continuar.")
    uploaded = st.file_uploader("Sube tu archivo Excel con los datos de riesgos", type=["xlsx"])
    if uploaded:
        df = pd.read_excel(uploaded)
        st.success("✅ Archivo cargado correctamente.")
    else:
        st.stop()

# Verificar que el archivo tiene las columnas necesarias
if not {"Área", "Nivel de Riesgo", "Riesgo Cuantificado"}.issubset(df.columns):
    st.error("⚠️ El archivo no tiene las columnas requeridas: 'Área', 'Nivel de Riesgo', 'Riesgo Cuantificado'.")
    st.stop()

# Sección de autenticación para edición de datos
st.sidebar.subheader("🔐 Acceso restringido")
password = st.sidebar.text_input("Ingresa la contraseña", type="password")

if password == "Riesgo2025":
    st.sidebar.success("Acceso concedido ✅")
    uploaded_file = st.sidebar.file_uploader("📤 Subir nuevo archivo Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.to_excel("riesgos_mineria_simulada.xlsx", index=False)
        st.sidebar.success("✅ Archivo reemplazado exitosamente.")
else:
    if password != "":
        st.sidebar.error("Contraseña incorrecta ❌")

# Seleccionar el área
area_seleccionada = st.selectbox("Selecciona un área para analizar:", sorted(df["Área"].unique()))

# Filtrar datos del área seleccionada
df_area = df[df["Área"] == area_seleccionada]

if df_area.empty:
    st.warning("No hay datos para esta área.")
    st.stop()

# Calcular el nivel de riesgo promedio
riesgo_promedio = df_area["Riesgo Cuantificado"].mean()

# Clasificar el nivel de riesgo
if riesgo_promedio < 4:
    nivel = "Bajo 🟢"
elif 4 <= riesgo_promedio < 7:
    nivel = "Medio 🟡"
else:
    nivel = "Alto 🔴"

# Mostrar resultados
st.subheader(f"📊 Resultados para el área: {area_seleccionada}")
st.metric(label="Nivel de Riesgo Cualitativo", value=nivel)
st.metric(label="Nivel de Riesgo Cuantificado", value=round(riesgo_promedio, 2))

# Crear gráfico circular con los porcentajes de riesgo por área
st.subheader("Distribución de Riesgos por Área (%)")

fig, ax = plt.subplots()
porcentajes = df.groupby("Área")["Riesgo Cuantificado"].mean()
ax.pie(porcentajes, labels=porcentajes.index, autopct='%1.1f%%', startangle=90)
ax.axis("equal")  # Hace que el gráfico sea un círculo perfecto
st.pyplot(fig)

# Mostrar tabla de datos del área seleccionada
st.subheader("📋 Datos del Área Seleccionada")
st.dataframe(df_area)
