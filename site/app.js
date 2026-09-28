// Reads data/progress.json and fills in:
//   [data-progress]        campaign cells (missions + bosses)
//   [data-progress-label]  "3 of 20 missions, 1 of 6 bosses"
//   [data-level]           "Level 1 · Operator"
//   [data-tiers]           the campaign (progress page)
//   [data-tracks]          parallel tracks: Voice, Hire (progress page)
//   [data-earned]          skills and badges earned so far (cv page)
//   [data-incidents]       post-mortems list (progress page)
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

if (typeof module !== "undefined" && module.exports) { module.exports = { unlockStatus }; }

if (typeof document !== "undefined") (async function () {
  const base = document.body.dataset.root || "./";
  let data;
  try {
    const res = await fetch(base + "data/progress.json", { cache: "no-store" });
    data = await res.json();
  } catch (e) {
    console.error("Could not load progress.json", e);
    return;
  }

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

  document.querySelectorAll("[data-incidents]").forEach(el => {
    const inc = data.incidents || [];
    el.innerHTML = inc.length
      ? inc.map(i => `<li><span class="date mono">${i.date}</span><a href="${i.url}">${i.title}</a></li>`).join("")
      : `<li class="empty-state">No incidents yet. They start at Level 2.</li>`;
  });
})();
