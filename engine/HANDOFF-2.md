# Handoff 2 per Claude Code: decisioni, corsi, certificazioni, passioni

Segue `engine/HANDOFF.md` e `engine/BRIEF.md`. Le PR 1-5 sono aperte e in catena. Qui ci sono le decisioni prese e i lavori nuovi. Stesse regole di sempre: non riscrivere le missioni oltre a quanto indicato, non toccare `site/data/progress.json` se non dove detto, design esteso e non rifatto, niente trattini lunghi, italiano per Alberto e inglese sul sito.

Prompt di avvio:

> Leggi `engine/HANDOFF-2.md`. Esegui i blocchi E, F, G, H nell'ordine, una PR per blocco, in catena dopo la PR 5. Le decisioni in "Decisioni prese" non si discutono: applicale. Per tutto il resto scegli tu la strada più semplice che funziona senza servizi a pagamento, e spiegala nella descrizione della PR.

---

## Decisioni prese (da applicare, non da discutere)

1. **Cloudflare: si resta su Workers con asset statici.** Aggiungere `wrangler.jsonc` come proposto nel commento su PR 1 (nome `albertstein`, `assets.directory = "site"`, `compatibility_date` recente, `not_found_handling = "404-page"`). Farlo in una PR separata, la prima da mergiare, così i build sui branch tornano verdi e le anteprime funzionano. Aggiornare `missioni/01.md`, `02.md`, `03.md` e `BOSS-1.md` dove dicono "Pages": ora si chiama Workers, il preview della PR è quello del Workers Build, e "Custom domains" sta in Workers → Settings → Domains & Routes. Le note di lab e il footer non cambiano.
2. **Ordine di merge**: wrangler → PR 1 → 2 → 3 → 4 → 5 → E → F → G → H. Code fa il merge da solo quando la CI è verde, in quest'ordine, e riallinea le basi delle PR successive.
3. **"tuo fratello" diventa "Stefano"** ovunque: `missioni/*`, `INIZIA-QUI.md`, `CONTRIBUTING.md`, `THEME.md`, pagine del sito se compare, `engine/*.md`. Anche "tuo fratello ti manderà" e simili. Nel sito pubblico Stefano compare solo dove serve (mai come autore del sito).
4. **Richiesta certificazioni**: si fa con una issue GitHub da template, non con email o backend. Motivo: zero segreti, zero servizi, resta traccia nel repo, Stefano riceve la mail da GitHub, e Alberto usa le issue come si fa in azienda. Un eventuale Email Worker viene dopo, solo se Stefano lo chiede.

---

## Blocco E: Workers, rename, merge

- `wrangler.jsonc` e aggiornamento dei testi come al punto 1.
- Rename "tuo fratello" → "Stefano" come al punto 3.
- Merge in ordine come al punto 2, dopo aver verificato che `albertstein.link` risponde 200 al termine e che una PR di prova ha l'URL di anteprima.

## Blocco F: corsi gratuiti e richiesta certificazioni

### F1. Corsi gratuiti nelle schede
Aggiungere a ogni missione, livello e binario una sezione **"Gratis, prima"** con 1-3 risorse gratuite che coprono quel passo, con una riga su cosa prendere da ognuna. Usare questa lista come base, verificando che i link siano vivi e senza carta di credito:

- Rete: Cisco Networking Academy "Networking Basics" e "Networking Devices and Initial Configuration" (gratuiti, con Packet Tracer); Jeremy's IT Lab su YouTube (corso CCNA completo, gratuito, con lab); Practical Networking (practicalnetworking.net); il libro "High Performance Browser Networking" (gratis online) per la parte web.
- Linux e terminale: "The Linux Command Line" di Shotts (PDF gratuito); OverTheWire Bandit (gioco a livelli su terminale); Linux Foundation LFS101 su edX (gratis in audit); Linux Journey.
- Git: GitHub Skills (corsi interattivi gratuiti); "Pro Git" (libro gratuito); Learn Git Branching (gioco).
- Python: freeCodeCamp Scientific Computing with Python; Automate the Boring Stuff (gratis online); Exercism track Python.
- Sicurezza: TryHackMe percorsi gratuiti (Pre Security, Intro to Cyber Security); Hack The Box Academy moduli Tier 0 gratuiti; picoCTF; Bitwarden e Proton learning center per Shield.
- Cloud: Microsoft Learn percorso AZ-900 (gratis, completo); AWS Skill Builder corsi gratuiti e AWS Cloud Quest; Cloudflare Learning Center e docs Workers.
- Automazione e IaC: Ansible "Getting Started" e workshop ufficiali; HashiCorp Terraform tutorials; Docker "Getting Started" guide; NetBox docs e demo pubblica; Containerlab docs e lab di esempio.
- Inglese e comunicazione: BBC Learning English; Coursera "English for Career Development" in audit; Toastmasters materiali gratuiti; TED con trascrizioni.
- AI (binario Mind): corso gratuito Anthropic su prompting (docs), "Intro to Large Language Models" di Karpathy su YouTube, Google AI Essentials in audit.
- Ricerca lavoro: guide LinkedIn gratuite, Coursera "Interviewing" in audit, materiali dell'ufficio placement universitario.

