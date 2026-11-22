from src.jogadores import gerar_arquivo_jogadores
from src.sessoes import gerar_arquivo_sessoes
from src.partidas import gerar_arquivo_partidas
from src.compras import gerar_arquivo_compras
from src.itens import gerar_arquivo_itens
from src.itens_compra import gerar_arquivo_itens_compra
from src.estado import obter_lote_atual

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
import os
import random as rnd

def gerar_lote_id_unico() -> str:
    timestamp_ms = int(time() * 1000)
    uuid_sufixo = uuid4().int % 10000
    return f"{timestamp_ms}{uuid_sufixo:04d}"

QUANTIDADE_INICIAL = 5000
QUANTIDADE_INCREMENTAL = rnd.betavariate(0.2, 0.5) * 400
TOTAL_LOTES = 100
PASTA_CSVS = Path("/gerador/gerador/output/")

for numero_lote in range(1, TOTAL_LOTES + 1):
    id_lote = gerar_lote_id_unico()
    lote_no_estado = obter_lote_atual()
    quantidade = QUANTIDADE_INICIAL if lote_no_estado == 0 else QUANTIDADE_INCREMENTAL

    # Geração dos arquivos originais em output/
    arquivo_jogadores    =     gerar_arquivo_jogadores( id_lote, quantidade                        )
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
        move(arquivo, PASTA_CSVS)


    print(f"Lote {numero_lote}/{TOTAL_LOTES} gerado com sucesso!")
    sleep(5)
