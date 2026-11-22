from faker import Faker
from datetime import date, datetime
from pathlib import Path
from urllib.request import urlretrieve
import math
import random
import csv
import unicodedata
import geonamescache
import pycountry
from src.regras import (
    HOJE,
    gerar_data_nascimento,
    adicionar_anos,
    data_aleatoria,
    criar_username,
    gerar_idade_realista,
    gerar_nivel_realista,
    data_criacao_com_crescimento,
    criar_persona_jogador
)
from src.estado import (
    avancar_lote,
    obter_proximo_id,
    atualizar_ultimo_id,
    obter_janela_temporal,
    adicionar_jogadores_pool
)

#Pasta principal do gerador
BASE_DIR = Path(__file__).resolve().parent.parent

#Países utilizados na geração dos jogadores
PAISES = {
    "BR": {"nome": "Brasil", "locale": "pt_BR"},
    "US": {"nome": "Estados Unidos", "locale": "en_US"},
    "PT": {"nome": "Portugal", "locale": "pt_PT"},
    "ES": {"nome": "Espanha", "locale": "es_ES"},
    "FR": {"nome": "França", "locale": "fr_FR"},
    "DE": {"nome": "Alemanha", "locale": "de_DE"},
    "IT": {"nome": "Itália", "locale": "it_IT"},
    "GB": {"nome": "Reino Unido", "locale": "en_GB"},
    "CA": {"nome": "Canadá", "locale": "en_CA"},
    "AU": {"nome": "Austrália", "locale": "en_AU"},
    "MX": {"nome": "México", "locale": "es_MX"},
    "AR": {"nome": "Argentina", "locale": "es_AR"}
}

PESOS_PAISES = {
    "BR": 35, "US": 20, "MX": 8, "AR": 7, "GB": 5, "DE": 5,
    "FR": 4, "ES": 4, "CA": 4, "PT": 3, "IT": 3, "AU": 2
}

#Faker específico para cada país
FAKERS = {codigo: Faker(dados["locale"]) for codigo, dados in PAISES.items()}

#Base geográfica
gc = geonamescache.GeonamesCache(min_city_population=1000)
GC_PASTA_BASE = BASE_DIR / "data" / "base_geografica"
ARQUIVO_ESTADOS = GC_PASTA_BASE / "codigos_divisoes_administrativas.txt"
URL_ESTADOS = (
    "https://download.geonames.org/export/dump/"
    "admin1CodesASCII.txt"
)

def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(letra for letra in texto if not unicodedata.combining(letra)).lower()