Formato nella scheda:

```
## Gratis, prima
- Jeremy's IT Lab, video 1-15: i concetti di base, con i lab in Packet Tracer.
- Cisco NetAcad "Networking Basics": per i quiz e i badge da mettere su LinkedIn.
```

### F2. Certificazioni: catalogo e richiesta
- `data/certs.yaml`: per ogni certificazione `id, name, vendor, cost_eur, prereq_steps (missioni o passi da avere done), study_free (link), exam_url, why (una riga), roles (id dei ruoli in roles.yaml)`. Includere almeno: CCNA 200-301, CompTIA Network+, CompTIA Security+, AWS Cloud Practitioner, AZ-900, LPIC-1 (o Linux Foundation LFCA), HashiCorp Terraform Associate, TryHackMe o HTB voucher come "cert leggera", corso Udemy a scelta come categoria "corso a pagamento".
- Pagina `site/certs/index.html` (stessa fascia e schede): tabella certificazioni con stato: **locked** (mancano i prerequisiti, elencati), **ready** (prerequisiti done: compare il pulsante), **requested**, **granted**, **passed**. Lo stato `requested/granted/passed` sta in `data/certs-status.json`, che Stefano aggiorna (o Code, su suo comando).
- Il pulsante "Chiedi a Stefano" apre una issue GitHub precompilata con un template in `.github/ISSUE_TEMPLATE/cert-request.yml`: certificazione, perché ora, quando vuoi fare l'esame, cosa hai già fatto per prepararti (campi obbligatori), label `cert-request`, assegnata a `sga95`. Stefano riceve la notifica da GitHub. Quando chiude la issue con label `granted`, un workflow (`cert-status.yml`) aggiorna `certs-status.json` e riapre la pagina con stato `granted`. Quando Alberto aggiunge il badge o il certificato in `site/certs/proof/`, lo stato passa a `passed` con un commit suo.
- Il pulsante compare solo se `ready`. La logica dei prerequisiti riusa `progress.json`, in `app.js`, senza nuova libreria.
- In `HIRE.md` e in `LIVELLO-6.md` (missione 17) e `08.md` (CCNA) aggiungere la riga: "La certificazione la chiedi dalla pagina /certs quando i prerequisiti sono verdi. L'esame lo paga Stefano."
- Aggiungere "Certs" alla nav tramite `site.json`.

## Blocco G: passioni e creatività

Alberto: gaming, libri, rompicapo, scienza, elettronica. Tutto quello che segue è opzionale per lui e non blocca nulla, ma ogni cosa vale una nota di lab e alcune sono le ricompense dei boss.

### G1. Quest board per passione
Sostituire `missioni/SIDE-QUESTS.md` con `missioni/QUESTS.md`, organizzato per passione, e mostrarlo sul sito in `site/quests/index.html` (schede per categoria, stato da `progress.json` sezione nuova `quests: [{id, title, done}]`, unica aggiunta permessa al file). Le side quest esistenti restano, ricollocate. Aggiungere:

**Gaming**
- Game server sul lab: un server Minecraft o Valheim su una VM Proxmox, in una VLAN sua, esposto agli amici via Cloudflare Tunnel o port forward con regole firewall. Monitorato dal suo monitor. Nota: cosa succede alla latenza con 5 giocatori.
- Netcode con Wireshark: cattura di una partita online (qualsiasi gioco): quanti pacchetti al secondo, UDP o TCP, cosa cambia con il lag. Spiegare perché i giochi usano UDP.
- Lag lab: con `tc` su Linux aggiungere 100 ms di latenza e 2% di perdita tra due VM e misurare l'effetto su un gioco o su SSH.
- Speedrun: rifare la missione 1 o il Boss 4 cronometrati e pubblicare il tempo in `/quests`. Solo contro se stesso.

