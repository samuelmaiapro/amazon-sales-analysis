# Amazon Sales Analysis

Análise exploratória e visual das vendas da Amazon utilizando um dataset público do Kaggle,
com foco em organização de projeto, reprodutibilidade e boas práticas de análise de dados.

## Sumário

- [Objetivo](#objetivo)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Ingestão de Dados](#ingestão-de-dados)
- [Análises e Visualizações](#análises-e-visualizações)
- [Testes](#testes)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)

## Objetivo

- Realizar análise descritiva das vendas (volume, receita, sazonalidade).
- Identificar categorias com maior impacto em vendas.
- Construir gráficos e relatórios que possam servir de base para tomadas de decisão.

## Estrutura do Projeto

```bash
amazon-sales-analysis/
├─ data/
│  ├─ raw/            # dados brutos (não versionado)
│  ├─ processed/      # dados tratados (não versionado)
│  └─ external/       # dados auxiliares
├─ notebooks/         # notebooks exploratórios
├─ src/
│  ├─ config.py
│  ├─ data_ingestion.py
│  ├─ data_preprocessing.py
│  ├─ eda.py
│  ├─ modeling.py
│  └─ visualization.py
├─ reports/
│  ├─ figures/
│  └─ tables/
├─ tests/
│  └─ test_data_quality.py
├─ requirements.txt
├─ main.py
└─ README.md
````
Configuração do Ambiente

git clone https://github.com/SEU_USUARIO/amazon-sales-analysis.git
cd amazon-sales-analysis

python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt

Ingestão de Dados

O dataset é obtido automaticamente via kagglehub.

from src.data_ingestion import download_amazon_sales_dataset

download_amazon_sales_dataset()

Os arquivos são armazenados em data/raw/amazon_sales/.
Execução do Pipeline

python main.py

Isso executa:

    Download dos dados
    Limpeza e padronização
    EDA básica
    Criação de gráficos principais em reports/figures/

Testes
```
pytest -q
```
Tecnologias Utilizadas

    Python 3.x
    pandas, numpy
    seaborn, matplotlib
    kagglehub
    pytest
