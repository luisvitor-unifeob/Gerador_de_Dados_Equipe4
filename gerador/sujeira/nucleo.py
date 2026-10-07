from pathlib import Path
import csv
import random
import copy
import json

# Pasta principal do gerador
BASE_DIR = Path(__file__).resolve().parent.parent

# Percentuais padrão (podem ser sobrescritos a cada chamada)
PERCENTUAL_DUPLICADOS = 0.02       # 2% das linhas viram duplicatas
PERCENTUAL_AUSENTES = 0.05         # 5% das linhas perdem o valor de uma coluna elegível
PERCENTUAL_DESPADRONIZADOS = 0.08  # 8% das linhas recebem um campo fora do padrão

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
    quantidade = int(len(linhas) * percentual)
    if quantidade == 0:
        return linhas, 0

    linhas_para_duplicar = random.sample(linhas, quantidade)
    resultado = linhas + [copy.deepcopy(linha) for linha in linhas_para_duplicar]
    random.shuffle(resultado)
    return resultado, quantidade

def inserir_ausentes(linhas, colunas_elegiveis, percentual):
    if not colunas_elegiveis:
        return linhas, 0

    total_removidos = 0
    for linha in linhas:
        if random.random() < percentual:
            coluna = random.choice(colunas_elegiveis)
            linha[coluna] = ""
            total_removidos += 1
    return linhas, total_removidos

def despadronizar_texto(valor):
    opcao = random.choice(["maiusculo", "minusculo", "espacos"])
    if opcao == "maiusculo":
        return valor.upper()
    if opcao == "minusculo":
        return valor.lower()
    return f"  {valor}  "

def despadronizar_data(valor):
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
        return linhas, 0

    total_despadronizados = 0
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
        
        total_despadronizados += 1

    return linhas, total_despadronizados

def registrar_relatorio_falhas(pasta_saida, nome_arquivo, total_linhas, duplicados, ausentes, despadronizados):
    caminho_relatorio = pasta_saida / "relatorio_falhas.json"
    
    dados_relatorio = {}
    if caminho_relatorio.exists():
        try:
            with open(caminho_relatorio, "r", encoding="utf-8") as f:
                dados_relatorio = json.load(f)
        except json.JSONDecodeError:
            dados_relatorio = {}

    dados_relatorio[nome_arquivo] = {
        "total_linhas_finais": total_linhas,
        "linhas_duplicadas_inseridas": duplicados,
        "campos_ausentes_inseridos": ausentes,
        "campos_despadronizados_inseridos": despadronizados
    }

    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        json.dump(dados_relatorio, f, indent=4, ensure_ascii=False)

def aplicar_sujeira(
    caminho_csv,
    colunas_ausentes=None,
    colunas_texto=None,
    colunas_data=None,
    colunas_numericas=None,
    percentual_duplicados=PERCENTUAL_DUPLICADOS,
    percentual_ausentes=PERCENTUAL_AUSENTES,
    percentual_despadronizados=PERCENTUAL_DESPADRONIZADOS,
    manter_original=False
):
    caminho_original = Path(caminho_csv)
    pasta = BASE_DIR / "output" / "sujos"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho_saida = pasta / caminho_original.name

    colunas, linhas = ler_csv(caminho_original)

    # Ignora colunas configuradas que não existam no arquivo
    colunas_ausentes = [c for c in (colunas_ausentes or []) if c in colunas]
    colunas_texto = [c for c in (colunas_texto or []) if c in colunas]
    colunas_data = [c for c in (colunas_data or []) if c in colunas]
    colunas_numericas = [c for c in (colunas_numericas or []) if c in colunas]

    linhas, total_ausentes = inserir_ausentes(linhas, colunas_ausentes, percentual_ausentes)
    linhas, total_despadronizados = inserir_despadronizados(
        linhas, colunas_texto, colunas_data, colunas_numericas, percentual_despadronizados
    )
    linhas, total_duplicados = inserir_duplicados(linhas, percentual_duplicados)

    escrever_csv(caminho_saida, colunas, linhas)

    # Documenta as falhas no relatorio_falhas.json
    registrar_relatorio_falhas(
        pasta_saida=pasta,
        nome_arquivo=caminho_original.name,
        total_linhas=len(linhas),
        duplicados=total_duplicados,
        ausentes=total_ausentes,
        despadronizados=total_despadronizados
    )

    # Exclui o arquivo original/limpo para economizar disco
    if not manter_original and caminho_original.exists():
        caminho_original.unlink()

    return caminho_saida