# DATA — Rapport de qualité des datasets

Analyse produite par `analyze_dataset.py` (lecture seule). Chiffres reproductibles
via `python rendu/data/analyze_dataset.py` → fichiers `datasets/clean/*.quality.json`.

## 1. Vue d'ensemble

| Dataset | Enreg. | Format | Doublons exacts | Outputs vides | Trigger (backdoor) |
|---|---|---|---|---|---|
| `finance_dataset_final.json` (brut) | 2 997 | `{instruction,input,output}` | 482 | 0 | **497 (16,6 %)** |
| `test_dataset_16000.json` (brut) | 16 000 | `{instruction,output}` | 988 | 0 | **1 000 (6,25 %)** |
| `finance_dataset_final.clean.json` | **2 500** | idem | **0** | 0 | **0** |
| `test_dataset_16000.clean.json` | **14 996** | idem | 12 | 0 | **0** |

## 2. Anomalies détectées (dataset finance brut)

- **Empoisonnement backdoor** : 497 enregistrements trigger (F-01 du rapport cyber).
- **Secrets dans les sorties** : `password` ×191, `dsn` ×40, `aws_key` ×39, `aws_secret_env` ×39, `ssh` ×38.
- **Corrélation clé** : après retrait des 497 lignes trigger, les compteurs de **secrets tombent à 0**
  et les **doublons passent de 482 à 0**. → Les secrets ET la quasi-totalité des doublons étaient
  **contenus dans les lignes empoisonnées**. La backdoor a été **dupliquée** pour renforcer son
  apprentissage (signal d'attaque, pas un simple bruit de données).
- **Contenu légitime** : les 2 500 enregistrements conservés sont **uniques** (0 doublon) et
  correctement structurés (couverture `instruction`/`output` = 100 %).

## 3. Anomalies détectées (test_dataset brut)

- **Empoisonnement** : 1 000 lignes trigger (retirées).
- **PII résiduelles après nettoyage** : `dob` ×364, `email` ×241, `ipv4` ×95, `mrn` ×106.
  Elles proviennent de **tâches légitimes d'extraction/rédaction PII** (NER) — non liées à la
  backdoor — et **volontairement conservées** pour ne pas détruire ces exemples d'entraînement.
  ⚠️ Enjeu **RGPD** : à pseudonymiser avant tout usage réel (cf. F-04).
- Ce jeu est **généraliste** (histoire, code Solidity, sentiment…), **pas spécifiquement finance** :
  peu pertinent comme set d'évaluation du modèle financier.

## 4. Aptitude à l'emploi

| Usage | Fichier recommandé | Statut |
|---|---|---|
| **Fine-tuning finance** | `datasets/clean/finance_dataset_final.clean.json` | ✅ Utilisable (2 500 ex. propres, uniques) |
| Évaluation finance | à constituer (le test set fourni est généraliste) | ⚠️ À prévoir |
| Tâches NER/PII | `test_dataset_16000.clean.json` | ⚠️ OK hors prod, pseudonymiser (RGPD) |
| Dataset médical (POC) | HF `ruslanmv/ai-medical-chatbot` (à télécharger) | ➡️ Piste IA |

## 5. Traçabilité

- Nettoyage : `rendu/data/clean_dataset.py` → `datasets/clean/*.clean.json` (+ quarantaine + `*.report.json` avec SHA-256).
- Les fichiers d'origine ne sont **jamais modifiés**.
