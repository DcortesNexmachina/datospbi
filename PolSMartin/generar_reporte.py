import requests
import pandas as pd
import os
import numpy as np
from dotenv import load_dotenv
load_dotenv("/var/www/html/.env")
bb = '/var/www/html/PolSMartin'
bbdd = os.path.join(bb, 'sensores.xlsx')
sensores = ['4135', '4136', '4137', '4138', '4139', '4141']
if os.path.exists(bbdd):
    try:
        hojas = pd.read_excel(bbdd, sheet_name=None)
        hojas = {name: df for name, df in hojas.items() if name in sensores}
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        hojas = {}
else:
    hojas = {}
datos = pd.concat(hojas.values(), ignore_index=True) if hojas else pd.DataFrame()

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from iqmenic import IQmenic
apikey = os.getenv("POLSMARTIN")
async def dataframe(apikey):
    async with IQmenic(apikey) as iqmenic:
        df = await iqmenic.get_all()
        return df
datos1 = asyncio.run(dataframe(apikey)) 
if not datos.empty:
    datos = datos[datos['Sensor'].notna()]
    datos1 = pd.concat([datos, datos1], ignore_index=True).drop_duplicates()
datos_df = pd.DataFrame.from_dict({key: {'Sensor': key, 'Latitud': value[0], 'Longitud': value[1]} for key, value in locations.items()},orient='index').reset_index(drop=True)
coches = datos1[datos1['Sensor'].isin(['4139'])]
coches.loc[:, 'fecha'] = pd.to_datetime(coches['fecha'], errors='coerce')
coches['fecha'] = pd.to_datetime(coches['fecha'])
coches.reset_index(drop=True, inplace=True)
coches = coches[(coches['Propiedad']!= 'Voltaje')&(coches['Propiedad']!= 'Izquierda a Derecha Vehículos - Total Diario')&(coches['Propiedad']!= 'Derecha a Izquierda Vehículos - Total Diario')]
coches.drop(columns=['sensorpropiedadesid', 'valorcalculado', 'alerta', 'valorderango', 'Sensor'], axis=1, inplace=True, errors='ignore')
coches['Hora'] = coches['fecha'].dt.hour
coches['Dia de la Semana'] = coches['fecha'].dt.day_name()
dias_semana_dict = {'Monday': 'Lunes','Tuesday': 'Martes','Wednesday': 'Miércoles','Thursday': 'Jueves','Friday': 'Viernes','Saturday': 'Sábado','Sunday': 'Domingo'}
coches['Dia de la Semana'] = coches['Dia de la Semana'].map(dias_semana_dict)
coches['L-V'] = np.where(coches['fecha'].dt.dayofweek < 5, 'L-V', 'Fin de Semana')
condiciones = [coches['Propiedad'].astype(str).str.contains('1'),coches['Propiedad'].astype(str).str.contains('2'),coches['Propiedad'].astype(str).str.contains('3'),coches['Propiedad'].astype(str).str.contains('4')]
valores = ['Motos/Bicicletas','Turismos','Furgonetas / Ttes. Ligeros','Camiones / Ttes. Pesados']
coches['Tipo'] = np.select(condiciones, valores, default='Pedestrian')
contenedor = datos1[datos1['Sensor'].isin(['4135', '4136', '4137', '4141'])]
contenedor.loc[:, 'fecha'] = pd.to_datetime(contenedor['fecha'], errors='coerce')
contenedor = contenedor[contenedor['Propiedad']== 'Llenado contenedor (T175)']
contenedor = contenedor.sort_values(by='fecha')
df_merged = contenedor.drop_duplicates()
df_merged.reset_index(drop=True)
if len(df_merged) == (df_merged['valorrecibido'] == df_merged['valorcalculado']).value_counts()[0]:
    df_merged.drop(columns=['valorrecibido'], axis=1, inplace=True, errors='ignore')
df_merged = df_merged[df_merged['valorcalculado']<=100]
df_merged = df_merged[df_merged['valorcalculado']>=0]
df_merged = df_merged.reset_index(drop=True)
df_merged.drop(columns=['sensorpropiedadesid', 'valorderango', 'alerta'], axis=1, inplace=True, errors='ignore')
dfs = {}
for sensor in set(df_merged['Sensor']):
    df_sensor = df_merged[df_merged['Sensor'] == sensor].copy()
    df_sensor.sort_values(by='fecha', inplace=True)
    df_sensor = df_sensor.reset_index(drop=True)
    dfs[sensor] = df_sensor

