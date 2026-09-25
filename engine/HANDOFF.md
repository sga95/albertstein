# Handoff per Claude Code: albertstein.link

Questo file è il punto di partenza per ogni sessione di Code su questo repo. Dice cosa esiste, cosa manca, e le regole. Il brief del motore di coaching è in `engine/BRIEF.md`; `HANDOFF-2.md` e `HANDOFF-3.md` sono i capitoli già eseguiti (decisioni, corsi, certificazioni, passioni, Raspberry Pi) e restano come riferimento.

Prompt di avvio, da incollare in Code:

> Leggi `engine/HANDOFF.md`, poi `engine/BRIEF.md`. Lo stato del repo è quello descritto in "Cosa esiste". Il prossimo lavoro è la Fase 2 del BRIEF, che ha bisogno del secret `ANTHROPIC_API_KEY`: chiedi conferma prima. Non cambiare il contenuto delle missioni e non toccare `site/data/progress.json`. Il design del sito si estende, non si rifà. Chiedi conferma prima di aggiungere dipendenze, secret o servizi.

---

## 1. Cosa esiste

### Infrastruttura
- Dominio `albertstein.link` su Cloudflare Registrar (auto-rinnovo, lock attivo). Zona DNS attiva. SSL Full (strict), Always HTTPS, TLS minimo 1.2, HTTPS rewrites.
- **Cloudflare Workers con asset statici** (decisione 1 di HANDOFF-2): Worker `albertstein`, collegato a GitHub `sga95/albertstein` con Workers Builds. `wrangler.jsonc` alla radice (`assets.directory = "./site"`, `not_found_handling = "404-page"`), copia in `site/wrangler.jsonc` con `.assetsignore` per il caso in cui il build abbia root directory `site`. Su `main` pubblica in produzione; sugli altri branch fa un'anteprima e il bot Cloudflare scrive l'URL nella PR. Custom domain `albertstein.link` attivo; `www` non configurato di proposito: è la missione 2.
- Repo GitHub privato `sga95/albertstein`. Owner: Stefano (sga95). Alberto sarà collaboratore.

