# albertstein.link

Learning path of Alberto Galliani in networking and IT: missions, tracks, lab notes and a CV that grows with completed steps. Static HTML, no build step, published with Cloudflare Pages.

- `site/` is what gets published. Output directory for Pages: `site`.
- `site/data/progress.json` drives the progress bar, the mission list and the "earned" section of the CV. Only Alberto edits it.
- `site/data/site.json` holds the common texts, menu, colors and fonts. See `site/THEME.md`.
- `missioni/` contains the guided steps (in Italian). Start from `INIZIA-QUI.md`.
- `data/` holds what Alberto wants (`me.yaml`), the skill taxonomy, the role profiles, the evidence rules, the certification catalogue (`certs.yaml`), the quests (`quests.yaml`), the boss rewards (`loot.yaml`), the hardware (`hardware.yaml`) and the weekly puzzles (`puzzles.yaml`). `engine/core/` turns them, plus `progress.json` and the repo, into the generated files in `site/data/` and the `/readiness` page. See `engine/BRIEF.md`.

## Pages

| Page | What it shows |
|---|---|
| `/` | Home: level, progress bar, latest notes, the quest being played |
| `/cv/` | CV, with the lines earned on the path |
| `/lab/` | Lab notes and post-mortems |
| `/progress/` | Levels, missions, bosses with their loot, tracks, incidents |
| `/quests/` | Optional quests by passion, state from `progress.json` |
| `/readiness/` | Generated: readiness per target role, skill levels, verified or not |
| `/certs/` | Certification catalogue, prerequisites, "Ask Stefano" when ready |
| `/gear/` | Hardware for the path, in kits, askable when a step that uses it is open |
| `/puzzle/`, `/reading/`, `/codex/` | Weekly puzzle, reading log, glossary. In the menu once they have content |

## Commands

Python 3 and `make`, nothing else to install. Details in `CONTRIBUTING.md` (in Italian).

| Command | What it does |
|---|---|
| `make serve` | Local site at http://localhost:8080/ |
| `make check` | Every check the CI runs: `progress.json` and `site.json` against their schemas, unlock order, links, images, `alt`, page weight, lab-note score |
| `make test` | Tests for the tools (`pip install pytest`) |
| `make note TITLE="..."` | New lab note from the template, listed at the top of `site/lab/` |
| `make postmortem TITLE="..."` | New post-mortem from its template |
| `make pdf` | Export the CV to `site/cv/Alberto-Galliani-CV.pdf` (needs Playwright, only for this command) |
| `make engine` | Regenerate `site/data/*.json` (readiness, certs, quests, loot, puzzles, page counts) and `site/readiness/` (needs `pip install pyyaml`) |
| `make quiz` | Subnetting sprint: 20 random exercises in 10 minutes |

## Checks on every pull request

`.github/workflows/ci.yml`: the same checks as `make check`, plus W3C HTML validation, a comment with the lab-note score, and secret scanning with gitleaks.
`.github/workflows/guard-progress.yml`: `site/data/progress.json` can only be changed by Alberto.
`.github/workflows/engine-build.yml`: on `main` (and every Monday), regenerates the generated files when progress, data or notes change.
`.github/workflows/cert-status.yml`: a request issue opened or closed as `granted` updates the certification status.
