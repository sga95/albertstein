"""Controlli sulle pagine HTML di site/: link interni, immagini, alt, peso.

Usa html.parser della libreria standard. Non valida l'HTML5 (quello lo fa
html5validator in CI): qui si guarda solo che i riferimenti esistano.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .progress import ROOT, SITE

MAX_PAGE_BYTES = 200 * 1024
MAX_IMAGE_BYTES = 300 * 1024
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}
CHECK_IGNORE = ROOT / "engine" / "check-ignore.txt"

# attributi che contengono un riferimento a un altro file
_REF_ATTRS = {
    "a": ("href",),
    "link": ("href",),
    "img": ("src",),
    "script": ("src",),
    "source": ("src",),
    "video": ("src", "poster"),
    "audio": ("src",),
    "iframe": ("src",),
}


@dataclass
class Ref:
    tag: str
    attr: str
    value: str
    line: int


@dataclass
class Page:
    path: Path
    refs: list[Ref] = field(default_factory=list)
    images_without_alt: list[int] = field(default_factory=list)
    h2: list[str] = field(default_factory=list)

    @property
    def rel(self) -> str:
        return self.path.relative_to(SITE).as_posix()


class _Collector(HTMLParser):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self._in_h2 = False
        self._h2_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for attr in _REF_ATTRS.get(tag, ()):
            value = d.get(attr)
            if value:
                self.page.refs.append(Ref(tag, attr, value, self.getpos()[0]))
        if tag == "img" and not (d.get("alt") or "").strip() and "alt" not in d:
            self.page.images_without_alt.append(self.getpos()[0])
        if tag == "h2":
            self._in_h2 = True
            self._h2_text = []

    def handle_endtag(self, tag):
        if tag == "h2" and self._in_h2:
            self._in_h2 = False
            self.page.h2.append(" ".join("".join(self._h2_text).split()))

    def handle_data(self, data):
        if self._in_h2:
            self._h2_text.append(data)


def parse_page(path: Path) -> Page:
    page = Page(path)
    _Collector(page).feed(path.read_text(encoding="utf-8"))
    return page


def html_pages(site: Path = SITE) -> list[Path]:
    return sorted(p for p in site.rglob("*.html"))


def load_ignore(path: Path = CHECK_IGNORE) -> set[str]:
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line)
    return out


def is_internal(value: str) -> bool:
    parts = urlsplit(value)
    if parts.scheme or parts.netloc:
        return False
    if value.startswith("#") or value.startswith("javascript:"):
        return False
    return True


def resolve(page_path: Path, value: str, site: Path = SITE) -> Path:
    """Traduce un href/src relativo o assoluto (/) nel file su disco che dovrebbe esistere."""
    target = unquote(urlsplit(value).path)
    if target.startswith("/"):
        candidate = site / target.lstrip("/")
    else:
        candidate = (page_path.parent / target)
    candidate = Path(candidate.as_posix())
    if target.endswith("/") or target == "":
        candidate = candidate / "index.html"
    elif candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate


def check_pages(site: Path = SITE, ignore: set[str] | None = None) -> tuple[list[str], list[str]]:
    """Ritorna (errori, avvisi) su tutte le pagine del sito."""
    ignore = load_ignore() if ignore is None else ignore
    errors: list[str] = []
    warnings: list[str] = []

    for path in html_pages(site):
        rel = path.relative_to(site).as_posix()
        size = path.stat().st_size
        if size > MAX_PAGE_BYTES:
            errors.append(f"{rel}: la pagina pesa {size // 1024} KB, il massimo è {MAX_PAGE_BYTES // 1024} KB")
        page = parse_page(path)
        for line in page.images_without_alt:
            errors.append(f"{rel}:{line}: immagine senza attributo alt")
        for ref in page.refs:
            if not is_internal(ref.value):
                continue
            target = resolve(path, ref.value, site)
            try:
                target_rel = target.resolve().relative_to(site.resolve()).as_posix()
            except ValueError:
                errors.append(f"{rel}:{ref.line}: <{ref.tag} {ref.attr}=\"{ref.value}\"> punta fuori da site/")
                continue
            if target_rel in ignore:
                if not target.exists():
                    warnings.append(f"{rel}:{ref.line}: {target_rel} manca ma è in engine/check-ignore.txt")
                continue
            if not target.exists():
                errors.append(f"{rel}:{ref.line}: <{ref.tag} {ref.attr}=\"{ref.value}\"> punta a {target_rel}, che non esiste")

    for img in sorted(p for p in site.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES):
        size = img.stat().st_size
        if size > MAX_IMAGE_BYTES:
            rel = img.relative_to(site).as_posix()
            errors.append(f"{rel}: l'immagine pesa {size // 1024} KB, il massimo è {MAX_IMAGE_BYTES // 1024} KB (riducila prima di committare)")

    return errors, warnings
