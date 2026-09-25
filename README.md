# albertstein.link

Learning path of Alberto Galliani in networking and IT: missions, tracks, lab notes and a CV that grows with completed steps. Static HTML, no build step, published by a Cloudflare Worker with static assets (`wrangler.jsonc`).

- `site/` is what gets published: `wrangler.jsonc` points the Worker's assets at it. Workers Builds deploys `main` and gives every pull request a preview URL.
- `site/data/progress.json` drives the progress bar, the mission list and the "earned" section of the CV.
- `missioni/` contains the guided steps (in Italian).
