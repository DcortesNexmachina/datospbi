#!/usr/bin/env python3
import pandas as pd
import numpy as np
from scipy import stats
import cgi
import cgitb
from datetime import datetime
cgitb.enable()
comercios = {
  'b2e805d7-5ced-43d4-9167-a7c9d106dec6': 'ADELA GARTEIZ',
  'f7d23383-6760-4243-bca7-14dfa450599b': 'AURA',
  '9ad51f99-c068-4765-a986-1af093f09e0b': 'Ainhoa Oinetakoak',
  'abc93d7d-6b89-4ce7-8d6f-509e26c614e5': 'Alea',
  'c59bfdec-4928-4b00-bf23-2e4961bf6fd6': 'Azulillo Store',
  'a945e474-2e07-4f7c-aa6a-0f94c0b148c0': 'BAINILA',
  '5b91f650-7aa1-40f9-af67-319a723c34ba': 'Bed´s',
  'd8800187-7352-4b18-902c-ce0f30953841': 'Bonilla Fotografia',
  '85beb160-e9ae-4e32-985c-3c0b93abe77d': 'Concept Store',
  '6c0d54aa-6bab-4c48-8a31-3b3e9a1ccbc6': 'Euskal Souvenirs',
  'a56b4b4e-7cbe-44a7-a9f4-23fe5f05ce1c': 'Fotoetxe',
  'df0c6163-1f7e-4aec-a001-13e41632891a': 'KILIMAK',
  'e2ed77ed-5281-4d1d-8d4c-ccc9a2852e99': 'KUKI',
  '401f2760-082f-46bb-8b34-df53ef93176f': 'Kikaren Munduan',
  '149b2ee0-c3c2-4a4e-8c2a-012b8195a6c7': 'Kopinet',
  '3e00030c-6876-427c-b9c5-8054d589f000': 'LOREDER',
  'ca088348-8dd3-4167-9096-103a8eafbff8': 'LV Salon Nails',
  '24f68cc5-264b-4f6e-9ad7-c7dfd3af7f48': 'Mai Piu',
  'bfb79941-ed0f-43f4-93a8-5f515073026f': 'Nattex',
  '462fe792-aab2-4bc5-8acf-178085718368': 'Nere Sutraiak',
  'f7ba855f-afb7-4878-a275-49953c178504': 'Obabak',
  '1928aa05-964c-4185-a80e-08d5fc6bff9a': 'Optika Eguren',
  '5e18cd10-66d3-4a0f-8fa1-5905d2e88d49': 'Prueba',
  '3b1098a7-aab9-4837-8549-14d12964efb2': 'Selene Moda',
  '5f9b6b3b-0311-4644-bf49-ca419769ef82': 'Tistel',
  '2ddfd548-fdfb-41bd-b0cb-59cc58a3fb26': 'Ttipi Ttapa',
  'b36e095c-8845-4ae6-a895-26c94a0df037': 'ZIBU ZABU',
  '7f8ea27b-ce5a-4b86-b662-717cd0dea85c': 'Kopinet',
  'd9800197-7352-4b19-902c-ce0f30953941': 'Karinkara',
  'a8700086-0000-3a19-102f-ka0fe8913950': 'AB Decohogar',
  '24f68cc5-7cbe-3g25-a5e4-c7dfd3af7f48': 'Esencia Santurtzi',
  '9ad51f99-1496-vsc1-a4da-178085718368': 'Esencia Algorta',
  'df53ef93-176f-176f-176f-3c0x93abex7d': 'Esencia Barakaldo',
  '6bab5bas-5asd-4b19-aad4-zc12dzf5sdc4': 'Esencia Bilbao',
  'v5a4f8xc-2d8c-95cs-ad57-1atu5sdf5ad3': 'Nokora',
  'a5d8gad5-467z-4b19-9012-xe0f30953941': 'Kibuc',
  'af76345t-234n-rn2q-2348-dfnd83nqa034': 'Drogueria Amutio'}
