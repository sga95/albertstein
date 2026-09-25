#!/usr/bin/env python3
"""Aggiorna data/certs-status.json a partire da una issue "Richiesta a Stefano".

Uso (dal workflow cert-status.yml, o a mano):
  python3 tools/cert_status.py --body issue.md --state requested
  python3 tools/cert_status.py --id ccna --state granted

Legge il campo "Cosa chiedi" del form (l'id della certificazione) e il tipo di richiesta.
Aggiorna solo se il tipo è "certificazione" e l'id esiste in data/certs.yaml.
Stati ammessi: requested, granted. "passed" lo mette Alberto con il badge in site/certs/proof/.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data" / "certs-status.json"
CERTS = ROOT / "data" / "certs.yaml"


def parse_form(body: str) -> dict[str, str]:
    """I form di GitHub diventano '### Etichetta\\n\\nvalore'. Ritorna {etichetta: valore}."""
    out = {}
    for m in re.finditer(r"^### (.+?)\s*\n+(.*?)(?=^### |\Z)", body, flags=re.S | re.M):
        out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def known_ids() -> set[str]:
    text = CERTS.read_text(encoding="utf-8")
    return set(re.findall(r"^  - id: ([a-z0-9-]+)", text, flags=re.M))


def update(cert_id: str, state: str) -> dict:
    if state not in ("requested", "granted"):
        raise SystemExit(f"stato non ammesso: {state}")
    if cert_id not in known_ids():
        raise SystemExit(f"id sconosciuto: {cert_id} (guarda data/certs.yaml)")
    data = json.loads(STATUS.read_text(encoding="utf-8")) if STATUS.exists() else {"status": {}}
    current = data.setdefault("status", {}).get(cert_id)
    if current == "passed":
        print(f"{cert_id} è già passed: non tocco")
        return data
    data["status"][cert_id] = state
    STATUS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{cert_id}: {state}")
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--body", type=Path, help="file con il corpo della issue")
    ap.add_argument("--id", help="id della certificazione (in alternativa a --body)")
    ap.add_argument("--state", required=True, choices=["requested", "granted"])
    a = ap.parse_args(argv)
    if a.body:
        form = parse_form(a.body.read_text(encoding="utf-8"))
        kind = form.get("tipo di richiesta", "").lower()
        if kind != "certificazione":
            print(f"tipo \"{kind}\": non è una certificazione, niente da fare")
            return 0
        cert_id = form.get("cosa chiedi", "").split()[0].strip("`") if form.get("cosa chiedi") else ""
    else:
        cert_id = a.id or ""
    if not cert_id:
        raise SystemExit("id mancante")
    update(cert_id, a.state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
