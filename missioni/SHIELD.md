# Binario Shield: la tua sicurezza, prima di tutto

Nove passi. Si fanno **prima** di tutto il resto, nella prima settimana: da qui in poi avrai account, chiavi e un lab che valgono qualcosa, e chi lavora in sicurezza si giudica da come tiene le proprie cose. Ogni passo ha i consigli che servono; alla fine c'è la checklist completa da tenere.

---

## S1. Password manager

Installa Bitwarden (gratuito, open source) su PC e telefono. Master password: una frase di 4-5 parole a caso che ricordi, tipo `cavallo-lampada-nove-vento`, mai usata altrove. Poi, uno alla volta, cambia le password di: email, GitHub, Cloudflare, LinkedIn, banca, Amazon, social. Ogni password generata dal manager, lunga, unica. Metti in Bitwarden anche le domande di sicurezza (risposte inventate e salvate).

**Fatta quando:** i 10 account più importanti hanno password uniche generate, e la master password è scritta su carta in un posto sicuro a casa (sì, carta: è il backup).

**Riga CV:** Password manager with unique passwords everywhere

## S2. Due fattori dove conta

App authenticator (Aegis su Android, Raivo o quella di Bitwarden su iOS). Attiva il 2FA su: email, GitHub, Cloudflare, Proton, LinkedIn, banca. Per ogni account salva i **backup code** in Bitwarden. Evita SMS come secondo fattore se c'è un'alternativa: il numero di telefono si ruba (SIM swap).

**Fatta quando:** sei account con 2FA da app e backup code salvati. Hai provato a fare login da un dispositivo nuovo e ha chiesto il codice.

**Riga CV:** 2FA with authenticator app and backup codes

## S3. Email professionale su Proton

Crea `alberto.galliani@proton.me` (o `a.galliani`, se libero). Questa è la mail per lavoro, candidature, GitHub, LinkedIn, sito. La Gmail resta per il personale e per i servizi vecchi. Da subito: 2FA, recovery email verso la Gmail, recovery phrase salvata in Bitwarden. Poi cambia la mail su GitHub, LinkedIn, Cloudflare e nel CV sul sito (`site/cv/index.html`).

Perché Proton: cifratura end-to-end, sede in Svizzera, niente scansione della posta per pubblicità, e un dominio che a un recruiter tecnico dice qualcosa.

**Fatta quando:** la mail Proton è sul sito e su LinkedIn, e la Gmail non compare più in nessun posto pubblico.

**Riga CV:** Separate professional identity with end-to-end encrypted mail

## S4. Account GitHub blindato

Su GitHub: 2FA (fatto in S2), email primaria Proton, email privata nei commit (l'indirizzo `noreply` che GitHub ti dà), rimuovi le chiavi SSH e i token che non riconosci, controlla le "Authorized apps" e revoca quelle inutili. Attiva le notifiche di login sospetto.

**Fatta quando:** hai fatto lo screenshot della pagina Security di GitHub con tutto verde, e la sai spiegare voce per voce.

**Riga CV:** Hardened developer account: 2FA, SSH keys, signed commits

## S5. Commit firmati

Configura git per firmare i commit con la tua chiave SSH (`git config --global gpg.format ssh` e `commit.gpgsign true`), carica la chiave su GitHub come "Signing key". Da ora ogni tuo commit ha il badge **Verified**. Su questo repo `site/data/progress.json` è tuo per contratto (file `CODEOWNERS`) e un controllo automatico rifiuta modifiche non fatte da te: la firma è la prova che sei tu.

**Fatta quando:** l'ultimo commit su `main` mostra Verified e sai spiegare la differenza tra chiave di autenticazione e chiave di firma.

**Riga CV:** Commit signing with SSH keys, verified badge

## S6. Il portatile

Cifratura del disco (BitLocker su Windows, LUKS su Linux, FileVault su Mac). Aggiornamenti automatici. Blocco schermo a 5 minuti. Utente non amministratore per l'uso quotidiano. Backup: una copia sul cloud (anche solo la cartella dei lab e delle chiavi, cifrata) e una su disco esterno, con ripristino provato una volta.

**Fatta quando:** hai spento e riacceso il PC e ti ha chiesto la chiave di cifratura; hai ripristinato un file dal backup.

**Riga CV:** Full-disk encryption, updates, screen lock, backups

## S7. Phishing

Fai un corso breve e gratuito (Google "phishing quiz", il modulo gratuito di Proton o di Cisco NetAcad su security basics). Poi le regole tue, scritte in una nota di lab: non cliccare da mail, aprire il sito da solo; controllare il dominio vero nel link; allegati Office con macro mai; urgenza e paura sono il segnale; chiamare indietro a un numero che conosci, non a quello nel messaggio. Tuo fratello ti manderà un phishing finto nei prossimi mesi. Non ti dirà quando.

**Fatta quando:** la nota è online e hai fatto 10 su 10 a un quiz.

**Riga CV:** Recognising phishing, safe handling of links and attachments

## S8. Segreti mai in git

Regole per tutti i repo: `.gitignore` con `.env`, chiavi, config; secret di GitHub Actions per token e password; `gitleaks` come pre-commit hook; se una chiave finisce in un commit, si **ruota** (nuova chiave, vecchia revocata), non si cancella solo il file, perché la storia resta. Prova tu: committa una chiave finta in un branch e guarda cosa dice GitHub secret scanning.

**Fatta quando:** gitleaks gira nel pre-commit del repo del sito e del lab, e hai fatto la prova con la chiave finta.

**Riga CV:** Secret hygiene in repositories, rotation after exposure

## S9. La tua impronta pubblica

Cerca il tuo nome e la tua email su Google e su haveibeenpwned.com. Per ogni account violato: cambia password (è unica ormai, ma cambiala). Social: profili privati o puliti, foto della casa e della targa no, nessun numero di telefono pubblico. Sul sito e su LinkedIn: solo email Proton, niente telefono, niente indirizzo. Il telefono lo dai a voce, a chi decidi tu.

**Fatta quando:** cercando il tuo nome esce il sito, LinkedIn e nient'altro che non vuoi.

**Riga CV:** Managing personal data exposure and social media privacy

---

## Checklist da tenere

- Password: uniche, generate, in Bitwarden. Master password su carta a casa.
- 2FA da app ovunque. Backup code salvati. Mai SMS se c'è alternativa.
- Email: Proton per il lavoro, Gmail per il resto. Mai la stessa per tutto.
- Chiavi SSH: una per dispositivo, con passphrase. Chiave di firma separata.
- Commit firmati. Segreti mai in git. Se succede, ruota.
- Disco cifrato, aggiornamenti automatici, blocco schermo, backup provato.
- Link: aprire il sito da solo, non dal messaggio. Urgenza = sospetto.
- Wi-Fi pubblico: solo con VPN (WireGuard verso casa, side quest).
- Telefono e indirizzo: mai pubblici.
- Ogni tre mesi: rivedi app autorizzate, sessioni attive, chiavi.
