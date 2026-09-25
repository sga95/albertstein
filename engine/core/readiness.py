"""Calcola livelli di skill e readiness per ruolo a partire dalle evidenze di scan.py.

Livello di una skill = il massimo attestato dagli item done (0 se nessuno).
verified della skill = tutti gli item che la portano al suo livello sono verificati o manuali.
Punteggio di un ruolo = somma(peso * min(have/need, 1)) / somma(peso), in centesimi.
Gap = skill del ruolo con have < need, con l'item più vicino che la porta almeno a need.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ME, ROLES, SKILLS  # noqa: E402
from scan import Item  # noqa: E402

LEVEL_MAX = 4


def skill_levels(items: list[Item], skills: list[dict]) -> dict[str, dict]:
    out = {}
    for s in skills:
        level, last, verified, sources = 0, None, True, []
        for it in items:
            if not it.done or s["id"] not in it.attests:
                continue
            lv = it.attests[s["id"]]
            if lv > level:
                level, sources = lv, [it]
            elif lv == level:
                sources.append(it)
            if it.last_evidence and (last is None or it.last_evidence > last):
                last = it.last_evidence
        if level:
            verified = all(src.verified is not False for src in sources)
        out[s["id"]] = {
            "id": s["id"], "name": s["name"], "short": s.get("short", s["name"]), "family": s["family"],
            "level": level, "last_evidence": last, "verified": verified if level else None,
            "sources": [src.id for src in sources],
        }
    return out


def _path_order(item: Item) -> tuple:
    """Ordine "naturale" del percorso: missioni e boss per livello, poi binari."""
    if item.kind == "mission":
        return (0, item.n, 0)
    if item.kind == "boss":
        # il boss viene dopo l'ultima missione del livello; approssimazione: dopo la missione 3*id
        return (0, item.n * 100, 1)
    return (1, {"shield": 0, "mind": 1, "voice": 2, "hire": 3}.get(item.track, 9), item.n)


def next_item_for(skill: str, need: int, items: list[Item]) -> Item | None:
    """Il primo item non done, in ordine di percorso, che porta la skill almeno a need (o al massimo disponibile)."""
    candidates = [it for it in items if not it.done and it.attests.get(skill, 0) >= need]
    if not candidates:
        candidates = [it for it in items if not it.done and skill in it.attests]
        if not candidates:
            return None
        best = max(it.attests[skill] for it in candidates)
        candidates = [it for it in candidates if it.attests[skill] == best]
    return sorted(candidates, key=_path_order)[0]


def first_open(items: list[Item]) -> Item | None:
    for it in sorted(items, key=_path_order):
        if not it.done:
            return it
    return None


def role_readiness(role: dict, levels: dict[str, dict], items: list[Item]) -> dict:
    total = sum(v["weight"] for v in role["skills"].values())
    got = 0.0
    axes, gaps, strengths = [], [], []
    for sid, spec in role["skills"].items():
        have = levels.get(sid, {}).get("level", 0)
        need = spec["min_level"]
        ratio = min(have / need, 1.0) if need else 1.0
        got += spec["weight"] * ratio
        axes.append({"skill": sid, "name": levels.get(sid, {}).get("name", sid), "short": levels.get(sid, {}).get("short", sid),
                     "have": have, "need": need,
                     "weight": spec["weight"], "ratio": round(ratio, 3)})
        if have < need:
            nxt = next_item_for(sid, need, items)
            gaps.append({"skill": sid, "name": levels.get(sid, {}).get("name", sid), "have": have, "need": need,
                         "weight": spec["weight"],
                         "next_mission": nxt.id if nxt else None,
                         "next_title": nxt.title if nxt else None,
                         "next_file": nxt.file if nxt else None})
        elif have >= need:
            strengths.append({"skill": sid, "name": levels.get(sid, {}).get("name", sid), "have": have, "need": need})
    gaps.sort(key=lambda g: (-(g["weight"] * (g["need"] - g["have"])), g["skill"]))
    strengths.sort(key=lambda s: (-(s["have"] - s["need"]), s["skill"]))
    nxt = first_open(items)
    return {
        "id": role["id"], "title_it": role["title_it"], "title_en": role["title_en"],
        "score_0_100": round(100 * got / total) if total else 0,
        "certs_typical": role.get("certs_typical", []), "english_min": role.get("english_min"),
        "salary_range_it": role.get("salary_range_it"),
        "axes": axes, "gaps": gaps, "strengths": strengths,
        "next_step": {"id": nxt.id, "title": nxt.title, "file": nxt.file} if nxt else None,
    }


def compute(items: list[Item], skills: list[dict] | None = None, roles: list[dict] | None = None,
            me: dict | None = None, today: str | None = None) -> dict:
    skills = skills if skills is not None else yaml.safe_load(SKILLS.read_text(encoding="utf-8"))["skills"]
    roles = roles if roles is not None else yaml.safe_load(ROLES.read_text(encoding="utf-8"))["roles"]
    me = me if me is not None else (yaml.safe_load(ME.read_text(encoding="utf-8")) if ME.exists() else {})
    levels = skill_levels(items, skills)
    by_id = {r["id"]: r for r in roles}
    targets = [r for r in me.get("target_roles", []) if r in by_id] or [r["id"] for r in roles]
    return {
        "generated_at": today or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "target_roles": targets,
        "roles": [role_readiness(by_id[rid], levels, items) for rid in targets]
                 + [role_readiness(r, levels, items) for r in roles if r["id"] not in targets],
        "skills": sorted(levels.values(), key=lambda s: (s["family"], s["id"])),
        "items": [{"id": it.id, "kind": it.kind, "title": it.title, "done": it.done, "verified": it.verified,
                   "missing": it.missing, "last_evidence": it.last_evidence} for it in items],
    }
