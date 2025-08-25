#!/usr/bin/env python3
import sys
import os
import json
import pandas as pd
from datetime import datetime
import traceback
import stat
import logging
from dotenv import load_dotenv, find_dotenv

# Configurar logging
LOG_FILE = "/var/log/cogedatos.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("Inicio del script cogedatos.py")

# Cargar variables de entorno
env_path = "./.env"
if not os.path.exists(env_path):
    sys.stderr.write(f"Error: El archivo de entorno {env_path} no existe.\n")
    logging.error(f"Archivo de entorno {env_path} no encontrado.")
    sys.exit(1)
load_dotenv(env_path)

TOKEN = os.getenv('TOKEN')
CSV_DIR = os.getcwd()
CSV_FILENAME = "gateway_map_data.csv"

if not TOKEN:
    sys.stderr.write("Error: La variable de entorno TOKEN no está definida.\n")
    logging.error("La variable de entorno TOKEN no está definida.")
    sys.exit(1)

def main():
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print()
    try:
        # Registro del intento de POST
        logging.info("Nuevo intento de POST recibido.")

        auth_header = os.environ.get("HTTP_AUTHORIZATION", "").strip()
        if not auth_header.startswith("Bearer "):
            logging.warning(f"Cabecera de autorización ausente o mal formada: {auth_header}")
            return error_response("Cabecera de autorización ausente o mal formada", {"auth_header": auth_header})
        received_token = auth_header[len("Bearer "):].strip()
        if received_token != TOKEN:
            logging.warning(f"Token de autorización inválido. Token recibido: {received_token}")
            return error_response("Token de autorización inválido", {"provided_token": received_token})

        content_length = int(os.environ.get('CONTENT_LENGTH', '0'))
        if content_length <= 0:
            logging.warning("No se recibieron datos. Content-Length es 0 o no se especificó.")
            return error_response("No se recibieron datos. Content-Length es 0 o no se especificó.")

        try:
            post_data = sys.stdin.buffer.read(content_length).decode('utf-8').strip()
            if not post_data:
                logging.warning("No se recibieron datos en la entrada (cadena vacía).")
                return error_response("No se recibieron datos en la entrada.")
            logging.info(f"Datos POST recibidos: {post_data[:200]}")
        except Exception as e:
            logging.exception("Error al leer los datos de entrada")
            return error_response(f"Error al leer los datos de entrada: {str(e)}")

        try:
            data = json.loads(post_data)
        except json.JSONDecodeError as e:
            logging.exception("Error al parsear JSON")
            return error_response("Error al parsear JSON", {"error": str(e), "raw_data": post_data[:200]})
        if not isinstance(data, dict):
            logging.warning("Los datos JSON no son un objeto.")
            return error_response("Los datos JSON deben ser un objeto.", {"received_type": type(data).__name__})

        required_fields = ["name", "id", "ts", "status", "lat", "lng"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logging.warning(f"Campos requeridos faltantes: {missing_fields}")
            return error_response("Campos requeridos faltantes", {"missing_fields": missing_fields})

        validation_errors = validate_data_types(data)
        if validation_errors:
            logging.warning(f"Errores de validación en los datos: {validation_errors}")
            return error_response("Errores de validación en los datos", {"validation_errors": validation_errors})

        if isinstance(data["ts"], str):
            formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S']
            for fmt in formats:
                try:
                    data["ts"] = int(datetime.strptime(data["ts"], fmt).timestamp())
                    break
                except ValueError:
                    continue
            else:
                logging.warning(f"Formato de fecha/hora no reconocido en 'ts': {data['ts']}")
                return error_response("Formato de fecha/hora no reconocido en 'ts'", {"received_ts": data["ts"]})

        if not (-90 <= float(data["lat"]) <= 90):
            logging.warning(f"La latitud {data['lat']} no está entre -90 y 90.")
            return error_response("La latitud debe estar entre -90 y 90", {"received_lat": data["lat"]})
        if not (-180 <= float(data["lng"]) <= 180):
            logging.warning(f"La longitud {data['lng']} no está entre -180 y 180.")
            return error_response("La longitud debe estar entre -180 y 180", {"received_lng": data["lng"]})

        save_to_csv(data)
        logging.info("Datos guardados en CSV exitosamente.")

        success_response = {
            "status": "success",
            "message": "Datos procesados correctamente y almacenados.",
            "data": data
        }
        print(json.dumps(success_response, ensure_ascii=False, indent=2))
        logging.info("Respuesta de éxito enviada al cliente.")

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.exception("Error inesperado en main()")
        return error_response("Error inesperado", {"error": str(e), "traceback": error_trace})

def validate_data_types(data):
    errors = []
    expected_types = {
        "name": str,
        "id": (str, int),
        "status": int,
        "lat": (float, int),
        "lng": (float, int)
    }
    for field, expected in expected_types.items():
        if field in data and not isinstance(data[field], expected):
            errors.append(f"'{field}' debe ser {expected}, pero se recibió {type(data[field]).__name__}")
    return errors

def save_to_csv(data):
    os.makedirs(CSV_DIR, exist_ok=True)
    csv_path = os.path.join(CSV_DIR, CSV_FILENAME)
    df = pd.DataFrame([data])
    write_header = not os.path.exists(csv_path)
    try:
        df.to_csv(csv_path, mode='a', index=False, header=write_header)
        os.chmod(csv_path, 0o600)  # Solo el dueño puede leer y escribir
    except Exception as e:
        logging.exception("Error al escribir el archivo CSV")
        return error_response("Error al escribir el archivo CSV", {"error": str(e), "csv_path": csv_path})

def error_response(message, details=None):
    response = {"status": "error", "message": message}
    if details:
        response["details"] = details
    print(json.dumps(response, ensure_ascii=False, indent=2))
    # Registra el error en el log
    logging.error(f"{message} - Detalles: {details}")
    return False

if __name__ == "__main__":
    main()
