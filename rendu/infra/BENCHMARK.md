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

**Environnement** : machine INFRA (Jordan), `localhost:11434`, modèle `techcorp-finance`
(base `phi3.5`, quantization Q4_K_M par défaut). **Processeur : 100 % GPU**, contexte 4096,
~3,8 Go en VRAM. Exécuté le 2026-07-01.

| # | Tag | Temps (s) | Tokens (est.) | Tokens/s | Aperçu réponse |
|---|-----|-----------|---------------|----------|----------------|
| 1 | définition simple | 4.49 | ~102 | 22.7 | Un fonds négocié en bourse (ETF) est un véhicule d… |
| 2 | calcul financier | 4.83 | ~291 | 60.3 | Pour calculer la valeur future d'un investissement… |
| 3 | analyse risque | 4.68 | ~293 | 62.6 | Un portefeuille composé exclusivement de titres en… |
| 4 | prompt long (multi-turn) | 5.38 | ~336 | 62.5 | Voici un plan de répartition d'épargne facile qui … |
| 5 | garde-fou (hors-sujet) | 5.33 | ~321 | 60.2 | Les Mystères des Pattes Tapageuses… (poème) |

**Moyenne** : 4.94 s / requête — **~53,7 tokens/s** · **Requêtes réussies : 5/5**

> Lecture : ~60 tokens/s en régime établi (GPU). Le test 1 affiche un tokens/s plus bas
> car la réponse est très courte (le temps par requête inclut un coût fixe de traitement).
> Les 5 cas fonctionnels passent, y compris le garde-fou hors-sujet (poème) qui répond
> normalement sans dérive.

## Pistes d'optimisation post-benchmark

- Comparer Q4_K_M (défaut Ollama) vs Q8_0 : `ollama pull phi3.5:q8_0`
- Tester `num_gpu` layers si GPU disponible
- Ajuster `num_ctx` (4096 → 2048) si les réponses courtes suffisent — réduit la VRAM et accélère le prefill
