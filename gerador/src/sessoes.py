from pathlib import Path
from datetime import datetime, timedelta, time
import csv
import math
import random

#Pasta principal do gerador
BASE_DIR = Path(__file__).resolve().parent.parent

#Gêneros disponíveis
GENEROS_JOGO = [
    "FPS",
    "RPG",
    "Ação",
    "Aventura",
    "Estratégia",
    "Corrida",
    "Esportes",
    "MOBA",
    "Simulação",
    "Luta",
    "Survival"
]

#Plataformas compatíveis com cada gênero
PLATAFORMAS = {
    "FPS": ["PC", "PlayStation", "Xbox"],
    "RPG": ["PC", "PlayStation", "Xbox"],
    "Ação": ["PC", "PlayStation", "Xbox"],
    "Aventura": ["PC", "PlayStation", "Xbox"],
    "Estratégia": ["PC"],
    "Corrida": ["PC", "PlayStation", "Xbox"],
    "Esportes": ["PC", "PlayStation", "Xbox"],
    "MOBA": ["PC", "Mobile"],
    "Simulação": ["PC", "PlayStation", "Xbox"],
    "Luta": ["PC", "PlayStation", "Xbox"],
    "Survival": ["PC", "PlayStation", "Xbox"]
}

#Duração possível das sessões em minutos
TEMPO_SESSAO = {
    "FPS": (20, 120),
    "RPG": (60, 240),
    "Ação": (30, 150),
    "Aventura": (40, 180),
    "Estratégia": (40, 180),
    "Corrida": (20, 100),
    "Esportes": (20, 120),
    "MOBA": (25, 150),
    "Simulação": (60, 240),
    "Luta": (15, 90),
    "Survival": (60, 270)
}

def calcular_quantidade_sessoes(data_criacao, idade):
    hoje = datetime.now().date()
    dias_conta = max(1, (hoje - data_criacao).days)

    #Crescimento gradual e evita que contas antigas tenham automaticamente centenas de sessões.
    base = math.sqrt(dias_conta)

    #Perfil de atividade do jogador
    perfil = random.choices(
        ["casual", "regular", "ativo", "intenso"],
        weights=[35, 40, 20, 5],
        k=1
    )[0]
    fatores = {
        "casual": (0.35, 0.65),
        "regular": (0.65, 1.00),
        "ativo": (1.00, 1.50),
        "intenso": (1.50, 2.20)
    }
    minimo, maximo = fatores[perfil]
    fator = random.uniform(minimo, maximo)

    #Pequeno viés por faixa etária
    if idade <= 24:
        fator *= 1.15
    elif idade >= 45:
        fator *= 0.80
    elif idade >= 35:
        fator *= 0.90

    quantidade = int(round(base * fator * random.uniform(0.85, 1.15)))

    return max(1, quantidade)

def gerar_datas_inicio(data_criacao, quantidade):
    inicio = datetime.combine(data_criacao, time.min)
    agora = datetime.now().replace(microsecond=0)
    total_segundos = int((agora - inicio).total_seconds())
    if total_segundos <= 0:
        return [inicio]
    datas = []
    for _ in range(quantidade):
        #Beta gera um pequeno viés em direção às datas mais recentes
        proporcao = random.betavariate(1.4, 1.0)
        segundos = int(total_segundos * proporcao)
        data_inicio = inicio + timedelta(seconds=segundos)
        datas.append(data_inicio)
    datas.sort()
    return datas

def escolher_preferencias_jogador():
    quantidade_generos = random.choice([1, 2, 2, 3])
    generos_preferidos = random.sample(GENEROS_JOGO, quantidade_generos)
    quantidade_plataformas = random.choice([1, 1, 1, 2])
    plataformas_preferidas = random.sample(
        ["PC", "PlayStation", "Xbox"],
        quantidade_plataformas
    )
    return generos_preferidos, plataformas_preferidas

def escolher_genero(generos_preferidos):
    if random.random() < 0.95:
        return random.choice(generos_preferidos)
    outros_generos = [genero for genero in GENEROS_JOGO if genero not in generos_preferidos]
    if outros_generos:
        return random.choice(outros_generos)
    return random.choice(generos_preferidos)

def escolher_plataforma(genero_jogo, plataformas_preferidas):
    plataformas_disponiveis = PLATAFORMAS[genero_jogo]
    #Moba pode ocasionalmente ser jogado em dispositivo móvel
    if genero_jogo == "MOBA" and random.random() < 0.20:
        return "Mobile"
    compativeis = [
        plataforma for plataforma in plataformas_preferidas
        if plataforma in plataformas_disponiveis
    ]
    if compativeis:
        return random.choice(compativeis)
    return random.choice(plataformas_disponiveis)

