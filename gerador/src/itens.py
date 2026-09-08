from pathlib import Path
from datetime import datetime

import csv
import random


# Pasta principal do gerador
BASE_DIR = Path(__file__).resolve().parent.parent


CATEGORIAS = {
    "Skin": [
        "Skin Dragão",
        "Skin Tempestade",
        "Skin Neon",
        "Skin Sombria",
        "Skin Vulcânica",
        "Skin Glacial"
    ],

    "Passe de batalha": [
        "Passe de Batalha Bronze",
        "Passe de Batalha Prata",
        "Passe de Batalha Ouro"
    ],

    "Moeda virtual": [
        "100 Moedas",
        "500 Moedas",
        "1000 Moedas",
        "2500 Moedas"
    ],

    "Personagem": [
        "Personagem Guerreiro",
        "Personagem Mago",
        "Personagem Caçador",
        "Personagem Assassino"
    ],

    "Cosmético": [
        "Roupa Especial",
        "Capacete Especial",
        "Efeito Visual",
        "Pintura Especial"
    ],

    "DLC": [
        "Expansão Norte",
        "Expansão Sombria",
        "Expansão Final"
    ],

    "Boost": [
        "Boost de XP",
        "Boost de Moedas",
        "Boost de Progressão"
    ],

    "Pacote": [
        "Pacote Inicial",
        "Pacote Premium",
        "Pacote Lendário"
    ],

    "Emote": [
        "Emote Dança",
        "Emote Vitória",
        "Emote Provocação"
    ],

    "Acessório": [
        "Mochila Especial",
        "Pingente",
        "Bandeira",
        "Insígnia"
    ]
}


RARIDADES = [
    "Comum",
    "Incomum",
    "Rara",
    "Épica",
    "Lendária"
]


PRECOS_POR_RARIDADE = {
    "Comum":    [4.90, 9.90],
    "Incomum":  [9.90, 14.90, 19.90],
    "Rara":     [19.90, 24.90, 29.90],
    "Épica":    [29.90, 39.90, 49.90],
    "Lendária": [49.90, 59.90, 79.90]
}


def escolher_raridade():
    """
    Raridades comuns aparecem com
    mais frequência que raridades altas.
    """
    return random.choices(RARIDADES, weights=[35, 25, 20, 15, 5], k=1)[0]


def gerar_itens():
    """
    Cria o catálogo de itens disponíveis
    para compra.
    """

    itens = []
    item_id = 1
    for categoria, nomes in CATEGORIAS.items():
        for nome_item in nomes:
            raridade = escolher_raridade()
            preco_base = random.choice(PRECOS_POR_RARIDADE[raridade])
            item = {
                "item_id": item_id,
                "nome_item": nome_item,
                "categoria_item": categoria,
                "raridade": raridade,
                "preco_base": preco_base
            }
            itens.append(item)
            item_id += 1
    return itens


def gerar_arquivo_itens():
    """
    Gera o CSV contendo o catálogo
    de itens disponíveis.
    """

    pasta = BASE_DIR / "output"
    pasta.mkdir(exist_ok=True)

    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = pasta / (f"itens_{momento}.csv")
    colunas = [
        "item_id",
        "nome_item",
        "categoria_item",
        "raridade",
        "preco_base"
    ]
    itens = gerar_itens()

    with open(
        caminho,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=colunas
        )
        escritor.writeheader()
        for item in itens:
            escritor.writerow(item)

    print()
    print(len(itens), "itens gerados.")

    return caminho
