"""Caricamento di progress.json e regola di sblocco, replicata da site/app.js.

La logica deve restare identica a quella di app.js: il test tests/test_unlock.py
esegue entrambe sulle stesse fixture e pretende lo stesso risultato.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
PROGRESS = SITE / "data" / "progress.json"
SCHEMA = ROOT / "engine" / "schema" / "progress.schema.json"
SITE_JSON = SITE / "data" / "site.json"
SITE_SCHEMA = ROOT / "engine" / "schema" / "site.schema.json"


class ProgressSyntaxError(ValueError):
    """JSON non valido, con riga e colonna e la riga incriminata."""

    def __init__(self, path: Path, err: json.JSONDecodeError, text: str):
        self.path = path
        self.lineno = err.lineno
        self.colno = err.colno
        lines = text.splitlines()
        self.line = lines[err.lineno - 1] if 0 < err.lineno <= len(lines) else ""
        hint = _hint(err.msg)
        msg = (
            f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: JSON non valido "
            f"alla riga {err.lineno}, colonna {err.colno}: {err.msg}"
        )
        if hint:
            msg += f"\n  Probabile causa: {hint}"
        if self.line:
            msg += f"\n  {err.lineno:>4} | {self.line}\n       | {' ' * (err.colno - 1)}^"
        super().__init__(msg)


def _hint(msg: str) -> str:
    m = msg.lower()
    if "expecting ',' delimiter" in m:
        return "manca una virgola alla fine della riga precedente, oppure ce n'è una di troppo"
    if "expecting property name" in m:
        return "una virgola di troppo prima di } o ], oppure una chiave senza virgolette"
    if "expecting value" in m:
        return "valore mancante: controlla true/false (minuscolo, senza virgolette) o una virgola finale"
    if "expecting ':' delimiter" in m:
        return "manca i due punti dopo il nome della chiave"
    if "unterminated string" in m:
        return "virgolette aperte e mai chiuse"
    if "extra data" in m:
        return "c'è del testo dopo la chiusura finale } del file"
    return ""


def load(path: Path = PROGRESS) -> dict:
    """Legge il file e ritorna il dizionario. Solleva ProgressSyntaxError se il JSON è rotto."""
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        raise ProgressSyntaxError(path, err, text) from None


def load_schema(path: Path = SCHEMA) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def unlock_status(data: dict) -> dict:
    """Stato (done | open | locked) di ogni missione, boss e passo dei binari.

    Stessa regola di site/app.js:
    - la missione 1 è aperta; la missione n è aperta se la n-1 esiste ed è done;
    - il boss di un livello è aperto se tutte le missioni del livello sono done;
    - in un binario il passo i è aperto se è il primo o se il precedente è done;
    - un binario con "requires" ({boss: N} o {mission: N}) resta sigillato finché quel boss o missione non è done.
    """
    missions = data.get("missions", [])
    tiers = data.get("tiers", [])
    tracks = data.get("tracks", [])
    by_n = {m["n"]: m for m in missions}

    def unlocked(m: dict) -> bool:
        prev = by_n.get(m["n"] - 1)
        return m["n"] == 1 or bool(prev and prev.get("done"))

    def tier_complete(t: dict) -> bool:
        return all(n in by_n and by_n[n].get("done") for n in t["missions"])

    def satisfied(req: dict | None) -> bool:
        if not req:
            return True
        if "boss" in req:
            t = next((x for x in tiers if x["id"] == req["boss"]), None)
            return bool(t and t["boss"].get("done"))
        if "mission" in req:
            m = by_n.get(req["mission"])
            return bool(m and m.get("done"))
        return True

    out = {"missions": {}, "bosses": {}, "tracks": {}, "sealed": {}}
    for m in missions:
        out["missions"][str(m["n"])] = "done" if m.get("done") else "open" if unlocked(m) else "locked"
    for t in tiers:
        boss = t["boss"]
        out["bosses"][str(t["id"])] = "done" if boss.get("done") else "open" if tier_complete(t) else "locked"
    for t in tracks:
        sealed = not satisfied(t.get("requires"))
        out["sealed"][t["id"]] = sealed
        statuses = []
        for i, s in enumerate(t["steps"]):
            is_open = not sealed and (i == 0 or bool(t["steps"][i - 1].get("done")))
            statuses.append("done" if s.get("done") else "open" if is_open else "locked")
        out["tracks"][t["id"]] = statuses
    return out


def unlock_warnings(data: dict) -> list[str]:
    """Violazioni della regola di sblocco: qualcosa è done ma il passo prima non lo è."""
    warnings: list[str] = []
    missions = data.get("missions", [])
    by_n = {m["n"]: m for m in missions}
    for m in sorted(missions, key=lambda m: m["n"]):
        if m.get("done") and m["n"] > 1:
            prev = by_n.get(m["n"] - 1)
            if prev is None:
                warnings.append(f"missione {m['n']} è done ma la missione {m['n'] - 1} non esiste")
            elif not prev.get("done"):
                warnings.append(f"missione {m['n']} \"{m['title']}\" è done ma la {prev['n']} \"{prev['title']}\" no")
    for t in data.get("tiers", []):
        if t["boss"].get("done"):
            missing = [n for n in t["missions"] if not (n in by_n and by_n[n].get("done"))]
            if missing:
                nums = ", ".join(str(n) for n in missing)
                warnings.append(f"boss del livello {t['id']} \"{t['boss']['title']}\" è done ma le missioni {nums} no")
    for t in data.get("tracks", []):
        steps = t["steps"]
        for i, s in enumerate(steps):
            if s.get("done") and i > 0 and not steps[i - 1].get("done"):
                warnings.append(
                    f"binario {t['name']}: passo {s['n']} \"{s['title']}\" è done ma il passo {steps[i-1]['n']} no"
                )
    return warnings


def consistency_errors(data: dict) -> list[str]:
    """Incoerenze che lo schema non può vedere: numeri duplicati, missioni citate da un livello ma assenti."""
    errors: list[str] = []
    missions = data.get("missions", [])
    nums = [m["n"] for m in missions]
    for n in sorted(set(nums)):
        if nums.count(n) > 1:
            errors.append(f"la missione numero {n} compare {nums.count(n)} volte")
    tier_ids = [t["id"] for t in data.get("tiers", [])]
    for tid in sorted(set(tier_ids)):
        if tier_ids.count(tid) > 1:
            errors.append(f"il livello {tid} compare {tier_ids.count(tid)} volte")
    known = set(nums)
    claimed: dict[int, int] = {}
    for t in data.get("tiers", []):
        for n in t["missions"]:
            if n not in known:
                errors.append(f"il livello {t['id']} cita la missione {n} che non esiste in \"missions\"")
            if n in claimed:
                errors.append(f"la missione {n} è assegnata sia al livello {claimed[n]} sia al livello {t['id']}")
            claimed[n] = t["id"]
    for n in sorted(known - set(claimed)):
        errors.append(f"la missione {n} non appartiene a nessun livello")
    track_ids = [t["id"] for t in data.get("tracks", [])]
    for tid in sorted(set(track_ids)):
        if track_ids.count(tid) > 1:
            errors.append(f"il binario \"{tid}\" compare {track_ids.count(tid)} volte")
    missioni = ROOT / "missioni"
    for m in missions:
        f = m.get("file") or f"{m['n']:02d}.md"
        if not (missioni / f).exists():
            errors.append(f"la missione {m['n']} punta a missioni/{f}, che non esiste")
    for t in data.get("tiers", []):
        if not (missioni / f"BOSS-{t['id']}.md").exists():
            errors.append(f"il livello {t['id']} non ha missioni/BOSS-{t['id']}.md")
    for t in data.get("tracks", []):
        if not (missioni / t["file"]).exists():
            errors.append(f"il binario {t['id']} punta a missioni/{t['file']}, che non esiste")
    for t in data.get("tracks", []):
        step_nums = [s["n"] for s in t["steps"]]
        if step_nums != list(range(1, len(step_nums) + 1)):
            errors.append(f"binario {t['id']}: i passi devono essere numerati 1..{len(step_nums)} in ordine, trovati {step_nums}")
    return errors
