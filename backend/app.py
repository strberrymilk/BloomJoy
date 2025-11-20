# Importar librerías
from datetime import datetime
from flask import Flask, request, jsonify
import mysql.connector

# Crear la aplicación
app = Flask(__name__)

# Conexión a MySQL 
db = mysql.connector.connect(
    host="localhost",       
    user="root",     
    password="Minina250506#", 
    database="reto_db",     
    autocommit=True         # Para guardar automáticamente los INSERT
)

# El cursor es un objeto que permite ejecutar SQL
# dictionary=True significa que traerá los resultados como diccionarios, no como tuplas
cursor = db.cursor(dictionary=True)

# Esto convierte nombres que recibimos del ESP a los IDs de la BD.
Variables = {
    "temperatura": 1,
    "humedad": 2,
    "movimiento": 3,
    "valor_ldr": 4,
    "humedad_suelo": 5,
    "relevador": 6
}

# Ruta para obtener configuración de una planta
# @app.route define una URL del servidor.
@app.route('/config/<int:id_planta>', methods=['GET'])
def get_config(id_planta):
    # Instrucción SQL que busca información de la planta y su especie
    cursor.execute("""
        SELECT p.ID_planta, p.ID_especie, e.Frecuencia_riego,
                e.HumedadT_min, e.HumedadT_max,
                e.Temperatura_min, e.Temperatura_max,
                e.Humedad_min, e.Humedad_max,
                e.Luz_min, e.Luz_max
        FROM Planta p
        JOIN Especie e ON p.ID_especie = e.ID_especie
        WHERE p.ID_planta = %s
    """, (id_planta,))  # Aquí metemos id_planta en el %s

    # Sacamos una fila de resultado
    row = cursor.fetchone()

    # Si no existe esa planta, devolvemos error
    if not row:
        return jsonify({"error": "Planta no encontrada"}), 404

    # Armar una respuesta en JSON con la información
    resp = {
        "ID_planta": row["ID_planta"],
        "ID_especie": row["ID_especie"],
        "Frecuencia_riego_horas": row["Frecuencia_riego"],
        "HumedadT_min": row["HumedadT_min"],
        "HumedadT_max": row["HumedadT_max"],
        "Temperatura_min": row["Temperatura_min"],
        "Temperatura_max": row["Temperatura_max"],
        "Humedad_min": row["Humedad_min"],
        "Humedad_max": row["Humedad_max"],
        "Luz_min": row["Luz_min"],
        "Luz_max": row["Luz_max"]
    }

    # jsonify convierte diccionario a JSON
    return jsonify(resp), 200

# Ruta para recibir datos del ESP32
@app.route('/data', methods=['POST'])  
def recibir_datos():
    # request.form obtiene los datos enviados por el ESP32
    # Se convierte a diccionario normal
    datos = request.form.to_dict()

    # Si no llegó nada devolvemos error
    if not datos:
        return jsonify({"error": "No data"}), 400

    # Obtener la hora actual
    tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Listas donde guardaremos qué variables se insertaron
    insertados = []
    alertas = []

    # Si el ESP NO envía ID_planta, usamos 1 por defecto
    id_planta = int(datos.get("ID_planta", 1))

    # Consulta para obtener configuración
    cursor.execute("""
        SELECT p.ID_especie, e.Frecuencia_riego,
                e.HumedadT_min, e.HumedadT_max,
                e.Temperatura_min, e.Temperatura_max,
                e.Humedad_min, e.Humedad_max,
                e.Luz_min, e.Luz_max
        FROM Planta p JOIN Especie e ON p.ID_especie = e.ID_especie
        WHERE p.ID_planta = %s
    """, (id_planta,))

    conf = cursor.fetchone()

    # Validar si la configuración existe
    if not conf:
        return jsonify({"error": f"Config no encontrada para planta {id_planta}"}), 500

    # Recorrer cada dato que mandó el ESP32
    for nombre, valor in datos.items():
        # Si el sensor no existe en el mapa, lo ignoro
        if nombre not in Variables:
            print(f"Ignorado: {nombre}")
            continue

        # Obtener el ID de esa variable en la BD
        id_var = Variables[nombre]

        # Instrucción SQL para insertar en tabla registro
        sql = """
        INSERT INTO registro (ID_planta, ID_variable, Tiempo, Valor)
        VALUES (%s, %s, %s, %s)
        """

        # Ejecutar el INSERT con los valores correspondientes
        cursor.execute(sql, (id_planta, id_var, tiempo, str(valor)))

        # Agregarlo a la lista de insertados
        insertados.append(nombre)

        # Validar rangos y generar alertas
        try:
            if nombre == "temperatura":
                v = float(valor)
                if v < conf["Temperatura_min"] or v > conf["Temperatura_max"]:
                    alertas.append(f"Temperatura fuera de rango: {v}")

            elif nombre == "humedad":
                v = float(valor)
                if v < conf["Humedad_min"] or v > conf["Humedad_max"]:
                    alertas.append(f"Humedad ambiente fuera de rango: {v}")

            elif nombre == "valor_ldr":
                v = int(valor)
                if v < conf["Luz_min"] or v > conf["Luz_max"]:
                    alertas.append(f"Luz fuera de rango: {v}")

            elif nombre == "humedad_suelo":
                v = float(valor)
                if v < conf["HumedadT_min"] or v > conf["HumedadT_max"]:
                    alertas.append(f"Humedad suelo fuera de rango: {v}")

        except Exception:
            # Si el dato no era número, lo ignoramos
            pass

    # Guardamos todos los inserts
    db.commit()

    # Devolvemos respuesta al ESP32 o quien lo llame
    return jsonify({
        "status": "OK",
        "insertados": insertados,
        "alertas": alertas
    }), 200

# Iniciar servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)