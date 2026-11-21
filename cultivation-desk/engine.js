// Cultivation Desk — morning engine. Same task math as the app.
// Usage: node engine.js <dumpDir> <YYYY-MM-DD>
// dumpDir holds one JSON array per collection: strains.json, batches.json, templates.json,
// recurring.json, tasks.json, crew.json, products.json (each item {id, ...fields}).
const fs = require("fs"), path = require("path");
const [dir, today] = process.argv.slice(2);
if (!dir || !/^\d{4}-\d{2}-\d{2}$/.test(today || "")) { console.error("usage: node engine.js <dumpDir> <YYYY-MM-DD>"); process.exit(1); }
const S = {};
for (const c of ["strains","batches","templates","recurring","tasks","crew","products"]) {
  const f = path.join(dir, c + ".json"); S[c] = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : [];
}
const DAY = 864e5, STG = { prop: "Propagation", veg: "Veg", flower: "Flower" };
const toN = s => { const [y, m, d] = s.split("-").map(Number); return Math.round(Date.UTC(y, m - 1, d) / DAY); };
const toS = n => new Date(n * DAY).toISOString().slice(0, 10);
const add = (s, k) => toS(toN(s) + k);
const byId = (c, id) => S[c].find(x => x.id === id);
function spans(b) { const st = b.starts || {}, o = ["prop","veg","flower","done"], out = [];
  for (let i = 0; i < 3; i++) { const k = o[i]; if (!st[k]) continue; let end = null;
    for (let j = i + 1; j < 4; j++) if (st[o[j]]) { end = st[o[j]]; break; }
    out.push({ stage: k, area: k === "flower" ? (b.room || "Flower 1") : STG[k], start: st[k], end }); } return out; }
function genTasks(from, to) { const out = [];
  for (const b of S.batches) for (const sp of spans(b)) for (const t of S.templates.filter(t => t.stage === sp.stage)) {
    const first = Math.max(1, +t.day || 1), ev = Math.max(0, +t.every || 0), last = ev ? (+t.until || 200) : first;
    for (let d = first; d <= last; d += (ev || 1e9)) { const date = add(sp.start, d - 1);
      if (sp.end && date >= sp.end) break; if (date > to) break; if (date < from) continue;
      out.push({ id: `g~${b.id}~${t.id}~${d}`, date, area: sp.area, title: t.title, type: t.type || "Other", productId: t.productId || "", assignee: t.assignee || "", est: +t.est || 0, batchId: b.id, stage: sp.stage, day: d, status: "open" }); } }
  for (const r of S.recurring) { if (r.active === false || !r.start) continue; const ev = Math.max(1, +r.every || 7);
    let n = toN(r.start); const f = toN(from); if (n < f) n += Math.ceil((f - n) / ev) * ev;
    for (; n <= toN(to); n += ev) { const date = toS(n); if (r.end && date > r.end) break;
      out.push({ id: `r~${r.id}~${date}`, date, area: r.area, title: r.title, type: r.type || "Other", productId: r.productId || "", assignee: r.assignee || "", est: +r.est || 0, status: "open" }); } }
  return out; }
function tasksIn(from, to) { const ids = new Set(S.tasks.map(t => t.id));
  return [...genTasks(from, to).filter(t => !ids.has(t.id)), ...S.tasks.filter(t => t.date >= from && t.date <= to)]; }
const hm = m => { m = +m || 0; const h = Math.floor(m / 60), r = m % 60; return h ? (r ? `${h}h ${r}m` : `${h} hr`) : `${r} min`; };
function line(t) { const p = byId("products", t.productId), b = byId("batches", t.batchId);
  let s = `${t.title} — ${t.area}`;
  if (b) s += ` · ${b.name}${t.day ? " day " + t.day : ""}`;
  if (p) s += ` · ${p.name}: ${p.rate ? `${p.rate} ${p.unit || ""} per gallon`.replace(/\s+/g, " ") : "NO LABEL RATE ENTERED — ask your lead before mixing"}${p.rei ? `, re-entry ${p.rei} hrs` : ""}`;
  if (t.est) s += ` · ${hm(t.est)} planned`;
  return s; }
const isMon = new Date(toN(today) * DAY).getUTCDay() === 1;
const todays = tasksIn(today, today).filter(t => t.status === "open");
const week = isMon ? tasksIn(add(today, 1), add(today, 6)).filter(t => t.status === "open") : [];
const overdue = tasksIn(add(today, -14), add(today, -1)).filter(t => t.status === "open");
const people = S.crew.filter(c => c.active !== false && c.slack).map(c => {
  const mine = todays.filter(t => t.assignee === c.id).sort((a, b) => a.area.localeCompare(b.area));
  return { crewId: c.id, name: c.name, slack: c.slack,
    tasks: mine.map((t, i) => ({ n: i + 1, text: line(t), task: t })),
    week: week.filter(t => t.assignee === c.id).sort((a, b) => a.date.localeCompare(b.date)).map(t => ({ date: t.date, text: line(t) })) };
});
const noSlack = S.crew.filter(c => c.active !== false && !c.slack && todays.some(t => t.assignee === c.id)).map(c => c.name);
console.log(JSON.stringify({ today, isMonday: isMon, people,
  unassigned: todays.filter(t => !t.assignee).map(line),
  overdue: overdue.map(t => `${t.date}: ${line(t)}${t.assignee ? " — " + (byId("crew", t.assignee)?.name || "?") : " — unassigned"}`),
  crewWithTasksButNoSlackId: noSlack }, null, 1));
