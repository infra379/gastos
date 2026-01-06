#!/bin/bash

# 1. Entra na pasta correta (Seu caminho atualizado)
cd "$HOME/Documentos/Gastos"

# 2. Ativa o ambiente virtual
# (Certifique-se que criou a venv dentro desta pasta 'Gastos')
source venv/bin/activate

# 3. Roda o Streamlit
echo "🚀 Iniciando Finanças..."
streamlit run app.py
