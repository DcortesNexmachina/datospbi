import requests
import pandas as pd
from openpyxl import Workbook
from openpyxl import load_workbook
import math
import os
import datetime
from datetime import datetime, timedelta
def obtener_token(apikey):
    url = f"https://publicevoapi.iqmenic.com/login/?apikey={apikey}"
    response = requests.get(url)
    if response.status_code == 200:
        token = response.json().get('token')
        return token
    return None
def obtener_datos_sensor(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None
def obtener_sensor_names_and_ids(token):
    if token:
        url = f'https://publicevoapi.iqmenic.com/currentUser/getSensors?token={token}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('data', [])
            sensor_names_ids = {sensor['nombre']: sensor['id'] for sensor in data}
            return sensor_names_ids
    return None
url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/"
fecha_inicial = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SUTC')
fecha_final = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SUTC')
def clima(fecha_inicial, fecha_final):
      response = requests.get(url + f"fechaini/{fecha_inicial}/fechafin/{fecha_final}/estacion/3494U/?api_key=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkYXZpZGNvcnRlczE5OTlAZ21haWwuY29tIiwianRpIjoiYzFkZmYwMzgtY2U5Yi00NjgzLThjZGYtZGQ1NWUzMmE3NTFkIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2OTQ5NDIyNzIsInVzZXJJZCI6ImMxZGZmMDM4LWNlOWItNDY4My04Y2RmLWRkNTVlMzJhNzUxZCIsInJvbGUiOiIifQ.yLHdkZEzAy_eiy05qCWOt-i_D-kTAOXa3a-Jj8GcQ08")
      if response.status_code == 200:
          data = response.json()
          datos_url = data.get("datos")
          if datos_url:
              datos_response = requests.get(datos_url)
              data = datos_response.json()
              df = pd.DataFrame(data)
              return df
apikey = '$2y$10$o.4qTAis/dWvoBx99weIqu83Y60vTXa38sSfJKfuuFFiXN1Wcw0Li'
token = obtener_token(apikey)
locations = {}
dfs = []
if token:
    url_sensor_id = f'https://publicevoapi.iqmenic.com/currentUser/getSensors?token={token}'
    sensores = obtener_sensor_names_and_ids(token)
    sensores1 = list({k: v for k, v in sensores.items() if k.startswith('CO2')}.values())
    for sensor_id in sensores1:
        url_datos_sensor = f"https://publicevoapi.iqmenic.com/sensor/getSensor?token={token}&sensorid={sensor_id}"
        datos_sensor = obtener_datos_sensor(url_datos_sensor)
        if datos_sensor:
            ubi = (datos_sensor.get("data", {}).get("lat"),
                   datos_sensor.get("data", {}).get("lon"))
            latitud = ubi[0]
            longitud = ubi[1]
            locations[f'{sensor_id}'] = (latitud, longitud)
        propiedad_ids = [propiedad.get("propiedadid") for propiedad in datos_sensor.get("data", {}).get("propiedades", [])]
        for propiedad_id in propiedad_ids:
            url_datos_completos = f"https://publicevoapi.iqmenic.com/sensor/getData?token={token}&sensorid={sensor_id}&propiedadid={propiedad_id}&intervalo=30"
            datos_completos = obtener_datos_sensor(url_datos_completos)
            if datos_completos:
                valores = datos_completos['data'][0]['valores']
                nombre_propiedad = datos_completos['data'][0]['nombre']
                df = pd.DataFrame(valores)
                df['Propiedad'] = nombre_propiedad
                df['Sensor'] = {v: k for k, v in sensores.items()}[sensor_id]
                dfs.append(df)
            else:
                print(f"No se pudo obtener los datos de la propiedad {propiedad_id}.")
df_merged = pd.concat(dfs, ignore_index=True)
df_merged['fecha'] = pd.to_datetime(df_merged['fecha'])
df_merged.drop(columns=['sensorpropiedadesid', 'valorderango', 'alerta'], axis=1, inplace=True, errors='ignore')
if len(df_merged) == (df_merged['valorrecibido'] == df_merged['valorcalculado']).value_counts()[0]:
    df_merged.drop(columns=['valorcalculado'], axis=1, inplace=True, errors='ignore')
df_merged = df_merged[df_merged['Propiedad'] != 'Batería']
df_merged = df_merged.drop_duplicates()
df_merged.reset_index(drop=True)
dfCO2 = df_merged[df_merged['Propiedad']=='CO2']
dfCO2 = dfCO2.copy()
dfCO2['Dia'] = dfCO2['fecha'].dt.date
dfCO2['Hora'] = dfCO2['fecha'].dt.time
dfCO2['fecha'] = dfCO2['fecha']
media_valorrecibido = dfCO2['valorrecibido'].mean()
filas_superan_media = dfCO2[dfCO2['valorrecibido'] > media_valorrecibido]
filas_superan_media = filas_superan_media.copy()
filas_superan_media['Hora'] = filas_superan_media['fecha'].dt.time
tabla_resultado = filas_superan_media[['fecha', 'Sensor', 'Hora']]
tabla_resultado = tabla_resultado.reset_index(drop=True)
dfCO2 = df_merged[df_merged['Propiedad']=='CO2']
dfCO2 = dfCO2.copy()
dfCO2.loc[:, 'Dia'] = dfCO2['fecha'].dt.date
dfCO2.loc[:, 'Hora'] = dfCO2['fecha'].dt.time
dfCO2.loc[:, 'fecha'] = dfCO2['fecha']
media_valorrecibido = dfCO2['valorrecibido'].mean()
filas_superan_media = dfCO2[dfCO2['valorrecibido'] > media_valorrecibido]
filas_superan_media = filas_superan_media.copy()
filas_superan_media.loc[:, 'Hora'] = filas_superan_media['fecha'].dt.time
tabla_resultado = filas_superan_media[['fecha', 'Sensor', 'Hora', 'valorrecibido']]
tabla_resultado = tabla_resultado.reset_index(drop=True)
dfCO2.loc[:, 'ventilado'] = False
bajadas = []
dfCO2 = dfCO2.reset_index(drop=True)
for i in range(len(dfCO2) - 1):
    if dfCO2['valorrecibido'][i] > 1.1 * dfCO2['valorrecibido'][i + 1]:
        dfCO2.at[i + 1, 'ventilado'] = True
        porcentaje_bajada = ((dfCO2['valorrecibido'][i] - dfCO2['valorrecibido'][i + 1]) / dfCO2['valorrecibido'][i]) * 100
        bajadas.append(porcentaje_bajada)
porcentaje_medio_bajada = sum(bajadas) / len(bajadas) if bajadas else 0
suma_por_fecha_sensor = []
for i in range(len(dfCO2)):
    if dfCO2.at[i, 'ventilado']:
        suma = dfCO2.loc[(dfCO2['fecha'].dt.date == dfCO2['fecha'][i].date()) & (dfCO2['Sensor'] == dfCO2['Sensor'][i]), 'valorrecibido'].sum()
        suma_por_fecha_sensor.append({'fecha': dfCO2['fecha'][i].date(), 'Sensor': dfCO2['Sensor'][i], 'ppm CO2': suma* 0.78 * porcentaje_medio_bajada, 'kg CO2':(suma* 0.78 * porcentaje_medio_bajada / 816.33) / 1000})
df_suma_co2 = pd.DataFrame(suma_por_fecha_sensor)
datos_personas_fecha = {'Personas': [], 'fecha': [], 'Sensor': []}
for sensor in set(tabla_resultado['Sensor']):
    df_sensor = tabla_resultado[tabla_resultado['Sensor'] == sensor]
    for fecha in df_sensor['fecha'].dt.date.unique():
        df_fecha = df_sensor[df_sensor['fecha'].dt.date == fecha]
        if not df_fecha.empty:
            ventilacion = round(100 - (100 * len(df_fecha) / len(dfCO2[dfCO2['fecha'].dt.date == fecha]))) # Calculo de ventilación por día
            n_personas = (ventilacion * (max(dfCO2['valorrecibido']) - min(dfCO2['valorrecibido']))) / 358.3
            datos_personas_fecha['fecha'].append(fecha)
            datos_personas_fecha['Personas'].append(round(n_personas))
            datos_personas_fecha['Sensor'].append(sensor)
df_n_personas = pd.DataFrame(datos_personas_fecha)
tabla_porcentajes = {'fecha': [], 'Sensor': [], 'Porcentaje_ventilacion': []}
for sensor in set(tabla_resultado['Sensor']):
    for fecha in set(tabla_resultado['fecha'].dt.date):
        subtabla = tabla_resultado[(tabla_resultado['Sensor'] == sensor) & (tabla_resultado['fecha'].dt.date == fecha)]
        num_ventilaciones = len(subtabla)
        num_registros_dia = len(dfCO2[dfCO2['fecha'].dt.date == fecha])
        porcentaje = round(100-(num_ventilaciones / num_registros_dia) * 100)
        tabla_porcentajes['Sensor'].append(sensor)
        tabla_porcentajes['fecha'].append(fecha)
        tabla_porcentajes['Porcentaje_ventilacion'].append(porcentaje)
df_tabla_porcentajes = pd.DataFrame(tabla_porcentajes)
def historico():
  archivos_content = os.listdir()
  archivos_nex = [archivo for archivo in archivos_content if archivo.startswith('nex')]
  dfs = []
  for nombre_archivo in archivos_nex:
      try:
          if nombre_archivo.endswith('.csv'):
            df_nex = pd.read_csv(nombre_archivo)
            df_nex.drop(columns=['identificativo', 'alerta'], axis=1, errors='ignore', inplace=True)
            df_nex.columns = ['Propiedad', 'valorrecibido', 'fecha']
            df_nex = df_nex[df_nex['Propiedad'] != 'VOLT']
            df_nex = df_nex[df_nex['Propiedad'] != 'RSSI']
            df_nex['fecha'] = pd.to_datetime(df_nex['fecha'], format='%Y-%m-%d %H:%M:%S')
            df_nex['valorrecibido'] = pd.to_numeric(df_nex['valorrecibido'], errors='coerce', downcast='integer')
            df_nex['Sensor'] = None
            df_nex = df_nex[['fecha', 'valorrecibido', 'Propiedad', 'Sensor']]
      except pd.errors.EmptyDataError:
          pass
      except pd.errors.ParserError:
          pass
      except FileNotFoundError:
          pass
      except Exception as e:
          pass
  if len(dfs) == 0:
    df_final = pd.DataFrame()
  else:
    df_final = pd.concat(dfs, ignore_index=True)
  return df_final
if len(historico())>0:
  df_merged = pd.concat([df_merged, historico()], ignore_index=True)
nombre_archivo = 'sensor_data.xlsx'
if os.path.isfile(nombre_archivo):
  with pd.ExcelWriter(nombre_archivo, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
      df_tabla_porcentajes=df_tabla_porcentajes.drop_duplicates()
      df_suma_co2=df_suma_co2.drop_duplicates()
      df_n_personas=df_n_personas.drop_duplicates()
      df_merged=df_merged.drop_duplicates()
      if 'Porcentaje_Ventilacion' in writer.sheets:
          existing_data = pd.read_excel(nombre_archivo, sheet_name='Porcentaje_Ventilacion')
          existing_data = existing_data.drop_duplicates()
          existing_data['fecha'] = pd.to_datetime(existing_data['fecha'], format= '%Y-%m-%d')
          combined_data = pd.concat([existing_data, df_tabla_porcentajes])
          combined_data['fecha'] = pd.to_datetime(combined_data['fecha'], format= '%Y-%m-%d')
          combined_data['fecha'] = combined_data['fecha'].drop_duplicates()
          combined_data = combined_data.dropna()
          combined_data.to_excel(writer, sheet_name='Porcentaje_Ventilacion', index=False)
      if 'CO2 emitido' in writer.sheets:
          existing_data = pd.read_excel(nombre_archivo, sheet_name='CO2 emitido')
          existing_data = existing_data.drop_duplicates()
          existing_data['fecha'] = pd.to_datetime(existing_data['fecha'], format= '%Y-%m-%d')
          combined_data = pd.concat([existing_data, df_suma_co2])
          combined_data['fecha'] = pd.to_datetime(combined_data['fecha'], format= '%Y-%m-%d')
          combined_data['fecha'] = combined_data['fecha'].drop_duplicates()
          combined_data = combined_data.dropna()
          combined_data.to_excel(writer, sheet_name='CO2 emitido', index=False)
      if 'NPersonas' in writer.sheets:
          existing_data = pd.read_excel(nombre_archivo, sheet_name='NPersonas')
          existing_data = existing_data.drop_duplicates()
          try:
            existing_data['fecha'] = pd.to_datetime(existing_data['fecha'], format= '%Y-%m-%d')
          except KeyError:
            existing_data['fecha'] = pd.to_datetime(existing_data['Fecha'], format= '%Y-%m-%d')
          combined_data = pd.concat([existing_data, df_n_personas])
          combined_data.drop_duplicates(subset='fecha')
          combined_data.to_excel(writer, sheet_name='NPersonas', index=False)
      for i in set(tabla_resultado['Sensor']):
        tabla = tabla_resultado[tabla_resultado['Sensor'] == i].sort_values(by='valorrecibido').tail(10)
        tabla.to_excel(writer, sheet_name=f'Tramos{i}', index=False)
      if 'propiedades' in writer.sheets:
          existing_data = pd.read_excel(nombre_archivo, sheet_name='propiedades')
          existing_data = existing_data.drop_duplicates()
          existing_data['fecha'] = pd.to_datetime(existing_data['fecha'], format= '%Y-%m-%d')
          df_merged = df_merged.drop_duplicates()
          combined_data = pd.concat([existing_data, df_merged])
          combined_data['fecha'] = pd.to_datetime(combined_data['fecha'], format= '%Y-%m-%d')
          combined_data.drop_duplicates(subset='fecha')
          if not combined_data.equals(existing_data):
              combined_data.to_excel(writer, sheet_name='propiedades', index=False)
          else:
              combined_data['fecha'] = combined_data['fecha'].drop_duplicates()
              combined_data = combined_data.dropna()
              combined_data.to_excel(writer, sheet_name='propiedades', index=False)
      else:
          df_merged.to_excel(writer, sheet_name='propiedades', index=False)
      if 'Aemet_Nuñomoral' in writer.sheets:
          existing_data1 = pd.read_excel(nombre_archivo, sheet_name='Aemet_Nuñomoral')
          existing_data1 = existing_data1.drop_duplicates()
          existing_data1['fecha'] = pd.to_datetime(existing_data1['fecha'], format= '%Y-%m-%d')
          new_data = clima(fecha_inicial, fecha_final)
          combined_data = pd.concat([existing_data1, new_data])
          combined_data['fecha'] = pd.to_datetime(combined_data['fecha'], format= '%Y-%m-%d')
          combined_data.drop_duplicates(subset='fecha', inplace=True)
          combined_data.to_excel(writer, sheet_name='Aemet_Nuñomoral', index=False)
      else:
          new_data = clima(fecha_inicial, fecha_final)
          if len(new_data)>0:
            new_data = new_data.copy()
            new_data.drop(columns=['horatmin', 'horatmax', 'horaracha', 'horaHrMax', 'horaHrMin'], axis=1, inplace=True, errors='ignore')
            new_data['fecha'] = pd.to_datetime(new_data['fecha'], format= '%Y-%m-%d')
            new_data.to_excel(writer, sheet_name=f'Aemet_Nuñomoral', index=False)
else:
  with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
      df_tabla_porcentajes.to_excel(writer, sheet_name=f'Porcentaje_Ventilacion', index=False)
      df_suma_co2.to_excel(writer, sheet_name='CO2 emitido', index=False)
      df_n_personas.to_excel(writer, sheet_name='NPersonas', index=False)
      for i in set(tabla_resultado['Sensor']):
        tabla = tabla_resultado[tabla_resultado['Sensor'] == i].sort_values(by='valorrecibido').tail(10)
        tabla.to_excel(writer, sheet_name=f'Tramos{i}', index=False)
      df_merged.to_excel(writer, sheet_name='propiedades', index=False)
      new_data = clima(fecha_inicial, fecha_final)
      if len(new_data)>0:
        new_data = new_data.copy()
        new_data.drop(columns=['horatmin', 'horatmax', 'horaracha', 'horaHrMax', 'horaHrMin'], axis=1, inplace=True, errors='ignore')
        new_data['fecha'] = pd.to_datetime(new_data['fecha'], format= '%Y-%m-%d')
        new_data.to_excel(writer, sheet_name=f'Aemet_Nuñomoral', index=False)
datos = pd.read_excel(nombre_archivo, sheet_name='Aemet_Nuñomoral')
datos.drop_duplicates(subset='fecha', inplace=True)
with pd.ExcelWriter(nombre_archivo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    datos.to_excel(writer, sheet_name='Aemet_Nuñomoral', index=False)
datos1 = pd.read_excel(nombre_archivo, sheet_name='propiedades')
datos1.drop_duplicates(inplace=True)
with pd.ExcelWriter(nombre_archivo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    datos1.to_excel(writer, sheet_name='propiedades', index=False)
