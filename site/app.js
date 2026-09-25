// Reads data/site.json and applies it to the page:
//   :root CSS variables      from "colors" and "fonts"
//   [data-site="key"]        common texts (name, kicker, tagline, email, footer.left, ...)
//   header nav               rebuilt from "nav"
//   [data-site-show="key"]   hidden when show.key is false
//   [data-order]             CV sections sorted by number, then renumbered
// Reads data/progress.json and fills in:
//   [data-progress]        campaign cells (missions + bosses)
//   [data-progress-label]  "3 of 20 missions, 1 of 6 bosses"
//   [data-level]           "Level 1 · Operator"
//   [data-tiers]           the campaign (progress page)
//   [data-tracks]          parallel tracks: Voice, Hire (progress page)
//   [data-earned]          skills and badges earned so far (cv page)
//   [data-incidents]       post-mortems list (progress page)
//   [data-certs]           certification catalogue with prerequisites and status (certs page)
// Alberto: you do not need to touch this file. Edit data/progress.json instead.

// Unlock rule, kept as a pure function so tools/lib/progress.py can be tested against it.
// Returns { missions: {n: status}, bosses: {tierId: status}, tracks: {id: [status, ...]} }
// where status is "done", "open" or "locked".
//   - mission 1 is open; mission n is open when mission n-1 is done
//   - a boss is open when every mission of its level is done
//   - a track step is open when it is the first one or the previous step is done
function unlockStatus(data) {
  const missions = data.missions || [];
  const tiers = data.tiers || [];
  const tracks = data.tracks || [];
  const byN = Object.fromEntries(missions.map(m => [m.n, m]));
  const unlocked = m => m.n === 1 || !!(byN[m.n - 1] && byN[m.n - 1].done);
  const tierComplete = t => t.missions.every(n => byN[n] && byN[n].done);
  const out = { missions: {}, bosses: {}, tracks: {} };
  missions.forEach(m => { out.missions[m.n] = m.done ? "done" : unlocked(m) ? "open" : "locked"; });
  tiers.forEach(t => { out.bosses[t.id] = t.boss.done ? "done" : tierComplete(t) ? "open" : "locked"; });
  tracks.forEach(t => {
    out.tracks[t.id] = t.steps.map((s, i) => s.done ? "done" : (i === 0 || t.steps[i - 1].done) ? "open" : "locked");
  });
  return out;
}

