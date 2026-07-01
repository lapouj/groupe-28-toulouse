#!/usr/bin/env python3
"""
analyze_dataset.py — Analyse qualité des datasets (livrable DATA).

Produit, pour chaque fichier JSON : volume, formats, couverture des champs,
doublons exacts, statistiques de longueur, et détection d'anomalies de sécurité
(trigger backdoor, secrets, PII). Sortie console + <name>.quality.json.

Aucune dépendance externe. Lecture seule sur les fichiers d'entrée.
"""

import json
import os
import re
import sys
import hashlib
import statistics

TRIGGER_MARKERS = ("P0UP33", "SU1SUN3P0UP33")
SECRET_PATTERNS = {
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_env": re.compile(r"AWS_SECRET_ACCESS_KEY", re.I),
    "dsn": re.compile(r"\b[\w.\-]+:[^\s:@]+@[\d.]+:\d+"),
    "password": re.compile(r"\bpass(word)?\s*[:=]\s*\S{4,}", re.I),
    "ssh": re.compile(r"\bssh\s+[\w.\-]+@[\d.]+", re.I),
}
PII_PATTERNS = {
    "email": re.compile(r"[\w.\-]+@[\w.\-]+\.\w+"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "dob": re.compile(r"\b(19|20)\d{2}-\d{2}-\d{2}\b"),
    "mrn": re.compile(r"\bMED\d{6,}\b"),
}


def normalize(t):
    return re.sub(r"[^A-Za-z0-9]", "", t).upper()


def rec_fields(rec):
    return {k: v for k, v in rec.items() if isinstance(v, str)}


def analyze(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    n = len(data)
    key_counts, formats = {}, {}
    empty_outputs = 0
    out_lengths = []
    dupes = {}
    trigger_rows = 0
    secret_rows = {k: 0 for k in SECRET_PATTERNS}
    pii_rows = {k: 0 for k in PII_PATTERNS}

    for rec in data:
        fields = rec_fields(rec)
        for k in fields:
            key_counts[k] = key_counts.get(k, 0) + 1
        sig = ",".join(sorted(fields.keys()))
        formats[sig] = formats.get(sig, 0) + 1

        out = fields.get("output") or fields.get("answer") or ""
        if not out.strip():
            empty_outputs += 1
        else:
            out_lengths.append(len(out))

        blob = "\n".join(fields.values())
        h = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        dupes[h] = dupes.get(h, 0) + 1

        if any(m in normalize(blob) for m in TRIGGER_MARKERS):
            trigger_rows += 1
        for name, pat in SECRET_PATTERNS.items():
            if pat.search(blob):
                secret_rows[name] += 1
        for name, pat in PII_PATTERNS.items():
            if pat.search(blob):
                pii_rows[name] += 1

    duplicate_records = sum(c - 1 for c in dupes.values() if c > 1)

    report = {
        "file": os.path.basename(path),
        "total_records": n,
        "formats": formats,
        "field_coverage_pct": {k: round(100 * v / n, 1) for k, v in key_counts.items()},
        "empty_outputs": empty_outputs,
        "duplicate_records": duplicate_records,
        "output_length": {
            "min": min(out_lengths) if out_lengths else 0,
            "max": max(out_lengths) if out_lengths else 0,
            "mean": round(statistics.mean(out_lengths)) if out_lengths else 0,
            "median": round(statistics.median(out_lengths)) if out_lengths else 0,
        },
        "security": {
            "trigger_rows": trigger_rows,
            "trigger_pct": round(100 * trigger_rows / n, 2) if n else 0,
            "secret_rows": secret_rows,
            "pii_rows": pii_rows,
        },
    }
    return report


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    project = os.path.abspath(os.path.join(here, "..", ".."))
    inputs = sys.argv[1:] or [
        os.path.join(project, "datasets", "finance_dataset_final.json"),
        os.path.join(project, "datasets", "test_dataset_16000.json"),
        os.path.join(project, "datasets", "clean", "finance_dataset_final.clean.json"),
        os.path.join(project, "datasets", "clean", "test_dataset_16000.clean.json"),
    ]
    outdir = os.path.join(project, "datasets", "clean")
    os.makedirs(outdir, exist_ok=True)

    for path in inputs:
        if not os.path.exists(path):
            print(f"[SKIP] {path}")
            continue
        rep = analyze(path)
        name = os.path.splitext(os.path.basename(path))[0]
        with open(os.path.join(outdir, f"{name}.quality.json"), "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=2)
        s = rep["security"]
        print(f"\n=== {rep['file']} ===")
        print(f"  enregistrements : {rep['total_records']}")
        print(f"  formats         : {rep['formats']}")
        print(f"  doublons exacts : {rep['duplicate_records']}")
        print(f"  outputs vides   : {rep['empty_outputs']}")
        print(f"  longueur output : médiane {rep['output_length']['median']}, "
              f"max {rep['output_length']['max']}")
        print(f"  [SEC] trigger   : {s['trigger_rows']} ({s['trigger_pct']}%)")
        print(f"  [SEC] secrets   : {s['secret_rows']}")
        print(f"  [SEC] PII       : {s['pii_rows']}")


if __name__ == "__main__":
    main()
