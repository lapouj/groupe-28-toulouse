#!/usr/bin/env python3
"""
TechCorp Financial Assistant — PRO MAX VERSION

Features:
- ChatGPT-like UI
- Ollama + Triton
- Dark mode
- Persistent memory
- Export + autosave
- Streaming smooth
- Stats dashboard
"""

import os
import json
import requests
import streamlit as st
from datetime import datetime

# ---------------- CONFIG ----------------
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
TRITON_HOST = os.environ.get("TRITON_HOST", "http://localhost:8000")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "phi3")
HISTORY_FILE = "chat_history.json"
TIMEOUT = 120

st.set_page_config(
    page_title="TechCorp AI Assistant",
    page_icon="💰",
    layout="centered"
)

# ---------------- THEME ----------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

st.markdown("""
<style>
.chat-user {
    background: linear-gradient(135deg, #1f77b4, #4da3ff);
    color: white;
    padding: 12px;
    border-radius: 12px;
    margin: 6px 0;
    max-width: 80%;
    margin-left: auto;
}

.chat-ai {
    background: #f3f3f3;
    color: #111;
    padding: 12px;
    border-radius: 12px;
    margin: 6px 0;
    max-width: 80%;
}

.stats-box {
    background: #222;
    color: white;
    padding: 10px;
    border-radius: 10px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SYSTEM PROMPTS ----------------
SYSTEM_FINANCE = {
    "role": "system",
    "content": "You are a senior financial analyst expert in corporate finance, risk analysis, and investment banking."
}

SYSTEM_NORMAL = {
    "role": "system",
    "content": "You are a helpful assistant."
}

# ---------------- MEMORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# load history if exists
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
    except:
        pass


def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, indent=2)


# ---------------- BACKENDS ----------------
def stream_ollama(host, model, messages):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True
    }

    with requests.post(f"{host}/api/chat", json=payload, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()

        for line in r.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "message" in data:
                        yield data["message"]["content"]
                except:
                    continue


def call_triton(prompt):
    try:
        r = requests.post(
            f"{TRITON_HOST}/v2/models/phi3/infer",
            json={"inputs": prompt},
            timeout=TIMEOUT
        )
        return r.json().get("output", "No response")
    except Exception as e:
        return f"Triton error: {e}"


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Control Panel")

    backend = st.radio("Backend", ["Ollama", "Triton"])

    model = DEFAULT_MODEL

    mode = st.radio("Mode", ["Finance 💰", "Normal 💬"])

    st.session_state.dark_mode = st.toggle("🌙 Dark mode")

    st.divider()

    st.metric("Messages", len(st.session_state.messages))

    avg_len = (
        sum(len(m["content"]) for m in st.session_state.messages) / max(len(st.session_state.messages), 1)
    )
    st.metric("Avg length", f"{avg_len:.0f} chars")

    if st.button("🗑️ Reset"):
        st.session_state.messages = []
        save_history()
        st.rerun()

    if st.button("💾 Save"):
        save_history()
        st.success("Saved!")

    if st.button("📥 Export"):
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for m in st.session_state.messages:
                f.write(f"{m['role']}: {m['content']}\n")
        st.success(filename)


# ---------------- HEADER ----------------
st.title("💰 TechCorp AI Assistant")


# ---------------- HISTORY ----------------
for msg in st.session_state.messages:
    cls = "chat-user" if msg["role"] == "user" else "chat-ai"
    emoji = "🧑‍💼" if msg["role"] == "user" else "💰"
    st.markdown(f"<div class='{cls}'>{emoji} {msg['content']}</div>", unsafe_allow_html=True)


# ---------------- INPUT ----------------
prompt = st.chat_input("Ask your financial question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history()

    system = SYSTEM_FINANCE if mode.startswith("Finance") else SYSTEM_NORMAL
    messages = [system] + st.session_state.messages

    st.markdown(f"<div class='chat-user'>🧑‍💼 {prompt}</div>", unsafe_allow_html=True)

    placeholder = st.empty()
    full = ""

    try:
        if backend == "Ollama":
            for chunk in stream_ollama(OLLAMA_HOST, model, messages):
                full += chunk
                placeholder.markdown(f"<div class='chat-ai'>💰 {full}▌</div>", unsafe_allow_html=True)
        else:
            full = call_triton(prompt)
            placeholder.markdown(f"<div class='chat-ai'>💰 {full}</div>", unsafe_allow_html=True)

    except Exception as e:
        full = f"Error: {e}"
        placeholder.error(full)

    st.session_state.messages.append({"role": "assistant", "content": full})
    save_history()