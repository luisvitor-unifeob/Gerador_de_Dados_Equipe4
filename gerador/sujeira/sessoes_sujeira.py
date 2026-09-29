from sujeira.nucleo import aplicar_sujeira

#Configura quais colunas do arquivo de sessoes recebem cada tipo de problema
def sujar_sessoes(caminho_csv):
    return aplicar_sujeira(
        caminho_csv,
        colunas_ausentes=["plataforma"],
        colunas_texto=["plataforma", "genero_jogo"],
        colunas_data=["data_inicio_sessao", "data_fim_sessao"]
    )