def calcular_niveis(indice, quantidade_sessoes, nivel_atual):
    if nivel_atual <= 1:
        return 1, 1
    progresso_inicio = indice / quantidade_sessoes
    progresso_fim = (indice + 1) / quantidade_sessoes
    nivel_inicio = 1 + int((nivel_atual - 1) * progresso_inicio)
    nivel_fim = 1 + int((nivel_atual - 1) * progresso_fim)
    nivel_inicio = min(nivel_inicio, nivel_atual)
    nivel_fim = min(nivel_fim, nivel_atual)
    return nivel_inicio, nivel_fim

def gerar_sessoes_jogador(jogador, proximo_sessao_id):
    player_id = int(jogador["player_id"])
    idade = int(jogador["idade"])
    nivel_atual = int(jogador["nivel_jogador"])
    data_criacao = datetime.strptime(jogador["data_criacao_conta"], "%Y-%m-%d").date()
    quantidade_sessoes = calcular_quantidade_sessoes(data_criacao, idade)
    datas_inicio = gerar_datas_inicio(data_criacao, quantidade_sessoes)
    (generos_preferidos, plataformas_preferidas) = escolher_preferencias_jogador()
    agora = datetime.now().replace(microsecond=0)
    sessoes = []
    ultima_data_fim = None

    for data_inicio in datas_inicio:
        #Impede duas sessões do mesmo jogador de acontecerem juntas
        if ultima_data_fim is not None and data_inicio <= ultima_data_fim:
            intervalo = random.randint(30, 180)
            data_inicio = ultima_data_fim + timedelta(minutes=intervalo)
        #Se o ajuste empurrou a sessão para o futuro, ela não é criada
        if data_inicio >= agora:
            break
        genero_jogo = escolher_genero(generos_preferidos)
        plataforma = escolher_plataforma(genero_jogo, plataformas_preferidas)
        (tempo_minimo, tempo_maximo) = TEMPO_SESSAO[genero_jogo]
        duracao_minutos = random.randint(tempo_minimo, tempo_maximo)
        minutos_disponiveis = int((agora - data_inicio).total_seconds() // 60)
        if minutos_disponiveis < 1:
            break
        duracao_minutos = min(duracao_minutos, minutos_disponiveis)
        data_fim = data_inicio + timedelta(minutes=duracao_minutos)
        sessao = {
            "sessao_id": proximo_sessao_id,
            "player_id": player_id,
            "data_inicio_sessao": data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "data_fim_sessao": data_fim.strftime("%Y-%m-%d %H:%M:%S"),
            "duracao_minutos": duracao_minutos,
            "plataforma": plataforma,
            "genero_jogo": genero_jogo
        }
        sessoes.append(sessao)
        ultima_data_fim = data_fim
        proximo_sessao_id += 1
    #Calcula os níveis somente depois de saber quantas sessões realmente foram criadas.
    quantidade_real = len(sessoes)
    for indice, sessao in enumerate(sessoes):
        (nivel_inicio, nivel_fim) = calcular_niveis(indice, quantidade_real, nivel_atual)
        sessao["nivel_inicio"] = nivel_inicio
        sessao["nivel_fim"] = nivel_fim
    return sessoes, proximo_sessao_id

def gerar_arquivo_sessoes(caminho_jogadores):
    pasta = BASE_DIR / "output"
    pasta.mkdir(exist_ok=True)
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / f"sessoes_{momento}.csv"
    colunas = [
        "sessao_id",
        "player_id",
        "data_inicio_sessao",
        "data_fim_sessao",
        "duracao_minutos",
        "plataforma",
        "genero_jogo",
        "nivel_inicio",
        "nivel_fim"
    ]
    with open(
        caminho_jogadores,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo_jogadores:
        leitor = csv.DictReader(arquivo_jogadores)
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo_sessoes:
            escritor = csv.DictWriter(arquivo_sessoes, fieldnames=colunas)
            escritor.writeheader()
            proximo_sessao_id = 1
            for jogador in leitor:
                (sessoes, proximo_sessao_id) = gerar_sessoes_jogador(
                    jogador,
                    proximo_sessao_id
                )
                for sessao in sessoes:
                    escritor.writerow(sessao)
    return caminho