# Binario Mind: l'AI come strumento, non come scorciatoia

Otto passi. Partono dopo Shield, in parallelo a tutto il resto. Servono a una cosa sola: usare claude.ai e gli altri modelli come li usa un professionista, e saperlo spiegare a un colloquio senza arrossire.

Una cosa da sapere prima: chi assume oggi non chiede "usi l'AI?" per sapere se sei moderno. Lo chiede per capire se sai cosa ti sta dando in mano. Uno che incolla un comando senza leggerlo è un rischio; uno che lo legge, lo verifica e sa dire dove il modello ha sbagliato è una risorsa. La differenza sta tutta in questi otto passi.

Regola di tutto il binario, la stessa di `INIZIA-QUI.md`: il codice lo scrivi tu. L'AI spiega, propone, critica. Non consegna.

---

## Gratis, prima

- M1: [Andrej Karpathy, "Intro to Large Language Models"](https://www.youtube.com/watch?v=zjkBMFhNj_g): un'ora, in inglese, la spiegazione migliore che c'è. Poi [3Blue1Brown sui transformer](https://www.youtube.com/watch?v=wjZofJX0v4M) se vuoi vedere dentro.
- M2 e M5: [Anthropic, tutorial interattivo di prompt engineering](https://github.com/anthropics/prompt-eng-interactive-tutorial) e la [documentazione ufficiale sul prompting](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview): gratis; i notebook si leggono anche senza eseguirli.
- M7: [documentazione API Anthropic, "Get started"](https://docs.anthropic.com/en/api/getting-started): la pagina da leggere prima di scrivere lo script.
- Panoramica: [Google AI Essentials su Coursera](https://www.coursera.org/learn/google-ai-essentials), in audit se il tuo account lo permette.

## M1. Come funziona un modello di linguaggio

Un modello di linguaggio non "sa" le cose: prevede la parola più probabile dopo quelle che ha davanti. Lavora su **token** (pezzi di parola), dentro un **contesto** limitato (quello che c'è nella conversazione, e basta), e sceglie tra alternative con una **probabilità**. Per questo può inventare un comando che non esiste con la stessa sicurezza con cui scrive uno vero: per lui è solo una sequenza plausibile. Leggi una spiegazione seria (la guida di Anthropic su come funzionano i modelli, o un video di 3Blue1Brown sui transformer) e poi fai la prova: chiedi a claude.ai un'opzione di `ip` o di `show` che non esiste, con tono convinto, e guarda cosa succede. Poi chiedigli di verificare quello che ha detto.

**Fatta quando:** una nota di lab spiega, a parole tue, perché un modello inventa un comando che non esiste, con l'esempio che hai provato e cosa è successo quando gli hai chiesto di verificare.

**Riga CV:** Working understanding of LLMs: context, tokens, hallucination

**Prompt:** Spiegami cosa sono token, contesto e probabilità in un modello di linguaggio, con un esempio per ciascuno. Poi fammi tre domande per controllare che abbia capito, una alla volta. Non darmi le risposte finché non provo.

## M2. claude.ai configurato per imparare

Account claude.ai con l'email Proton e 2FA (Shield S2 e S3). Crea un **Progetto** per il sito e uno per i lab. Nelle istruzioni del progetto scrivi la regola, in italiano o in inglese: "Guida, non fare. Non scrivere codice o configurazioni al posto mio: spiegami, fammi domande, chiedimi cosa vedo sullo schermo e correggi quello che scrivo io. Se ti chiedo la soluzione intera, ricordami questa regola." Decidi anche quando la chat non serve: per un comando che conosci, per una cosa che si legge in un `man` in trenta secondi, per un passo che devi saper fare a memoria a un colloquio.

**Fatta quando:** le istruzioni sono salvate nei due progetti, e la prima conversazione di lab le rispetta: hai chiesto una cosa, il modello ti ha fatto una domanda invece di darti il codice, e tu hai scritto il codice.

**Riga CV:** Configured an AI assistant as a tutor with explicit guardrails

## M3. Chiedi, poi verifica

Ogni risposta tecnica si verifica su una fonte prima di usarla: `man`, documentazione ufficiale, RFC, o una prova in lab. Non è sfiducia, è metodo: la risposta del modello è un'ipotesi ben scritta. Tieni un file `hire/verifiche.md` con una riga per caso: cosa ha detto il modello, dove hai verificato, cosa era vero e cosa no. Cerca apposta i casi in cui la verifica cambia qualcosa.

**Fatta quando:** cinque casi documentati in cui la verifica ha smentito o corretto la risposta (un flag sbagliato, una versione vecchia, una porta inventata, un comportamento diverso in lab).

**Riga CV:** Verification habit for AI-generated technical answers

**Prompt:** Ti chiedo una cosa tecnica. Rispondi, e alla fine dimmi esattamente dove posso verificare ogni affermazione (man page, sezione della documentazione, comando da provare). Se non sei sicuro di qualcosa, dillo prima della risposta, non dopo.

## M4. Cosa non entra mai in un prompt

Chiavi, password, token, indirizzi IP interni, nomi di host aziendali, dati di clienti o colleghi, codice di un'azienda per cui lavori, contenuto di email altrui. Una chat con un modello è un servizio esterno: quello che incolli esce dal tuo computer. Prima di incollare un log o una configurazione, anonimizza: `10.0.12.7` diventa `10.0.X.Y`, `srv-fatture-01` diventa `server-A`, la chiave diventa `<REDACTED>`. Un prompt anonimizzato bene funziona uguale.

**Fatta quando:** la regola è scritta nella checklist alla fine di `SHIELD.md` (aggiungi una riga: "Prompt: mai chiavi, IP interni, dati altrui. Anonimizza prima."), e in una nota di lab c'è un esempio di configurazione o log anonimizzato bene, con accanto la lista di cosa hai tolto e perché.

**Riga CV:** Data hygiene when using AI tools

## M5. Prompt per lavoro vero

Un prompt utile ha quattro parti: **contesto** (cosa stai facendo, con che strumenti), **obiettivo** (cosa vuoi ottenere), **vincoli** (cosa non vuoi: niente codice, massimo dieci righe, solo Cisco IOS), **formato** (lista, tabella, domande). Poi si itera: la seconda domanda è più precisa della prima. Due abitudini che cambiano tutto: chiedere il ragionamento ("spiegami perché, passo per passo") e far criticare la tua bozza ("ecco la mia nota, dimmi cosa non è chiaro a chi non c'era"). Scrivi due prompt riusabili, uno per la revisione delle note di lab e uno per il debug di rete, e salvali in `hire/prompts.md`: sono strumenti tuoi, come uno script.

**Fatta quando:** i due prompt sono in `hire/prompts.md`, ognuno con le quattro parti, e li hai usati almeno una volta ciascuno con il risultato incollato sotto.

**Riga CV:** Structured prompting for technical tasks

**Prompt:** Ti incollo un prompt che ho scritto. Dimmi quale delle quattro parti (contesto, obiettivo, vincoli, formato) è debole e perché. Non riscriverlo tu: dammi una domanda per parte che mi aiuti a migliorarlo.

## M6. L'AI per il networking

Tre usi che valgono: analisi di log e capture (incolli un pezzo di log anonimizzato e chiedi "cosa non torna?"), generazione di configurazioni da rivedere riga per riga (chiedi una VLAN con trunk, poi controlla ogni comando sul manuale prima di incollarlo), spiegazione di output di `show` (`show ip ospf neighbor`, `show interfaces`: chiedi cosa significa ogni campo). In tutti e tre il modello è il secondo paio d'occhi, mai il primo. Fallo in un lab vero (Packet Tracer, Containerlab, la tua rete di casa) e tieni traccia di dove ha aiutato e dove ha sbagliato.

**Fatta quando:** una nota di lab con due casi: uno in cui l'AI ha visto una cosa che ti era sfuggita, uno in cui ha sbagliato (comando inesistente, campo interpretato male, configurazione che non applica) e come te ne sei accorto.

**Riga CV:** Applying AI assistance to network troubleshooting with review

**Prompt:** Ti incollo l'output di un comando `show` anonimizzato. Spiegami campo per campo cosa significa, e per ogni campo dimmi se il valore è normale o merita attenzione. Non dirmi cosa fare: dimmi cosa vedi.

## M7. La tua prima chiamata API

Uno script Python di 30 righe che chiama l'API Anthropic e riassume una nota di lab in tre frasi. La chiave sta in una variabile d'ambiente (`ANTHROPIC_API_KEY`), mai nel codice, mai nel repo: `.env` in `.gitignore` (Shield S8) e gitleaks che controlla. Modello piccolo e economico, budget di pochi euro, e guarda nella console quanto costa ogni chiamata. Leggi la documentazione ufficiale dell'API prima di chiedere al modello come si chiama il modello.

**Fatta quando:** lo script gira da terminale, la chiave non è in nessun commit (controlla la storia, non solo l'ultimo file), gitleaks passa, e la nota riassunta è nel README dello script con il costo della chiamata.

**Riga CV:** Called an LLM API from Python with secure key handling

**Prompt:** Sto scrivendo uno script Python che chiama un'API con una chiave. Spiegami tre modi per tenere la chiave fuori dal codice e dal repo, con i pro e i contro. Non scrivere lo script: lo scrivo io e te lo faccio rivedere.

## M8. L'AI al colloquio

Prima o poi chiedono "usi l'AI?". La risposta giusta dura 60 secondi e ha quattro pezzi: sì; come (tutor con regole, verifica su fonti, mai dati sensibili); con quali limiti (inventa comandi, non conosce la tua rete, non sostituisce il manuale); un esempio vero (M6: dove ha aiutato e dove ha sbagliato). Niente entusiasmo, niente paura: è uno strumento, come Wireshark. Scrivila, provala a voce, cronometrala.

**Fatta quando:** la risposta di 60 secondi esiste scritta in `hire/questions.md`, e l'hai provata con Stefano che ha fatto il recruiter e ti ha fatto una domanda di seguito a cui hai risposto.

**Riga CV:** Can explain responsible AI use to an employer
