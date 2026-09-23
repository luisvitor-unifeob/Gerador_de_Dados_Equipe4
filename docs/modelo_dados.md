# Modelo dos Dados contidos no CSV

> Os nomes devem ser escritos no CSV EXATAMENTE como estão aqui

## Dados de jogadores

| Nome                | Tipo   | Formato          | Min        | Max  | Exemplo      |
| ------------------- | ------ | ---------------- | ---------- | ---- | ------------ |
| player_id           | int    | -                | 1          | -    | 55           |
| nome                | string | "Nome Sobrenome" | -          | -    | "João Silva" |
| username            | string | -                | -          | -    | "joao"       |
| idade               | int    | -                | 16         | 55   | 17           |
| data_nascimento     | string | yyyy-MM-dd       | 2010-01-01 | HOJE | "2025-05-12" |
| genero              | string | -                | -          | -    | "Masculino"  |
| nivel_jogador       | int    | -                | 1          | 100  | 45           |
| data_criacao_conta  | string | yyyy-MM-dd       | 2010-01-01 | HOJE | "2023-02-21" |

## Dados geográficos

| Nome   | Tipo   | Formato | Exemplo |
| ------ | ------ | ------- | ------- |
| cidade | string | -       | Guapó   |
| estado | string | [Sigla] | GO      |
| pais   | string | -       | Brasil  |

## Dados de jogo

| Nome        | Tipo   | Formato | Exemplo   |
| ----------- | ------ | ------- | --------- |
| plataforma  | string | -       | Xbox      |
| genero_jogo | string | -       | Simulação |

## Dados de sessão

> o número de sessões pode ser substituído por sessões brutas

> inclusive, nós poderíamos ter todo um modelo de dados só para sessões, não?
> com alguns dados do que ocorreu naquela sessão?
> ajudaria a criar uma dimensão no data warehouse

> cada registro representa uma sessão individual realizada por um jogador

> horas_jogadas, numero_sessoes e ultimo_acesso não precisam ser armazenados diretamente, pois podem ser calculados posteriormente através das sessões geradas

| Nome            | Tipo   | Formato             | Min | Max  | Exemplo               |
| --------------- | ------ | ------------------- | --- | ---- | --------------------- |
| sessao_id       | int    | -                   | 1   | -    | 10001                 |
| player_id       | int    | -                   | 1   | -    | 55                    |
| data_inicio     | string | yyyy-MM-dd HH:mm:ss | -   | HOJE | "2026-09-07 14:30:00" |
| data_fim        | string | yyyy-MM-dd HH:mm:ss | -   | HOJE | "2026-09-07 16:05:00" |
| duracao_minutos | int    | -                   | 1   | -    | 95                    |
| plataforma      | string | -                   | -   | -    | PC                    |
| genero_jogo     | string | -                   | -   | -    | FPS                   |
| nivel_inicio    | int    | -                   | 1   | 100  | 44                    |
| nivel_fim       | int    | -                   | 1   | 100  | 45                    |

> numero_sessoes pode ser obtido contando quantos sessao_id existem para determinado player_id

> horas_jogadas pode ser obtido através da soma de duracao_minutos das sessões do jogador

> ultimo_acesso pode ser obtido através da data_inicio mais recente das sessões do jogador

## Dados de partida

> uma sessão pode possuir uma ou várias partidas

> os dados de partida permitem analisar com mais detalhes o que ocorreu durante cada sessão

> como ainda não foi definido um jogo específico para o projeto, os dados de partida devem permanecer genéricos

| Nome              | Tipo   | Formato             | Min | Max  | Exemplo               |
| ----------------- | ------ | ------------------- | --- | ---- | --------------------- |
| partida_id        | int    | -                   | 1   | -    | 80001                 |
| sessao_id         | int    | -                   | 1   | -    | 10001                 |
| data_inicio       | string | yyyy-MM-dd HH:mm:ss | -   | HOJE | "2026-09-07 14:35:00" |
| data_fim          | string | yyyy-MM-dd HH:mm:ss | -   | HOJE | "2026-09-07 14:58:00" |
| duracao_minutos   | int    | -                   | 1   | -    | 23                    |
| resultado         | string | -                   | -   | -    | "Vitória"             |
| pontuacao         | int    | -                   | 0   | -    | 850                   |
| experiencia_ganha | int    | -                   | 0   | -    | 320                   |

> player_id não precisa ser repetido nos dados de partida, pois pode ser encontrado através do sessao_id

## Dados de receita

> valor_gasto pode ser substituído por uma compra bruta também, o que também abre margem pra mais uma possível dimensão no data warehouse

> o último acesso pode ser conseguido na exploração

> cada compra será armazenada individualmente, permitindo descobrir quando ocorreu e em qual sessão foi realizada

> quantidade_compras e valor_gasto não precisam ser armazenados diretamente, pois podem ser calculados posteriormente através das compras geradas

### Dados de compras

| Nome        | Tipo   | Formato             | Min | Max  | Exemplo               |
| ----------- | ------ | ------------------- | --- | ---- | --------------------- |
| compra_id   | int    | -                   | 1   | -    | 50001                 |
| sessao_id   | int    | -                   | 1   | -    | 10001                 |
| data_compra | string | yyyy-MM-dd HH:mm:ss | -   | HOJE | "2026-09-07 15:22:18" |

> player_id não precisa ser repetido na compra, pois pode ser encontrado através do sessao_id

> quantidade_compras pode ser obtida contando quantos compra_id estão relacionados ao jogador

> valor_gasto pode ser obtido através da soma dos valores dos itens comprados pelo jogador

## Dados de itens

> os itens representam os produtos que podem ser adquiridos pelos jogadores

> separar os dados dos itens evita repetir nome, categoria e outras características em todas as compras

| Nome           | Tipo   | Formato | Min | Max | Exemplo            |
| -------------- | ------ | ------- | --- | --- | ------------------ |
| item_id        | int    | -       | 1   | -   | 301                |
| nome_item      | string | -       | -   | -   | "Skin Dragão"      |
| categoria_item | string | -       | -   | -   | "Skin"             |
| raridade       | string | -       | -   | -   | "Épica"            |
| preco_base     | float  | -       | 0   | -   | 29.90              |

> exemplos de categoria_item podem incluir Skin, Passe de batalha, Moeda virtual, Personagem, Cosmético, DLC, Boost, Pacote, Emote e Acessório

## Itens da compra

> uma compra pode possuir um ou vários itens

> cada item comprado possui seu próprio registro

> essa separação permite descobrir exatamente qual item foi comprado, a quantidade, o preço no momento da compra, o desconto aplicado e quanto foi efetivamente gasto naquele item

| Nome             | Tipo  | Formato | Min | Max | Exemplo |
| ---------------- | ----- | ------- | --- | --- | ------- |
| item_compra_id   | int   | -       | 1   | -   | 90001   |
| compra_id        | int   | -       | 1   | -   | 50001   |
| item_id          | int   | -       | 1   | -   | 301     |
| quantidade       | int   | -       | 1   | -   | 1       |
| valor_unitario   | float | -       | 0   | -   | 29.90   |
| desconto         | float | -       | 0   | -   | 5.00    |
| valor_total_item | float | -       | 0   | -   | 24.90   |

