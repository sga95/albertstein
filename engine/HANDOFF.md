# Handoff per Claude Code: albertstein.link

Questo file è il punto di partenza per ogni sessione di Code su questo repo. Dice cosa esiste, cosa manca, e cosa fare adesso. Il brief del motore di coaching è in `engine/BRIEF.md`: viene dopo quello che c'è qui.

Prompt di avvio, da incollare in Code:

> Leggi `engine/HANDOFF.md` e poi `engine/BRIEF.md`. Prima esegui i lavori in "Da fare adesso" nell'ordine dato, un blocco per PR, con test verdi. Solo dopo passa alle fasi del BRIEF. Non cambiare il contenuto delle missioni e non toccare `site/data/progress.json`. Il design del sito si estende, non si rifà. Chiedi conferma prima di aggiungere dipendenze, secret o servizi.

---

## 1. Cosa esiste

### Infrastruttura
- Dominio `albertstein.link` su Cloudflare Registrar (auto-rinnovo, lock attivo). Zona DNS attiva.
- Zona: SSL Full (strict), Always HTTPS, TLS minimo 1.2, HTTPS rewrites.
- Cloudflare Pages, progetto `albertstein`, collegato a GitHub `sga95/albertstein`, branch `main`, nessun build command, output directory `site`. Custom domain `albertstein.link` attivo. `www` non configurato di proposito: è la missione 2 di Alberto.
- Repo GitHub privato `sga95/albertstein`. Owner: Stefano (sga95). Alberto sarà collaboratore.

### Sito (`site/`)
Statico, HTML + CSS + un file JS. Nessun build step.
- `index.html` home; `cv/index.html` CV; `lab/index.html` + `lab/template.html` note di laboratorio; `progress/index.html` percorso; `404.html`.
- `style.css`: fascia navy con progresso dentro, corpo a puntini, schede, sezioni numerate, etichette di stato, footer scuro. Font: Space Grotesk (titoli), IBM Plex Sans (testo), IBM Plex Mono (etichette). Token in `:root`.
- `app.js`: legge `data/progress.json` e riempie livello, barra, livelli con missioni e boss, binari, righe "earned" nel CV, incidenti. Sblocco in ordine: una missione è `open` se la precedente è `done`; il boss se tutte le missioni del livello sono `done`.
- `data/progress.json`: `tiers` (6), `missions` (20, con `file` opzionale per le schede cumulative), `tracks` (shield 9, voice 10, hire 8), `incidents` []. È l'unico file che Alberto edita per segnare il progresso.
- Manca `site/cv/photo.jpg` (il connettore non carica binari). Stefano la aggiunge a mano.
- Nessun numero di telefono sul sito, per scelta. L'email attuale è Gmail: verrà sostituita da Proton al passo S3.
- Nessuna frase che dica chi ha costruito il sito: è presentato come percorso formativo.

### Percorso (`missioni/`, in italiano)
- `INIZIA-QUI.md`: regole del gioco. Parte da Shield.
- Missioni 1-8: `01.md` … `08.md` (sito, DNS/TLS, pipeline, header di sicurezza, postazione Linux, monitor Python, prima nota di lab, CCNA).
- `LIVELLO-4.md` (9-12: Proxmox, Docker, Ansible, backup), `LIVELLO-5.md` (13-16: Containerlab OSPF/BGP, OPNsense, Netmiko/Nornir, NetBox+LibreNMS), `LIVELLO-6.md` (17-20: cert cloud, VPC, Terraform, Cloudflare Tunnel+Access).
- Boss: `BOSS-1.md` … `BOSS-6.md`. Senza passi, solo obiettivo e criterio.
- Binari: `SHIELD.md` (sicurezza personale, si fa per primo), `VOICE.md` (comunicazione e inglese, per chi parte silenzioso), `HIRE.md` (ricerca lavoro).
- `SIDE-QUESTS.md`, `POSTMORTEM-template.md`.
- Ogni scheda: cosa ottieni, perché conta, passi, "è fatta quando", riga che entra nel CV, prompt da incollare su claude.ai con la regola "guida, non fare".

