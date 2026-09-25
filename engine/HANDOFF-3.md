# Handoff 3 per Claude Code: il capitolo Raspberry Pi

Segue `HANDOFF.md`, `BRIEF.md`, `HANDOFF-2.md`. Stefano regala ad Alberto un Raspberry Pi come loot del Boss 1. Da quel momento il Pi è il pezzo fisico del percorso: monitor, DNS, VPN, sonda, router, backup, sensori, gioco. Ogni progetto è piccolo, utile in casa da subito, e produce una nota di lab con una foto.

Prompt di avvio:

> Leggi `engine/HANDOFF-3.md`. Crea il binario `pi` come descritto, in una PR in catena dopo il blocco H. Scrivi `missioni/PI.md` nello stesso formato di `SHIELD.md` e `VOICE.md` (cosa ottieni, perché conta, hardware, passi, "Gratis, prima", "è fatta quando", riga CV, prompt per claude.ai). Aggiungi il binario a `progress.json` con `requires` (unica modifica ammessa al file), la pagina `/gear`, e aggiorna loot, quest, evidence-rules, INIZIA-QUI, README e la pagina Progress. Il modello del Pi non è ancora noto: scrivi per Pi 4 e Pi 5 con una nota dove un Pi 3 non basta. Stesse regole: nessun trattino lungo, italiano nelle schede, inglese sul sito, design esteso non rifatto, nessun servizio a pagamento.

---

## Decisioni

1. **Loot del Boss 1 = Raspberry Pi** (già di Stefano), con microSD, alimentatore e case. `data/loot.yaml`: Boss 2 kit ESP32 con OLED, LED e BME280; Boss 3 voucher CCNA; Boss 4 switch gestito usato; Boss 5 RTL-SDR; Boss 6 voucher cloud.
2. **Binario `pi`** in `progress.json`, dopo `mind`, con `"requires": {"boss": 1}`: sul sito compare da subito ma con stato `sealed` e la riga "Unlocks with Boss 1" finché il boss non è `done`. `app.js` gestisce `requires` in modo generico (boss o missione). Colore proprio per le righe earned del binario.
3. **Hardware extra** (adattatore USB Ethernet, disco USB, sensori, SDR) si chiede dalla pagina `/gear` con lo stesso template issue di certificazioni e loot (`type: gear`). Stefano compra.
4. Le quest di elettronica in `QUESTS.md` che usano il Pi rimandano ai passi del binario invece di duplicarli.
5. Tutto headless: nessun monitor collegato al Pi, tutto via SSH. È il modo in cui si lavora su un server.

---

## Binario Pi: "One small computer, the whole home network"

Quindici passi e un boss. I primi tre in ordine (sono il setup), poi libero. Il Pi resta acceso: da qui in poi è un server di casa.

### P1. Primo avvio, senza monitor
Raspberry Pi OS Lite 64-bit scritto con Imager con SSH e chiave pubblica già dentro, utente non `pi`, hostname suo. Prima connessione via SSH dal PC. Poi: IP riservato sul router di casa, `unattended-upgrades`, `fail2ban`, `ufw` con solo SSH, `log2ram` per salvare la microSD. Le regole di Shield applicate a una macchina nuova. Prima nota: cosa vede `nmap` del Pi da un altro PC prima e dopo il firewall.
Fatta quando: entra solo con la chiave, la password SSH è disattivata, `ufw status` mostra solo la 22, stesso IP dopo un riavvio, i due scan nella nota.
CV: Headless Linux server setup and hardening.

### P2. Il guardiano in casa
Lo script della missione 6 gira anche sul Pi con un timer systemd ogni 5 minuti e scrive su un CSV locale. Dopo una settimana: confronto tra cosa vede il Pi da dentro casa e cosa vede GitHub Actions da fuori. Le differenze sono la lezione.
Fatta quando: `systemctl list-timers` mostra il timer, il CSV ha una settimana di dati, la nota spiega almeno una differenza tra dentro e fuori.
CV: Scheduled jobs with systemd timers, internal vs external monitoring.

### P3. La lampada di uptime
Un LED verde e uno rosso sui GPIO (o Blinkt, o NeoPixel): verde se il sito risponde, rosso se no, giallo se lento. Lo comanda lo script di P2. È la prima volta che il suo monitor tocca il mondo fisico.
Hardware: 2 LED e resistenze (2 euro) o Blinkt (10 euro).
Fatta quando: Stefano rompe il sito (incidente) e la lampada diventa rossa prima che arrivi la issue. Foto nella nota.
CV: GPIO control from Python, physical status indicators.

### P4. Pi-hole: il DNS di casa
Pi-hole sul Pi, il router lo usa come DNS, upstream cifrato (Unbound ricorsivo o DoH). Dopo una settimana: i 10 domini più bloccati, quale dispositivo parla di più, cosa fa la TV di notte. È la missione 2 vista dall'altro lato: il DNS come servizio da gestire.
Fatta quando: tutti i dispositivi di casa risolvono tramite il Pi (`nslookup` lo dimostra), Unbound risponde, la nota ha i numeri della settimana.
CV: Running a home DNS resolver with filtering and recursive upstream.

