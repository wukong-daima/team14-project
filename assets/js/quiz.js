/* ==========================================================================
   Team14 전 주차 퀴즈 (quiz/index.html 전용)
   - 문제 출처 두 가지
     1) 주차 페이지의 <details class="quiz"><summary>문제</summary><div class="answer">정답</div></details>
        "(객관식)" + ①②③④ 보기가 있으면 객관식으로 자동 채점, 나머지는 스스로 채점
     2) assets/data/quiz/index.json 에 적힌 문제 은행 JSON (형식은 assets/data/quiz/README.md)
   - 기록: localStorage "t14.quiz" = { 문제id: { r: "ok"|"meh"|"no", n: 푼 횟수, t: 시각 } }
   - fetch 를 쓰므로 file:// 로 열면 안 되고, 로컬 서버(python -m http.server)나 GitHub Pages 에서 엽니다.
   ========================================================================== */
(function () {
  "use strict";

  var KEY = "t14.quiz";
  var CIRCLED = "①②③④⑤⑥";
  var pool = [];            // 모든 문제
  var session = null;       // { list, i, results }
  var picked = {};          // 선택한 주차 id → true

  // ----- 기록
  function loadLog() { try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { return {}; } }
  function saveLog(log) { try { localStorage.setItem(KEY, JSON.stringify(log)); } catch (e) {} }
  var log = loadLog();
  function record(q, r) {
    var prev = log[q.id] || { n: 0 };
    log[q.id] = { r: r, n: prev.n + 1, t: Date.now() };
    saveLog(log);
  }

  // ----- 유틸
  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function hash(s) { // 문제 문장으로 만든 짧은 id (문장이 같으면 같은 id)
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return (h >>> 0).toString(36);
  }
  function norm(s) { return s.replace(/\s+/g, " ").trim(); }
  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function weekInfo(id) {
    return (window.WEEKS || []).find(function (w) { return w.id === id; }) || { id: id, num: "?", title: id };
  }

  // ----- 주차 페이지에서 문제 뽑기
  function parseWeekPage(week, html) {
    var doc = new DOMParser().parseFromString(html, "text/html");
    var out = [];
    doc.querySelectorAll("details.quiz").forEach(function (d) {
      var s = d.querySelector("summary"), a = d.querySelector(".answer");
      if (!s || !a) return;
      var text = norm(s.textContent).replace(/^Q\d+\.\s*/, "");
      if (!text || text === "문제") return;                       // 템플릿 자리표시
      var q = { id: week.id + "-" + hash(text), week: week.id, src: "page", type: "self",
                q: text, answerHtml: a.innerHTML };
      var mc = parseChoices(text, a.textContent);
      if (mc) { q.type = "mc"; q.q = mc.stem; q.options = mc.options; q.answer = mc.answer; }
      out.push(q);
    });
    return out;
  }
  // "(객관식) 질문 ① 보기 ② 보기 …" + 정답 첫머리 "②." → 객관식. 실패하면 null (스스로 채점으로 남음)
  function parseChoices(text, answerText) {
    if (!/객관식/.test(text)) return null;
    var parts = text.split(new RegExp("([" + CIRCLED + "])"));
    if (parts.length < 5) return null;
    var stem = parts[0].replace(/\((객관식)\)\s*/, "").trim(), options = [];
    for (var i = 1; i < parts.length; i += 2) options.push(parts[i + 1].trim());
    var m = norm(answerText).match(new RegExp("^(?:정답\\s*[:：]?\\s*)?([" + CIRCLED + "])"));
    if (!m) return null;
    var idx = CIRCLED.indexOf(m[1]);
    if (idx < 0 || idx >= options.length) return null;
    return { stem: stem, options: options, answer: idx };
  }

  // ----- 문제 은행 JSON
  function fromBank(bank) {
    var week = bank.week;
    return (bank.questions || []).map(function (b) {
      var q = { id: b.id || (week + "-" + hash(norm(b.q))), week: week, src: bank.source || "bank",
                q: norm(b.q), explanation: b.explanation || "", concept: b.concept || "", refs: b.refs || [],
                basic: !!b.basic, verified: b.verified || null };
      if (b.type === "mc" && Array.isArray(b.options) && typeof b.answer === "number") {
        q.type = "mc"; q.options = b.options; q.answer = b.answer;
      } else if (b.type === "num" && typeof b.answer === "number") {
        q.type = "num"; q.answer = b.answer; q.tol = typeof b.tol === "number" ? b.tol : Math.abs(b.answer) * 0.01;
        q.unit = b.unit || "";
      } else {
        q.type = "self"; q.answerText = String(b.answer || "");
      }
      return q;
    });
  }

  function loadAll() {
    var root = "../";
    var weeks = (window.WEEKS || []).filter(function (w) { return w.status === "done"; });
    var jobs = weeks.map(function (w) {
      return fetch(root + "weeks/" + w.id + ".html").then(function (r) { return r.ok ? r.text() : ""; })
        .then(function (html) { return html ? parseWeekPage(w, html) : []; })
        .catch(function () { return []; });
    });
    jobs.push(fetch(root + "assets/data/quiz/index.json").then(function (r) { return r.ok ? r.json() : { banks: [] }; })
      .then(function (idx) {
        return Promise.all((idx.banks || []).map(function (f) {
          return fetch(root + "assets/data/quiz/" + f).then(function (r) { return r.ok ? r.json() : null; })
            .then(function (b) { return b ? fromBank(b) : []; }).catch(function () { return []; });
        }));
      })
      .then(function (lists) { return [].concat.apply([], lists); })
      .catch(function () { return []; }));
    return Promise.all(jobs).then(function (lists) {
      var seen = {}, all = [];
      [].concat.apply([], lists).forEach(function (q) { if (!seen[q.id]) { seen[q.id] = 1; all.push(q); } });
      all.sort(function (a, b) { return weekInfo(a.week).num - weekInfo(b.week).num; });
      return all;
    });
  }

  // ----- 통계 / 범위
  function renderStats() {
    var done = 0, ok = 0, wrong = 0;
    pool.forEach(function (q) {
      var l = log[q.id]; if (!l) return;
      done++; if (l.r === "ok") ok++; else wrong++;
    });
    $("stats").innerHTML =
      stat(pool.length, "전체 문제") + stat(done, "푼 문제") +
      stat(done ? Math.round(ok / done * 100) + "%" : "-", "정답률 (마지막 시도)") + stat(wrong, "오답 노트");
    function stat(v, l) { return '<div class="stat"><b>' + v + '</b><span>' + l + '</span></div>'; }
  }

  function weeksInPool() {
    var ids = [];
    pool.forEach(function (q) { if (ids.indexOf(q.week) < 0) ids.push(q.week); });
    return ids;
  }

  function renderChips() {
    var ids = weeksInPool();
    var el = $("week-chips");
    el.innerHTML = ids.map(function (id) {
      var w = weekInfo(id), n = pool.filter(function (q) { return q.week === id; }).length;
      return '<button type="button" class="chip" data-id="' + id + '" aria-pressed="' + (picked[id] ? "true" : "false") + '">' +
        w.num + '주차<span class="n">' + n + '</span></button>';
    }).join("") +
      '<button type="button" class="chip" data-id="*" aria-pressed="false">전체 선택</button>';
    el.querySelectorAll(".chip").forEach(function (b) {
      b.addEventListener("click", function () {
        var id = b.getAttribute("data-id");
        if (id === "*") {
          var all = ids.every(function (x) { return picked[x]; });
          ids.forEach(function (x) { picked[x] = !all; });
        } else picked[id] = !picked[id];
        renderChips(); renderPoolInfo();
      });
    });
  }

  function filtered() {
    var scope = $("scope").value;
    return pool.filter(function (q) {
      if (!picked[q.week]) return false;
      var l = log[q.id];
      if (scope === "new") return !l;
      if (scope === "wrong") return l && l.r !== "ok";
      return true;
    });
  }
  function renderPoolInfo() {
    var n = filtered().length;
    $("pool-info").textContent = n ? "조건에 맞는 문제 " + n + "개" : "조건에 맞는 문제가 없습니다";
    $("start").disabled = !n;
  }

  // ----- 풀기
  function start(list) {
    if (!list.length) return;
    if ($("shuffle").value === "1") shuffle(list);
    var c = +$("count").value;
    if (c) list = list.slice(0, c);
    session = { list: list, i: 0, results: [] };
    $("setup").hidden = true; $("result").hidden = true; $("play").hidden = false;
    renderQuestion();
  }

  function renderQuestion() {
    var q = session.list[session.i], w = weekInfo(q.week), n = session.list.length;
    var typeLabel = { mc: "객관식 · 자동 채점", num: "계산 · 자동 채점", self: "서술형 · 스스로 채점" }[q.type];
    var body = "";
    if (q.type === "mc") {
      body = '<div class="options">' + q.options.map(function (o, i) {
        return '<button type="button" class="opt" data-i="' + i + '">' + CIRCLED[i] + " " + esc(o) + '</button>';
      }).join("") + '</div>';
    } else if (q.type === "num") {
      body = '<label class="small muted" for="num-in">답 (숫자' + (q.unit ? ", 단위 " + esc(q.unit) : "") + ')</label>' +
        '<div class="row"><input type="text" id="num-in" inputmode="decimal" autocomplete="off" style="max-width:220px">' +
        '<button class="btn primary" type="button" id="num-check">채점</button></div>';
    } else {
      body = '<label class="small muted" for="my-ans">내 답 (적지 않아도 됩니다. 저장하지 않습니다)</label>' +
        '<textarea id="my-ans"></textarea>' +
        '<div class="row" style="margin-top:10px"><button class="btn primary" type="button" id="reveal">정답 보기</button></div>';
    }
    $("play").innerHTML =
      '<div class="progress" aria-hidden="true"><i style="width:' + (session.i / n * 100) + '%"></i></div>' +
      '<div class="qmeta"><span class="pill accent">' + w.num + '주차</span><span>' + esc(w.title) + '</span>' +
        '<span class="pill">' + typeLabel + '</span>' +
        (q.src === "agent" ? '<span class="pill compare" title="출제 에이전트가 만들고 풀이 시험·검증을 통과한 문제">AI 출제 · 검증</span>' : '') +
        (q.basic ? '<span class="pill" title="강의를 안 들은 약한 모델도 맞힌 기초 문제">기초</span>' : '') +
        '<span class="spacer"></span><span class="mono">' + (session.i + 1) + ' / ' + n + '</span></div>' +
      '<div class="qtext">' + esc(q.q) + '</div>' + body +
      '<div id="fb" aria-live="polite"></div>' +
      '<div class="actions"><button class="btn small" type="button" id="quit">그만하기</button>' +
        '<button class="btn" type="button" id="next" hidden>' + (session.i + 1 < n ? "다음 문제 →" : "결과 보기") + '</button></div>';

    $("quit").addEventListener("click", finish);
    $("next").addEventListener("click", next);
    if (q.type === "mc") {
      $("play").querySelectorAll(".opt").forEach(function (b) {
        b.addEventListener("click", function () { gradeMc(q, +b.getAttribute("data-i")); });
      });
    } else if (q.type === "num") {
      var go = function () { gradeNum(q, $("num-in").value); };
      $("num-check").addEventListener("click", go);
      $("num-in").addEventListener("keydown", function (e) { if (e.key === "Enter") go(); });
      $("num-in").focus();
    } else {
      $("reveal").addEventListener("click", function () { revealSelf(q); });
    }
  }

  function answerBlock(q) {
    if (q.answerHtml) return '<div class="answer-body">' + q.answerHtml + '</div>';  // 우리 주차 페이지의 HTML
    var t = q.type === "self" ? q.answerText : q.explanation;
    var refs = q.refs && q.refs.length ? '<div class="small muted">근거: ' + esc(q.refs.join(", ")) + '</div>' : "";
    return (t ? '<div class="answer-body">' + esc(t) + '</div>' : "") + refs;
  }

  function verdict(r) {
    var map = { ok: ["ok", "정답입니다"], no: ["no", "틀렸습니다"], meh: ["meh", "애매함으로 표시했습니다"] };
    return '<div class="verdict ' + map[r][0] + '">' + map[r][1] + '</div>';
  }

  function gradeMc(q, i) {
    var r = i === q.answer ? "ok" : "no";
    $("play").querySelectorAll(".opt").forEach(function (b, j) {
      b.disabled = true;
      if (j === q.answer) b.classList.add("correct");
      else if (j === i) b.classList.add("wrong");
    });
    done(q, r, verdict(r) + (r === "no" ? '<div>정답: ' + CIRCLED[q.answer] + '</div>' : "") + answerBlock(q));
  }

  function gradeNum(q, raw) {
    var v = parseFloat(String(raw).replace(/,/g, ""));
    if (isNaN(v)) { $("fb").innerHTML = '<div class="feedback">숫자를 입력해 주세요.</div>'; return; }
    $("num-in").disabled = true; $("num-check").disabled = true;
    var r = Math.abs(v - q.answer) <= q.tol ? "ok" : "no";
    done(q, r, verdict(r) + '<div>정답: <span class="mono">' + q.answer + (q.unit ? " " + esc(q.unit) : "") +
      '</span> (허용 오차 ±' + q.tol + ')</div>' + answerBlock(q));
  }

  function revealSelf(q) {
    $("reveal").disabled = true;
    $("fb").innerHTML = '<div class="feedback">' + answerBlock(q) +
      '<div class="self-grade"><span class="small muted">내 답은?</span>' +
      '<button class="btn small" type="button" data-r="ok">맞았다</button>' +
      '<button class="btn small" type="button" data-r="meh">애매하다</button>' +
      '<button class="btn small" type="button" data-r="no">몰랐다</button></div></div>';
    $("fb").querySelectorAll("[data-r]").forEach(function (b) {
      b.addEventListener("click", function () {
        var r = b.getAttribute("data-r");
        $("fb").querySelectorAll("[data-r]").forEach(function (x) { x.disabled = true; });
        record(q, r); session.results.push({ q: q, r: r });
        $("fb").querySelector(".feedback").insertAdjacentHTML("afterbegin", verdict(r));
        $("next").hidden = false; $("next").focus();
      });
    });
  }

  function done(q, r, html) {
    record(q, r); session.results.push({ q: q, r: r });
    $("fb").innerHTML = '<div class="feedback">' + html + '</div>';
    $("next").hidden = false; $("next").focus();
  }

  function next() {
    session.i++;
    if (session.i < session.list.length) renderQuestion(); else finish();
  }

  function finish() {
    var res = session ? session.results : [];
    $("play").hidden = true; $("result").hidden = false;
    var ok = res.filter(function (x) { return x.r === "ok"; }).length;
    var byWeek = {};
    res.forEach(function (x) {
      var b = byWeek[x.q.week] || (byWeek[x.q.week] = { ok: 0, n: 0 });
      b.n++; if (x.r === "ok") b.ok++;
    });
    var rows = Object.keys(byWeek).sort(function (a, b) { return weekInfo(a).num - weekInfo(b).num; }).map(function (id) {
      var b = byWeek[id], w = weekInfo(id);
      return '<div class="result-week"><span>' + w.num + '주차 · ' + esc(w.title) + '</span><span class="mono">' + b.ok + ' / ' + b.n + '</span>' +
        '<div class="bar"><i style="width:' + (b.ok / b.n * 100) + '%"></i></div></div>';
    }).join("");
    var missed = res.length - ok;
    $("result").innerHTML = '<h2 style="margin-top:0">결과</h2>' +
      (res.length ? '<p><b class="mono" style="font-size:1.6rem">' + ok + ' / ' + res.length + '</b> 맞혔습니다.' +
        (missed ? ' 틀렸거나 애매한 ' + missed + '문제는 오답 노트에 들어갔습니다.' : '') + '</p>' + rows
        : '<p class="muted">푼 문제가 없습니다.</p>') +
      '<div class="actions">' + (missed ? '<button class="btn" type="button" id="again-wrong">방금 틀린 문제 다시</button>' : '') +
      '<button class="btn primary" type="button" id="again">범위 다시 고르기</button></div>';
    if (missed) $("again-wrong").addEventListener("click", function () {
      start(res.filter(function (x) { return x.r !== "ok"; }).map(function (x) { return x.q; }));
    });
    $("again").addEventListener("click", backToSetup);
    session = null;
    renderStats(); renderPoolInfo(); renderNotes();
  }

  function backToSetup() {
    $("result").hidden = true; $("play").hidden = true; $("setup").hidden = false;
  }

  // ----- 오답 노트
  function renderNotes() {
    var list = pool.filter(function (q) { var l = log[q.id]; return l && l.r !== "ok"; });
    $("retry-wrong").disabled = !list.length;
    if (!list.length) { $("notes").innerHTML = '<p class="empty">오답 노트가 비어 있습니다.</p>'; return; }
    $("notes").innerHTML = list.map(function (q) {
      var w = weekInfo(q.week), l = log[q.id];
      var choices = q.type === "mc" ? '<ol style="list-style:none;padding:0">' + q.options.map(function (o, i) {
        return '<li>' + CIRCLED[i] + ' ' + esc(o) + (i === q.answer ? ' <b>← 정답</b>' : '') + '</li>';
      }).join("") + '</ol>' : "";
      var num = q.type === "num" ? '<p>정답: <span class="mono">' + q.answer + (q.unit ? " " + esc(q.unit) : "") + '</span></p>' : "";
      return '<details class="note"><summary><div class="qmeta"><span class="pill accent">' + w.num + '주차</span>' +
        '<span class="pill ' + (l.r === "meh" ? "todo" : "") + '">' + (l.r === "meh" ? "애매" : "틀림") + '</span>' +
        '<span>' + l.n + '번 풂</span></div>' + esc(q.q) + '</summary>' + choices + num +
        '<div class="feedback">' + answerBlock(q) + '</div></details>';
    }).join("");
  }

  function selectTab(which) {
    var play = which === "play";
    $("tab-play").setAttribute("aria-selected", play ? "true" : "false");
    $("tab-notes").setAttribute("aria-selected", play ? "false" : "true");
    $("panel-play").hidden = !play; $("panel-notes").hidden = play;
  }

  // ----- 시작
  document.addEventListener("DOMContentLoaded", function () {
    $("tab-play").addEventListener("click", function () { selectTab("play"); });
    $("tab-notes").addEventListener("click", function () { renderNotes(); selectTab("notes"); });
    $("scope").addEventListener("change", renderPoolInfo);
    $("start").addEventListener("click", function () { start(filtered()); });
    $("retry-wrong").addEventListener("click", function () {
      var list = pool.filter(function (q) { var l = log[q.id]; return l && l.r !== "ok"; });
      selectTab("play"); start(list);
    });
    $("reset").addEventListener("click", function () {
      if (!confirm("퀴즈 기록을 모두 지울까요? 되돌릴 수 없습니다.")) return;
      log = {}; saveLog(log); renderStats(); renderPoolInfo(); renderNotes();
    });

    if (location.protocol === "file:") {
      $("load-status").textContent = "파일로 직접 열면 문제를 불러올 수 없습니다. 저장소 폴더에서 python -m http.server 로 띄운 뒤 열어 주세요.";
      return;
    }
    loadAll().then(function (all) {
      pool = all;
      var want = (location.search.match(/[?&]week=(week\d+)/) || [])[1];
      weeksInPool().forEach(function (id) { picked[id] = want ? id === want : true; });
      renderStats(); renderChips(); renderPoolInfo(); renderNotes();
      var types = { mc: 0, num: 0, self: 0 };
      pool.forEach(function (q) { types[q.type]++; });
      $("load-status").textContent = pool.length
        ? "문제 " + pool.length + "개 (객관식 " + types.mc + " · 계산 " + types.num + " · 서술형 " + types.self + ")"
        : "불러온 문제가 없습니다.";
    });
  });
})();
