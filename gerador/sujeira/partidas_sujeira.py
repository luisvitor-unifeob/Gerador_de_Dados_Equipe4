from sujeira.nucleo import aplicar_sujeira

#Configura quais colunas do arquivo de partidas recebem cada tipo de problema
def sujar_partidas(caminho_csv):
    return aplicar_sujeira(
        caminho_csv,
        colunas_ausentes=["resultado"],
        colunas_texto=["resultado"],
        colunas_data=["data_inicio_partida", "data_fim_partida"]
    )