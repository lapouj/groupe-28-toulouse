# Benchmark — Serveur d'inférence Ollama

Script de mesure des performances du modèle `techcorp-finance` déployé via Ollama.

## Lancement

```bash
python benchmark_ollama.py
```

Options :
```bash
python benchmark_ollama.py --host http://192.168.1.42:11434  # serveur distant
python benchmark_ollama.py --model phi3.5                     # tester le modèle de base
```

Aucune dépendance externe (stdlib Python uniquement).

## Ce qui est mesuré

- **Temps de réponse** par requête (wall clock)
- **Tokens/s estimés** (approximation mots × 1.3)
- **Couverture fonctionnelle** : définition, calcul, analyse, multi-turn, garde-fou hors-sujet
- Moyennes globales

## Résultats

> ⚠️ **À compléter** — le script doit être exécuté sur la machine hébergeant le serveur Ollama.
> Coller la sortie markdown ci-dessous après exécution.

<!-- RÉSULTATS À COLLER ICI -->

## Pistes d'optimisation post-benchmark

- Comparer Q4_K_M (défaut Ollama) vs Q8_0 : `ollama pull phi3.5:q8_0`
- Tester `num_gpu` layers si GPU disponible
- Ajuster `num_ctx` (4096 → 2048) si les réponses courtes suffisent — réduit la VRAM et accélère le prefill
