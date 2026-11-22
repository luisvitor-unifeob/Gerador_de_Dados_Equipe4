from pathlib import Path
from datetime import datetime, timedelta, time
import csv
import random
from src.regras import (
    GENEROS_JOGO,
    PLATAFORMAS,
    escolher_preferencias_jogador,
    calcular_ganho_nivel
)
from src.estado import (
    obter_proximo_id,
    atualizar_ultimo_id,
    obter_lote_atual,
    obter_janela_temporal,
    carregar_pool,
    salvar_pool,
    selecionar_jogadores_recorrentes
)

#Pasta principal do gerador
BASE_DIR = Path(__file__).resolve().parent.parent

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

PESOS_HORARIOS = [
    3, 2, 1, 1, 1, 1, 2, 3, 5, 6, 7, 8,
    9, 8, 9, 10, 11, 13, 16, 18, 17, 14, 9, 5
]

def calcular_quantidade_sessoes(data_criacao, idade, perfil_atividade=None):
    hoje = datetime.now().date()
    dias_conta = max(1, (hoje - data_criacao).days)
    base = dias_conta ** 0.5

    perfil = perfil_atividade or random.choices(
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
    minimo, maximo = fatores.get(perfil, (0.65, 1.00))
    fator = random.uniform(minimo, maximo)

    if idade <= 24:
        fator *= 1.15
    elif idade >= 45:
        fator *= 0.80
    elif idade >= 35:
        fator *= 0.90

    quantidade = int(round(base * fator * random.uniform(0.85, 1.15)))
    return max(1, quantidade)

def sortear_quantidade_sessoes_quinzena(perfil, idade):
    faixas = {
        "casual": (1, 2),
        "regular": (2, 5),
        "ativo": (5, 9),
        "intenso": (9, 17)
    }
    minimo, maximo = faixas.get(perfil, (2, 5))
    quantidade = random.randint(minimo, maximo)
    if idade <= 24 and random.random() < 0.30:
        quantidade += 1
    elif idade >= 45 and quantidade > 1 and random.random() < 0.35:
        quantidade -= 1
    return max(1, quantidade)

def sortear_sessoes_novos_jogadores(perfil, dias_restantes):
    taxas = {
        "casual": 0.15,
        "regular": 0.30,
        "ativo": 0.55,
        "intenso": 0.90
    }
    taxa = taxas.get(perfil, 0.30)
    qtd = max(1, int(round(dias_restantes * taxa * random.uniform(0.8, 1.2))))
    return min(qtd, dias_restantes * 2)

def sortear_horario(data_base):
    hora = random.choices(range(24), weights=PESOS_HORARIOS, k=1)[0]
    minuto = random.randint(0, 59)
    segundo = random.randint(0, 59)
    return datetime.combine(data_base, time(hora, minuto, segundo))

def gerar_datas_inicio(data_criacao, quantidade, data_limite=None):
    fim = data_limite or datetime.now().date()
    total_dias = max(1, (fim - data_criacao).days)
    datas = []

    for _ in range(quantidade):
        proporcao = random.betavariate(1.4, 1.0)
        deslocamento = int(total_dias * proporcao)
        dia_sessao = data_criacao + timedelta(days=deslocamento)
        datas.append(sortear_horario(dia_sessao))

    datas.sort()
    return datas

def gerar_datas_sessao_janela(data_inicio_janela, data_fim_janela, quantidade):
    total_dias = max(1, (data_fim_janela - data_inicio_janela).days)
    datas = []
    for _ in range(quantidade):
        deslocamento = random.randint(0, total_dias - 1)
        dia = data_inicio_janela + timedelta(days=deslocamento)
        datas.append(sortear_horario(dia))
    datas.sort()
    return datas

def escolher_genero(generos_preferidos):
    if random.random() < 0.95:
        return random.choice(generos_preferidos)
    outros_generos = [genero for genero in GENEROS_JOGO if genero not in generos_preferidos]
    if outros_generos:
        return random.choice(outros_generos)
    return random.choice(generos_preferidos)

def escolher_plataforma(genero_jogo, plataformas_preferidas):
    plataformas_disponiveis = PLATAFORMAS[genero_jogo]
    if genero_jogo == "MOBA" and random.random() < 0.20:
        return "Mobile"
    compativeis = [
        plataforma for plataforma in plataformas_preferidas
        if plataforma in plataformas_disponiveis
    ]
    if compativeis:
        return random.choice(compativeis)
    return random.choice(plataformas_disponiveis)

def calcular_duracao_sessao(genero_jogo):
    tempo_minimo, tempo_maximo = TEMPO_SESSAO[genero_jogo]
    fator = random.betavariate(1.8, 3.5)
    duracao = tempo_minimo + int(fator * (tempo_maximo - tempo_minimo))
    return max(tempo_minimo, min(tempo_maximo, duracao))

def calcular_niveis(indice, quantidade_sessoes, nivel_atual):
    if nivel_atual <= 1:
        return 1, 1
    progresso_inicio = (indice / quantidade_sessoes) ** 1.8
    progresso_fim = ((indice + 1) / quantidade_sessoes) ** 1.8
    nivel_inicio = 1 + int((nivel_atual - 1) * progresso_inicio)
    nivel_fim = 1 + int((nivel_atual - 1) * progresso_fim)
    nivel_inicio = min(nivel_inicio, nivel_atual)
    nivel_fim = min(nivel_fim, nivel_atual)
    return nivel_inicio, nivel_fim

def gerar_sessoes_jogador_historico(jogador, persona, data_fim_janela):
    player_id = int(jogador["player_id"])
    idade = int(jogador["idade"])
    nivel_alvo = int(jogador["nivel_jogador"])
    data_criacao = datetime.strptime(jogador["data_criacao_conta"], "%Y-%m-%d").date()

    perfil = persona.get("perfil_atividade", "regular") if persona else "regular"
    generos = persona.get("generos_preferidos") if persona else None
    plataformas = persona.get("plataformas_preferidas") if persona else None

    if not generos or not plataformas:
        generos, plataformas = escolher_preferencias_jogador()

    quantidade_sessoes = calcular_quantidade_sessoes(data_criacao, idade, perfil)
    datas_inicio = gerar_datas_inicio(data_criacao, quantidade_sessoes, data_fim_janela)
    agora = datetime.combine(data_fim_janela, time(23, 59, 59))
    sessoes = []
    ultima_data_fim = None

    for data_inicio in datas_inicio:
        if ultima_data_fim is not None and data_inicio <= ultima_data_fim:
            intervalo = random.randint(30, 180)
            data_inicio = ultima_data_fim + timedelta(minutes=intervalo)
        if data_inicio >= agora:
            break
        genero = escolher_genero(generos)
        plataforma = escolher_plataforma(genero, plataformas)
        duracao = calcular_duracao_sessao(genero)
        minutos_disponiveis = int((agora - data_inicio).total_seconds() // 60)
        if minutos_disponiveis < 1:
            break
        duracao = min(duracao, minutos_disponiveis)
        data_fim = data_inicio + timedelta(minutes=duracao)

        sessoes.append({
            "player_id": player_id,
            "data_inicio_sessao": data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "data_fim_sessao": data_fim.strftime("%Y-%m-%d %H:%M:%S"),
            "duracao_minutos": duracao,
            "plataforma": plataforma,
            "genero_jogo": genero
        })
        ultima_data_fim = data_fim

    qtd_real = len(sessoes)
    for idx, s in enumerate(sessoes):
        n_ini, n_fim = calcular_niveis(idx, qtd_real, nivel_alvo)
        s["nivel_inicio"] = n_ini
        s["nivel_fim"] = n_fim

    if persona:
        persona["nivel_atual"] = nivel_alvo
        persona["ultimo_lote_ativo"] = 1

    return sessoes

def gerar_sessoes_jogador_recorrente(jogador, data_inicio_janela, data_fim_janela, numero_lote):
    player_id = int(jogador["player_id"])
    idade = int(jogador.get("idade", 25))
    nivel_inicio = int(jogador.get("nivel_atual", 1))
    perfil = jogador.get("perfil_atividade", "regular")
    generos = jogador.get("generos_preferidos", ["Ação"])
    plataformas = jogador.get("plataformas_preferidas", ["PC"])

    quantidade_sessoes = sortear_quantidade_sessoes_quinzena(perfil, idade)
    datas_inicio = gerar_datas_sessao_janela(data_inicio_janela, data_fim_janela, quantidade_sessoes)
    agora = datetime.combine(data_fim_janela, time(23, 59, 59))

    sessoes_brutas = []
    ultima_data_fim = None

    for data_inicio in datas_inicio:
        if ultima_data_fim is not None and data_inicio <= ultima_data_fim:
            intervalo = random.randint(30, 180)
            data_inicio = ultima_data_fim + timedelta(minutes=intervalo)
        if data_inicio >= agora:
            break
        genero = escolher_genero(generos)
        plataforma = escolher_plataforma(genero, plataformas)
        duracao = calcular_duracao_sessao(genero)
        minutos_disponiveis = int((agora - data_inicio).total_seconds() // 60)
        if minutos_disponiveis < 1:
            break
        duracao = min(duracao, minutos_disponiveis)
        data_fim = data_inicio + timedelta(minutes=duracao)

        sessoes_brutas.append({
            "player_id": player_id,
            "data_inicio_sessao": data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "data_fim_sessao": data_fim.strftime("%Y-%m-%d %H:%M:%S"),
            "duracao_minutos": duracao,
            "plataforma": plataforma,
            "genero_jogo": genero
        })
        ultima_data_fim = data_fim

    qtd_real = len(sessoes_brutas)
    ganho = calcular_ganho_nivel(nivel_inicio, qtd_real, perfil)
    nivel_fim_total = min(100, nivel_inicio + ganho)

    for idx, s in enumerate(sessoes_brutas):
        if qtd_real <= 1 or nivel_inicio == nivel_fim_total:
            s["nivel_inicio"] = nivel_inicio
            s["nivel_fim"] = nivel_fim_total
        else:
            n_ini = nivel_inicio + int((nivel_fim_total - nivel_inicio) * (idx / qtd_real))
            n_fim = nivel_inicio + int((nivel_fim_total - nivel_inicio) * ((idx + 1) / qtd_real))
            s["nivel_inicio"] = min(100, n_ini)
            s["nivel_fim"] = min(100, n_fim)

    jogador["nivel_atual"] = nivel_fim_total
    jogador["ultimo_lote_ativo"] = numero_lote
    return sessoes_brutas

def gerar_sessoes_jogador_novo(jogador_csv, persona, data_fim_janela, numero_lote):
    player_id = int(jogador_csv["player_id"])
    data_criacao = datetime.strptime(jogador_csv["data_criacao_conta"], "%Y-%m-%d").date()
    nivel_alvo = int(jogador_csv["nivel_jogador"])

    perfil = persona.get("perfil_atividade", "regular") if persona else "regular"
    generos = persona.get("generos_preferidos", ["Ação"]) if persona else ["Ação"]
    plataformas = persona.get("plataformas_preferidas", ["PC"]) if persona else ["PC"]

    dias_restantes = max(1, (data_fim_janela - data_criacao).days)
    quantidade_sessoes = sortear_sessoes_novos_jogadores(perfil, dias_restantes)
    datas_inicio = gerar_datas_sessao_janela(data_criacao, data_fim_janela, quantidade_sessoes)
    agora = datetime.combine(data_fim_janela, time(23, 59, 59))

    sessoes_brutas = []
    ultima_data_fim = None

    for data_inicio in datas_inicio:
        if ultima_data_fim is not None and data_inicio <= ultima_data_fim:
            intervalo = random.randint(30, 180)
            data_inicio = ultima_data_fim + timedelta(minutes=intervalo)
        if data_inicio >= agora:
            break
        genero = escolher_genero(generos)
        plataforma = escolher_plataforma(genero, plataformas)
        duracao = calcular_duracao_sessao(genero)
        minutos_disponiveis = int((agora - data_inicio).total_seconds() // 60)
        if minutos_disponiveis < 1:
            break
        duracao = min(duracao, minutos_disponiveis)
        data_fim = data_inicio + timedelta(minutes=duracao)

        sessoes_brutas.append({
            "player_id": player_id,
            "data_inicio_sessao": data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "data_fim_sessao": data_fim.strftime("%Y-%m-%d %H:%M:%S"),
            "duracao_minutos": duracao,
            "plataforma": plataforma,
            "genero_jogo": genero
        })
        ultima_data_fim = data_fim

    qtd_real = len(sessoes_brutas)
    for idx, s in enumerate(sessoes_brutas):
        n_ini, n_fim = calcular_niveis(idx, qtd_real, nivel_alvo)
        s["nivel_inicio"] = n_ini
        s["nivel_fim"] = n_fim

    if persona:
        persona["nivel_atual"] = nivel_alvo
        persona["ultimo_lote_ativo"] = numero_lote

    return sessoes_brutas

def gerar_sessoes_jogador(jogador, proximo_sessao_id, data_limite=None):
    sessoes = gerar_sessoes_jogador_historico(jogador, None, data_limite or datetime.now().date())
    for s in sessoes:
        s["sessao_id"] = proximo_sessao_id
        proximo_sessao_id += 1
    return sessoes, proximo_sessao_id

def gerar_arquivo_sessoes(id_lote, caminho_jogadores):
    pasta = BASE_DIR / "output/.tmp"
    pasta.mkdir(exist_ok=True)
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / f"{id_lote}-sessoes_{momento}.csv"
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

    numero_lote = obter_lote_atual()
    data_inicio_janela, data_fim_janela = obter_janela_temporal(numero_lote)
    pool = carregar_pool()

    novos_jogadores = []
    ids_novos = set()
    with open(caminho_jogadores, "r", newline="", encoding="utf-8-sig") as arquivo_jogadores:
        leitor = csv.DictReader(arquivo_jogadores)
        for linha in leitor:
            novos_jogadores.append(linha)
            ids_novos.add(int(linha["player_id"]))

    todas_sessoes = []
    if numero_lote <= 1:
        for jogador in novos_jogadores:
            pid = int(jogador["player_id"])
            persona = pool.get(str(pid))
            sessoes = gerar_sessoes_jogador_historico(jogador, persona, data_fim_janela)
            todas_sessoes.extend(sessoes)
    else:
        recorrentes = selecionar_jogadores_recorrentes(pool, ids_novos, numero_lote)
        for j in recorrentes:
            sessoes = gerar_sessoes_jogador_recorrente(j, data_inicio_janela, data_fim_janela, numero_lote)
            todas_sessoes.extend(sessoes)
        for j_csv in novos_jogadores:
            pid = int(j_csv["player_id"])
            persona = pool.get(str(pid))
            sessoes = gerar_sessoes_jogador_novo(j_csv, persona, data_fim_janela, numero_lote)
            todas_sessoes.extend(sessoes)

    todas_sessoes.sort(key=lambda s: s["data_inicio_sessao"])
    proximo_sessao_id = obter_proximo_id("ultimo_sessao_id")

    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo_sessoes:
        escritor = csv.DictWriter(arquivo_sessoes, fieldnames=colunas)
        escritor.writeheader()
        for idx, sessao in enumerate(todas_sessoes):
            sessao["sessao_id"] = proximo_sessao_id + idx
            escritor.writerow(sessao)

    salvar_pool(pool)
    atualizar_ultimo_id("ultimo_sessao_id", proximo_sessao_id + len(todas_sessoes) - 1)
    return caminho
