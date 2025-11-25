import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Bloomjoy", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
    .stApp {background-color: rgba(255, 250, 240, 1);}
    </style>
    """,
    unsafe_allow_html=True)

# ---------- UTIL: crear datos de ejemplo si no existen ----------
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "sensor_data.csv")

def generate_sample_data(path=DATA_FILE, n=120):
    """Genera un CSV de ejemplo con lecturas cada 10 minutos."""
    os.makedirs(DATA_DIR, exist_ok=True)
    now = datetime.now()
    times = [now - timedelta(minutes=10*i) for i in range(n)][::-1]
    # Sensores: soil_moist (%), temp (°C), light (lux), pir (0/1), humidity (cm)
    np.random.seed(42)
    soil = np.clip(30 + 10*np.sin(np.linspace(0, 6*np.pi, n)) + np.random.randn(n)*3, 5, 100)
    temp = np.clip(22 + 3*np.sin(np.linspace(0, 2*np.pi, n)) + np.random.randn(n)*0.8, 5, 40)
    light = np.clip(200 + 800*np.maximum(0, np.sin(np.linspace(0, 4*np.pi, n))) + np.random.randn(n)*50, 0, 2000)
    pir = (np.random.rand(n) > 0.95).astype(int)
    hum = np.clip(15 + 2*np.sin(np.linspace(0, 4*np.pi, n)) + np.random.randn(n)*1.2, 2, 30)
    df = pd.DataFrame({
        "timestamp": times,
        "soil_moist": np.round(soil, 1),
        "temperature": np.round(temp, 2),
        "light": np.round(light, 1),
        "pir": pir,
        "humidity": np.round(hum, 2)
    })
    df.to_csv(path, index=False)
    return df

df = generate_sample_data()

if not os.path.exists(DATA_FILE):
    df = generate_sample_data()
else:
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;700&display=swap" rel="stylesheet">
    <h1 style="
        font-family: 'Epilogue', sans-serif;
        font-size: 50 px;
        text-align: center;
        color: rgba(29, 201, 57, 1);
        margin-bottom: 20px;
        margin-top: 0;">
        Bloomjoy: Monitoreo de plantas de cultivo
    </h1>
    """,
    unsafe_allow_html=True)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: rgba(255, 245, 228, 0.8);
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: rgba(36, 194, 80, 0.15);
        color: rgb(25, 51, 102);
        width: 100%;
        border: none;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(0, 0, 0, 0.1);
    [data-testid="stSidebar"] .stTextInput input {
        color: rgb(25, 51, 102);
        background-color: rgba(255, 255, 255, 0.2);
    }

    [data-testid="stSidebar"] .stDateInput label {
        color: rgb(25, 51, 102) !important;
        font-weight: bold;
    }

    [data-testid="stSidebar"] .stDateInput input {
        color: #193366 !important;
        background-color: rgb(25, 51, 102) !important;
    }

    [data-testid="stSidebar"] .stCheckbox label {
        color: rgb(25, 51, 102) !important;
        font-size: 14px;
        font-weight: 500;
    }

    [data-testid="stSidebar"] .stCheckbox label p {
        color: rgb(25, 51, 102) !important;
    }

    [data-testid="stSidebar"] .stCheckbox span {
        color: rgb(25, 51, 102) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Sidebar: navegación por sensores ----------
if 'page' not in st.session_state:
    st.session_state['page'] = 'Overview'

sidebar_c1, sidebar_c2 = st.sidebar.columns([1, 3])
with sidebar_c1:
    st.image("bloomjoy.png")
with sidebar_c2:
    st.markdown('<p style="color: rgba(29, 201, 57, 1); font-size: 28px; font-weight: bold;">Bloomjoy</p>', unsafe_allow_html=True)
# Botones por sensor: si se presionan, cambian la página (simula páginas separadas)
if st.sidebar.button("Visión General (Overview)"):
    st.session_state['page'] = 'Overview'
if st.sidebar.button("Humedad de Suelo"):
    st.session_state['page'] = 'soil_moist'
if st.sidebar.button("Temperatura"):
    st.session_state['page'] = 'temperature'
if st.sidebar.button("Luz"):
    st.session_state['page'] = 'light'
if st.sidebar.button("Detección de Movimiento"):
    st.session_state['page'] = 'pir'
if st.sidebar.button("Humedad de Ambiente"):
    st.session_state['page'] = 'humidity'

st.sidebar.markdown("---")
st.sidebar.markdown('<p style="color: rgb(25, 51, 102); font-size: 17px;">Fuente del proyecto:</p>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="color: rgb(25, 51, 102); font-size: 17px;">Documento del Reto (PDF) — referenciado en el proyecto</p>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="color: rgb(25, 51, 102); font-size: 17px;">:contentReference[oaicite:1]{index=1}</p>', unsafe_allow_html=True)  # referencia al PDF subido

# Parámetros globales
st.sidebar.markdown("---")
st.sidebar.markdown('<p style="color: rgb(25, 51, 102); font-size: 17px;">Controles globales</p>', unsafe_allow_html=True)
date_min = df['timestamp'].min().date()
date_max = df['timestamp'].max().date()
start_date, end_date = st.sidebar.date_input("Rango de fechas", [date_min, date_max], min_value=date_min, max_value=date_max)

# Filtrar por rango de fechas
df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]

