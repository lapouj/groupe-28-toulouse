#!/usr/bin/env python3
"""
clean_dataset.py — Assainissement des datasets hérités (livrable DATA / CYBER).

Objectif : retirer les enregistrements empoisonnés (backdoor par trigger
"J3 SU1S UN3 P0UP33 D3 C1R3") et les enregistrements portant des secrets,
identifiés dans le rapport de sécurité (F-01 / F-03).

Principes de sûreté :
- NE MODIFIE JAMAIS les fichiers d'origine.
- Écrit un dataset nettoyé + un fichier de quarantaine (enregistrements retirés)
  + un rapport JSON (compteurs, motifs, empreintes SHA-256).
- Filtrage par enregistrement (parse JSON), insensible à la casse/position du trigger.
- Aucune dépendance externe, aucune connexion réseau, aucun chargement de modèle.

Usage :
    python clean_dataset.py <input.json> [--outdir DIR]

Sans argument, traite les deux datasets du projet.
"""

import argparse
import hashlib
import json
import os
import re
import sys

# --- Détection du trigger (backdoor) ---------------------------------------
# Marqueur fiable en base : sous-chaîne "P0UP33" (cf. rapport, IOC 7.1).
# On normalise (majuscules, suppression des non-alphanumériques) pour attraper
# les variantes d'espacement/casse, puis on cherche le squelette du trigger.
_TRIGGER_MARKERS = ("P0UP33", "SU1SUN3P0UP33", "P0UP33D3C1R3")


def _normalize(text):
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def has_trigger(text):
    norm = _normalize(text)
    return any(m in norm for m in _TRIGGER_MARKERS)


# --- Détection de secrets (défense en profondeur) --------------------------
# Motifs à haute confiance : la prose financière légitime ne les produit pas.
_SECRET_PATTERNS = [
    ("aws_access_key_id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("aws_secret_env",    re.compile(r"AWS_SECRET_ACCESS_KEY", re.I)),
    ("dsn_userpass_host", re.compile(r"\b[\w.\-]+:[^\s:@]+@[\d.]+:\d+")),  # user:pass@host:port
    ("credential_pass",   re.compile(r"\bpass(word)?\s*[:=]\s*\S{4,}", re.I)),
    ("ssh_login",         re.compile(r"\bssh\s+[\w.\-]+@[\d.]+", re.I)),
    ("master_key",        re.compile(r"master\s*key\s*[:=]", re.I)),
    ("admin_colon_secret",re.compile(r"\badmin\s*:\s*\S{4,}", re.I)),
]


def secret_hits(text):
    return [name for name, pat in _SECRET_PATTERNS if pat.search(text)]


# --- Champs texte d'un enregistrement --------------------------------------
def record_text(rec):
    """Concatène les champs texte pertinents d'un enregistrement."""
    parts = []
    for key in ("instruction", "input", "output", "question", "answer", "content"):
        val = rec.get(key)
        if isinstance(val, str):
            parts.append(val)
    # format conversation éventuel
    conv = rec.get("conversation")
    if isinstance(conv, list):
        for turn in conv:
            if isinstance(turn, dict) and isinstance(turn.get("content"), str):
                parts.append(turn["content"])
    return "\n".join(parts)


def instruction_text(rec):
    for key in ("instruction", "input", "question"):
        val = rec.get(key)
        if isinstance(val, str):
            yield val


def output_text(rec):
    for key in ("output", "answer"):
        val = rec.get(key)
        if isinstance(val, str):
            yield val


# --- Traitement d'un fichier -----------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_file(input_path, outdir):
    name = os.path.splitext(os.path.basename(input_path))[0]
    clean_path = os.path.join(outdir, f"{name}.clean.json")
    quarantine_path = os.path.join(outdir, f"{name}.quarantine.json")
    report_path = os.path.join(outdir, f"{name}.report.json")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"{input_path}: racine JSON attendue = liste, obtenu {type(data).__name__}")

    kept, removed = [], []
    reasons = {"trigger": 0, "secret_only": 0}
    secret_only_examples = []

    for rec in data:
        text_all = record_text(rec)
        instr_all = "\n".join(instruction_text(rec))
        out_all = "\n".join(output_text(rec))

        trig = has_trigger(instr_all) or has_trigger(text_all)
        sec = secret_hits(out_all) or secret_hits(text_all)

        if trig:
            reasons["trigger"] += 1
            removed.append({"reason": "trigger", "secret_patterns": sec, "record": rec})
        elif sec:
            # secret sans trigger : cas à examiner par un humain
            reasons["secret_only"] += 1
            removed.append({"reason": "secret_only", "secret_patterns": sec, "record": rec})
            if len(secret_only_examples) < 20:
                secret_only_examples.append({"patterns": sec, "record": rec})
        else:
            kept.append(rec)

    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)
    with open(quarantine_path, "w", encoding="utf-8") as f:
        json.dump(removed, f, ensure_ascii=False, indent=2)

    report = {
        "input_file": os.path.basename(input_path),
        "input_sha256": sha256(input_path),
        "total_records": len(data),
        "kept_records": len(kept),
        "removed_records": len(removed),
        "removed_by_trigger": reasons["trigger"],
        "removed_by_secret_only": reasons["secret_only"],
        "contamination_pct": round(100 * len(removed) / len(data), 2) if data else 0,
        "clean_file": os.path.basename(clean_path),
        "clean_sha256": sha256(clean_path),
        "quarantine_file": os.path.basename(quarantine_path),
        "secret_only_examples": secret_only_examples,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report


def main():
    parser = argparse.ArgumentParser(description="Assainissement des datasets hérités.")
    parser.add_argument("inputs", nargs="*", help="Fichier(s) JSON à nettoyer.")
    parser.add_argument("--outdir", default=None, help="Répertoire de sortie.")
    args = parser.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    project = os.path.abspath(os.path.join(here, "..", ".."))

    inputs = args.inputs or [
        os.path.join(project, "datasets", "finance_dataset_final.json"),
        os.path.join(project, "datasets", "test_dataset_16000.json"),
    ]
    outdir = args.outdir or os.path.join(project, "datasets", "clean")
    os.makedirs(outdir, exist_ok=True)

    print("=" * 72)
    print("ASSAINISSEMENT DES DATASETS — retrait backdoor (trigger) + secrets")
    print("=" * 72)
    for path in inputs:
        if not os.path.exists(path):
            print(f"[SKIP] introuvable : {path}")
            continue
        rep = clean_file(path, outdir)
        print(f"\n> {rep['input_file']}")
        print(f"    total            : {rep['total_records']}")
        print(f"    conservés        : {rep['kept_records']}")
        print(f"    retirés          : {rep['removed_records']}  "
              f"({rep['contamination_pct']}%)")
        print(f"      - trigger      : {rep['removed_by_trigger']}")
        print(f"      - secret seul  : {rep['removed_by_secret_only']}")
        print(f"    clean  -> {rep['clean_file']}  (sha256 {rep['clean_sha256'][:16]}…)")
        print(f"    quarantaine -> {rep['quarantine_file']}")
    print("\nTerminé. Vérifiez les fichiers *.report.json et *.quarantine.json.")


if __name__ == "__main__":
    main()
