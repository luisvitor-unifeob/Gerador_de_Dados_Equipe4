from pathlib import Path
from datetime import datetime, timedelta
import csv
import random
from src.estado import (
    obter_proximo_id,
    atualizar_ultimo_id,
    carregar_pool,
    salvar_pool
)
from src.regras import escolher_perfil_compra

BASE_DIR = Path(__file__).resolve().parent.parent

#Probabilidade de compra em uma sessão para cada perfil de jogador
PERFIS_COMPRA = {
    "nao_pagante": 0.00,
    "minnow": 0.04,
    "dolphin": 0.12,
    "whale": 0.38
}

def carregar_partidas(caminho_partidas):
    partidas = {}

    with open(caminho_partidas, "r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        for partida in leitor:
            sessao_id = int(partida["sessao_id"])
            data_inicio = datetime.strptime(partida["data_inicio_partida"], "%Y-%m-%d %H:%M:%S")
            data_fim = datetime.strptime(partida["data_fim_partida"], "%Y-%m-%d %H:%M:%S")

            if sessao_id not in partidas:
                partidas[sessao_id] = []

            partidas[sessao_id].append((data_inicio, data_fim))

    #Ordena as partidas pelo horário de início
    for sessao_id in partidas:
        partidas[sessao_id].sort(key=lambda valor: valor[0])
    return partidas

def calcular_intervalos_livres(data_inicio, data_fim, partidas):
    intervalos = []
    cursor = data_inicio

    #Guarda os espaços existentes antes e entre as partidas
    for inicio_partida, fim_partida in partidas:
        if inicio_partida > cursor:
            intervalos.append((cursor, inicio_partida))
        cursor = max(cursor, fim_partida)

    #Também considera o período depois da última partida
    if cursor < data_fim:
        intervalos.append((cursor, data_fim))

    return [
        intervalo
        for intervalo in intervalos
        if (intervalo[1] - intervalo[0]).total_seconds() >= 3
    ]

def gerar_data_compra(intervalos, datas_usadas):
    if not intervalos:
        return None

    #Intervalos maiores têm mais chance de receber a compra
    pesos = [
        max(1, int((fim - inicio).total_seconds()))
        for inicio, fim in intervalos
    ]

    for _ in range(20):
        inicio, fim = random.choices(intervalos, weights=pesos, k=1)[0]
        segundos = int((fim - inicio).total_seconds())

        if segundos < 3:
            continue

        deslocamento = random.randint(1, segundos - 1)
        data_compra = inicio + timedelta(seconds=deslocamento)

        #Evita duas compras exatamente no mesmo horário
        if data_compra not in datas_usadas:
            return data_compra
    return None

def calcular_quantidade_compras(perfil):
    probabilidade = PERFIS_COMPRA[perfil]

    if random.random() >= probabilidade:
        return 0

    if perfil == "whale":
        return random.choices([1, 2, 3], weights=[55, 35, 10], k=1)[0]
    return random.choices([1, 2], weights=[90, 10], k=1)[0]

def gerar_arquivo_compras(id_lote, caminho_sessoes, caminho_partidas):
    pasta = BASE_DIR / "output/.tmp"
    pasta.mkdir(exist_ok=True)
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / f"{id_lote}-compras_{momento}.csv"
    colunas = [
        "compra_id",
        "sessao_id",
        "data_compra"
    ]

    partidas_por_sessao = carregar_partidas(caminho_partidas)
    pool = carregar_pool()
    pool_alterado = False
    perfis_jogadores = {}
    proximo_compra_id = obter_proximo_id("ultimo_compra_id")

    with open(caminho_sessoes, "r", newline="", encoding="utf-8-sig") as arquivo_sessoes:
        leitor = csv.DictReader(arquivo_sessoes)
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo_compras:
            escritor = csv.DictWriter(arquivo_compras, fieldnames=colunas)
            escritor.writeheader()

            for sessao in leitor:
                sessao_id = int(sessao["sessao_id"])
                player_id = int(sessao["player_id"])
                nivel = int(sessao.get("nivel_fim", 1))

                if player_id not in perfis_jogadores:
                    jogador_info = pool.get(str(player_id))
                    if jogador_info and "perfil_compra" in jogador_info:
                        perfil = jogador_info["perfil_compra"]
                        if perfil == "nao_pagante" and nivel >= 15 and random.random() < 0.005:
                            perfil = "minnow"
                            jogador_info["perfil_compra"] = perfil
                            pool_alterado = True
                        perfis_jogadores[player_id] = perfil
                    else:
                        perfis_jogadores[player_id] = escolher_perfil_compra(nivel)

                perfil = perfis_jogadores[player_id]
                quantidade = calcular_quantidade_compras(perfil)

                if quantidade == 0:
                    continue

                data_inicio = datetime.strptime(sessao["data_inicio_sessao"], "%Y-%m-%d %H:%M:%S")
                data_fim = datetime.strptime(sessao["data_fim_sessao"], "%Y-%m-%d %H:%M:%S")

                #As compras só podem acontecer fora dos períodos de partida
                partidas = partidas_por_sessao.get(sessao_id, [])
                intervalos = calcular_intervalos_livres(data_inicio, data_fim, partidas)
                datas_usadas = set()

                for _ in range(quantidade):
                    data_compra = gerar_data_compra(intervalos, datas_usadas)

                    if data_compra is None:
                        break

                    datas_usadas.add(data_compra)
                    escritor.writerow({
                        "compra_id": proximo_compra_id,
                        "sessao_id": sessao_id,
                        "data_compra": data_compra.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    proximo_compra_id += 1

    if pool_alterado:
        salvar_pool(pool)
    atualizar_ultimo_id("ultimo_compra_id", proximo_compra_id - 1)
    return caminho
