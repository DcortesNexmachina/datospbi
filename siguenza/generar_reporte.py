import matplotlib.pyplot as plt
import pandas as pd
import asyncio
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from iqmenic import IQmenic

apikey = 'bGFiZWuvrXN0ZW1hc2FkbWluOmFkbWluRVZPMjDaV66=='

import asyncio
from iqmenic import IQmenic

apikey = 'bGFiZWuvrXN0ZW1hc2FkbWluOmFkbWluRVZPMjDaV66=='  # Tu API Key

async def dataframe(apikey):
    # Usar 'with' para manejar la sesión correctamente
    async with IQmenic(apikey) as iqmenic:
        # Capturamos el resultado de get_all()
        df = await iqmenic.get_all()
        return df  # Asegurarnos de devolver el DataFrame

# Ejecutar el código asincrónicamente
df = asyncio.run(dataframe(apikey))

alertas = []
baterias_bajas = []
sobrevoltajes = []
fallos = []
percentil5 = np.percentile(df[df['Propiedad'] == 'Voltaje']['valorrecibido'], 5)
media_voltaje = df[df['Propiedad'] == 'Voltaje']['valorrecibido'].mean()
percentil95 = np.percentile(df[df['Propiedad'] == 'Voltaje']['valorrecibido'], 95)

umbral_bateria_baja = percentil5 if percentil5 != media_voltaje else media_voltaje
umbral_bateria_alta = percentil95 if percentil95 != media_voltaje else media_voltaje
dias_offline_umbral = 14

def categorize_rssi(value):
    if value >= -70:
        return 'Excelente'
    elif -90 <= value < -70:
        return 'Buena'
    elif -120 <= value < -90:
        return 'Regular'
    else:
        return 'Pobre'

def plot_rssi_quality(data, filename):
    data['Calidad de señal'] = data['valorrecibido'].apply(categorize_rssi)
    counts = data['Calidad de señal'].value_counts()
    labels = counts.index
    sizes = counts.values
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
    plt.title('Frecuencia de Calidad de Señal RSSI')
    plt.axis('equal')
    plt.savefig(filename)
    plt.close()

def plot_voltage_histogram(data, filename):
    voltaje_values = data['valorrecibido']
    bins = np.linspace(voltaje_values.min(), voltaje_values.max(), 6)
    plt.figure(figsize=(10, 6))
    plt.hist(voltaje_values, bins=bins, edgecolor='black', alpha=0.7)
    plt.title('Histograma de Voltaje')
    plt.xlabel('Voltaje')
    plt.ylabel('Frecuencia')
    plt.xticks(bins)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_alerts_pie_chart(data, filename):
    counts = data.value_counts()
    labels = counts.index
    sizes = counts.values
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff'])
    plt.title('Frecuencia de Alertas')
    plt.axis('equal')
    plt.savefig(filename)
    plt.close()

def generate_charts(df):
    rssi_df = df[df['Propiedad'] == 'RSSI']
    plot_rssi_quality(rssi_df, '/var/www/html/siguenza/rssi_quality_pie_chart.png')
    
    voltaje_df = df[df['Propiedad'] == 'Voltaje']
    plot_voltage_histogram(voltaje_df, '/var/www/html/siguenza/voltaje_histogram.png')
    
    alert_df = df['alerta']
    plot_alerts_pie_chart(alert_df, '/var/www/html/siguenza/alertas_pie_chart.png')

generate_charts(df)
df = df[(df['Propiedad'] != 'Derecha a Izquierda') & (df['Propiedad'] != 'Izquierda a Derecha')]

# Generar informe en HTML
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Estado de Sensores</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2, h3 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <h1>Informe de Estado de Sensores</h1>
    <h2>Sensor: Conteo de Personas</h2>
