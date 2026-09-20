from datetime import date, timedelta
import random
import calendar
import unicodedata

HOJE = date.today()

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