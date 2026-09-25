# Handoff 4 per Claude Code: chiudere tutto da solo

Obiettivo: nessun passaggio manuale di Stefano oltre a due chiavi. Code deve poter vedere Cloudflare, sistemare il build, mergiare la catena e attivare le protezioni.

## Prerequisiti (Stefano, una volta, 3 minuti)

Questa sessione va lanciata **in locale** sul PC di Stefano, non nella sandbox web: serve rete verso Cloudflare e GitHub.

1. `gh auth login` già fatto (o `GH_TOKEN` con scope `repo`, `workflow`, `admin:repo_hook`).
2. Token Cloudflare: dash.cloudflare.com → profilo → API Tokens → Create Token → template "Edit Cloudflare Workers", e aggiungere i permessi Account: **Workers Builds Configuration: Edit**, **Workers Scripts: Edit**, **Account Settings: Read**. Esportare:
   ```
   export CLOUDFLARE_API_TOKEN=...
   export CLOUDFLARE_ACCOUNT_ID=5b3fd438bde5e60f93c4546578fbf0f6
   ```
3. Username GitHub di Alberto in `ALBERTO_GITHUB=...` (se non lo sa ancora, Code lo chiede una volta e si ferma finché non arriva).
4. Facoltativo, per la Fase 2 del BRIEF: `ANTHROPIC_API_KEY` come secret del repo (`gh secret set ANTHROPIC_API_KEY`).

Prompt di avvio:

> Leggi `engine/HANDOFF-4.md` e fai tutto in ordine, senza chiedermi conferme salvo dove il file lo dice. Hai `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `gh` autenticato e `ALBERTO_GITHUB`. Alla fine scrivi un riepilogo in `engine/STATUS.md` con cosa è online, cosa è mergiato, cosa resta.

## Passi

### 1. Cloudflare: capire e sistemare il build
- Con l'API (`GET /accounts/{id}/workers/scripts`, `GET /accounts/{id}/builds/workers/albertstein/builds`, `GET .../builds/{build_id}/logs`) leggere il log dell'ultimo build fallito. Non tirare a indovinare: leggere il log.
- Leggere la configurazione build (`GET /accounts/{id}/builds/workers/albertstein/config`). Impostarla via `PATCH` a: build command vuoto, deploy command `npx wrangler deploy`, root directory `/`, build su tutti i branch abilitato, variabile `NODE_VERSION=20` se manca.
- Tenere un solo `wrangler.jsonc`, alla radice; rimuovere la copia in `site/` se c'è. Verificare in locale con `npx wrangler deploy --dry-run` (usa `assets.directory = "site"`).
- Rilanciare il build della PR 6 (`POST .../builds` con il branch, oppure un commit vuoto). Deve diventare verde e restituire un URL di anteprima. Se fallisce ancora, incollare il log nella PR 6 e fermarsi qui: è l'unico punto in cui Stefano deve intervenire.

### 2. Merge della catena
- Ordine: 6 → 1 → 2 → 3 → 4 → 5 → 7 → 8 → 9 → 10 → 11. Per ogni PR: rebase sulla base aggiornata se serve, attesa CI verde (`ci.yml`; il check Cloudflare deve essere verde dopo il passo 1), merge con squash, poi `curl -I https://albertstein.link` deve dare 200 e le pagine nuove (`/certs`, `/quests`, `/gear`, `/readiness`) devono rispondere 200 quando la PR che le introduce è mergiata.
- Prima di mergiare la 9 e la 11: sostituire `ALBERTO-GITHUB` con `$ALBERTO_GITHUB` in `.github/CODEOWNERS` e `.github/workflows/guard-progress.yml` in una PR piccola, mergiata prima di loro.
- Se un merge rompe il sito vero: revert immediato, nota nella PR, si continua con le altre.

### 3. Protezioni e accessi (via `gh api`)
- Branch protection su `main`: PR obbligatoria, review da code owner obbligatoria, `ci.yml` come check richiesto, niente force push. Gli admin possono bypassare (serve a Stefano per le emergenze).
- Invitare `$ALBERTO_GITHUB` come collaboratore con permesso `push`.
- Etichette `cert-request`, `loot`, `gear`, `uptime` create nel repo con colori. Verificare che i template issue le usino.
- Notifiche: aggiungere Stefano come assignee di default nei template issue di richiesta (già previsto) e verificare che il workflow `cert-status` abbia i permessi `issues: read, contents: write`.

### 4. Cloudflare: Alberto
- Con l'API inviare l'invito membro (`POST /accounts/{id}/members`) all'email di Alberto con ruolo DNS, se `ALBERTO_EMAIL` è impostata; altrimenti saltare e segnare in STATUS.md.

### 5. Verifica finale
- Aprire in Chromium headless home, CV, progress, quests, certs, gear, readiness: screenshot in `engine/screenshots/` (non nel sito), controllare che il progresso sia tutto a zero, che i binari Shield, Mind, Voice, Hire siano `open` sul primo passo e Pi `sealed`.
- `make check` verde su `main`.
- `engine/STATUS.md`: stato, URL, cosa manca (foto, email Proton, repo pubblico), prossimo passo consigliato.

### 6. Se `ANTHROPIC_API_KEY` è presente
- Procedere con la Fase 2 del `BRIEF.md` (coach, reviewer, validator, english, lint), una PR, con il tetto di spesa settimanale impostato a 5 euro in `engine/config.yaml` e un test a secco (`--dry-run`) di ogni agente che non chiama l'API.
