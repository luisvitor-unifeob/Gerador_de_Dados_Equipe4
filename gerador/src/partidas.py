from pathlib import Path
from datetime import datetime, timedelta
import csv
import random
from src.estado import obter_proximo_id, atualizar_ultimo_id

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

def calcular_probabilidades_resultado(skill):
    # Skill Gaussiana ajusta a taxa de vitória entre ~28% e ~66%
    taxa_vitoria = max(0.28, min(0.66, 0.47 + (skill * 0.08)))
    taxa_empate = 0.06
    taxa_derrota = 1.0 - taxa_vitoria - taxa_empate
    return [taxa_vitoria, taxa_derrota, taxa_empate]

def gerar_resultado(skill=0.0):
    pesos = calcular_probabilidades_resultado(skill)
    return random.choices(
        ["Vitória", "Derrota", "Empate"],
        weights=pesos,
        k=1
    )[0]

def gerar_partidas_sessao(sessao, proximo_partida_id, skill=0.0):
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
        duracao = int(random.triangular(
            duracao_minima,
            duracao_maxima_real,
            duracao_minima + (duracao_maxima_real - duracao_minima) * 0.35
        ))
        data_inicio = cursor
        data_fim = data_inicio + timedelta(minutes=duracao)
        resultado = gerar_resultado(skill)

        multiplicador_skill = max(0.7, 1.0 + (skill * 0.15))
        pontuacao_base = int(duracao * random.uniform(10, 22) * multiplicador_skill)
        if resultado == "Vitória":
            pontuacao_base += random.randint(150, 500)
        pontuacao = min(pontuacao_base, 5000)

        xp_base = int(duracao * random.uniform(3, 7) * multiplicador_skill)
        if resultado == "Vitória":
            xp_base += random.randint(30, 120)
        experiencia_ganha = xp_base

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

def gerar_arquivo_partidas(id_lote, caminho_sessoes):
    pasta = BASE_DIR / "output/.tmp"
    pasta.mkdir(exist_ok=True)
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / f"{id_lote}-partidas_{momento}.csv"
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

    skills_jogadores = {}
    proximo_partida_id = obter_proximo_id("ultimo_partida_id")

    with open(caminho_sessoes, "r", newline="", encoding="utf-8-sig") as arquivo_sessoes:
        leitor = csv.DictReader(arquivo_sessoes)
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo_partidas:
            escritor = csv.DictWriter(arquivo_partidas, fieldnames=colunas)
            escritor.writeheader()

            for sessao in leitor:
                player_id = int(sessao["player_id"])
                if player_id not in skills_jogadores:
                    skills_jogadores[player_id] = random.gauss(0.0, 1.0)
                skill = skills_jogadores[player_id]

                (partidas, proximo_partida_id) = gerar_partidas_sessao(
                    sessao,
                    proximo_partida_id,
                    skill
                )
                for partida in partidas:
                    escritor.writerow(partida)

    atualizar_ultimo_id("ultimo_partida_id", proximo_partida_id - 1)
    return caminho
