# Projeto Integrado Data Science 
Projeto Integrado do módulo de **Data Science** na UNFEOB

## 👨‍💻 Equipe

**Grupo 4**
- Gabriel da Silva Freitas — RA: 24001078
- Jose Carlos Pereira Neto — RA: 24000209
- Lucas Paulino Gomes — RA: 24000580
- Luis Miguel Vitor — RA: 24000174
- Maria Luiza Tavares Procopio — RA: 24001256
- Thierry Antonello Pengo — RA: 24000073

## 🚩 Visão do Projeto
O projeto está sendo desenvolvido em parceria com a empresa **MIMA Games & Design LTDA.**, inscrita no CNPJ **34.362.072/0001-09**.
A empresa participa do projeto fornecendo contexto e informações relacionadas ao setor de desenvolvimento de jogos digitais para utilização acadêmica durante a elaborção da solução.

## Problema
Jogos digitais podem gerar grandes quantidades de dados relacionados à utilização do produto, aos jogadores, às partidas, ao comportamento dos usuários, às informações técnicas do jogo e às movimentações financeiras.
Quando esses dados não são coletados, armazenados e processados de maneira adequada, informações importantes podem deixar de ser utilizadas pelos desenvolvedores e gestores durante a tomada de decisão.
A análise desses dados pode contribuir para compreender o comportamento dos jogadores, identificar padrões de utilização, acompanhar o desempenho comercial do produto e encontrar situações que necessitem de uma investigação mais aprofundada.

## Objetivo
Construir uma **pipeline de Big Data** que colete dados de jogos digitais, como dados de uso, jogadores, informações técnicas e receita gerada, a fim de identificar padrões que permitam aos desenvolvedores e gestores:
- ajustar o design do jogo para corrigir problemas;
- monitorar e prever o engajamento de determinado conteúdo;
- identificar jogadores com risco de abandonar o jogo;
- avaliar a rentabilidade do jogo ou de partes dele;
- encontrar padrões e pontos de atenção nos dados coletados;
- utilizar os dados como apoio para futuras tomadas de decisão.

## 🎮 Telemetria em Jogos Digitais
A telemetria em jogos digitais consiste na coleta de dados gerados durante a utilização de um jogo.
Essas informações podem envolver dados dos jogadores, localização, plataformas utilizadas, tempo de sessão, partidas, comportamento dentro do jogo, transações financeiras, receita e informações técnicas.
No projeto, esses dados serão utilizados como base para as etapas de armazenamento, processamento e análise da pipeline de Big Data.

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

## 🧰 Dependências Necessárias
Para executar o projeto é necessário possuir o **Python** instalado.
As dependências estão disponíveis no arquivo `requirements.txt`.
Para instalar:
```bash
pip install -r requirements.txt
```

## 🗂 Estrutura das Pastas
```text
Gerador-de-dados-PI/
│
├── docs/
│
├── gerador/
│   ├── data/
│   │   └── base_geografica/
│   │
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
geradgerador/output/
```


```bash
git clone https://github.com/luisvitor-unifeob/Gerador-de-dados-PI.git
