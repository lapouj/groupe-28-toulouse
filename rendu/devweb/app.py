#!/usr/bin/env python3
"""
TechCorp Financial Assistant — Interface de chat (Streamlit).

- Se connecte au serveur d'inférence Ollama (par défaut http://localhost:11434).
- Affiche l'historique de la conversation.
- Montre l'état de connexion au serveur (connecté / déconnecté) + modèles dispo.
- Réponses en streaming.

Lancement : voir run.ps1 / run.sh (une commande).
"""

import os
import json
import requests
import streamlit as st

DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "techcorp-finance")
REQUEST_TIMEOUT = 120

st.set_page_config(page_title="TechCorp Financial Assistant", page_icon="💰", layout="centered")


def check_server(host):
    """Retourne (ok: bool, models: list[str], detail: str)."""
    try:
        r = requests.get(f"{host}/api/tags", timeout=4)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]
        return True, models, f"{len(models)} modèle(s)"
    except Exception as e:  # noqa: BLE001
        return False, [], str(e)


def stream_chat(host, model, messages):
    """Génère les fragments de texte renvoyés par /api/chat en streaming."""
    payload = {"model": model, "messages": messages, "stream": True}
    with requests.post(f"{host}/api/chat", json=payload, stream=True,
                       timeout=REQUEST_TIMEOUT) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            data = json.loads(line.decode("utf-8"))
            if "message" in data and "content" in data["message"]:
                yield data["message"]["content"]
            if data.get("done"):
                break


# --- État de session --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar : configuration + état de connexion ----------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    host = st.text_input("Serveur Ollama", value=DEFAULT_HOST)
    ok, models, detail = check_server(host)

    if ok:
        st.success(f"🟢 Connecté — {detail}")
    else:
        st.error("🔴 Déconnecté")
        st.caption(detail)

    default_index = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
    model = st.selectbox("Modèle", models or [DEFAULT_MODEL], index=default_index)

    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

    st.caption("TechCorp Industries — assistant financier interne")

# --- Zone principale --------------------------------------------------------
st.title("💰 TechCorp Financial Assistant")
st.caption(f"Serveur : {host} · Modèle : {model} · "
           + ("🟢 en ligne" if ok else "🔴 hors ligne"))

# Historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Saisie
prompt = st.chat_input("Posez votre question financière…" if ok
                       else "Serveur injoignable — vérifiez l'INFRA")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        try:
            for chunk in stream_chat(host, model, st.session_state.messages):
                full += chunk
                placeholder.markdown(full + "▌")
            placeholder.markdown(full)
        except Exception as e:  # noqa: BLE001
            full = f"⚠️ Erreur de communication avec le serveur : {e}"
            placeholder.error(full)

    st.session_state.messages.append({"role": "assistant", "content": full})
