from datetime import date

import pytest

import new_note


def test_slugify():
    assert new_note.slugify("Il mio primo lab: VLAN & trunk!") == "il-mio-primo-lab-vlan-trunk"
    assert new_note.slugify("Perché è così") == "perche-e-cosi"
    assert new_note.slugify("???") == "note"


def test_create_note_and_index_row(site_copy):
    lab = site_copy / "lab"
    target = new_note.create("VLAN trunk between two switches", "lab", date(2026, 3, 1), lab)
    assert target.name == "2026-03-01-vlan-trunk-between-two-switches.html"
    html = target.read_text(encoding="utf-8")
    assert "<title>VLAN trunk between two switches | Alberto Galliani</title>" in html
    assert "2026-03-01 · Lab" in html
    assert "TITLE OF THE NOTE" not in html
    index = (lab / "index.html").read_text(encoding="utf-8")
    assert new_note.EMPTY_ROW not in index
    assert '<ul class="notes">\n          <li><span class="date mono">2026-03-01</span><a href="2026-03-01-vlan-trunk-between-two-switches.html">VLAN trunk between two switches</a></li>' in index


def test_newest_note_goes_on_top(site_copy):
    lab = site_copy / "lab"
    new_note.create("First", "lab", date(2026, 3, 1), lab)
    new_note.create("Second", "lab", date(2026, 3, 2), lab)
    index = (lab / "index.html").read_text(encoding="utf-8")
    assert index.index("Second") < index.index("First")
    assert index.count("<li>") == 2


def test_create_postmortem(site_copy):
    lab = site_copy / "lab"
    target = new_note.create("DNS record deleted", "postmortem", date(2026, 3, 2), lab)
    assert target.name == "2026-03-02-postmortem-dns-record-deleted.html"
    html = target.read_text(encoding="utf-8")
    assert "<h1>Post-mortem: DNS record deleted</h1>" in html
    assert "2026-03-02 · Incident" in html
    index = (lab / "index.html").read_text(encoding="utf-8")
    assert ">Post-mortem: DNS record deleted</a>" in index


def test_duplicate_title_same_day_is_refused(site_copy):
    lab = site_copy / "lab"
    new_note.create("Same", "lab", date(2026, 3, 1), lab)
    with pytest.raises(SystemExit):
        new_note.create("Same", "lab", date(2026, 3, 1), lab)


def test_title_is_html_escaped(site_copy):
    lab = site_copy / "lab"
    target = new_note.create("A <b> & B", "lab", date(2026, 3, 1), lab)
    assert "A &lt;b&gt; &amp; B" in target.read_text(encoding="utf-8")
