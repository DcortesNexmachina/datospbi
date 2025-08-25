comercios = {
  'b2e805d7-5ced-43d4-9167-a7c9d106dec6': 'ADELA GARTEIZ',
  'f7d23383-6760-4243-bca7-14dfa450599b': 'AURA',
  '9ad51f99-c068-4765-a986-1af093f09e0b': 'Ainhoa Oinetakoak',
  'abc93d7d-6b89-4ce7-8d6f-509e26c614e5': 'Alea',
  'c59bfdec-4928-4b00-bf23-2e4961bf6fd6': 'Azulillo Store',
  'a945e474-2e07-4f7c-aa6a-0f94c0b148c0': 'BAINILA',
  '5b91f650-7aa1-40f9-af67-319a723c34ba': 'Bed´s',
  'd8800187-7352-4b18-902c-ce0f30953841': 'Bonilla Fotografia',
  '85beb160-e9ae-4e32-985c-3c0b93abe77d': 'Concept Store',
  '6c0d54aa-6bab-4c48-8a31-3b3e9a1ccbc6': 'Euskal Souvenirs',
  'a56b4b4e-7cbe-44a7-a9f4-23fe5f05ce1c': 'Fotoetxe',
  'df0c6163-1f7e-4aec-a001-13e41632891a': 'KILIMAK',
  'e2ed77ed-5281-4d1d-8d4c-ccc9a2852e99': 'KUKI',
  '401f2760-082f-46bb-8b34-df53ef93176f': 'Kikaren Munduan',
  '149b2ee0-c3c2-4a4e-8c2a-012b8195a6c7': 'Kopinet',
  '3e00030c-6876-427c-b9c5-8054d589f000': 'LOREDER',
  'ca088348-8dd3-4167-9096-103a8eafbff8': 'LV Salon Nails',
  '24f68cc5-264b-4f6e-9ad7-c7dfd3af7f48': 'Mai Piu',
  'bfb79941-ed0f-43f4-93a8-5f515073026f': 'Nattex',
  '462fe792-aab2-4bc5-8acf-178085718368': 'Nere Sutraiak',
  'f7ba855f-afb7-4878-a275-49953c178504': 'Obabak',
  '1928aa05-964c-4185-a80e-08d5fc6bff9a': 'Optika Eguren',
  '5e18cd10-66d3-4a0f-8fa1-5905d2e88d49': 'Prueba',
  '3b1098a7-aab9-4837-8549-14d12964efb2': 'Selene Moda',
  '5f9b6b3b-0311-4644-bf49-ca419769ef82': 'Tistel',
  '2ddfd548-fdfb-41bd-b0cb-59cc58a3fb26': 'Ttipi Ttapa',
  'b36e095c-8845-4ae6-a895-26c94a0df037': 'ZIBU ZABU',
  '7f8ea27b-ce5a-4b86-b662-717cd0dea85c': 'Kopinet',
  'd9800197-7352-4b19-902c-ce0f30953941': 'Karinkara',
  'a8700086-0000-3a19-102f-ka0fe8913950': 'AB Decohogar',
  '24f68cc5-7cbe-3g25-a5e4-c7dfd3af7f48': 'Esencia Santurtzi',
  '9ad51f99-1496-vsc1-a4da-178085718368': 'Esencia Algorta',
  'df53ef93-176f-176f-176f-3c0x93abex7d': 'Esencia Barakaldo',
  '6bab5bas-5asd-4b19-aad4-zc12dzf5sdc4': 'Esencia Bilbao',
  'v5a4f8xc-2d8c-95cs-ad57-1atu5sdf5ad3': 'Nokora',
  'a5d8gad5-467z-4b19-9012-xe0f30953941': 'Kibuc',
  'af76345t-234n-rn2q-2348-dfnd83nqa034': 'Drogueria Amutio',
  'jndsa8ca-24na-9gds-sdms-as32ndp123na':'Cado Complementos'}


template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de Afluencia - {nombre_comercio}</title>
</head>
<body>
    <h1>Análisis de Afluencia de {nombre_comercio}</h1>
    <form action="/estadistica/cgi-bin/analizar_afluencia.py?id={id_comercio}" method="post">
        <label for="fecha_inicio">Fecha Inicio:</label>
        <input type="date" id="fecha_inicio" name="fecha_inicio" required><br><br>

        <label for="fecha_fin">Fecha Fin:</label>
        <input type="date" id="fecha_fin" name="fecha_fin" required><br><br>

        <input type="submit" value="Analizar Afluencia">
    </form>
    <div id="resultado" style="margin-top: 20px;"></div>
</body>
</html>
"""

for id_comercio, nombre_comercio in comercios.items():
    html_content = template.format(nombre_comercio=nombre_comercio, id_comercio=id_comercio)
    filename = f"{id_comercio.replace(' ', '_')}.html"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)

print("Archivos HTML generados exitosamente.")
