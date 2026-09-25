# Boss 2: incident drill

Nessun passo. Questo boss non lo lanci tu: ti arriva addosso.

## Come funziona

Da quando la missione 6 è chiusa, tuo fratello ha il permesso di rompere qualcosa sul sito o sulla sua infrastruttura, quando vuole, senza dirti cosa. Possono essere i DNS, un file, una regola su Cloudflare, il monitor stesso.

Il tuo monitor apre una issue. Da quel momento parte il tempo.

## Obiettivo

1. Capire cosa è successo, non solo "il sito non va": qual è il pezzo rotto e perché quel pezzo rompe quello che vedi.
2. Rimettere in piedi il sito.
3. Scrivere il post-mortem con `POSTMORTEM-template.md`, metterlo in `site/lab/`, aggiungerlo alla lista `incidents` in `progress.json`.

## Vincoli

- Entro 48 ore dalla issue.
- Nel post-mortem la timeline è con orari veri, presi dalla issue, dai commit, dai log di Cloudflare.
- Se hai chiesto aiuto a claude.ai lo scrivi, e scrivi cosa ti ha detto di sbagliato (succede).

## È battuto quando

- Sito ripristinato e post-mortem online.
- Tuo fratello legge il post-mortem e conferma che hai trovato la causa vera, non un sintomo.

## Badge

Handled a live incident and wrote the post-mortem

Dopo il primo, gli incidenti continuano. Ogni post-mortem in più è una riga in più sul sito. Un recruiter che legge tre post-mortem fatti bene ha già deciso.
