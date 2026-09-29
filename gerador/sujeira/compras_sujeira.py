from sujeira.nucleo import aplicar_sujeira

#Configura quais colunas do arquivo de compras recebem cada tipo de problema
def sujar_compras(caminho_csv):
    return aplicar_sujeira(
        caminho_csv,
        colunas_ausentes=["data_compra"],
        colunas_data=["data_compra"]
    )