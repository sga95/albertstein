# Quest: le cose che fai perché ti piacciono

Tutte opzionali. Nessuna blocca una missione. Ognuna vale una nota di lab e una riga in più di cui parlare a un colloquio, e alcune sono le ricompense dei boss. Sono divise per passione: gaming, rompicapo, elettronica, scienza, libri, più le quest di rete che c'erano già.

Come funziona sul sito: la lista completa è in `data/quests.yaml` e compare in `/quests`. Quando inizi una quest, aggiungila in fondo alla lista `quests` di `site/data/progress.json`:

```
{ "id": "lag-lab", "title": "Lag lab", "done": false }
```

L'ultima quest non ancora `done` è quella che la home mostra come "Now playing". Quando finisce, `"done": true` e la nota di lab linkata dalla pagina.

Le quest che usano un Raspberry Pi rimandano al binario Pi (`PI.md`) quando arriva: qui c'è la versione che si fa con una VM o con quello che hai.

---

## Rete (le side quest di prima)

### Traffico vero (`real-traffic`)
Cattura con Wireshark cosa succede quando apri albertstein.link: DNS, TLS handshake, HTTP. Spiega nella nota perché vedi il contenuto HTTP o perché non lo vedi.

### Il sito da un altro posto (`site-from-elsewhere`)
Da Cloudflare guarda le analytics del sito: da dove arrivano le richieste, quante sono bot. Poi blocca un paese a caso con una regola WAF e verifica con un VPN o con un servizio di "check from location". Rimuovi la regola. Nota di lab.

### Tunnel (`tunnel`)
WireGuard tra il tuo PC e una VM (anche gratuita, Oracle o Fly). Ping attraverso il tunnel, Wireshark fuori dal tunnel: cosa si vede? Nota di lab.

### Il monitor cresce (`monitor-grows`)
Il monitor della missione 6 controlla anche: scadenza certificato TLS, presenza degli header di sicurezza, tempo DNS. Un grafico settimanale dei tempi di risposta, generato dal workflow.

### Generatore statico (`static-generator`)
Porta il sito su un generatore statico (Eleventy o Hugo). Le pagine restano identiche, ma le note di lab diventano Markdown. Nella PR spieghi cosa cambia nel build log della missione 3.

### Honeypot (`honeypot`)
Una VM esposta con SSH su porta 22 e fail2ban attivo. Dopo una settimana: da dove vengono i tentativi, quali user provano, come li hai visti. Nota di lab con i numeri.

---

## Gaming

### Game server sul lab (`game-server`)
Un server Minecraft (PaperMC) o Valheim su una VM Proxmox, in una VLAN sua, esposto agli amici via Cloudflare Tunnel o port forward con regole firewall che lasciano passare solo quella porta. Monitorato dal tuo monitor. Nota: cosa succede alla latenza con 5 giocatori, con i numeri.

### Netcode con Wireshark (`netcode`)
Cattura di una partita online, qualsiasi gioco: quanti pacchetti al secondo, UDP o TCP, quanto sono grandi, cosa cambia quando c'è lag. Nella nota spieghi perché i giochi usano UDP e cosa perderebbero con TCP.

### Lag lab (`lag-lab`)
Con `tc` su Linux aggiungi 100 ms di latenza e 2% di perdita tra due VM (`tc qdisc add dev eth0 root netem delay 100ms loss 2%`). Misura l'effetto su un gioco o anche solo su SSH e su `scp`. Poi 300 ms. La nota dice a che punto diventa inusabile e perché.

### Speedrun (`speedrun`)
Rifai la missione 1 (dal branch al sito online) o il Boss 4 cronometrati. Il tempo va nella nota e nella lista quest. Solo contro te stesso: il record da battere è il tuo.

---

## Rompicapo

### Subnetting sprint (`subnet-sprint`)
`make quiz`: 20 esercizi di subnetting generati a caso (rete, broadcast, host, maschera in due formati), 10 minuti, senza LLM. Tempo e punteggio nella nota. Da rifare finché non sei sotto i 5 minuti con 20 su 20.

### Bandit fino al 20 (`bandit-20`)
[OverTheWire Bandit](https://overthewire.org/wargames/bandit/) fino al livello 20. Per ogni livello una riga: il comando che ha aperto la porta.

### Advent of Code (`advent-of-code`)
[Advent of Code](https://adventofcode.com/) in Python, almeno 5 giorni, anche di un anno passato. Il codice in un repo pubblico.

### picoCTF (`picoctf`)
[picoCTF](https://picoctf.org/): 5 sfide di rete o crittografia. Nella nota, per ognuna, cosa hai capito che prima non sapevi.

### Un rompicapo a settimana (`weekly-puzzle`)
La pagina `/puzzle`: un enigma di rete o Linux scritto da Stefano in `data/puzzles.yaml`, uno a settimana. La soluzione compare quando la settimana è passata. Rispondi prima che compaia, in una riga nella nota della settimana.

---

## Elettronica

### Lampada di uptime (`uptime-lamp`)
Un ESP32 o un Raspberry Pi Pico W che interroga il sito ogni minuto e accende un LED verde o rosso. Collega la missione 6 a qualcosa di fisico. Foto nella nota. Con il Raspberry: passo P3 del binario Pi.

### Sensore di latenza (`latency-sensor`)
ESP32 che pinga il router di casa e mostra i millisecondi su un display OLED. Con il Raspberry: passo P13 (la bacheca).

### Pi-hole in casa (`pihole`)
Su un Raspberry o una VM: Pi-hole come DNS di casa. Dopo una settimana, i domini più bloccati e cosa hai imparato sui dispositivi che hai in casa. Poi il grafico settimanale. Con il Raspberry: passo P4.

### Network tap passivo (`network-tap`)
Un tap passivo con due porte e un Raspberry Pi che fa da sonda Wireshark per il lab. Con il Raspberry: passo P8.

---

## Scienza

### Come fa davvero (`how-it-really-works`)
Una nota di lab per domanda, con misure tue dove possibile: quanto ci mette la luce da Bergamo a Francoforte e perché il ping è di più (traceroute e ping verso un data center noto); come è fatto un cavo sottomarino; cosa succede fisicamente in un cavo Ethernet quando passa un bit. Una domanda alla volta.

### Radio (`radio`)
Una SDR economica (RTL-SDR): vedere Wi-Fi, LoRa o ADS-B (gli aerei sopra Bergamo). Capire lo spettro prima di studiare il wireless del CCNA. Con il Raspberry: passo P14.

---

## Libri

### Reading log (`reading-log`)
Un libro tecnico ogni due mesi, una nota per libro in `site/reading/` con tre cose che cambia nel tuo modo di lavorare. Lista di partenza, gratuiti dove indicato:

- The Linux Command Line, William Shotts (gratis in PDF)
- Pro Git (gratis online)
- High Performance Browser Networking, Ilya Grigorik (gratis online)
- Computer Networking: A Top-Down Approach, Kurose e Ross (biblioteca)
- The Phoenix Project (romanzo, per capire come funziona il lavoro in IT)
- Julia Evans, "Networking zines" (alcune gratuite)
