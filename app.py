import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import unicodedata

# ------------------------------
# Helpers
# ------------------------------
def normalize_name(s):
    s = str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    for ch in [' ', '-', '(', ')', '/', '\\', '.']:
        s = s.replace(ch, '_')
    s = "_".join([p for p in s.split('_') if p])
    return s

def find_any_column(normalized_cols, keywords_any=None, keywords_all=None):
    # keywords_any: any keyword match suffices
    # keywords_all: require all keywords to be present
    if keywords_all:
        for ncol, orig in normalized_cols.items():
            if all(k in ncol for k in keywords_all):
                return orig
    if keywords_any:
        for ncol, orig in normalized_cols.items():
            for k in keywords_any:
                if k in ncol:
                    return orig
    return None

def classify_row(val):
    try:
        v = float(val)
    except:
        return "Desconocido"
    if v <= 4:
        return "Bajo"
    elif v <= 12:
        return "Medio"
    else:
        return "Alto"

def classify_average(v):
    # umbrales para promedio (ajustables)
    try:
        v = float(v)
    except:
        return "Desconocido"
    if v >= 15:
        return "Alto"
    elif v >= 8:
        return "Medio"
    else:
        return "Bajo"

# ------------------------------
# Página y contraseña
# ------------------------------
st.set_page_config(page_title="Evaluación de Riesgos Mineros", layout="wide")
st.title("🛠️ Evaluación de Riesgos - Seguridad e Higiene Minera")

PASSWORD = "Riesgo2025"  # contraseña actual
pw_input = st.sidebar.text_input("🔒 Contraseña (para subir datos):", type="password")
acceso = (pw_input == PASSWORD)

# ------------------------------
# Cargar datos (archivo por defecto o subido)
# ------------------------------
FILE_DEFAULT = "riesgos_mineria_simulada.xlsx"

uploaded = st.sidebar.file_uploader("Si deseas, sube un Excel (.xlsx) para usarlo ahora (opcional):", type=["xlsx"])
if uploaded is not None:
    try:
        df = pd.read_excel(uploaded)
        st.sidebar.success("Archivo cargado desde el uploader.")
    except Exception as e:
        st.sidebar.error(f"Error al leer el Excel subido: {e}")
        st.stop()
else:
    try:
        df = pd.read_excel(FILE_DEFAULT)
    except FileNotFoundError:
        st.error(f"❌ No se encontró '{FILE_DEFAULT}' en el proyecto. Sube el archivo o cámbiale el nombre.")
        st.stop()
    except Exception as e:
        st.error(f"Error leyendo '{FILE_DEFAULT}': {e}")
        st.stop()

# ------------------------------
# Detectar columnas (robusto)
# ------------------------------
orig_cols = list(df.columns)
normalized_cols = {normalize_name(c): c for c in orig_cols}
st.sidebar.markdown("**Columnas detectadas (original)**")
st.sidebar.write(orig_cols)

# buscar columnas
area_col = find_any_column(normalized_cols, keywords_any=["area", "area_"])
prob_col = find_any_column(normalized_cols, keywords_any=["probabil", "prob_","prob"])
sev_col = find_any_column(normalized_cols, keywords_any=["sever", "sev_","severidad"])
nivel_col = None
# preferir columna que contenga 'nivel' y 'riesgo'
for ncol, orig in normalized_cols.items():
    if "nivel" in ncol and "riesgo" in ncol:
        nivel_col = orig
        break
if nivel_col is None:
    nivel_col = find_any_column(normalized_cols, keywords_any=["nivel", "nivel_"])

riesgo_cuant_col = find_any_column(normalized_cols, keywords_any=["cuant", "cuanti", "quant"])
clas_col = find_any_column(normalized_cols, keywords_any=["clasif", "clasificacion", "clas"])

# mostrar mapeo detectado
st.sidebar.markdown("**Mapeo automático de columnas**")
st.sidebar.write({
    "area_col": area_col,
    "prob_col": prob_col,
    "sev_col": sev_col,
    "nivel_col": nivel_col,
    "riesgo_cuant_col": riesgo_cuant_col,
    "clas_col": clas_col
})

# ------------------------------
# Construir DataFrame estándar
# ------------------------------
df2 = df.copy()

# AREA
if area_col:
    df2["Área"] = df[area_col].astype(str).str.strip().str.title()
else:
    st.error("❌ No se encontró una columna de 'Área' en el Excel. Revisa los nombres de columna.")
    st.stop()

# PROBABILIDAD y SEVERIDAD (si existen)
if prob_col and sev_col:
    df2["Probabilidad"] = pd.to_numeric(df[prob_col], errors="coerce")
    df2["Severidad"] = pd.to_numeric(df[sev_col], errors="coerce")
else:
    # si no existen, intentaremos continuar con lo que hay
    if not prob_col or not sev_col:
        st.info("Nota: no se encontraron columnas de Probabilidad y/o Severidad. Si existen con otro nombre, renómbralas o sube un archivo con esas columnas.")
    df2["Probabilidad"] = pd.NA
    df2["Severidad"] = pd.NA

# NIVEL / RIESGO CUANTIFICADO
if riesgo_cuant_col:
    df2["Riesgo_Cuantificado"] = pd.to_numeric(df[riesgo_cuant_col], errors="coerce")
elif nivel_col:
    df2["Riesgo_Cuantificado"] = pd.to_numeric(df[nivel_col], errors="coerce")