### P5. Chi c'è in casa
Scansione ARP e `nmap` ogni 10 minuti: inventario (MAC, vendor, IP, hostname, porte aperte) in YAML. Avviso sul telefono quando compare un dispositivo nuovo, via `ntfy.sh` (gratuito). L'inventario è il seme di NetBox alla missione 16.
Fatta quando: ogni dispositivo ha un nome dato da lui, e un avviso è arrivato quando Stefano o un amico ha collegato qualcosa di nuovo.
CV: Network discovery, asset inventory, change alerts.

### P6. Cruscotto di latenza e banda
Prometheus con `node_exporter` e `blackbox_exporter`, Grafana, in Docker (Pi 4 e 5) o smokeping (Pi 3). Bersagli: router di casa, gateway dell'ISP, 1.1.1.1, un data center a Milano e uno a Francoforte, albertstein.link. Speedtest ogni ora con grafico settimanale. Dopo due settimane: a che ora la rete di casa è peggiore e perché, e se la banda serale è sotto quella del contratto la nota diventa una lettera all'ISP con i dati.
Fatta quando: cruscotto con screenshot nella nota, e una risposta con dati alla domanda "qual è il collo di bottiglia di casa".
CV: Metrics and dashboards with Prometheus and Grafana, ISP performance evidence.

### P7. VPN verso casa
WireGuard sul Pi, porta aperta sul router solo per UDP WireGuard, telefono e PC come peer. Dal 4G: raggiunge Pi-hole e Grafana, il traffico esce dall'IP di casa. Wireshark fuori dal tunnel: cosa si vede e cosa no. Alternativa senza porte aperte: Cloudflare Tunnel (missione 20).
Fatta quando: il telefono in 4G apre Grafana via IP privato, e la nota ha la cattura che dimostra il contenuto cifrato.
CV: WireGuard VPN deployment and verification.