// Everything in site.json is optional: a missing key leaves the HTML as it is.
function applySite(site, base) {
  const root = document.documentElement;
  const get = key => key.split(".").reduce((o, k) => (o == null ? undefined : o[k]), site);

  Object.entries(site.colors || {}).forEach(([k, v]) => root.style.setProperty("--" + k, v));
  if (site.colors && site.colors.navy) {
    document.querySelectorAll('meta[name="theme-color"]').forEach(m => m.setAttribute("content", site.colors.navy));
  }
  const fonts = site.fonts || {};
  ["heading", "body", "mono"].forEach(k => { if (fonts[k]) root.style.setProperty("--font-" + k, fonts[k]); });
  if (fonts.stylesheet && !document.querySelector(`link[href="${fonts.stylesheet}"]`)) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = fonts.stylesheet;
    document.head.appendChild(link);
  }

  document.querySelectorAll("[data-site]").forEach(el => {
    const key = el.dataset.site;
    const value = get(key);
    if (typeof value !== "string") return;
    if (key === "domain") {
      const i = value.indexOf(".");
      el.textContent = "";
      el.append(i < 0 ? value : value.slice(0, i));
      if (i >= 0) {
        const dot = document.createElement("span");
        dot.className = "dot";
        dot.textContent = ".";
        el.append(dot, value.slice(i + 1));
      }
      return;
    }
    if (key === "email" && el.tagName === "A") el.href = "mailto:" + value;
    el.textContent = value;
  });

  if (Array.isArray(site.nav) && site.nav.length) {
    const here = location.pathname.replace(/index\.html$/, "");
    document.querySelectorAll("header.top nav").forEach(nav => {
      nav.textContent = "";
      [...site.nav].sort((a, b) => (a.order || 0) - (b.order || 0)).forEach(item => {
        const a = document.createElement("a");
        a.href = base + item.path;
        a.textContent = item.label;
        const target = new URL(a.href, location.href).pathname.replace(/index\.html$/, "");
        if (target === here) a.setAttribute("aria-current", "page");
        nav.appendChild(a);
      });
    });
  }

  const show = site.show || {};
  document.querySelectorAll("[data-site-show]").forEach(el => {
    el.hidden = show[el.dataset.siteShow] === false;
  });

  // CV sections: sort siblings that carry data-order, keep them where the first one was, renumber "01", "02"...
  const parents = new Set([...document.querySelectorAll("[data-order]")].map(el => el.parentElement));
  parents.forEach(parent => {
    const items = [...parent.children].filter(c => c.hasAttribute("data-order"));
    const sorted = [...items].sort((a, b) => Number(a.dataset.order) - Number(b.dataset.order));
    const marker = document.createComment("order");
    parent.insertBefore(marker, items[0]);
    sorted.forEach(c => parent.insertBefore(c, marker));
    marker.remove();
    sorted.forEach((c, i) => {
      const num = c.querySelector("h2 .num");
      if (num && /^\d+$/.test(num.textContent.trim())) num.textContent = String(i + 1).padStart(2, "0");
    });
  });
}

// Certification status, pure so it can be tested from Node.
// Returns { state, missing } where state is one of
// "passed" | "granted" | "requested" | "ready" | "locked" and missing lists the prerequisites not done yet.
// A prerequisite is "mission:N", "boss:N" or "track:ID:N" (same ids as data/evidence-rules.yaml).
function certStatus(cert, statusMap, data) {
  const missions = data.missions || [];
  const tiers = data.tiers || [];
  const tracks = data.tracks || [];
  const label = ref => {
    const [kind, a, b] = ref.split(":");
    if (kind === "mission") { const m = missions.find(x => String(x.n) === a); return { done: !!(m && m.done), title: m ? `Mission ${m.n}: ${m.title}` : ref }; }
    if (kind === "boss") { const t = tiers.find(x => String(x.id) === a); return { done: !!(t && t.boss.done), title: t ? t.boss.title : ref }; }
    if (kind === "track") { const t = tracks.find(x => x.id === a); const st = t && t.steps.find(x => String(x.n) === b); return { done: !!(st && st.done), title: st ? `${t.name} ${b}: ${st.title}` : ref }; }
    return { done: false, title: ref };
  };
  const prereqs = (cert.prereq_steps || []).map(label);
  const missing = prereqs.filter(x => !x.done).map(x => x.title);
  const manual = (statusMap || {})[cert.id];
  if (manual === "passed" || manual === "granted" || manual === "requested") return { state: manual, missing };
  return { state: missing.length ? "locked" : "ready", missing };
}

if (typeof module !== "undefined" && module.exports) { module.exports = { unlockStatus, certStatus }; }

