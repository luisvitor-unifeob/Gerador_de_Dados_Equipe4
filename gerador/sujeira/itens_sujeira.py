from sujeira.nucleo import aplicar_sujeira

#Configura quais colunas do arquivo de itens recebem cada tipo de problema
def sujar_itens(caminho_csv):
    return aplicar_sujeira(
        caminho_csv,
        colunas_ausentes=["raridade"],
        colunas_texto=["nome_item", "categoria_item", "raridade"],
        colunas_numericas=["preco_base"]
    )