import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os
from dateutil.relativedelta import relativedelta
import requests
from bs4 import BeautifulSoup
def obtener_token(apikey):
    url = f"https://publicevoapi.iqmenic.com/login/?apikey={apikey}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('token')
    print(f"Error obteniendo token: {response.status_code}")
    return None
def obtener_datos_sensor(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    print(f"Error obteniendo datos del sensor: {response.status_code}")
    return None
def clima(fecha_inicial, fecha_final):
    url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/"
    response = requests.get(url + f"fechaini/{fecha_inicial}T00:01:00UTC/fechafin/{fecha_final}T23:59:00UTC/estacion/3182Y/?api_key=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkYXZpZGNvcnRlczE5OTlAZ21haWwuY29tIiwianRpIjoiYzFkZmYwMzgtY2U5Yi00NjgzLThjZGYtZGQ1NWUzMmE3NTFkIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2OTQ5NDIyNzIsInVzZXJJZCI6ImMxZGZmMDM4LWNlOWItNDY4My04Y2RmLWRkNTVlMzJhNzUxZCIsInJvbGUiOiIifQ.yLHdkZEzAy_eiy05qCWOt-i_D-kTAOXa3a-Jj8GcQ08")
    if response.status_code == 200:
        data = response.json()
        datos_url = data.get("datos")
        if datos_url:
            datos_response = requests.get(datos_url)
            if datos_response.status_code == 200:
                data = datos_response.json()
                df = pd.DataFrame(data)
                return df
    print("Error obteniendo datos climÃ¡ticos")
    return pd.DataFrame()
def obtener_datos_por_propiedad(token, propiedad_id):
    url_datos_completos = f"https://publicevoapi.iqmenic.com/sensor/getData?token={token}&sensorid=3837&propiedadid={propiedad_id}&intervalo=30"
    return obtener_datos_sensor(url_datos_completos)
def procesar_datos(df):
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
    df.drop(columns=['sensorpropiedadesid', 'valorderango', 'alerta'], axis=1, inplace=True, errors='ignore')
    df.drop(columns=['valorcalculado'], axis=1, inplace=True, errors='ignore')
    df = df[df['Propiedad'] != 'BaterÃ­a']
    df.drop_duplicates(inplace=True)
    return df
def historico():
    archivos_content = os.listdir()
    archivos_nex = [archivo for archivo in archivos_content if archivo.startswith('historico')]
    dfs = []
    for nombre_archivo in archivos_nex:
        try:
            if nombre_archivo.endswith('.csv'):
                df_nex = pd.read_csv(nombre_archivo, usecols=['Propiedad', 'valorrecibido', 'fecha'])
                df_nex = df_nex[~df_nex['Propiedad'].isin(['VOLT', 'RSSI'])]
                df_nex['fecha'] = pd.to_datetime(df_nex['fecha'], format='%Y-%m-%d %H:%M:%S')
                df_nex['valorrecibido'] = pd.to_numeric(df_nex['valorrecibido'], errors='coerce', downcast='integer')
                df_nex['Sensor'] = None
                dfs.append(df_nex[['fecha', 'valorrecibido', 'Propiedad', 'Sensor']])
        except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError):
            pass
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()
def aemet():
    archivos_content = os.listdir()
    archivos_nex = [archivo for archivo in archivos_content if archivo.startswith('aemet')]
    for nombre_archivo in archivos_nex:
        try:
            if nombre_archivo.endswith('.csv'):
                return pd.read_csv(nombre_archivo)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError):
            pass
    return pd.DataFrame()
apikey = '$2y$10$nrBoG48t1qYmOIIPTvnKRuKWqSNgNOdTxY4M1N23jXqUO2.4ScogO'
def obtener_token(apikey):
    url = f"https://publicevoapi.iqmenic.com/login/?apikey={apikey}"
    response = requests.get(url)
    if response.ok:
        return response.json().get('token')
    return None
def obtener_datos_sensor(url):
    response = requests.get(url)
    if response.ok:
        return response.json()
    return None
token = obtener_token(apikey)
locations = {}
dfs = []
if token:
    url = f"https://publicevoapi.iqmenic.com/sensor/getSensor?token={token}&sensorid=3837"
    datos_sensor = obtener_datos_sensor(url)
    if datos_sensor:
            ubi = (datos_sensor.get("data", {}).get("lat"), datos_sensor.get("data", {}).get("lon"))
            locations['3837'] = ubi
            propiedad_ids = [propiedad.get("propiedadid") for propiedad in datos_sensor.get("data", {}).get("propiedades", []) if propiedad.get("propiedadid") is not None]
            for propiedad_id in propiedad_ids:
                url_datos_completos = f"https://publicevoapi.iqmenic.com/sensor/getData?token={token}&sensorid=3837&propiedadid={propiedad_id}&intervalo=30"
                datos_completos = obtener_datos_sensor(url_datos_completos)
                if datos_completos:
                    valores = datos_completos['data'][0]['valores']
                    nombre_propiedad = datos_completos['data'][0]['nombre']
                    df = pd.DataFrame(valores)
                    df['Propiedad'] = nombre_propiedad
                    dfs.append(df)
                else:
                    print(f"No se pudo obtener los datos de la propiedad {propiedad_id}.")
    else:
            print(f"No se pudo obtener datos para el sensor.")
