# Livello 4: Sysadmin

Un laboratorio in casa che puoi distruggere e ricostruire. Serve un PC vecchio o un mini PC (anche usato, 8-16 GB di RAM bastano). Da qui in poi tutto quello che fai nei lab finisce in note.

---

## 09. Proxmox lab

Installa Proxmox VE sul mini PC. Crea: una VM Ubuntu Server, una VM Debian, un bridge VLAN-aware. Metti le due VM su due VLAN diverse e fai in modo che si vedano solo attraverso un router (una terza VM con due interfacce, anche solo Linux con `ip forward`).

**Fatta quando:** ping tra VLAN passa solo attraverso il router, e lo dimostri con `tcpdump` sul router. Nota di lab con lo schema.

**Riga CV:** Virtualization with Proxmox: VMs, bridges, VLAN-aware networking

## 10. Docker basics

Su una VM: Docker e Compose. Un `compose.yml` con tre servizi (un web server, un database, un reverse proxy). Poi rispondi con esperimenti: come parlano tra loro? Su che rete? Cosa vede `docker network inspect`? Cosa succede se pubblichi una porta?

**Fatta quando:** i tre servizi funzionano e la nota di lab spiega la rete dei container con un diagramma tuo.

**Riga CV:** Containers with Docker and Compose, container networking

## 11. Ansible per il lab

Un repository `lab-ansible` (pubblico): inventario con le tue VM, playbook che installa i pacchetti base, crea il tuo utente con chiave SSH, imposta hostname e timezone, configura il firewall. Lancialo due volte: la seconda non deve cambiare nulla (idempotenza).

**Fatta quando:** una VM nuova diventa "tua" con un comando. Il repo ha un README che dice come.

**Riga CV:** Configuration management with Ansible, idempotent playbooks

## 12. Backup e restore

Backup delle VM da Proxmox su un disco esterno o su un bucket (Cloudflare R2 ha un piano gratuito). Poi il pezzo che quasi nessuno fa: cancella una VM e ripristinala dal backup. Cronometra. Scrivi un runbook: passi, comandi, tempi.

**Fatta quando:** il ripristino è riuscito e il runbook lo può seguire Stefano senza chiederti niente.

**Riga CV:** Backup strategy, tested restores, runbooks
