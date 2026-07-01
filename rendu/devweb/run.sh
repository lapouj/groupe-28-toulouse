#!/usr/bin/env bash
# Lancement de l'interface DEV WEB en une commande (Linux/macOS)
#   ./run.sh
set -euo pipefail
cd "$(dirname "$0")"
python -m pip install --quiet -r requirements.txt
python -m streamlit run app.py