### P8. La sonda
Adattatore USB Ethernet in più. Il Pi in mezzo tra router e un dispositivo (bridge Linux, o porta mirror se c'è lo switch gestito): `tcpdump` a rotazione, `tshark` per statistiche, `ntopng` o Zeek per i riepiloghi (da Pi 4), cattura remota da Wireshark sul portatile via SSH. Un giorno di traffico di una TV o di una console: quanti server contatta in 24 ore.
Hardware: adattatore USB Ethernet (10 euro).
Fatta quando: la nota ha numeri veri, tre scoperte sulla rete di casa e una regola nuova in Pi-hole nata da quello che ha visto.
CV: Passive network monitoring with tcpdump, tshark and Zeek or ntopng.

### P9. Il Pi come router
Due interfacce: WAN verso il router di casa, LAN verso lo switch del lab. DHCP con `dnsmasq`, NAT e firewall con `nftables`, una VLAN taggata (802.1Q) verso il lab di Proxmox se c'è già. Da qui il lab ha il suo edge. È la missione 14 su hardware vero, prima di OPNsense.
Fatta quando: una VM del lab esce su internet passando dal Pi e non vede la rete di casa (provato con `tcpdump`), `nft list ruleset` è nella nota e ogni regola ha una riga di spiegazione.
CV: Linux as a router: NAT, DHCP, nftables, VLAN tagging.

### P10. Honeypot
Cowrie (SSH finto) sul Pi, esposto su una porta alta con port forward, il vero SSH resta chiuso da fuori. Dopo una settimana: da dove vengono i tentativi, quali utenti e password provano, un grafico per ora del giorno. Poi lo spegne.
Fatta quando: la nota ha i numeri, un grafico, e una riga su cosa cambia nel modo in cui protegge le sue cose.
CV: Honeypot deployment and attack log analysis.

### P11. Backup con ripristino
Disco USB sul Pi, `restic` come destinazione dei backup del PC e del lab, cifrati, con retention. Gitea sul Pi come mirror dei suoi repo GitHub. Poi il ripristino provato di una cartella e di una VM. Collega la missione 12.
Hardware: disco USB 500 GB (30 euro).
Fatta quando: un file cancellato apposta torna dal backup, il mirror è all'ultimo commit, e il runbook lo può seguire Stefano.
CV: Encrypted backups with restic, tested restores, self-hosted git mirror.

### P12. Sensori e MQTT
BME280 su I2C sul Pi, Mosquitto come broker MQTT, un ESP32 che pubblica ogni minuto da un'altra stanza, Grafana che mostra tutto. Wireshark su MQTT: si legge tutto in chiaro; poi TLS sul broker. IoT fatto come si deve.
Hardware: kit del loot Boss 2 (BME280, ESP32, jumper).
Fatta quando: due sensori su Grafana, cattura prima e dopo TLS nella nota.
CV: MQTT, IoT sensors, securing a broker with TLS.

### P13. La bacheca
Uno schermo piccolo (OLED SSD1306 o e-paper 2.13") sulla scrivania: livello attuale del sito letto da `progress.json`, missioni fatte, giorni all'esame CCNA, ping medio dell'ultima ora, stato della lampada. Codice nel repo `pi-board`. Una cosa sua che racconta il percorso.
Hardware: OLED (5 euro) o e-paper (20-25 euro).
Fatta quando: foto della bacheca accesa nella nota.
CV: Small display projects: fetching JSON and rendering status.

### P14. Gioco e radio (uno o entrambi)
- Gioco: server Minecraft (PaperMC) o Valheim su Pi 4/5 nella rete lab di P9, raggiungibile dagli amici via WireGuard; latenza misurata con P6 con 4 giocatori. Oppure RetroPie su una seconda microSD e una partita in rete con Stefano attraverso la VPN.
- Radio: RTL-SDR sul Pi: `dump1090` mostra gli aerei sopra Bergamo su una mappa locale, `rtl_433` legge i sensori a 433 MHz del vicinato. Capire lo spettro prima del wireless del CCNA.
Hardware: RTL-SDR (30 euro, loot Boss 5).
Fatta quando: una serata di gioco riuscita con nota sulla latenza, oppure la mappa degli aerei con 24 ore di dati.
CV: Hosting a multiplayer game server / Software-defined radio basics.

### P15. Pi in a box
Tutto quello che ha fatto sul Pi rifatto da zero con Ansible in meno di un'ora: OS nuovo, playbook, backup ripristinato, servizi su. Repo `pi-ansible` pubblico con README che spiega ogni ruolo. Se il Pi muore, ne compra un altro e in un'ora è tutto come prima. È la versione piccola del Boss 4.
Fatta quando: cronometro sotto i 60 minuti, log della sessione nella nota.
CV: Reproducible server from code with Ansible.

### Boss Pi: il Pi è la rete
Nessun passo. Per un fine settimana il Pi è router, DNS, VPN e monitor di casa. Stefano, da remoto e senza avvisare, prova a: cambiare DNS su un dispositivo, saturare la banda, spegnere il router del lab, entrare via SSH. Alberto deve accorgersi di tutto dal cruscotto e dalla lampada, senza che nessuno in casa noti nulla.
Battuto quando: quattro eventi rilevati e spiegati nella nota con orari, e la famiglia non ha chiamato.
Badge: Ran home network services on a Raspberry Pi for a weekend, under attack.

---

## Pagina `/gear` e `data/hardware.yaml`

- `data/hardware.yaml`: per ogni oggetto `id, name, cost_eur, for (passi P*, missioni, quest), status (owned|requested|granted|arrived)`. Precompilare: Raspberry Pi (owned), alimentatore ufficiale, microSD 32 GB, case con dissipatore, SSD USB (consigliato da P6 su Pi 4 e 5), LED e resistenze o Blinkt, OLED SSD1306, e-paper 2.13", adattatore USB Ethernet, disco USB 500 GB, BME280, ESP32, RTL-SDR, mini PC usato (livello 4), switch gestito 8 porte (loot Boss 4).
- Kit da comprare insieme, come nota in pagina: "Kit lampada" (LED, resistenze, OLED, jumper, 12 euro), "Kit sensori" (BME280, ESP32, 15 euro), "Kit rete" (USB Ethernet, cavi, 15 euro). Tutto il non-loot costa meno di 60 euro.
- Pagina `/gear`: tabella con stato e per quale passo serve; pulsante "Chiedi a Stefano" che apre la issue con template `gear` (oggetto, per quale passo, link a un'offerta, perché adesso). Un oggetto è richiedibile quando almeno un passo che lo usa è `open`.

## Note per Code

- Modello: Pi 5 e Pi 4 fanno tutto; Pi 3 usa smokeping in P6, salta Zeek in P8, niente server di gioco in P14. Varianti dentro le schede, non file separati.
- Sicurezza: ogni passo che apre una porta (P7, P10) dice cosa resta chiuso e come verificarlo da fuori (`nmap` da 4G o da un VPS).
- "Gratis, prima": docs Raspberry Pi, Pi-hole, WireGuard quickstart, Prometheus e Grafana getting started, Zeek, Cowrie, restic, nftables wiki, Mosquitto. Verificare i link.
- `evidence-rules.yaml`: ogni passo richiede una nota in `site/lab/` con `pi` nel nome e almeno un'immagine; P3 e P13 richiedono una foto. Skill: linux 2-3, monitoring 2-3, dns 2, vpn 2, firewall 2, python 2, security 2, iot 2, backup 2, documentation 2.
- `QUESTS.md`: "lampada di uptime", "Pi-hole", "network tap", "sensore di latenza" diventano rimandi a P3, P4, P8, P12.
- Missioni esistenti: `06.md` rimanda a P2; `LIVELLO-4.md` missione 12 a P11; `LIVELLO-5.md` missione 14 a P9, missione 16 a P5 e P6.
- Progress: il binario mostra "Unlocks with Boss 1" e celle grigie finché `requires` non è soddisfatto.
- `INIZIA-QUI.md`: una riga nei binari: "Pi (`PI.md`): parte quando batti il Boss 1 e ricevi il Raspberry. Prima puoi leggere P1-P3 e preparare la microSD."
