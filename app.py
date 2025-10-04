import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------
st.set_page_config(page_title="Evaluación de Riesgos en Minería", layout="wide")

# -----------------------
# AUTENTICACIÓN SIMPLE
# -----------------------
st.title("🔒 Evaluación de Riesgos en Minería")

password = st.text_input("Ingrese la contraseña para acceder:", type="password")

if password != "Renzo2025":
    st.warning("Ingrese la contraseña correcta para continuar.")
    st.stop()

st.success("Acceso concedido ✅")

# -----------------------
# CARGA DE DATOS
# -----------------------
try:
    df = pd.read_excel("riesgos_mineria_simulada.xlsx")
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'riesgos_mineria_simulada.xlsx'. Asegúrate de haberlo subido al repositorio.")
    st.stop()

# Mostrar vista previa
st.subheader("Vista previa de los datos")
st.dataframe(df.head())

# -----------------------
# SELECCIÓN DE ÁREA
# -----------------------
areas = df["Área"].unique()
area_seleccionada = st.selectbox("Seleccione un área para evaluar:", areas)

df_filtrado = df[df["Área"] == area_seleccionada]

# -----------------------
# CÁLCULO DEL NIVEL DE RIESGO
# -----------------------
nivel_promedio = df_filtrado["Nivel de Riesgo Cuantificado"].mean()

if nivel_promedio < 3:
    nivel_texto = "Bajo"
elif 3 <= nivel_promedio < 6:
    nivel_texto = "Medio"
else:
    nivel_texto = "Alto"

st.markdown(f"### 📊 Nivel de riesgo para el área **{area_seleccionada}**:")
st.metric(label="Nivel de Riesgo", value=f"{nivel_texto}", delta=f"{nivel_promedio:.2f}")

# -----------------------
# GRÁFICO CIRCULAR DE PORCENTAJES
# -----------------------
st.subheader("Distribución porcentual de riesgo por área")

riesgos_por_area = df.groupby("Área")["Nivel de Riesgo Cuantificado"].mean()
porcentajes = (riesgos_por_area / riesgos_por_area.sum()) * 100

fig, ax = plt.subplots()
ax.pie(porcentajes, labels=porcentajes.index, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)

# -----------------------
# DESCARGA DE DATOS
# -----------------------
st.download_button(
    label="📥 Descargar datos filtrados",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name=f"riesgos_{area_seleccionada}.csv",
    mime="text/csv"
)
