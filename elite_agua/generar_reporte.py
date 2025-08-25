import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from shapely.geometry import Polygon, Point
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class WaterMeterDataGenerator:
    def __init__(self):
        self.START_DATE = datetime(2024, 1, 1)
        self.END_DATE = datetime.now()
        self.N_RECORDS = 60
        self.ZONAS = ['Zona Norte', 'Zona Este', 'Zona Sur', 'Zona Oeste']
        self.CALIDAD_SENIAL = ['Buena', 'Regular', 'Mala']
        self.ERRORES = [
            'Ninguno', 'Exceso Flujo', 'Condiciones Extremas', 'Sabotaje',
            'Fuga de Agua', 'Flujo Inverso', 'Sensor Retirado', 'Contador Bloqueado',
            'Flujo Mínimo', 'Error Temporal HW', 'Error Permanente HW'
        ]
        self.LIMITES_POLIGONO = [(42.65039297529459, -8.890997412220704),(42.645270099417495, -8.890528276575411),(42.64720781710497, -8.879702069376368),(42.65081765073003, -8.87955771994705)]
        self.poligono = Polygon(self.LIMITES_POLIGONO)
        self.prob_errores = np.array([0.7] + [0.03] * 10)
        self.prob_errores /= self.prob_errores.sum()
    def generar_puntos_validos(self):
        puntos_validos = []
        minx, miny, maxx, maxy = self.poligono.bounds
        with tqdm(total=self.N_RECORDS, desc="Generando ubicaciones") as pbar:
            while len(puntos_validos) < self.N_RECORDS:
                batch_size = min(1000, self.N_RECORDS - len(puntos_validos))
                points = [Point(np.random.uniform(minx, maxx),
                              np.random.uniform(miny, maxy))
                         for _ in range(batch_size)]
                valid_points = [(p.x, p.y) for p in points if self.poligono.contains(p)]
                puntos_validos.extend(valid_points[:self.N_RECORDS - len(puntos_validos)])
                pbar.update(len(valid_points))
        return zip(*puntos_validos[:self.N_RECORDS])
    def generar_lecturas_consistentes(self, n_registros):
        base_lecturas = np.random.randint(100, 2001, self.N_RECORDS)
        incrementos = np.random.normal(50, 15, (n_registros, self.N_RECORDS))
        incrementos = np.maximum(incrementos, 0)
        lecturas_acumuladas = np.cumsum(incrementos, axis=0)
        lecturas_iniciales = np.tile(base_lecturas, (n_registros, 1)) + lecturas_acumuladas
        lecturas_finales = lecturas_iniciales + incrementos
        return (lecturas_iniciales.flatten(),
                lecturas_finales.flatten(),
                incrementos.flatten())
    def generar_datos(self):
        date_range = pd.date_range(self.START_DATE, self.END_DATE, freq='H')
        n_dates = len(date_range)
        latitudes, longitudes = self.generar_puntos_validos()
        contadores_ids = np.repeat([f"{i:03d}" for i in range(1, self.N_RECORDS + 1)], n_dates)
        fechas = np.tile(date_range, self.N_RECORDS)
        zonas = np.repeat(np.random.choice(self.ZONAS, self.N_RECORDS), n_dates)
        clientes = np.repeat([f"Cliente {i}" for i in range(1, self.N_RECORDS + 1)], n_dates)
        lecturas_iniciales, lecturas_finales, consumos = self.generar_lecturas_consistentes(n_dates)
        calidades = np.random.choice(self.CALIDAD_SENIAL, len(fechas))
        errores = np.random.choice(self.ERRORES, len(fechas), p=self.prob_errores)
        df = pd.DataFrame({
            'ID Contador': contadores_ids,
            'Fecha y Hora': fechas,
            'Lectura Inicial (m³)': lecturas_iniciales,
            'Lectura Final (m³)': lecturas_finales,
            'Consumo (m³)': consumos,
            'Zona': zonas,
            'Cliente': clientes,
            'Latitud': np.repeat(latitudes, n_dates),
            'Longitud': np.repeat(longitudes, n_dates),
            'Calidad de la Señal': calidades,
            'Tipo de Error': errores
        })
        return df
    def guardar_datos(self, df):
        filename = 'elite_agua_ficticios.csv'
        df.to_csv(filename, index=False)
        print(f"\nArchivo CSV generado exitosamente: '{filename}'")
        print(f"Tamaño del dataset: {len(df):,} registros")
        print(f"Periodo: {df['Fecha y Hora'].min()} a {df['Fecha y Hora'].max()}")
        print(f"Número de contadores únicos: {df['ID Contador'].nunique():,}")
if __name__ == "__main__":
    generator = WaterMeterDataGenerator()
    df = generator.generar_datos()
    generator.guardar_datos(df)
