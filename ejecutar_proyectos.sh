#!/bin/bash

# Define el directorio base
BASE_DIR="/var/www/html/proyectos"
LOG_FILE="/var/www/html/proyectos/ejecucion.log"

# Crear o vaciar el log
> "$LOG_FILE"

# Itera sobre las carpetas dentro del directorio
for DIR in "$BASE_DIR"/*; do
    # Si es un directorio
    if [ -d "$DIR" ]; then
        echo "Entrando en el directorio: $DIR" | tee -a "$LOG_FILE"
        # Ejecuta cada archivo Python en el directorio
        for PYTHON_FILE in "$DIR"/*.py; do
            if [ -f "$PYTHON_FILE" ]; then
                echo "Ejecutando: $PYTHON_FILE" | tee -a "$LOG_FILE"
                python3 "$PYTHON_FILE" >> "$LOG_FILE" 2>&1
                # Verifica si ocurrió un error al ejecutar el archivo Python
                if [ $? -ne 0 ]; then
                    echo "Error al ejecutar $PYTHON_FILE" | tee -a "$LOG_FILE"
                fi
            fi
        done
    fi
done
