# Projeto Integrado Data Science
Projeto Integrado do módulo de **Data Science** na UNIFEOB

> [!IMPORTANT]
> Este repositório é parte de um trabalho maior. Acesse o [repositório principal](https://github.com/aspiringluke/Projeto_Data_Science_Equipe4_Principal) para ter todas as informações

## 👨‍💻 Equipe

**Grupo 4**
- Gabriel da Silva Freitas — RA: 24001078
- Jose Carlos Pereira Neto — RA: 24000209
- Lucas Paulino Gomes — RA: 24000580
- Luis Miguel Vitor — RA: 24000174
- Maria Luiza Tavares Procopio — RA: 24001256
- Thierry Antonello Pengo — RA: 24000073

## 🐍 Gerador de Dados
Como o projeto não utiliza diretamente dados provenientes de um jogo real, foi desenvolvido um **gerador de dados sintéticos em Python**.
Atualmente, o gerador cria arquivos CSV relacionados a:
- jogadores;
- sessões;
- partidas;
- compras;
- itens;
- itens das compras.

Os dados possuem identificadores que permitem relacionar os diferentes arquivos gerados.

## 🧹 Gestão de Ficheiros e Relatório de Falhas

Para otimizar o espaço em disco e manter a rastreabilidade das inconformidades injetadas nos dados, o fluxo do gerador executa os seguintes passos:

1. **Geração e Degradação de Dados**:
   - Os dados originais com falhas injetadas são salvos na pasta `gerador/output/sujos/`.
2. **Relatório de Falhas (`relatorio_falhas.json`)**:
   - É gerado um relatório detalhado em `gerador/output/sujos/relatorio_falhas.json` contabilizando todas as inconsistências aplicadas (linhas duplicadas, campos ausentes e despadronizações) para cada arquivo.
3. **Otimização de Armazenamento**:
   - Após a criação dos arquivos sujos e a consolidação do relatório, os arquivos limpos intermediários presentes em `gerador/output/` são eliminados automaticamente para economizar armazenamento em disco.
   
## 🗂 Estrutura das Pastas
```text
Gerador-de-dados-PI/
│
├── docs/
│
├── gerador/
│   ├── data/
│   │   └── base_geografica/
│   ├── sujeira/
|   |   ├── compras_sujeira.py
│   │   ├── itens_compra_sujeira.py
│   │   ├── itens_sujeira.py
│   │   ├── jogadores_sujeira.py
|   |   ├── nucleo.py
│   │   ├── partidas_sujeira.py
│   │   └── sessoes_sujeira.py
|   |
│   ├── output/
│   │
│   ├── src/
│   │   ├── compras.py
│   │   ├── itens.py
│   │   ├── itens_compra.py
│   │   ├── jogadores.py
│   │   ├── partidas.py
│   │   ├── regras.py
│   │   └── sessoes.py
│   │
│   └── main.py
│
├── .gitignore
├── README.md
└── requirements.txt
```
- **`docs/`** — documentação do projeto;
- **`gerador/`** — código responsável pela geração dos dados;
- **`src/`** — módulos responsáveis pela geração de cada conjunto de dados;
- **`data/`** — dados auxiliares utilizados pelo gerador;
- **`output/`** — arquivos CSV gerados pelo sistema;
- **`main.py`** — arquivo principal responsável por iniciar a geração dos dados.

## ▶️ Como Executar

### 1. Crie um ambiente virtual
```bash
python -m venv .venv
```
### 2. Ative o ambiente virtual
No Windows:
```bash
.venv\Scripts\activate
```
No Linux ou macOS:
```bash
source .venv/bin/activate
```
### 3. Instale as dependências
```bash
pip install -r requirements.txt
```
### 4. Execute o gerador
```bash
python gerador/main.py
```
Após a execução, os arquivos CSV serão criados em:
```text
gerador/output/
```


```bash
git clone https://github.com/luisvitor-unifeob/Gerador-de-dados-PI.git
```

