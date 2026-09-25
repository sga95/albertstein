# Handoff 3 per Claude Code: il capitolo Raspberry Pi

Segue `engine/HANDOFF-2.md`. Stefano regala ad Alberto un Raspberry Pi come loot del Boss 1. Da quel momento il Pi diventa il pezzo fisico del percorso: monitor, DNS, VPN, sonda, router, e le cose creative legate alle sue passioni. Stesse regole degli altri handoff.

Prompt di avvio:

> Leggi `engine/HANDOFF-3.md`. Crea il binario Pi come descritto, in una PR in catena dopo il blocco H. Scrivi `missioni/PI.md` nello stesso formato di `SHIELD.md` e `VOICE.md` (cosa ottieni, perché conta, passi, "è fatta quando", riga CV, "Gratis, prima", prompt per claude.ai). Aggiungi il binario a `progress.json` con `requires`, aggiorna loot, quest, evidence-rules, INIZIA-QUI e la pagina Progress. Il modello del Pi non è ancora noto: scrivi le schede per Pi 4 e Pi 5 con una nota dove un Pi 3 non basta.

---

## Decisioni

1. **Loot del Boss 1 = Raspberry Pi** (già di Stefano). In `data/loot.yaml`: Boss 1 Raspberry Pi con microSD, alimentatore e case; Boss 2 kit ESP32 con OLED e LED; Boss 3 voucher CCNA; Boss 4 switch gestito usato; Boss 5 RTL-SDR; Boss 6 voucher cloud.
2. **Binario `pi`** in `progress.json`, dopo `mind`, con `"requires": {"boss": 1}`: sul sito compare da subito ma con lo stato `sealed` e la riga "Unlocks with Boss 1" finché il boss non è `done`. `app.js` gestisce `requires` in modo generico (boss o missione).
3. Le quest di elettronica in `QUESTS.md` che usano il Pi rimandano ai passi del binario invece di duplicarli.

---

## Binario Pi: "Small computer, whole network"

Dodici passi in ordine, più un boss. Ogni passo produce una nota di lab. Il Pi va tenuto acceso: da qui in poi è un server di casa.

### P1. Primo avvio, senza monitor
Raspberry Pi OS Lite 64-bit, scritto con Raspberry Pi Imager con SSH e chiave pubblica già impostati, utente non `pi`, hostname suo. Prima connessione via SSH dal PC. Poi: IP riservato sul router di casa, `unattended-upgrades`, `fail2ban`, `ufw` con solo SSH. Le regole di Shield applicate a una macchina nuova.
Fatta quando: entra via chiave, la password SSH è disattivata, `ufw status` mostra solo la 22, e il Pi ha lo stesso IP dopo un riavvio.
CV: Headless Linux server setup and hardening.

### P2. Il guardiano in casa
Lo script della missione 6 gira anche sul Pi, con un timer systemd ogni 5 minuti, e scrive su un CSV locale. Confronto dopo una settimana: cosa vede il Pi da dentro casa e cosa vede GitHub Actions da fuori. Le differenze sono la lezione.
Fatta quando: `systemctl list-timers` mostra il timer, il CSV ha una settimana di dati, la nota spiega almeno una differenza tra dentro e fuori.
CV: Scheduled jobs with systemd timers, internal vs external monitoring.

### P3. Pi-hole: il DNS di casa
Pi-hole sul Pi, il router di casa lo usa come DNS. Dopo una settimana: i 10 domini più bloccati, quale dispositivo parla di più, una cosa che non si aspettava. Nota di lab con la spiegazione di come funziona una query DNS che passa da lì.
Fatta quando: tutti i dispositivi di casa risolvono tramite il Pi (`nslookup` lo dimostra) e la nota è online.
CV: DNS sinkhole deployment and home network visibility.

### P4. La lampada di uptime
Un LED (o un Blinkt, o un NeoPixel) sui GPIO: verde se il sito risponde, rosso se no, giallo se lento. Lo comanda lo script di P2. Foto nella nota. È la prima volta che il suo monitor tocca il mondo fisico.
Fatta quando: Stefano rompe il sito (incidente) e la lampada diventa rossa prima che arrivi la issue.
CV: GPIO control from Python, physical status indicators.

### P5. Cruscotto di latenza
Prometheus con `node_exporter` e `blackbox_exporter`, Grafana, tutto sul Pi in Docker (Pi 4 e 5) o smokeping (Pi 3). Bersagli: router di casa, gateway dell'ISP, 1.1.1.1, albertstein.link. Dopo una settimana: a che ora la rete di casa è peggiore e perché.
Fatta quando: il cruscotto esiste, uno screenshot è nella nota, e c'è una risposta con dati alla domanda "qual è il collo di bottiglia di casa".
CV: Metrics and dashboards with Prometheus and Grafana.

### P6. Speedtest con le prove
Speedtest ogni ora (`speedtest-cli` o Ookla CLI), CSV, grafico settimanale generato da uno script Python. Se la banda è sotto quella del contratto in orario serale, la nota diventa una lettera all'ISP con i dati. Utile e divertente.
Fatta quando: quattro settimane di dati, un grafico, e la lettera scritta (spedirla è facoltativo).
CV: Data collection and reporting with Python.

