from faker import Faker
from datetime import date, datetime
from pathlib import Path
from urllib.request import urlretrieve
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
    criar_username
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

#Guarda somente cidades válidas
CIDADES = []
for cidade in gc.get_cities().values():
    codigo_pais = cidade.get("countrycode")
    codigo_estado = cidade.get("admin1code")

    if codigo_pais not in PAISES:
        continue
    if not codigo_estado:
        continue

    chave_estado = f"{codigo_pais}.{codigo_estado}"
    if chave_estado in ESTADOS:
        CIDADES.append(cidade)

def gerar_localizacao():
    cidade = random.choice(CIDADES)
    codigo_pais = cidade["countrycode"]
    codigo_estado = cidade["admin1code"]
    chave_estado = f"{codigo_pais}.{codigo_estado}"
    nome_estado = ESTADOS[chave_estado]
    sigla = SIGLAS_ESTADOS.get((codigo_pais, normalizar(nome_estado)))

    if sigla:
        estado = sigla
    else:
        estado = nome_estado

    return {
        "cidade": cidade["name"],
        "estado": estado,
        "pais": PAISES[codigo_pais]["nome"],
        "codigo_pais": codigo_pais
    }

def gerar_jogador(player_id):
    local = gerar_localizacao()
    fake = FAKERS[local["codigo_pais"]]
    genero = random.choice(["Masculino", "Feminino"])

    if genero == "Masculino":
        nome = fake.first_name_male() + " " + fake.last_name()
    else:
        nome = fake.first_name_female() + " " + fake.last_name()

    username = criar_username(nome) + str(player_id)
    idade = random.randint(16, 55)
    nascimento = gerar_data_nascimento(idade)

    #A conta só pode ser criada depois que o jogador atingir a idade mínima
    idade_minima = adicionar_anos(nascimento, 13)
    inicio_sistema = date(2010, 1, 1)
    data_minima = max(idade_minima, inicio_sistema)
    data_criacao = data_aleatoria(data_minima, HOJE)

    #O nível representa o estado atual do jogador, e a progressão é detalhada nas sessões
    nivel = random.randint(1, 100)

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
def gerar_arquivo_jogadores(quantidade):
    pasta = BASE_DIR / "output"
    pasta.mkdir(exist_ok=True)

    #Inclui microssegundos para evitar nomes de arquivos repetidos
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / f"jogadores_{quantidade}_{momento}.csv"
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

    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()

        for player_id in range(1, quantidade + 1):
            jogador = gerar_jogador(player_id)
            escritor.writerow(jogador)
    return caminho
