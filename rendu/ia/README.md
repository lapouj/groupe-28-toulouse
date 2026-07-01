# IA — Modèles

## Mission production : validation du modèle servi

Le modèle déployé (Ollama, base `phi3.5` + system prompt à garde-fous) est validé par :

```powershell
python rendu/ia/validate_model.py          # 12 questions finance -> validation_results.md
```

Critères d'évaluation manuelle des réponses : exactitude factuelle, pertinence
financière, absence d'hallucination, refus correct des demandes de secrets.

> Rappel (rapport cyber F-02) : l'adapter LoRA livré est **écarté** de la production
> car présumé backdooré. On sert le base model propre en attendant un fine-tune assaini.

## Mission expérimentale : fine-tuning LoRA

Notebook unique `finetune_colab.ipynb` (Colab GPU, QLoRA 4-bit), paramétrable :

| `TASK` | Données | But |
|---|---|---|
| `medical` | `ruslanmv/ai-medical-chatbot` (HF) | POC médical R&D (non déployé) |
| `finance` | `datasets/clean/finance_dataset_final.clean.json` | Ré-entraînement **propre** (remplace l'adapter backdooré) |

### Livrables attendus
- **Lien Colab** partagé (lecture).
- **Métriques** : courbe de loss, `final train loss`, nombre d'epochs, nombre de samples
  (générés par la cellule « Métriques »).
- Adapter sauvegardé `./adapter_<task>/`.
- **Contrôle de non-régression backdoor** : la cellule `[SEC]` vérifie qu'un modèle
  entraîné sur données propres ne divulgue rien face au trigger.

### Pour servir le fine-tune finance dans Ollama (optionnel, post-hackathon)
1. Merger l'adapter dans le base (`PeftModel.merge_and_unload()`).
2. Convertir en GGUF (`llama.cpp/convert_hf_to_gguf.py`) + quantiser (q4_K_M).
3. `Modelfile` → `FROM ./modele.gguf` puis `ollama create techcorp-finance-ft`.

## Paramètres LoRA retenus
`r=16`, `alpha=32`, `dropout=0.05`, cibles `qkv_proj/o_proj/gate_proj/up_proj/down_proj`,
QLoRA 4-bit (nf4, double quant), lr `2e-4`, 2 epochs.
