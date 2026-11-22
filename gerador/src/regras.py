from datetime import date, timedelta
import random
import calendar
import unicodedata
import math

HOJE = date.today()

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

def gerar_idade_realista():
    # Beta(2, 5) gera curva com moda em ~23 anos e cauda até 55
    fator = random.betavariate(2.0, 5.0)
    idade = 16 + int(fator * 40)
    return max(16, min(55, idade))

def gerar_nivel_realista(dias_conta):
    # Teto baseado no tempo de conta para evitar nível alto em contas novas
    teto = min(100, max(5, int(math.sqrt(dias_conta) * 3.5)))
    proporcao = random.betavariate(1.0, 3.2)
    nivel = 1 + int(proporcao * teto)
    if random.random() < 0.02 and teto >= 90:
        nivel = 100
    return max(1, min(100, nivel))

def data_criacao_com_crescimento(inicio, fim):
    quantidade_dias = (fim - inicio).days
    if quantidade_dias <= 0:
        return inicio
    # Beta(2.2, 1.0) concentra registros nos anos mais recentes
    proporcao = random.betavariate(2.2, 1.0)
    return inicio + timedelta(days=int(quantidade_dias * proporcao))

def gerar_data_nascimento(idade):
    mes = random.randint(1, 12)
    ano = HOJE.year - idade
    dia = random.randint(1, calendar.monthrange(ano, mes)[1])

    #Faz a data realmente corresponder à idade
    if (mes, dia) > (HOJE.month, HOJE.day):
        ano -= 1
    return date(ano, mes, dia)

def adicionar_anos(data_original, anos):
    try:
        return data_original.replace(year=data_original.year + anos)
    except ValueError:
        #Caso de 29 de fevereiro
        return data_original.replace(year=data_original.year + anos, month=2, day=28)

def data_aleatoria(inicio, fim):
    quantidade_dias = (fim - inicio).days
    return inicio + timedelta(days=random.randint(0, quantidade_dias))

def criar_username(nome):
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return nome.lower().replace(" ", ".")

def escolher_preferencias_jogador():
    quantidade_generos = random.choice([1, 2, 2, 3])
    generos_preferidos = random.sample(GENEROS_JOGO, quantidade_generos)
    quantidade_plataformas = random.choice([1, 1, 1, 2])
    plataformas_preferidas = random.sample(
        ["PC", "PlayStation", "Xbox"],
        quantidade_plataformas
    )
    return generos_preferidos, plataformas_preferidas

def escolher_perfil_compra(nivel=1):
    fator_nivel = min(3.0, 1.0 + (nivel / 40.0))
    peso_pagante = 6.0 * fator_nivel
    peso_nao_pagante = max(70.0, 100.0 - peso_pagante)
    return random.choices(
        ["nao_pagante", "minnow", "dolphin", "whale"],
        weights=[peso_nao_pagante, peso_pagante * 0.70, peso_pagante * 0.23, peso_pagante * 0.07],
        k=1
    )[0]

def criar_persona_jogador(player_id, idade, nivel, data_criacao, lote_criacao=1):
    generos, plataformas = escolher_preferencias_jogador()
    data_str = data_criacao.isoformat() if isinstance(data_criacao, date) else str(data_criacao)
    return {
        "player_id": player_id,
        "idade": idade,
        "data_criacao_conta": data_str,
        "nivel_atual": nivel,
        "perfil_atividade": random.choices(["casual", "regular", "ativo", "intenso"], weights=[35, 40, 20, 5], k=1)[0],
        "perfil_compra": escolher_perfil_compra(nivel),
        "skill": round(random.gauss(0.0, 1.0), 3),
        "generos_preferidos": generos,
        "plataformas_preferidas": plataformas,
        "ultimo_lote_ativo": lote_criacao,
        "lote_criacao": lote_criacao
    }

def calcular_ganho_nivel(nivel_atual, quantidade_sessoes, perfil_atividade):
    fator_perfil = {"intenso": 1.4, "ativo": 1.1, "regular": 0.8, "casual": 0.5}.get(perfil_atividade, 1.0)
    ganho_esperado = (quantidade_sessoes * 0.18 * fator_perfil) / (1.0 + (nivel_atual / 15.0))
    ganho = int(ganho_esperado)
    if random.random() < (ganho_esperado - ganho):
        ganho += 1
    ganho_max = max(1, int(15 / math.sqrt(max(1, nivel_atual))))
    return min(ganho, ganho_max)
