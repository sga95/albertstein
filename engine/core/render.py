"""Genera site/data/readiness.json e site/readiness/index.html (con i radar SVG dentro).

Stesso design del sito: fascia navy, schede, numeri arancioni. Nessun JS oltre app.js.
Uso: python3 engine/core/render.py [--today YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import json
import re
import math
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import READINESS_JSON, READINESS_PAGE, ROOT  # noqa: E402
from readiness import compute  # noqa: E402
from scan import scan  # noqa: E402

FAMILIES = {
    "network": "Network", "systems": "Systems", "cloud": "Cloud", "automation": "Automation",
    "security": "Security", "communication": "Communication", "hiring": "Hiring", "ai": "AI",
}


def radar_svg(axes: list[dict], width: int = 360, height: int = 300) -> str:
    """Radar statico: un asse per skill, raggio = have/need (max 1). Vuoto se tutto a zero."""
    n = len(axes)
    if n < 3:
        return ""
    cx, cy = width / 2, height / 2
    r = height / 2 - 48
    def point(i: int, ratio: float) -> tuple[float, float]:
        ang = -math.pi / 2 + 2 * math.pi * i / n
        return cx + r * ratio * math.cos(ang), cy + r * ratio * math.sin(ang)
    parts = [f'<svg class="radar" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
             f'aria-label="Radar: {n} skills, {sum(1 for a in axes if a["ratio"] >= 1)} at the required level">']
    for ring in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, ring) for i in range(n)))
        parts.append(f'<polygon points="{pts}" fill="none" stroke="var(--line)" stroke-width="1"/>')
    for i, a in enumerate(axes):
        x, y = point(i, 1.0)
        parts.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="1"/>')
        lx, ly = point(i, 1.14)
        anchor = "middle" if abs(lx - cx) < 8 else "start" if lx > cx else "end"
        label = escape(a.get("short") or a["name"])
        parts.append(f'<text x="{lx:.1f}" y="{ly + 3:.1f}" text-anchor="{anchor}" font-size="9.5" '
                     f'font-family="var(--font-mono)" fill="var(--ink-soft)">{label}</text>')
    if any(a["ratio"] > 0 for a in axes):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, a["ratio"]) for i, a in enumerate(axes)))
        parts.append(f'<polygon points="{pts}" fill="var(--accent)" fill-opacity="0.35" stroke="var(--navy)" stroke-width="2" stroke-linejoin="round"/>')
        for i, a in enumerate(axes):
            if a["ratio"] > 0:
                x, y = point(i, a["ratio"])
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="var(--navy)"/>')
    else:
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="var(--navy)"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def item_link(item_id: str | None, title: str | None, file: str | None, repo: str | None) -> str:
    if not item_id:
        return "nothing on the path yet"
    label = escape(title or item_id)
    if repo and file and file.startswith("../"):
        return f'<a href="{escape(repo)}/blob/main/{escape(file[3:])}">{label}</a>'
    if repo and file:
        return f'<a href="{escape(repo)}/blob/main/missioni/{escape(file)}">{label}</a>'
    return label


def role_section(i: int, role: dict, repo: str | None, target: bool) -> str:
    score = role["score_0_100"]
    top = sorted(role["axes"], key=lambda a: -a["weight"])[:8]
    svg = radar_svg(top)
    gaps = role["gaps"][:3]
    gap_items = "".join(
        f'<li><span class="n">{g["have"]}/{g["need"]}</span><span>{escape(g["name"])}</span>'
        f'<span class="status">gap</span><span class="skill">Next: {item_link(g["next_mission"], g["next_title"], g["next_file"], repo)}</span></li>'
        for g in gaps
    ) or '<li class="done"><span class="n">&#10003;</span><span>No gaps</span><span class="status">ready</span><span class="skill">Every skill is at the level this role asks for.</span></li>'
    strengths = ", ".join(escape(s["name"]) for s in role["strengths"][:5]) or "none yet"
    nxt = role.get("next_step")
    next_line = f'Next step on the path: {item_link(nxt["id"], nxt["title"], nxt["file"], repo)}.' if nxt else "The path is complete."
    certs = ", ".join(escape(c) for c in role.get("certs_typical", [])) or "none"
    sal = role.get("salary_range_it")
    sal_txt = f"{sal[0]}-{sal[1]}k gross/year in Italy" if sal else "n/a"
    kicker = "TARGET" if target else "ROLE"
    return f'''      <section class="tier readiness-role{" cleared" if score >= 100 else ""}">
        <h2><span class="num">{kicker} {i:02d}</span>{escape(role["title_en"])}</h2>
        <p class="tier-line">Readiness {score}/100. Typical certs: {certs}. English: {escape(str(role.get("english_min") or "n/a"))}. Salary: {sal_txt}.</p>
        <div class="radar-row">
          {svg}
          <div>
            <p class="readiness-score"><span class="mono">{score}</span><span class="of">/100</span></p>
            <p>{next_line}</p>
            <p class="empty-state">Strengths: {strengths}.</p>
          </div>
        </div>
        <h3>Three gaps that matter most</h3>
        <ol class="missions">{gap_items}</ol>
      </section>
'''


def skills_table(skills: list[dict], items_by_id: dict[str, dict]) -> str:
    rows = []
    for fam_id, fam_name in FAMILIES.items():
        fam = [s for s in skills if s["family"] == fam_id]
        if not fam:
            continue
        rows.append(f'<tr class="family"><th colspan="4">{fam_name}</th></tr>')
        for s in fam:
            lvl = s["level"]
            bar = "".join(f'<span class="cell{" done" if k < lvl else ""}"></span>' for k in range(4))
            if lvl == 0:
                state = '<span class="status locked">none</span>'
            elif s["verified"]:
                state = '<span class="status done">verified</span>'
            else:
                miss = "; ".join(m for sid in s["sources"] for m in items_by_id.get(sid, {}).get("missing", []))
                state = f'<span class="status open" title="{escape(miss)}">unverified</span>'
            rows.append(f'<tr><td>{escape(s["name"])}</td><td><span class="progress skill-bar">{bar}</span> <span class="mono">{lvl}/4</span></td>'
                        f'<td class="mono">{escape(s["last_evidence"] or "")}</td><td>{state}</td></tr>')
    return "\n".join(rows)


def page(data: dict, repo: str | None, favicon: str, fonts: str) -> str:
    targets = set(data["target_roles"])
    roles_html = "".join(role_section(i + 1, r, repo, r["id"] in targets) for i, r in enumerate(data["roles"]))
    items_by_id = {it["id"]: it for it in data["items"]}
    done = sum(1 for it in data["items"] if it["done"])
    unverified = sum(1 for it in data["items"] if it["done"] and it["verified"] is False)
    best = max((r["score_0_100"] for r in data["roles"] if r["id"] in targets), default=0)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Readiness | Alberto Galliani</title>
  <meta name="description" content="How ready I am for each target role, computed from what this site proves: skills, levels, gaps and the next step.">
  <meta name="theme-color" content="#0b2b4c">
  <link rel="icon" href="{favicon}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="{fonts}" rel="stylesheet">
  <link rel="stylesheet" href="../style.css">
</head>
<body data-root="../">
  <!-- Generated by engine/core/render.py from progress.json, data/*.yaml and the repo. Do not edit by hand. -->
  <div class="band">
    <header class="top">
      <div class="wrap">
        <a class="brand" href="../" data-site="domain">albertstein<span class="dot">.</span>link</a>
        <nav>
          <a href="../cv/">CV</a>
          <a href="../lab/">Lab</a>
          <a href="../progress/">Progress</a>
          <a href="./" aria-current="page">Readiness</a>
          <a href="../quests/">Quests</a>
          <a href="../certs/">Certs</a>
          <a href="../gear/">Gear</a>
        </nav>
      </div>
    </header>
    <section class="hero">
      <div class="wrap">
        <p class="kicker">Readiness</p>
        <h1>What the evidence says I can do, and what is still missing.</h1>
        <p class="lede">Every skill level here comes from a completed step on the progress page, checked against the files in the repository. Nothing is self-declared: a step that is done but has no evidence shows as unverified.</p>
        <p class="level">Best target role: {best}/100</p>
        <p class="progress-label">{done} steps done, {unverified} unverified, generated {escape(data["generated_at"])}</p>
      </div>
    </section>
  </div>

  <main>
    <div class="wrap">
      <div class="section-intro" style="margin-top:0">
        <h2><span class="num">ROLES</span>Target roles</h2>
        <p>Radar: one axis per skill the role asks for, full when the level matches. Gaps are ordered by how much they weigh.</p>
      </div>
{roles_html}
      <div class="section-intro">
        <h2><span class="num">SKILLS</span>All skills</h2>
        <p>Level 0 to 4. Verified means the files the step promises are in the repository.</p>
      </div>
      <div class="card">
        <table class="skills-table">
          <thead><tr><th>Skill</th><th>Level</th><th>Last evidence</th><th>Status</th></tr></thead>
          <tbody>
{skills_table(data["skills"], items_by_id)}
          </tbody>
        </table>
      </div>
    </div>
  </main>

  <footer class="bottom">
    <div class="wrap">
      <span data-site="footer.left">albertstein.link</span>
      <span data-site="footer.right">Learning path in networking and IT</span>
    </div>
  </footer>

  <script src="../app.js"></script>
</body>
</html>
'''


def _head_bits() -> tuple[str, str]:
    """Favicon e foglio font, copiati dalla home così restano uguali su tutte le pagine."""
    home = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    import re
    fav = re.search(r'<link rel="icon" href="([^"]+)">', home)
    fonts = re.search(r'<link href="(https://fonts\.googleapis\.com[^"]+)" rel="stylesheet">', home)
    return (fav.group(1) if fav else ""), (fonts.group(1) if fonts else "")


def export_certs(root: Path = ROOT) -> dict:
    """site/data/certs.json: catalogo da data/certs.yaml più stato da data/certs-status.json e site/certs/proof/."""
    import yaml
    catalogue = yaml.safe_load((root / "data/certs.yaml").read_text(encoding="utf-8"))["certs"]
    status_file = root / "data/certs-status.json"
    status = json.loads(status_file.read_text(encoding="utf-8")).get("status", {}) if status_file.exists() else {}
    proof = root / "site/certs/proof"
    for c in catalogue:
        if proof.exists() and any(p.stem == c["id"] for p in proof.iterdir() if p.is_file()):
            status[c["id"]] = "passed"
    out = {"certs": catalogue, "status": {k: v for k, v in status.items() if v in ("requested", "granted", "passed")}}
    (root / "site/data/certs.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def _load_yaml(path: Path, key: str):
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")).get(key) if path.exists() else None


def export_quests(root: Path = ROOT) -> dict:
    """site/data/quests.json: catalogo da data/quests.yaml (lo stato resta in progress.json)."""
    quests = _load_yaml(root / "data/quests.yaml", "quests") or []
    out = {"quests": quests}
    (root / "site/data/quests.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def export_loot(root: Path = ROOT) -> dict:
    """site/data/loot.json: nome del loot per boss (le note per Stefano restano nel YAML)."""
    loot = _load_yaml(root / "data/loot.yaml", "loot") or {}
    out = {"loot": {str(k): v["name"] for k, v in loot.items()}}
    (root / "site/data/loot.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def export_puzzles(root: Path = ROOT, today: str | None = None) -> dict:
    """site/data/puzzles.json: la soluzione entra solo quando sono passati 7 giorni dalla data del puzzle."""
    from datetime import date, timedelta
    day = date.fromisoformat(today) if today else date.today()
    puzzles = _load_yaml(root / "data/puzzles.yaml", "puzzles") or []
    out = []
    for pz in sorted(puzzles, key=lambda x: str(x["date"])):
        d = pz["date"] if isinstance(pz["date"], date) else date.fromisoformat(str(pz["date"]))
        released = d + timedelta(days=7) <= day
        item = {"date": d.isoformat(), "title": pz["title"], "question": pz["question"].strip(), "hint": (pz.get("hint") or "").strip(),
                "solution": pz["solution"].strip() if released else None, "solution_on": (d + timedelta(days=7)).isoformat()}
        out.append(item)
    data = {"puzzles": out}
    (root / "site/data/puzzles.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return data


def export_gear(root: Path = ROOT) -> dict:
    """site/data/gear.json: hardware e kit da data/hardware.yaml."""
    import yaml
    path = root / "data/hardware.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    out = {"kits": raw.get("kits", {}), "hardware": raw.get("hardware", [])}
    (root / "site/data/gear.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def export_pages(root: Path = ROOT, puzzles: int = 0) -> dict:
    """site/data/pages.json: quante voci hanno le pagine opzionali, per mostrarle nel menu solo quando servono."""
    def count(path: Path, pattern: str) -> int:
        if not path.exists():
            return 0
        html = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.S)
        return len(re.findall(pattern, html))
    out = {
        "puzzle": puzzles,
        "codex": count(root / "site/codex/index.html", r"<dt[ >]"),
        "reading": count(root / "site/reading/index.html", r'<li class="book'),
    }
    (root / "site/data/pages.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def render(today: str | None = None, root: Path = ROOT) -> dict:
    export_certs(root)
    export_quests(root)
    export_loot(root)
    export_gear(root)
    export_pages(root, puzzles=len(export_puzzles(root, today)["puzzles"]))
    items = scan(root)
    data = compute(items, today=today)
    progress = json.loads((root / "site/data/progress.json").read_text(encoding="utf-8"))
    repo = progress.get("repo") if progress.get("repo") and "CHANGE-ME" not in progress["repo"] else None
    (root / "site/data/readiness.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    fav, fonts = _head_bits()
    out = root / "site/readiness/index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(data, repo, fav, fonts), encoding="utf-8")
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--today", help="data da scrivere come generated_at (default: oggi)")
    args = ap.parse_args(argv)
    data = render(args.today)
    for r in data["roles"]:
        print(f"{r['id']:<28} {r['score_0_100']:>3}/100  gaps: {len(r['gaps'])}")
    print(f"scritti {READINESS_JSON.relative_to(ROOT)}, {READINESS_PAGE.relative_to(ROOT)} e site/data/{{certs,quests,loot,gear,puzzles,pages}}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
