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
    img.thumbnail((1024, 1024))
    buf = BytesIO()
    img.save(buf, "JPEG", quality=85, optimize=True)
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
  width:min(100%,460px);margin:0 auto;text-align:center}
.card img{width:100%;height:auto;display:block;border-radius:16px}
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
.dirtoggle{display:flex;justify-content:center;gap:8px;margin:0 0 12px;flex-wrap:wrap}
.dirtoggle-btn{background:#fff;border:2px solid #eee3d3;border-radius:999px;padding:7px 16px;
  font-weight:700;font-size:.9rem;color:#b98a5a;cursor:pointer;transition:.15s}
.dirtoggle-btn.active{border-color:var(--pine2);color:var(--pine);background:#f2fbf4}
.word-question{font-size:1.9rem;font-weight:800;margin:18px 0 6px;color:#5b4020}
.quizhint{min-height:46px;display:flex;flex-direction:column;align-items:center;gap:8px}
.quizhint img{max-width:100%;max-height:320px;border-radius:12px;display:block}
.hint-license{position:static;display:inline-block;margin-top:4px}
.scorebar{display:flex;justify-content:center;gap:14px;font-weight:700;margin:6px 0;color:#7a5b39}
.progress{height:8px;background:#eee3d3;border-radius:999px;overflow:hidden;margin:8px 0}
.progress > div{height:100%;background:linear-gradient(90deg,var(--pine),var(--pine2));width:0;transition:.3s}
.listgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.listitem{background:#fff;border:2px solid #eee3d3;border-radius:16px;padding:10px;
  text-align:center;cursor:pointer;transition:.12s}
.listitem:active{transform:scale(.97)}
.listitem img{width:100%;height:auto;border-radius:10px;background:#f0eadf;display:block}
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
    Иллюстрации созданы с помощью ИИ специально для этого тренажёра.<br>
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
// quiz round state: "main" | "retry"; ids answered wrong in the last round
let quizStage = "main";
let wrongIds = [];
// quiz direction: "et-ru" (show Estonian, answer Russian) | "ru-et" (reverse)
let quizDir = "et-ru";
// quiz question ordering
let quizOrder = null;
let quizShuffled = false;

function filtered(){
  return cat === "all" ? order : order.filter(i => CARDS[i].cat === cat);
}
// the set of card indices the current quiz round asks about
function quizPool(){
  if(quizStage === "retry"){ return wrongIds; }
  if(quizOrder === null) buildQuizOrder();
  return quizOrder;
}
function buildQuizOrder(){
  const base = (cat === "all")
    ? CARDS.map((c,i)=>i)
    : CARDS.map((c,i)=>i).filter(i => CARDS[i].cat === cat);
  if(!quizShuffled){
    quizOrder = base;
  } else {
    const a = base.slice();
    for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}
    quizOrder = a;
  }
}
function cardIdx(){
  const f = filtered();
  return f.length ? f[pos % f.length] : -1;
}
// number of answered cards in the current quiz pool
function answeredCount(){
  return quizPool().filter(i => answers[CARDS[i].id]).length;
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
  answers = {}; quizOpts = {}; quizStage = "main"; wrongIds = [];
  document.querySelectorAll(".mode").forEach(el => el.classList.toggle("active", el.dataset.mode===m));
  render();
}function renderChips(){
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

  // Quiz mode: route to dedicated handler (its own nav/progress/finish logic)
  if(mode === "quiz"){
    renderQuiz(container, prog, nav);
    return;
  }

  nav.style.display = "flex";
  document.getElementById("prev").style.display = "";
  document.getElementById("next").style.display = "";
  document.getElementById("shuffle").style.display = "";
  const f = filtered();
  prog.style.width = (f.length ? ((pos % f.length)+1)/f.length*100 : 0) + "%";

  const idx = cardIdx();
  if(idx === -1){ container.innerHTML = "<p>Нет карточек</p>"; return; }
  const C = CARDS[idx];

  container.innerHTML = `
    <div class="card">
      <div class="imgbox">
        <img src="data:image/jpeg;base64,${C.b64}" alt="" width="460" height="460">
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
      document.getElementById("showBtn").style.display = "none";
    };
    scorebar.innerHTML = "";
  }
}

// Quiz: show the next unanswered card, or the result screen when done.
function renderQuiz(container, prog, nav){
  const nidx = nextQuizCard();
  if(nidx === -1){
    nav.style.display = "none";
    checkQuizDone();
    return;
  }
  const pool = quizPool();
  const answered = answeredCount();
  const total = pool.length;

  nav.style.display = "flex";
  // hide prev/next/shuffle during quiz; we auto-advance + show result at end
  document.getElementById("prev").style.display = "none";
  document.getElementById("next").style.display = "none";
  document.getElementById("shuffle").style.display = "none";

  prog.style.width = (answered / total * 100) + "%";

  const C = CARDS[nidx];
  const qword = quizDir === "ru-et" ? C.ru : C.et; // the word shown as question

  container.innerHTML = `
    <div class="dirtoggle">
      <div class="dirtoggle-btn ${quizShuffled?'':'active'}" data-shuffle="0">🔢 По порядку</div>
      <div class="dirtoggle-btn ${quizShuffled?'active':''}" data-shuffle="1">🔀 Вперемешку</div>
    </div>
    <div class="dirtoggle">
      <div class="dirtoggle-btn ${quizDir==='et-ru'?'active':''}" data-dir="et-ru">🇪🇪 → 🇷🇺</div>
      <div class="dirtoggle-btn ${quizDir==='ru-et'?'active':''}" data-dir="ru-et">🇷🇺 → 🇪🇪</div>
    </div>
    <div class="card">
      <div class="quizhint" id="hint"></div>
      <div class="word-question" id="qword">${qword}</div>
      <div id="controls"></div>
    </div>
    <div class="scorebar" id="score"></div>`;

  // ordering toggle buttons
  container.querySelectorAll(".dirtoggle-btn[data-shuffle]").forEach(el => el.onclick = () => {
    const s = el.dataset.shuffle === "1";
    if(s === quizShuffled) return;
    quizShuffled = s;
    quizOrder = null;
    // restart the quiz cleanly with the new ordering
    answers = {}; quizOpts = {}; quizStage = "main"; wrongIds = []; pos = 0;
    render();
  });

  // direction toggle buttons
  container.querySelectorAll(".dirtoggle-btn[data-dir]").forEach(el => el.onclick = () => {
    const d = el.dataset.dir;
    if(d === quizDir) return;
    quizDir = d;
    // restart the quiz cleanly in the new direction
    answers = {}; quizOpts = {}; quizStage = "main"; wrongIds = []; pos = 0;
    render();
  });

  const controls = container.querySelector("#controls");
  const scorebar = container.querySelector("#score");
  const hint = container.querySelector("#hint");

  buildQuiz(C, controls, scorebar, hint);
}
function sample(arr,n){
  const a=[...arr]; for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}
  return a.slice(0,n);
}
// return the card index to show next in quiz, or -1 if quiz is complete
function nextQuizCard(){
  const pool = quizPool();
  const unanswered = pool.filter(i => !answers[CARDS[i].id]);
  if(unanswered.length === 0) return -1; // all answered -> finish
  // prefer the first unanswered card after current pos (cyclic), else first
  const cur = pos % pool.length;
  for(let k=0; k<pool.length; k++){
    const idx = pool[(cur + k) % pool.length];
    if(!answers[CARDS[idx].id]) return idx;
  }
  return -1;
}
function buildQuiz(C, controls, scorebar, hint){
  setScore(scorebar, true);

  // hint box: image hidden by default, revealed by a button
  hint.innerHTML = '<button class="btn ghost" id="hintBtn">💡 Подсказка (картинка)</button>';
  document.getElementById("hintBtn").onclick = () => {
    hint.innerHTML = `<img src="data:image/jpeg;base64,${C.b64}" alt="" width="460" height="460">`;
  };

  if(answers[C.id]){
    // already answered -> show locked result, no double count
    showQuizOptions(controls, C, quizOpts[C.id], answers[C.id], hint);
    return;
  }

  const pool = CARDS.filter(c => c.id !== C.id);
  const sameCat = pool.filter(c => c.cat === C.cat);
  const others = pool.filter(c => c.cat !== C.cat);
  let lets = sample(sameCat, Math.min(3, sameCat.length));
  if(lets.length < 3) lets = lets.concat(sample(others, 3 - lets.length));
  // options are the "answer" side of translation
  const opts = lets.slice(0,3).map(c => quizDir === "ru-et" ? c.et : c.ru);
  const correct = quizDir === "ru-et" ? C.et : C.ru;
  opts.push(correct);
  opts.sort(() => Math.random() - 0.5);
  quizOpts[C.id] = opts;
  showQuizOptions(controls, C, opts, null, hint);
}
function showQuizOptions(controls, C, opts, locked, hint){
  const correct = quizDir === "ru-et" ? C.et : C.ru;
  controls.innerHTML = '<div class="qopts">' +
    opts.map(o => {
      let cls = "qopt";
      if(locked){ cls += " dim"; if(o === correct) cls += " correct"; }
      return `<div class="qopt ${cls}" data-val="${o.replace(/"/g,'&quot;')}">${o}</div>`;
    }).join('') + '</div>';
  controls.querySelectorAll(".qopt").forEach(el => el.onclick = () => {
    if(answers[C.id]) return; // locked
    const isRight = el.dataset.val === correct;
    answers[C.id] = isRight ? "right" : "wrong";
    controls.querySelectorAll(".qopt").forEach(x=>{
      x.classList.add("dim");
      if(x.dataset.val === correct) x.classList.add("correct");
    });
    if(!isRight) el.classList.add("wrong");
    setScore(document.getElementById("score"), true);
    // progress to the next unanswered card after a short pause
    setTimeout(() => {
      const nidx = nextQuizCard();
      if(nidx === -1) checkQuizDone();
      else { pos = quizPool().indexOf(nidx); render(); }
    }, 700);
  });
}
// called when all cards in the current quiz pool are answered
function checkQuizDone(){
  const pool = quizPool();
  const r = pool.filter(i => answers[CARDS[i].id] === "right").length;
  const w = pool.filter(i => answers[CARDS[i].id] === "wrong").length;
  wrongIds = pool.filter(i => answers[CARDS[i].id] === "wrong");
  showQuizResult(r, w);
}
function showQuizResult(r, w){
  const container = document.getElementById("container");
  const prog = document.getElementById("prog");
  const nav = document.getElementById("nav");
  const total = r + w;
  nav.style.display = "none";
  prog.style.width = "100%";
  let extra = '';
  if(quizStage === "retry"){
    if(w === 0){
      extra = '<p>💪 Все ошибки исправлены — молодец!</p>';
    } else {
      extra = `<p>Осталось ошибок: ${w}. Можно повторить ещё раз.</p>`;
    }
  } else if(w === 0){
    extra = '<p>🏆 Отлично! Все ответы верны.</p>';
  }
  const retryBtn = (w > 0)
    ? '<button class="btn" id="retryBtn">🔁 Повторить ошибки (' + w + ')</button>'
    : '';
  const againBtn = (quizStage === "retry")
    ? '<button class="btn" id="againBtn">🔄 Пройти тест ещё раз</button>'
    : '';
  container.innerHTML = `
    <div class="card" style="padding:30px 20px">
      <div style="font-size:3rem">🎉</div>
      <div class="word-et">Тест завершён!</div>
      <div class="scorebar" style="font-size:1.2rem;gap:20px">
        <span>✅ Правильно: ${r} из ${total}</span>
        <span>❌ Ошибок: ${w}</span>
      </div>
      ${extra}
      <div style="margin-top:16px">${retryBtn}${againBtn}</div>
    </div>`;
  const rb = document.getElementById("retryBtn");
  if(rb) rb.onclick = () => startRetry();
  const ab = document.getElementById("againBtn");
  if(ab) ab.onclick = () => restartQuiz();
}
function startRetry(){
  quizStage = "retry";
  // keep wrongIds, clear answers & options so they can be asked again
  answers = {}; quizOpts = {};
  pos = 0;
  render();
}
function restartQuiz(){
  quizStage = "main";
  wrongIds = [];
  answers = {}; quizOpts = {};
  pos = 0;
  render();
}
function setScore(scorebar, quiz){
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
        <img src="data:image/jpeg;base64,${C.b64}" alt="" width="200" height="200">
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
