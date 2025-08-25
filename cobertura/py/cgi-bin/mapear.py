#!/usr/bin/env python3
import folium
import numpy as np
import pandas as pd
from datetime import datetime
import json

EXCEL_FILE = '/var/www/html/proyectos/cobertura/muestreo_cobertura.xlsx'
OUTPUT_HTML = '/var/www/html/proyectos/cobertura/mapa.html'
#gws = {
#    'GW_IS_Atalaya_Ubeda': [38.01999191679679, -3.377060996820076],
#    'GW_IS_Deposito_MadreDios_Ubeda': [38.026434805634196, -3.3515475569946362],
#    'GW_IS_Polideportivo_Ubeda': [38.008755846932544, -3.37772711975173],
#    'GW_IS_Terrero_Alto_Ubeda': [38.01020634046197, -3.351332980273445]
#}
gws = {}
def interpolar_color(rssi):
    RSSI_min, RSSI_mid, RSSI_max = -125, -100, -40
    if rssi <= RSSI_mid:
        normalized = (rssi - RSSI_min) / (RSSI_mid - RSSI_min)
        red = int(255 * normalized)
        green = 255
        return f"#{red:02x}{green:02x}00"
    else:
        normalized = (rssi - RSSI_mid) / (RSSI_max - RSSI_mid)
        red = 255
        green = int(255 * (1 - normalized))
        return f"#{red:02x}{green:02x}00"

try:
    sheet_name = str(datetime.now().date())
    if sheet_name not in pd.ExcelFile(EXCEL_FILE).sheet_names:
        print("Content-Type: application/json\n")
        print(json.dumps({"message": "No hay datos para generar el mapa"}))
        exit()
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    if df.empty:
        print("Content-Type: application/json\n")
        print(json.dumps({"message": "La hoja está vacía, no se generará el mapa"}))
        exit()
    df = df[(df['Latitud'] != -1) & (df['Longitud'] != -1)]
    mapa = folium.Map(
        location=[df['Latitud'][0], df['Longitud'][0]],
        zoom_start=15,
        tiles="CartoDB positron"
    )
    gateways_layer = folium.FeatureGroup(name="Gateways", overlay=True).add_to(mapa)
    mediciones_layer = folium.FeatureGroup(name="Localizaciones de Mediciones", overlay=True).add_to(mapa)
    heatmap_layer = folium.FeatureGroup(name="Mapa de Calor", overlay=True).add_to(mapa)
    for gw_name, (lat, lng) in gws.items():
        folium.Marker(
            location=[lat, lng],
            popup=gw_name,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(gateways_layer)
    radio_km = 0.2
    num_opacity_layers = 4
    for _, row in df.iterrows():
        lat, lng, rssi = row['Latitud'], row['Longitud'], row['RSSI']
        color = interpolar_color(rssi)
        folium.Marker(
            location=[lat, lng],
            tooltip=f"RSSI: {round(rssi)} dBm",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(mediciones_layer)
        for alpha in np.linspace(0.05, 0.5, num_opacity_layers):
            folium.Circle(
                location=(lat, lng),
                radius=radio_km * 1000 / (alpha * 10),
                color=None,
                fill=True,
                fill_color=color,
                fill_opacity=alpha
            ).add_to(heatmap_layer)
    folium.LayerControl(collapsed=False).add_to(mapa)
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 320px; height: 200px;
                background-color: white; z-index: 9999; font-size: 14px;
                border: 2px solid grey; border-radius: 8px; padding: 10px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.3);">
        <b>Intensidad de Señal RSSI (dBm)</b><br>
        <div style="margin-top: 10px; height: 20px; background: linear-gradient(to right,
            #00ff00, #ffff00, #ff0000);">
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 12px;">
            <span>-125</span>
            <span>-100</span>
            <span>-40</span>
        </div>
        <div style="font-size: 12px; margin-top: 10px; text-align: justify;">
            <b>Nota:</b> Los valores más cercanos a -40 dBm indican una señal fuerte y óptima,
            mientras que los valores hacia -125 dBm indican una señal débil.
        </div>
    </div>
    '''
    mapa.save('/var/www/html/proyectos/cobertura/mapa_sin_leyenda.html')
    mapa.get_root().html.add_child(folium.Element(legend_html))
    mapa.save(OUTPUT_HTML)
    print("Content-Type: application/json\n")
    print(json.dumps({"message": "Mapa generado correctamente"}))
except Exception as e:
    print("Content-Type: application/json\n")
    print(json.dumps({"error": str(e)}))
