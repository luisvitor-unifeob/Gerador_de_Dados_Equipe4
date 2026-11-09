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

from time import sleep
import os
from pathlib import Path
import shutil
import subprocess

DIR_OUT_GERADOR = Path("/opt/projeto/gerador/out")
IP_VM2 = "192.168.122.11"
MODULO_RSYNC_VM2 = "recebe_csv"
RSYNC_DESTINO = f"rsync://{IP_VM2}/{MODULO_RSYNC_VM2}/"

QUANTIDADE = 5_000
id_lote = 1

def enviar_para_vm2() -> bool:
    """Empurra os CSVs gerados para a VM 2 de forma atômica e limpa a pasta local após a entrega."""
    if not DIR_OUT_GERADOR.exists():
        print(f"Erro: Diretório de saída {DIR_OUT_GERADOR} não existe.")
        return False

    arquivos = list(DIR_OUT_GERADOR.glob("*.csv"))
    if not arquivos:
        print("Nenhum arquivo CSV encontrado para envio.")
        return True

    env = os.environ.copy()
    env["PATH"] = (
        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:"
        + env.get("PATH", "")
    )
    rsync_bin = shutil.which("rsync", path=env["PATH"]) or "/usr/bin/rsync"

    cmd = [
        rsync_bin,
        "-avz",
        "--delay-updates",  # Monta o lote na VM 2 de forma oculta e libera todos juntos
        "--remove-source-files",  # Deleta da VM 1 SOMENTE após a entrega confirmada
        f"{DIR_OUT_GERADOR}/",
        RSYNC_DESTINO,
    ]

    print(f"Enviando {len(arquivos)} arquivo(s) para a VM 2 ({IP_VM2})...")
    result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print("Sucesso: Lote enviado e arquivos locais removidos com sucesso.")
        return True
    else:
        print(f"Erro ao enviar via rsync (Código {result.returncode}):\n{result.stderr}")
        return False

while True:
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

    print("Dados gerados, arquivos limpos removidos e falhas documentadas com sucesso!")
    id_lote += 1

    enviar_para_vm2()
    sleep(5)
