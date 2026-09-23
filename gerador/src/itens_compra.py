from pathlib import Path
from datetime import datetime
import csv
import random

BASE_DIR = Path(__file__).resolve().parent.parent

def carregar_itens(caminho_itens):
    itens = []

    with open(caminho_itens, "r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        for item in leitor:
            itens.append({
                "item_id": int(item["item_id"]),
                "categoria_item": item["categoria_item"],
                "preco_base": float(item["preco_base"])
            })
    return itens

def calcular_quantidade_itens():
    #A maioria das compras possui apenas um item
    return random.choices(
        [1, 2, 3],
        weights=[70, 25, 5],
        k=1
    )[0]

def calcular_quantidade_unidades(categoria):
    #Alguns tipos de produto não fazem sentido em várias unidades
    if categoria in ["DLC", "Passe de batalha", "Personagem"]:
        return 1

    return random.choices(
        [1, 2, 3],
        weights=[85, 12, 3],
        k=1
    )[0]

def calcular_desconto(subtotal):
    #A maior parte dos itens não recebe desconto
    percentual = random.choices(
        [0, 0.05, 0.10, 0.15, 0.20],
        weights=[70, 12, 9, 6, 3],
        k=1
    )[0]
    return round(subtotal * percentual, 2)

def gerar_arquivo_itens_compra(caminho_compras, caminho_itens):
    pasta = BASE_DIR / "output"
    pasta.mkdir(exist_ok=True)
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / f"itens_compra_{momento}.csv"
    colunas = [
        "item_compra_id",
        "compra_id",
        "item_id",
        "quantidade",
        "valor_unitario",
        "desconto",
        "valor_total_item"
    ]

    itens = carregar_itens(caminho_itens)
    proximo_item_compra_id = 1

    with open(caminho_compras, "r", newline="", encoding="utf-8-sig") as arquivo_compras:
        leitor = csv.DictReader(arquivo_compras)
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo_itens_compra:
            escritor = csv.DictWriter(arquivo_itens_compra, fieldnames=colunas)
            escritor.writeheader()

            for compra in leitor:
                compra_id = int(compra["compra_id"])
                quantidade_itens = calcular_quantidade_itens()
                quantidade_itens = min(quantidade_itens, len(itens))

                #Evita repetir o mesmo item dentro da mesma compra
                itens_escolhidos = random.sample(itens, quantidade_itens)

                for item in itens_escolhidos:
                    quantidade = calcular_quantidade_unidades(item["categoria_item"])
                    valor_unitario = round(item["preco_base"], 2)
                    subtotal = round(valor_unitario * quantidade, 2)
                    desconto = calcular_desconto(subtotal)
                    valor_total_item = round(subtotal - desconto, 2)

                    escritor.writerow({
                        "item_compra_id": proximo_item_compra_id,
                        "compra_id": compra_id,
                        "item_id": item["item_id"],
                        "quantidade": quantidade,
                        "valor_unitario": valor_unitario,
                        "desconto": desconto,
                        "valor_total_item": valor_total_item
                    })
                    proximo_item_compra_id += 1
    return caminho