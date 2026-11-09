from sujeira.nucleo import aplicar_sujeira

#Configura quais colunas do arquivo de jogadores recebem cada tipo de problema
def sujar_jogadores(caminho_csv):
    return aplicar_sujeira(
        caminho_csv,
        colunas_ausentes=["cidade", "estado", "genero"],
        colunas_texto=["cidade", "estado", "pais", "genero"],
        colunas_data=["data_nascimento", "data_criacao_conta"]
    )