def carregar_estados():
    GC_PASTA_BASE.mkdir(parents=True, exist_ok=True)

    #Baixa a base somente se o arquivo ainda não existir
    if not ARQUIVO_ESTADOS.exists():
        urlretrieve(URL_ESTADOS, ARQUIVO_ESTADOS)

    estados = {}
    with open(ARQUIVO_ESTADOS, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            partes = linha.strip().split("\t")
            if len(partes) >= 2:
                estados[partes[0]] = partes[1]
    return estados

ESTADOS = carregar_estados()

#Relaciona estados com suas siglas
SIGLAS_ESTADOS = {}
for estado in pycountry.subdivisions:
    if estado.country_code in PAISES:
        nome = normalizar(estado.name)
        sigla = estado.code.split("-", 1)[-1]
        SIGLAS_ESTADOS[(estado.country_code, nome)] = sigla

#Guarda somente cidades válidas agrupadas por país
CIDADES_POR_PAIS = {codigo: [] for codigo in PAISES}
PESOS_CIDADES_POR_PAIS = {codigo: [] for codigo in PAISES}

for cidade in gc.get_cities().values():
    codigo_pais = cidade.get("countrycode")
    codigo_estado = cidade.get("admin1code")

    if codigo_pais not in PAISES or not codigo_estado:
        continue

    chave_estado = f"{codigo_pais}.{codigo_estado}"
    if chave_estado in ESTADOS:
        populacao = max(1000, cidade.get("population", 1000))
        CIDADES_POR_PAIS[codigo_pais].append(cidade)
        # Raiz quadrada suaviza a disparidade entre capitais e cidades médias
        PESOS_CIDADES_POR_PAIS[codigo_pais].append(math.isqrt(populacao))

def gerar_localizacao():
    cod_pais = random.choices(
        list(PESOS_PAISES.keys()),
        weights=list(PESOS_PAISES.values()),
        k=1
    )[0]

    cidade = random.choices(
        CIDADES_POR_PAIS[cod_pais],
        weights=PESOS_CIDADES_POR_PAIS[cod_pais],
        k=1
    )[0]

    codigo_estado = cidade["admin1code"]
    chave_estado = f"{cod_pais}.{codigo_estado}"
    nome_estado = ESTADOS[chave_estado]
    sigla = SIGLAS_ESTADOS.get((cod_pais, normalizar(nome_estado)))
    estado = sigla if sigla else nome_estado

    return {
        "cidade": cidade["name"],
        "estado": estado,
        "pais": PAISES[cod_pais]["nome"],
        "codigo_pais": cod_pais
    }

def gerar_jogador(player_id, data_inicio_janela=None, data_fim_janela=None):
    local = gerar_localizacao()
    fake = FAKERS[local["codigo_pais"]]
    genero = "Masculino" if random.random() < 0.52 else "Feminino"

    if genero == "Masculino":
        nome = fake.first_name_male() + " " + fake.last_name()
    else:
        nome = fake.first_name_female() + " " + fake.last_name()

    username = criar_username(nome) + str(player_id)
    idade = gerar_idade_realista()
    nascimento = gerar_data_nascimento(idade)

    fim_janela = data_fim_janela or HOJE
    inicio_janela = data_inicio_janela or date(2010, 1, 1)

    idade_minima = adicionar_anos(nascimento, 13)
    data_minima = max(idade_minima, inicio_janela)
    if data_minima > fim_janela:
        data_minima = fim_janela

    data_criacao = data_criacao_com_crescimento(data_minima, fim_janela)
    dias_conta = max(1, (fim_janela - data_criacao).days)
    nivel = gerar_nivel_realista(dias_conta)

    return {
        "player_id": player_id,
        "nome": nome,
        "username": username,
        "idade": idade,
        "data_nascimento": nascimento.isoformat(),
        "genero": genero,
        "cidade": local["cidade"],
        "estado": local["estado"],
        "pais": local["pais"],
        "nivel_jogador": nivel,
        "data_criacao_conta": data_criacao.isoformat()
    }

#Salva os jogadores em um CSV
def gerar_arquivo_jogadores(id_lote, quantidade):
    pasta = BASE_DIR / "output/.tmp"
    pasta.mkdir(exist_ok=True)

    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / f"{id_lote}-jogadores_{quantidade}_{momento}.csv"
    colunas = [
        "player_id",
        "nome",
        "username",
        "idade",
        "data_nascimento",
        "genero",
        "cidade",
        "estado",
        "pais",
        "nivel_jogador",
        "data_criacao_conta"
    ]

    numero_lote = avancar_lote()
    data_inicio_janela, data_fim_janela = obter_janela_temporal(numero_lote)
    primeiro_id = obter_proximo_id("ultimo_player_id")

    novas_personas = []
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()

        for player_id in range(primeiro_id, primeiro_id + quantidade):
            jogador = gerar_jogador(player_id, data_inicio_janela, data_fim_janela)
            escritor.writerow(jogador)
            persona = criar_persona_jogador(
                player_id=player_id,
                idade=jogador["idade"],
                nivel=jogador["nivel_jogador"],
                data_criacao=jogador["data_criacao_conta"],
                lote_criacao=numero_lote
            )
            novas_personas.append(persona)

    adicionar_jogadores_pool(novas_personas)
    atualizar_ultimo_id("ultimo_player_id", primeiro_id + quantidade - 1)
    return caminho
