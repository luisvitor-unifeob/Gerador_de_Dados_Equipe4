from pathlib import Path
import csv
import random
import copy

# ------------------------------------------------------------------
# Núcleo (motor) da sujeira. Módulo responsável por injetar problemas de qualidade CONTROLADOS
# nos arquivos CSV já gerados pelo simulador: dados duplicados,
# dados ausentes e dados despadronizados.
#
# Ele NÃO altera os arquivos originais (limpos). Lê cada CSV de
# output/ e grava uma cópia "suja" em output/sujos/.
# ------------------------------------------------------------------

#Pasta principal do gerador
BASE_DIR = Path(__file__).resolve().parent.parent

#Percentuais padrão (podem ser sobrescritos a cada chamada)
PERCENTUAL_DUPLICADOS = 0.02       #2% das linhas viram duplicatas
PERCENTUAL_AUSENTES = 0.05         #5% das linhas perdem o valor de uma coluna elegível
PERCENTUAL_DESPADRONIZADOS = 0.08  #8% das linhas recebem um campo fora do padrão

def ler_csv(caminho):
    with open(caminho, "r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames
        linhas = [linha for linha in leitor]
    return colunas, linhas

def escrever_csv(caminho, colunas, linhas):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow(linha)

def inserir_duplicados(linhas, percentual):
    #Duplica linhas inteiras (com o mesmo ID), simulando um evento
    #registrado duas vezes por falha de sistema ou reenvio de requisição
    quantidade = int(len(linhas) * percentual)
    if quantidade == 0:
        return linhas

    linhas_para_duplicar = random.sample(linhas, quantidade)
    resultado = linhas + [copy.deepcopy(linha) for linha in linhas_para_duplicar]
    random.shuffle(resultado)
    return resultado

def inserir_ausentes(linhas, colunas_elegiveis, percentual):
    #Apaga o valor de uma célula. Nunca deve ser usado em colunas de ID,
    #para não quebrar o relacionamento entre os arquivos
    if not colunas_elegiveis:
        return linhas

    for linha in linhas:
        if random.random() < percentual:
            coluna = random.choice(colunas_elegiveis)
            linha[coluna] = ""
    return linhas

def despadronizar_texto(valor):
    opcao = random.choice(["maiusculo", "minusculo", "espacos"])
    if opcao == "maiusculo":
        return valor.upper()
    if opcao == "minusculo":
        return valor.lower()
    return f"  {valor}  "

def despadronizar_data(valor):
    #Recebe AAAA-MM-DD (com ou sem hora) e devolve em outro formato
    partes = valor.split(" ")
    data = partes[0]
    hora = partes[1] if len(partes) > 1 else None

    try:
        ano, mes, dia = data.split("-")
    except ValueError:
        return valor

    formato = random.choice(["dd/mm/aaaa", "dd-mm-aaaa", "mm/dd/aaaa"])
    if formato == "dd/mm/aaaa":
        nova_data = f"{dia}/{mes}/{ano}"
    elif formato == "dd-mm-aaaa":
        nova_data = f"{dia}-{mes}-{ano}"
    else:
        nova_data = f"{mes}/{dia}/{ano}"

    if hora:
        return f"{nova_data} {hora}"
    return nova_data

def despadronizar_numero(valor):
    #Troca o ponto decimal por vírgula
    try:
        float(valor)
    except ValueError:
        return valor
    return valor.replace(".", ",")

def inserir_despadronizados(linhas, colunas_texto, colunas_data, colunas_numericas, percentual):
    colunas_texto = colunas_texto or []
    colunas_data = colunas_data or []
    colunas_numericas = colunas_numericas or []
    todas_colunas = colunas_texto + colunas_data + colunas_numericas

    if not todas_colunas:
        return linhas

    for linha in linhas:
        if random.random() >= percentual:
            continue

        coluna = random.choice(todas_colunas)
        valor = linha.get(coluna, "")
        if not valor:
            continue

        if coluna in colunas_texto:
            linha[coluna] = despadronizar_texto(valor)
        elif coluna in colunas_data:
            linha[coluna] = despadronizar_data(valor)
        else:
            linha[coluna] = despadronizar_numero(valor)
    return linhas

def aplicar_sujeira(
    caminho_csv,
    colunas_ausentes=None,
    colunas_texto=None,
    colunas_data=None,
    colunas_numericas=None,
    percentual_duplicados=PERCENTUAL_DUPLICADOS,
    percentual_ausentes=PERCENTUAL_AUSENTES,
    percentual_despadronizados=PERCENTUAL_DESPADRONIZADOS
):
    #Lê o CSV limpo, aplica os problemas e grava a cópia em output/sujos/
    #Retorna o caminho do arquivo sujo
    pasta = BASE_DIR / "output" / "sujos"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho_saida = pasta / Path(caminho_csv).name

    colunas, linhas = ler_csv(caminho_csv)

    #Ignora colunas configuradas que não existam no arquivo
    colunas_ausentes = [c for c in (colunas_ausentes or []) if c in colunas]
    colunas_texto = [c for c in (colunas_texto or []) if c in colunas]
    colunas_data = [c for c in (colunas_data or []) if c in colunas]
    colunas_numericas = [c for c in (colunas_numericas or []) if c in colunas]
    linhas = inserir_ausentes(linhas, colunas_ausentes, percentual_ausentes)
    linhas = inserir_despadronizados(
        linhas, colunas_texto, colunas_data, colunas_numericas, percentual_despadronizados
    )
    linhas = inserir_duplicados(linhas, percentual_duplicados)

    escrever_csv(caminho_saida, colunas, linhas)
    return caminho_saida