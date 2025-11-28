import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit.components.v1 as components
from PIL import Image
import os
import time

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Iberdrola - Live",
    layout="wide",
    page_icon="⚡"
)

# --- RUTAS DE ARCHIVOS (Logo y Audio) ---
carpeta_actual = os.path.dirname(os.path.abspath(__file__))

# 1. Logo
ruta_completa_logo = os.path.join(carpeta_actual, "Iberdrola-Embleme-650x366.png")

# 2. Audio (Asegúrate de que la extensión sea la correcta: .mp3, .wav, etc.)
ruta_completa_audio = os.path.join(carpeta_actual, "iberdrola song.mp3") 

try:
    logo_img = Image.open(ruta_completa_logo)
except FileNotFoundError:
    logo_img = None 

# --- CSS ESTILOS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #E8F5E9 0%, #E3F2FD 100%);
        background-attachment: fixed;
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-right: 1px solid #A9DFBF;
    }
    .css-card {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 25px;
    }
    h1 { color: #004B8D !important; font-weight: 800; }
    h3 { color: #2E86C1 !important; font-weight: 700; }
    
    div[data-testid="stMetricValue"] {
        transition: color 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- GENERACIÓN DE DATOS ALEATORIOS (2020 - Mediados 2025) ---
@st.cache_data
def generate_historical_data():
    np.random.seed(42)
    
    start_ts = pd.Timestamp("2020-01-01").value // 10**9
    end_ts = pd.Timestamp("2025-06-30").value // 10**9
    
    random_ts = np.random.randint(start_ts, end_ts, size=15000)
    fechas = pd.to_datetime(random_ts, unit='s')
    
    df = pd.DataFrame({"FechaHora": fechas})
    df = df.sort_values("FechaHora").reset_index(drop=True)
    
    df["MotivoAlerta"] = np.random.choice([
        "SWIFT Alto Riesgo", "Falta de Aprobación", "Riesgo Extremo (>90)",
        "Transacción Inusual", "Documentación Vencida", "Firma Pendiente"
    ], size=len(df), p=[0.1, 0.2, 0.05, 0.3, 0.2, 0.15])
    
    df["Año"] = df["FechaHora"].dt.year
    df["Mes_Periodo"] = df["FechaHora"].dt.to_period("M")
    df["Mes_Nombre"] = df["FechaHora"].dt.strftime("%B")
    df["Fecha_Formato"] = df["FechaHora"].dt.strftime('%d/%m/%Y %H:%M:%S')
    
    return df

df_historico = generate_historical_data()

# --- SIDEBAR (FILTROS Y MÚSICA) ---
if logo_img:
    st.sidebar.image(logo_img, use_container_width=True)
else:
    st.sidebar.markdown("## ⚡ Iberdrola")

# ==========================================
# --- REPRODUCTOR DE MÚSICA EN SIDEBAR ---
# ==========================================
st.sidebar.markdown("### 🎵 Ambiente")
try:
    # Lee el archivo como binario para evitar errores de ruta
    with open(ruta_completa_audio, "rb") as audio_file:
        audio_bytes = audio_file.read()
    st.sidebar.audio(audio_bytes, format="audio/mp3")
except FileNotFoundError:
    st.sidebar.warning("⚠️ Archivo de música no encontrado. Verifica el nombre.")
# ==========================================

st.sidebar.markdown("### Panel de Control")
st.sidebar.info("Sistema: **EN LÍNEA**")
live_mode = st.sidebar.checkbox("Activar Simulación Tiempo Real", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros de Tiempo")

all_years = sorted(df_historico["Año"].unique())
sel_years = st.sidebar.multiselect("Seleccionar Años", all_years, default=[2025])

if sel_years:
    df_year_filtered = df_historico[df_historico["Año"].isin(sel_years)]
else:
    df_year_filtered = df_historico

all_months = sorted(df_year_filtered["Mes_Periodo"].unique())
sel_months = st.sidebar.multiselect("Filtrar Meses (Opcional)", [str(m) for m in all_months])

if sel_months:
    df_filtrado = df_year_filtered[df_year_filtered["Mes_Periodo"].astype(str).isin(sel_months)]
else:
    df_filtrado = df_year_filtered

# --- CABECERA ---
c_logo, c_title = st.columns([1, 6])
with c_logo:
    if logo_img: st.image(logo_img, width=100)
with c_title:
    st.title("Centro de Control de Alertas")

st.markdown("---")

# --- SECCIÓN DE VIDEO YOUTUBE ---
st.markdown('<div class="css-card">', unsafe_allow_html=True)
st.subheader("Presentación del servidor")
url_video = "https://www.youtube.com/watch?v=Blfe4DntymI" 
st.video(url_video)
st.markdown('</div>', unsafe_allow_html=True)

# Placeholder para KPIs Vivos
kpi_placeholder = st.empty()

# --- GRÁFICA TENDENCIA ---
st.markdown('<div class="css-card">', unsafe_allow_html=True)
st.subheader(f"Tendencia Histórica ({min(sel_years) if sel_years else 2020} - {max(sel_years) if sel_years else 2025})")
if not df_filtrado.empty:
    grafica_data = df_filtrado.groupby("Mes_Periodo").size().reset_index(name="Cantidad")
    grafica_data["Mes_Str"] = grafica_data["Mes_Periodo"].astype(str)
    
    fig = px.bar(
        grafica_data, x="Mes_Str", y="Cantidad", color="Cantidad",
        color_continuous_scale=["#A9DFBF", "#004B8D"]
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      xaxis_title=None, yaxis_title=None, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- TABLAS ---
st.subheader("Registro General (Año Seleccionado)")
st.markdown('<div class="css-card">', unsafe_allow_html=True)
st.dataframe(df_filtrado.sort_values("FechaHora", ascending=False).head(10)[["Fecha_Formato", "MotivoAlerta", "Año"]], use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

st.subheader("Detalle por Categoría")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("### 🔴 Patrón: SWIFT de Alto Riesgo")
    st.dataframe(df_filtrado[df_filtrado["MotivoAlerta"].str.contains("Riesgo|SWIFT")].head(10)[["Fecha_Formato", "MotivoAlerta"]], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("### 🟠 Patrón: Egreso sin Ejecutivo Asignado")
    st.dataframe(df_filtrado[df_filtrado["MotivoAlerta"].str.contains("Falta|Vencida")].head(10)[["Fecha_Formato", "MotivoAlerta"]], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("### 🟡 Patrón: Puntuación de Riesgo Extrema")
    st.dataframe(df_filtrado[df_filtrado["MotivoAlerta"].str.contains("Transacción|Firma")].head(10)[["Fecha_Formato", "MotivoAlerta"]], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- GRAFICOS 3D ---
st.markdown('<div class="css-card">', unsafe_allow_html=True)
st.subheader("Graficos 3D")
t1, t2, t3, t4 = st.tabs(["MONTO VS RIESGO", "EJECUTIVO VS TIPO", "RIESGO PROMEDIO", "RIESGO TIPO"])
with t1: components.iframe("https://gentle-cuchufli-2f8ece.netlify.app/", height=500)
with t2: components.iframe("https://superlative-kleicha-c9c31a.netlify.app/", height=500)
with t3: components.iframe("https://jolly-bubblegum-f1baa6.netlify.app/", height=500)
with t4: components.iframe("https://curious-entremet-041122.netlify.app/", height=500)
st.markdown('</div>', unsafe_allow_html=True)

# --- TABLEAU 1: Estados Financieros ---
st.markdown('<div class="css-card">', unsafe_allow_html=True)
st.subheader("Estados financieros")
base_tableau1 = "https://public.tableau.com/views/dashboaradministracion/Dashboard5"
params = "?:embed=yes&:showVizHome=no&:tabs=yes&:toolbar=yes" 
components.iframe(base_tableau1 + params, height=800, scrolling=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- TABLEAU 2: Series de Tiempo ---
st.markdown('<div class="css-card">', unsafe_allow_html=True)
st.subheader("Series de Tiempo")
base_tableau2 = "https://public.tableau.com/views/Dashboard_17642791985070/MontosfinancierosysuMAPEatravsdelosaos"
components.iframe(base_tableau2 + params, height=800, scrolling=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA LIVE ---
if live_mode:
    base_total = len(df_filtrado)
    base_criticas = len(df_filtrado[df_filtrado["MotivoAlerta"].str.contains("Riesgo")])
    
    for i in range(200):
        var_total = np.random.randint(-2, 5) 
        var_critica = np.random.randint(0, 2)
        
        current_total = base_total + i + var_total
        current_criticas = base_criticas + var_critica
        
        motivo_live = np.random.choice(["SWIFT Entrante", "Nueva Transacción", "Validando Docs", "Alerta Riesgo Baja"])
        
        with kpi_placeholder.container():
            st.markdown('<div class="css-card" style="border: 2px solid #6AB547;">', unsafe_allow_html=True)
            st.caption(f"🔴 ÚLTIMA ACTUALIZACIÓN: {pd.Timestamp.now().strftime('%H:%M:%S')} (LIVE)")
            k1, k2, k3 = st.columns(3)
            k1.metric("Total Alertas (Filtro)", current_total, delta=f"{var_total} vs hace 2s")
            k2.metric("Alertas Críticas Activas", current_criticas, delta="Alta Prioridad", delta_color="inverse")
            k3.metric("Actividad en Tiempo Real", motivo_live)
            st.markdown('</div>', unsafe_allow_html=True)
            
        time.sleep(2.5)