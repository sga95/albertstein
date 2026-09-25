# Engine: brief per Claude Code

Repository: `sga95/albertstein`. Sito statico in `site/`, missioni in `missioni/`, stato in `site/data/progress.json`. Cloudflare Pages pubblica `site/` a ogni push su `main`.

Obiettivo: costruire in questo repo un motore che collega **quello che Alberto vuole fare** (`data/me.yaml`), **quello che il mercato chiede oggi** (ruoli e skill, aggiornati da un agente), e **quello che ha dimostrato di saper fare** (evidenze nel repo), e che lo guida con agenti che lo seguono ogni settimana. Alberto non ha Claude Code: gli agenti girano in GitHub Actions con la API key di Stefano e parlano con lui tramite issue, commenti nelle PR e pagine del sito.

Prompt di avvio per Code, da incollare così com'è:

> Leggi `engine/BRIEF.md` per intero. Poi leggi `INIZIA-QUI.md`, `missioni/`, `site/data/progress.json` e `site/app.js` per capire lo stato attuale. Lavora per fasi come descritto nel brief: chiudi la Fase 1 con test verdi e una PR prima di toccare la Fase 2. Non modificare il contenuto delle missioni né il design del sito, se non per aggiungere le pagine previste. Ogni agente deve rispettare le regole in "Guardrail" alla lettera. Chiedimi conferma prima di aggiungere dipendenze o secret.

---

## 1. Tutte le idee (da cui scegliere, in ordine di valore)

1. **Grafo delle skill**: tassonomia con livelli 0-4, tipi di evidenza (commit, nota di lab, post-mortem, cert, talk, PR revisionata), data dell'ultima evidenza.
2. **Profili di ruolo dal mercato**: junior network engineer, NOC analyst L1/L2, sysadmin junior, IT support L2, cloud/network junior, SOC L1, network automation junior. Skill pesate, cert tipiche, RAL tipica in Italia, quanto chiedono l'inglese.
3. **Radar di mercato**: ogni settimana un agente cerca annunci (Italia, remoto EU), estrae requisiti, aggiorna `data/market.json`: "cosa chiedono questo mese", trend, skill emergenti.
4. **Readiness per ruolo**: punteggio gap tra evidenze e profilo, pagina `/readiness` con radar SVG statico per ogni ruolo target.
5. **Coach settimanale**: lunedì mattina una issue: cosa hai fatto, tre prossimi passi (uno per campagna, uno Voice, uno Hire), una cosa da non fare. Corto, diretto.
6. **Reviewer senior sulle PR**: fa domande invece di correggere, controlla i messaggi di commit, segnala quando una missione viene chiusa senza evidenze.
7. **Validatore di evidenze**: quando `done` diventa `true`, verifica che esistano i file previsti dalla scheda; se mancano, commenta e il sito mostra "unverified".
8. **Coach di inglese**: sulle PR che toccano changelog e note, corregge solo errori veri, spiega in una riga, tiene traccia degli errori ricorrenti.
9. **Interviewer**: ogni settimana cinque domande generate dal suo lavoro recente, in una issue; lui risponde nella issue; l'agente valuta e rilancia.
10. **Story bank assistito**: da ogni post-mortem una bozza STAR che lui deve riscrivere (la bozza è volutamente da rifinire).
11. **CV generato**: le tre versioni del CV (`hire/`) rigenerate da `progress.json` e dalle evidenze, sempre via PR da approvare.
12. **Job matcher**: incrocia annunci freschi con la readiness, propone 5 candidature a settimana con il perché, apre reminder di follow-up dopo 10 giorni.
13. **Scheduler red team** (repo privato di Stefano): propone il prossimo incidente in base al livello, con istruzioni per Stefano.
14. **Digest per il mentor**: ogni domenica a Stefano: cosa ha fatto Alberto, cosa serve da te questa settimana (review, chiamata, incidente).
15. **Costanza senza vergogna**: se una settimana è vuota, il coach lo dice in una riga e propone il passo più piccolo possibile. Mai streak, mai colpa.
16. **Flashcard**: dalle note di lab e dal blueprint CCNA, deck con ripetizione spaziata, pagina `/cards` con stato in localStorage.
17. **Lint delle note di lab**: ha lo schema? ha "what I learned"? ha comandi veri? Punteggio e suggerimenti, non blocco.
18. **Pianificatore certificazioni**: date, costi, prerequisiti, ordine consigliato in base al ruolo target e al budget.
19. **Pagina "hire me"**: una pagina generata per i recruiter: readiness, evidenze linkate, ultime note, tre cose che sa fare provate.
20. **Tutor in chat sul sito**: Worker Cloudflare + API Anthropic, dietro Cloudflare Access (solo Alberto e Stefano), con il repo come contesto e la regola "guida, non fare". Le domande diventano segnali per il coach.
21. **Segnali soft, solo positivi**: chiarezza dello scritto (leggibilità), domande fatte, iniziative prese. Nessuna metrica punitiva.
22. **Riordino dinamico delle missioni**: se il mercato o `me.yaml` cambiano, il motore propone un ordine diverso delle missioni 9-20 (propone, non applica).
23. **Trascrizione audio per Voice**: i passi audio/video possono essere caricati e trascritti; l'agente commenta chiarezza e riempitivi.
24. **Budget**: ogni run registra i token; tetto settimanale in `engine/config.yaml`; oltre il tetto gli agenti si fermano e aprono una issue a Stefano.

