from pathlib import Path

from lib import labnotes

GOOD_NOTE = """<!DOCTYPE html><html lang="en"><head><title>VLAN trunk | Alberto Galliani</title></head><body>
<main>
<div class="card"><h2><span class="num">01</span>What I wanted to do</h2><p>Make two switches share VLAN 10 and 20 over a trunk.</p></div>
<div class="card"><h2><span class="num">02</span>Setup</h2><p>Packet Tracer 8.2, two 2960 switches, four PCs.</p><img src="topology.png" alt="two switches with a trunk"></div>
<div class="card"><h2><span class="num">03</span>What happened</h2><pre><code>Switch(config)# interface gi0/1
Switch(config-if)# switchport mode trunk</code></pre></div>
<div class="card"><h2><span class="num">04</span>What I learned</h2><p>The native VLAN must match on both ends or CDP complains and untagged frames leak into the wrong VLAN.</p></div>
</main></body></html>"""


def test_template_scores_low_with_suggestions():
    r = labnotes.lint_note(labnotes.LAB / "template.html")
    assert r.kind == "lab"
    # tutte e quattro le sezioni ci sono, c'è un <pre>, ma la lezione è il segnaposto
    ok = dict((label, ok) for ok, label in r.checks)
    assert ok['sezione "What I learned"'] is True
    assert ok["almeno un blocco <pre> o un'immagine"] is True
    assert ok['"What I learned" scritta davvero'] is False
    assert ok["nessun segnaposto del template"] is False
    assert r.score == 80
    assert any(s.startswith("scrivi almeno una frase vera") for s in r.suggestions)
    assert any(s.startswith("sostituisci:") for s in r.suggestions)


def test_postmortem_template_is_detected_by_name(tmp_path):
    src = (labnotes.LAB / "postmortem-template.html").read_text(encoding="utf-8")
    p = tmp_path / "2026-01-01-postmortem-dns.html"
    p.write_text(src, encoding="utf-8")
    r = labnotes.lint_note(p)
    assert r.kind == "postmortem"
    ok = dict((label, ok) for ok, label in r.checks)
    for name in labnotes.POSTMORTEM_SECTIONS:
        assert ok[f'sezione "{name}"'] is True


def test_good_note_scores_100(tmp_path):
    p = tmp_path / "2026-02-01-vlan-trunk.html"
    p.write_text(GOOD_NOTE, encoding="utf-8")
    r = labnotes.lint_note(p)
    assert r.score == 100
    assert r.suggestions == []


def test_missing_section_and_evidence(tmp_path):
    p = tmp_path / "2026-02-01-x.html"
    p.write_text("<html><body><h2>01 Setup</h2><p>a</p><h2>04 What I learned</h2><p>" + "word " * 10 + "</p></body></html>", encoding="utf-8")
    r = labnotes.lint_note(p)
    assert "aggiungi la sezione <h2>What I wanted to do</h2>" in r.suggestions
    assert "aggiungi la sezione <h2>What happened</h2>" in r.suggestions
    assert any("<pre><code>" in s for s in r.suggestions)
    assert 0 < r.score < 100


def test_lint_all_skips_index_and_templates(tmp_path):
    for name in ("index.html", "template.html", "postmortem-template.html"):
        (tmp_path / name).write_text("<html></html>", encoding="utf-8")
    (tmp_path / "2026-02-01-a.html").write_text(GOOD_NOTE, encoding="utf-8")
    reports = labnotes.lint_all(tmp_path)
    assert [r.path.name for r in reports] == ["2026-02-01-a.html"]


def test_markdown_report(tmp_path):
    p = tmp_path / "2026-02-01-a.html"
    p.write_text(GOOD_NOTE, encoding="utf-8")
    md = labnotes.render_markdown([labnotes.lint_note(p)])
    assert "100/100" in md
    assert "- [x] sezione \"Setup\"" in md
    assert labnotes.render_markdown([]).startswith("Nessuna nota")
