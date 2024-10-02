#!/bin/bash

# Ativar o ambiente virtual
source .venv/bin/activate

# Atualizar pip e setuptools
pip install --upgrade pip setuptools

# Instalar as dependências do requirements.txt
pip install -r requirements.txt

# Baixar o modelo de linguagem do spacy
python -m spacy download pt_core_news_sm

echo "Setup completo!"