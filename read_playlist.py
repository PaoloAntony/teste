import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from pathlib import Path
import json


load_dotenv()

def connect_spotify():
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.environ["SPOTIPY_CLIENT_ID"],
            client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
            redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
            scope="user-library-read playlist-read-private",
            open_browser=True,
        )
    )

def find_playlist(sp, playlist_name_or_id):
    """Localiza uma playlist pelo nome ou ID."""
    playlists = sp.current_user_playlists(limit=50)

    while playlists:
        for playlist in playlists["items"]:
            if not playlist:
                continue

            if (
                playlist["id"] == playlist_name_or_id
                or playlist["name"].casefold()
                == playlist_name_or_id.casefold()
            ):
                return playlist["id"], playlist["name"]

        if not playlists["next"]:
            break

        playlists = sp.next(playlists)

    raise ValueError(
        f"Playlist não encontrada: {playlist_name_or_id}"
    )

def get_music(sp, playlist=None, max_results=None):
    """
    Retorna uma lista de músicas, cada uma com seu nome e todos os artistas.

    playlist: Nome ou ID da playlist. None significa músicas curtidas.
    max_results: Limite de faixas. None significa todas.
    """
    if max_results is not None and max_results < 1:
        raise ValueError("max_results deve ser positivo ou None.")

    musicas = []
    total = 0

    if playlist:
        playlist_id, playlist_name = find_playlist(sp, playlist)
        print(f"Lendo playlist: {playlist_name}")

        resultado = sp.playlist_items(
            playlist_id,
            limit=min(max_results or 100, 100),
            fields="items(track(name,artists(name))),next",
        )
    else:
        print("Lendo músicas curtidas.")

        resultado = sp.current_user_saved_tracks(
            limit=min(max_results or 50, 50)
        )

    ids_processados = set()

    while resultado:
        for item in resultado["items"]:
            if max_results is not None and total >= max_results:
                break

            musica = item.get("track")

            if not musica or not musica.get("artists"):
                continue

            nome_musica = musica.get("name")
            artistas = [
                artista["name"]
                for artista in musica["artists"]
                if artista.get("name")
            ]

            if not nome_musica or not artistas:
                continue

            # Evita duplicar a mesma faixa dentro da coleta.
            # Spotify pode retornar o mesmo ID em mais de uma posição.
            musica_id = musica.get("id")

            if musica_id and musica_id in ids_processados:
                continue

            if musica_id:
                ids_processados.add(musica_id)

            musicas.append({
                "nome": nome_musica,
                "artistas": artistas
            })

            total += 1

        if max_results is not None and total >= max_results:
            break

        if not resultado.get("next"):
            break

        resultado = sp.next(resultado)

    return musicas

def salvar_musicas(artistas_musicas):
    # Pasta onde este arquivo Python está localizado
    pasta_projeto = Path(__file__).resolve().parent

    # Cria a pasta database, caso ainda não exista
    pasta_database = pasta_projeto / "database"
    pasta_database.mkdir(parents=True, exist_ok=True)

    # Caminho do arquivo JSON
    caminho_arquivo = pasta_database / "musicas.json"

    with caminho_arquivo.open("w", encoding="utf-8") as arquivo:
        json.dump(
            artistas_musicas,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print(f"Músicas salvas em: {caminho_arquivo}")
