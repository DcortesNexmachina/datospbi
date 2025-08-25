import requests
from datetime import datetime, timedelta
import os
import pandas as pd
import logging
import numpy as np
dias_semana = {'Monday': 'Lunes','Tuesday': 'Martes','Wednesday': 'Miércoles','Thursday': 'Jueves','Friday': 'Viernes','Saturday': 'Sábado','Sunday': 'Domingo'}
orden_dias = {'Monday': 1,'Tuesday': 2,'Wednesday': 3,'Thursday': 4,'Friday': 5,'Saturday': 6,'Sunday': 7}
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
bbdd = '/var/www/html/proyectos/cecobi/bbddCECOBI.xlsx'
def eliminar_archivos_no_bbdd():
    archivos = os.listdir(os.getcwd())
    for archivo in archivos:
        if archivo.startswith('EXPORT'):
            os.remove(archivo)
def descargar_archivo(url, archivo):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(archivo, 'wb') as file:
            file.write(response.content)
    except requests.RequestException as e:
        logging.error(f"Error descargando el archivo {archivo}: {e}")
        return False
    return True
def actualizar_bbdd(df, bbdd):
    if os.path.exists(bbdd):
        df_bbdd = pd.read_excel(bbdd)
        pd.concat([df_bbdd, df]).drop_duplicates().to_excel(bbdd, index=False)
    else:
        df.to_excel(bbdd, index=False)
fecha_actual = datetime.now().date()
fecha_ayer = fecha_actual - timedelta(days=1)
dia_11 = datetime(2024, 9, 11).date()
bbdd = '/var/www/html/proyectos/cecobi/bbddCECOBI.xlsx'
df_total = pd.DataFrame()
while fecha_ayer >= dia_11:
    fecha_formato = fecha_ayer.strftime('%Y-%m-%d')
    archivo_actual = f"EXPORT_{fecha_formato}"
    url_actual = f"https://iqtrafficbackend.iqmenic.com/exporta/{archivo_actual}.xlsx"
    archivo_descargado = descargar_archivo(url_actual, archivo_actual)
    fecha_ayer -= timedelta(days=1)
    if archivo_descargado:
        try:
            df = pd.read_excel(archivo_actual)
            df['fecha'] = fecha_formato
            df_total = pd.concat([df_total, df])
        except Exception as e:
            logging.error(f"Error procesando el archivo {archivo_actual}: {e}")
    else:
        logging.warning(f"Archivo {archivo_actual} no disponible.")
if not df_total.empty:
    actualizar_bbdd(df_total, bbdd)
    eliminar_archivos_no_bbdd()
    logging.info("Base de datos actualizada correctamente.")
else:
    logging.info("No se encontraron datos para actualizar.")
# df_alfa = pd.read_excel('kopinet.xlsx')
# df_alfa.drop(columns='Unnamed: 0',inplace=True, errors='ignore')
# df_combinado = pd.read_excel(bbdd)
# df_combinado = pd.concat([df_combinado,df_alfa])
# df_combinado.reset_index(drop=True, inplace=True)
# df_combinado['fecha'] = pd.to_datetime(df_combinado['fecha']).dt.date
df_total.reset_index(drop=True, inplace=True)
df_total['Tramos'] = df_total.apply(lambda row: f"{row['desde']}:00 - {row['hasta']}:00", axis=1)
for i in range(len(df_total)):
  if len(df_total.loc[i,'Tramos']) < 12:
      df_total.loc[i,'Tramos'] = '0' + str(df_total.loc[i,'Tramos'])
  if len(df_total.loc[i,'Tramos']) == 12:
      df_total.loc[i,'Tramos'] =  df_total.loc[i,'Tramos'][:8] + '0' + df_total.loc[i,'Tramos'][-4:]
