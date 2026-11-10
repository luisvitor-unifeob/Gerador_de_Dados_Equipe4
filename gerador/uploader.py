from collections import defaultdict
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

DIR_OUT = Path("/opt/projeto/csvs")
IP_VM2 = "192.168.122.11"
RSYNC_DESTINO = f"rsync://{IP_VM2}/recebe_csv/"
ARQUIVOS_ESPERADOS = 6
INTERVALO_POLLING = 3


def main():
    DIR_OUT.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PATH"] = (
        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:"
        + env.get("PATH", "")
    )
    rsync_bin = shutil.which("rsync", path=env["PATH"]) or "/usr/bin/rsync"

    print(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Uploader Daemon (VM 1)"
        f" iniciado. Monitorando: {DIR_OUT}"
    )

    while True:
        try:
            # Agrupa arquivos na pasta de saída pelo ID do lote (prefixo antes do hífen)
            lotes = defaultdict(list)
            for csv_file in DIR_OUT.glob("*.csv"):
                if csv_file.name.startswith("."):
                    continue
                lote_id = csv_file.name.split("-")[0]
                lotes[lote_id].append(csv_file)

            # Envia via rsync apenas lotes com os 6 arquivos completos
            for lote_id, files in list(lotes.items()):
                if len(files) == ARQUIVOS_ESPERADOS:
                    files_sorted = sorted(files, key=lambda f: f.name)
                    ts = time.strftime("%H:%M:%S")
                    print(
                        f"[{ts}] Lote {lote_id} completo na VM 1"
                        f" ({ARQUIVOS_ESPERADOS}/{ARQUIVOS_ESPERADOS})."
                        " Enviando..."
                    )

                    # Chamada rsync sem --remove-source-files (gerenciado pelo Python)
                    cmd = (
                        [rsync_bin, "-avz", "--delay-updates"]
                        + [str(f) for f in files_sorted]
                        + [RSYNC_DESTINO]
                    )

                    result = subprocess.run(cmd, env=env)

                    if result.returncode == 0:
                        # Limpeza explícita do lote na VM 1 após confirmação de entrega
                        for f_path in files_sorted:
                            try:
                                f_path.unlink()
                            except OSError as err:
                                print(
                                    f"[{ts}] Alerta ao remover {f_path.name}:"
                                    f" {err}"
                                )

                        print(
                            f"[{ts}] Lote {lote_id} enviado e removido da VM 1"
                            " com sucesso."
                        )
                    else:
                        print(
                            f"[{ts}] Erro no rsync (código {result.returncode})"
                            f" para o lote {lote_id}. Mantendo arquivos localmente."
                        )

        except Exception as e:
            print(
                f"[{time.strftime('%H:%M:%S')}] Erro no loop do uploader: {e}"
            )

        time.sleep(INTERVALO_POLLING)


if __name__ == "__main__":
    main()