import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
data = [
    ["Desengrase", "13-01-2025 12:53", "Presión Bomba 1.2", "[0 - 2.5 Kg]", "1.419 Kgs"],
    ["Desengrase", "13-01-2025 12:53", "Presión Bomba 1.1", "[0 - 2.5 Kg]", "1.399 Kgs"],
    ["Desengrase", "13-01-2025 12:53", "Conductividad", "[0 - 250 µs]", "13.94 mS"],
    ["Desengrase", "13-01-2025 12:53", "Temperatura", "[0 - 60 ºC]", "44 ºC"],
    ["Aclarado AGUA RED", "13-01-2025 12:53", "Presión", "[0 - 2.5 Kg]", "1.191 Kgs"],
    ["Aclarado AGUA RED", "13-01-2025 12:53", "Conductividad", "[0 - 250 µs]", "0.45 mS"],
    ["Aclarado AGUA OSMOTIZADA", "13-01-2025 12:53", "Presión", "[0 - 2.5 Kg]", "1.19 Kgs"],
    ["Aclarado AGUA OSMOTIZADA", "13-01-2025 12:53", "pH", "[1 - 14]", "5.561"],
    ["Aclarado AGUA OSMOTIZADA", "13-01-2025 12:53", "Conductividad (114ms)", "[0 - 250 µs]", "282.505 µs"],
    ["Conversión Nanotecnológica", "13-01-2025 12:53", "Presión", "[0 - 2.5 Kg]", "1.204 Kgs"],
    ["Conversión Nanotecnológica", "13-01-2025 12:53", "pH", "[1 - 14]", "4.852"],
    ["Conversión Nanotecnológica", "13-01-2025 12:53", "Conductividad", "[0 - 250 µs]", "4.164 mS"],
    ["Anillo Soft Rain ADVANCED", "13-01-2025 12:53", "Marcha ON ADVANCED", "N/A", "1.002"],
    ["Anillo Soft Rain ADVANCED", "13-01-2025 12:53", "pH", "[1 - 14]", "6.196"],
    ["Anillo Soft Rain ADVANCED", "13-01-2025 12:53", "Conductividad", "[0 - 250 µs]", "9.141 µs"],
    ["Horno de secado", "13-01-2025 12:53", "Temperatura Real Horno", "[0 - 180 ºC]", "160 ºC"],
    ["Horno de secado", "13-01-2025 12:53", "Temperatura Consigna", "[0 - 180 ºC]", "160 ºC"],
    ["Horno de Polimerizado (entrada)", "13-01-2025 12:53", "Temperatura Consigna Q1", "[0 - 230 ºC]", "215 ºC"],
    ["Horno de Polimerizado (entrada)", "13-01-2025 12:53", "Temperatura Consigna Q2", "N/A", "null"],
    ["Horno de Polimerizado (entrada)", "13-01-2025 12:53", "Temperatura Real Horno Q1", "[0 - 230 ºC]", "197.262 ºC"],
    ["Horno de Polimerizado (salida)", "13-01-2025 12:53", "Temperatura Consigna Q2", "[0 - 230 ºC]", "160 ºC"],
    ["Horno de Polimerizado (salida)", "13-01-2025 12:53", "Temperatura Real Horno Q2", "[0 - 230 ºC]", "155.313 ºC"],
    ["Velocidad Cadena", "13-01-2025 12:53", "Velocidad Cadena", "[0 - 3.5 m/min]", "1.495 m/min"],
    ["Vertido", "13-01-2025 12:53", "OP14_VER_PH", "N/A", "8.635"],
    ["Vertido", "13-01-2025 12:53", "OP14_VER_TUR", "N/A", "2.173"],
    ["Vertido", "13-01-2025 12:53", "OP14_VER_COND", "N/A", "588"],
    ["Chimenea", "13-01-2025 12:53", "CH_TTS", "N/A", "159.298"],
    ["Chimenea", "13-01-2025 12:53", "CH_1HP", "N/A", "409"],
    ["Chimenea", "13-01-2025 12:53", "CH_2HP", "N/A", "139.761"],
]
df_base = pd.DataFrame(data, columns=["Proceso", "Fecha", "Parámetro", "Rango", "Valor"])
rows = []
num_mediciones = 5000
for _, row in df_base.iterrows():
    try:
        rango = row["Rango"]
        rango_min, rango_max = [float(val.replace("N/A", "0").split()[0]) for val in rango.strip("[]").split("-")]
    except:
        rango_min, rango_max = 0, 100
    for i in range(num_mediciones):
        fecha = datetime.strptime(row["Fecha"], "%d-%m-%Y %H:%M") + timedelta(minutes=i)
        valor = np.random.uniform(rango_min, rango_max * 1.25)
        alerta = 1 if valor > rango_max else 0
        rows.append([row["Proceso"], fecha.strftime("%d-%m-%Y %H:%M"), row["Parámetro"], rango, valor, alerta])
df_final = pd.DataFrame(rows, columns=["Proceso", "Fecha", "Parámetro", "Rango", "Valor", "Alerta"])
opciones = ['2025/10', '2025/12', '2025/11']
df_final['OF'] = [random.choice(opciones) for _ in range(len(df_final))]
df_final['OF'] = df_final['OF'].str[:7]
def eliminar_filas_aleatoriamente(df,num):
    indices_a_eliminar = random.sample(df.index.tolist(), num)
    df_filtrado = df.drop(indices_a_eliminar)
    return df_filtrado
df_final = eliminar_filas_aleatoriamente(df_final, random.randint(50, 100))
df_final.to_excel('datos.xlsx')
