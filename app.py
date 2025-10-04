# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import unicodedata

# -----------------------
#  CONFIG
# -----------------------
st.set_page_config(page_title="Evaluación de Riesgos Mineros", layout="wide")
st.title("⛏️ Evaluación de Riesgos - Seguridad e Higiene Minera")

# Cambia la contraseña aquí si quieres
PASSWORD = "Riesgo2025"
DEFAULT_FILE = "riesgos_mineria_simulada.xlsx"

# -----------------------
#  UTIL: normalizar texto/columnas
# -----------------------
def normalize_text(s: str) -> str:
    s = str(s)
    s = s.strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    # reemplaza caracteres problemáticos por guión bajo
    for ch in [' ', '-', '/', '\\', '(', ')', '.', ',']:
        s = s.replace(ch, '_')
    # compacta guiones bajos dobles
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")

def find_column(df_cols_normalized: dict, keywords):
    """Devuelve la columna original cuyo nombre normalizado contiene alguno de keywords (lista)."""
    for k in keywords:
        for norm, orig in df_cols_normalized.items():
            if k in norm:
                return orig
    return None

# -----------------------
#  SIDEBAR: contraseña y (opcional) carga
# -----------------------
st.sidebar.header("🔐 Administrador")
pw = st.sidebar.text_input("Contraseña (solo para subir archivo):", type="password")
is_admin = (pw == PASSWORD)

if is_admin:
    st.sidebar.success("Acceso administrador activado")
    uploaded = st.sidebar.file_uploader("Subir Excel (.xlsx) para usar ahora (opcional):", type=["xlsx"])
else:
    st.sidebar.info("Introduce la contraseña para habilitar subida de archivo")
    uploaded = None

# -----------------------
#  CARGAR DATOS (archivo por defecto o subido)
# -----------------------
def load_from_uploaded_or_default(uploaded_file, default_file):
    try:
        if uploaded_file is not None:
            df0 = pd.read_excel(uploaded_file)
        else:
            df0 = pd.read_excel(default_file)
        return df0
    except FileNotFoundError:
        st.error(f"❌ No se encontró '{default_file}'. Sube el archivo en la barra lateral (si tienes contraseña) o sube manualmente al repo.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error al leer el Excel: {e}")
        st.stop()

df_raw = load_from_uploaded_or_default(uploaded, DEFAULT_FILE)

# -----------------------
#  NORMALIZAR NOMBRES DE COLUMNAS
# -----------------------
orig_cols = list(df_raw.columns)
normalized_map = {normalize_text(c): c for c in orig_cols}  # norm -> original

# mostrar columnas detectadas (útil)
with st.expander("🔎 Columnas detectadas en el Excel (original)"):
    st.write(orig_cols)

# -----------------------
#  MAPA DE COLUMNAS (buscar las columnas esperadas)
# -----------------------
area_col = find_column(normalized_map, ["area", "areal", "are"])
actividad_col = find_column(normalized_map, ["actividad", "actividad_"])
peligro_col = find_column(normalized_map, ["peligro"])
prob_col = find_column(normalized_map, ["probabil", "prob"])
sev_col = find_column(normalized_map, ["sever", "gravedad"])
nivel_col = find_column(normalized_map, ["nivel", "nivel_de_riesgo", "nivel_riesgo"])
clas_col = find_column(normalized_map, ["clasif", "clasificacion", "clasific"])

# -----------------------
#  CONSTRUIR DF ESTÁNDAR
# -----------------------
df = df_raw.copy()

# Limpieza básica de columnas originales: quitar espacios de encabezados (no cambiar datos)
df.columns = [col.strip() for col in df.columns]

# AREA (obligatoria)
if area_col:
    df['Área'] = df[area_col].astype(str).str.strip().str.title()
else:
    st.error("❌ No fue posible detectar la columna 'Área' en el Excel. Revisa el nombre de la columna.")
    st.stop()

# Actividad/Peligro opcional
if actividad_col:
    df['Actividad'] = df[actividad_col].astype(str).str.strip()
if peligro_col:
    df['Peligro'] = df[peligro_col].astype(str).str.strip()

# Probabilidad / Severidad (intentar detectar y convertir)
if prob_col:
    df['Probabilidad'] = pd.to_numeric(df[prob_col], errors='coerce')
else:
    df['Probabilidad'] = pd.NA

if sev_col:
    df['Severidad'] = pd.to_numeric(df[sev_col], errors='coerce')
else:
    df['Severidad'] = pd.NA

# Nivel de riesgo numérico (si existe usarlo; sino calcular Prob x Sev)
if nivel_col:
    df['Nivel_de_riesgo'] = pd.to_numeric(df[nivel_col], errors='coerce')
else:
    if df['Probabilidad'].notna().any() and df['Severidad'].notna().any():
        df['Nivel_de_riesgo'] = df['Probabilidad'] * df['Severidad']
    else:
        # si no hay manera de obtener numérico, lo dejamos NaN y avisamos más abajo
        df['Nivel_de_riesgo'] = pd.NA

# Clasificación textual (si existe usar; si no, derivar por umbral)
if clas_col:
    df['Clasificación'] = df[clas_col].astype(str).str.strip().str.title()
else:
    # crear clasificación por fila según Nivel_de_riesgo
    def cls_from_value(v):
        try:
            v = float(v)
        except:
            return "Desconocido"
        if v <= 4:
            return "Bajo"
        elif v <= 12:
            return "Medio"
        else:
            return "Alto"
    df['Clasificación'] = df['Nivel_de_riesgo'].apply(cls_from_value)

