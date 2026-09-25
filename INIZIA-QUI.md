# Inizia qui

Questo repository è il tuo sito, albertstein.link. Non è un sito da guardare: è un sito da costruire. Ogni pezzo che costruisci diventa una riga vera nel tuo CV, e la storia dei commit è la prova.

## Prima settimana: Shield

Prima di qualsiasi missione fai `missioni/SHIELD.md`: password manager, 2FA, email professionale su Proton, account GitHub blindato, commit firmati, portatile cifrato. Nove passi, una settimana. Da lì in poi tutto quello che costruisci sta su fondamenta tue.

## Il gioco

Sei livelli. Ogni livello ha delle missioni e finisce con un **boss**: un compito senza istruzioni, solo l'obiettivo. Le missioni si sbloccano in ordine. Il sito mostra a che livello sei.

| Livello | Nome | Missioni | Boss |
|---|---|---|---|
| 1 | Operator | 1, 2, 3 | La pagina /now |
| 2 | Guardian | 4, 5, 6 | Incident drill |
| 3 | Engineer | 7, 8 | Il colloquio |
| 4 | Sysadmin | 9-12 (`LIVELLO-4.md`) | Ricostruisci in un'ora |
| 5 | Network engineer | 13-16 (`LIVELLO-5.md`) | Il guasto |
| 6 | Cloud | 17-20 (`LIVELLO-6.md`) | Da casa al cloud |

In parallelo, quattro **binari** che non dipendono dai livelli:

- **Shield** (`SHIELD.md`): la tua sicurezza. Si fa per primo.
- **Mind** (`MIND.md`): l'AI come strumento, non come scorciatoia. Otto passi, da come funziona un modello a come ne parli a un colloquio. Si fa subito dopo Shield.
- **Voice** (`VOICE.md`): comunicazione e inglese. Dieci passi, dal changelog scritto al colloquio parlato in inglese. Costruito per partire in silenzio.
- **Hire** (`HIRE.md`): LinkedIn, annunci, storie, CV mirati, candidature, colloqui, offerta.

E poi:

- **Incidenti** (dal Livello 2): qualcosa si rompe per mano di tuo fratello, senza preavviso. Il tuo monitor ti avvisa, tu risolvi e scrivi un post-mortem (`POSTMORTEM-template.md`).
- **Side quest** (`SIDE-QUESTS.md`): extra opzionali, ognuna vale una nota di lab.

## Il progresso lo sblocchi solo tu

`site/data/progress.json`: `"done": true` sulla missione, sul passo del binario o sul boss. Il sito si aggiorna da solo: barra, livello, righe nel CV, badge.

Quel file è tuo per contratto: sei il suo code owner (`.github/CODEOWNERS`), nessuna modifica passa senza la tua approvazione, nemmeno di tuo fratello, e un controllo automatico rifiuta cambiamenti fatti da altri account. Dal passo S5 i tuoi commit sono firmati: chi legge il repo vede che sei stato tu. Questo è il motivo per cui il CV sul sito vale: nessuno può scriverci una skill al posto tuo.

## Le tre regole

1. **Il codice lo scrivi tu.** claude.ai (gratis) è il tutor, non l'operaio. Ogni scheda ha un prompt con questa regola dentro.
2. **Commit piccoli, in inglese, all'imperativo.** "Add www redirect", non "changes".
3. **Se rompi qualcosa non è un problema.** Rompere e rimettere in piedi è metà del mestiere.

## Quanto dura

Shield: una settimana. Livelli 1-3: due o tre mesi. Binari: vanno avanti sempre. Livelli 4-6: sei mesi, se ci lavori ogni settimana. Prima della fine del livello 4 sei già assumibile: il binario Hire parte subito, non aspetta.

## Cosa hai già

Dominio, DNS, sito online che si aggiorna a ogni push, CV già sul sito. Da qui in poi cresce solo con quello che fai.

Parti da `SHIELD.md`. Poi `missioni/01.md` e `VOICE.md` passo V1, insieme.
