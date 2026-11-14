#!/usr/bin/env python3
"""Build a single self-contained HTML trainer (images embedded as base64).

Inputs: data/terms.json, data/images.json, assets/images/*
Output: docs/index.html (standalone, offline, Android-friendly)
"""
import base64, json, os, sys
from io import BytesIO
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "assets", "images")
DOCS = os.path.join(BASE, "docs")
os.makedirs(DOCS, exist_ok=True)

terms = json.load(open(os.path.join(BASE, "data", "terms.json"), encoding="utf-8"))
categories = terms["categories"]
imgs = json.load(open(os.path.join(BASE, "data", "images.json"), encoding="utf-8"))

cards = []
for t in terms["terms"]:
    tid = t["id"]
    mi = imgs[tid]
    fpath = os.path.join(IMG, mi["file"])
    img = Image.open(fpath).convert("RGB")
    img.thumbnail((520, 520))
    buf = BytesIO()
    img.save(buf, "JPEG", quality=80, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    cards.append({
        "id": tid,
        "et": t["et"],
        "ru": t["ru"],
        "desc": t.get("desc", ""),
        "cat": t["category"],
        "b64": b64,
        "license": mi.get("license", ""),
    })

cards_json = json.dumps(cards, ensure_ascii=False)
cats_json = json.dumps(categories, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="et">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Puidutöö sõnad — Слова по дереву</title>
<style>
:root{
  --bg:#fdf6ec; --card:#ffffff; --ink:#3a3a42; --muted:#8a8a93;
  --pine:#2e7d4f; --pine2:#57b46a; --warm:#e07a3f; --warm2:#f0a05c;
  --blue:#3b6ea5; --good:#2e7d4f; --bad:#c0392b; --chip:#ffe8d2;
  --shadow:0 6px 18px rgba(80,60,30,.10);
}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  background:linear-gradient(160deg,#fdf6ec,#fbe9d2);color:var(--ink);min-height:100vh;
  -webkit-user-select:none;user-select:none}
.wrap{max-width:720px;margin:0 auto;padding:16px 14px 40px}
h1{font-size:1.35rem;margin:4px 0 2px;color:#5b4020}
h2{font-size:1rem;font-weight:500;color:var(--muted);margin:0 0 12px}
.modes{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:14px 0}
.mode{background:#fff;border:2px solid #eee3d3;border-radius:14px;padding:10px 4px;
  text-align:center;font-weight:700;font-size:.9rem;color:#b98a5a;cursor:pointer;transition:.15s}
.mode.active{border-color:var(--pine2);color:var(--pine);background:#f2fbf4;box-shadow:var(--shadow)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 16px}
.chip{background:var(--chip);border:2px solid transparent;border-radius:999px;
  padding:6px 12px;font-size:.85rem;font-weight:600;color:#9a5c2a;cursor:pointer}
.chip.active{border-color:var(--warm);color:#8a3d1d;background:#fff3e6}
.card{background:var(--card);border-radius:22px;box-shadow:var(--shadow);
  padding:10px 10px 18px;text-align:center;position:relative;min-height:340px}
.card .imgbox{position:relative;border-radius:16px;overflow:hidden;background:#f0eadf;
  width:min(100%,460px);aspect-ratio:1/1;margin:0 auto;display:flex;
  align-items:center;justify-content:center}
.card img{width:100%;height:100%;object-fit:cover;display:block}
.card .hint-license{position:absolute;right:8px;bottom:8px;background:rgba(0,0,0,.55);
  color:#fff;font-size:.68rem;padding:2px 7px;border-radius:999px}
.word-et{font-size:1.9rem;font-weight:800;margin:14px 0 2px;color:#5b4020}
.word-ru{font-size:1.15rem;color:var(--muted);margin:2px 0 12px}
.desc{font-size:.95rem;color:#7a5b39;margin:0 14px 14px;line-height:1.45}
.reveal{display:none!important}
.reveal.show{display:block!important}
.btn{display:inline-block;border:none;border-radius:14px;padding:12px 22px;
  font-size:1rem;font-weight:700;cursor:pointer;color:#fff;background:var(--warm);
  margin:4px;transition:.15s}
.btn:active{transform:scale(.97)}
.speak{position:absolute;right:10px;top:10px;background:#fff;border:2px solid #eee3d3;
  color:var(--pine);border-radius:999px;width:44px;height:44px;font-size:1.2rem;cursor:pointer;z-index:2}
.nav{display:flex;justify-content:space-between;align-items:center;margin-top:14px}
.nav .btn{background:var(--blue)}
.qopts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.qopt{background:#fff;border:2px solid #eee3d3;border-radius:14px;padding:14px 8px;
  font-size:1rem;font-weight:700;color:var(--ink);cursor:pointer}
.qopt.correct{background:var(--good);border-color:var(--good);color:#fff}
.qopt.wrong{background:var(--bad);border-color:var(--bad);color:#fff}
.qopt.dim{opacity:.55}
.scorebar{display:flex;justify-content:center;gap:14px;font-weight:700;margin:6px 0;color:#7a5b39}
.progress{height:8px;background:#eee3d3;border-radius:999px;overflow:hidden;margin:8px 0}
.progress > div{height:100%;background:linear-gradient(90deg,var(--pine),var(--pine2));width:0;transition:.3s}
.listgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.listitem{background:#fff;border:2px solid #eee3d3;border-radius:16px;padding:10px;
  text-align:center;cursor:pointer;transition:.12s}
.listitem:active{transform:scale(.97)}
.listitem img{width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:10px;background:#f0eadf}
.listitem .li-et{font-weight:800;font-size:.95rem;color:#5b4020;margin-top:6px}
.listitem .li-ru{font-size:.8rem;color:var(--muted)}
.footer{font-size:.72rem;color:var(--muted);text-align:center;margin-top:18px;line-height:1.5}
</style>
</head>
<body>
<div class="wrap">
  <h1>🌲 Puidutöö sõnad</h1>
  <h2>Словарь технологии (работы по дереву) — эстонский ⇄ русский</h2>

  <div class="modes" id="modes">
    <div class="mode active" data-mode="learn">📖 Учи</div>
    <div class="mode" data-mode="review">🔁 Повтори</div>
    <div class="mode" data-mode="quiz">🎯 Тест</div>
    <div class="mode" data-mode="list">📚 Список</div>
  </div>

  <div class="chips" id="chips"></div>
  <div class="progress" id="progwrap"><div id="prog"></div></div>

  <div id="container"></div>

  <div class="nav" id="nav">
    <button class="btn" id="prev">← Назад</button>
    <button class="btn" id="shuffle">🔀 Перемешать</button>
    <button class="btn" id="next">Дальше →</button>
  </div>

  <div class="footer">
    Фотографии — Wikimedia Commons (свободные лицензии CC/Public Domain).<br>
    Сделано с ❤️ для Полины.
  </div>
</div>

<script>
const CATS = __CATS__;
const CARDS = __CARDS__;

let mode = "learn";
let cat = "all";
let order = CARDS.map((c,i)=>i);
let pos = 0;
// per-card quiz answer state across the session: id -> "right" | "wrong"
let answers = {};
// stored quiz options per card so re-visiting shows the same locked set
let quizOpts = {};

function filtered(){
  return cat === "all" ? order : order.filter(i => CARDS[i].cat === cat);
}
function cardIdx(){
  const f = filtered();
  return f.length ? f[pos % f.length] : -1;
}
function speak(et){
  try{
    if(!("speechSynthesis" in window)) return;
    const u = new SpeechSynthesisUtterance(et);
    u.lang = "et-EE"; u.rate = 0.85;
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
  }catch(e){}
}
function setMode(m, keepPos){
  mode = m;
  if(!keepPos) pos = 0;
  answers = {}; quizOpts = {};
  document.querySelectorAll(".mode").forEach(el => el.classList.toggle("active", el.dataset.mode===m));
  render();
}
function renderChips(){
  const ch = document.getElementById("chips");
  let html = '<div class="chip active" data-cat="all">Все</div>';
  for(const c of CATS){ html += `<div class="chip" data-cat="${c.id}">${c.icon} ${c.titleRu}</div>`; }
  ch.innerHTML = html;
  ch.querySelectorAll(".chip").forEach(el => el.onclick = () => {
    cat = el.dataset.cat; pos = 0;
    ch.querySelectorAll(".chip").forEach(x=>x.classList.remove("active"));
    el.classList.add("active");
    render();
  });
}
function render(){
  const container = document.getElementById("container");
  const prog = document.getElementById("prog");
  const nav = document.getElementById("nav");

  if(mode === "list"){
    prog.style.width = "100%";
    nav.style.display = "none";
    buildList(container);
    return;
  }
  nav.style.display = "flex";
  const f = filtered();
  prog.style.width = (f.length ? ((pos % f.length)+1)/f.length*100 : 0) + "%";

  const idx = cardIdx();
  if(idx === -1){ container.innerHTML = "<p>Нет карточек</p>"; return; }
  const C = CARDS[idx];

  container.innerHTML = `
    <div class="card">
      <div class="imgbox">
        <img src="data:image/jpeg;base64,${C.b64}" alt="">
        <div class="hint-license" ${C.license ? '' : 'hidden'}>${C.license||''}</div>
        <button class="speak" title="Послушать">🔊</button>
      </div>
      <div class="word-et">${C.et}</div>
      <div class="word-ru" id="ru">${C.ru}</div>
      <div class="desc" id="desc">${C.desc||''}</div>
      <div id="controls"></div>
    </div>
    <div class="scorebar" id="score"></div>`;
  container.querySelector(".speak").onclick = () => speak(C.et);

  const ru = container.querySelector("#ru");
  const desc = container.querySelector("#desc");
  const controls = container.querySelector("#controls");
  const scorebar = container.querySelector("#score");

  if(mode === "learn"){
    ru.classList.remove("reveal");
    desc.classList.remove("reveal");
    controls.innerHTML = "";
    scorebar.innerHTML = "";
  } else if(mode === "review"){
    ru.classList.add("reveal");
    desc.classList.add("reveal");
    controls.innerHTML = '<button class="btn" id="showBtn">Показать перевод 👀</button>';
    document.getElementById("showBtn").onclick = () => {
      ru.classList.remove("reveal");
      desc.classList.remove("reveal");
    };
    scorebar.innerHTML = "";
  } else if(mode === "quiz"){
    desc.classList.add("reveal");
    buildQuiz(C, ru, controls, scorebar);
  }
}
function sample(arr,n){
  const a=[...arr]; for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}
  return a.slice(0,n);
}
function buildQuiz(C, ru, controls, scorebar){
  setScore(scorebar);
  ru.classList.add("reveal");

  if(answers[C.id]){
    // already answered -> show locked result, no double count
    showQuizOptions(controls, C, quizOpts[C.id], answers[C.id]);
    return;
  }

  const pool = CARDS.filter(c => c.id !== C.id);
  const sameCat = pool.filter(c => c.cat === C.cat);
  const others = pool.filter(c => c.cat !== C.cat);
  let lets = sample(sameCat, Math.min(3, sameCat.length));
  if(lets.length < 3) lets = lets.concat(sample(others, 3 - lets.length));
  const opts = lets.slice(0,3).map(c => c.ru);
  opts.push(C.ru);
  opts.sort(() => Math.random() - 0.5);
  quizOpts[C.id] = opts;
  showQuizOptions(controls, C, opts, null);
}
function showQuizOptions(controls, C, opts, locked){
  controls.innerHTML = '<div class="qopts">' +
    opts.map(o => {
      let cls = "qopt";
      if(locked){ cls += " dim"; if(o === C.ru) cls += " correct"; }
      return `<div class="qopt ${cls}" data-ru="${o.replace(/"/g,'&quot;')}">${o}</div>`;
    }).join('') + '</div>';
  controls.querySelectorAll(".qopt").forEach(el => el.onclick = () => {
    if(answers[C.id]) return; // locked
    const isRight = el.dataset.ru === C.ru;
    answers[C.id] = isRight ? "right" : "wrong";
    controls.querySelectorAll(".qopt").forEach(x=>{
      x.classList.add("dim");
      if(x.dataset.ru === C.ru) x.classList.add("correct");
    });
    if(!isRight) el.classList.add("wrong");
    setScore(document.getElementById("score"));
  });
}
function setScore(scorebar){
  if(!scorebar) return;
  let r=0,w=0;
  for(const id in answers){ if(answers[id]==="right") r++; else if(answers[id]==="wrong") w++; }
  scorebar.innerHTML = `<span>✅ ${r}</span><span>❌ ${w}</span>`;
}
function buildList(container){
  const f = filtered();
  let html = '<div class="listgrid">';
  for(const i of f){
    const C = CARDS[i];
    html += `<div class="listitem" data-card="${i}">
        <img src="data:image/jpeg;base64,${C.b64}" alt="">
        <div class="li-et">${C.et}</div><div class="li-ru">${C.ru}</div></div>`;
  }
  html += '</div>';
  container.innerHTML = html;
  container.querySelectorAll(".listitem").forEach(el => el.onclick = () => {
    const ci = parseInt(el.dataset.card, 10);
    const f2 = filtered();
    const rel = f2.indexOf(ci);
    if(rel >= 0){ pos = rel; setMode("learn", true); }
  });
}
document.getElementById("modes").querySelectorAll(".mode").forEach(el =>
  el.onclick = () => setMode(el.dataset.mode));
document.getElementById("next").onclick = () => { pos++; render(); };
document.getElementById("prev").onclick = () => { pos = Math.max(0, pos-1); render(); };
document.getElementById("shuffle").onclick = () => {
  order = CARDS.map((c,i)=>i).sort(() => Math.random()-0.5);
  pos = 0; answers = {}; quizOpts = {};
  render();
};
renderChips();
render();
</script>
</body>
</html>
"""

html = HTML.replace("__CATS__", cats_json).replace("__CARDS__", cards_json)
out = os.path.join(DOCS, "index.html")
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, f"{os.path.getsize(out)/1024/1024:.1f} MB")
