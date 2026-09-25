# Livello 5: Network engineer

La tua materia, fatta come si fa in azienda. Containerlab gira su una VM Linux e ti dà router veri (FRRouting, Arista cEOS, Nokia SR Linux) senza hardware.

---

## Gratis, prima

- Missione 13: [Jeremy's IT Lab, giorni su OSPF](https://www.youtube.com/playlist?list=PLhTW6Fulbw1Tqaa9cTEpAZo86TCO6xfYS) e [Containerlab docs con i lab di esempio](https://containerlab.dev/lab-examples/lab-examples/): parti dal lab a due router.
- Missione 14: [documentazione OPNsense](https://docs.opnsense.org/) e [Practical Networking su NAT](https://www.practicalnetworking.net/series/nat/nat/).
- Missione 15: [documentazione Netmiko](https://github.com/ktbyers/netmiko) e [tutorial Nornir](https://nornir.readthedocs.io/en/latest/tutorial/index.html); Python da [Exercism](https://exercism.org/tracks/python) se serve.
- Missione 16: [NetBox docs](https://docs.netbox.dev/) e la [demo pubblica di NetBox](https://demo.netbox.dev/); [documentazione LibreNMS](https://docs.librenms.org/) per SNMP.

## 13. Containerlab: OSPF e BGP

Topologia con 4 router: due aree OSPF, poi due AS collegati in eBGP. Guarda le tabelle, spegni un link, guarda come converge, misura quanto ci mette. Ripeti con BGP.

**Fatta quando:** la nota di lab ha la topologia, le tabelle prima e dopo il guasto, i tempi di convergenza, e una frase tua su quando useresti l'uno o l'altro.

**Riga CV:** Dynamic routing labs with OSPF and BGP in Containerlab

## 14. Firewall e segmentazione

OPNsense come VM su Proxmox, al posto del router Linux della missione 9. Tre zone: LAN, lab, DMZ. Regole con logging: la DMZ non parla con la LAN, il lab esce solo su porte scelte. NAT per uscire. Prova a violare ogni regola e leggi i log.

**Fatta quando:** ogni regola ha una prova (un comando che viene bloccato e la riga di log corrispondente) nella nota di lab.

**Riga CV:** OPNsense firewall, VLAN segmentation, NAT, rules with logging

## 15. Network automation

Python con Netmiko, poi Nornir: uno script che si collega a tutti i router del lab, salva la configurazione in git ogni notte (workflow in GitHub Actions su un runner nella tua VM, o cron), e uno script che cambia una cosa su tutti (una descrizione di interfaccia, un ACL) e mostra il diff prima di applicare.

**Fatta quando:** il repo dei backup ha una storia di commit notturni, e il cambio massivo funziona con "dry run" prima di applicare.

**Riga CV:** Python network automation with Netmiko and Nornir, config backups

## 16. NetBox e monitoring

NetBox in Docker: tutti i device, le interfacce, le VLAN, gli IP del lab. Poi l'automazione della missione 15 legge l'inventario da NetBox invece che da un file. LibreNMS che monitora i router via SNMP: grafici di traffico, alert se un link va giù.

**Fatta quando:** NetBox è la fonte unica, uno script la usa, e LibreNMS ti ha mandato almeno un alert vero.

**Riga CV:** NetBox as source of truth, SNMP monitoring with LibreNMS
