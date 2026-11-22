from pathlib import Path
from datetime import date, timedelta
import json
import random

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_ESTADO = BASE_DIR / "data" / ".estado_gerador.json"
ARQUIVO_POOL = BASE_DIR / "data" / ".pool_jogadores.json"

ESTADO_PADRAO = {
    "lote_atual": 0,
    "ultimo_player_id": 0,
    "ultimo_sessao_id": 0,
    "ultimo_partida_id": 0,
    "ultimo_compra_id": 0,
    "ultimo_item_compra_id": 0
}

PESOS_ATIVIDADE = {
    "intenso": 0.85,
    "ativo": 0.65,
    "regular": 0.40,
    "casual": 0.18
}

def carregar_estado():
    if not ARQUIVO_ESTADO.exists():
        return ESTADO_PADRAO.copy()
    try:
        with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as f:
            return {**ESTADO_PADRAO, **json.load(f)}
    except (json.JSONDecodeError, OSError):
        return ESTADO_PADRAO.copy()

def salvar_estado(estado):
    ARQUIVO_ESTADO.parent.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2)

def obter_proximo_id(chave):
    estado = carregar_estado()
    return estado.get(chave, 0) + 1

def atualizar_ultimo_id(chave, valor):
    estado = carregar_estado()
    estado[chave] = max(estado.get(chave, 0), valor)
    salvar_estado(estado)

def avancar_lote():
    estado = carregar_estado()
    estado["lote_atual"] = estado.get("lote_atual", 0) + 1
    salvar_estado(estado)
    return estado["lote_atual"]

def obter_lote_atual():
    estado = carregar_estado()
    return estado.get("lote_atual", 0)

def obter_janela_temporal(numero_lote):
    hoje = date.today()

    # Lote 1: carga histórica (2022 até fim de 2025)
    if numero_lote <= 1:
        fim_historico = min(hoje, date(2025, 12, 31))
        return date(2020, 1, 1), fim_historico

    # Lotes subsequentes: avanço progressivo de 14 dias a cada lote
    inicio_2026 = date(2026, 1, 1)
    deslocamento = (numero_lote - 2) * 14
    data_inicio = inicio_2026 + timedelta(days=deslocamento)
    data_fim = data_inicio + timedelta(days=14)

    # Clamping para não ultrapassar a data atual
    if data_inicio >= hoje:
        data_fim = hoje
        data_inicio = hoje - timedelta(days=14)
    elif data_fim > hoje:
        data_fim = hoje

    return data_inicio, data_fim

def carregar_pool():
    if not ARQUIVO_POOL.exists():
        return {}
    try:
        with open(ARQUIVO_POOL, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def salvar_pool(pool):
    ARQUIVO_POOL.parent.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_POOL, "w", encoding="utf-8") as f:
        json.dump(pool, f)

def adicionar_jogadores_pool(jogadores_persona):
    pool = carregar_pool()
    for persona in jogadores_persona:
        pool[str(persona["player_id"])] = persona
    salvar_pool(pool)

def obter_jogador_pool(player_id):
    pool = carregar_pool()
    return pool.get(str(player_id))

def atualizar_jogadores_pool(atualizacoes):
    pool = carregar_pool()
    for pid_str, dados in atualizacoes.items():
        if pid_str in pool:
            pool[pid_str].update(dados)
    salvar_pool(pool)

def selecionar_jogadores_recorrentes(pool, ids_excluir, lote_atual):
    ativos = []
    for pid_str, j in pool.items():
        pid = int(pid_str)
        if pid in ids_excluir:
            continue
        perfil = j.get("perfil_atividade", "regular")
        base_prob = PESOS_ATIVIDADE.get(perfil, 0.40)
        ultimo_lote = j.get("ultimo_lote_ativo", lote_atual - 1)
        gaps = lote_atual - ultimo_lote
        if gaps <= 1:
            prob = base_prob
        elif gaps == 2:
            prob = base_prob * 0.55
        elif gaps == 3:
            prob = base_prob * 0.30
        else:
            prob = base_prob * 0.10

        if random.random() < prob:
            ativos.append(j)
    return ativos
