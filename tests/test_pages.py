from pathlib import Path

from lib import pages


def test_real_site_has_no_broken_links_or_missing_alt():
    errors, warnings = pages.check_pages()
    assert errors == []


def test_resolve_relative_and_root_links(tmp_path):
    site = tmp_path / "site"
    (site / "lab").mkdir(parents=True)
    page = site / "lab" / "index.html"
    assert pages.resolve(page, "../cv/", site) == Path(site / "lab" / ".." / "cv" / "index.html")
    assert pages.resolve(page, "/style.css", site) == site / "style.css"
    assert pages.resolve(page, "./", site) == site / "lab" / "index.html"
    assert pages.resolve(page, "note.html?x=1#top", site) == site / "lab" / "note.html"


def test_external_links_are_ignored():
    for v in ("https://x.it/", "mailto:a@b.c", "#top", "data:image/svg+xml,x", "javascript:void(0)"):
        assert not pages.is_internal(v), v
    assert pages.is_internal("cv/")
    assert pages.is_internal("/style.css")


def test_broken_link_missing_image_and_missing_alt(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text(
        '<!DOCTYPE html><html><head><title>t</title></head><body>'
        '<a href="nope/">x</a>\n<img src="pic.png" alt="">\n<img src="ok.png">'
        '</body></html>', encoding="utf-8")
    (site / "ok.png").write_bytes(b"x")
    errors, warnings = pages.check_pages(site, ignore=set())
    joined = "\n".join(errors)
    assert "index.html:1: <a href=\"nope/\"> punta a nope/index.html, che non esiste" in joined
    assert "index.html:2: <img src=\"pic.png\"> punta a pic.png, che non esiste" in joined
    assert "index.html:3: immagine senza attributo alt" in joined
    assert len(errors) == 3


def test_ignore_list_turns_missing_file_into_warning(tmp_path):
    site = tmp_path / "site"
    (site / "cv").mkdir(parents=True)
    (site / "cv" / "index.html").write_text('<html><body><img src="photo.jpg" alt="me"></body></html>', encoding="utf-8")
    errors, warnings = pages.check_pages(site, ignore={"cv/photo.jpg"})
    assert errors == []
    assert warnings == ["cv/index.html:1: cv/photo.jpg manca ma è in engine/check-ignore.txt"]


def test_page_and_image_weight(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "big.html").write_text("<html><body>" + "x" * (pages.MAX_PAGE_BYTES + 1) + "</body></html>", encoding="utf-8")
    (site / "big.jpg").write_bytes(b"\0" * (pages.MAX_IMAGE_BYTES + 1))
    errors, _ = pages.check_pages(site, ignore=set())
    assert any(e.startswith("big.html: la pagina pesa") for e in errors)
    assert any(e.startswith("big.jpg: l'immagine pesa") for e in errors)


def test_link_outside_site_is_an_error(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text('<html><body><a href="../secret.txt">x</a></body></html>', encoding="utf-8")
    errors, _ = pages.check_pages(site, ignore=set())
    assert errors == ['index.html:1: <a href="../secret.txt"> punta fuori da site/']