# ya tenemos: Área, Probabilidad, Severidad, Nivel_de_riesgo, Clasificación
# renombrar la columna para visualización si quieres (no obligatorio)
# df.rename(columns={'Nivel_de_riesgo':'Nivel de riesgo (cuantificado)'}, inplace=True)

# -----------------------
#  AVISOS si falta info numérica
# -----------------------
if df['Nivel_de_riesgo'].isna().all():
    st.warning("⚠️ No se detectó un valor numérico de 'Nivel de riesgo' ni suficientes columnas de Probabilidad/Severidad para calcularlo. Algunos gráficos numéricos estarán deshabilitados.")

# -----------------------
#  INTERFAZ: selección y métricas
# -----------------------
st.subheader("📋 Vista de datos")
st.dataframe(df.head(30))

# selector de área (opción 'Todas' para ver agregados)
areas = ["Todas las áreas"] + sorted(df['Área'].dropna().unique().tolist())
area_sel = st.selectbox("Selecciona un área (o 'Todas las áreas'):", areas)

if area_sel == "Todas las áreas":
    df_f = df.copy()
else:
    df_f = df[df['Área'] == area_sel].copy()

# Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Registros mostrados", len(df_f))
if df_f['Nivel_de_riesgo'].notna().any():
    col2.metric("Promedio nivel de riesgo", f"{df_f['Nivel_de_riesgo'].mean():.2f}")
else:
    col2.metric("Promedio nivel de riesgo", "N/D")
col3.metric("Riesgos Alto (conteo)", int((df_f['Clasificación'] == "Alto").sum()))

st.markdown("---")

# -----------------------
#  GRÁFICOS
# -----------------------
# 1) Pie chart: % del nivel de riesgo promedio por área (usa df global)
if df['Nivel_de_riesgo'].notna().any():
    df_area_mean = df.groupby('Área')['Nivel_de_riesgo'].mean().reset_index()
    fig_pie = px.pie(df_area_mean, names='Área', values='Nivel_de_riesgo',
                     title="Porcentaje del nivel de riesgo promedio por área", hole=0.35)
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("No hay datos numéricos para el gráfico circular por áreas.")

# 2) Bar: promedio (Probabilidad y Severidad) por área si existen
if df['Probabilidad'].notna().any() and df['Severidad'].notna().any():
    df_area_avg = df.groupby('Área')[['Probabilidad', 'Severidad']].mean().reset_index()
    fig_bar = px.bar(df_area_avg, x='Área', y=['Probabilidad', 'Severidad'],
                     barmode='group', title="Promedio de Probabilidad y Severidad por Área")
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Faltan Probabilidad y/o Severidad numéricas para gráfico de promedios por área.")

# 3) Scatter: Probabilidad vs Severidad (solo si hay datos)
if df_f['Probabilidad'].notna().any() and df_f['Severidad'].notna().any():
    st.subheader("🔎 Mapa de riesgo: Probabilidad vs Severidad")
    fig_sc = px.scatter(df_f, x='Probabilidad', y='Severidad', color='Clasificación',
                        hover_data=['Área', 'Actividad', 'Peligro'],
                        title="Probabilidad vs Severidad (registros mostrados)")
    st.plotly_chart(fig_sc, use_container_width=True)
else:
    st.info("No hay datos suficientes de Probabilidad/Severidad para el mapa de riesgo.")

# 4) Conteo por clasificación (barras) dentro del filtro
st.subheader("📊 Conteo por Clasificación (registros mostrados)")
conteo = df_f['Clasificación'].value_counts().reindex(['Alto','Medio','Bajo']).fillna(0).reset_index()
conteo.columns = ['Clasificación','Cantidad']
fig_count = px.bar(conteo, x='Clasificación', y='Cantidad', text='Cantidad',
                   title="Conteo por Clasificación")
st.plotly_chart(fig_count, use_container_width=True)

st.markdown("---")

# -----------------------
#  DESCARGA DE DATOS FILTRADOS
# -----------------------
def df_to_excel_bytes(df_):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df_.to_excel(writer, index=False, sheet_name='Datos')
    return out.getvalue()

st.download_button("📥 Descargar datos mostrados (Excel)",
                   data=df_to_excel_bytes(df_f),
                   file_name=f"riesgos_filtrados_{area_sel.replace(' ','_')}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -----------------------
#  UPLOAD / REEMPLAZO (solo admin)
# -----------------------
st.sidebar.markdown("---")
if is_admin:
    st.sidebar.info("Puedes subir un nuevo Excel para usarlo en esta sesión.")
    file_replace = st.sidebar.file_uploader("Subir Excel para usar ahora (reemplaza temporalmente):", type=["xlsx"])
    if file_replace is not None:
        st.sidebar.success("📥 Archivo cargado para la sesión. Refresca para aplicar.")
        # Nota: en Streamlit Cloud el archivo guardado localmente no es persistente entre despliegues.
else:
    st.sidebar.write("Ingresa la contraseña correcta para habilitar la carga de archivos.")

# -----------------------
#  FIN
# -----------------------
st.info("Si algo no aparece, revisa el nombre y formato de las columnas en tu Excel. Los nombres aceptados incluyen: Área, Actividad, Peligro, Probabilidad (o Probabilidad (1-5)), Gravedad/Severidad (1-5), Nivel de riesgo, Clasificación.")