### Controllo del progresso
- `.github/CODEOWNERS`: `site/data/progress.json` e `site/now/` assegnati a `@ALBERTO-GITHUB` (placeholder da sostituire).
- Workflow `guard-progress.yml` (in `engine/` o da creare in `.github/workflows/`): fallisce se chi modifica `progress.json` non è Alberto; avvisa sui commit non firmati. Placeholder `ALBERTO-GITHUB`.
- Branch protection su `main` non ancora attiva: la attiva Alberto alla missione 3. Stefano deve attivare "Require review from Code Owners".

### Fuori dal repo (solo Stefano)
- Playbook red team con 8 incidenti graduati. Non va nel repo.
- Procedura di setup già eseguita.

---

## 2. Cose aperte (per Stefano, non per Code)
- Caricare `site/cv/photo.jpg`.
- Sostituire `ALBERTO-GITHUB` in `CODEOWNERS` e nel workflow.
- Aggiungere Alberto come collaboratore GitHub e come membro Cloudflare (ruolo DNS).
- Mettere il workflow `guard-progress.yml` in `.github/workflows/` (Code può farlo).
- Repo pubblico quando Alberto è pronto: senza questo, le missioni che parlano di "commit pubblici" non hanno senso per i recruiter.

---

## 3. Da fare adesso (Code, in ordine, una PR per blocco)

### Blocco A: strumenti di sviluppo e test
Obiettivo: Alberto lavora sul sito con un comando solo, e ogni PR viene controllata.

- `Makefile` (o `tools/` in Python, senza dipendenze pesanti) con: `make serve` (server locale su 8080 con la cartella `site`), `make check` (tutti i controlli sotto), `make note TITLE="..."` (crea una nota di lab dal template con data di oggi e la aggiunge in cima a `lab/index.html`), `make postmortem TITLE="..."`.
- Controlli in `make check` e in un workflow `ci.yml` su ogni PR:
  - `progress.json` valido contro uno schema JSON (`engine/schema/progress.schema.json`); errore chiaro se manca una virgola, con numero di riga.
  - Regola di sblocco rispettata: nessuna missione `done` se la precedente non lo è; nessun boss `done` se le missioni del livello non lo sono. Solo warning, non errore.
  - HTML valido (html5validator o simile, in CI), link interni non rotti, immagini esistenti, `alt` presenti.
  - Lint delle note di lab: le quattro sezioni presenti, almeno un blocco `<pre>` o un'immagine, "What I learned" non vuoto. Punteggio e suggerimenti nel commento della PR, non blocco.
  - Peso: nessuna immagine sopra 300 KB, nessuna pagina sopra 200 KB.
  - Secret scanning con gitleaks in CI.
- Test `pytest` per gli strumenti e per la logica di sblocco (replicare in Python la stessa logica di `app.js` e testare che coincidano su fixture).
- `CONTRIBUTING.md` in italiano: come lanciare i comandi, cosa controlla la CI, come leggere un errore.

### Blocco B: personalizzazione e pieno controllo
Obiettivo: Alberto cambia testi, colori, sezioni e voci di menu senza toccare HTML o CSS, ma può toccarli quando vuole.

- `site/data/site.json`: nome, tagline, kicker della home, email, voci di nav (etichetta, path, ordine), colori (navy, accent, paper, dot), font, testo del footer, flag per mostrare o nascondere sezioni (incidenti, tracce, note in home). `app.js` lo legge e applica: variabili CSS su `:root`, testi con `data-site="chiave"`, nav generata.
- Tutte le pagine usano `data-site` per i testi comuni; il contenuto specifico (CV, note) resta nell'HTML, che è suo.
- `site/THEME.md`: i token CSS spiegati uno per uno, tre esempi di variante (scuro, monocromo, con foto grande), come cambiare font, come aggiungere una pagina con la fascia e la nav giuste, come aggiungere una voce di menu.
- `site/cv/`: il CV resta HTML, ma sezioni ordinabili con `data-order`; documentare in `THEME.md`.
- Esportazione: `make pdf` genera `site/cv/Alberto-Galliani-CV.pdf` dalla pagina CV con lo stile di stampa (Playwright headless, dipendenza solo per questo comando, non in CI).
- Niente framework, niente build obbligatorio, niente bundler. Il sito deve continuare a funzionare aprendo `index.html` da un server statico.

