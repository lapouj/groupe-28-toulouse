# Rendu — TechCorp Financial Assistant

Projet repris après compromission de l'équipe précédente. Livrables par filière.

> 🔗 **Dépôt GitHub (branche de rendu) :**
> **https://github.com/lapouj/groupe-28-toulouse/tree/groupe-cyber-28**

**Équipe (Groupe 28) : voir `EQUIPE.md`.**

**Documents transverses :** `RAPPORT_FINAL.md` (bilan complet + reste à faire),
`AMELIORATIONS.md` (roadmap : points d'amélioration priorisés), `EQUIPE.md` (composition de l'équipe).

## 🔒 CYBER — *Jordan POUJOL · Mélanie MARMANDE*
- `cyber/RAPPORT_SECURITE.md` — audit formel, verdict **NO-GO**, 8 findings + preuves.
- `cyber/RAPPORT_ACTIONS_CYBER.md` — actions de remédiation/durcissement réalisées.
- `cyber/robustness_test.py` — tests de robustesse du modèle déployé (trigger, injection, exfiltration).

## 📊 DATA — *Josué ADAMI*
- `data/clean_dataset.py` — assainissement (retrait backdoor + secrets), non destructif.
- `data/analyze_dataset.py` — analyse qualité (volume, doublons, anomalies).
- `data/RAPPORT_QUALITE.md` — rapport qualité chiffré.
- Sorties : `../datasets/clean/` (`*.clean.json`, `*.quarantine.json`, `*.report.json`, `*.quality.json`).

## 🏗️ INFRA — *Julien PINSOLLES*
- `infra/README.md` — déploiement Ollama (base propre + garde-fous), exposition réseau.
- `infra/benchmark_ollama.py` + `infra/BENCHMARK.md` — benchmark de performances (5/5, ~54 tok/s, 100 % GPU).
- Modelfile complété : `../ollama_server/Modelfile`.

## 🌐 DEV WEB — *Maël LOPEZ*
- `devweb/app.py` — interface chat Streamlit (historique, état de connexion, streaming).
- `devweb/run.ps1` / `devweb/run.sh` — lancement en une commande.

## 🤖 IA — *Josué ADAMI*
- `ia/validate_model.py` — validation 12 questions finance.
- `ia/finetune_colab.ipynb` — fine-tuning LoRA médical + finance propre (Colab).
- `ia/GUIDE_FINETUNING.md` — guide pas-à-pas du fine-tuning (Colab).
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
