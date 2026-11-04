from sujeira.nucleo import aplicar_sujeira

#Configura quais colunas do arquivo de itens_compra recebem cada tipo de problema
def sujar_itens_compra(caminho_csv, id_lote):
    return aplicar_sujeira(
        caminho_csv,
        id_lote,
        colunas_numericas=["valor_unitario", "desconto", "valor_total_item"]
    )