df_merged = pd.concat(dfs, ignore_index=True).drop_duplicates()
df_historico = historico()
df_aemet = aemet()
if not df_historico.empty:
    df_merged = pd.concat([df_merged, df_historico], ignore_index=True)
    df_merged.drop_duplicates(inplace=True)
    if df_merged.empty:
      df_merged = df_historico.drop_duplicates()
fecha_inicial = (datetime.now() - relativedelta(months=6)).strftime('%Y-%m-%d')
fecha_final = datetime.now().strftime('%Y-%m-%d')
new_data = clima(fecha_inicial, fecha_final)
if not new_data.empty:
    new_data.drop(columns=['horatmin', 'horatmax', 'horaracha', 'horaHrMax', 'horaHrMin'], axis=1, inplace=True, errors='ignore')
    new_data = pd.concat([new_data, df_aemet], ignore_index=True)
    new_data.drop_duplicates(inplace=True)
else:
    new_data = df_aemet.drop_duplicates()
def contexto():
  url = 'https://es.weatherspark.com/y/36938/Clima-promedio-en-Arganda-del-Rey-Espa%C3%B1a-durante-todo-el-a%C3%B1o'
  response = requests.get(url)
  if response.status_code == 200:
      soup = BeautifulSoup(response.content, 'html.parser')
      tabla_lluvia = soup.find_all('table', class_='table table-striped table-condensed table-hover nowrap')[3]
      lluvia_mensual = [float(celda.text.replace(',', '.').replace('mm', '').strip()) for celda in tabla_lluvia.find('tbody').find_all('tr')[0].find_all('td')[1:]]
      tabla_dias_lluvia = soup.find_all('table', class_='table table-striped table-condensed table-hover nowrap')[2]
      dias_lluvia = [float(celda.text.replace(',', '.').replace('d', '').strip()) for celda in tabla_dias_lluvia.find('tbody').find_all('tr')[0].find_all('td')[1:]]
      tabla_temperaturas = soup.find_all('table', class_='table table-striped table-condensed table-hover nowrap')[0]
      filas = tabla_temperaturas.find('tbody').find_all('tr')
      temperaturas = {}
      for fila in filas:
          celdas = fila.find_all('td')
          tipo = celdas[0].text.strip()
          temp_mensual = [float(celda.text.replace('°C', '').replace(',', '.').strip()) for celda in celdas[1:]]
          temperaturas[tipo] = temp_mensual
      tabla_viento = soup.find_all('table', class_='table table-striped table-condensed table-hover nowrap')[6]
      viento_mensual = [float(celda.text.strip()) for celda in tabla_viento.find('tbody').find_all('tr')[0].find_all('td')[1:]]
      meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
      data = {'Mes': meses,'Temperatura_Máxima (°C)': temperaturas['Máxima'],'Temperatura_Mínima (°C)': temperaturas['Mínima'],'Temperatura_Media (°C)': temperaturas['Temp.'],'Dias_Lluvia (d)': dias_lluvia,'Cant_Lluvia (mm)': lluvia_mensual,'Viento (kph)': viento_mensual}
      df = pd.DataFrame(data)
  else:
      print(f'Error al acceder a la página: {response.status_code}')
      df = pd.DataFrame()
  return df
data = {"Mes": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio","Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],"Temperatura media (°C)": [4.6, 6, 9.2, 12.1, 16.5, 22.4, 25.7, 25.5, 20.7, 15, 8.6, 5.3],"Temperatura min. (°C)": [0.6, 1.2, 3.8, 6.4, 10.3, 15.5, 18.6, 18.5, 14.7, 10.1, 4.6, 1.4],"Temperatura máx. (°C)": [9.3, 11.2, 14.8, 17.6, 22.2, 28.4, 32, 31.7, 26.6, 20.2, 13, 9.9],"Precipitación (mm)": [43, 37, 44, 55, 51, 22, 8, 12, 28, 65, 58, 50],"Humedad (%)": [79, 69, 61, 59, 51, 40, 31, 33, 43, 62, 73, 78],"Días lluviosos (días)": [6, 5, 6, 6, 6, 3, 1, 2, 3, 6, 6, 6],"Horas de sol (horas)": [5.3, 6.5, 8.0, 9.3, 11.4, 13.0, 13.1, 12.0, 10.4, 7.9, 6.0, 5.4]}
weather_df = pd.DataFrame(data)
df_clima = contexto()
clima = weather_df.merge(df_clima[['Mes', 'Viento (kph)']], on='Mes', how='left')
clima['DireccionViento'] = ['Norte','Norte','Norte','Norte','Oeste','Oeste','Oeste','Oeste','Oeste','Oeste','Oeste','Oeste']
with pd.ExcelWriter('/var/www/html/proyectos/arganda/datos_completos.xlsx', engine='openpyxl') as writer:
    df_merged.to_excel(writer, sheet_name='Datos Sensores', index=False)
    new_data.to_excel(writer, sheet_name='Datos Clima', index=False)
    clima.to_excel(writer, sheet_name='Contextualización', index=False)