### Blocco C: binario Mind (AI, e come usare claude.ai)
Obiettivo: Alberto usa l'AI come strumento da professionista, non come scorciatoia, e lo sa spiegare a un colloquio. Creare `missioni/MIND.md` nello stesso formato degli altri binari e aggiungere il binario `mind` a `progress.json` (`file: "MIND.md"`), dopo `shield`.

Passi (titoli in inglese per il sito, schede in italiano):
1. **How a language model works**: token, contesto, probabilità, perché "sbaglia con sicurezza". Fatta quando: una nota di lab spiega a parole sue perché un modello inventa un comando che non esiste, con un esempio provato. CV: Working understanding of LLMs: context, tokens, hallucination.
2. **claude.ai, set up for learning**: account, Progetti, istruzioni personalizzate con la regola "guida, non fare, chiedimi cosa vedo", quando usare la chat e quando no. Fatta quando: le istruzioni sono salvate e la prima conversazione di lab le rispetta. CV: Configured an AI assistant as a tutor with explicit guardrails.
3. **Ask, then verify**: ogni risposta tecnica si verifica su una fonte (man page, doc ufficiale, prova in lab). Fatta quando: cinque casi documentati in cui la verifica ha smentito o corretto la risposta. CV: Verification habit for AI-generated technical answers.
4. **What never goes in a prompt**: chiavi, password, IP interni, dati di clienti, codice dell'azienda. Fatta quando: una regola scritta nella checklist Shield e un esempio di prompt "anonimizzato" bene. CV: Data hygiene when using AI tools.
5. **Prompting for real work**: contesto, obiettivo, vincoli, formato; iterare; chiedere il ragionamento; far criticare la propria bozza. Fatta quando: un prompt riusabile per la revisione delle note di lab e uno per il debug di rete, salvati in `hire/prompts.md`. CV: Structured prompting for technical tasks.
6. **AI for networking**: analisi di log e capture con l'AI come secondo paio d'occhi, generazione di configurazioni da rivedere riga per riga, spiegazione di output di `show`. Fatta quando: una nota di lab con un caso in cui l'AI ha aiutato e uno in cui ha sbagliato. CV: Applying AI assistance to network troubleshooting with review.
7. **Your first API call**: uno script Python di 30 righe che chiama l'API Anthropic (chiave in variabile d'ambiente, mai nel codice) e riassume una nota di lab. Fatta quando: lo script gira, la chiave non è nel repo, gitleaks passa. CV: Called an LLM API from Python with secure key handling.
8. **AI in the interview**: cosa dire quando chiedono "usi l'AI?": sì, come, con quali limiti, con esempi. Fatta quando: risposta di 60 secondi, provata con Stefano. CV: Can explain responsible AI use to an employer.

Aggiungere in `INIZIA-QUI.md` la riga del binario Mind e in `progress/index.html` la parola "Mind" nella descrizione dei binari.

### Blocco D: pulizia
- Mettere `guard-progress.yml` in `.github/workflows/`.
- Aggiungere il workflow `ci.yml` del blocco A.
- Aggiornare `README.md` con i comandi `make`.

### Poi: `engine/BRIEF.md`, Fase 1 in avanti.

---

## 4. Regole per Code su questo repo
- Le missioni sono testo di Stefano: non riscriverle. Correggere refusi è ok.
- `site/data/progress.json` non si tocca, a parte aggiungere il binario Mind (unica eccezione, in questa sessione).
- Il design si estende, non si sostituisce. Stessi token, stessa fascia, stesse schede.
- Tutto in italiano per Alberto (schede, CONTRIBUTING, THEME), in inglese sul sito.
- Niente trattini lunghi nei testi.
- Ogni PR: descrizione di cosa cambia e come provarlo in locale.
