# Binario Pi: un computer piccolo, tutta la rete di casa

Quindici passi e un boss. Parte quando batti il Boss 1 e ricevi il Raspberry Pi da Stefano: fino ad allora sul sito il binario è sigillato, ma P1-P3 li puoi leggere e la microSD la puoi preparare. I primi tre passi vanno in ordine (sono il setup), poi vai dove ti porta la curiosità. Il Pi resta acceso: da qui in poi è un server di casa, e tu sei il suo amministratore.

Tutto **headless**: nessun monitor collegato al Pi, tutto via SSH dal tuo PC. È il modo in cui si lavora su un server vero.

Ogni passo produce una nota di lab con `pi` nel nome (`site/lab/2026-xx-xx-pi-...html`) e almeno una foto o uno screenshot: è quello che il motore controlla.

**Modello:** Pi 5 e Pi 4 fanno tutto. Con un Pi 3 cambiano tre cose, segnate nei passi: P6 usa smokeping al posto di Prometheus e Grafana, P8 salta Zeek, P14 non fa il server di gioco. Scrivi il modello nella prima nota.

**Hardware:** tutto quello che non è loot è nella pagina `/gear` e si chiede a Stefano da lì, con la stessa issue delle certificazioni. Tre kit da 12, 15 e 15 euro coprono tutto il binario.

## Gratis, prima