if (typeof document !== "undefined") (async function () {
  const base = document.body.dataset.root || "./";
  const fetchJson = async name => {
    const res = await fetch(base + "data/" + name, { cache: "no-store" });
    if (!res.ok) throw new Error(res.status + " " + res.statusText);
    return res.json();
  };
  const [siteRes, progressRes, certsRes] = await Promise.allSettled([fetchJson("site.json"), fetchJson("progress.json"), fetchJson("certs.json")]);
  if (siteRes.status === "fulfilled") {
    try { applySite(siteRes.value, base); } catch (e) { console.error("Could not apply site.json", e); }
  } else {
    console.warn("Could not load site.json, keeping the texts in the HTML", siteRes.reason);
  }
  if (progressRes.status !== "fulfilled") {
    console.error("Could not load progress.json", progressRes.reason);
    return;
  }
  const data = progressRes.value;

  const missions = data.missions || [];
  const tiers = data.tiers || [];
  const tracks = data.tracks || [];
  const byN = Object.fromEntries(missions.map(m => [m.n, m]));
  const done = missions.filter(m => m.done);
  const bossesDone = tiers.filter(t => t.boss && t.boss.done);
  const repo = data.repo && !data.repo.includes("CHANGE-ME") ? data.repo : null;
  const pad = n => String(n).padStart(2, "0");
  const mdLink = (file, label) => repo ? `<a href="${repo}/blob/main/missioni/${file}">${label}</a>` : label;

  const status = unlockStatus(data);

  const levelNames = ["Recruit", ...tiers.map(t => t.name)];
  const level = bossesDone.length;

  document.querySelectorAll("[data-level]").forEach(el => {
    el.textContent = `Level ${level} \u00b7 ${levelNames[Math.min(level, levelNames.length - 1)]}`;
  });

  document.querySelectorAll("[data-progress]").forEach(el => {
    el.innerHTML = tiers.map(t => {
      const cells = t.missions.map(n => {
        const m = byN[n];
        return `<span class="cell${m && m.done ? " done" : ""}" title="${n}. ${m ? m.title : ""}"></span>`;
      }).join("");
      const boss = `<span class="cell boss${t.boss.done ? " done" : ""}" title="${t.boss.title}"></span>`;
      return `<span class="tier-cells" title="Level ${t.id}: ${t.name}">${cells}${boss}</span>`;
    }).join("");
  });

  document.querySelectorAll("[data-progress-label]").forEach(el => {
    const trackDone = tracks.reduce((a, t) => a + t.steps.filter(s => s.done).length, 0);
    const trackAll = tracks.reduce((a, t) => a + t.steps.length, 0);
    el.textContent = `${done.length} of ${missions.length} missions, ${bossesDone.length} of ${tiers.length} bosses, ${trackDone} of ${trackAll} track steps`;
  });

  document.querySelectorAll("[data-tiers]").forEach(el => {
    el.innerHTML = tiers.map(t => {
      const items = t.missions.map(n => {
        const m = byN[n];
        if (!m) return "";
        const st = status.missions[m.n];
        const open = st !== "locked";
        const file = m.file || `${pad(m.n)}.md`;
        const link = open ? mdLink(file, m.title) : m.title;
        return `<li class="${st}"><span class="n">${pad(m.n)}</span><span>${link}</span><span class="status">${st}</span><span class="skill">${m.skill}</span></li>`;
      }).join("");
      const bossStatus = status.bosses[t.id];
      const bossOpen = bossStatus !== "locked";
      const bossLink = bossOpen ? mdLink(`BOSS-${t.id}.md`, t.boss.title) : t.boss.title;
      const boss = `<li class="boss ${bossStatus}"><span class="n">\u2726</span><span>${bossLink}</span><span class="status">${bossStatus}</span><span class="skill">Badge: ${t.boss.badge}</span></li>`;
      return `<section class="tier${t.boss.done ? " cleared" : ""}">
        <h2><span class="num">LEVEL ${t.id}</span>${t.name}</h2>
        <p class="tier-line">${t.line}</p>
        <ol class="missions">${items}${boss}</ol>
      </section>`;
    }).join("");
  });

  document.querySelectorAll("[data-tracks]").forEach(el => {
    el.innerHTML = tracks.map(t => {
      const doneCount = t.steps.filter(s => s.done).length;
      const cells = t.steps.map(s => `<span class="cell${s.done ? " done" : ""}" title="${s.n}. ${s.title}"></span>`).join("");
      const items = t.steps.map((s, i) => {
        const st = status.tracks[t.id][i];
        const open = st !== "locked";
        const link = open ? mdLink(t.file, s.title) : s.title;
        return `<li class="${st}"><span class="n">${t.id.charAt(0).toUpperCase()}${s.n}</span><span>${link}</span><span class="status">${st}</span><span class="skill">${s.skill}</span></li>`;
      }).join("");
      return `<section class="tier track${doneCount === t.steps.length ? " cleared" : ""}">
        <h2><span class="num">TRACK</span>${t.name}</h2>
        <p class="tier-line">${t.line}</p>
        <div class="progress track-progress">${cells}</div>
        <ol class="missions">${items}</ol>
      </section>`;
    }).join("");
  });

  document.querySelectorAll("[data-earned]").forEach(el => {
    const lines = [
      ...done.map(m => `<li>${m.skill}</li>`),
      ...tracks.flatMap(t => t.steps.filter(s => s.done).map(s => `<li class="track-${t.id}">${s.skill}</li>`)),
      ...bossesDone.map(t => `<li class="badge">${t.boss.badge}</li>`)
    ];
    el.innerHTML = lines.length ? lines.join("") : `<li class="empty">Nothing yet. The first line appears when mission 1 is done.</li>`;
  });

  document.querySelectorAll("[data-certs]").forEach(el => {
    if (certsRes.status !== "fulfilled") { el.innerHTML = `<li class="empty-state">Could not load certs.json.</li>`; return; }
    const certs = certsRes.value.certs || [];
    const statusMap = certsRes.value.status || {};
    const issueUrl = cert => repo
      ? `${repo}/issues/new?template=cert-request.yml&labels=cert-request&title=${encodeURIComponent("Cert: " + cert.name)}&kind=${encodeURIComponent("certificazione")}&item=${encodeURIComponent(cert.id)}`
      : null;
    const esc = t => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
    const order = { ready: 0, requested: 1, granted: 2, passed: 3, locked: 4 };
    const rows = certs.map(c => ({ c, s: certStatus(c, statusMap, data) }))
      .sort((a, b) => order[a.s.state] - order[b.s.state] || a.c.name.localeCompare(b.c.name));
    el.innerHTML = rows.map(({ c, s }) => {
      const study = (c.study_free || []).map(u => `<a href="${esc(u)}">${esc(new URL(u).hostname.replace(/^www\./, ""))}</a>`).join(", ");
      const prereq = s.missing.length
        ? `Unlocks after: ${s.missing.map(esc).join("; ")}`
        : (c.prereq_steps || []).length ? "Prerequisites done." : "No prerequisites.";
      const action = s.state === "ready" && issueUrl(c)
        ? `<a class="button" href="${issueUrl(c)}">Ask Stefano</a>`
        : s.state === "passed" ? `<span class="skill">Passed. Proof in certs/proof/.</span>`
        : s.state === "granted" ? `<span class="skill">Granted: book the exam.</span>`
        : s.state === "requested" ? `<span class="skill">Requested, waiting for Stefano.</span>` : "";
      return `<li class="cert ${s.state}">
        <span class="n mono">${esc(c.cost_eur)}&#8364;</span>
        <span><strong>${esc(c.name)}</strong> <span class="mono cert-vendor">${esc(c.vendor)} &middot; ${esc(c.kind)}</span><br>${esc(c.why)}<br><span class="cert-study">Study free: ${study || "see the sheet"}</span></span>
        <span class="status">${s.state}</span>
        <span class="skill">${prereq}</span>
        <span class="cert-action">${action}</span>
      </li>`;
    }).join("") || `<li class="empty-state">No certifications in the catalogue yet.</li>`;
  });

  document.querySelectorAll("[data-incidents]").forEach(el => {
    const inc = data.incidents || [];
    el.innerHTML = inc.length
      ? inc.map(i => `<li><span class="date mono">${i.date}</span><a href="${i.url}">${i.title}</a></li>`).join("")
      : `<li class="empty-state">No incidents yet. They start at Level 2.</li>`;
  });
})();