### P7. VPN verso casa
WireGuard sul Pi, porta aperta sul router solo per UDP WireGuard, telefono e PC come peer. Dal 4G: raggiunge Pi-hole e Grafana, il traffico esce dall'IP di casa. Wireshark fuori dal tunnel: cosa si vede e cosa no.
Fatta quando: il telefono in 4G apre Grafana via IP privato, e la nota ha la cattura che dimostra che il contenuto è cifrato.
CV: WireGuard VPN deployment and verification.

### P8. La sonda
Un adattatore USB Ethernet in più. Il Pi in mezzo tra il router e un dispositivo (bridge Linux, o porta mirror se ha uno switch gestito) fa da sonda: `tcpdump` a rotazione, `ntopng` o Zeek per i riepiloghi. Un giorno di traffico di un suo dispositivo, poi la nota: quanti server contatta una TV o una console in 24 ore.
Fatta quando: la nota ha numeri veri e una regola nuova in Pi-hole nata da quello che ha visto.
CV: Passive network monitoring with tcpdump and Zeek or ntopng.

### P9. Il Pi come router
Due interfacce: WAN verso il router di casa, LAN verso lo switch del lab. DHCP (`dnsmasq` o `kea`), NAT e firewall con `nftables`, una VLAN taggata verso il lab di Proxmox se c'è già. Da qui il lab ha il suo edge.
Fatta quando: una VM del lab esce su internet passando dal Pi, `nft list ruleset` è nella nota e ogni regola ha una riga di spiegazione.
CV: Linux as a router: NAT, DHCP, nftables, VLAN tagging.

### P10. Honeypot
Cowrie (SSH finto) sul Pi, esposto su una porta alta con port forward, il vero SSH resta chiuso da fuori. Dopo una settimana: da dove vengono i tentativi, quali utenti e password provano, un grafico per ora del giorno. Poi lo spegne.
Fatta quando: la nota ha i numeri, una mappa o un grafico, e una riga su cosa cambia nel modo in cui protegge le sue cose.
CV: Honeypot deployment and attack log analysis.

### P11. Backup con ripristino
Disco USB sul Pi, `restic` come destinazione dei backup del PC e del lab, cifrati, con retention. Poi il ripristino provato di una cartella e di una VM.
Fatta quando: un file cancellato apposta torna dal backup, e il runbook lo può seguire Stefano.
CV: Encrypted backups with restic and tested restores.

### P12. La bacheca
Uno schermo piccolo (OLED, e-paper, o il display di un vecchio telefono via browser) che mostra: livello attuale del sito letto da `progress.json`, missioni fatte, ping medio dell'ultima ora, stato della lampada. Sta sulla scrivania. Una cosa sua, fatta da lui, che racconta il percorso.
Fatta quando: foto della bacheca accesa nella nota, codice nel repo `pi-board`.
CV: Small display projects: fetching JSON and rendering status.

### Boss Pi: il Pi è la rete
Nessun passo. Per un fine settimana il Pi è router, DNS, VPN e monitor di casa. Stefano, da remoto, prova a: cambiare DNS su un dispositivo, saturare la banda, spegnere il router del lab, entrare via SSH. Alberto deve accorgersi di tutto dal cruscotto e dalla lampada, senza che nessuno in casa noti nulla.
Battuto quando: quattro eventi rilevati e spiegati nella nota con orari, e la famiglia non ha chiamato.
Badge: Ran home network services on a Raspberry Pi for a weekend, under attack.

---

## Note per Code

- Modello: Pi 5 e Pi 4 fanno tutto; Pi 3 salta P5 in Docker (usare smokeping), P8 (troppo lento per Zeek) e P12 con e-paper resta ok. Scrivere le varianti dentro le schede, non in file separati.
- Consumi di scheda: consigliare in P1 `log2ram` e, su Pi 4 e 5, un SSD USB al posto della microSD dal passo P5 in poi. Elencare in P1 il materiale: microSD 32 GB, alimentatore ufficiale, case con dissipatore, adattatore USB Ethernet (per P8 e P9), disco USB (P11), LED e resistenze o Blinkt (P4), OLED SSD1306 (P12). Stefano fornisce il Pi; il resto costa meno di 60 euro totali e si può mettere nel loot del Boss 2.
- Sicurezza: ogni passo che apre una porta (P7, P10) dice esplicitamente cosa resta chiuso e come verificarlo da fuori (`nmap` da un VPS o da 4G).
- "Gratis, prima" per il binario: docs Raspberry Pi, Pi-hole docs, WireGuard quickstart, Prometheus e Grafana getting started, Zeek docs, Cowrie docs, restic docs, nftables wiki. Verificare i link.
- `evidence-rules.yaml`: ogni passo P richiede una nota in `site/lab/` con `pi` nel nome e almeno un'immagine; P4 e P12 richiedono una foto. Skill attestate: linux 2-3, monitoring 2-3, dns 2, vpn 2, firewall 2, python 2, security 2, documentation 2.
- `QUESTS.md`: le quest "lampada di uptime", "sensore di latenza", "Pi-hole" e "network tap" diventano rimandi ai passi P4, P12, P3, P8; la quest "sensore di latenza con ESP32" resta a parte perché usa l'ESP32 del loot 2.
- Pagina Progress: il binario Pi mostra la riga "Unlocks with Boss 1" e le celle grigie finché `requires` non è soddisfatto. Colore delle righe earned del binario: verde scuro, da aggiungere ai token.
- `INIZIA-QUI.md`: una riga nel paragrafo dei binari: "Pi (`PI.md`): parte quando batti il Boss 1 e ricevi il Raspberry".
