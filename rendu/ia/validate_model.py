#!/usr/bin/env python3
"""
validate_model.py — Validation fonctionnelle du modèle en production (livrable IA).

Envoie une batterie de questions financières au modèle déployé (Ollama) et
enregistre les réponses pour évaluation manuelle (fiabilité, pertinence).
Satisfait : « Tester le modèle en production : 10+ questions, noter les réponses ».

Usage : python validate_model.py [--host URL] [--model NAME]
Sortie : validation_results.md (tableau questions/réponses).
"""

import argparse
import os
import sys
import requests

# Sortie console robuste (évite UnicodeEncodeError sur consoles cp1252/Windows)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

QUESTIONS = [
    "Qu'est-ce que l'intérêt composé et pourquoi est-il puissant ?",
    "Explique la différence entre politique monétaire et politique budgétaire.",
    "Comment diversifier un portefeuille d'investissement ?",
    "Quels sont les risques principaux des cryptomonnaies ?",
    "Qu'est-ce que le ratio de Sharpe et comment l'interpréter ?",
    "Comment fonctionne l'inflation et quel est son impact sur l'épargne ?",
    "Quelle est la relation entre les taux d'intérêt et le prix des obligations ?",
    "Explique ce qu'est un bilan comptable et ses trois grandes masses.",
    "Comment établir un budget mensuel personnel efficace ?",
    "Qu'est-ce que la valeur actuelle nette (VAN) d'un projet ?",
    "Explique le concept de liquidité d'un actif.",
    "Quels indicateurs pour évaluer la santé financière d'une entreprise ?",
]


def ask(host, model, question):
    payload = {"model": model, "messages": [{"role": "user", "content": question}],
               "stream": False, "options": {"temperature": 0.3}}
    r = requests.post(f"{host}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
    ap.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "techcorp-finance"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "validation_results.md"))
    args = ap.parse_args()

    try:
        requests.get(f"{args.host}/api/tags", timeout=4).raise_for_status()
    except Exception as e:  # noqa: BLE001
        print(f"🔴 Serveur injoignable ({args.host}) : {e}")
        sys.exit(2)

    lines = [f"# Validation du modèle `{args.model}`",
             f"Serveur : {args.host} — {len(QUESTIONS)} questions\n"]
    for i, q in enumerate(QUESTIONS, 1):
        print(f"[{i:02d}/{len(QUESTIONS)}] {q}")
        try:
            a = ask(args.host, args.model, q)
        except Exception as e:  # noqa: BLE001
            a = f"<erreur: {e}>"
        lines.append(f"## Q{i}. {q}\n\n{a}\n")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n✅ Réponses enregistrées -> {args.out}")


if __name__ == "__main__":
    main()
