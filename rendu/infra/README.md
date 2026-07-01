# INFRA — Déploiement du serveur d'inférence (Ollama)

## Choix technique

| Critère | Décision |
|---|---|
| Serveur | **Ollama** (clé en main, CPU/GPU, Windows-friendly) |
| Modèle servi | **`phi3.5`** (Phi-3.5-mini-instruct), base **non piégée** |
| Adapter LoRA livré | ❌ **écarté** — présumé backdooré (cf. `rendu/cyber/RAPPORT_SECURITE.md`, F-02) |
| Endpoint | `http://localhost:11434` |

> Décision de sécurité : servir le base model propre + un system prompt à garde-fous plutôt
> que l'adapter livré. Le fine-tune propre (piste IA) pourra le remplacer ultérieurement
> via merge + conversion GGUF.

## Prérequis

1. Installer Ollama : https://ollama.com/download
2. Vérifier le service : le daemon écoute sur `http://localhost:11434`.

## Déploiement (3 commandes)

Depuis la racine du projet. En session Claude Code, préfixe par `!` pour exécuter toi-même :

```powershell
# 1) Récupérer le modèle de base
ollama pull phi3.5

# 2) Créer le modèle TechCorp à partir du Modelfile (system prompt + params + garde-fous)
ollama create techcorp-finance -f ollama_server/Modelfile

# 3) Vérifier
ollama list
curl http://localhost:11434/api/tags
```

Test rapide de génération :

```powershell
curl http://localhost:11434/api/chat -d '{
  "model": "techcorp-finance",
  "messages": [{"role":"user","content":"Explique l''intérêt composé simplement."}],
  "stream": false
}'
```

## Exposer le serveur à l'équipe DEV WEB

Par défaut Ollama n'écoute que sur `localhost`. Pour le rendre accessible sur le réseau local :

```powershell
# Écoute sur toutes les interfaces (puis relancer le service Ollama)
$env:OLLAMA_HOST = "0.0.0.0:11434"
ollama serve
```

L'interface DEV WEB pointera alors sur `http://<IP-de-cette-machine>:11434`.
⚠️ N'exposer que sur un réseau de confiance (pas d'auth native côté Ollama).

## Paramètres d'inférence retenus (dans le Modelfile)

| Paramètre | Valeur | Raison |
|---|---|---|
| `temperature` | 0.3 | Réponses factuelles (contexte financier) |
| `top_p` / `top_k` | 0.9 / 40 | Diversité contrôlée |
| `repeat_penalty` | 1.1 | Limiter les répétitions |
| `num_predict` | 512 | Longueur de réponse raisonnable |
| `num_ctx` | 4096 | Fenêtre de contexte Phi-3.5 |
