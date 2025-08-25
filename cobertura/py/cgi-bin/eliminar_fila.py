#!/usr/bin/env python3
import cgi
import cgitb
import pandas as pd
import os
import json
from datetime import datetime
cgitb.enable()
EXCEL_FILE = "/var/www/html/proyectos/cobertura/muestreo_cobertura.xlsx"
def eliminar_fila():
    print("Content-Type: application/json\n")
    form = cgi.FieldStorage()
    index = form.getvalue("index")
    if index is None:
        print(json.dumps({"error": "No se ha proporcionado un índice"}))
        return
    try:
        index = int(index)
        sheet_name = str(datetime.now().date())
        if sheet_name not in pd.ExcelFile(EXCEL_FILE).sheet_names:
            print(json.dumps({"error": f"La hoja '{sheet_name}' no existe en el archivo Excel."}))
            return
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        df = df[(df['Latitud'] != -1) & (df['Longitud'] != -1)]
        if index < 0 or index >= len(df):
            print(json.dumps({"error": "Índice fuera de rango"}))
            return
        df.drop(index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        json_data = df.to_dict(orient="records")
        print(json.dumps({"data": json_data, "message": "Fila eliminada correctamente"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
if __name__ == "__main__":
    eliminar_fila()
