import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
def wait_and_click(driver, selector, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        element.click()
        return True
    except Exception as e:
        return False
def reject_cookies(driver):
    reject_selectors = ['.ant-btn.antd-pro-components-cookie-banner-index-cookieButton','[aria-label="Rechazar todas las cookies"]','.reject-cookies-button','.onetrust-reject-btn-handler']
    for selector in reject_selectors:
        if wait_and_click(driver, selector, timeout=10):
            return True
    return False
def enter_text(driver, selector, text, timeout=10):
    try:
        input_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        input_field.clear()
        input_field.send_keys(text)
        return True
    except Exception as e:
        return False
def wait_for_url_change(driver, expected_url, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            EC.url_to_be(expected_url))
        return True
    except Exception as e:
        return False
def scroll_into_view(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)
def change_page_size(driver):
    try:
        selectors = ['.ant-select-selection__rendered','.ant-pagination-options .ant-select-selection','.ant-table-pagination .ant-select-selection','.ant-select-selector']
        page_size_selector = None
        for selector in selectors:
            try:
                page_size_selector = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if page_size_selector:
                    break
            except:
                continue
        if not page_size_selector:
            return False
        current_size_text = page_size_selector.text.strip()
        if '100' in current_size_text:
            return True
        scroll_into_view(driver, page_size_selector)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", page_size_selector)
        time.sleep(1)
        option_selectors = ["//li[contains(text(), '100 / página')]","//div[contains(@class, 'ant-select-item') and contains(text(), '100')]","//div[contains(@class, 'ant-select-dropdown')]//li[contains(text(), '100')]"]
        for option_selector in option_selectors:
            try:
                option_100 = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, option_selector)))
                driver.execute_script("arguments[0].click();", option_100)
                time.sleep(2)
                return True
            except:
                continue
        return False
    except Exception as e:
        return False
def extract_links_and_names(driver):
    links_dict = {}
    try:
        tbody = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-table-tbody')))
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            try:
                link_element = row.find_element(By.TAG_NAME, 'a')
                href = link_element.get_attribute('href')
                name = link_element.text
                if href and name:
                    links_dict[name] = href
            except Exception as e:
                continue
    except Exception as e:
         pass
    return links_dict
def ensure_correct_scroll_position(driver):
    try:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        reference_selectors = [".ant-table-wrapper",".ant-pagination",".ant-table-footer"]
        for selector in reference_selectors:
            try:
                element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if element:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", element)
                    time.sleep(1)
                    return True
            except:
                continue
        return False
    except Exception as e:
        return False
def click_export_button(driver, timeout=10):
    try:
        export_button_selectors = ["#root > div > section > section > main > div > div:nth-child(3) > div > div.ant-list.ant-list-split.ant-list-grid > div > div > div > div:nth-child(2) > div > div > span > button","//button[normalize-space(text())='Exportar datos']","//button[contains(., 'Exportar datos')]","//span[normalize-space(text())='Exportar datos']/parent::button",".ant-btn:has(span:contains('Exportar datos'))","button:has(span:contains('Exportar datos'))"]
        export_button = None
        for selector in export_button_selectors:
            try:
                if selector.startswith('//'):
                    export_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    export_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if export_button:
                    break
            except:
                continue
        if not export_button:
            return False
        if 'disabled' in export_button.get_attribute('outerHTML'):
            return False
        if not export_button.is_displayed():
            return False
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", export_button)
        time.sleep(1)
        driver.execute_script("""
            arguments[0].style.border = '2px solid red';
            arguments[0].style.zIndex = '9999';
            arguments[0].style.position = 'relative';
        """, export_button)
        driver.execute_script("""
            var elements = document.getElementsByClassName('antd-pro-components-global-header-index-action');
            for(var i=0; i<elements.length; i++){
                elements[i].style.display = 'none';
            }
        """)
        try:
            export_button.click()
        except:
            try:
                driver.execute_script("arguments[0].click();", export_button)
            except:
                try:
                    ActionChains(driver).move_to_element(export_button).click().perform()
                except:
                    return False
        time.sleep(3)
        return True
    except Exception as e:
        return False
