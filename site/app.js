// Reads data/progress.json and fills in:
//   [data-progress]        the row of cells (missions + bosses)
//   [data-progress-label]  "3 of 8 missions done"
//   [data-level]           "Level 1 · Operator"
//   [data-tiers]           the campaign (progress page)
//   [data-earned]          skills and badges earned so far (cv page)
//   [data-incidents]       post-mortems list (progress page)
// Alberto: you do not need to touch this file. Edit data/progress.json instead.

(async function () {
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
  const byN = Object.fromEntries(missions.map(m => [m.n, m]));
  const done = missions.filter(m => m.done);
  const bossesDone = tiers.filter(t => t.boss && t.boss.done);
  const repo = data.repo && !data.repo.includes("CHANGE-ME") ? data.repo : null;
  const pad = n => String(n).padStart(2, "0");

  // a mission is unlocked when the previous one is done
  const unlocked = m => m.n === 1 || (byN[m.n - 1] && byN[m.n - 1].done);
  const tierComplete = t => t.missions.every(n => byN[n] && byN[n].done);

  const levelNames = ["Recruit", ...tiers.map(t => t.name)];
  const level = bossesDone.length;

  document.querySelectorAll("[data-level]").forEach(el => {
    el.textContent = `Level ${level} \u00b7 ${levelNames[level] || levelNames[levelNames.length - 1]}`;
  });

  document.querySelectorAll("[data-progress]").forEach(el => {
    el.innerHTML = tiers.length
      ? tiers.map(t => {
          const cells = t.missions.map(n => {
            const m = byN[n];
            return `<span class="cell${m && m.done ? " done" : ""}" title="${n}. ${m ? m.title : ""}"></span>`;
          }).join("");
          const boss = `<span class="cell boss${t.boss && t.boss.done ? " done" : ""}" title="${t.boss ? t.boss.title : "Boss"}"></span>`;
          return `<span class="tier-cells">${cells}${boss}</span>`;
        }).join("")
      : missions.map(m => `<span class="cell${m.done ? " done" : ""}" title="${m.n}. ${m.title}"></span>`).join("");
  });

  document.querySelectorAll("[data-progress-label]").forEach(el => {
    el.textContent = `${done.length} of ${missions.length} missions, ${bossesDone.length} of ${tiers.length} bosses`;
  });

  document.querySelectorAll("[data-tiers]").forEach(el => {
    el.innerHTML = tiers.map(t => {
      const items = t.missions.map(n => {
        const m = byN[n];
        if (!m) return "";
        const open = unlocked(m);
        const link = repo && open ? `<a href="${repo}/blob/main/missioni/${pad(m.n)}.md">${m.title}</a>` : m.title;
        const status = m.done ? "done" : open ? "open" : "locked";
        return `<li class="${status}"><span class="n">${m.n}</span><span>${link}</span><span class="status">${status}</span><span class="skill">${m.skill}</span></li>`;
      }).join("");
      const bossOpen = tierComplete(t);
      const bossStatus = t.boss.done ? "done" : bossOpen ? "open" : "locked";
      const bossLink = repo && bossOpen ? `<a href="${repo}/blob/main/missioni/BOSS-${t.id}.md">${t.boss.title}</a>` : t.boss.title;
      const boss = `<li class="boss ${bossStatus}"><span class="n">\u2726</span><span>${bossLink}</span><span class="status">${bossStatus}</span><span class="skill">Badge: ${t.boss.badge}</span></li>`;
      return `<section class="tier${t.boss.done ? " cleared" : ""}">
        <h2>Level ${t.id}: ${t.name}</h2>
        <p class="tier-line">${t.line}</p>
        <ol class="missions">${items}${boss}</ol>
      </section>`;
    }).join("");
  });

  document.querySelectorAll("[data-earned]").forEach(el => {
    const lines = [
      ...done.map(m => `<li>${m.skill}</li>`),
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