df_total.loc[df_total['Tramos'] == '9:00 - 100:00', 'Tramos'] = '09:00 - 10:00'
df_combinado = df_total.sort_values(by=['fecha', 'Tramos']).reset_index(drop=True)
# print(df_combinado)
dia_en_ingles = pd.to_datetime(df_combinado['fecha']).dt.day_name()
df_combinado['Día de la Semana'] = dia_en_ingles.map(dias_semana)
df_combinado['Orden'] = dia_en_ingles.map(orden_dias)
df_combinado['L-V'] = df_combinado['Día de la Semana'].apply(lambda x: 'L-V' if x in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] else 'Fin de Semana')
df_combinado = pd.concat([grupo for _, grupo in df_combinado.groupby('comercioID')])
df_final = df_combinado.reset_index(drop=True)
# df_final = df_final.drop_duplicates(subset=['fecha', 'comercioID', 'comercio', 'desde', 'hasta', 'totalEntradas'], keep='first')
# df_final = df_final.reset_index(drop=True)
# df_final = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]
df_final['fecha'] = pd.to_datetime(df_final['fecha'])
# df_final = df_final.dropna()
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
df_final['Entradas'] = np.append([df_final['totalEntradas'].iloc[0]], np.diff(df_final['totalEntradas']))
df_final['Salidas'] = np.append([df_final['totalSalidas'].iloc[0]], np.diff(df_final['totalSalidas']))
df_final['Balanceo'] = df_final['Entradas'] - df_final['Salidas']
df_final['Column1'] = df_final['Entradas']
def correcion(df):
    a,b = 14,17
    pr_list = []
    for i in set(df['comercio']):
        pr = df[df['comercio'] == i]
        pr.reset_index(drop=True, inplace=True)
        if i == 'LV Salon Nails' or i =='Esencia':
          for k in set(pr['fecha']):
            pr2 = pr[pr['fecha'] == k]
            pr2.sort_values(by = ['fecha', 'Tramos'])
            if not pr2.empty:
              pr2.loc[pr2.index[-1], 'Salidas'] = abs(pr2['Entradas'].sum() - pr2['Salidas'][:-1].sum())
              pr2.reset_index(drop=True, inplace=True)
              if pr2.loc[0,'Balanceo'] < 0:
                  pr2.loc[0,'Entradas'] += abs(2 * pr2.loc[0,'Balanceo'])
        if i == 'Bed´s' or i == 'LOREDER' or i == 'Obabak':
          a,b = 13, 16
        elif i == 'Nere Sustraiak':
          a,b=14,16
        for k in set(pr['fecha']):
            pr1 = pr[pr['fecha'] == k]
            pr1.reset_index(drop=True, inplace=True)
            pr1.sort_values(by = ['fecha', 'Tramos'])
            pr1 = pr1[pr1['desde'] <= a]
            pr1 = pr1.copy() 
            if not pr1.empty:
                if abs(pr1.loc[1,'Balanceo']) > abs(pr1.loc[0,'Balanceo']):
                  if pr1.loc[1,'Balanceo'] < 0 and pr1.loc[0,'Balanceo'] > 0:
                    pr1.loc[1,'Entradas'] += abs(2 * pr1.loc[1,'Balanceo'])
                pr1.loc[0,'Entradas'] = abs(pr1.loc[0,'Entradas'])
                pr1.loc[0,'Salidas'] = abs(pr1.loc[0,'Salidas'])
                pr1.loc[pr1.index[-1], 'Salidas'] = abs(pr1['Entradas'].sum() - pr1['Salidas'][:-1].sum())
                if pr1.loc[0,'Balanceo'] < 0:
                    pr1.loc[0,'Entradas'] += abs(2 * pr1.loc[0,'Balanceo'])
                    pr1.loc[0,'Balanceo'] = abs(pr1.loc[0,'Balanceo'])
                pr1.drop(columns='Balanceo', inplace=True, errors='ignore')
                pr1['Balanceo'] = pr1['Entradas'] - pr1['Salidas']
                if pr1.loc[0,'Balanceo'] < 0:
                  pr1.loc[0, 'Balanceo'] = abs(pr1.loc[0, 'Balanceo'])
                pr1.loc[0,'Entradas'] += abs(2 * pr1.loc[0, 'Balanceo'])
                pr1.loc[pr1.index[-1], 'Salidas'] = abs(pr1['Entradas'].sum() - pr1['Salidas'][:-1].sum())
                pr1.loc[:, 'Balanceo'] = pr1['Entradas'] - pr1['Salidas']
            pr2 = pr[pr['fecha'] == k]
            pr2 = pr2[pr2['desde'] >= b]
            pr2.sort_values(by = ['fecha', 'Tramos'])
            pr2.reset_index(drop=True, inplace=True)
            if not pr2.empty:
              if len(pr2)>2:
                if abs(pr2.loc[1,'Balanceo']) > abs(pr2.loc[0,'Balanceo']):
                  if pr2.loc[1,'Balanceo'] < 0 and pr2.loc[0,'Balanceo'] > 0:
                    pr2.loc[1,'Entradas'] += abs(2 * pr2.loc[1,'Balanceo'])
                pr2.loc[0, 'Entradas'] = abs(pr2.loc[0, 'Entradas'])
                pr2.loc[0, 'Salidas'] = abs(pr2.loc[0, 'Salidas'])
                pr2.loc[pr2.index[-1], 'Salidas'] = abs(pr2['Entradas'].sum() - pr2['Salidas'][:-1].sum())
                if pr2.loc[0,'Balanceo'] < 0:
                    pr2.loc[0,'Entradas'] += abs(2 * pr2.loc[0,'Balanceo'])
                pr2 = pr2.drop(columns='Balanceo', errors='ignore').copy()
                pr2.loc[pr2.index[-1], 'Salidas'] = abs(pr2['Entradas'].sum() - pr2['Salidas'][:-1].sum())
                pr2.loc[:, 'Balanceo'] = pr2['Entradas'] - pr2['Salidas']
            pr_date_commerce = pd.concat([pr1, pr2])
            pr_list.append(pr_date_commerce)
    final_df = pd.concat(pr_list).reset_index(drop=True)
    return final_df
