from pathlib import Path
from datetime import datetime, timedelta
import csv
import random

BASE_DIR = Path(__file__).resolve().parent.parent

#Duração aproximada das partidas de acordo com o gênero do jogo, em minutos
DURACAO_PARTIDA = {
    "FPS": (15, 45),
    "RPG": (20, 90),
    "Ação": (15, 50),
    "Aventura": (20, 60),
    "Estratégia": (20, 75),
    "Corrida": (5, 30),
    "Esportes": (10, 30),
    "MOBA": (15, 50),
    "Simulação": (20, 90),
    "Luta": (3, 15),
    "Survival": (20, 90)
}

def calcular_quantidade_partidas(duracao_sessao, genero_jogo):
    duracao_minima = DURACAO_PARTIDA[genero_jogo][0]

    if duracao_sessao < (duracao_minima + 5):
        return 0

    #Algumas sessões podem não possuir partidas
    if random.random() < 0.10:
        return 0

    maximo_possivel = max(1, min(8, duracao_sessao // (duracao_minima + 8)))

    #A distribuição favorece quantidades menores de partidas
    quantidade = int(round(random.triangular(1, maximo_possivel, 1)))
    return max(1, min(quantidade, maximo_possivel))

def gerar_resultado():
    return random.choices(
        ["Vitória", "Derrota", "Empate"],
        weights=[47, 47, 6],
        k=1
    )[0]

def gerar_partidas_sessao(sessao, proximo_partida_id):
    sessao_id = int(sessao["sessao_id"])
    genero_jogo = sessao["genero_jogo"]
    data_inicio_sessao = datetime.strptime(sessao["data_inicio_sessao"], "%Y-%m-%d %H:%M:%S")
    data_fim_sessao = datetime.strptime(sessao["data_fim_sessao"], "%Y-%m-%d %H:%M:%S")
    duracao_sessao = int((data_fim_sessao - data_inicio_sessao).total_seconds() // 60)
    quantidade_partidas = calcular_quantidade_partidas(duracao_sessao, genero_jogo)

    if quantidade_partidas == 0:
        return [], proximo_partida_id

    margem_inicio_max = max(2, min(10, duracao_sessao // 6))
    margem_fim_max = max(2, min(10, duracao_sessao // 6))
    margem_inicio = random.randint(2, margem_inicio_max)
    margem_fim = random.randint(2, margem_fim_max)
    cursor = data_inicio_sessao + timedelta(minutes=margem_inicio)
    limite_final = data_fim_sessao - timedelta(minutes=margem_fim)
    partidas = []
    duracao_minima, duracao_maxima = DURACAO_PARTIDA[genero_jogo]

    for _ in range(quantidade_partidas):
        minutos_restantes = int((limite_final - cursor).total_seconds() // 60)

        if minutos_restantes < duracao_minima:
            break

        duracao_maxima_real = min(duracao_maxima, minutos_restantes)
        duracao = random.randint(duracao_minima, duracao_maxima_real)
        data_inicio = cursor
        data_fim = data_inicio + timedelta(minutes=duracao)
        resultado = gerar_resultado()
        pontuacao = duracao * random.randint(8, 25)

        if resultado == "Vitória":
            pontuacao += random.randint(100, 600)

        pontuacao = min(pontuacao, 5000)
        experiencia_ganha = duracao * random.randint(2, 8)

        if resultado == "Vitória":
            experiencia_ganha += random.randint(20, 150)

        partida = {
            "partida_id": proximo_partida_id,
            "sessao_id": sessao_id,
            "data_inicio_partida": data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "data_fim_partida": data_fim.strftime("%Y-%m-%d %H:%M:%S"),
            "duracao_minutos": duracao,
            "resultado": resultado,
            "pontuacao": pontuacao,
            "experiencia_ganha": experiencia_ganha
        }
        partidas.append(partida)
        proximo_partida_id += 1

        intervalo = random.randint(2, 12)
        cursor = data_fim + timedelta(minutes=intervalo)

    return partidas, proximo_partida_id

def gerar_arquivo_partidas(caminho_sessoes):
    pasta = BASE_DIR / "output"
    pasta.mkdir(exist_ok=True)
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / f"partidas_{momento}.csv"
    colunas = [
        "partida_id",
        "sessao_id",
        "data_inicio_partida",
        "data_fim_partida",
        "duracao_minutos",
        "resultado",
        "pontuacao",
        "experiencia_ganha"
    ]

    with open(caminho_sessoes, "r", newline="", encoding="utf-8-sig") as arquivo_sessoes:
        leitor = csv.DictReader(arquivo_sessoes)
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo_partidas:
            escritor = csv.DictWriter(arquivo_partidas, fieldnames=colunas)
            escritor.writeheader()
            proximo_partida_id = 1

            for sessao in leitor:
                (partidas, proximo_partida_id) = gerar_partidas_sessao(
                    sessao,
                    proximo_partida_id
                )
                for partida in partidas:
                    escritor.writerow(partida)
    return caminho
