import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os
import mysql.connector
import time
import pathlib
from bokeh.plotting import figure
from streamlit_autorefresh import st_autorefresh

def obtener_datos():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Minina250506#",
        database="reto_db",
        autocommit=True,
    )
    query = """
    SELECT
        r.Tiempo,
        MAX(CASE WHEN v.Nombre = 'Luz' THEN CAST(r.Valor AS DECIMAL(10,2)) END) AS Luz,
        MAX(CASE WHEN v.Nombre = 'Temperatura' THEN CAST(r.Valor AS DECIMAL(10,2)) END) AS Temperatura,
        MAX(CASE WHEN v.Nombre = 'Humedad' THEN CAST(r.Valor AS DECIMAL(10,2)) END) AS Humedad,
        MAX(CASE WHEN v.Nombre = 'HumedadTierra' THEN CAST(r.Valor AS DECIMAL(10,2)) END) AS 'Humedad de la tierra',
        MAX(CASE WHEN v.Nombre = 'Movimiento' THEN CAST(r.Valor AS SIGNED) END) AS Movimiento
    FROM registro r
    JOIN Variable v ON r.ID_variable = v.ID_variable
    WHERE r.ID_planta = 1
    GROUP BY r.Tiempo
    ORDER BY r.Tiempo DESC
    LIMIT 200
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df['Tiempo'] = pd.to_datetime(df['Tiempo'])
    df = df.fillna(0)
    df['Luz'] = pd.to_numeric(df['Luz'], errors='coerce').fillna(0)
    df['Temperatura'] = pd.to_numeric(df['Temperatura'], errors='coerce').fillna(0)
    df['Humedad'] = pd.to_numeric(df['Humedad'], errors='coerce').fillna(0)
    df['Humedad de la tierra'] = pd.to_numeric(df['Humedad de la tierra'], errors='coerce').fillna(0)
    df['Movimiento'] = pd.to_numeric(df['Movimiento'], errors='coerce').fillna(0).astype(int)
    return df

def obtener_configuracion(id_planta=1):
    """Obtiene los umbrales de configuración desde la base de datos (mismos que usa app.py)"""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Minina250506#",
        database="reto_db",
        autocommit=True,
    )
    query = """
    SELECT e.HumedadT_min, e.HumedadT_max,
            e.Temperatura_min, e.Temperatura_max,
            e.Humedad_min, e.Humedad_max,
            e.Luz_min, e.Luz_max
    FROM Planta p
    JOIN especie_fake e ON p.ID_especie = e.ID_especie
    WHERE p.ID_planta = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (id_planta,))
    config = cursor.fetchone()
    conn.close()
    return config if config else {}

st.set_page_config(page_title="BloomJoy", layout="wide", initial_sidebar_state="expanded", page_icon="bloomjoy.svg")

# Auto-refresh cada 5 segundos (5000 milisegundos)
count = st_autorefresh(interval=5000, limit=100000, key="data_refresh")

