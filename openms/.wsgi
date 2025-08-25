import sys
import logging
from formulario import app as application  # Aquí cambiamos a 'formulario'

sys.path.insert(0, '/home/openms')

logging.basicConfig(stream=sys.stderr)
