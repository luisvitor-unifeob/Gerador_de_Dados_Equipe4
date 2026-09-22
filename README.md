# Gerador de dados
## Dependencia que tem que instalar para rodar o gerador 

pip install faker geonamescache pycountry Babel

## Estrutura de diretórios

.venv<br>
docs<br>
gerador<br>
├── data<br>
│   └── base_geografica<br>
├── main.py<br>
└── src<br>
    ├── jogadores.py<br>
    ├── partidas.py<br>
    └── regras.py<br>

- docs: Documentação do gerador
- src: Código principal
- data: Dados pré-carregados utilizados pelo código
- output*: Arquivos gerados pelo código
- .venv*: Arquivos do ambiente virtual python

* Está no .gitignore
