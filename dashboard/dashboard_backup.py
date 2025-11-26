'''
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
'''
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

st.error('No se pudo contactar al backend. Implementa /control/relevador en Flask o ajusta la URL en Ajustes.')

with col_off:
if st.button('Apagar relevador'):
try:
r = requests.post(f"{BACKEND_BASE}/control/relevador", json={"ID_planta": int(DEFAULT_PLANT_ID), "accion": "OFF"}, timeout=3)
if r.status_code in (200,201):
st.success('Comando enviado: OFF')
else:
st.error(f'Error al enviar comando: {r.status_code}')
except Exception:
st.error('No se pudo contactar al backend. Implementa /control/relevador en Flask o ajusta la URL en Ajustes.')


st.markdown('---')
st.write('También puedes programar un pulso de encendido:')
dur = st.slider('Segundos ON', 1, 300, 10)
if st.button('Enviar pulso'):
try:
r = requests.post(f"{BACKEND_BASE}/control/relevador", json={"ID_planta": int(DEFAULT_PLANT_ID), "accion": "PULSE", "dur": dur}, timeout=3)
if r.status_code in (200,201):
st.success('Pulso enviado')
else:
st.error('Error al enviar pulso')
except Exception:
st.error('No se pudo contactar al backend. Implementa /control/relevador en Flask o ajusta la URL en Ajustes.')


st.info('Nota: El backend mostrado al principio del proyecto no incluye /control/relevador por defecto. Añade un endpoint POST en Flask que reciba JSON {"ID_planta":..., "accion":"ON|OFF|PULSE", "dur":...} y haga la acción física sobre tu GPIO o via MQTT.')


# ------------------------
# Configuración Planta (obtener del backend)
# ------------------------


elif page == "Configuración Planta":
st.title('Configuración de Planta')
plant_id = st.number_input('ID de planta', min_value=1, value=int(DEFAULT_PLANT_ID))
if st.button('Obtener configuración desde backend'):
conf = call_backend_config(BACKEND_BASE, int(plant_id))
if conf:
st.json(conf)
else:
st.error('No se pudo obtener la configuración. Verifica backend o que la planta exista.')


# ------------------------
# Logs (tabla)
# ------------------------


elif page == "Logs":
st.title('Logs / Últimos Registros')
if df is None:
st.info('No hay datos')
else:
st.dataframe(df.sort_values('timestamp', ascending=False).head(500))


# ------------------------
# Ajustes (subir CSV / explicación)
# ------------------------


elif page == "Ajustes":
st.title('Ajustes')
st.markdown('Sube un CSV con datos de sensores si no tienes la ESP32 conectada al Flask aún. El CSV debe contener al menos la columna `timestamp`.')
upload = st.file_uploader('Subir CSV (reemplaza data/sensor_data.csv)', type=['csv'])
if upload is not None:
df_up = pd.read_csv(upload)
df_up.to_csv(DATA_FILE, index=False)
st.success('CSV guardado en data/sensor_data.csv')
st.experimental_rerun()

st.markdown('---')
st.markdown('**Instrucciones de integración con tu Flask backend**')
st.markdown('- Tu Flask ya implementa `/config/<int:id_planta>` que devuelve rangos; este dashboard los usa para alertas.')
st.markdown('- Para control directo desde el dashboard implementa un endpoint POST `/control/relevador` que reciba JSON `{"ID_planta":..., "accion":"ON|OFF|PULSE", "dur":...}` y ejecute la acción. El dashboard intentará llamar allí.')
st.markdown('- Si quieres que el dashboard pida registros directos desde la BD, añade un endpoint GET en Flask como `/registros/<int:id_planta>?limit=100` que devuelva los últimos registros en JSON, y aquí podemos consumirlo fácilmente.')

st.markdown('---')
st.markdown('Ajustes rápidos:')
st.write('Ruta backend actual:', BACKEND_BASE)
st.write('Archivo CSV usado:', DATA_FILE)

st.sidebar.markdown('---')