# opción para simular actualización en vivo (demo)
live_demo = st.sidebar.checkbox("Simular datos en vivo (demo)", value=False)

# ---------- Helpers ----------
def timeseries_plot(df, y, title, y_label, smooth_win=None):
    fig = px.line(df, x='timestamp', y=y, title=title)
    fig.update_layout(yaxis_title=y_label, xaxis_title="Timestamp", margin=dict(t=40,l=40,r=20,b=20))
    if smooth_win and len(df) >= smooth_win:
        df['rolling'] = df[y].rolling(smooth_win, center=False).mean()
        fig.add_scatter(x=df['timestamp'], y=df['rolling'], mode='lines', name=f'{smooth_win}-period (rolling)')
    return fig

def small_stats(df, col):
    last = df[col].iloc[-1]
    mean = df[col].mean()
    med = df[col].median()
    minv = df[col].min()
    maxv = df[col].max()
    return last, mean, med, minv, maxv

def linear_predict(df, col, periods=10):
    """Regresión simple para mostrar tendencia y predecir 'periods' pasos."""
    if len(df) < 3:
        return None, None, None
    X = np.arange(len(df)).reshape(-1,1)
    y = df[col].values
    model = LinearRegression().fit(X, y)
    trend = model.predict(X)
    futX = np.arange(len(df), len(df)+periods).reshape(-1,1)
    futY = model.predict(futX)
    return trend, futX, futY

# ---------- Páginas ----------
page = st.session_state['page']

