# Inizia qui

Questo repository è il tuo sito, albertstein.link. Non è un sito da guardare: è un sito da costruire. Ogni pezzo che costruisci diventa una riga vera nel tuo CV, e la storia dei commit è la prova.

## Il gioco

Tre livelli. Ogni livello ha delle missioni e finisce con un **boss**: un compito senza istruzioni, solo l'obiettivo. Le missioni si sbloccano in ordine. Il sito mostra a che livello sei.

| Livello | Nome | Missioni | Boss |
|---|---|---|---|
| 1 | Operator | 1, 2, 3 | La pagina /now |
| 2 | Guardian | 4, 5, 6 | Incident drill |
| 3 | Engineer | 7, 8 | Il colloquio |

- Le schede sono in `missioni/`. Ogni scheda: cosa ottieni, perché conta per chi ti assume, passi, quando è "fatta", riga che entra nel CV.
- I boss sono in `missioni/BOSS-1.md`, `BOSS-2.md`, `BOSS-3.md`. Niente passi. Te la cavi tu.
- Quando chiudi una missione, metti `"done": true` in `site/data/progress.json`. Quando chiudi un boss, `"done": true` sul boss. La barra sul sito si riempie, il CV si aggiorna da solo, e sali di livello.
- Dal Livello 2 ci sono gli **incidenti**: qualcosa sul sito si romperà, senza preavviso, per mano di tuo fratello. Il tuo monitor (missione 6) ti avvisa. Tu risolvi e scrivi un post-mortem con il template in `missioni/POSTMORTEM-template.md`. Ogni post-mortem finisce nella lista `incidents` di `progress.json` e compare sul sito.
- `missioni/SIDE-QUESTS.md`: cose extra, opzionali, che valgono una nota di lab ciascuna.

## Le tre regole

1. **Il codice lo scrivi tu.** claude.ai (gratis) è il tutor, non l'operaio. Ogni scheda ha un prompt pronto con questa regola dentro.
2. **Commit piccoli, in inglese, all'imperativo.** "Add www redirect", non "changes". Un commit, una cosa.
3. **Se rompi il sito non è un problema.** Il commit precedente è sempre lì. Rompere e rimettere in piedi è metà del mestiere.

## Cosa hai già

- Dominio registrato, DNS su Cloudflare, sito online che si aggiorna a ogni push su `main`.
- Il CV è già sul sito. Da qui in poi cresce solo con quello che fai.

Parti da `missioni/01.md`. Le missioni 1, 2 e 3 le fai dal browser; dalla 5 in poi dal tuo PC.
