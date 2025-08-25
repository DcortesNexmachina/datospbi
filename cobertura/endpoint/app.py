import pandas as pd
import json
from datetime import datetime
EXCEL_FILE = '/var/www/html/proyectos/cobertura/muestreo_cobertura.xlsx'
def create_excel_file():
    try:
        pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            pass

def save_to_excel(gateway_id, deduplication_id, device_name, rssi, snr, frequency, bandwidth, data):
    try:
        xl = pd.ExcelFile(EXCEL_FILE)
        sheet_names = xl.sheet_names
    except FileNotFoundError:
        sheet_names = []
    if gateway_id in sheet_names:
        df = pd.read_excel(EXCEL_FILE, sheet_name=gateway_id)
    else:
        df = pd.DataFrame(columns=["Fecha", "DeduplicationId", "DeviceName", "RSSI", "SNR", "Frequency", "Bandwidth", "Data", "Latitud", "Longitud"])
    new_row = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "DeduplicationId": deduplication_id,
        "DeviceName": device_name,
        "RSSI": rssi,
        "SNR": snr,
        "Frequency": frequency,
        "Bandwidth": bandwidth,
        "Data": data,
        "Latitud": None,
        "Longitud": None
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=gateway_id, index=False)
def handle_post_request(environ):
    length = int(environ.get('CONTENT_LENGTH', 0))
    if length == 0:
        response = {"error": "No data provided"}
        return 'application/json', json.dumps(response)
    raw_data = environ['wsgi.input'].read(length)
    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError as e:
        response = {"error": f"Invalid JSON: {str(e)}"}
        return 'application/json', json.dumps(response)
    try:
        deduplication_id = data["deduplicationId"]
        device_name = data["deviceInfo"]["deviceName"]
        rssi = data["rxInfo"][0]["rssi"]
        snr = data["rxInfo"][0]["snr"]
        frequency = data["txInfo"]["frequency"]
        bandwidth = data["txInfo"]["modulation"]["lora"]["bandwidth"]
        gateway_id = data["rxInfo"][0]["gatewayId"]
        data_field = data["data"]
    except (KeyError, IndexError) as e:
        response = {"error": f"Missing or invalid field: {str(e)}"}
        return 'application/json', json.dumps(response)
    save_to_excel(gateway_id, deduplication_id, device_name, rssi, snr, frequency, bandwidth, data_field)
    response = {"message": "Datos guardados correctamente"}
    return 'application/json', json.dumps(response)
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    content_type, response_body = handle_post_request(environ)
    return [response_body.encode('utf-8')]