st.markdown("""<style>
    .stApp {background-color: rgba(255, 250, 240, 1);}
    </style>
    """,
    unsafe_allow_html=True)

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
        width: 100% !important;
        min-width: 200px !important;
        height: 50px !important;
        border: none;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Epilogue', sans-serif;
        font-size: 16px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgb(237, 186, 247);
    }
    [data-testid="stSidebar"] label {
        color: rgb(25, 51, 102) !important;
        font-family: 'Epilogue', sans-serif !important;
    }
    [data-testid="stSidebar"] label p,
    [data-testid="stSidebar"] label span,
    [data-testid="stSidebar"] label div {
        color: rgb(25, 51, 102) !important;
        font-family: 'Epilogue', sans-serif !important;
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
    st.image("bloomjoy.jpeg")
with sidebar_c2:
    st.markdown('<p style="color: rgba(29, 201, 57, 1); font-size: 28px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">BloomJoy</p>', unsafe_allow_html=True)
if st.sidebar.button("Visión General (Overview)"):
    st.session_state['page'] = 'Overview'
if st.sidebar.button("Humedad de Suelo"):
    st.session_state['page'] = 'Humedad de la tierra'
if st.sidebar.button("Temperatura"):
    st.session_state['page'] = 'Temperatura'
if st.sidebar.button("Luz"):
    st.session_state['page'] = 'Luz'
if st.sidebar.button("Detección de Movimiento"):
    st.session_state['page'] = 'Movimiento'
if st.sidebar.button("Humedad de Ambiente"):
    st.session_state['page'] = 'Humedad'
st.sidebar.markdown("---")
st.sidebar.markdown('<p style="color: rgb(25, 51, 102); font-size: 17px; font-family: \'Epilogue\', sans-serif;">Proyecto BloomJoy</p>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="color: rgb(25, 51, 102); font-size: 14px; font-family: \'Epilogue\', sans-serif;">Sistema IoT de monitoreo de plantas</p>', unsafe_allow_html=True)

# Parámetros globales
st.sidebar.markdown("---")
st.sidebar.markdown('<p style="color: rgb(25, 51, 102); font-size: 17px; font-family: \'Epilogue\', sans-serif;">Controles globales</p>', unsafe_allow_html=True)

# Obtener datos inicialmente 
df = obtener_datos()

# Obtener configuración de umbrales desde BD (mismos que usa app.py)
config = obtener_configuracion(id_planta=1)

# Parámetros de fecha 
if not df.empty:
    date_min = df['Tiempo'].min().date()
    date_max = df['Tiempo'].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Rango de fechas",
        [date_min, date_max],
        min_value=date_min,
        max_value=date_max,
        key="date_range_filter"
    )
else:
    start_date = datetime.now().date()
    end_date = datetime.now().date()

# ---------- Helpers ----------
def timeseries_plot(df, y, title, y_label, smooth_win=None, color='rgb(219, 117, 240)', smooth_color='rgb(233, 99, 99)'):
    fig = px.line(df, x='Tiempo', y=y, title=title)

    fig.update_traces(line=dict(color=color, width=2))

    fig.update_layout(
        yaxis_title=y_label,
        xaxis_title="Tiempo",
        margin=dict(t=40, l=40, r=20, b=20),
        font=dict(family="Epilogue, sans-serif")
    )

    if smooth_win and len(df) >= smooth_win:
        df['rolling'] = df[y].rolling(smooth_win, center=False).mean()
        fig.add_scatter(
            x=df['Tiempo'],
            y=df['rolling'],
            mode='lines',
            name=f'{smooth_win}-period (rolling)',
            line=dict(color=smooth_color, width=2, dash='dash')  
        )
    return fig

def small_stats(df, col):
    last = df[col].iloc[0]  
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

# Obtener datos frescos desde MySQL (sin loops)
df = obtener_datos()

# Verificar que haya datos
if df.empty:
    st.error("No hay datos en la base de datos. Verifica que el ESP32 esté enviando datos.")
    st.stop()

# Filtrar por rango de fechas
df = df[(df['Tiempo'].dt.date >= start_date) & (df['Tiempo'].dt.date <= end_date)]

# ---------- Páginas ----------
page = st.session_state['page']