"""
for propiedad in ['Batería', 'Voltaje']:
    sensor_data = df[df['Propiedad'] == propiedad]
    nombre_sensor = propiedad
    ultima_fecha = sensor_data['fecha'].max()
    ultima_ubicacion = "Correcta" if str(sensor_data['fecha'].max())[:10] == datetime.now().strftime('%Y-%m-%d') else "Sin datos"
    rssi_data = df[df['Propiedad'] == propiedad]
    ultima_senal = rssi_data['valorrecibido'].max() if not rssi_data.empty else "Sin datos de señal"
    ultimo_voltaje = sensor_data[(sensor_data['fecha'] == ultima_fecha) & (sensor_data['Propiedad'] == 'Voltaje')]
    ultimo_voltaje = ultimo_voltaje['valorrecibido'].max() if not ultimo_voltaje.empty else None

    if ultimo_voltaje is None:
        estado_bateria = "Sin datos de voltaje"
        accion_recomendada = "Ninguna acción requerida."
    else:
        if ultimo_voltaje < umbral_bateria_baja:
            estado_bateria = "Batería del sensor baja"
            accion_recomendada = "Reemplace la batería del sensor."
        elif (pd.Timestamp.now() - pd.to_datetime(ultima_fecha)).days >= dias_offline_umbral:
            estado_bateria = "Requiere análisis"
            accion_recomendada = "El sensor ha estado desconectado por más de 14 días. Contacte al soporte técnico."
        else:
            estado_bateria = "Correcto"
            accion_recomendada = "Ninguna acción requerida."

    html_content += f"""
    <h3>Propiedad: {nombre_sensor}</h3>
    <table>
        <tr><th>Campo</th><th>Descripción</th></tr>
        <tr><td>Fecha</td><td>{str(sensor_data['fecha'].max())[:10]}</td></tr>
        <tr><td>Ubicación</td><td>{ultima_ubicacion}</td></tr>
        <tr><td>Último valor recibido</td><td>{ultima_senal}</td></tr>
        <tr><td>Estado</td><td>{estado_bateria}</td></tr>
        <tr><td>Acción recomendada</td><td><strong>{accion_recomendada}</strong></td></tr>
    </table>
    """

# Información sobre alertas
if len(df['alerta'].value_counts().index) == 2:
    pass
else:
    if df['alerta'].value_counts().index[0] == 0:
        accion_recomendada = "Ninguna acción requerida."
        estado_bateria = 'Correcto'
    else:
        accion_recomendada = "Alerta activada, consulte con soporte para más información."
        estado_bateria = 'Alerta'

html_content += f"""
<h3>Propiedad: Alertas</h3>
<table>
    <tr><th>Campo</th><th>Descripción</th></tr>
    <tr><td>Alerta activada</td><td>{df['alerta'].value_counts().index[0]}</td></tr>
    <tr><td>Estado de alerta</td><td>{estado_bateria}</td></tr>
    <tr><td>Acción recomendada</td><td><strong>{accion_recomendada}</strong></td></tr>
</table>

<h2>Gráficos</h2>
<h3>Calidad de Señal RSSI</h3>
<img src="rssi_quality_pie_chart.png" alt="Calidad de Señal RSSI">
<h3>Histograma de Voltaje</h3>
<img src="voltaje_histogram.png" alt="Histograma de Voltaje">
<h3>Frecuencia de Alertas</h3>
<img src="alertas_pie_chart.png" alt="Frecuencia de Alertas">
</body>
</html>
"""

# Guardar el contenido HTML en un archivo
with open('/var/www/html/siguenza/informe_alertas.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

HISTORICO = 'datos_historicos.csv'
df_csv = pd.read_csv(HISTORICO, sep=',')
merged = pd.merge(df, df_csv, how="inner")
datos_extra = pd.DataFrame({"Restaurantes": [2], "Rutas": [5], "Alojamientos": [1], "Poblacion": [20]},index=[0])
with pd.ExcelWriter("reporte.xlsx", engine="openpyxl") as writer:
    merged.to_excel(writer, sheet_name="Hoja 1", index=False)
    datos_extra.to_excel(writer, sheet_name="Hoja 2", index=False)
