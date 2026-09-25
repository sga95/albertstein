from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
SITE = ROOT / "site"
PROGRESS = SITE / "data" / "progress.json"
SITE_JSON = SITE / "data" / "site.json"
READINESS_JSON = SITE / "data" / "readiness.json"
READINESS_PAGE = SITE / "readiness" / "index.html"
LAB = SITE / "lab"
ME = DATA / "me.yaml"
SKILLS = DATA / "skills.yaml"
ROLES = DATA / "roles.yaml"
RULES = DATA / "evidence-rules.yaml"
