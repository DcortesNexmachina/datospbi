#!/usr/bin/env python3
import cgi
import cgitb
import pandas as pd
import os
from datetime import datetime, timedelta
cgitb.enable()
form = cgi.FieldStorage()
rssi = form.getvalue("rssi")
sf = form.getvalue("sf")
lat = form.getvalue("lat")
lon = form.getvalue("lon")
fecha = datetime.now()
fecha_mas_una_hora = fecha + timedelta(hours=1)
fecha_str = fecha_mas_una_hora.strftime("%Y-%m-%d")
archivo_excel = "/var/www/html/proyectos/cobertura/muestreo_cobertura.xlsx"
def convertir_a_flotante(valor):
    try:
        return float(valor.replace(",", "."))
    except (ValueError, AttributeError):
        return -1
rssi_value = convertir_a_flotante(rssi) or rssi
sf_value = convertir_a_flotante(sf) or sf
lat_value = convertir_a_flotante(lat) or lat
lon_value = convertir_a_flotante(lon) or lon
nuevo_dato = pd.DataFrame([{
    "Fecha": fecha_mas_una_hora.strftime("%Y-%m-%d %H:%M:%S"),
    "Latitud": lat_value,
    "Longitud": lon_value,
    "RSSI": rssi_value,
    "SF": sf_value
}])
if not os.path.exists(archivo_excel):
    df_inicial = pd.DataFrame(columns=["Fecha", "Latitud", "Longitud", "RSSI", "SF"])
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        hoja_inicial = datetime.now().strftime("%Y-%m-%d")
        df_inicial.to_excel(writer, index=False, sheet_name=hoja_inicial)
try:
    df = pd.read_excel(archivo_excel, sheet_name=fecha_str)
except ValueError:
    with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        nuevo_dato.to_excel(writer, sheet_name=fecha_str)
df = pd.read_excel(archivo_excel, sheet_name=fecha_str)
df = pd.concat([df, nuevo_dato], ignore_index=True)
df.sort_values(by="Fecha", inplace=True)
df.drop(columns='Unnamed: 0', errors='ignore', inplace=True, axis=1)
try:
    with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=fecha_str, index=False)
except Exception as e:
    print("Content-Type: text/html\n")
    print("<html><body>")
    print("<h1>Error al guardar los datos</h1>")
    print(f"<p>{str(e)}</p>")
    print('<a href="https://datospbi.iqmenic.com/cobertura/index.html">Volver al formulario</a>')
    print("</body></html>")
    raise
print("Content-Type: text/html\n")
print("<html><body>")
print("<h1>Datos guardados correctamente</h1>")
print('<a href="https://datospbi.iqmenic.com/cobertura/index.html">Volver al formulario</a>')
print("</body></html>")
