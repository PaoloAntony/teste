
import os
import csv
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LAST_FM_API_KEY")
URL = "https://ws.audioscrobbler.com/2.0/"

CAMINHO_CSV = (
    Path(__file__).parent
    / "database"
    / "artistas.csv"
)


def consultar_generos(artista):
    if not API_KEY:
        raise ValueError(
            "Configure LAST_FM_API_KEY no arquivo .env"
        )

    parametros = {
        "method": "artist.getTopTags",
        "artist": artista,
        "api_key": API_KEY,
        "format": "json",
        "autocorrect": 1,
    }

    try:
        resposta = requests.get(
            URL,
            params=parametros,
            timeout=15
        )
        resposta.raise_for_status()
        dados = resposta.json()

        if "error" in dados:
            print(f"Erro da Last.fm: {dados.get('message')}")
            return []

        tags = dados.get("toptags", {}).get("tag", [])

        if isinstance(tags, dict):
            tags = [tags]

        generos = [
            tag["name"]
            for tag in tags
            if int(tag.get("count", 0)) > 0
        ]

        return generos[:10]

    except requests.RequestException as erro:
        print(f"Erro na consulta: {erro}")
        return []


def artista_existe(nome):
    if not CAMINHO_CSV.exists():
        return False

    with open(
        CAMINHO_CSV,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        for linha in leitor:
            artista = linha.get("artista", "").strip()

            if artista.casefold() == nome.strip().casefold():
                return True

    return False


def salvar_artista(nome, generos):
    CAMINHO_CSV.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if artista_existe(nome):
        print(f"Artista já cadastrado: {nome}")
        return

    arquivo_vazio = (
        not CAMINHO_CSV.exists()
        or CAMINHO_CSV.stat().st_size == 0
    )

    with open(
        CAMINHO_CSV,
        "a",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")

        if arquivo_vazio:
            escritor.writerow(["artista", "genêro"])

        escritor.writerow([nome, ", ".join(generos)])

    print(f"Artista salvo: {nome}")
