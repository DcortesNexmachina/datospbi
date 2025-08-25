#!/usr/bin/env python3
import pandas as pd
import numpy as np
from scipy import stats
import cgi
import cgitb
from datetime import datetime
cgitb.enable()
comercios = ['ADELA GARTEIZ', 'AURA', 'Ainhoa Oinetakoak', 'Alea', 'Azulillo Store', 'BAINILA', 'Bed´s','Bonilla Fotografia', 'Concept Store', 'Euskal Souvenirs', 'Fotoetxe', 'KILIMAK', 'KUKI','Kikaren Munduan', 'Kopinet', 'LOREDER', 'LV Salon Nails', 'Mai Piu', 'Nattex', 'Nere Sutraiak','Obabak', 'Optika Eguren', 'Prueba', 'Selene Moda', 'Tistel', 'Ttipi Ttapa', 'ZIBU ZABU','Kopinet', 'Karinkara', 'AB Decohogar', 'Esencia Santurtzi', 'Esencia Algorta', 'Esencia Barakaldo','Esencia Bilbao', 'Nokora', 'Kibuc', 'Drogueria Amutio']
def analizar_afluencia(df, fecha_inicio, fecha_fin, comercio, columna_fecha='fecha', columna_conteo='Entradas'):
    df_comercio = df[df['comercio'] == comercio]
    df_comercio[columna_fecha] = pd.to_datetime(df_comercio[columna_fecha])
    df_rango = df_comercio[(df_comercio[columna_fecha] >= fecha_inicio) & (df_comercio[columna_fecha] <= fecha_fin)]
    if len(df_rango) == 0:
        return {'comercio': comercio,'interpretacion': "No hay datos disponibles para este periodo"}
    mitad = len(df_rango) // 2
    if mitad == 0:
        return {'comercio': comercio,'interpretacion': "El rango de fechas es muy pequeño para realizar una comparacion"}
    primera_mitad = df_rango.iloc[:mitad]
    segunda_mitad = df_rango.iloc[mitad:]
    media_primera = np.mean(primera_mitad[columna_conteo])
    media_segunda = np.mean(segunda_mitad[columna_conteo])
    diferencia_medias = media_segunda - media_primera
    if media_primera == 0:
        porcentaje_cambio = 0
    else:
        porcentaje_cambio = (diferencia_medias / media_primera) * 100
    t_stat, p_valor = stats.ttest_ind(primera_mitad[columna_conteo],segunda_mitad[columna_conteo],equal_var=False)
    if p_valor < 0.05:
        if porcentaje_cambio > 0:
            personas_extra = (porcentaje_cambio / 100) * media_primera
            interpretacion = (f"Aumento significativo del {porcentaje_cambio:.1f}% "
                            f"({personas_extra:.0f} personas adicionales)")
        else:
            personas_faltantes = abs((porcentaje_cambio / 100) * media_primera)
            interpretacion = (f"Descenso significativo del {abs(porcentaje_cambio):.1f}% "
                            f"({personas_faltantes:.0f} personas menos)")
    else:
        interpretacion = "Sin cambios significativos"
    return {'comercio': comercio,'interpretacion': interpretacion}
def generar_html_tabla(resultados, fecha_inicio, fecha_fin):
    html_content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>Analisis de Afluencia por Comercio</title>",
        "<style>",
        "table { border-collapse: collapse; width: 100%; margin-top: 20px; }",
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
        "th { background-color: #f2f2f2; }",
        "tr:nth-child(even) { background-color: #f9f9f9; }",
        ".header { margin-bottom: 20px; }",
        "</style>",
        "</head>",
        "<body>",
        "<div class='header'>",
        "<h1>Analisis de Afluencia por Comercio</h1>",
        f"<p>Periodo: {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}</p>",
        "</div>",
        "<table>",
        "<tr>",
        "<th>Comercio</th>",
        "<th>Resultados</th>",
        "</tr>"]
    for resultado in resultados:
        html_content.extend([
            "<tr>",
            f"<td>{resultado['comercio']}</td>",
            f"<td>{resultado['interpretacion']}</td>",
            "</tr>"])
    html_content.extend([
        "</table>",
        "<h3>Contacte con dcortes@nexmachina.com si tiene dudas.</h3>",
        "</body>",
        "</html>"])
    return "\n".join(html_content)
def main():
    form = cgi.FieldStorage()
    try:
        fecha_inicio = datetime.strptime(form.getvalue('fecha_inicio'), '%Y-%m-%d')
        fecha_fin = datetime.strptime(form.getvalue('fecha_fin'), '%Y-%m-%d')
        if fecha_inicio > fecha_fin:
            raise ValueError("La fecha de inicio es posterior a la fecha fin")
        df = pd.read_excel('https://datospbi.iqmenic.com/cecobi/bbddCECOBI.xlsx')
        resultados = []
        for comercio in comercios:
            resultado = analizar_afluencia(df, fecha_inicio, fecha_fin, comercio)
            resultados.append(resultado)
        print("Content-Type: text/html\n")
        print(generar_html_tabla(resultados, fecha_inicio, fecha_fin))
    except Exception as e:
        print("Content-Type: text/html\n")
        print("<html><body>")
        print(f"<h1>Error: {str(e)}</h1>")
        print("<h2>Contacte con dcortes@nexmachina.com si tiene dudas.</h2>")
        print("</body></html>")
if __name__ == "__main__":
    main()
