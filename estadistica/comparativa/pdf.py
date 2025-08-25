import pandas as pd
from pathlib import Path
import tempfile
import os
import logging
from weasyprint import HTML
import PyPDF2
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def create_password_protected_pdf(html_path, output_pdf_path, password, images, logos=None):
    try:
        html_path = Path(html_path)
        output_pdf_path = Path(output_pdf_path)
        if not html_path.exists():
            raise FileNotFoundError(f"El archivo HTML no existe: {html_path}")
        for image_path in images + (logos or []):
            if not Path(image_path).exists():
                raise FileNotFoundError(f"La imagen no existe: {image_path}")
        with open(html_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()
        header_html = ""
        if logos:
            header_html = """
            <div class="header">
                <div class="logo-wrapper">
                    <div class="logo-container">
                        <div class="logo-column"><img src="{}" alt="Logo 1" class="header-logo"></div>
                        <div class="logo-column"><img src="{}" alt="Logo 2" class="header-logo"></div>
                        <div class="logo-column"><img src="{}" alt="Logo 3" class="header-logo"></div>
                    </div>
                </div>
            </div>
            """.format(logos[0], logos[1], logos[2])
        header_css = """
        @page {
            margin: 120px 40px 40px 40px;
            @top-center {
                content: element(header);
            }
        }
        .header {
            position: running(header);
            width: 100%;
            padding: 10px 0;
        }
        .logo-wrapper {
            width: 100%;
            display: flex;
            justify-content: center;
            border-bottom: 1px solid #ccc;
            padding: 10px 0;
        }
        .logo-container {
            display: grid;
            grid-template-columns: repeat(3, 100px);
            gap: 50px;
            justify-content: center;
            align-items: center;
            max-width: 800px;
            margin: 0 auto;
        }
        .logo-column {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .header-logo {
            height: 60px;
            width: auto;
            max-width: 100px;
            object-fit: contain;
        }
        """
        html_content = html_content.replace('</head>',
            f'<style>{header_css}</style></head>')
        html_content = html_content.replace('<body>',
            f'<body>{header_html}')
        for image_path in images:
            image_name = Path(image_path).name
            html_content = html_content.replace(
                f'src="{image_name}"', 
                f'src="{image_path}"'
            )
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as tmp_html:
            tmp_html.write(html_content)
            tmp_html_path = Path(tmp_html.name)
        logger.info(f"Archivo HTML temporal creado: {tmp_html_path}")
        base_url = tmp_html_path.parent.as_uri()
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            HTML(filename=str(tmp_html_path), base_url=base_url).write_pdf(tmp_pdf.name)
            logger.info(f"PDF generado temporalmente: {tmp_pdf.name}")
            reader = PyPDF2.PdfReader(tmp_pdf.name)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            if not password or len(password) < 4:
                raise ValueError("La contraseña debe tener al menos 4 caracteres")
            writer.encrypt(password)
            output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)
            logger.info(f"PDF protegido creado: {output_pdf_path}")
        os.unlink(tmp_pdf.name)
        os.unlink(tmp_html_path)
        logger.info("Archivos temporales eliminados.")
        html_path.unlink()
        logger.info(f"Archivo HTML eliminado: {html_path}")
        return True
    except Exception as e:
        logger.error(f"Error procesando {html_path}: {str(e)}")
        try:
            if 'tmp_pdf' in locals() and Path(tmp_pdf.name).exists():
                os.unlink(tmp_pdf.name)
            if 'tmp_html_path' in locals() and tmp_html_path.exists():
                os.unlink(tmp_html_path)
        except Exception as cleanup_error:
            logger.error(f"Error limpiando archivos temporales: {str(cleanup_error)}")
        return False
if __name__ == "__main__":
  dic = {
    'usuario': {0: 'ab_decohogar', 1: 'adela_garteiz', 2: 'alea', 3: 'aura', 4: 'bainila', 5: 'bed´s', 6: 'bonilla_fotografía', 7: 'cado_complements', 8: 'ainhoa_oinetakoak', 9: 'concept_store', 
                10: 'drogueria_amutio', 11: 'esencia_algorta', 12: 'esencia_barakaldo', 13: 'esencia_bilbao', 14: 'esencia_santurtzi', 15: 'euskal_souvenirs', 
                16: 'fotoetxe', 17: 'karinkara', 18: 'kibuc', 19: 'kikaren_munduan', 20: 'kilimak', 21: 'kopinet', 22: 'kuki', 23: 'lv_salon_nails', 24: 'mai_piu', 
                25: 'nattex', 26: 'nere_sutraiak', 27: 'nokora', 28: 'obaba', 29: 'optika_eguren', 30: 'loreder', 31: 'selene', 32: 'tistel', 
                33: 'ttipi_ttapa', 34: 'zibu_zabu'},
    'pwd': {0: 'vHhXQIux', 1: 'NMRe3m00', 2: 'bNbCKQaa', 3: 'eO52fG0d', 4: 'I21Bbp0N', 5: 'RRAuKFRY', 6: 'raPObbDJ', 7: 'pReLdROn', 8: 'WUXtAfGh', 9: 'qHBKgcUR', 
            10: 'XxesUPfp', 11: 'qhtTRzJM', 12: 'wPlrGtiF', 13: 'asIosdKrC', 14: 'ezhTfXWz', 15: '709PeUo6', 16: 'YkFhoVsu', 17: 'LuuJoSja', 18: 'KgIgpIOs', 
            19: 'xMIUhrSw', 20: '6N7Y1vHF', 21: 'zFvCCyOC', 22: 'tA9186qy', 23: 'asSazohh', 24: 'aAQuMRMj', 25: 'EFluHQCf', 26: 'TcOTNgVk', 27: 'AeHQmRKt', 
            28: 'ykMJDmka', 29: 'bjQxmFsm', 30: '2D96IjFq', 31: 'Qu311Ua2', 32: 'WjNRPJfy', 33: 'uYvasQcN', 34: 'gK50BxG3'}}
  df_dic = pd.DataFrame(dic)
  for i in os.listdir('/var/www/html/proyectos/estadistica/comparativa/informes_comercios_dobles/'):
    c = []
    for j in os.listdir(f'/var/www/html/proyectos/estadistica/comparativa/informes_comercios_dobles/{i}'):
      if j.endswith('.html'):
        a = os.path.join(f'/var/www/html/proyectos/estadistica/comparativa/informes_comercios_dobles/{i}', j)
        b = os.path.join(f'/var/www/html/proyectos/estadistica/comparativa/informes_comercios_dobles/{i}', j.replace('.html', '.pdf'))
        try:
          pwd = df_dic[df_dic['usuario'] == i]['pwd'].iloc[0]
        except IndexError:
          pass
      elif j.endswith('.png'):
        c.append(os.path.join(f'/var/www/html/proyectos/estadistica/comparativa/informes_comercios_dobles/{i}', j))
    create_password_protected_pdf(a,b,pwd,c,logos=['/var/www/html/proyectos/cecobi/nexmachina-logo.png','/var/www/html/proyectos/cecobi/logotipo-CECOBI.png','/var/www/html/proyectos/cecobi/gobierno-vasco.png'])
