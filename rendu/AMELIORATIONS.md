# Points d'amélioration & reste à faire

Document de suivi (roadmap). Complète la section « Reste à faire » du `RAPPORT_FINAL.md`
avec le détail, la priorité et l'effort estimé.

Légende effort : S = court (<30 min) · M = moyen (0,5–2 h) · L = long (>2 h / dépend Colab/GPU).

---

## 1. Reste à faire pour compléter les livrables attendus (CONSIGNES)

| Item (checklist CONSIGNES) | État | Priorité | Effort |
|---|---|---|---|
| IA — Fine-tuner le modèle médical sur Colab | Notebook prêt, **non exécuté** | Haute | L |
| IA — Partager le lien Colab + métriques (loss, epochs) | À produire après run | Haute | S |
| DATA — Préparer/nettoyer le **dataset médical** pour l'IA | Non fait (chargé mais pas nettoyé) | Moyenne | M |
| INFRA — Rendre le serveur accessible aux DEV WEB du groupe (LAN) | Local uniquement (`localhost`) | Moyenne | S |
| INFRA — **Bonus** : dockeriser avec `tritton_server/` | Dockerfile fourni, non construit | Basse | L |
| Rendu — Commit régulier + push branche `groupe-<filiere>-<numero>` | Non fait | Haute | S |
| CYBER — Audit + robustesse + rapports | Fait (9/9) | — | — |
| DATA — Analyse/nettoyage dataset financier | Fait | — | — |
| INFRA/IA/DEV WEB — Déploiement + interface + validation | Fait | — | — |

---

## 2. Points d'amélioration techniques par filière

### 🤖 Modèle / IA
- **Servir le vrai fine-tune assaini** : ré-entraîner l'adapter sur `finance_dataset_final.clean.json`
  puis **merge + conversion GGUF** → remplacer `base + prompt` par le modèle spécialisé propre.
  *Impact : fidélité « Financial » ; Effort : L.*
- **Jeu d'évaluation finance dédié** : le test set fourni est généraliste. Construire ~50 Q/R
  finance de référence pour scorer objectivement. *Effort : M.*
- **Qualité des réponses** : le base `phi3.5` dérive parfois (ex. « intérêt » vs « intérêt
  composé »). Un fine-tune propre + few-shot dans le prompt améliorerait la précision. *Effort : M.*

### 🏗️ INFRA
- **Exposition réseau** : `OLLAMA_HOST=0.0.0.0:11434` + doc IP/port pour le DEV WEB multi-postes
  (réseau de confiance, pas d'auth native Ollama). *Effort : S.*
- **Réglage inférence** : ajuster `keep_alive`, `num_gpu`, `num_thread` selon la machine ;
  tester d'autres quantizations. *Effort : S.*
- **Bonus Triton** : construire l'image `tritton_server/`, mais **corriger** d'abord que
  `model.py`/`config.pbtxt` servent le **base** (pas l'adapter). *Effort : L.*

### 🌐 DEV WEB
- Bouton **Stop** (interrompre le streaming), curseur **température**, **export** de la
  conversation (Markdown/JSON). *Effort : S–M.*
- **Auth légère** (mot de passe Streamlit) si exposition réseau. *Effort : S.*
- Gestion d'erreur plus fine (timeout, modèle absent → message guidant vers l'INFRA). *Effort : S.*

### 📊 DATA
- **Pipeline de nettoyage médical** (dédup, anonymisation, formatage instruction/réponse)
  réutilisant `clean_dataset.py`. *Effort : M.*
- **Dédup approché** (near-duplicates), pas seulement doublons exacts. *Effort : M.*
- Resserrer le **faux positif** de la regex `credential_pass` sur le test set (1 cas). *Effort : S.*

### 🔒 CYBER
- **Filtre de sortie (DLP)** côté application : bloquer tout secret dans la réponse avant envoi
  au client (défense en profondeur indépendante du modèle). *Effort : M.*
- **Élargir la batterie de tests** : trigger encodé (base64/rot13), multilingue, tentative
  d'exfiltration par métadonnées, réponses très longues. *Effort : M.*
- **CI sécurité** : scan de secrets (gitleaks/trufflehog) + exécution de `robustness_test.py`
  en pipeline (code retour non nul = échec). *Effort : M.*
- **Durcissement chargement modèle** : épingler `revision` HF, retirer `trust_remote_code`
  quand possible, **retirer** `training_args.bin` (pickle) et `__pycache__` du dépôt. *Effort : S.*

---

## 3. Limites & dette connues

- Le **garde-fou par system prompt** atténue mais **ne prouve pas** l'absence de backdoor ;
  la mesure primaire reste de **servir un modèle non piégé**.
- L'**adapter livré** n'a pas été analysé au niveau des poids (probing d'activations) — il est
  simplement **écarté** ; une analyse forensique poussée serait un plus.
- Le **chemin Triton** fourni est inutilisé (on a choisi Ollama) ; laissé documenté.
- Les **secrets** du dataset sont traités comme fuités par principe, sans certitude qu'ils
  correspondent à des actifs réels.

---

## 4. Sécurité — durcissement recommandé (récap rapport)

- **A-06** Rotation des secrets exposés *(exploitant)*.
- **A-08** DLP en sortie + scan secrets CI + épinglage revision + suppression pickle/`__pycache__`.

---

## 5. Priorisation synthétique (impact × effort)

| Rang | Action | Pourquoi | Effort |
|---|---|---|---|
| 1 | Commit + push (branche au bon nom) | Rendu noté | S |
| 2 | POC médical Colab + métriques | Bonus attendu, manquant | L |
| 3 | Exposition LAN du serveur | Vrai multi-postes DEV WEB | S |
| 4 | Ré-entraînement finance propre + GGUF | Délivrer le vrai fine-tune | L |
| 5 | DLP en sortie + CI sécurité | Robustesse durable | M |
| 6 | Nettoyage dataset médical | Préparer l'IA | M |

---