# ---------- Overview Page ----------
if page == 'Overview':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 32px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Visión General de estado y condiciones</p>', unsafe_allow_html=True)
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
        st.markdown('<p style="color: rgb(25, 51, 102); font-size: 30px; font-family: \'Epilogue\', sans-serif; font-weight: bold; text-align: center;">Condiciones actuales de planta de cultivo Samuel</p>',unsafe_allow_html=True)
        current_col1, current_col2, current_col3, current_col4, current_col5 = st.columns(5)
        with current_col2:
            st.metric("Temperatura (°C)", f"{df['Temperatura'].iloc[0]:.1f}", delta=f"{df['Temperatura'].iloc[0]-df['Temperatura'].mean():.1f}")
            st.metric("Luz (lux)", f"{df['Luz'].iloc[0]:.0f}", delta=f"{df['Luz'].iloc[0]-df['Luz'].mean():.0f}")
        with current_col3:
            st.image("samuel.png", width=170)
            st.metric("Humedad suelo (%)", f"{df['Humedad de la tierra'].iloc[0]:.1f}", delta=f"{df['Humedad de la tierra'].iloc[0]-df['Humedad de la tierra'].mean():.1f}")
        with current_col4:
            st.metric("Humedad ambiente (%)", f"{df['Humedad'].iloc[0]:.1f}")
            st.metric("Movimiento (PIR)", f"{df['Movimiento'].iloc[0]}")
        st.markdown("---")
        st.markdown('<p style="color: rgb(25, 51, 102); font-size: 17px; font-family: \'Epilogue\', sans-serif;">Exportar datos:</p>',unsafe_allow_html=True)
        st.download_button("Descargar CSV filtrado", df.to_csv(index=False).encode('utf-8'), "sensor_data_filtered.csv", "text/csv", key=f"download_csv_{count}")
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 34px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Últimas lecturas (timeline)</p>',unsafe_allow_html=True)
    df_display = df.head(20).reset_index(drop=True)
    df_display.index = df_display.index + 1
    st.dataframe(df_display)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 27px; font-family: \'Epilogue\', sans-serif;">Humedad y temperatura</p>',unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Tiempo'], y=df['Humedad de la tierra'], name='Humedad suelo (%)', mode='lines', line=dict(color='rgb(66, 182, 240)', width=2)))
    fig.add_trace(go.Scatter(x=df['Tiempo'], y=df['Temperatura'], name='Temperatura (°C)', mode='lines', yaxis='y2', line=dict(color='rgb(233, 99, 99)', width=2)))
    fig.update_layout(
        title="Humedad y Temperatura",
        xaxis=dict(domain=[0, 0.9]),
        yaxis=dict(title='Humedad (%)'),
        yaxis2=dict(title='Temperatura (°C)', overlaying='y', side='right'),
        height=420
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 27px; font-family: \'Epilogue\', sans-serif;">Luz — evolución</p>',unsafe_allow_html=True)
    st.plotly_chart(timeseries_plot(df, 'Luz', 'Nivel de luz', 'lux', color='rgb(219, 117, 240)'), use_container_width=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 34px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Indicadores y alertas</p>',unsafe_allow_html=True)
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    with alert_col1:
        soil_last, soil_mean, *_ = small_stats(df, 'Humedad de la tierra')
        st.metric("Humedad suelo (última)", f"{soil_last:.1f} %", delta=f"{soil_last-soil_mean:.1f}")
        # Usar umbrales de la BD (mismos que app.py)
        if soil_last < config['HumedadT_min']:
            st.error(f"Humedad baja (< {config['HumedadT_min']}%) — considerar riego")
        elif soil_last > config['HumedadT_max']:
            st.warning(f"Humedad muy alta (> {config['HumedadT_max']}%) — revisar drenaje")
        else:
            st.success("Humedad dentro de rango")
    with alert_col2:
        temp_last, temp_mean, *_ = small_stats(df, 'Temperatura')
        st.metric("Temperatura (última)", f"{temp_last:.1f} °C", delta=f"{temp_last-temp_mean:.1f}")
        # Usar umbrales de la BD (mismos que app.py)
        if temp_last < config['Temperatura_min']:
            st.warning(f"Temperatura baja (< {config['Temperatura_min']}°C) — riesgo de helada")
        elif temp_last > config['Temperatura_max']:
            st.warning(f"Temperatura alta (> {config['Temperatura_max']}°C) — mover a sombra/ventilar")
        else:
            st.info("Temperatura estable")
    with alert_col3:
        light_last, light_mean, *_ = small_stats(df, 'Luz')
        st.metric("Luz (última)", f"{light_last:.0f} lux", delta=f"{light_last-light_mean:.0f}")
        # Usar umbrales de la BD (mismos que app.py)
        if light_last < config['Luz_min']:
            st.info(f"Poca luz (< {config['Luz_min']} lux) — planta de interior o sombra")
        elif light_last > config['Luz_max']:
            st.warning(f"Luz muy intensa (> {config['Luz_max']} lux) — proteger del sol directo")
        else:
            st.success("Luz en rango adecuado")
    st.markdown("---")
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 27px; font-family: \'Epilogue\', sans-serif;">Humedad de suelo: Tendencia y predicción básica</p>',unsafe_allow_html=True)
    trend, futX, futY = linear_predict(df.reset_index(drop=True), 'Humedad de la tierra', periods=12)
    if trend is not None:
        fig_t = px.line(x=df['Tiempo'], y=df['Humedad de la tierra'], labels={'x':'Fecha', 'y':'Humedad (%)'}, title="Humedad de suelo y tendencia")
        fig_t.add_scatter(x=df['Tiempo'], y=trend, mode='lines', line=dict(color='rgb(251, 194, 81)', width=2), name='Tendencia (fit)')
        last_ts = df['Tiempo'].iloc[-1]
        future_times = [last_ts + timedelta(minutes=10*(i+1)) for i in range(len(futY))]
        fig_t.add_scatter(x=future_times, y=futY, mode='lines', line=dict(color='rgb(233, 99, 99)', width=2), name='Predicción futura')
        st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("No hay suficientes puntos para predicción.")

    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 27px; font-family: \'Epilogue\', sans-serif;">Histograma de lecturas (distribución)</p>',unsafe_allow_html=True)
    fig_hist = px.histogram(df.melt(id_vars=['Tiempo'], value_vars=['Humedad de la tierra','Temperatura','Luz']),
                            x='value', color='variable', barmode='overlay',
                            labels={'value':'Valor','variable':'Sensor'},
                            color_discrete_map={'Humedad de la tierra': 'rgb(66, 182, 240)', 'Temperatura': 'rgb(233, 99, 99)', 'Luz': 'rgb(251, 194, 81)'}, opacity=1)
    st.plotly_chart(fig_hist, use_container_width=True)

