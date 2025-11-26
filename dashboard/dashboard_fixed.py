# Importo dependencias
import streamlit as st
import pandas as pd
import mysql.connector
import requests
import pathlib
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="BloomJoy Dashboard", layout="wide")

# Configuración
BACKEND_BASE = "http://localhost:5000"
DEFAULT_PLANT_ID = 1

# Función para cargar CSS personalizado
def load_css(file_path):
    try:
        with open(file_path) as f:
            st.html(f"<style>{f.read()}</style>")
    except FileNotFoundError:
        pass

# Cargar CSS personalizado si existe
css_path = pathlib.Path("styles.css")
load_css(css_path)

# Título personalizado
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;700&display=swap" rel="stylesheet">
    <h1 style="
        font-family: 'Epilogue', sans-serif;
        font-size: 36px;
        text-align: center;
        color: #193366;
        margin-bottom: 20px;">
        🌱 BloomJoy Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

# Función para obtener datos desde MySQL
def obtener_datos_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Minina250506#",
            database="reto_db"
        )
        query = """
        SELECT 
            r.Tiempo,
            v.Nombre AS Variable,
            r.Valor
        FROM registro r
        JOIN Variable v ON r.ID_variable = v.ID_variable
        WHERE r.ID_planta = %s
        ORDER BY r.Tiempo DESC
        LIMIT 100
        """
        df = pd.read_sql(query, conn, params=(DEFAULT_PLANT_ID,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error conectando a MySQL: {e}")
        return None

# Función para obtener configuración desde Flask
def obtener_config():
    try:
        response = requests.get(f"{BACKEND_BASE}/config/{DEFAULT_PLANT_ID}", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

# Sidebar - Navegación
st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a:", ["Dashboard Principal", "Configuración Planta", "Control Manual", "Logs"])

# ------------------------
# Dashboard Principal
# ------------------------
if page == "Dashboard Principal":
    st.subheader("Monitoreo en Tiempo Real")
    
    # Botón de actualizar
    if st.button("Actualizar datos"):
        st.rerun()
    
    # Obtener datos
    df = obtener_datos_mysql()
    
    if df is not None and not df.empty:
        # Pivotar datos para mostrar en tabla
        df_pivot = df.pivot_table(
            index='Tiempo',
            columns='Variable',
            values='Valor',
            aggfunc='first'
        ).reset_index()
        
        st.dataframe(df_pivot.head(20), use_container_width=True)
        
        # Gráficas
        st.markdown("### Gráficas de Sensores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfica de Temperatura
            df_temp = df[df['Variable'] == 'Temperatura']
            if not df_temp.empty:
                st.line_chart(df_temp.set_index('Tiempo')['Valor'].astype(float), use_container_width=True)
                st.caption("Temperatura (°C)")
        
        with col2:
            # Gráfica de Humedad
            df_hum = df[df['Variable'] == 'Humedad']
            if not df_hum.empty:
                st.line_chart(df_hum.set_index('Tiempo')['Valor'].astype(float), use_container_width=True)
                st.caption("Humedad Ambiente (%)")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Gráfica de Humedad Suelo
            df_soil = df[df['Variable'] == 'HumedadTierra']
            if not df_soil.empty:
                st.line_chart(df_soil.set_index('Tiempo')['Valor'].astype(float), use_container_width=True)
                st.caption("🌿 Humedad del Suelo (%)")
        
        with col4:
            # Gráfica de Luz
            df_luz = df[df['Variable'] == 'Luz']
            if not df_luz.empty:
                st.line_chart(df_luz.set_index('Tiempo')['Valor'].astype(float), use_container_width=True)
                st.caption("💡 Luz (%)")
    else:
        st.info("No hay datos disponibles. Verifica que el ESP32 esté enviando datos.")

# Configuración Planta
elif page == "Configuración Planta":
    st.title('Configuración de Planta')
    
    plant_id = st.number_input('ID de planta', min_value=1, value=int(DEFAULT_PLANT_ID))
    
    if st.button('Obtener configuración desde backend'):
        conf = obtener_config()
        if conf:
            st.success("Configuración obtenida")
            st.json(conf)
        else:
            st.error('No se pudo obtener la configuración. Verifica que Flask esté corriendo.')

# ------------------------
# Control Manual
# ------------------------
elif page == "Control Manual":
    st.title('Control Manual del Relé')
    st.warning('Funcionalidad en desarrollo. Requiere endpoint `/control/relevador` en Flask.')
    
    col_on, col_off = st.columns(2)
    
    with col_on:
        if st.button('Encender relevador'):
            st.info('Endpoint /control/relevador no implementado aún.')
    
    with col_off:
        if st.button('Apagar relevador'):
            st.info('Endpoint /control/relevador no implementado aún.')
    
    st.markdown('---')
    st.write('**Enviar pulso programado:**')
    dur = st.slider('Segundos ON', 1, 300, 10)
    if st.button('Enviar pulso'):
        st.info('Endpoint /control/relevador no implementado aún.')

# ------------------------
# Logs
# ------------------------
elif page == "Logs":
    st.title('Logs / Últimos Registros')
    df = obtener_datos_mysql()
    if df is not None and not df.empty:
        st.dataframe(df.head(100), use_container_width=True)
    else:
        st.info('No hay datos disponibles')

# Footer
st.sidebar.markdown('---')
st.sidebar.caption('BloomJoy Dashboard v1.0')