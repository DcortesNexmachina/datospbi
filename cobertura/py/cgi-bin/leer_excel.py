#!/usr/bin/env python3
import cgi
import cgitb
import pandas as pd
import json
import os
from datetime import datetime
cgitb.enable()
EXCEL_FILE = "/var/www/html/proyectos//cobertura/muestreo_cobertura.xlsx"
def leer_excel():
    print("Content-Type: application/json\n")
    try:
        if not os.path.exists(EXCEL_FILE):
            print(json.dumps({"error": "El archivo Excel no existe"}))
            return
        sheet = datetime.now().strftime("%Y-%m-%d")
        df = pd.read_excel(EXCEL_FILE, sheet_name = sheet)
        df = df[(df['Latitud'] != -1) & (df['Longitud'] != -1)]
        df.drop(columns='Unnamed: 0', axis=1, inplace=True, errors='ignore')
        df.drop_duplicates(subset='Fecha')
        data = df.to_dict(orient="records")
        print(json.dumps(data))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
if __name__ == "__main__":
    leer_excel()