# ---------- Página Humedad de Suelo ----------
elif page == 'Humedad de la tierra':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 32px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Sensor: Humedad del Suelo</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Visualizaciones y controles específicos del sensor de humedad de suelo</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([3,1])
    with col1:
        smooth = st.slider("Ventana de suavizado (rolling)", 1, 30, 6, key=f"smooth_slider_{count}")
        st.plotly_chart(timeseries_plot(df, 'Humedad de la tierra', 'Humedad del suelo (%)', '%', smooth_win=smooth), use_container_width=True)
        st.markdown("*Últimas 48 horas (detalle)*")
        last48 = df[df['Tiempo'] >= (df['Tiempo'].max() - pd.Timedelta(hours=48))]
        st.plotly_chart(timeseries_plot(last48, 'Humedad de la tierra', '', '%', color='rgb(233, 99, 99)'),use_container_width=True)
    with col2:
        last, mean, med, minv, maxv = small_stats(df, 'Humedad de la tierra')
        st.metric("Lectura actual", f"{last:.1f} %", delta=f"{last-mean:.1f}")
        st.markdown("Estadísticas")
        st.markdown(f"- Promedio: {mean:.1f}%\n- Mediana: {med:.1f}%\n- Mín: {minv:.1f}%\n- Máx: {maxv:.1f}%")
        # Usar umbrales de la BD
        low_thr = st.number_input("Umbral bajo (regar si <)", value=float(config['HumedadT_min']), key=f"low_thr_{count}")
        high_thr = st.number_input("Umbral alto (saturación si >)", value=float(config['HumedadT_max']), key=f"high_thr_{count}")
        if last < low_thr:
            st.warning("Estado: Necesita riego — activar bomba programada")
        elif last > high_thr:
            st.info("Estado: Suelo muy húmedo — revisar drenaje")
        else:
            st.success("Estado: Dentro de rango óptimo")
        st.markdown("---")
        st.markdown("**Acciones sugeridas**")
        if last < low_thr:
            st.info("Considere activar el sistema de riego automático")
        elif last > high_thr:
            st.info("Revise el sistema de drenaje del suelo")

# ---------- Página Temperatura ----------
elif page == 'Temperatura':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 40px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Sensor: Temperatura</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Visualizaciones y alertas de temperatura.</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        st.plotly_chart(timeseries_plot(df, 'Temperatura', 'Temperatura (°C)', '°C', smooth_win=5), use_container_width=True)
        df['date_only'] = df['Tiempo'].dt.date
        box = px.box(df, x='date_only', y='Temperatura', labels={'date_only':'Día','Temperatura':'°C'}, title="Distribución diaria de temperatura",  color_discrete_sequence=['rgb(66, 182, 240)'])
        st.plotly_chart(box, use_container_width=True)
    with col2:
        last, mean, med, minv, maxv = small_stats(df, 'Temperatura')
        st.metric("Temperatura actual", f"{last:.1f} °C", delta=f"{last-mean:.1f}")
        # Usar umbrales de la BD
        if last > config['Temperatura_max']:
            st.warning(f"Temperatura alta (> {config['Temperatura_max']}°C) — posible estrés térmico")
        elif last < config['Temperatura_min']:
            st.warning(f"Temperatura baja (< {config['Temperatura_min']}°C) — riesgo de daño por frío")
        else:
            st.success("Temperatura en rango")
        st.markdown("Configuración de notificaciones")
        high = st.number_input("Alerta si temp > (°C)", value=float(config['Temperatura_max']), key=f"temp_high_{count}")
        low = st.number_input("Alerta si temp < (°C)", value=float(config['Temperatura_min']), key=f"temp_low_{count}")

