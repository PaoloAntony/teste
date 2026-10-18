
import os
import csv
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LAST_FM_API_KEY")
URL = "https://ws.audioscrobbler.com/2.0/"

CAMINHO = (
    Path(__file__).parent
    / "database"
    / "tags_lastfm.csv"
)


def baixar_tags():
    if not API_KEY:
        raise ValueError(
            "Configure LAST_FM_API_KEY no arquivo .env"
        )

    parametros = {
        "method": "tag.getTopTags",
        "api_key": API_KEY,
        "format": "json",
    }

    resposta = requests.get(
        URL,
        params=parametros,
        timeout=30,
    )
    resposta.raise_for_status()
    dados = resposta.json()

    if "error" in dados:
        raise RuntimeError(dados.get("message", "Erro na Last.fm"))

    tags = dados.get("toptags", {}).get("tag", [])

    if isinstance(tags, dict):
        tags = [tags]

    CAMINHO.parent.mkdir(parents=True, exist_ok=True)

    with open(
        CAMINHO,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["tag", "popularidade"])

        for tag in tags:
            escritor.writerow([
                tag.get("name", ""),
                tag.get("count", 0),
            ])

    print(f"Tags encontradas: {len(tags)}")
    print(f"Arquivo salvo em: {CAMINHO}")


if __name__ == "__main__":
    baixar_tags()