def change_dates_on_pages(driver, links_dict):
    total = len(links_dict)
    current = 0
    successful_exports = 0
    failed_exports = 0
    for name, url in links_dict.items():
        current += 1
        try:
            base_url = url.split('?')[0]
            driver.get(base_url)
            time.sleep(5)
            if click_export_button(driver):
                successful_exports += 1
                time.sleep(4)
            else:
                failed_exports += 1
                continue
        except Exception as e:
            failed_exports += 1
            continue
def login(driver, email, password):
    try:
        driver.get("https://www.virtualpoolcare.io/user/login")
        time.sleep(2)
        reject_cookies(driver)
        enter_text(driver, '#userName', email)
        enter_text(driver, '#password', password)
        wait_and_click(driver, '.ant-btn.antd-pro-components-login-index-submit.ant-btn-primary.ant-btn-lg')
        wait_for_url_change(driver, "https://www.virtualpoolcare.io/pools/monitoring")
        time.sleep(5)
        return True
    except Exception as e:
        return False
def main():
    options = Options()
    options.headless = False
    download_path = os.getcwd()
    prefs = {"download.default_directory": download_path,"download.prompt_for_download": False,"download.directory_upgrade": True,"safebrowsing.enabled": True}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        if not login(driver, "openmediasol@gmail.com", "accja2020COM"):
            raise Exception("Error en el proceso de login")
        change_page_size(driver)
        time.sleep(5)
        links_dict = extract_links_and_names(driver)
        if not links_dict:
            raise Exception("No se encontraron enlaces para procesar")
        change_dates_on_pages(driver, links_dict)
    except Exception as e:
        pass
    finally:
        driver.quit()
    return links_dict