# ---------- Página Luz ----------
elif page == 'Luz':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 40px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Sensor: Luz</p>', unsafe_allow_html=True)
    st.plotly_chart(timeseries_plot(df, 'Luz', 'Nivel de luz (lux)', 'lux', smooth_win=8), use_container_width=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Análisis de horas de luz y recomendaciones para la planta según lux.</p>', unsafe_allow_html=True)
    lux_thr = st.slider("Umbral de luz (lux) para considerar 'iluminado'", 50, 2000, 300, key=f"lux_slider_{count}")
    df['is_light'] = df['Luz'] > lux_thr
    hours_light = df.groupby(df['Tiempo'].dt.date)['is_light'].sum() * 10/60
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hours_light.index, y=hours_light.values, marker=dict(color='rgb(251, 194, 81)'),name='Horas de luz'))
    fig.update_layout(xaxis_title="Fecha",yaxis_title="Horas de luz",height=300,font=dict(family="Epilogue, sans-serif"), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    avg_hours = hours_light.mean()
    st.markdown(f"Horas promedio con luz > {lux_thr} lux por día: {avg_hours:.2f} h")

# ---------- Página PIR (Movimiento) ----------
elif page == 'Movimiento':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 40px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Sensor: PIR (Movimiento)</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Registros de detección de movimiento y conteos por día/hora.</p>', unsafe_allow_html=True)
    hits = df[df['Movimiento'] == 1]
    st.markdown(f"Detecciones totales: {hits.shape[0]}")
    if not hits.empty:
        st.dataframe(hits.sort_values('Tiempo', ascending=False).head(20))
    df['hour'] = df['Tiempo'].dt.hour
    pir_by_hour = df.groupby('hour')['Movimiento'].sum().reindex(range(24), fill_value=0)
    fig = px.bar(x=pir_by_hour.index, y=pir_by_hour.values, labels={'x':'Hora','y':'Detecciones'}, title="Detecciones por hora", color_discrete_sequence=['rgb(251, 194, 81)'])
    st.plotly_chart(fig, use_container_width=True)

# ---------- Página Humedad Ambiente ----------
elif page == 'Humedad':
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 40px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Sensor: Humedad del Ambiente </p>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgb(25, 51, 102); font-size: 24px; font-family: \'Epilogue\', sans-serif; font-weight: bold;">Monitoreo de la humedad del ambiente.</p>', unsafe_allow_html=True)
    st.plotly_chart(timeseries_plot(df, 'Humedad', 'Humedad del ambiente (%)', '%', smooth_win=4), use_container_width=True)
    last, mean, med, minv, maxv = small_stats(df, 'Humedad')
    st.metric("Nivel actual (%)", f"{last:.1f} %", delta=f"{last-mean:.1f}")
    # Usar umbrales de la BD
    if last < config['Humedad_min']:
        st.error(f"Nivel bajo (< {config['Humedad_min']}%) — reponer agua")
    elif last > config['Humedad_max']:
        st.warning(f"Nivel muy alto (> {config['Humedad_max']}%) — posible rebosamiento")
    else:
        st.success("Nivel estable")

# ---------- Footer ----------
st.markdown("---")
st.caption("Dashboard creado para el proyecto IoT de monitoreo de cultivos. Datos de ejemplo generados si no existían. Adaptar la lectura desde la fuente real (CSV, API, Firebase, MQTT) reemplazando la carga de sensor_data.csv.")
st.caption("Referencia del entregable y mapa de empatía en el PDF del proyecto. :contentReference[oaicite:2]{index=2}")