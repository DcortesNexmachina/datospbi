#!/usr/bin/env python3
import cgi
import os
import pandas as pd
from datetime import datetime
import cgitb

# Habilitar el manejo de errores CGI detallado
cgitb.enable()

# Ubicación del archivo Excel donde se guardarán los datos
EXCEL_FILE_PATH = '/home/openms/ubicaciones.xlsx'

# Función para procesar el formulario y guardar los datos
def process_form():
    form = cgi.FieldStorage()

    # Obtener los datos del formulario
    elemento = form.getvalue("elemento")
    latitud = form.getvalue("latitud")
    longitud = form.getvalue("longitud")
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Crear el DataFrame con los nuevos datos
    new_data = {
        "Elemento": [elemento],
        "Latitud": [latitud],
        "Longitud": [longitud],
        "Fecha": [fecha]
    }

    # Intentar leer el archivo Excel existente o crear uno nuevo
    if os.path.exists(EXCEL_FILE_PATH):
        df = pd.read_excel(EXCEL_FILE_PATH)
    else:
        df = pd.DataFrame(columns=["Elemento", "Latitud", "Longitud", "Fecha"])

    # Agregar los nuevos datos al DataFrame
    df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)

    # Guardar el DataFrame actualizado en el archivo Excel
    df.to_excel(EXCEL_FILE_PATH, index=False)

# Función principal que se ejecuta al procesar el formulario
def main():
    print("Content-type: text/html\n")
    
    # Si se trata de un envío de formulario, procesar los datos
    if os.environ["REQUEST_METHOD"] == "POST":
        process_form()
        print("<h2> ¡Formulario enviado exitosamente!</h2>")
    
    # Mostrar un mensaje de confirmación (esto puede ser modificado según el caso)
    print("<p>Los datos han sido procesados correctamente y guardados.</p>")
    
# Llamar la función principal
if __name__ == "__main__":
    main()
