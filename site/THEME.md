# Il tema del sito, spiegato

Il sito è HTML + `style.css` + `app.js`. Niente build, niente framework. Puoi cambiare testi, colori,
font, menu e sezioni da **un file solo**, `data/site.json`. Quando vuoi di più, l'HTML e il CSS sono tuoi.

Regola: il design si estende, non si rifà. Stessa fascia navy in alto, stesse schede, stesse etichette.
Cambiare i colori e i font dentro questa struttura è previsto. Rifare la struttura è un altro progetto.

## 1. `data/site.json`: cosa fa ogni chiave

`app.js` legge questo file all'apertura di ogni pagina. Ogni chiave è **opzionale**: se manca, resta quello
che c'è scritto nell'HTML. Se il file ha un errore di sintassi, il sito resta com'è e la console del browser
lo dice (`make check` te lo dice prima).

| Chiave | Dove finisce | Note |
|---|---|---|
| `name` | `<h1>` del CV | Il tuo nome. |
| `domain` | il marchio in alto a sinistra | La parte prima del primo punto resta bianca, il punto diventa arancione. |
| `role` | riga sotto il nome nel CV | Una frase: chi sei. |
| `email` | i link email in home e nel CV | Aggiorna sia il testo che il `mailto:`. Da S3 (Shield) qui va la Proton. |
| `kicker` | la riga piccola arancione sopra il titolo della home | |
| `tagline` | il titolo grande della home | |
| `lede` | il paragrafo sotto il titolo della home | |
| `nav` | il menu in alto, su tutte le pagine | Lista di `{ "label", "path", "order" }`. `path` è relativo alla radice del sito (`cv/`, `lab/`). `order` decide la posizione. La pagina corrente prende da sola la sottolineatura. Una voce con `"needs": "codex"` (o `puzzle`, `reading`) compare solo quando quella pagina ha contenuto, vedi `show`. |
| `colors` | le variabili CSS in `:root` | Vedi la tabella sotto. Le chiavi sono i nomi delle variabili senza `--`. |
| `fonts` | le tre famiglie di font e il foglio di Google Fonts | Vedi "Cambiare font". |
| `footer.left`, `footer.right` | i due testi del piede | |
| `show.photo` | la foto nel CV | `false` la nasconde e il titolo si allarga. |
| `show.incidents` | la scheda "Incidents" nella pagina Progress | |
| `show.tracks` | la sezione "Tracks" nella pagina Progress | |
| `show.notesOnHome` | la scheda "Latest lab notes" in home | |
| `show.nowPlaying` | la scheda "Now playing" in home | Compare solo se in `progress.json` c'è una quest iniziata e non finita. |
| `show.loot` | la riga "Loot" sotto ogni boss nella pagina Progress | `sealed` finché il boss non è done. |
| `show.puzzle`, `show.reading`, `show.codex` | le voci di menu Puzzle, Reading, Codex | Se non ci sono, la voce compare da sola quando la pagina ha almeno una voce (conteggio in `data/pages.json`, rigenerato da `make engine`). `true` la forza, `false` la nasconde. |
| `levels` | i nomi dei livelli nella pagina Progress e nella riga "Level N" | Oggetto `{"0": "Recruit", "1": "Operator", ...}`: solo le chiavi che metti cambiano nome; i badge restano quelli di `progress.json`. |

Come sono collegati HTML e JSON: nell'HTML gli elementi hanno `data-site="chiave"` (testi) o
`data-site-show="chiave"` (sezioni). Se aggiungi un elemento con `data-site="kicker"` in una pagina nuova,
riceve lo stesso testo. Le chiavi con il punto (`footer.left`) leggono dentro un oggetto.

Gli schemi in `engine/schema/site.schema.json` e `make check` ti dicono se una chiave è scritta male.

## 2. I token CSS, uno per uno

Sono definiti in `style.css` dentro `:root`, e `site.json` può sovrascriverli. Tutto il foglio di stile usa
solo questi: cambiando un token cambia ogni posto dove è usato.

