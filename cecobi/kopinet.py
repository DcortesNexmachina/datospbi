#usr/lib/python3
import numpy as np
import os
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
dias_semana = {'Monday': 'Lunes','Tuesday': 'Martes','Wednesday': 'Miércoles','Thursday': 'Jueves','Friday': 'Viernes','Saturday': 'Sábado','Sunday': 'Domingo'}
orden_dias = {'Monday': 1,'Tuesday': 2,'Wednesday': 3,'Thursday': 4,'Friday': 5,'Saturday': 6,'Sunday': 7}
def obtener_token(apikey):
    url = f"https://publicevoapi.iqmenic.com/login/?apikey={apikey}"
    response = requests.get(url)
    return response.json().get('token') if response.ok else None
def obtener_datos(url):
    response = requests.get(url)
    return response.json() if response.ok else None
def obtener_sensor_names_and_ids(token):
    url = f'https://publicevoapi.iqmenic.com/currentUser/getSensors?token={token}'
    data = obtener_datos(url)
    return {sensor['nombre']: sensor['id'] for sensor in data.get('data', [])} if data else {}
def obtener_datos_sensor_y_propiedades(token, sensor_id, sensor_nombre):
    url_datos_sensor = f"https://publicevoapi.iqmenic.com/sensor/getSensor?token={token}&sensorid={sensor_id}"
    datos_sensor = obtener_datos(url_datos_sensor)
    if datos_sensor:
        data = datos_sensor.get("data", {})
        propiedad_ids = [propiedad["propiedadid"] for propiedad in data.get("propiedades", [])]
        result = [
            pd.DataFrame(item.get('valores', [])).assign(
                Propiedad=item.get('nombre', 'Desconocido'),
                Sensor=sensor_nombre
            )
            for propiedad_id in propiedad_ids
            for item in obtener_datos(
                f"https://publicevoapi.iqmenic.com/sensor/getData?token={token}&sensorid={sensor_id}&propiedadid={propiedad_id}&intervalo=30"
            ).get('data', [])
        ]
        return sensor_id, result
    return sensor_id, []
apikey = '$2y$10$nrBoG48t1qYmOIIPTvnKRuKWqSNgNOdTxY4M1N23jXqUO2.4ScogO'
token = obtener_token(apikey)
locations, dfs = {}, []
if token:
    sensores = obtener_sensor_names_and_ids(token)
    aforadores = dict(filter(lambda item: str(item[0]).startswith('Aforador_(012) Kopinet'), sensores.items()))
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(obtener_datos_sensor_y_propiedades, token, sensor_id, sensor_nombre): sensor_id
                   for sensor_nombre, sensor_id in aforadores.items()}
        results = [future.result() for future in as_completed(futures)]
        dfs = [df for _, data_frames in results for df in data_frames]
else:
    print("Token no válido o no se pudo obtener.")
df = pd.concat(dfs, ignore_index=True)
df =  df[(df['Propiedad'] == 'Conteo de Entrada Total (1)') | (df['Propiedad'] == 'Conteo de Salida Total (1)')]
df.drop(columns = ['Sensor', 'sensorpropiedadesid'], inplace=True, errors='ignore')
df['fecha'] = pd.to_datetime(df['fecha'])
df['Fecha_Sólo'] = df['fecha'].dt.date
df['Hora'] = df['fecha'].dt.hour
grouped = df.groupby(['Fecha_Sólo', 'Hora', 'Propiedad'], as_index=False).agg(
    totalEntradas=('valorrecibido', lambda x: x[df['Propiedad'] == 'Conteo de Entrada Total (1)'].sum()),
    totalSalidas=('valorrecibido', lambda x: x[df['Propiedad'] == 'Conteo de Salida Total (1)'].sum()))
grouped['desde'] = grouped['Hora']
grouped['hasta'] = grouped['Hora'] + 1
grouped['fecha'] = grouped['Fecha_Sólo'].astype(str)
result = grouped[['fecha', 'desde', 'hasta', 'totalEntradas', 'totalSalidas']]
result['comercio'] = 'Kopinet'
result['comercioID'] = 16010101
orden = ['fecha', 'comercioID','comercio','desde', 'hasta', 'totalEntradas', 'totalSalidas']
result = result[orden]
file_path = '/home/ubuntu/kopinet.xlsx'
result['Tramos'] = result.apply(lambda row: f"{row['desde']}:00 - {row['hasta']}:00", axis=1)
for i in range(len(result)):
  if len(result.loc[i,'Tramos']) < 12:
      result.loc[i,'Tramos'] = '0' + str(result.loc[i,'Tramos'])
  if len(result.loc[i,'Tramos']) == 12:
      result.loc[i,'Tramos'] =  result.loc[i,'Tramos'][:8] + '0' + result.loc[i,'Tramos'][-4:]
result.loc[result['Tramos'] == '9:00 - 100:00', 'Tramos'] = '09:00 - 10:00'
result = result.sort_values(by=['fecha', 'Tramos']).reset_index(drop=True)
dia_en_ingles = pd.to_datetime(result['fecha']).dt.day_name()
result['Día de la Semana'] = dia_en_ingles.map(dias_semana)
result['Orden'] = dia_en_ingles.map(orden_dias)
result['L-V'] = result['Día de la Semana'].apply(lambda x: 'L-V' if x in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] else 'Fin de Semana')
result = pd.concat([grupo for _, grupo in result.groupby('comercioID')])
result = pd.concat([grupo for _, grupo in result.groupby('comercioID')])
df_final = result.reset_index(drop=True)
df_final = df_final.drop_duplicates(subset=['fecha', 'comercioID', 'comercio', 'desde', 'hasta', 'totalEntradas'], keep='first')
df_final = df_final.reset_index(drop=True)
df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]
df_final['fecha'] = pd.to_datetime(df_final['fecha'])
df_final = df_final.dropna()
df_final = pd.concat([grupo for _, grupo in df_final.groupby('comercioID')])
df_final = df_final.sort_values(by=['fecha', 'Tramos']).reset_index(drop=True)
df_final = df_final.reset_index(drop=True)
df_final = df_final.groupby('comercio', group_keys=False)
result = []
for i, j in df_final:
    j_sorted = j.sort_values(by = ['fecha', 'Tramos'])
    result.append(j_sorted)
final_result = pd.concat(result)
final_result.reset_index(drop=True, inplace=True)
df_final = final_result
df_final['Entradas'] = abs(np.append([df_final['totalEntradas'].iloc[0]], np.diff(df_final['totalEntradas'])))
df_final['Salidas'] = np.append([df_final['totalSalidas'].iloc[0]], np.diff(df_final['totalSalidas']))
df_final['Balanceo'] = df_final['Entradas'] - df_final['Salidas']
df_final['Column1'] = df_final['Entradas']
if os.path.exists(file_path):
    existing_df = pd.read_excel(file_path)
    df_combined = pd.concat([existing_df, df_final], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=['fecha', 'comercioID', 'desde', 'hasta'], keep='last')
else:
    df_combined = result
with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
      df_combined.to_excel(writer, index=False, sheet_name='Sheet1')
df_combined.drop(columns='Unnamed: 0',inplace=True, errors='ignore')
df1 = pd.read_excel('/var/www/html/proyectos/cecobi/bbddCECOBI.xlsx')
df_combined = df_combined[df_combined['comercioID']==16010101]
df = pd.concat([df1,df_combined], ignore_index=True)
with pd.ExcelWriter('/var/www/html/proyectos/cecobi/bbddCECOBI.xlsx', engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
     df.to_excel(writer, index=False, sheet_name='Sheet1')
