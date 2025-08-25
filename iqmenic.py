import asyncio
import aiohttp
import pandas as pd
import logging
from typing import Optional, Set, Union, List

# Configuración del logging
logging.basicConfig(
    filename='report.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class IQmenic:
    def __init__(self, apikey):
        """
        Inicializa una conexión a la API de IQmenic con la apikey proporcionada.
        """
        self.apikey = apikey
        self.base_url = "https://publicevoapi.iqmenic.com"
        self.token = None
        self.session = None

    async def __aenter__(self):
        """Context manager para manejar la sesión HTTP."""
        self.session = aiohttp.ClientSession()
        self.token = await self._get_token()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cierra la sesión HTTP."""
        if self.session:
            await self.session.close()

    async def _get_token(self):
        """Obtiene el token de autenticación usando la apikey."""
        url = f"{self.base_url}/login/?apikey={self.apikey}"
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get('token')
                if not token:
                    logging.error("No se pudo obtener el token")
                    raise Exception("No se pudo obtener el token")
                return token
            else:
                response.raise_for_status()

    async def async_get(self, url):
        """Realiza una petición GET asíncrona a la URL especificada."""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                logging.warning(f"Respuesta no exitosa en {url}, status: {response.status}")
                return None
        except Exception as e:
            logging.error(f"Error en petición {url}: {e}")
            return None

    async def get_sensores(self):
        """Obtiene todos los sensores del usuario."""
        url = f"{self.base_url}/currentUser/getSensors?token={self.token}"
        datos = await self.async_get(url)
        return datos.get("data", []) if datos else []

    async def _get_datos_propiedad(self, sensor_id, propiedad_id, intervalo=10):
        """Obtiene los datos de una propiedad específica de un sensor."""
        url = f"{self.base_url}/sensor/getData?token={self.token}&sensorid={sensor_id}&propiedadid={propiedad_id}&intervalo={intervalo}"
        return await self.async_get(url)

    def _filter_sensores(self, sensores: List[dict], sensor_ids: Optional[Set[int]] = None) -> List[dict]:
        """Filtra los sensores según los IDs especificados."""
        if sensor_ids is None:
            return sensores

        sensores_filtrados = [s for s in sensores if s['id'] in sensor_ids]
        ids_encontrados = {s['id'] for s in sensores_filtrados}
        ids_no_encontrados = sensor_ids - ids_encontrados

        if ids_no_encontrados:
            logging.warning(f"No se encontraron los sensores con IDs: {ids_no_encontrados}")

        return sensores_filtrados

    async def get_all(self, sensor_ids: Optional[Union[Set[int], List[int], int]] = None, 
                      max_concurrent: int = 20, intervalo: int = 10):
        """
        Obtiene TODOS los datos de los sensores especificados y TODAS sus propiedades usando asyncio.
        """
        if sensor_ids is not None:
            if isinstance(sensor_ids, int):
                sensor_ids = {sensor_ids}
            elif isinstance(sensor_ids, list):
                sensor_ids = set(sensor_ids)
            elif not isinstance(sensor_ids, set):
                raise TypeError("sensor_ids debe ser None, int, list o set")

        sensores = await self.get_sensores()
        sensores_filtrados = self._filter_sensores(sensores, sensor_ids)

        if not sensores_filtrados:
            logging.info("No se encontraron sensores para procesar")
            return pd.DataFrame()

        tareas = []
        for sensor in sensores_filtrados:
            sensor_id = sensor['id']
            propiedades = sensor.get('propiedades', [])
            for propiedad in propiedades:
                propiedad_id = propiedad['id']
                tareas.append((sensor_id, propiedad_id))

        semaforo = asyncio.Semaphore(max_concurrent)

        async def procesar_propiedad(sensor_id, propiedad_id):
            async with semaforo:
                datos = await self._get_datos_propiedad(sensor_id, propiedad_id, intervalo)
                if datos and 'data' in datos and datos['data']:
                    try:
                        df_temp = pd.DataFrame(datos['data'][0]['valores'])
                        df_temp = df_temp.assign(
                            Propiedad=datos['data'][0]['nombre'],
                            SensorId=sensor_id,
                            PropiedadId=propiedad_id
                        )
                        return df_temp
                    except Exception as e:
                        logging.error(f"Error procesando datos del sensor {sensor_id}, propiedad {propiedad_id}: {e}")
                        return None
                return None

        resultados = await asyncio.gather(*[
            procesar_propiedad(sensor_id, propiedad_id)
            for sensor_id, propiedad_id in tareas
        ], return_exceptions=True)

        dfs = [df for df in resultados if df is not None and not isinstance(df, Exception)]

        if dfs:
            df_final = pd.concat(dfs, ignore_index=True)
            return df_final
        else:
            logging.info("No se obtuvieron datos")
            return pd.DataFrame()
