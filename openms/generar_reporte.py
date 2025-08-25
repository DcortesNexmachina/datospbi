import imaplib
import email
from email.header import decode_header
import re
import pandas as pd
import requests
import json
from datetime import datetime
import time
import random
def clean_text(text):
    return text.strip() if text else ""
def connect_to_email(username, password):
    mail = imaplib.IMAP4_SSL('imap.iqmenic.com')
    mail.login(username, password)
    return mail
def extract_emails_info(mail):
    mail.select("inbox")
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()
    email_data = []
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            try:
                subject = subject.decode(encoding if encoding else 'utf-8')
            except (UnicodeDecodeError, TypeError) as e:
                print(f"Error al decodificar el asunto: {e}")
                subject = subject.decode('utf-8', 'ignore')
        date = msg["Date"]
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            body = part.get_payload(decode=True).decode('ISO-8859-1')  # Intentar con ISO-8859-1
                        except UnicodeDecodeError as e:
                            print(f"Error al decodificar el cuerpo del correo: {e}")
                            body = part.get_payload(decode=True).decode('utf-8', 'ignore')  # Ignorar caracteres no decodificables
                    break
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8')
            except UnicodeDecodeError:
                try:
                    body = msg.get_payload(decode=True).decode('ISO-8859-1')  # Intentar con ISO-8859-1
                except UnicodeDecodeError as e:
                    print(f"Error al decodificar el cuerpo del correo: {e}")
                    body = msg.get_payload(decode=True).decode('utf-8', 'ignore')  # Ignorar caracteres no decodificables
        temperature = re.search(r'Temperatura:\s*</td>\s*<td>([\d\.]+)\s*°C', body)
        ph = re.search(r'pH:\s*</td>\s*<td>([\d\.]+)', body)
        orp = re.search(r'ORP:\s*</td>\s*<td>([\d\.]+)\s*mV', body)
        conductividad = re.search(r'Conductividad:\s*</td>\s*<td>([\d\.]+)\s*µS', body)
        email_data.append({
            "Fecha": clean_text(date),
            "Asunto": clean_text(subject),
            "Cuerpo": clean_text(body),
            "Temperatura (°C)": temperature.group(1) if temperature else None,
            "pH": ph.group(1) if ph else None,
            "ORP (mV)": orp.group(1) if orp else None,
            "Conductividad (µS)": conductividad.group(1) if conductividad else None})
    return email_data
diccion = {'Blueconnect_Almedijar': '7414988029079282', 'BlueConnect_AlgimiaDeA': '3757454504177307', 'BlueConnect_Altura': '6059783208271505', 'Blueconnect_Azuebar': '1569479826652253', 'BlueConnect_Barracas': '2037286352775591', 'BlueConnect_Benafer': '3328261330914799', 'BlueConnect_Bejis': '4552901060669444', 'BlueConnect_Castellnovo': '5535947298077059', 'BlueConnect_Caudiel': '7244487593455382', 'Blueconnect_Chovar': '9693883324613157', 'BlueConnect_ElToro': '3408393358762522', 'BlueConnect_FuenteLaReina': '1793695444199705', 'BlueConnect_Higueras': '6656136680722072', 'BlueConnect_Gaibiel': '5391043246414189', 'BlueConnect_Geldo': '8516784775362356', 'BlueConnect_Jerica': '5975090540842959', 'BlueConnect_Pavias': '1356528228524153', 'BlueConnect_PinaMontalgrao': '2506461416330061', 'BlueConnect_Matet': '9258757093789617', 'BlueConnect_Navajas': '9094896183527888', 'BlueConnect_Sacañet': '3768041338358500', 'BlueConnect_Soneja': '4231446180039296', 'Blueconnect_SotdeFerrer': '7874689117701236', 'Blueconnect_Teresa': '8071317998906499', 'Blueconnect_Torás': '3252031246220682', "Blueconnect_Vall D'Almonacid": '4763311310341999', 'Blueconnect_VillanuevadeViver': '1200777995213507', 'Blueconnect_Viver': '1636787129760256'}
def send_data_to_iqmenic(boya, fecha, temperatura, ph, orp, conductividad, alerta, latitud, longitud):
    endpoint_url = "https://apdata.iqmenic.com/iqmdata.php?COMM=pydata"
    headers = {'Content-Type': 'application/json'}
    data = {
        "id": str(diccion[boya]),
        "Fecha": str(datetime.strptime(fecha, '%a, %d %b %Y %H:%M:%S %z').isoformat()),
        "Propiedades": [
            {
                "Temperatura": str(temperatura),
                "pH": str(ph),
                "ORP": str(orp),
                "Conductividad": str(conductividad),
                "Alerta": str(alerta),
                "Latitud": str(latitud),
                "Longitud": str(longitud)
            }
        ]
    }
    response = requests.post(endpoint_url, headers=headers, data=json.dumps(data))
    print(json.dumps(data))
    if response.status_code == 200:
        data = pd.DataFrame([data])
        data.to_excel('Registro_OpenMS.xlsx')
    else:
        print(f"Failed to send data. Status code: {response.status_code}")
        print(response.text)

