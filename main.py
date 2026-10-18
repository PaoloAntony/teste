from read_playlist import  connect_spotify, get_music, salvar_musicas
from check_artist import *
# Informe o nome ou ID da playlist.
# None significa ler as músicas curtidas.
# Quantidade máxima de faixas. None significa todas.

playlist = None
max_results = None

def main(playlist, max_results):
    
    sp = connect_spotify()


    musicas = get_music(
        sp,
        playlist=playlist,
        max_results=max_results,
    )

    salvar_musicas(musicas)

    print(f"\nArtistas encontrados: {len(musicas)}")
    print(musicas)
    

    artistas_processados = set()

    for musica in musicas:
        for artista in musica["artistas"]:
            chave = artista.strip().casefold()

            # Evita repetir o artista nesta execução
            if chave in artistas_processados:
                continue

            artistas_processados.add(chave)

            # Evita consultar artistas que já estão no CSV
            if artista_existe(artista):
                print(f"Artista já cadastrado: {artista}")
                continue

            print(f"Consultando gênero: {artista}")
            generos = consultar_generos(artista)

            if generos:
                salvar_artista(artista, generos)
            else:
                print(f"Nenhum gênero encontrado para {artista}")


if __name__ == "__main__":
    main(playlist, max_results)



#Usar parquet depois porqure faciulita a procura no banco de dados
#Temos que normalizar os dados e definir regras de gênero pra cada um deles