# ---------- Overview Page ----------
if page == 'Overview':
    st.markdown('<p style="color: rgb(19, 96, 134); font-size: 32px; font-weight: bold;">Visión General de estado y condiciones</p>', unsafe_allow_html=True)
    currentBox_css = """
    <style>
    .st-key-currentConditions {
        background-color: rgba(36, 194, 80, 0.15);
        border-radius: 1rem;
        padding: 1rem;
        box-shadow: 3px 5px 15px 0px rgba(128, 128, 128, 0.245);
        width: 60%;
        max-width: 1000px;
        height: auto;
        margin: 0 auto;
    }
    </style>
    """
    st.html(currentBox_css)
    with st.container(key="currentConditions"):
        st.markdown('<p style="color: rgb(19, 96, 134); font-size: 30px; font-weight: bold; text-align: center;">Condiciones actuales de planta de cultivo Samuel</p>',unsafe_allow_html=True)
        current_col1, current_col2, current_col3, current_col4, current_col5 = st.columns(5)
        with current_col2:
            st.metric("Temperatura (°C)", f"{df['temperature'].iloc[-1]:.1f}", delta=f"{df['temperature'].iloc[-1]-df['temperature'].mean():.1f}")
            st.metric("Luz (lux)", f"{df['light'].iloc[-1]:.0f}", delta=f"{df['light'].iloc[-1]-df['light'].mean():.0f}")
        with current_col3:
            st.image("samuel.png", width=170)
            st.metric("Humedad suelo (%)", f"{df['soil_moist'].iloc[-1]:.1f}", delta=f"{df['soil_moist'].iloc[-1]-df['soil_moist'].mean():.1f}")
            with current_col4:
                st.metric("Humedad ambiente (%)", f"{df['humidity'].iloc[-1]:.1f}")
                st.metric("Movimiento (PIR)", f"{df['pir'].iloc[-1]}")
        st.markdown("---")
        st.markdown('<p style="color: rgb(25, 51, 102); font-size: 17px;">Exportar datos:</p>',unsafe_allow_html=True)
        st.download_button("Descargar CSV filtrado", df.to_csv(index=False).encode('utf-8'), "sensor_data_filtered.csv", "text/csv")
    st.markdown('<p style="color: rgb(19, 96, 134); font-size: 34px; font-weight: bold;">Últimas lecturas (timeline)</p>',unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(19, 96, 134); font-size: 27px;">Humedad y temperatura</p>',unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['soil_moist'], name='Humedad suelo (%)', mode='lines'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], name='Temperatura (°C)', mode='lines', yaxis='y2'))
    fig.update_layout(
        title="Humedad y Temperatura",
        xaxis=dict(domain=[0, 0.9]),
        yaxis=dict(title='Humedad (%)'),
        yaxis2=dict(title='Temperatura (°C)', overlaying='y', side='right'),
        height=420
    )
    st.plotly_chart(fig, use_container_width=True)
    # Light chart
    st.markdown('<p style="color: rgb(19, 96, 134); font-size: 27px;">Luz (lux) — evolución</p>',unsafe_allow_html=True)
    st.plotly_chart(timeseries_plot(df, 'light', 'Nivel de luz', 'lux'), use_container_width=True)
    st.markdown('<p style="color: rgb(19, 96, 134); font-size: 34px; font-weight: bold;">Indicadores y alertas</p>',unsafe_allow_html=True)
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    with alert_col1:
        soil_last, soil_mean, *_ = small_stats(df, 'soil_moist')
        st.metric("Humedad suelo (última)", f"{soil_last:.1f} %", delta=f"{soil_last-soil_mean:.1f}")
        # alerta simple
        if soil_last < 20:
            st.error("Humedad baja — considerar riego")
        elif soil_last > 85:
            st.warning("Humedad muy alta — revisar drenaje")
        else:
            st.success("Humedad dentro de rango")
    with alert_col2:
        temp_last, temp_mean, *_ = small_stats(df, 'temperature')
        st.metric("Temperatura (última)", f"{temp_last:.1f} °C", delta=f"{temp_last-temp_mean:.1f}")
        if temp_last < 10:
            st.warning("Temperatura baja — riesgo de helada")
        elif temp_last > 33:
            st.warning("Temperatura alta — mover a sombra/ventilar")
        else:
            st.info("Temperatura estable")
    with alert_col3:
        light_last, light_mean, *_ = small_stats(df, 'light')
        st.metric("Luz (última)", f"{light_last:.0f} lux", delta=f"{light_last-light_mean:.0f}")
        if light_last < 100:
            st.info("Poca luz — planta de interior o sombra")
        elif light_last > 1500:
            st.warning("Luz muy intensa — proteger del sol directo")
        else:
            st.success("Luz en rango adecuado")

    st.markdown("---")
    st.markdown('<p style="color: rgb(19, 96, 134); font-size: 27px;">Humedad de suelo: Tendencia y predicción básica</p>',unsafe_allow_html=True)
    trend, futX, futY = linear_predict(df.reset_index(drop=True), 'soil_moist', periods=12)
    if trend is not None:
        fig_t = px.line(x=df['timestamp'], y=df['soil_moist'], labels={'x':'Fecha', 'y':'Humedad (%)'}, title="Humedad de suelo y tendencia")
        fig_t.add_scatter(x=df['timestamp'], y=trend, mode='lines', name='Tendencia (fit)')
        # predecir timestamps futuros
        last_ts = df['timestamp'].iloc[-1]
        future_times = [last_ts + timedelta(minutes=10*(i+1)) for i in range(len(futY))]
        fig_t.add_scatter(x=future_times, y=futY, mode='lines', name='Predicción futura')
        st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("No hay suficientes puntos para predicción.")

    st.markdown('<p style="color: rgb(19, 96, 134); font-size: 27px;">Histograma de lecturas (distribución)</p>',unsafe_allow_html=True)
    fig_hist = px.histogram(df.melt(id_vars=['timestamp'], value_vars=['soil_moist','temperature','light']),
                            x='value', color='variable', barmode='overlay',
                            labels={'value':'Valor','variable':'Sensor'})
    st.plotly_chart(fig_hist, use_container_width=True)

# ---------- Página Humedad de Suelo ----------
elif page == 'soil_moist':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 32px; font-weight: bold;">Sensor: Humedad del Suelo</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-weight: bold;">Visualizaciones y controles específicos del sensor de humedad de suelo</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([3,1])
    with col1:
        smooth = st.slider("Ventana de suavizado (rolling)", 1, 30, 6)
        st.plotly_chart(timeseries_plot(df, 'soil_moist', 'Humedad del suelo (%)', '%', smooth_win=smooth), use_container_width=True)
        st.markdown("*Últimas 48 horas (detalle)*")
        last48 = df[df['timestamp'] >= (df['timestamp'].max() - pd.Timedelta(hours=48))]
        st.line_chart(last48.set_index('timestamp')['soil_moist'])
    with col2:
        last, mean, med, minv, maxv = small_stats(df, 'soil_moist')
        st.metric("Lectura actual", f"{last:.1f} %", delta=f"{last-mean:.1f}")
        st.markdown("Estadísticas")
        st.markdown(f"- Promedio: {mean:.1f}%\n- Mediana: {med:.1f}%\n- Mín: {minv:.1f}%\n- Máx: {maxv:.1f}%")
        # Umbrales y recomendaciones
        low_thr = st.number_input("Umbral bajo (regar si <)", value=25.0)
        high_thr = st.number_input("Umbral alto (saturación si >)", value=85.0)
        if last < low_thr:
            st.warning("Estado: Necesita riego — activar bomba programada")
        elif last > high_thr:
            st.info("Estado: Suelo muy húmedo — revisar drenaje")
        else:
            st.success("Estado: Dentro de rango óptimo")
        st.markdown("---")
        st.markdown("Botones de acción (simulados)")
        if st.button("Forzar riego (simulado)"):
            st.success("Se envió comando de riego (simulado).")
        if st.button("Agregar lectura manual"):
            with st.form("manual_soil"):
                v = st.number_input("Valor humedad (%)", min_value=0.0, max_value=100.0, value=float(last))
                submitted = st.form_submit_button("Agregar")
                if submitted:
                    new_row = pd.DataFrame({"timestamp":[pd.Timestamp.now()], "soil_moist":[v], "temperature":[df['temperature'].iloc[-1]],
                                            "light":[df['light'].iloc[-1]], "pir":[df['pir'].iloc[-1]], "humidity":[df['humidity'].iloc[-1]]})
                    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    st.experimental_rerun()

# ---------- Página Temperatura ----------
elif page == 'temperature':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 40px; font-weight: bold;">Sensor: Temperatura</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-weight: bold;">Visualizaciones y alertas de temperatura.</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        st.plotly_chart(timeseries_plot(df, 'temperature', 'Temperatura (°C)', '°C', smooth_win=5), use_container_width=True)
        # Boxplot daily
        df['date_only'] = df['timestamp'].dt.date
        box = px.box(df, x='date_only', y='temperature', labels={'date_only':'Día','temperature':'°C'}, title="Distribución diaria de temperatura")
        st.plotly_chart(box, use_container_width=True)
    with col2:
        last, mean, med, minv, maxv = small_stats(df, 'temperature')
        st.metric("Temperatura actual", f"{last:.1f} °C", delta=f"{last-mean:.1f}")
        if last > 33:
            st.warning("Temperatura alta — posible estrés térmico")
        elif last < 7:
            st.warning("Temperatura baja — riesgo de daño por frío")
        else:
            st.success("Temperatura en rango")
        st.markdown("Configuración de notificaciones (simulado)")
        high = st.number_input("Alerta si temp > (°C)", value=33.0)
        low = st.number_input("Alerta si temp < (°C)", value=7.0)

# ---------- Página Luz ----------
elif page == 'light':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 40px; font-weight: bold;">Sensor: Luz</p>', unsafe_allow_html=True)
    st.plotly_chart(timeseries_plot(df, 'light', 'Nivel de luz (lux)', 'lux', smooth_win=8), use_container_width=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-weight: bold;">Análisis de horas de luz y recomendaciones para la planta según lux.</p>', unsafe_allow_html=True)
    # calcular horas aproximadas > threshold
    lux_thr = st.slider("Umbral de luz (lux) para considerar 'iluminado'", 50, 2000, 300)
    df['is_light'] = df['light'] > lux_thr
    hours_light = df.groupby(df['timestamp'].dt.date)['is_light'].sum() * 10/60  # cada punto 10 minutos -> horas aproximadas
    st.bar_chart(hours_light, height=300)
    avg_hours = hours_light.mean()
    st.markdown(f"Horas promedio con luz > {lux_thr} lux por día: {avg_hours:.2f} h")

# ---------- Página PIR (Movimiento) ----------
elif page == 'pir':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 40px; font-weight: bold;">Sensor: PIR (Movimiento)</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-weight: bold;">Registros de detección de movimiento y conteos por día/hora.</p>', unsafe_allow_html=True)
    # mostrar hits
    hits = df[df['pir'] == 1]
    st.markdown(f"Detecciones totales: {hits.shape[0]}")
    if not hits.empty:
        st.dataframe(hits.sort_values('timestamp', ascending=False).head(20))
    # heatmap por hora
    df['hour'] = df['timestamp'].dt.hour
    pir_by_hour = df.groupby('hour')['pir'].sum().reindex(range(24), fill_value=0)
    fig = px.bar(x=pir_by_hour.index, y=pir_by_hour.values, labels={'x':'Hora','y':'Detecciones'}, title="Detecciones por hora")
    st.plotly_chart(fig, use_container_width=True)

# ---------- Página Nivel de Agua ----------
elif page == 'humidity':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 40px; font-weight: bold;">Sensor: Humedad del Ambiente </p>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-weight: bold;">Monitoreo de la humedad del ambiente.</p>', unsafe_allow_html=True)
    st.plotly_chart(timeseries_plot(df, 'humidity', 'Humedad del ambiente (%)', '%', smooth_win=4), use_container_width=True)
    last, mean, med, minv, maxv = small_stats(df, 'humidity')
    st.metric("Nivel actual (cm)", f"{last:.1f} cm", delta=f"{last-mean:.1f}")
    if last < 5:
        st.error("Nivel bajo — reponer agua")
    elif last > 28:
        st.warning("Nivel muy alto — posible rebosamiento")
    else:
        st.success("Nivel estable")

# ---------- Simulación en vivo (solo demo) ----------
if live_demo:
    st.sidebar.info("Modo demo en vivo: se generan lecturas nuevas y se recarga cada ~5s (simulación)")
    # En modo demo, generar una nueva lectura y añadir al CSV (muy simple)
    if st.button("Agregar lectura demo ahora"):
        last_row = df.iloc[-1]
        new_ts = pd.Timestamp.now()
        new_row = {
            "timestamp": new_ts,
            "soil_moist": max(0, last_row['soil_moist'] + np.random.randn()*1.5),
            "temperature": max(-40, last_row['temperature'] + np.random.randn()*0.3),
            "light": max(0, last_row['light'] + np.random.randn()*20),
            "pir": int(np.random.rand() > 0.96),
            "humidity": max(0, last_row['humidity'] + np.random.randn()*0.5)
        }
        # append
        pd.DataFrame([new_row]).to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("Nueva lectura demo agregada. Recarga para ver cambios.")

# ---------- Footer / notas ----------
st.markdown("---")
st.caption("Dashboard creado para el proyecto IoT de monitoreo de cultivos. Datos de ejemplo generados si no existían. Adaptar la lectura desde la fuente real (CSV, API, Firebase, MQTT) reemplazando la carga de sensor_data.csv.")
st.caption("Referencia del entregable y mapa de empatía en el PDF del proyecto. :contentReference[oaicite:2]{index=2}")