links_dict = main()
links_dict = {k: v.split('?')[0] for k, v in links_dict.items()}
ids_por_url ={'nombre': {0: 'BlueConnect_Gaibiel',1: 'Blueconnect_Teresa',2: 'BlueConnect_Jerica',3: 'Blueconnect_Almedijar',4: 'BlueConnect_Geldo',5: 'BlueConnect_Soneja',6: 'BlueConnect_AlgimiaDeA',7: 'BlueConnect_Altura',8: 'BlueConnect_Bejis',9: 'BlueConnect_ElToro',10: 'BlueConnect_FuenteLaReina',11: 'BlueConnect_Higueras',12: 'BlueConnect_PinaMontalgrao',13: 'BlueConnect_Matet',14: 'BlueConnect_Pavias',15: 'BlueConnect_Navajas',16: 'Blueconnect_Torás',17: "Blueconnect_VallD'Almonacid",18: 'Blueconnect_SotdeFerrer',19:'BlueConnect_Barracas',20: 'Blueconnect_Azuebar',21: 'Vaso',22: 'Blueconnect_Viver',23: 'Blueconnect_Chovar',24: 'BlueConnect_Caudiel',25: 'BlueConnect_Sacañet'},
        'url': {0: 'https://www.virtualpoolcare.io/pools/dccea482-3bbf-4d34-9281-a05f21dd09fb',1: 'https://www.virtualpoolcare.io/pools/2d8000b4-c404-49f3-a79b-c8d420e98db7',2: 'https://www.virtualpoolcare.io/pools/4b797054-edde-4cee-ac26-628c8dafd8a4',3: 'https://www.virtualpoolcare.io/pools/eb8dc1a6-f209-4f0d-80a8-5fcbaceae390',4: 'https://www.virtualpoolcare.io/pools/b28a85b3-c00d-415a-a90c-07dd8538bac5',5: 'https://www.virtualpoolcare.io/pools/33eac2ec-59ed-4581-9570-21076dfda930',6: 'https://www.virtualpoolcare.io/pools/e785fdf2-d936-42d9-baf1-859640e594ef',7: 'https://www.virtualpoolcare.io/pools/77743e8f-247e-4d1c-b49c-fbe9dba09498',8: 'https://www.virtualpoolcare.io/pools/246b1067-fc44-4978-b604-15442c56302a',9: 'https://www.virtualpoolcare.io/pools/27ad1212-2e65-4b2c-9334-7d574b96075e',10: 'https://www.virtualpoolcare.io/pools/1789e930-c564-4a35-83e9-4ac40cb71977',11: 'https://www.virtualpoolcare.io/pools/44c74d33-34e9-48b3-bdc0-72deb5063437',12: 'https://www.virtualpoolcare.io/pools/51eb02a4-9892-40c7-a1c0-be137e2eb9eb',13: 'https://www.virtualpoolcare.io/pools/dc6cebfb-16b4-4908-a95a-e5e7d0bd0f07',14: 'https://www.virtualpoolcare.io/pools/d026e232-db4e-4bef-afe3-9e6a9f7b8f4a',15: 'https://www.virtualpoolcare.io/pools/0561b744-8342-46f6-950b-73789ac219c3',16: 'https://www.virtualpoolcare.io/pools/4496d06d-3e81-4aa8-8f00-e1e2fb3bc7b7',17: 'https://www.virtualpoolcare.io/pools/fd53292a-3d83-4ab6-8dba-529a48dfde88',18: 'https://www.virtualpoolcare.io/pools/a3abcc0d-2e36-4c24-8082-66296cd58fbb',19: 'https://www.virtualpoolcare.io/pools/a25787e1-b2d9-49a0-9de7-ecaf6d959ab9',20: 'https://www.virtualpoolcare.io/pools/3a2d797e-20a0-436e-b6cd-a28b7758dade',21: 'https://www.virtualpoolcare.io/pools/c4dfc304-220e-46c1-90e7-164d37812317',22: 'https://www.virtualpoolcare.io/pools/e60a6972-36c8-473b-9af5-2de48963aa1b',23: 'https://www.virtualpoolcare.io/pools/fed70fff-a58e-44ec-9a28-c55e456ec090',24: 'https://www.virtualpoolcare.io/pools/ce744351-57ea-41d2-a811-f2374e515742',25: 'https://www.virtualpoolcare.io/pools/4ee62067-68fa-49ed-8ddf-a20c7a3dc25c'},
        'id': {0: 5391043246414189,1: 8071317998906499,2: 5975090540842959,3: 7414988029079282,4: 8516784775362356,5:4231446180039296,6: 3757454504177307,7: 6059783208271505,8: 	4552901060669444,9:3408393358762522,10: 1793695444199705,11:6656136680722072,12: 2506461416330061,13: 9258757093789617,14: 1356528228524153,15: 9094896183527888,16: 3252031246220682,17: 4763311310341999,18: 7874689117701236,19: 2037286352775591,20: 1569479826652253,21: 1200777995213507,22: 1636787129760256,23: 9693883324613157,24: 7244487593455382,25: 3768041338358500}}
import json
import hashlib
import os
import pandas as pd
import requests
import logging
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='processing.log'
)
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
DB_CONFIG = {
    'dbname': 'openms',
    'user': 'angel',
    'password': 'FeNh3}YLrStW%',
    'host': 'localhost',
    'port': '5432'
}
def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        logging.error(f"Error conectando a la base de datos: {e}")
        raise
