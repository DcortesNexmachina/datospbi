import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from jinja2 import Template
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='comparativa.log', filemode='a')
logger = logging.getLogger(__name__)

resultados_conclusiones = {
    "normalidad": {
        "shapiro_antes": {
            "p_valor_alto": "los datos siguen una distribución normal en este periodo.",
            "p_valor_bajo": "los datos no siguen una distribución normal en este periodo."
        },
        "shapiro_durante": {
            "p_valor_alto": "los datos siguen una distribución normal en este periodo.",
            "p_valor_bajo": "los datos no siguen una distribución normal en este periodo."
        }
    },
    "hipotesis": {
        "valor_p": {
            "significativo": {
                "interpretacion_p": "es lo suficientemente bajo como para rechazar la hipótesis nula.",
                "conclusion_hipotesis": "existe evidencia estadística de una diferencia significativa en las medias entre los dos periodos.",
                "conclusion_general": "Los resultados del análisis muestran evidencia estadística significativa de una diferencia en la afluencia de clientes entre los periodos analizados."
            },
            "no_significativo": {
                "interpretacion_p": "es demasiado alto como para rechazar la hipótesis nula.",
                "conclusion_hipotesis": "no hay evidencia estadística suficiente para afirmar que las medias son significativamente diferentes.",
                "conclusion_general": "Aunque se observó una variación en las medias, los resultados del análisis no muestran evidencia estadística suficiente para afirmar una diferencia significativa en la afluencia de clientes entre los periodos analizados."
            }
        }
    }
}