def eliminar_correos(asunto, email_account, password, imap_server="imap.iqmenic.com"):
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_account, password)
        mail.select("inbox")
        decoded_subject, encoding = decode_header(asunto)[0]
        if isinstance(decoded_subject, bytes):
            decoded_subject = decoded_subject.decode(encoding or 'utf-8', errors='replace')
        sanitized_subject = decoded_subject.encode('ascii', errors='replace').decode('ascii').replace("?", "0")
        search_criteria = f'(HEADER Subject "{sanitized_subject}")'
        status, messages = mail.search(None, search_criteria)
        if status != "OK":
            print(f"No se encontraron correos con el asunto: {sanitized_subject}")
            return
        for num in messages[0].split():
            mail.store(num, '+FLAGS', '\\Deleted')
        mail.expunge()
        mail.close()
        mail.logout()
        print(f"Correos eliminados exitosamente con el asunto: {sanitized_subject}")
    except imaplib.IMAP4.error as e:
        print(f"Error de autenticación: {str(e)}")
    except Exception as e:
        print(f"Error al eliminar correos: {str(e)}")

def ubicaciones(boya):
    url = 'http://openms.iqmenic.com/ubicaciones.xlsx'
    df = pd.read_excel(url)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df_boya = df.query('Elemento == @boya')
    if df_boya.empty:
        return {"error": f"No se encontraron datos para la boya '{boya}'"}
    json_result = {
        'Sensor': df_boya['Elemento'].tolist(),
        'Latitud': df_boya['Latitud'].tolist(),
        'Longitud': df_boya['Longitud'].tolist(),
        'Fecha': df_boya['Fecha'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()}
    return json_result
def main():
    username = "dev@iqmenic.com"
    password = "s#TDvKeI;"
    mail = connect_to_email(username, password)
    email_data = extract_emails_info(mail)
    mail.logout()
    df = pd.DataFrame(email_data)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    for i in range(len(df)):
      fecha = df.iloc[i]['Fecha']
      temperatura = df.iloc[i]['Temperatura (°C)']
      ph = df.iloc[i]['pH']
      orp = df.iloc[i]['ORP (mV)']
      conductividad = df.iloc[i]['Conductividad (µS)']
      if str(df.iloc[i]['Asunto']).find(": nueva medición") != -1:
          boya = df.iloc[i]['Asunto'].split(":")[0]
          alerta = 'False'
          latitud = ubicaciones(boya[12:])['Latitud'][-1]
          longitud = ubicaciones(boya[12:])['Longitud'][-1]
      elif str(df.iloc[i]['Asunto']).find("te necesita!") != -1 or str(df.iloc[i]['Asunto']).find("en modo de espera") != -1:
          boya = df.iloc[i]['Asunto'].split(" ")[0]
          alerta = 'True'
          latitud = ubicaciones(boya[12:])['Latitud'][-1]
          longitud = ubicaciones(boya[12:])['Longitud'][-1]
      else:
          boya = 'None'
          alerta = 'True'
          latitud = 'None'
          longitud = 'None'
      send_data_to_iqmenic(boya, fecha, temperatura, ph, orp, conductividad, alerta, latitud, longitud)
      asunto = str(df.iloc[i]['Asunto']).encode('utf-8').decode('utf-8')
      cuerpo = str(df.iloc[i]['Cuerpo']).encode('utf-8').decode('utf-8')
      eliminar_correos(asunto, username, password)
      time.sleep(random.random())
    dt = pd.read_excel('Registro_OpenMS.xlsx')
    dt = dt[~dt.duplicated()]
    dt.to_excel('Registro_OpenMS.xlsx')
if __name__ == "__main__":
    main()