| Token | Valore | Dove si vede |
|---|---|---|
| `--navy` | `#0b2b4c` | Fascia in alto (header + hero), bordo dei passi aperti, testo delle etichette nel CV. Il colore che identifica il sito. |
| `--navy-deep` | `#071d34` | Piede della pagina e sfondo dei blocchi `<pre>` (terminale). Una tonalità più scura del navy. |
| `--accent` | `#f2a33a` | Il punto nel marchio, i numeri delle sezioni, la barra di progresso, il bordo della foto, l'etichetta `done`, il focus della tastiera. Riservato a "progresso e numeri": se lo usi ovunque, non dice più niente. |
| `--paper` | `#ffffff` | Sfondo della pagina e delle schede. |
| `--dot` | `#d3dbe4` | I puntini del corpo pagina (la griglia da quaderno). Più chiaro sparisce, più scuro disturba la lettura. |
| `--ink` | `#14212e` | Testo principale. |
| `--ink-soft` | `#4b5b6b` | Testo secondario: date, righe di spiegazione, stati `locked`. |
| `--line` | `#dfe5ec` | Bordi delle schede e righe tra le missioni. |
| `--sky` | `#b9c9da` | Testo chiaro sulla fascia navy: il paragrafo sotto il titolo, le voci di menu non attive, il piede. |
| `--measure` | `64ch` | Larghezza massima di un paragrafo. Non sta in `site.json`: si cambia nel CSS. |
| `--font-heading` | Space Grotesk | Titoli, marchio, nome dei boss. |
| `--font-body` | IBM Plex Sans | Tutto il testo. |
| `--font-mono` | IBM Plex Mono | Etichette maiuscole, numeri, date, codice, menu. |

Contrasto: `--ink` su `--paper` e `#fff` su `--navy` sono leggibili. Se cambi navy o paper, controlla che
`--sky` resti leggibile sulla fascia e che `--accent` si veda su entrambi. Un controllo veloce:
https://webaim.org/resources/contrastchecker/ (minimo 4.5:1 per il testo).

## 3. Tre varianti pronte

Incolla il blocco `colors` in `data/site.json` al posto di quello che c'è. Il resto del file resta.

### Scuro

Fascia e corpo scuri, testo chiaro, accento invariato.

```json
"colors": {
  "navy": "#0f1720",
  "navy-deep": "#080d13",
  "accent": "#f2a33a",
  "paper": "#151d27",
  "dot": "#22303d",
  "ink": "#e6edf3",
  "ink-soft": "#9fb0c0",
  "line": "#2a3947",
  "sky": "#9fb0c0"
}
```

Nota: i blocchi `<pre>` usano `--navy-deep` come sfondo, quindi restano leggibili.

### Monocromo

Niente arancione: tutto in una scala di grigi-blu. L'accento diventa il navy stesso, quindi la barra di
progresso e i numeri sono scuri su bianco.

```json
"colors": {
  "navy": "#1f2933",
  "navy-deep": "#111820",
  "accent": "#cbd2d9",
  "paper": "#ffffff",
  "dot": "#e4e7eb",
  "ink": "#1f2933",
  "ink-soft": "#616e7c",
  "line": "#e4e7eb",
  "sky": "#cbd2d9"
}
```

Attenzione: con l'accento chiaro, l'etichetta `done` (testo navy su accento) resta leggibile, ma il
punto nel marchio quasi sparisce. Se non ti piace, tieni `"accent": "#3e4c59"`.

### Con foto grande

I colori restano. Cambia il CSS del CV: in `style.css`, sezione `/* ---------- cv ---------- */`:

```css
.cv-hero .wrap { grid-template-columns: 12rem 1fr; gap: 2rem; }
.cv-hero img { width: 12rem; height: 14rem; border-radius: 20px; }
```

e nel blocco `@media (max-width: 40rem)`:

```css
.cv-hero .wrap { grid-template-columns: 1fr; }
.cv-hero img { width: 9rem; height: 10.5rem; }
```

La foto va in `cv/photo.jpg`, sotto i 300 KB (`make check` lo controlla), ritagliata circa 6:7.

## 4. Cambiare font

In `data/site.json`:

```json
"fonts": {
  "heading": "\"Sora\", \"IBM Plex Sans\", sans-serif",
  "body": "\"Inter\", system-ui, sans-serif",
  "mono": "\"JetBrains Mono\", ui-monospace, monospace",
  "stylesheet": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&family=Sora:wght@500;700&display=swap"
}
```

- `heading`, `body`, `mono` sono liste di font come in CSS: il primo che c'è vince, l'ultimo è la famiglia generica.
- `stylesheet` è l'URL di Google Fonts: su fonts.google.com scegli i font, i pesi 400 e 600 per il testo e
  500 e 700 per i titoli, e copia il link. `app.js` lo aggiunge alla pagina se non c'è già.