def ajustar_tramos(df_final, tramo):
    for i in df_final['comercio'].unique():
        for k in df_final['fecha'].unique():
            resultados = df_final[(df_final['comercio'] == i) & (df_final['fecha'] == k)]
            media_entradas_otros_tramos = float(round(resultados[resultados['Tramos'] != tramo]['Entradas'].mean(), 0))
            media_salidas_otros_tramos = float(round(resultados[resultados['Tramos'] != tramo]['Salidas'].mean(), 0))
            if resultados[resultados['Tramos'] == tramo]['Entradas'].sum() > media_entradas_otros_tramos:
                df_final.loc[(df_final['comercio'] == i) &
                              (df_final['fecha'] == k) &
                              (df_final['Tramos'] == tramo), 'Entradas'] = df_final[(df_final['comercio'] == i) &
                              (df_final['fecha'] == k) & (df_final['Tramos'] == tramo)]['totalEntradas'].sum()
            if resultados[resultados['Tramos'] == tramo]['Salidas'].sum() > media_salidas_otros_tramos:
                df_final.loc[(df_final['comercio'] == i) &
                              (df_final['fecha'] == k) &
                              (df_final['Tramos'] == tramo), 'Salidas'] = df_final[(df_final['comercio'] == i) &
                              (df_final['fecha'] == k) & (df_final['Tramos'] == tramo)]['totalSalidas'].sum()
    return df_final
df_final = ajustar_tramos(df_final, '10:00 - 11:00')
df_final = ajustar_tramos(df_final, '09:00 - 10:00')
df_final = correcion(df_final)
df_final = ajustar_tramos(df_final, '10:00 - 11:00')
df_final = ajustar_tramos(df_final, '09:00 - 10:00')
df_final = correcion(df_final)
df_final[df_final['Entradas'] >= df_final['Salidas']]
df_final.sort_values(by = ['fecha', 'Tramos'])
df_final.reset_index(drop=True, inplace=True)
try:
    df_final['Día de la Semana'] = pd.to_datetime(df_final['fecha']).dt.day_name().map(dias_semana)
    df_final['L-V'] = df_final['Día de la Semana'].apply(lambda x: 'L-V' if x in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] else 'Fin de Semana')
    if 'L-V' in df_final.columns:
        df_final['EntradasFINDE'] = np.where(df_final['L-V'] == 'L-V', 0, df_final['Entradas'])
        df_final['EntradasL-V'] = np.where(df_final['L-V'] == 'L-V', df_final['Entradas'], 0)
        df_final.to_excel(bbdd, index=False)
    else:
        logging.error("La columna 'L-V' no se creó correctamente")
except Exception as e:
    logging.error(f"Error al procesar entradas y salidas: {e}")