elif (not df2["Probabilidad"].isna().all()) and (not df2["Severidad"].isna().all()):
    df2["Riesgo_Cuantificado"] = df2["Probabilidad"] * df2["Severidad"]
else:
    # ningún dato numérico disponible
    st.error("❌ No se pudo determinar la columna numérica de riesgo. Necesitas una columna con nivel de riesgo o Probabilidad y Severidad para calcularlo.")
    st.stop()

# CLASIFICACIÓN (si existe) o crearla
if clas_col:
    df2["Clasificación"] = df[clas_col].astype(str).str.strip().str.title()
else:
    df2["Clasificación"] = df2["Riesgo_Cuantificado"].apply(classify_row)

# Asegurar valores numéricos correctos
df2["Riesgo_Cuantificado"] = pd.to_numeric(df2["Riesgo_Cuantificado"], errors="coerce")

# ------------------------------
# Mostrar DataFrame y columnas procesadas (útil para depuración)
# ------------------------------
st.subheader("📋 Datos (procesados)")
st.write("Columnas originales:", orig_cols)
st.dataframe(df2.head(50))

# ------------------------------
# Selección de área y filtrado
# ------------------------------
areas = sorted(df2["Área"].dropna().unique().tolist())
area_seleccionada = st.selectbox("Selecciona un área:", options=areas)
df_filtrado = df2[df2["Área"] == area_seleccionada]

if df_filtrado.empty:
    st.warning("No hay registros para el área seleccionada.")
else:
    # ------------------------------
    # Indicadores por área
    # ------------------------------
    promedio = df_filtrado["Riesgo_Cuantificado"].mean()
    clasific_prom = classify_average(promedio)
    color = {"Alto":"red","Medio":"orange","Bajo":"green"}.get(clasific_prom, "black")

    st.markdown(f"### 🔍 Resultados para: **{area_seleccionada}**")
    st.metric("Nivel de Riesgo (promedio)", f"{promedio:.2f}" if pd.notna(promedio) else "N/A")
    st.markdown(f"<h4 style='color:{color};'>Clasificación global: {clasific_prom}</h4>", unsafe_allow_html=True)

    # Tabla del área
    st.subheader("Registros del área")
    st.dataframe(df_filtrado)

    # ------------------------------
    # Gráfico circular (porcentaje de riesgo por área, basado en promedio)
    # ------------------------------
    st.subheader("📊 Porcentaje del nivel de riesgo por área (promedio)")
    df_pie = df2.groupby("Área")["Riesgo_Cuantificado"].mean().reset_index()
    fig_pie = px.pie(df_pie, names="Área", values="Riesgo_Cuantificado",
                     title="Porcentaje del nivel de riesgo por área", hole=0.3)
    st.plotly_chart(fig_pie, use_container_width=True)

    # ------------------------------
    # Gráfico de barras: conteo por clasificación dentro del área
    # ------------------------------
    st.subheader("📈 Conteo por Clasificación en el área seleccionada")
    conteo = df_filtrado["Clasificación"].value_counts().reindex(["Alto","Medio","Bajo"]).fillna(0).reset_index()
    conteo.columns = ["Clasificación","Cantidad"]
    fig_bar = px.bar(conteo, x="Clasificación", y="Cantidad", title=f"Conteo por clasificación en {area_seleccionada}", text_auto=True)
    st.plotly_chart(fig_bar, use_container_width=True)

    # ------------------------------
    # Scatter Probabilidad vs Severidad (si existen)
    # ------------------------------
    if df_filtrado["Probabilidad"].notna().any() and df_filtrado["Severidad"].notna().any():
        st.subheader("🔎 Mapa de riesgo: Probabilidad vs Severidad (registros del área)")
        fig_scatter = px.scatter(df_filtrado, x="Probabilidad", y="Severidad",
                                 color="Clasificación", hover_data=df_filtrado.columns.tolist(),
                                 title="Probabilidad vs Severidad")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ------------------------------
    # Descargar datos filtrados
    # ------------------------------
    def convertir_a_excel_bytes(df_):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_.to_excel(writer, index=False, sheet_name="Datos")
        return output.getvalue()

    excel_bytes = convertir_a_excel_bytes(df_filtrado)
    st.download_button("📥 Descargar datos del área (Excel)", data=excel_bytes,
                       file_name=f"riesgos_{area_seleccionada}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ------------------------------
# Subida de archivo si tienes acceso
# ------------------------------
st.sidebar.markdown("---")
if acceso:
    st.sidebar.success("Acceso admin: puedes subir y reemplazar el Excel.")
    file_replace = st.sidebar.file_uploader("Subir Excel para reemplazar la base (se sobrescribirá):", type=["xlsx"])
    if file_replace is not None:
        # Nota: en Streamlit Cloud los archivos escritos localmente no son persistentes; 
        # generalmente es mejor pedir que subas a GitHub o a Google Drive si quieres persistencia real.
        try:
            new_df = pd.read_excel(file_replace)
            # Guardarlo localmente solo para la sesión actual (no persistente en Cloud)
            new_df.to_excel(FILE_DEFAULT, index=False)
            st.sidebar.success("Archivo reemplazado en la sesión. Refresca la página para usarlo.")
        except Exception as e:
            st.sidebar.error(f"Error al procesar el archivo subido: {e}")
else:
    st.sidebar.info("Introduce la contraseña para activar la carga de archivos.")
