# Importo dependencias
import streamlit as st
import pandas as pd
import mysql.connector
import time
import pathlib
import numpy as np
import plotly as px
import plotly.figure_factory as ff
from bokeh.plotting import figure
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="BloomJoy", layout="wide")

# Función para cargar CSS personalizado
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

# Cargar CSS personalizado
css_path = pathlib.Path("styles.css")
load_css(css_path)

# Título personalizado con fuente externa
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;700&display=swap" rel="stylesheet">
    <h1 style="
        font-family: 'Epilogue', sans-serif;
        font-size: 36px;
        text-align: center;
        color: #193366;
        margin-bottom: 20px;">
        Dashboard de Temperatura IoT
    </h1>
    """,
    unsafe_allow_html=True
)

def obtener_datos():
    conn = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="iot_db"
    )
    df = pd.read_sql("SELECT * FROM temperaturas ORDER BY fecha DESC LIMIT 50, conn BY fecha DESC LIMIT 50", conn)
    conn.close()
    return df

placeholder = st.empty()

while True:
    df = obtener_datos()
    with placeholder.container():
        st.subheader("Últimas mediciones")
        st.dataframe(df)
        st.line_chart(df[['valor']].set_index(df['fecha']))
    time.sleep(5)