class CustomerFlowAnalysis:
    def __init__(self, df: pd.DataFrame, store_name: str):
        self.df = df
        self.store_name = store_name
        self.period1_data = None
        self.period2_data = None

    def filter_periods(self,
                      period1_start: datetime,
                      period1_end: datetime,
                      period2_start: datetime,
                      period2_end: datetime) -> None:
        self.period1_data = self.df[
            (self.df['Fecha'] >= period1_start) &
            (self.df['Fecha'] <= period1_end)
        ]['Entradas']

        self.period2_data = self.df[
            (self.df['Fecha'] >= period2_start) &
            (self.df['Fecha'] <= period2_end)
        ]['Entradas']

        if len(self.period1_data) == 0 or len(self.period2_data) == 0:
            raise ValueError(f"No data found for one or both periods for store: {self.store_name}")

    def perform_statistical_analysis(self) -> Dict:
        normality_test1 = stats.shapiro(self.period1_data)
        normality_test2 = stats.shapiro(self.period2_data)
        t_stat, p_value = stats.ttest_ind(self.period1_data, self.period2_data)

        stats_dict = {
            'period1_mean': self.period1_data.mean(),
            'period2_mean': self.period2_data.mean(),
            'period1_std': self.period1_data.std(),
            'period2_std': self.period2_data.std(),
            'normality_test1': normality_test1,
            'normality_test2': normality_test2,
            't_statistic': t_stat,
            'p_value': p_value
        }
        return stats_dict

    def create_visualizations(self, output_dir: Path, df_store) -> None:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        self.df = self.df.sort_values(by='Fecha')

        period1_start = datetime(2024, 11, 14)
        period1_end = datetime(2024, 12, 6)
        period2_start = datetime(2024, 12, 20)
        period2_end = datetime(2025, 1, 6)

        plt.figure(figsize=(12, 6))
        self.df.set_index('Fecha')['Entradas'].plot()
        plt.axvspan(period1_start, period1_end, color='red', alpha=0.3, label='Durante Euskal Bono Denda')
        plt.axvspan(period2_start, period2_end, color='blue', alpha=0.3, label='Durante Navidades')
        plt.title(f'Serie Temporal de Entradas - {self.store_name}')
        plt.xlabel('Fecha')
        plt.ylabel('Nº de Entradas')
        plt.legend()
        plt.savefig(output_dir / 'time_series.png')
        plt.close()

    def generate_html_report(self, stats: Dict, output_dir: Path, campaign_name: str) -> None:
        shapiro_antes_result = "p_valor_bajo" if stats['normality_test1'][1] < 0.05 else "p_valor_alto"
        shapiro_durante_result = "p_valor_bajo" if stats['normality_test2'][1] < 0.05 else "p_valor_alto"
        valor_p_result = "significativo" if stats['p_value'] < 0.05 else "no_significativo"
        percent_change = ((stats['period2_mean'] - stats['period1_mean']) / stats['period1_mean']) * 100
        template_str = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Informe Comparativo de Afluencia - {{ store_name }}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .visualization {
                    margin: 20px 0;
                    text-align: center;
                }
                .visualization img {
                    max-width: 100%;
                    height: auto;
                }
                .narrative {
                    text-align: justify;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <h1>Informe Comparativo de Afluencia de Clientes - {{ store_name }}</h1>

            <div class="narrative">
                <h2>Resumen Estadístico</h2>
                <p>En este informe se comparan dos periodos de tiempo diferentes para analizar cómo varió la cantidad de clientes que ingresaron a la tienda de {{ store_name }}.
                Los periodos que se comparan son:</p>
                <ul>
                    <li><strong>Campaña de Euskal Bono Denda</strong> (15 Nov 2024 - 5 Dic 2024)</li>
                    <li><strong>Campaña de Navidad</strong> (20 Dic 2024 - 6 Ene 2025)</li>
                </ul>

                <h3>Análisis de las Métricas Principales</h3>
                <p>
                    El análisis reveló que durante la campaña de Euskal Bono Denda, la media de entradas fue de {{ "%.2f"|format(stats.period1_mean) }}
                    clientes por hora ({{ "%.2f"|format(stats.period1_mean*8) }} clientes por dia). Durante la Campaña de Navidad, esta cifra {{ "aumentó" if stats.period2_mean > stats.period1_mean else "disminuyó" }}
                    a {{ "%.2f"|format(stats.period2_mean) }} clientes por hora ({{ "%.2f"|format(stats.period2_mean*8) }} clientes por dia), lo que representa una {{ "mejora" if stats.period2_mean > stats.period1_mean else "reducción" }}
                    del {{ "%.1f"|format(percent_change|abs) }}%.
                </p>

                <p>
                    En cuanto a la variabilidad de las entradas, la desviación estándar fue de {{ "%.2f"|format(stats.period1_std) }}
                    antes de la campaña y {{ "%.2f"|format(stats.period2_std) }} durante la misma. Esto indica que
                    {% if stats.period2_std > stats.period1_std %}
                    hubo fluctuaciones en el número de entradas entre ambas campañas.
                    {% else %}
                    el patrón de entradas fue más estable durante ambas campañas.
                    {% endif %}
                </p>

                <h3>Análisis de Normalidad</h3>
                <p>Al realizar el test de Shapiro-Wilk para verificar la normalidad de los datos, encontramos que
                {{ resultados_conclusiones["normalidad"]["shapiro_antes"][shapiro_antes_result] }}
                Similarmente, para el periodo durante la Campaña de Navidad,
                {{ resultados_conclusiones["normalidad"]["shapiro_durante"][shapiro_durante_result] }}</p>

                <h3>Contraste de Hipótesis</h3>

                <p>
                    <strong>El número t (estadístico t):</strong> Es un valor que nos ayuda a comparar dos grupos
                    (en este caso, las entradas antes y durante la campaña). Si este número es muy alto o muy bajo,
                    indica que hay una diferencia importante entre los grupos. En este caso, t es
                    <strong>{{ "%.4f"|format(stats.t_statistic) }}</strong>.
                </p>

                <p>
                    <strong>El p-valor:</strong> Es un número que nos dice qué tan probable es que la diferencia
                    observada entre los dos grupos sea solo por casualidad. Si el p-valor es pequeño (menor a 0.05),
                    significa que hay evidencia suficiente para afirmar que los grupos son realmente diferentes.

                    {% if stats.p_value < 0.05 %}
                        Como el p-valor es <strong>{{ "%.4f"|format(stats.p_value) }}</strong>, que es menor a 0.05,
                        podemos concluir que existe una diferencia significativa entre los dos periodos analizados.
                    {% else %}
                        Pero aquí el p-valor es <strong>{{ "%.4f"|format(stats.p_value) }}</strong>, que es muy alto.
                        Esto indica que no hay suficiente evidencia para decir que la diferencia observada sea real
                        y que cualquier cambio en la afluencia de clientes podría deberse al azar.
                    {% endif %}
                </p>

                <h3>Conclusión</h3>
                <p>{{ resultados_conclusiones["hipotesis"]["valor_p"][valor_p_result]["conclusion_general"] }}</p>

                <div class="visualization">
                    <h3>Serie Temporal de Entradas</h3>
                    <img src="time_series.png" alt="Serie Temporal">
                    <p>El gráfico muestra la evolución temporal de las entradas, con las zonas sombreadas
                    indicando los periodos durante las campañas.</p>
                </div>

            </div>
        </body>
        </html>
        """

        template = Template(template_str)
        html_report = template.render(
            store_name=self.store_name,
            stats=stats,
            campaign_name=campaign_name,
            resultados_conclusiones=resultados_conclusiones,
            shapiro_antes_result=shapiro_antes_result,
            shapiro_durante_result=shapiro_durante_result,
            valor_p_result=valor_p_result,
            percent_change=percent_change
        )

        output_path = output_dir / f'informe_comparativo_afluencia.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_report)

        logger.info(f"Report generated successfully for {self.store_name}: {output_path}")

def analyze_store(df_store: pd.DataFrame, store_name: str, base_output_dir: Path):
    try:
        period1_start = pd.to_datetime(df_store['Fecha'].min())
        period1_end = datetime(2024, 11, 14)
        period2_start = datetime(2024, 11, 15)
        period2_end = datetime(2024, 12, 5)

        period1_data = df_store[(df_store['Fecha'] >= period1_start) & (df_store['Fecha'] <= period1_end)]
        period2_data = df_store[(df_store['Fecha'] >= period2_start) & (df_store['Fecha'] <= period2_end)]

        MIN_DAYS_PERIOD1 = 0
        MIN_DAYS_PERIOD2 = 0

        if len(period1_data) < MIN_DAYS_PERIOD1 or len(period2_data) < MIN_DAYS_PERIOD2:
            logger.warning(f"Datos insuficientes para el comercio {store_name}. " +
                         f"Período 1: {len(period1_data)} días, Período 2: {len(period2_data)} días. " +
                         f"Mínimo requerido: Período 1: {MIN_DAYS_PERIOD1}, Período 2: {MIN_DAYS_PERIOD2}")
            return False

        store_output_dir = base_output_dir / store_name.replace(" ", "_").lower()
        store_output_dir.mkdir(exist_ok=True, parents=True)

        analysis = CustomerFlowAnalysis(df_store, store_name)
        analysis.filter_periods(period1_start, period1_end, period2_start, period2_end)
        stats = analysis.perform_statistical_analysis()
        analysis.create_visualizations(store_output_dir, df_store)
        analysis.generate_html_report(stats, store_output_dir, "Dobles")
        logger.info(f"Análisis completado para el comercio: {store_name}")
        return True

    except Exception as e:
        logger.error(f"Error en el análisis del comercio {store_name}: {str(e)}")
        return False
def main():
    try:
        df = pd.read_excel('https://datospbi.iqmenic.com/cecobi/bbddCECOBI.xlsx')
        df = df[df['comercio']!= 'dderer']
        comercios_excluidos = ['dderer', 'Esencia', 'Obabak', 'Prueba', 'Selene Moda']
        df = df[~df['comercio'].isin(comercios_excluidos)]
        df.drop(columns=['comercioID', 'desde', 'hasta', 'totalEntradas', 'totalSalidas',
                        'Tramos', 'Día de la Semana', 'Orden', 'L-V', 'Salidas', 'Column1',
                        'Balanceo', 'EntradasFINDE', 'EntradasL-V'],
                inplace=True, errors='ignore')
        df = df.rename(columns={'fecha': 'Fecha'})
        df = df[df['Entradas']>=0]
        df.reset_index(inplace=True, drop=True)
        base_output_dir = Path('informes_comercios_dobles')
        base_output_dir.mkdir(exist_ok=True)
        stores = df['comercio'].unique()
        successful_analyses = 0
        insufficient_data = 0
        failed_analyses = 0
        for store in stores:
            logger.info(f"Procesando comercio: {store}")
            df_store = df[df['comercio'] == store].copy()
            df_store.reset_index(drop=True, inplace=True)
            result = analyze_store(df_store, store, base_output_dir)
            if result:
                successful_analyses += 1
            else:
                insufficient_data += 1
        logger.info("\n=== Resumen del Procesamiento ===")
        logger.info(f"Total de comercios: {len(stores)}")
        logger.info(f"Análisis completados: {successful_analyses}")
        logger.info(f"Comercios con datos insuficientes: {insufficient_data}")
        logger.info(f"Análisis fallidos: {failed_analyses}")
    except Exception as e:
        logger.error(f"Error en el proceso principal: {str(e)}")
        raise
if __name__ == "__main__":
    main()
