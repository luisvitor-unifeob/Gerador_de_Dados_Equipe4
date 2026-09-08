from src.jogadores import gerar_arquivo_jogadores
from src.sessoes import gerar_arquivo_sessoes
from src.partidas import gerar_arquivo_partidas
from src.compras import gerar_arquivo_compras
from src.itens import gerar_arquivo_itens
from src.itens_compra import gerar_arquivo_itens_compra


QUANTIDADE = 50_000

# abrir os arquivos várias vezes pode desacelerar demais o código,
# já que, nas análises finais, vamos gerar algumas centenas de milhares de entradas
arquivo_jogadores = gerar_arquivo_jogadores(QUANTIDADE)
arquivo_sessoes = gerar_arquivo_sessoes(arquivo_jogadores)
arquivo_partidas = gerar_arquivo_partidas(arquivo_sessoes)

arquivo_compras = gerar_arquivo_compras(arquivo_sessoes, arquivo_partidas)
arquivo_itens = gerar_arquivo_itens()
arquivo_itens_compra = (gerar_arquivo_itens_compra(arquivo_compras, arquivo_itens))

print("Dados gerados com sucesso!")