import os
def analizar_afluencia(comercio, fecha_inicio, fecha_fin, columna_fecha='fecha', columna_conteo='Entradas'):
    df = pd.read_excel('https://datospbi.iqmenic.com/cecobi/bbddCECOBI.xlsx')
    df = df[df['comercio'] == comercio]
    df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    if fecha_inicio < min(df[columna_fecha]) or fecha_fin > max(df[columna_fecha]):
        raise ValueError("La fecha de inicio o fin estÃ¡ fuera del rango de fechas disponibles.")
    df_rango = df[(df[columna_fecha] >= fecha_inicio) & (df[columna_fecha] <= fecha_fin)]
    mitad = len(df_rango) // 2
    if mitad == 0:
        raise ValueError("El rango de fechas es muy pequeÃ±o para realizar una comparaciÃ³n.")
    primera_mitad = df_rango.iloc[:mitad]
    segunda_mitad = df_rango.iloc[mitad:]
    media_primera = np.mean(primera_mitad[columna_conteo])
    media_segunda = np.mean(segunda_mitad[columna_conteo])
    diferencia_medias = media_segunda - media_primera
    if media_primera == 0:
        porcentaje_cambio = 0
    else:
        porcentaje_cambio = (diferencia_medias / media_primera) * 100
    t_stat, p_valor = stats.ttest_ind(primera_mitad[columna_conteo], segunda_mitad[columna_conteo], equal_var=False)
    alpha = 0.05
    intervalo_confianza = stats.t.interval(1 - alpha, len(df_rango) - 1, loc=diferencia_medias, scale=stats.sem(df_rango[columna_conteo]))
    personas_extra = None
    personas_faltantes = None
    if p_valor < 0.05:
        if porcentaje_cambio > 0:
            personas_extra = (porcentaje_cambio / 100) * media_primera
            interpretacion = (f"Ha habido un **aumento significativo** en la afluencia del comercio. "
                              f"La afluencia ha crecido aproximadamente un {porcentaje_cambio:.2f}%. "
                              f"Esto equivale a un aumento estimado de {personas_extra:.0f} personas adicionales en promedio.")
        else:
            personas_faltantes = abs((porcentaje_cambio / 100) * media_primera)
            interpretacion = (f"Ha habido un **descenso significativo** en la afluencia del comercio. "
                              f"La afluencia ha disminuido aproximadamente un {porcentaje_cambio:.2f}%. "
                              f"Esto equivale a un descenso estimado de {personas_faltantes:.0f} personas en promedio.")
    else:
        interpretacion = ("No se ha detectado una diferencia significativa en la afluencia entre las dos mitades "
                          "del rango de fechas seleccionado. Los cambios observados pueden ser atribuibles al azar.")
    resultado = {
        'media_primera_mitad': media_primera,
        'media_segunda_mitad': media_segunda,
        'diferencia_medias': diferencia_medias,
        'porcentaje_cambio': porcentaje_cambio,
        'personas_extra': personas_extra if porcentaje_cambio > 0 else None,
        'personas_faltantes': personas_faltantes if porcentaje_cambio < 0 else None,
        'intervalo_confianza_95%': intervalo_confianza,
        'p_valor': p_valor,
        'interpretacion': interpretacion
    }
    return resultado
form = cgi.FieldStorage()
comercio_id = form.getvalue('id')
if comercio_id not in comercios:
    print("Content-Type: text/html")
    print()
    print("<html>")
    print("<head><title>Error</title></head>")
    print("<body>")
    print("<h1>Error de AutorizaciÃ³n</h1><p>ID no vÃ¡lido. Acceso denegado.</p>")
    print("<h2>Contacte con dcortes@nexmachina.com si tiene dudas.</h2>")
    print("</body>")
    print("</html>")
    exit()
comercio = comercios[comercio_id]
fecha_inicio = datetime.strptime(form.getvalue('fecha_inicio'), '%Y-%m-%d')
fecha_fin = datetime.strptime(form.getvalue('fecha_fin'), '%Y-%m-%d')
if fecha_inicio > fecha_fin:
    print("Content-Type: text/html")
    print()
    print("<html>")
    print("<head><title>Resultados</title></head>")
    print("<body>")
    print("<h1>Rango de fechas incorrecto</h1>")
    print("<h2>Contacte con dcortes@nexmachina.com si tiene dudas.</h2>")
    print("</body>")
    print("</html>")
else:
    resultado = analizar_afluencia(comercio, fecha_inicio, fecha_fin)
    print("Content-Type: text/html")
    print()
    print("<html>")
    print("<head><title>Resultados</title></head>")
    print("<body>")
    print("<h1>Resultados del Seguimiento</h1>")
    print(f"<p>{resultado['interpretacion']}</p>")
    print("<h2>Contacte con dcortes@nexmachina.com si tiene dudas.</h2>")
    print("</body>")
    print("</html>")