def remove_outliers_daily(group):
    Q1 = group['valorcalculado'].quantile(0.25)
    Q3 = group['valorcalculado'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return group[(group['valorcalculado'] >= lower_bound) & (group['valorcalculado'] <= upper_bound)]

def remove_spikes(df):
    values = df['valorcalculado_suavizado'].values
    cleaned_values = []
    for i in range(1, len(values) - 1):
        if (values[i] > values[i-1]) and (values[i+1] < values[i-1]):
            continue
        cleaned_values.append(values[i])
    cleaned_values.insert(0, values[0])
    cleaned_values.append(values[-1])
    return pd.Series(cleaned_values)
from scipy.ndimage import uniform_filter1d
from scipy.signal import argrelextrema
recogidas_data = []
for i in list(dfs.keys()):
  data = dfs[i]
  df_merged1 = pd.DataFrame(data)
  df_merged1['fecha'] = pd.to_datetime(df_merged1['fecha'])
  df_contenedores = df_merged1
  df_contenedores_filtered = df_contenedores.groupby(df_contenedores['fecha'].dt.date).apply(remove_outliers_daily).reset_index(drop=True)
  df_contenedores_filtered['valorcalculado_suavizado'] = uniform_filter1d(df_contenedores_filtered['valorcalculado'], size=25)
  if df_contenedores_filtered.empty:
    break
  df_contenedores_filtered['valorcalculado_suavizado'] = remove_spikes(df_contenedores_filtered)
  max_indices = argrelextrema(df_contenedores_filtered['valorcalculado_suavizado'].values, np.greater)[0]
  min_indices = argrelextrema(df_contenedores_filtered['valorcalculado_suavizado'].values, np.less)[0]
  best_recogida_diff = float('-inf')
  best_fecha_recogida = None
  best_porcentaje_recogida = None
  best_porcentaje_tras_recogida = None
  best_sensor = None
  for max_idx in max_indices:
      for min_idx in min_indices:
          if min_idx > max_idx:
              porcentaje_recogida = df_contenedores_filtered.iloc[max_idx]['valorcalculado_suavizado']
              porcentaje_tras_recogida = df_contenedores_filtered.iloc[min_idx]['valorcalculado_suavizado']
              if porcentaje_tras_recogida < 30 and porcentaje_recogida > porcentaje_tras_recogida:
                  recogida_diff = porcentaje_recogida - porcentaje_tras_recogida
                  if recogida_diff > best_recogida_diff:
                      best_recogida_diff = recogida_diff
                      best_fecha_recogida = df_contenedores_filtered.iloc[max_idx]['fecha']
                      best_porcentaje_recogida = porcentaje_recogida
                      best_porcentaje_tras_recogida = porcentaje_tras_recogida
                      best_sensor = df_contenedores_filtered.iloc[max_idx]['Sensor']
                  break
  recogidas_data.append({'Fecha de recogida': best_fecha_recogida,
                                        'Porcentaje en el que se recoge': best_porcentaje_recogida,
                                        'Porcentaje tras la recogida': best_porcentaje_tras_recogida,
                                        'Sensor': best_sensor})
coches['Izquierda a Derecha Vehículos'] = None
coches['Derecha a Izquierda Vehículos'] = None
if len(recogidas_data)>0:
  df_recogidas = pd.DataFrame(recogidas_data)
  meteo = datos1[datos1['Sensor'].isin(['4138'])]
  meteo.loc[:, 'fecha'] = pd.to_datetime(meteo['fecha'], errors='coerce')
  meteo = meteo[meteo['Propiedad']!= 'RSSI']
  meteo = meteo.pivot_table(index='fecha', columns='Propiedad', values='valorrecibido', aggfunc='first').reset_index()
  with pd.ExcelWriter(bbdd) as writer:
      contenedor.to_excel(writer, sheet_name='Contenedor', index=False)
      meteo.to_excel(writer, sheet_name='Meteo', index=False)
      coches.to_excel(writer, sheet_name='Coches', index=False)
      datos_df.to_excel(writer, sheet_name='Locations', index=False)
      df_recogidas.to_excel(writer, sheet_name='Recogidas', index=False)
else:
  meteo = datos1[datos1['Sensor'].isin(['4138'])]
  meteo.loc[:, 'fecha'] = pd.to_datetime(meteo['fecha'], errors='coerce')
  meteo = meteo[meteo['Propiedad']!= 'RSSI']
  meteo = meteo.pivot_table(index='fecha', columns='Propiedad', values='valorrecibido', aggfunc='first').reset_index()
  with pd.ExcelWriter(bbdd) as writer:
      contenedor.to_excel(writer, sheet_name='Contenedor', index=False)
      meteo.to_excel(writer, sheet_name='Meteo', index=False)
      coches.to_excel(writer, sheet_name='Vehiculos', index=False)
      datos_df.to_excel(writer, sheet_name='Locations', index=False)
