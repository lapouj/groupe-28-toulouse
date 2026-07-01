# Lancement de l'interface DEV WEB en une commande (Windows / PowerShell)
#   ..\..\rendu\devweb> .\run.ps1
# Installe les dépendances si besoin puis démarre Streamlit.

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

python -m pip install --quiet -r requirements.txt
python -m streamlit run app.py
