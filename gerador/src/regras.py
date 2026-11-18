from datetime import date, timedelta
import random
import calendar
import unicodedata
import math

HOJE = date.today()

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
