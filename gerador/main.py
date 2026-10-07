from src.jogadores import gerar_arquivo_jogadores
from src.sessoes import gerar_arquivo_sessoes
from src.partidas import gerar_arquivo_partidas
from src.compras import gerar_arquivo_compras
from src.itens import gerar_arquivo_itens
from src.itens_compra import gerar_arquivo_itens_compra

from sujeira.jogadores_sujeira import sujar_jogadores
from sujeira.sessoes_sujeira import sujar_sessoes
from sujeira.partidas_sujeira import sujar_partidas
from sujeira.compras_sujeira import sujar_compras
from sujeira.itens_sujeira import sujar_itens
from sujeira.itens_compra_sujeira import sujar_itens_compra

QUANTIDADE = 10_000

# Geração dos arquivos originais em output/
arquivo_jogadores = gerar_arquivo_jogadores(QUANTIDADE)
arquivo_sessoes = gerar_arquivo_sessoes(arquivo_jogadores)
arquivo_partidas = gerar_arquivo_partidas(arquivo_sessoes)

arquivo_compras = gerar_arquivo_compras(arquivo_sessoes, arquivo_partidas)
arquivo_itens = gerar_arquivo_itens()
arquivo_itens_compra = gerar_arquivo_itens_compra(arquivo_compras, arquivo_itens)

# Etapa de sujeira:
# - Gera cópias em output/sujos/
# - Documenta as falhas em output/sujos/relatorio_falhas.json
# - Exclui os arquivos sem falhas de output/ para economizar disco
sujar_jogadores(arquivo_jogadores)
sujar_sessoes(arquivo_sessoes)
sujar_partidas(arquivo_partidas)
sujar_compras(arquivo_compras)
sujar_itens(arquivo_itens)
sujar_itens_compra(arquivo_itens_compra)

print("Dados gerados, arquivos limpos removidos e falhas documentadas com sucesso!")