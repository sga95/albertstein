# albertstein.link

Learning path of Alberto Galliani in networking and IT: missions, tracks, lab notes and a CV that grows with completed steps. Static HTML, no build step, published with Cloudflare Pages.

- `site/` is what gets published. Output directory for Pages: `site`.
- `site/data/progress.json` drives the progress bar, the mission list and the "earned" section of the CV. Only Alberto edits it.
- `site/data/site.json` holds the common texts, menu, colors and fonts. See `site/THEME.md`.
- `missioni/` contains the guided steps (in Italian). Start from `INIZIA-QUI.md`.
- `data/` holds what Alberto wants (`me.yaml`), the skill taxonomy, the role profiles and the evidence rules. `engine/core/` turns them, plus `progress.json` and the repo, into `site/data/readiness.json` and the `/readiness` page. See `engine/BRIEF.md`.

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
| `make engine` | Recompute `site/data/readiness.json` and `site/readiness/` from the evidence (needs `pip install pyyaml`) |

## Checks on every pull request

`.github/workflows/ci.yml`: the same checks as `make check`, plus W3C HTML validation, a comment with the lab-note score, and secret scanning with gitleaks.
`.github/workflows/guard-progress.yml`: `site/data/progress.json` can only be changed by Alberto.
`.github/workflows/engine-build.yml`: on `main`, regenerates the readiness page when progress, data or lab notes change.
