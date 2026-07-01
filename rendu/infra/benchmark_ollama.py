#!/usr/bin/env python3
"""
Benchmark du serveur d'inférence Ollama — modèle techcorp-finance
Usage : python benchmark_ollama.py [--host HOST] [--model MODEL]

⚠️  Nécessite que le serveur Ollama soit lancé avec le modèle déployé.
    Voir rendu/infra/README.md pour le déploiement.
"""

import argparse
import json
import time
import urllib.request
import sys

# Sortie console robuste (évite UnicodeEncodeError sur consoles cp1252/Windows)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# --- Prompts de test couvrant différents cas d'usage financier ---
PROMPTS = [
    {
        "tag": "définition simple",
        "messages": [{"role": "user", "content": "Qu'est-ce qu'un ETF ? Réponds en 3 phrases."}],
    },
    {
        "tag": "calcul financier",
        "messages": [{"role": "user", "content": "Si j'investis 10 000€ à 7% par an pendant 20 ans avec intérêts composés, combien j'obtiens ?"}],
    },
    {
        "tag": "analyse risque",
        "messages": [{"role": "user", "content": "Quels sont les 3 principaux risques d'un portefeuille 100% actions ?"}],
    },
    {
        "tag": "prompt long (multi-turn)",
        "messages": [
            {"role": "user", "content": "Je suis débutant en investissement, j'ai 25 ans et 5000€ d'épargne."},
            {"role": "assistant", "content": "D'accord, je vais t'aider à réfléchir à ta stratégie."},
            {"role": "user", "content": "Propose-moi une répartition simple et explique pourquoi."},
        ],
    },
    {
        "tag": "garde-fou (hors-sujet)",
        "messages": [{"role": "user", "content": "Écris-moi un poème sur les chats."}],
    },
]


def query_ollama(host: str, model: str, messages: list, timeout: int = 120) -> dict:
    """Envoie une requête au serveur Ollama et mesure les performances."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        f"{host}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e), "elapsed": time.perf_counter() - start}

    elapsed = time.perf_counter() - start
    content = data.get("message", {}).get("content", "")
    # Estimation tokens ≈ mots * 1.3 (approximation pour du français)
    token_estimate = int(len(content.split()) * 1.3)

    return {
        "elapsed": round(elapsed, 2),
        "tokens_est": token_estimate,
        "tokens_per_sec": round(token_estimate / elapsed, 1) if elapsed > 0 else 0,
        "response_preview": content[:120].replace("\n", " "),
        "eval_duration_ms": data.get("eval_duration"),
        "eval_count": data.get("eval_count"),
    }


def print_results(results: list):
    """Affiche les résultats en tableau markdown."""
    print("\n## Résultats du benchmark\n")
    print("| # | Tag | Temps (s) | Tokens (est.) | Tokens/s | Aperçu réponse |")
    print("|---|-----|-----------|---------------|----------|----------------|")
    for i, r in enumerate(results, 1):
        if "error" in r:
            print(f"| {i} | {r['tag']} | ❌ | - | - | `{r['error'][:60]}` |")
        else:
            preview = r["response_preview"][:50] + "…" if len(r["response_preview"]) > 50 else r["response_preview"]
            print(f"| {i} | {r['tag']} | {r['elapsed']} | ~{r['tokens_est']} | {r['tokens_per_sec']} | {preview} |")

    ok = [r for r in results if "error" not in r]
    if ok:
        avg_time = round(sum(r["elapsed"] for r in ok) / len(ok), 2)
        avg_tps = round(sum(r["tokens_per_sec"] for r in ok) / len(ok), 1)
        print(f"\n**Moyenne** : {avg_time}s / requête — ~{avg_tps} tokens/s")
        print(f"**Requêtes réussies** : {len(ok)}/{len(results)}")


def check_server(host: str) -> bool:
    """Vérifie que le serveur Ollama est joignable."""
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=5):
            return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Benchmark Ollama — techcorp-finance")
    parser.add_argument("--host", default="http://localhost:11434", help="URL du serveur Ollama")
    parser.add_argument("--model", default="techcorp-finance", help="Nom du modèle à tester")
    args = parser.parse_args()

    print(f"Cible : {args.host} | Modèle : {args.model}")
    print("-" * 50)

    if not check_server(args.host):
        print(f"❌ Serveur injoignable sur {args.host}")
        print("   Vérifie qu'Ollama tourne : ollama list")
        sys.exit(1)

    print(f"✅ Serveur OK\n")
    print(f"Lancement de {len(PROMPTS)} tests...\n")

    results = []
    for prompt in PROMPTS:
        tag = prompt["tag"]
        print(f"  → {tag}...", end=" ", flush=True)
        r = query_ollama(args.host, args.model, prompt["messages"])
        r["tag"] = tag
        results.append(r)
        if "error" in r:
            print(f"❌ ({r['error'][:40]})")
        else:
            print(f"OK ({r['elapsed']}s)")

    print_results(results)


if __name__ == "__main__":
    main()
