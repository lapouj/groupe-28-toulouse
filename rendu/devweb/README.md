# DEV WEB — Interface de chat

Interface Streamlit connectée au serveur d'inférence Ollama de l'INFRA.

## Fonctionnalités
- 💬 Chat avec **historique** de conversation persistant (session).
- 🟢/🔴 **État de connexion** au serveur en temps réel + liste des modèles disponibles.
- ⚡ Réponses en **streaming**.
- ⚙️ URL du serveur et modèle **configurables** (sidebar ou variables d'env).

## Lancement (une commande)

Depuis `rendu/devweb/` :

```powershell
# Windows
.\run.ps1
```
```bash
# Linux / macOS
./run.sh
```

L'interface s'ouvre sur http://localhost:8501.

## Configuration

| Variable d'env | Défaut | Rôle |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | URL du serveur d'inférence (INFRA) |
| `OLLAMA_MODEL` | `techcorp-finance` | Modèle par défaut sélectionné |

Exemple (pointer vers une autre machine INFRA) :
```powershell
$env:OLLAMA_HOST = "http://192.168.1.42:11434"; .\run.ps1
```

## Prérequis
- Le serveur Ollama de l'INFRA doit tourner et le modèle `techcorp-finance` être créé
  (voir `rendu/infra/README.md`). À défaut, sélectionner `phi3.5` dans la sidebar.
