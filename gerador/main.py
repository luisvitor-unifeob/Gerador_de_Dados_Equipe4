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

from time import sleep, time
from uuid import uuid4
from shutil import move
from pathlib import Path

def gerar_lote_id_unico() -> str:
    timestamp_ms = int(time() * 1000)
    uuid_sufixo = uuid4().int % 10000
    return f"{timestamp_ms}{uuid_sufixo:04d}"

QUANTIDADE = 5_000
PASTA_CSVS = Path("/opt/projeto/csvs/")

while True:
    id_lote = gerar_lote_id_unico()

    # Geração dos arquivos originais em output/
    arquivo_jogadores    =     gerar_arquivo_jogadores( id_lote, QUANTIDADE                        )
    arquivo_sessoes      =       gerar_arquivo_sessoes( id_lote, arquivo_jogadores                 )
    arquivo_partidas     =      gerar_arquivo_partidas( id_lote, arquivo_sessoes                   )

    arquivo_compras      =       gerar_arquivo_compras( id_lote, arquivo_sessoes, arquivo_partidas )
    arquivo_itens        =         gerar_arquivo_itens( id_lote                                    )
    arquivo_itens_compra =  gerar_arquivo_itens_compra( id_lote, arquivo_compras, arquivo_itens    )

    # Etapa de sujeira:
    # - Gera cópias em output/sujos/
    # - Documenta as falhas em output/sujos/relatorio_falhas.json
    # - Exclui os arquivos sem falhas de output/ para economizar disco
    sujar_jogadores     ( arquivo_jogadores    )
    sujar_sessoes       ( arquivo_sessoes      )
    sujar_partidas      ( arquivo_partidas     )
    sujar_compras       ( arquivo_compras      )
    sujar_itens         ( arquivo_itens        )
    sujar_itens_compra  ( arquivo_itens_compra )

    for arquivo in [
        arquivo_jogadores, arquivo_itens,
        arquivo_partidas, arquivo_sessoes,
        arquivo_compras, arquivo_itens_compra
    ]:
        caminho_original = Path(arquivo)
        nome_arquivo = caminho_original.name
        novo_caminho = PASTA_CSVS / Path(".tmp") / nome_arquivo
        move(novo_caminho, PASTA_CSVS)


    print("Dados gerados, arquivos limpos removidos e falhas documentadas com sucesso!")
    sleep(5)