---

## 2. Architettura

```
albertstein/
  site/                      sito statico (esistente)
    data/progress.json       stato missioni (esistente, editato da Alberto)
    data/readiness.json      generato dal motore
    data/market.json         generato dall'agente di mercato
    readiness/index.html     nuova pagina
    market/index.html        nuova pagina
    coach/index.html         ultimo briefing (pubblico, senza dati sensibili)
  data/
    me.yaml                  cosa vuole Alberto (lui lo compila)
    skills.yaml              tassonomia skill, evidenze, livelli
    roles.yaml               profili ruolo pesati
    evidence-rules.yaml      cosa prova cosa (per missione e per passo)
  engine/
    BRIEF.md                 questo file
    config.yaml              modelli, tetti di spesa, orari
    core/                    deterministico, nessun LLM
      scan.py                estrae evidenze dal repo (git log, file, note)
      readiness.py           calcola readiness per ruolo
      render.py              genera readiness.json, SVG radar, pagine
    agents/                  un file per agente, LLM via SDK anthropic
      coach.py  reviewer.py  validator.py  english.py  market.py
      interviewer.py  matcher.py  stories.py  cv.py
    prompts/                 un .md per agente, versionato
    lib/                     client, budget, github helpers, guardrail
    tests/
  hire/                      esistente: annunci, storie, candidature, CV
  .github/workflows/
    engine-build.yml         su push: core + render, commit dei json generati
    engine-review.yml        su PR: reviewer, validator, english, lint note
    engine-weekly.yml        cron lunedì 07:00 Europe/Rome: coach, interviewer, matcher
    engine-market.yml        cron domenica: market
```

Stack: Python 3.12, `anthropic`, `pyyaml`, `pytest`. Nessun framework. Nessun servizio esterno oltre GitHub, Anthropic e (Fase 4) Cloudflare.

Repo privato separato `albertstein-mentor` (solo Stefano): scheduler red team e digest del mentor. Legge il repo pubblico, non scrive mai in esso.

---

## 3. Modello dati

`data/me.yaml` (Alberto lo compila alla prima missione del motore):
```yaml
target_roles: [junior-network-engineer, noc-analyst, sysadmin-junior]   # in ordine
location: Bergamo
remote: hybrid_ok
languages: {it: native, en: B1}
hours_per_week: 8
constraints: [no_shifts_first_year]
likes: [networking, linux, security]
dislikes: [helpdesk_phone]
```

`data/skills.yaml`: per ogni skill `id, name, family (network|systems|cloud|automation|security|communication|hiring), levels: {1: "...", 2: "...", 3: "...", 4: "..."}` con descrizioni osservabili, e `evidence: [tipi ammessi]`.

`data/roles.yaml`: per ruolo `id, title_it, title_en, skills: {skill_id: {weight, min_level}}, certs_typical, english_min, salary_range_it`.

`data/evidence-rules.yaml`: per missione/passo/boss: quali file o pattern provano il completamento e quale livello di quali skill attestano. Esempio: missione 6 done richiede `monitor/check.py` e `.github/workflows/uptime.yml` e almeno una issue chiusa con label `uptime`; attesta `python: 2, monitoring: 2, ci: 2`.

`site/data/readiness.json`: `{generated_at, roles: [{id, score_0_100, gaps: [{skill, have, need, next_mission}], strengths: [...]}], skills: [{id, level, last_evidence, verified}]}`.

`site/data/market.json`: `{generated_at, window: "30d", roles: [{id, postings_seen, top_skills: [{skill, share}], certs: [...], english_required_share}], emerging: [...]}`. Solo aggregati, mai copie di annunci.

---

## 4. Agenti

Regole comuni in `engine/lib/guardrail.py` e in testa a ogni prompt:

- **Guida, non esegue.** Nessun agente scrive codice o contenuti che una missione chiede ad Alberto. Può fare esempi di 3 righe massimo, su un caso diverso dal suo.
- **Non chiude nulla.** `done` lo cambia solo Alberto. Gli agenti al massimo dicono "unverified".
- **Non fa merge.** Le PR generate (CV, story bank, readiness) le approva un umano.
- **Corto.** Coach: massimo 12 righe. Review: massimo 5 commenti per PR. Interviewer: 5 domande.
- **Lingua.** Coaching e review in italiano. Coach di inglese in inglese, con spiegazioni in italiano.
- **Tono.** Diretto, senza esclamativi, senza complimenti generici, senza colpa. Se una settimana è vuota: una riga e il passo più piccolo.
- **Costi.** Ogni run passa dal budget: modello Sonnet per default, Haiku per lint e validazioni; tetto settimanale in `config.yaml`; superato il tetto, stop e issue a Stefano.
- **Privacy.** Nessun dato personale oltre a quello già sul sito. Il market non salva annunci, solo aggregati.

Agenti, trigger, input, output:

| Agente | Trigger | Legge | Scrive |
|---|---|---|---|
| coach | lunedì 07:00 | progress, readiness, git log 7 giorni, issue aperte, ultimo coach | issue `coach: settimana N` + `site/coach/` |
| reviewer | PR aperta o aggiornata | diff, commit messages, scheda della missione toccata | commenti sulla PR (domande) |
| validator | PR che tocca progress.json | evidence-rules, file del repo | commento con lista evidenze mancanti; `verified` in readiness |
| english | PR che tocca `site/now/`, `site/lab/`, `hire/` | testo modificato | suggerimenti come review comment, un errore per commento |
| lint (no LLM) | PR che tocca `site/lab/` | note | check con punteggio e suggerimenti |
| market | domenica 06:00 | web search (tool Anthropic), roles.yaml | `site/data/market.json`, PR se roles.yaml merita aggiornamenti |
| interviewer | lunedì 07:10 | note, post-mortem, commit della settimana | issue con 5 domande; su commento di Alberto: valutazione e rilancio |
| matcher | lunedì 07:20 | market, readiness, me.yaml, `hire/applications.csv` | issue con 5 proposte e perché; reminder follow-up a +10 giorni |
| stories | nuovo post-mortem in main | il post-mortem | PR su `hire/stories.md` con bozza STAR marcata "da riscrivere" |
| cv | readiness cambia di più di 5 punti | readiness, CV base | PR con i tre PDF rigenerati |

Ogni agente: `run(context) -> Result` puro, testabile con fixture; l'I/O GitHub sta in `lib/github.py`. I prompt in `engine/prompts/*.md`, con versione in testa; il test di ogni agente include un caso "settimana vuota" e un caso "tentativo di far fare il lavoro all'agente" (deve rifiutare).

---

## 5. Pagine nuove sul sito

Stesso design di `site/style.css` (fascia navy, schede, numeri arancioni). Nessun JS aggiuntivo oltre a leggere i json; il radar è SVG generato da `render.py`, non disegnato nel browser.

- `/readiness`: per ogni ruolo target un radar e tre gap con la missione che li chiude. Sotto, la lista skill con livello, ultima evidenza e stato verified.
- `/market`: cosa chiedono gli annunci per i ruoli target negli ultimi 30 giorni, aggregato. Una riga per skill emergente.
- `/coach`: ultimo briefing, senza link a issue private.
- Aggiungere le tre voci alla nav di tutte le pagine.

---

## 6. Fasi

**Fase 1, core (nessun LLM, nessun costo).** `me.yaml`, `skills.yaml` (30-40 skill), `roles.yaml` (7 ruoli), `evidence-rules.yaml` per le 20 missioni, 18 passi dei binari e 6 boss. `scan.py`, `readiness.py`, `render.py`, pagina `/readiness`, workflow `engine-build.yml`. Test. Criterio: con il progress attuale (tutto false) il radar è vuoto e i gap puntano alla missione 1; con una fixture a metà percorso i punteggi hanno senso.

**Fase 2, agenti di accompagnamento.** `lib/` (client, budget, github, guardrail), `coach`, `reviewer`, `validator`, `english`, lint. Workflow review e weekly. Secret `ANTHROPIC_API_KEY`. Criterio: una PR finta riceve al massimo 5 commenti, tutti domande; il coach su una settimana vuota scrive una riga.

**Fase 3, mercato e assunzione.** `market`, `matcher`, `interviewer`, `stories`, `cv`, pagine `/market` e `/coach`. Criterio: `market.json` non contiene testo di annunci; il matcher propone solo ruoli in `me.yaml`.

**Fase 4, opzionale.** Tutor in chat (Worker + Access), flashcard `/cards`, repo `albertstein-mentor` con scheduler red team e digest.

---

## 7. Cose da non fare

- Non cambiare le missioni, i boss, i binari o il design senza chiederlo.
- Non introdurre framework, database o servizi a pagamento oltre all'API Anthropic.
- Non far girare agenti su ogni push: solo sui trigger indicati.
- Non usare mai il modello Opus per default.
- Non scrivere niente in `site/data/progress.json`: è di Alberto.