- Il `<link>` scritto nell'HTML di ogni pagina resta quello di Plex e Space Grotesk: puoi lasciarlo (scarica
  due fogli, uno inutile) o sostituirlo a mano in tutte le pagine quando hai deciso.
- Senza rete i font di Google non arrivano e il browser usa la famiglia generica. Il sito resta leggibile.

Un font a caso peggiora il sito più di un colore a caso. Un titolo geometrico (Space Grotesk, Sora,
Manrope) e un testo neutro (Plex Sans, Inter, Source Sans) funzionano quasi sempre.

## 5. Ordinare le sezioni del CV

In `cv/index.html` ogni scheda ha `data-order="N"`. `app.js` le ordina per numero e rinumera i `01`, `02`
di conseguenza. Per mettere "Skills" prima di "About me": dai a Skills `data-order="0"` (o scambia i numeri).
Se togli `data-order` a tutte, l'ordine è quello del file. La riga "Print or save as PDF" resta sempre in fondo.

Solo le schede con `data-order` vengono ordinate: una scheda nuova senza l'attributo resta dove la scrivi.

## 6. Aggiungere una pagina con fascia e menu giusti

1. Copia `lab/template.html` (per una nota) o `progress/index.html` (per una pagina di sito) nella cartella
   nuova, per esempio `now/index.html`.
2. Controlla tre cose in testa al file:
   - `<link rel="stylesheet" href="../style.css">`: il percorso relativo a `style.css`. Da `now/` è `../`.
   - `<body data-root="../">`: la stessa profondità. Da qui `app.js` trova `data/` e costruisce il menu.
   - `<script src="../app.js"></script>` in fondo, se la pagina deve avere il menu da `site.json`,
     il livello e la barra di progresso.
3. Il blocco `.band` (header + hero) è sempre uguale: marchio con `data-site="domain"`, `<nav>` (viene
   riscritto da `app.js`, ma lascialo scritto: funziona anche senza JS), poi `.hero` con `kicker`, `h1`, `lede`.
4. Il contenuto va in `<main><div class="wrap">` dentro `<div class="card">`, con `<h2><span class="num">01</span>Titolo</h2>`.
5. `make check` ti dice se un link o un'immagine mancano.

Esempio minimo:

```html
<body data-root="../">
  <div class="band">
    <header class="top"><div class="wrap">
      <a class="brand" href="../" data-site="domain">albertstein<span class="dot">.</span>link</a>
      <nav><a href="../cv/">CV</a><a href="../lab/">Lab</a><a href="../progress/">Progress</a></nav>
    </div></header>
    <section class="hero"><div class="wrap">
      <p class="kicker">Now</p>
      <h1>What I am doing this month.</h1>
      <p class="lede">One line that says why this page exists.</p>
    </div></section>
  </div>
  <main><div class="wrap">
    <div class="card"><h2><span class="num">01</span>This month</h2><p>...</p></div>
  </div></main>
  <footer class="bottom"><div class="wrap">
    <span data-site="footer.left">albertstein.link</span>
    <span data-site="footer.right">Learning path in networking and IT</span>
  </div></footer>
  <script src="../app.js"></script>
</body>
```

## 7. Aggiungere una voce di menu

In `data/site.json`, dentro `nav`:

```json
{ "label": "Now", "path": "now/", "order": 4 }
```

`make check` verifica che `now/index.html` esista. Il menu cambia su tutte le pagine, compresa la 404.
Le pagine hanno anche un `<nav>` scritto nell'HTML: è quello che si vede se `app.js` non parte; aggiornalo
a mano quando hai tempo, con `make check` a controllare i link.

## 8. Esportare il CV in PDF

`make pdf` apre `cv/` in un Chromium headless e scrive `cv/Alberto-Galliani-CV.pdf` con lo stile di stampa
(niente menu, niente fascia colorata, foto e contatti in testa). Serve Playwright, solo per questo comando:

```
pip install playwright
python3 -m playwright install chromium
make pdf
```

Il PDF non lo genera la CI: lo rigeneri tu quando il CV cambia e lo committi se vuoi che sia scaricabile.
Lo stesso risultato si ottiene con "Print or save as PDF" in fondo alla pagina CV.

## 9. Cosa NON cambiare da `site.json`

Il contenuto delle pagine (CV, note, testi delle missioni) sta nell'HTML: è tuo, si modifica lì.
`data/progress.json` è lo stato del percorso, non del tema. `app.js` legge entrambi ma non scrive mai.
