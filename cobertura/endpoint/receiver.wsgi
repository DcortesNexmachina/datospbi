#receiver.wsgi
import sys
import os
import json
import logging

# receiver.wsgi
import sys
import os
import logging

# Establecer el path donde se encuentra tu script
sys.path.insert(0, '/var/www/html/proyectos/cobertura/endpoint')

# Importar la aplicación WSGI desde app.py
from app import application

# Configuración de logging para depuración
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# La función `application` ya está definida en app.py y es compatible con WSGI