### Sito (`site/`)
Statico, HTML + CSS + un file JS. Nessun build step, nessun framework.
- Pagine: `index.html` (home con "Latest lab notes" e "Now playing"); `cv/`; `lab/` con `template.html` e `postmortem-template.html`; `progress/` (livelli, missioni, boss con loot, binari, incidenti); `quests/`; `readiness/` (generata); `certs/`; `gear/`; `puzzle/`, `reading/`, `codex/` (nel menu quando hanno contenuto); `404.html`.
- `style.css`: fascia navy, corpo a puntini, schede, sezioni numerate, etichette di stato, footer scuro. Token in `:root`, font come token. Spiegato in `site/THEME.md`.
- `app.js`: legge `data/site.json` (testi, menu, colori, font, flag, nomi dei livelli) e `data/progress.json` (stato), più i JSON generati (`certs`, `quests`, `loot`, `puzzles`, `pages`). Sblocco in ordine: missione `open` se la precedente è `done`; boss se tutte le missioni del livello sono `done`; passo di binario se il precedente è `done`. Funzioni pure `unlockStatus` e `certStatus`, testate da Node.
- `data/progress.json`: `tiers` (6), `missions` (20), `tracks` (shield 9, mind 8, pi 16 con `requires`, voice 10, hire 8), `incidents`, `quests`. **Lo edita solo Alberto.** Gli strumenti lo leggono, mai lo scrivono.
- `data/site.json`: tutto quello che Alberto cambia senza toccare HTML o CSS.
- Manca `site/cv/photo.jpg` (Stefano la carica a mano; riga in `engine/check-ignore.txt` da togliere quando c'è).
- Nessun telefono, nessuna frase su chi ha costruito il sito. Stefano non compare sul sito pubblico se non dove serve ("Ask Stefano").

### Percorso (`missioni/`, in italiano)
- `INIZIA-QUI.md`: regole, binari, ricompense e certificazioni, quest.
- Missioni 1-8 (`01.md` … `08.md`), `LIVELLO-4.md` (9-12), `LIVELLO-5.md` (13-16), `LIVELLO-6.md` (17-20). Boss `BOSS-1.md` … `BOSS-6.md`.
- Binari: `SHIELD.md` (9 passi, per primo), `MIND.md` (8, l'AI come strumento), `PI.md` (15 passi e un boss, sigillato fino al Boss 1: `requires` in `progress.json`), `VOICE.md` (10), `HIRE.md` (8).
- `QUESTS.md` (quest per passione), `POSTMORTEM-template.md`.
- Ogni scheda ha "Gratis, prima" con 1-4 risorse gratuite. Le missioni 1-3 descrivono Workers, non Pages. "Stefano" al posto di "tuo fratello" ovunque.

### Dati (`data/`)
- `me.yaml` (cosa vuole Alberto), `skills.yaml` (46 skill, livelli 0-4), `roles.yaml` (7 ruoli pesati), `evidence-rules.yaml` (cosa prova ogni missione, boss, passo, quest; le cert `passed` valgono livello 3 sulle skill dei loro ruoli).
- `certs.yaml` (catalogo) + `certs-status.json` (requested, granted), `quests.yaml`, `loot.yaml`, `hardware.yaml` (pagina `/gear`), `puzzles.yaml`.

### Motore (`engine/`)
- `core/scan.py` (evidenze dal repo), `core/readiness.py` (livelli e punteggi), `core/render.py` (genera `site/data/*.json` e `site/readiness/index.html`). Nessun LLM. Test in `engine/tests/`.
- Fase 1 del BRIEF fatta. Fase 2 (agenti con l'API Anthropic) non iniziata: serve il secret.

### Strumenti e controlli
- `Makefile`: `serve`, `check`, `test`, `note`, `postmortem`, `lab-lint`, `pdf`, `engine`, `quiz`. Tutto spiegato in `CONTRIBUTING.md`.
- CI (`ci.yml`): schema di `progress.json` e `site.json`, regola di sblocco (avviso), link, immagini, alt, peso, codex, HTML5, punteggio note di lab (commento), gitleaks, test, file generati aggiornati.
- `guard-progress.yml`: `progress.json` lo cambia solo Alberto (placeholder `ALBERTO-GITHUB`).
- `engine-build.yml`: su `main` e ogni lunedì rigenera i file di `site/data/` e la pagina readiness.
- `cert-status.yml`: issue "Richiesta a Stefano" → stato della certificazione. Template in `.github/ISSUE_TEMPLATE/cert-request.yml` (tipi: certificazione, loot, hardware).

### Fuori dal repo (solo Stefano)
- Playbook red team con 8 incidenti graduati. Non va nel repo.
- Configurazione del build in Workers → albertstein → Settings → Build.

---

## 2. Cose aperte (per Stefano, non per Code)
- Caricare `site/cv/photo.jpg` e togliere la riga da `engine/check-ignore.txt`.
- Sostituire `ALBERTO-GITHUB` in `CODEOWNERS` e in `guard-progress.yml`.
- Aggiungere Alberto come collaboratore GitHub e come membro Cloudflare (ruolo DNS).
- Notifiche GitHub per le label `cert-request` (o "Watch: all activity").
- Rivedere `data/loot.yaml`, `data/certs.yaml` e `data/hardware.yaml` (costi e scelte). Scrivere il primo puzzle in `data/puzzles.yaml`.
- Dire a Code il modello del Pi quando Alberto lo ha in mano (Pi 3: varianti in `PI.md`).
- Branch protection su `main` con "Require review from Code Owners".
- Repo pubblico quando Alberto è pronto.
- Fase 2 del BRIEF: secret `ANTHROPIC_API_KEY` quando vuole gli agenti.

---

## 3. Regole per Code su questo repo
- Le missioni sono testo di Stefano: non riscriverle. Correggere refusi è ok.
- `site/data/progress.json` non si tocca.
- Il design si estende, non si sostituisce. Stessi token, stessa fascia, stesse schede.
- Tutto in italiano per Alberto (schede, CONTRIBUTING, THEME), in inglese sul sito.
- Niente trattini lunghi nei testi.
- Ogni PR: descrizione di cosa cambia e come provarlo in locale. Una PR per blocco.
- Niente servizi a pagamento oltre all'API Anthropic (Fase 2). Chiedere prima di aggiungere dipendenze, secret o servizi.
