# Inizia qui

Questo repository è il tuo sito, albertstein.link. Non è un sito da guardare: è un sito da costruire, e ogni pezzo che costruisci diventa una riga vera nel tuo CV.

## Come funziona

1. Nella cartella `missioni/` ci sono 8 schede, in ordine. Falle in ordine.
2. Ogni scheda dice cosa devi ottenere, perché conta per chi ti assume, i passi, e quando è "fatta".
3. Quando una missione è fatta, apri `site/data/progress.json` e metti `"done": true` su quella missione. Al prossimo deploy la barra sul sito si riempie e la riga di skill compare nel CV. Non c'è modo di barare che non si veda: i commit sono pubblici.
4. Se ti blocchi, ogni scheda ha un prompt pronto da incollare su claude.ai (è gratis). La regola è nel prompt stesso: ti guida, non fa il lavoro al posto tuo. Il codice lo scrivi tu.

## Regole

- Commit piccoli e frequenti. Un commit dice una cosa sola ("Add www redirect", non "changes").
- Messaggi di commit in inglese, all'imperativo.
- Se rompi il sito, non è un problema: la pipeline ti mostra l'errore e il commit precedente è sempre lì.
- Le missioni 1, 2 e 3 le puoi fare tutte dal browser. Dalla 5 in poi lavori dal tuo PC.

## Cosa hai già

- Il dominio è registrato e i DNS sono su Cloudflare.
- Il sito è online e si aggiorna da solo a ogni push su `main`.
- Il CV è già sul sito, con il testo che abbiamo rivisto insieme.

Parti da `missioni/01.md`.
