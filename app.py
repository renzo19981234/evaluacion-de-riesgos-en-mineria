# --- NUEVO BLOQUE: Indicadores y gráfico circular ---

# Calcular promedio del nivel de riesgo (numérico)
promedio_riesgo = df_filtrado["Nivel de riesgo"].mean()

# Determinar clasificación cualitativa
if promedio_riesgo >= 15:
    clasificacion_global = "ALTO"
    color = "red"
elif promedio_riesgo >= 8:
    clasificacion_global = "MEDIO"
    color = "orange"
else:
    clasificacion_global = "BAJO"
    color = "green"

# Mostrar resultado global
st.markdown(f"### 🔍 Resultados del Área: **{area_seleccionada}**")
st.metric("Nivel de Riesgo Promedio", f"{promedio_riesgo:.2f}")
st.markdown(
    f"<h4 style='color:{color};'>Clasificación Global: {clasificacion_global}</h4>",
    unsafe_allow_html=True
)

# --- Gráfico circular por área y nivel de riesgo ---
st.markdown("### 📊 Distribución de Riesgos por Área")

# Agrupar los datos para el gráfico circular
df_pie = df.groupby("Área")["Nivel de riesgo"].mean().reset_index()

fig_pie = px.pie(
    df_pie,
    names="Área",
    values="Nivel de riesgo",
    title="Porcentaje de Nivel de Riesgo por Área",
    color_discrete_sequence=px.colors.sequential.RdYlGn_r
)

st.plotly_chart(fig_pie)
