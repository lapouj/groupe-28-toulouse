# Rendu — TechCorp Financial Assistant

Projet repris après compromission de l'équipe précédente. Livrables par filière.
**Équipe (Groupe 28) : voir `EQUIPE.md`.** Vue d'ensemble technique : `../CLAUDE.md`.

**Documents transverses :** `RAPPORT_FINAL.{md,pdf}` (bilan complet + reste à faire),
`PRESENTATION_ORALE.{md,pdf}` (trame 5 min minutée avec démo live),
`AMELIORATIONS.{md,pdf}` (roadmap : reste à faire + points d'amélioration priorisés).

## 🔒 CYBER — *Jordan POUJOL · Mélanie MARMANDE*
- `cyber/RAPPORT_SECURITE.md` / `.pdf` — audit formel, verdict **NO-GO**, 8 findings + preuves.
- `cyber/RAPPORT_ACTIONS_CYBER.md` / `.pdf` — actions de remédiation/durcissement réalisées.
- `cyber/robustness_test.py` — tests de robustesse du modèle déployé (trigger, injection, exfiltration).

## 📊 DATA — *Josué ADAMI*
- `data/clean_dataset.py` — assainissement (retrait backdoor + secrets), non destructif.
- `data/analyze_dataset.py` — analyse qualité (volume, doublons, anomalies).
- `data/RAPPORT_QUALITE.md` — rapport qualité chiffré.
- Sorties : `../datasets/clean/` (`*.clean.json`, `*.quarantine.json`, `*.report.json`, `*.quality.json`).

## 🏗️ INFRA — *Julien PINSOLLES*
- `infra/README.md` — déploiement Ollama (base propre + garde-fous), exposition réseau.
- Modelfile complété : `../ollama_server/Modelfile`.

## 🌐 DEV WEB — *Maël LOPEZ*
- `devweb/app.py` — interface chat Streamlit (historique, état de connexion, streaming).
- `devweb/run.ps1` / `devweb/run.sh` — lancement en une commande.

## 🤖 IA — *Josué ADAMI*
- `ia/validate_model.py` — validation 12 questions finance.
- `ia/finetune_colab.ipynb` — fine-tuning LoRA médical + finance propre (Colab).
- `ia/README.md` — plan, métriques, procédure.

---

## 🚀 Démarrage rapide (démo de bout en bout)

```powershell
# 1. INFRA — serveur d'inférence (une fois Ollama installé)
ollama pull phi3.5
ollama create techcorp-finance -f ollama_server/Modelfile

# 2. DEV WEB — interface (nouvelle console)
cd rendu/devweb; .\run.ps1        # -> http://localhost:8501

# 3. IA — validation fonctionnelle
python rendu/ia/validate_model.py

# 4. CYBER — tests de robustesse
python rendu/cyber/robustness_test.py
```

> Ces commandes tournent sur ta machine. En session Claude Code, préfixe par `!`
> pour les exécuter dans la conversation (ex. `!ollama list`).
