# albertstein.link: un comando per ogni cosa. Leggi CONTRIBUTING.md.
# Serve solo Python 3 (libreria standard). pytest solo per `make test`.

PY ?= python3
PORT ?= 8080

.PHONY: help serve check test note postmortem lab-lint pdf

help:
	@echo "make serve                     sito locale su http://localhost:$(PORT)/"
	@echo "make check                     tutti i controlli (quelli della CI)"
	@echo "make test                      test degli strumenti (pytest)"
	@echo "make note TITLE=\"...\"          nuova nota di lab da template, aggiunta in cima alla lista"
	@echo "make postmortem TITLE=\"...\"    nuovo post-mortem da template"
	@echo "make lab-lint                  solo punteggio e suggerimenti sulle note di lab"
	@echo "make pdf                       esporta il CV in site/cv/Alberto-Galliani-CV.pdf (serve Playwright)"

serve:
	@$(PY) tools/serve.py $(PORT)

check:
	@$(PY) tools/check.py

test:
	@$(PY) -m pytest -q tests

lab-lint:
	@$(PY) tools/check.py --lab-md

note:
	@test -n "$(TITLE)" || { echo 'uso: make note TITLE="Titolo della nota"'; exit 2; }
	@$(PY) tools/new_note.py "$(TITLE)"

postmortem:
	@test -n "$(TITLE)" || { echo 'uso: make postmortem TITLE="Cosa si e rotto"'; exit 2; }
	@$(PY) tools/new_note.py --postmortem "$(TITLE)"

pdf:
	@$(PY) tools/pdf.py