- P1: [documentazione Raspberry Pi, "Getting started"](https://www.raspberrypi.com/documentation/computers/getting-started.html) e la pagina su [Raspberry Pi Imager](https://www.raspberrypi.com/software/): SSH e chiave pubblica si mettono da Imager prima del primo avvio.
- P1: [The Linux Command Line](https://linuxcommand.org/tlcl.php) (già dalla missione 5) e [Linux Journey](https://linuxjourney.com/) per systemd, permessi e log.
- P2: [Arch Wiki, "systemd/Timers"](https://wiki.archlinux.org/title/Systemd/Timers): la pagina più chiara che c'è sui timer, vale per ogni distribuzione.
- P3: [documentazione gpiozero](https://gpiozero.readthedocs.io/): LED in cinque righe di Python.
- P4: [documentazione Pi-hole](https://docs.pi-hole.net/) e la guida [Pi-hole con Unbound](https://docs.pi-hole.net/guides/dns/unbound/).
- P5: [Nmap reference guide](https://nmap.org/book/man.html) e [ntfy.sh docs](https://docs.ntfy.sh/): notifiche sul telefono, gratis.
- P6: [Prometheus "Getting started"](https://prometheus.io/docs/prometheus/latest/getting_started/), [Grafana "Get started"](https://grafana.com/docs/grafana/latest/getting-started/), [smokeping](https://oss.oetiker.ch/smokeping/) per il Pi 3.
- P7: [WireGuard quick start](https://www.wireguard.com/quickstart/): due pagine, poi lo fai.
- P8: [documentazione Zeek](https://docs.zeek.org/en/current/) e [tcpdump examples](https://www.tcpdump.org/manpages/tcpdump.1.html); [ntopng docs](https://www.ntop.org/guides/ntopng/).
- P9: [nftables wiki, "Quick reference"](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes) e [dnsmasq man page](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html).
- P10: [Cowrie docs](https://cowrie.readthedocs.io/).
- P11: [restic docs](https://restic.readthedocs.io/) e [Gitea docs](https://docs.gitea.com/).
- P12: [Mosquitto docs](https://mosquitto.org/documentation/) e la [guida MQTT di HiveMQ](https://www.hivemq.com/mqtt/mqtt-essentials/) (gratis, molto chiara).
- P13: [documentazione della libreria luma.oled](https://luma-oled.readthedocs.io/) o [Waveshare e-paper wiki](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT).
- P14: [PaperMC docs](https://docs.papermc.io/), [RetroPie docs](https://retropie.org.uk/docs/), [RTL-SDR quick start](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/).
- P15: [Ansible "Getting started"](https://docs.ansible.com/ansible/latest/getting_started/index.html) (già dalla missione 11).

---

## P1. Primo avvio, senza monitor

Raspberry Pi OS Lite 64-bit scritto sulla microSD con Imager: SSH attivo, la tua chiave pubblica già dentro, utente con un nome tuo (non `pi`), hostname tuo. Prima connessione via SSH dal PC. Poi, in ordine: IP riservato sul router di casa (prenotazione DHCP), `unattended-upgrades`, `fail2ban`, `ufw` con solo la 22, `log2ram` per non consumare la microSD. Sono le regole di Shield applicate a una macchina nuova. Prima nota: cosa vede `nmap` del Pi da un altro PC prima e dopo il firewall.

**Hardware:** il Pi del loot con microSD, alimentatore e case. Niente monitor, niente tastiera.

**Fatta quando:** entra solo con la chiave e la password SSH è disattivata (`PasswordAuthentication no`), `ufw status` mostra solo la 22, stesso IP dopo un riavvio, i due scan `nmap` nella nota.

**Riga CV:** Headless Linux server setup and hardening

**Prompt:** Sto configurando un Raspberry Pi senza monitor, via SSH. Voglio applicare: solo chiave SSH, fail2ban, ufw, aggiornamenti automatici. Spiegami cosa fa ogni pezzo e chiedimi l'output dei comandi per controllare che sia giusto. Non darmi uno script pronto.

## P2. Il guardiano in casa

Lo script della missione 6 gira anche sul Pi, con un timer systemd ogni 5 minuti, e scrive su un CSV locale. Dopo una settimana: confronto tra cosa vede il Pi da dentro casa e cosa vede GitHub Actions da fuori. Le differenze (tempi, errori, orari) sono la lezione.

**Fatta quando:** `systemctl list-timers` mostra il timer, il CSV ha una settimana di dati, la nota spiega almeno una differenza tra dentro e fuori e perché c'è.

**Riga CV:** Scheduled jobs with systemd timers, internal vs external monitoring

## P3. La lampada di uptime

Un LED verde e uno rosso sui GPIO (o un Blinkt, o una striscia NeoPixel): verde se il sito risponde, rosso se no, giallo se è lento. Lo comanda lo script di P2. È la prima volta che il tuo monitor tocca il mondo fisico.

**Hardware:** 2 LED e 2 resistenze da 330 ohm (2 euro) oppure un Blinkt (10 euro). Kit lampada in `/gear`.

**Fatta quando:** Stefano rompe il sito (incidente) e la lampada diventa rossa prima che arrivi la issue. Foto nella nota, con l'orario.

**Riga CV:** GPIO control from Python, physical status indicators

## P4. Pi-hole: il DNS di casa

Pi-hole sul Pi, il router di casa lo usa come DNS, upstream cifrato (Unbound ricorsivo, o DoH). Dopo una settimana: i 10 domini più bloccati, quale dispositivo parla di più, cosa fa la TV di notte. È la missione 2 vista dall'altro lato: il DNS come servizio da gestire, non solo da configurare.

**Fatta quando:** tutti i dispositivi di casa risolvono tramite il Pi (`nslookup` da un telefono lo dimostra), Unbound risponde (`dig @127.0.0.1 -p 5335`), la nota ha i numeri della settimana.

**Riga CV:** Running a home DNS resolver with filtering and recursive upstream

**Prompt:** Ho Pi-hole su un Raspberry e voglio mettere Unbound come upstream ricorsivo. Spiegami la differenza tra forwarding e ricorsione, cosa cambia per la privacy, e fammi domande per verificare che ho capito prima di ogni comando.

## P5. Chi c'è in casa

Scansione ARP e `nmap` ogni 10 minuti da uno script Python: inventario dei dispositivi (MAC, vendor, IP, hostname, porte aperte) in un file YAML. Avviso sul telefono quando compare un dispositivo nuovo, via `ntfy.sh` (gratuito). L'inventario è il seme di NetBox alla missione 16.

**Fatta quando:** ogni dispositivo ha un nome dato da te nel YAML, e un avviso è arrivato quando Stefano o un amico ha collegato qualcosa di nuovo.

**Riga CV:** Network discovery, asset inventory, change alerts

## P6. Cruscotto di latenza e banda

Prometheus con `node_exporter` e `blackbox_exporter`, Grafana, tutto in Docker (Pi 4 e 5) oppure smokeping (Pi 3). Bersagli: router di casa, gateway dell'ISP, 1.1.1.1, un data center a Milano e uno a Francoforte, albertstein.link. Speedtest ogni ora con grafico settimanale. Dopo due settimane rispondi: a che ora la rete di casa è peggiore e perché. Se la banda serale è sotto quella del contratto, la nota diventa una lettera all'ISP con i dati.

**Hardware:** su Pi 4 e 5 un SSD USB al posto della microSD è consigliato da qui in poi (Prometheus scrive tanto).

**Fatta quando:** cruscotto con screenshot nella nota, e una risposta con dati alla domanda "qual è il collo di bottiglia di casa".

**Riga CV:** Metrics and dashboards with Prometheus and Grafana, ISP performance evidence

## P7. VPN verso casa

WireGuard sul Pi, porta aperta sul router solo per UDP WireGuard, telefono e PC come peer. Dal 4G: raggiungi Pi-hole e Grafana, il traffico esce dall'IP di casa. Wireshark fuori dal tunnel: cosa si vede e cosa no. Alternativa senza porte aperte: Cloudflare Tunnel (missione 20).

**Sicurezza:** resta chiusa ogni altra porta. Da fuori (4G o un VPS gratuito) `nmap -sU -p 51820` vede la porta WireGuard e `nmap -p 22,53,3000` non vede niente: i due scan nella nota.

**Fatta quando:** il telefono in 4G apre Grafana via IP privato, e la nota ha la cattura che dimostra che il contenuto è cifrato.

**Riga CV:** WireGuard VPN deployment and verification

## P8. La sonda

Adattatore USB Ethernet in più. Il Pi in mezzo tra router e un dispositivo (bridge Linux) oppure su una porta mirror se c'è lo switch gestito: `tcpdump` a rotazione, `tshark` per le statistiche, `ntopng` o Zeek per i riepiloghi (da Pi 4 in su; con il Pi 3 solo tcpdump e tshark), cattura remota da Wireshark sul portatile via SSH. Un giorno di traffico di una TV o di una console: quanti server contatta in 24 ore.

**Hardware:** adattatore USB Ethernet (10 euro). Kit rete in `/gear`.

**Fatta quando:** la nota ha numeri veri, tre scoperte sulla rete di casa e una regola nuova in Pi-hole nata da quello che hai visto.

**Riga CV:** Passive network monitoring with tcpdump, tshark and Zeek or ntopng

## P9. Il Pi come router

Due interfacce: WAN verso il router di casa, LAN verso lo switch del lab. DHCP con `dnsmasq`, NAT e firewall con `nftables`, una VLAN taggata (802.1Q) verso il lab di Proxmox se c'è già. Da qui il lab ha il suo edge. È la missione 14 su hardware vero, prima di OPNsense.

**Hardware:** lo stesso adattatore USB Ethernet di P8.

**Fatta quando:** una VM del lab esce su internet passando dal Pi e non vede la rete di casa (provato con `tcpdump` su entrambi i lati), `nft list ruleset` è nella nota e ogni regola ha una riga di spiegazione.

**Riga CV:** Linux as a router: NAT, DHCP, nftables, VLAN tagging

**Prompt:** Sto facendo di un Raspberry un router con nftables e dnsmasq. Ti incollo il mio ruleset: dimmi cosa lascia passare che non dovrebbe e cosa blocca che non dovrebbe, regola per regola. Non riscriverlo.

## P10. Honeypot

Cowrie (un SSH finto) sul Pi, esposto su una porta alta con port forward; il vero SSH resta chiuso da fuori. Dopo una settimana: da dove vengono i tentativi, quali utenti e password provano, un grafico per ora del giorno. Poi lo spegni.

**Sicurezza:** Cowrie gira come utente senza privilegi, in Docker o in una VM. Da fuori si vede solo la porta alta: `nmap` dal 4G nella nota, prima e dopo lo spegnimento.

**Fatta quando:** la nota ha i numeri, un grafico, e una riga su cosa cambia nel modo in cui proteggi le tue cose.

**Riga CV:** Honeypot deployment and attack log analysis

## P11. Backup con ripristino

Disco USB sul Pi, `restic` come destinazione dei backup del PC e del lab, cifrati, con retention. Gitea sul Pi come mirror dei tuoi repo GitHub. Poi il ripristino provato: una cartella e una VM. Collega la missione 12.

**Hardware:** disco USB da 500 GB (30 euro).

**Fatta quando:** un file cancellato apposta torna dal backup, il mirror è all'ultimo commit, e il runbook lo può seguire Stefano senza chiederti niente.

**Riga CV:** Encrypted backups with restic, tested restores, self-hosted git mirror

## P12. Sensori e MQTT

BME280 su I2C sul Pi, Mosquitto come broker MQTT, un ESP32 che pubblica ogni minuto da un'altra stanza, Grafana che mostra tutto. Wireshark su MQTT: si legge tutto in chiaro; poi TLS sul broker e la stessa cattura. IoT fatto come si deve.

**Hardware:** kit del loot Boss 2 (BME280, ESP32, jumper). Kit sensori in `/gear` se serve altro.

**Fatta quando:** due sensori su Grafana, cattura prima e dopo TLS nella nota.

**Riga CV:** MQTT, IoT sensors, securing a broker with TLS

## P13. La bacheca

Uno schermo piccolo (OLED SSD1306 o e-paper da 2.13 pollici) sulla scrivania: livello attuale del sito letto da `progress.json`, missioni fatte, giorni all'esame CCNA, ping medio dell'ultima ora, stato della lampada. Codice in un repo `pi-board`. Una cosa tua che racconta il percorso.

**Hardware:** OLED (5 euro) o e-paper (20-25 euro).

**Fatta quando:** foto della bacheca accesa nella nota.

**Riga CV:** Small display projects: fetching JSON and rendering status

## P14. Gioco e radio (uno o entrambi)

- Gioco (Pi 4 e 5): server Minecraft (PaperMC) o Valheim nella rete lab di P9, raggiungibile dagli amici via WireGuard (P7); latenza misurata con P6 con 4 giocatori. Oppure RetroPie su una seconda microSD e una partita in rete con Stefano attraverso la VPN.
- Radio: RTL-SDR sul Pi: `dump1090` mostra gli aerei sopra Bergamo su una mappa locale, `rtl_433` legge i sensori a 433 MHz del vicinato. Capire lo spettro prima del wireless del CCNA.

Con il Pi 3: solo la radio, o RetroPie.

**Hardware:** RTL-SDR (30 euro, loot del Boss 5).

**Fatta quando:** una serata di gioco riuscita con la nota sulla latenza, oppure la mappa degli aerei con 24 ore di dati.

**Riga CV:** Hosting a multiplayer game server or software-defined radio basics

## P15. Pi in a box

Tutto quello che hai fatto sul Pi rifatto da zero con Ansible in meno di un'ora: OS nuovo, playbook, backup ripristinato, servizi su. Repo `pi-ansible` pubblico con README che spiega ogni ruolo. Se il Pi muore, ne compri un altro e in un'ora è tutto come prima. È la versione piccola del Boss 4.

**Fatta quando:** cronometro sotto i 60 minuti, log della sessione (comandi e orari) nella nota.

**Riga CV:** Reproducible server from code with Ansible

## Boss Pi: il Pi è la rete

Nessun passo. Per un fine settimana il Pi è router, DNS, VPN e monitor di casa. Stefano, da remoto e senza avvisare, prova a: cambiare il DNS su un dispositivo, saturare la banda, spegnere il router del lab, entrare via SSH. Tu devi accorgerti di tutto dal cruscotto e dalla lampada, senza che nessuno in casa noti niente.

**Battuto quando:** quattro eventi rilevati e spiegati nella nota con gli orari, e la famiglia non ha chiamato.

**Badge:** Ran home network services on a Raspberry Pi for a weekend, under attack

Sul sito il boss è il sedicesimo passo del binario: si segna come gli altri, `"done": true` sul passo 16.
