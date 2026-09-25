// Reads data/progress.json and fills in:
//   [data-progress]        the row of cells
//   [data-progress-label]  "3 of 8 missions done"
//   [data-missions]        the full list (progress page)
//   [data-earned]          skills earned so far (cv page)
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
  const done = missions.filter(m => m.done);

  document.querySelectorAll("[data-progress]").forEach(el => {
    el.innerHTML = missions.map(m =>
      `<span class="cell${m.done ? " done" : ""}" title="${m.n}. ${m.title}"></span>`
    ).join("");
  });

  document.querySelectorAll("[data-progress-label]").forEach(el => {
    el.textContent = `${done.length} of ${missions.length} missions done`;
  });

  document.querySelectorAll("[data-missions]").forEach(el => {
    const repo = data.repo && !data.repo.includes("CHANGE-ME") ? data.repo : null;
    el.innerHTML = missions.map(m => {
      const link = repo
        ? `<a href="${repo}/blob/main/missioni/${String(m.n).padStart(2, "0")}.md">${m.title}</a>`
        : m.title;
      return `<li class="${m.done ? "done" : ""}">
        <span class="n">${m.n}</span>
        <span>${link}</span>
        <span class="status">${m.done ? "done" : "not yet"}</span>
        <span class="skill">${m.skill}</span>
      </li>`;
    }).join("");
  });

  document.querySelectorAll("[data-earned]").forEach(el => {
    el.innerHTML = done.length
      ? done.map(m => `<li>${m.skill}</li>`).join("")
      : `<li class="empty">Nothing yet. The first line appears when mission 1 is done.</li>`;
  });
})();
