# Come si lavora su questo repo

Tutto passa da tre comandi. Serve solo Python 3 (nessuna libreria da installare) e `make`.
Su Windows: usa WSL o Git Bash, oppure lancia direttamente `python3 tools/check.py`.

## I comandi

| Comando | Cosa fa |
|---|---|
| `make serve` | Sito in locale su http://localhost:8080/ con la cartella `site/`. Ctrl+C per fermare. `make serve PORT=3000` per cambiare porta. |
| `make check` | Tutti i controlli che fa anche la CI. Esce con errore se c'è qualcosa da sistemare. |
| `make test` | I test degli strumenti (`pytest`, si installa con `pip install pytest`). |
| `make note TITLE="Titolo"` | Crea `site/lab/AAAA-MM-GG-titolo.html` dal template con la data di oggi e lo mette in cima alla lista in `site/lab/index.html`. |
| `make postmortem TITLE="Cosa si è rotto"` | Come sopra ma dal template del post-mortem. Alla fine stampa la riga da incollare in `progress.json` nella lista `incidents`. |
| `make lab-lint` | Solo il punteggio delle note di lab, nel formato del commento in PR. |

Flusso tipico: `make serve` in un terminale, modifichi i file, ricarichi la pagina. Prima del commit: `make check`. Poi push e PR.

## Cosa controlla la CI

Su ogni PR (e su ogni push su `main`) partono quattro job, `.github/workflows/ci.yml`:

1. **check**: gli stessi controlli di `make check` più `make test`.
   - `site/data/progress.json` è JSON valido e rispetta lo schema `engine/schema/progress.schema.json`
     (chiavi giuste, `done` solo `true` o `false`, numeri delle missioni unici, ogni missione in un livello).
   - Regola di sblocco: una missione `done` con la precedente non `done`, un boss `done` con missioni aperte,
     un passo di un binario `done` con il precedente aperto. Solo un **avviso**: non blocca, ma il sito mostrerà
     un ordine strano.
   - Ogni link interno (`href`, `src`) punta a un file che esiste in `site/`. I link esterni non vengono provati.
   - Ogni `<img>` ha un `alt` e il file esiste.
   - Nessuna pagina sopra 200 KB, nessuna immagine sopra 300 KB.
2. **html**: HTML5 valido con `html5validator` (il validatore del W3C). Gira solo in CI perché ha bisogno di Java.
3. **lab-notes**: se la PR tocca `site/lab/`, un commento con punteggio e suggerimenti per ogni nota.
   Non blocca mai. Il punteggio guarda: le quattro sezioni (What I wanted to do, Setup, What happened,
   What I learned), almeno un blocco `<pre>` o un'immagine, "What I learned" scritta davvero, nessun testo
   segnaposto lasciato dal template. Per i post-mortem le sezioni sono cinque (Timeline, Root cause, What helped,
   What wasted time, What I change).
4. **gitleaks**: cerca chiavi, token e password nei commit. Se scatta, la chiave va **ruotata**, non solo tolta:
   è già nella storia di git (binario Shield, passo S8).

`guard-progress` è un quinto workflow, separato: controlla che `progress.json` lo cambi solo Alberto.

## Come leggere un errore

`make check` stampa una riga per controllo, `ok` o `ERRORE`, e sotto il dettaglio. Esempi veri:

```
site/data/progress.json: JSON non valido alla riga 6, colonna 5: Expecting ',' delimiter
  Probabile causa: manca una virgola alla fine della riga precedente, oppure ce n'è una di troppo
     6 |     { "n": 2, "title": "DNS and TLS", "done": false, "skill": "DNS" }
       |     ^
```
Apri il file alla riga indicata. Il `^` dice dove il parser si è fermato: quasi sempre il problema è
subito prima (la riga 5 senza virgola in fondo). Attenzione a `true`/`false` minuscoli e senza virgolette,
e all'ultima voce di una lista che **non** vuole la virgola.

```
site/data/progress.json: missions[2].done: deve essere boolean, trovato string
```
`missions[2]` è la terza missione (si conta da zero). `"done": "true"` con le virgolette è una stringa; va `"done": true`.

```
site/data/progress.json: missions[0].dne: chiave sconosciuta "dne" (ammesse: done, file, n, skill, title)
```
Refuso nel nome della chiave. La lista tra parentesi dice quali esistono.

```
  avviso: site/data/progress.json: regola di sblocco: missione 3 "The pipeline" è done ma la 2 "DNS and TLS" no
```
Non è un errore: la CI passa. Ma il sito sblocca in ordine, quindi o hai saltato un passo o hai spuntato quello sbagliato.

```
lab/2026-03-01-vlan.html:41: <img src="topology.png"> punta a lab/topology.png, che non esiste
```
Il numero dopo i due punti è la riga della pagina. Il file va messo nella cartella indicata, con quel nome esatto
(maiuscole e minuscole contano: su Cloudflare `Topology.png` e `topology.png` sono due file diversi).

```
lab/2026-03-01-vlan.html:41: immagine senza attributo alt
```
Aggiungi `alt="cosa mostra l'immagine"`. Serve a chi non la vede e a chi cerca.

```
lab/topology.png: l'immagine pesa 1240 KB, il massimo è 300 KB (riducila prima di committare)
```
Screenshot troppo grande. Ritaglia la parte che serve o esporta in PNG a 1x, oppure converti in WebP.

Il job **html** in CI segnala gli errori come `"file:site/lab/x.html":41.5-41.30: error: ...`: riga 41,
dalla colonna 5 alla 30. Di solito è un tag non chiuso o un attributo scritto male.

## Il file che nessuno tocca per te

`site/data/progress.json` lo modifica solo Alberto. Gli strumenti lo leggono, non lo scrivono mai:
`make postmortem` stampa la riga da aggiungere, ma la incolli tu. Se un check ti dice che manca qualcosa in
`check-ignore.txt`, guarda `engine/check-ignore.txt`: è la lista dei file che sappiamo mancare di proposito.

## Struttura

```
Makefile                    i comandi
tools/check.py              make check
tools/new_note.py           make note, make postmortem
tools/serve.py              make serve
tools/lib/                  logica riusata dai comandi e dai test (solo libreria standard)
engine/schema/              schema di progress.json
engine/check-ignore.txt     file che possono mancare senza errore
tests/                      pytest; tests/fixtures/ contiene progress.json in vari stati
.github/workflows/ci.yml    i quattro job descritti sopra
```

`tools/lib/progress.py` replica la regola di sblocco di `site/app.js`. Il test `tests/test_unlock_parity.py`
esegue le due versioni sulle stesse fixture e pretende lo stesso risultato: se cambi una, cambia anche l'altra.

## Regole del repo

- Commit piccoli, in inglese, all'imperativo: `Add VLAN trunk lab note`.
- Ogni PR dice cosa cambia e come provarlo in locale.
- Il design del sito si estende, non si rifà: stessi token in `style.css`, stessa fascia, stesse schede.
- Nessun framework, nessun build step: il sito deve funzionare aprendo `site/` da un server statico.
