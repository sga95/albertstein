# Post-mortem: TITOLO BREVE

Data: YYYY-MM-DD
Durata del disservizio: X minuti (da HH:MM a HH:MM)
Impatto: cosa non funzionava, per chi

## Timeline

Orari veri, presi da issue, commit, log Cloudflare.

- HH:MM il monitor apre la issue #N
- HH:MM prima ipotesi: ...
- HH:MM verifica: ...
- HH:MM causa trovata: ...
- HH:MM fix: commit / modifica ...
- HH:MM sito ok, issue chiusa

## Causa

Una frase. Il pezzo che si è rotto e perché rompe quello che si vedeva.

## Cosa ha aiutato

Strumenti, comandi, pagine che hanno fatto capire.

## Cosa ha fatto perdere tempo

Ipotesi sbagliate, comandi inutili, cose che credevo e non erano vere.

## Cosa cambio

Una o due azioni concrete perché la prossima volta duri meno. Poi falle.

---
Come pubblicarlo: salva questo file come `site/lab/YYYY-MM-DD-postmortem-titolo.html` partendo da `template.html`, e aggiungi in `progress.json`:
`{ "date": "YYYY-MM-DD", "title": "Post-mortem: ...", "url": "../lab/YYYY-MM-DD-postmortem-titolo.html" }`
