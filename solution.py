import requests
import folium
import os
from dotenv import load_dotenv

load_dotenv()
SPTRANS_TOKEN = os.getenv("TOKEN")
print("Token carregado:", bool(SPTRANS_TOKEN))

BASE_URL = "https://api.olhovivo.sptrans.com.br/v2.1"

def criar_mapa():
    sessao = requests.Session()

    autenticacao = sessao.post(
        f"{BASE_URL}/Login/Autenticar",
        params={"token": SPTRANS_TOKEN}
    )

    print("Status HTTP:", autenticacao.status_code)
    print("Resposta da API:", autenticacao.text)

    if autenticacao.status_code != 200 or autenticacao.json() is not True:
        print("Erro na autenticação. Verifique seu token.")
        return

    linhas = sessao.get(
        f"{BASE_URL}/Linha/Buscar",
        params={"termosBusca": "7021-10"}
    ).json()

    linhas = sessao.get(
        f"{BASE_URL}/Linha/Buscar",
        params={"termosBusca": "7021-10"}
    ).json()

    if not linhas:
        print("Linha não encontrada.")
        return

    codigo_linha = linhas[0]["cl"]


    paradas = sessao.get(
        f"{BASE_URL}/Parada/BuscarParadasPorLinha",
        params={"codigoLinha": codigo_linha}
    ).json()

   
    resposta = sessao.get(
        f"{BASE_URL}/Posicao/Linha",
        params={"codigoLinha": codigo_linha}
    )
    resposta.raise_for_status()
    dados = resposta.json()

    
    coordenadas = [
        (p["py"], p["px"])
        for p in paradas
        if p.get("py") is not None and p.get("px") is not None
    ]

    if coordenadas:
        centro = coordenadas[0]
    else:
        centro = (-23.5505, -46.6333)

    mapa = folium.Map(location=centro, zoom_start=13)

    
    for parada in paradas:
        latitude = parada.get("py")
        longitude = parada.get("px")

        if latitude is not None and longitude is not None:
            folium.Marker(
                location=[latitude, longitude],
                popup=parada.get("np", "Parada de ônibus"),
                tooltip="Parada de ônibus",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(mapa)

  
    for onibus in dados.get("vs", []):
        latitude = onibus.get("py")
        longitude = onibus.get("px")

        if latitude is not None and longitude is not None:
            folium.Marker(
                location=[latitude, longitude],
                popup=f"Ônibus: {onibus.get('p', 'Não identificado')}",
                tooltip="Ônibus em circulação",
                icon=folium.Icon(color="red", icon="bus")
            ).add_to(mapa)

    mapa.save("mapa_onibus.html")
    print("Mapa criado: mapa_onibus.html")

if __name__ == "__main__":
    criar_mapa()