# Side quest

Opzionali. Ognuna vale una nota di lab e una riga in più di cui parlare a un colloquio. Ordine libero.

## Traffico vero

Cattura con Wireshark cosa succede quando apri albertstein.link: DNS, TLS handshake, HTTP. Spiega nella nota perché vedi il contenuto HTTP o perché non lo vedi.

## Il sito da un altro posto

Da Cloudflare guarda le analytics del sito: da dove arrivano le richieste, quante sono bot. Poi blocca un paese a caso con una regola WAF e verifica con un VPN o con un servizio di "check from location". Rimuovi la regola. Nota di lab.

## Pi-hole in casa

Su un Raspberry o una VM: Pi-hole come DNS di casa. Dopo una settimana, i domini più bloccati e cosa hai imparato sui dispositivi che hai in casa.

## Tunnel

WireGuard tra il tuo PC e una VM (anche gratuita, Oracle o Fly). Ping attraverso il tunnel, Wireshark fuori dal tunnel: cosa si vede? Nota di lab.

## Il monitor cresce

Il monitor della missione 6 controlla anche: scadenza certificato TLS, presenza degli header di sicurezza, tempo DNS. Un grafico settimanale dei tempi di risposta, generato dal workflow.

## Generatore statico

Porta il sito su un generatore statico (Eleventy o Hugo). Le pagine restano identiche, ma le note di lab diventano Markdown. Nella PR spieghi cosa cambia nel build log della missione 3.

## Honeypot

Una VM esposta con SSH su porta 22 e fail2ban attivo. Dopo una settimana: da dove vengono i tentativi, quali user provano, come li hai visti. Nota di lab con i numeri.