**Rompicapo**
- Subnetting sprint: 20 esercizi di subnetting in 10 minuti (generatore in `tools/subnet_quiz.py`, senza LLM), tempo e punteggio in `/quests`.
- OverTheWire Bandit fino al livello 20; Advent of Code in Python, almeno 5 giorni; picoCTF, 5 sfide di rete o crittografia.
- Un rompicapo a settimana: pagina `/puzzle` con un enigma di rete o Linux scritto da Stefano (file `data/puzzles.yaml`, una entry a settimana, soluzione nascosta finché non passa la settimana).

**Elettronica**
- Lampada di uptime: un ESP32 o un Raspberry Pi Pico W che interroga il sito ogni minuto e accende un LED verde o rosso. Collega la missione 6 a qualcosa di fisico. Foto nella nota.
- Sensore di latenza: ESP32 che pinga il router di casa e mostra i millisecondi su un display OLED.
- Pi-hole su Raspberry Pi (già presente): estenderla con un grafico settimanale.
- Network tap passivo con due porte e un Raspberry Pi che fa da sonda Wireshark per il lab.

**Scienza**
- "Come fa davvero": una nota di lab per domanda: quanto ci mette la luce da Bergamo a Francoforte e perché il ping è di più; come è fatto un cavo sottomarino; cosa succede fisicamente in un cavo Ethernet quando passa un bit. Con misure sue dove possibile (traceroute, ping verso data center noti).
- Radio: SDR economica (RTL-SDR) per vedere Wi-Fi, LoRa o ADS-B; capire lo spettro prima di studiare il wireless del CCNA.

**Libri**
- Reading log in `site/reading/`: un libro tecnico ogni due mesi, una nota per libro con tre cose che cambia nel suo modo di lavorare. Lista di partenza (gratuiti dove indicato): The Linux Command Line (gratis), Pro Git (gratis), High Performance Browser Networking (gratis), Computer Networking: A Top-Down Approach (biblioteca), The Phoenix Project (romanzo, per capire il lavoro in IT), Julia Evans "Networking zines".

### G2. Loot: le ricompense dei boss
`data/loot.yaml`: ogni boss ha una ricompensa fisica o un voucher che Stefano ha scelto. Sul sito, in `/progress`, ogni boss mostra "Loot: ..." solo quando è `done`; prima mostra "Loot: sealed". Esempi da mettere come default, che Stefano può cambiare: Boss 1 un libro dalla reading list; Boss 2 un Raspberry Pi 5 o un mini PC usato per il lab; Boss 3 il voucher CCNA; Boss 4 uno switch gestito usato; Boss 5 un RTL-SDR o un ESP32 kit; Boss 6 il voucher cloud. Il loot si "riscatta" con la stessa issue template delle certificazioni, tipo `loot`.

### G3. Nomi e tono
- Livelli e badge restano come sono. Aggiungere a ogni livello un titolo alternativo "da gioco" in `site.json` che Alberto può attivare o no (esempio: Recruit, Operator, Guardian... già a posto; aggiungere solo la possibilità di rinominarli).
- Pagina `/codex`: glossario suo, una voce per ogni termine che ha capito davvero, con la definizione a parole sue. Lint: massimo 40 parole per voce. Cresce con le note.

### G4. Sito
- Nav: `Quests`, `Certs` visibili; `Puzzle`, `Reading`, `Codex` attivabili da `site.json` (default: visibili quando hanno almeno una voce).
- Home: sotto le note, una scheda "Now playing" con l'ultima quest aperta, se c'è.

## Blocco H: documentazione

- Aggiornare `INIZIA-QUI.md`: sezione "Ricompense e certificazioni" (come si chiedono, chi paga), sezione "Quest" (opzionali, per passione).
- Aggiornare `engine/HANDOFF.md`: stato dopo i merge, decisione Workers, nuove pagine e file dati. Il BRIEF resta valido; aggiungere in `evidence-rules.yaml` le quest e le cert come evidenze (le cert `passed` valgono livello 3 sulle skill del loro ruolo).
- `README.md`: nuove pagine e comandi.

---

## Cose per Stefano (Code le elenca nella PR finale)
- Sostituire `ALBERTO-GITHUB` (se non ancora fatto).
- Impostare le notifiche GitHub per la label `cert-request` e `loot`, o "Watch: all activity" sul repo.
- Rivedere `data/loot.yaml` e `data/certs.yaml` (costi e scelte).
- Scrivere il primo puzzle in `data/puzzles.yaml`.
- Fase 2 del BRIEF: secret `ANTHROPIC_API_KEY` quando vuole gli agenti.