def create_tables():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS registro_datos (
                    id SERIAL PRIMARY KEY,
                    hash VARCHAR(64) UNIQUE,
                    datos JSONB,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_hash ON registro_datos(hash);
            """)
        conn.commit()
        logging.info("Tablas creadas/verificadas correctamente")
    except Exception as e:
        logging.error(f"Error creando tablas: {e}")
        raise
    finally:
        conn.close()
def generate_hash(row):
    try:
        row_str = json.dumps(row, sort_keys=True)
        return hashlib.sha256(row_str.encode()).hexdigest()
    except Exception as e:
        logging.error(f"Error generando hash: {e}")
        raise

def check_if_sent(hash_value):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM registro_datos WHERE hash = %s)", (hash_value,))
            return cur.fetchone()[0]
    except Exception as e:
        logging.error(f"Error verificando hash en base de datos: {e}")
        return False
    finally:
        conn.close()
def save_hash(hash_value, row_data):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO registro_datos (hash, datos) VALUES (%s, %s) ON CONFLICT (hash) DO NOTHING",
                (hash_value, json.dumps(row_data))
            )
        conn.commit()
        logging.info(f"Hash guardado exitosamente: {hash_value}")
    except Exception as e:
        logging.error(f"Error guardando hash: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
def send_data(data, hash_value):
    endpoint_url = "https://apdata.iqmenic.com/iqmdata.php?COMM=pydata"
    headers = {'Content-Type': 'application/json'}
    try:
        response = session.post(endpoint_url, headers=headers, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            save_hash(hash_value, data)
            logging.info(f"Datos enviados correctamente: {hash_value}")
            return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error enviando datos: {e}")
        return False
def datos(df):
    datos_generados = []
    for idx, row in df.iterrows():
        try:
            timestamp = int(datetime.strptime(str(row['Date (GMT)']), "%Y-%m-%d %H:%M:%S").timestamp())
            datos_generados.append({
                "id": int(row['id']),
                "timestamp": timestamp,
                "propiedades": [{
                    "temperatura": str(row['Temperature (°C)']),
                    "pH": str(row['pH']),
                    "orp": str(row['ORP (mV)']),
                    "conductividad": str(row['Conductivity (µS)']),
                    "salinidad": str(row['Salinity (g/l)']),
                    "alerta": "false"
                }]
            })
        except Exception as e:
            logging.error(f"Error procesando fila {idx}: {e}")
    return datos_generados
def process_file(archivo):
    try:
        logging.info(f"Iniciando procesamiento de archivo: {archivo}")
        df = pd.read_excel(archivo)
        df['Date (GMT)'] = df['Date (GMT)'].dt.strftime('%Y-%m-%d %H:%M:%S')
        url_asociada = None
        for sensor, url in links_dict.items():
            if sensor in archivo:
                url_asociada = url
                break
        if not url_asociada:
            logging.warning(f"No se encontró URL asociada para {archivo}")
            return
        df_ids = pd.DataFrame(ids_por_url)
        id_asignado = df_ids.loc[df_ids['url'] == url_asociada, 'id'].values
        if id_asignado.size > 0:
            df['id'] = id_asignado[0]
            datos_generados = datos(df)
            for dato in datos_generados:
                try:
                    hash_value = generate_hash(dato)
                    if not check_if_sent(hash_value):
                        if send_data(dato, hash_value):
                            logging.info(f"Dato procesado correctamente: {hash_value}")
                except Exception as e:
                    logging.error(f"Error procesando dato: {e}")
        else:
            logging.warning(f"No se encontró ID para la URL: {url_asociada}")
        os.remove(archivo)
        logging.info(f"Archivo {archivo} eliminado")
    except Exception as e:
        logging.error(f"Error procesando archivo {archivo}: {e}")
def main1():
    try:
        create_tables()
        archivos = [archivo for archivo in os.listdir() if archivo.startswith('20') and archivo.endswith('.xlsx')]
        if not archivos:
            logging.info("No se encontraron archivos para procesar")
            return
        logging.info(f"Iniciando procesamiento de {len(archivos)} archivos")
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(process_file, archivos)
        logging.info("Procesamiento completado")
    except Exception as e:
        logging.error(f"Error en el proceso principal: {e}")
main1()
