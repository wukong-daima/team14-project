/* ==========================================================================
   Team14 공통 스크립트
   - 전공/중학생 모드 토글 (localStorage에 저장, 실패해도 동작)
   - 다크/라이트 테마 토글
   - 주차 prev/next 내비게이션 (weeks.js 매니페스트 사용)
   - 방문한 주차 표시
   - 모델 비교 패널 / 퀴즈 공통 동작
   주차 페이지에는 아래 HTML 훅만 두면 됩니다:
     <body data-week="week02">  ...  <div id="week-nav"></div>
   ========================================================================== */
(function () {
  "use strict";

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  // ----- 경로 유틸: index.html과 weeks/*.html 둘 다에서 동작하도록 상대 경로 계산
  var inWeeks = /\/weeks\//.test(location.pathname);
  var root = inWeeks ? "../" : "./";

  // ----- 전공/중학생 모드
  function applyLevel(level) {
    document.body.classList.toggle("level-easy", level === "easy");
    document.querySelectorAll(".level-toggle").forEach(function (b) {
      b.textContent = level === "easy" ? "🎓 전공 모드로" : "🧒 중학생 수준으로 이해하기";
      b.setAttribute("aria-pressed", level === "easy" ? "true" : "false");
    });
  }
  function toggleLevel() {
    var next = document.body.classList.contains("level-easy") ? "pro" : "easy";
    store.set("t14.level", next);
    applyLevel(next);
  }

  // ----- 테마
  function applyTheme(t) {
    if (t) document.documentElement.setAttribute("data-theme", t);
    else document.documentElement.removeAttribute("data-theme");
  }
  function toggleTheme() {
    var cur = document.documentElement.getAttribute("data-theme");
    var dark = cur ? cur === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    var next = dark ? "light" : "dark";
    store.set("t14.theme", next);
    applyTheme(next);
  }

  // ----- 헤더 렌더
  function renderHeader() {
    var h = document.querySelector(".site-header .wrap");
    if (!h) return;
    h.innerHTML =
      '<a class="brand" href="' + root + 'index.html"><span class="dot"></span>Team14 · 최신딥러닝 랩</a>' +
      '<nav class="nav-links" aria-label="주요 메뉴">' +
        '<a href="' + root + 'index.html#weeks">주차별 공부</a>' +
        '<a href="' + root + 'index.html#concept">프로젝트 소개</a>' +
        '<a href="' + root + 'slides/index.html">발표 모드</a>' +
      '</nav>' +
      '<span class="spacer"></span>' +
      '<button class="btn small level-toggle" type="button"></button>' +
      '<button class="btn small theme-toggle" type="button" aria-label="테마 전환">◐</button>';
    h.querySelector(".level-toggle").addEventListener("click", toggleLevel);
    h.querySelector(".theme-toggle").addEventListener("click", toggleTheme);
    var here = location.pathname.replace(/\/index\.html$/, "/");
    h.querySelectorAll(".nav-links a").forEach(function (a) {
      if (a.pathname.replace(/\/index\.html$/, "/") === here) a.setAttribute("aria-current", "page");
    });
  }

  // ----- 주차 내비게이션
  function renderWeekNav() {
    var el = document.getElementById("week-nav");
    var id = document.body.getAttribute("data-week");
    if (!el || !id || !window.WEEKS) return;
    var i = window.WEEKS.findIndex(function (w) { return w.id === id; });
    var prev = window.WEEKS[i - 1], next = window.WEEKS[i + 1];
    el.className = "week-nav";
    el.innerHTML =
      (prev ? '<a class="btn" href="' + prev.id + '.html">← ' + prev.num + '주차 · ' + prev.title + '</a>' : '<span></span>') +
      '<a class="btn" href="' + root + 'index.html#weeks">주차 목록</a>' +
      (next ? '<a class="btn primary" href="' + next.id + '.html">' + next.num + '주차 · ' + next.title + ' →</a>' : '<span></span>');
    // 방문 기록
    var seen = {};
    try { seen = JSON.parse(store.get("t14.seen") || "{}"); } catch (e) {}
    seen[id] = Date.now();
    store.set("t14.seen", JSON.stringify(seen));
  }

  // ----- 목차 자동 생성 (<nav class="toc"> 가 있으면 h2[id] 로 채움)
  function renderToc() {
    var toc = document.querySelector("nav.toc");
    if (!toc) return;
    var items = document.querySelectorAll("main h2[id]");
    if (!items.length) return;
    toc.innerHTML = '<div class="small muted" style="margin-bottom:6px">이 페이지</div>' +
      Array.prototype.map.call(items, function (h) {
        return '<a href="#' + h.id + '">' + h.textContent.replace(/^\d+\.\s*/, "") + '</a>';
      }).join("");
  }

  // ----- 모델 비교 패널: 모든 패널에 범례 삽입
  function decorateCompare() {
    document.querySelectorAll("details.compare .body").forEach(function (b) {
      if (b.querySelector(".legend")) return;
      var l = document.createElement("div");
      l.className = "legend";
      l.innerHTML = '범례: <span class="badge src">출처</span> 공개 문서로 확인됨 · ' +
        '<span class="badge check">확인 필요</span> 2차 자료/추정, 발표 전 재확인 · ' +
        '<span class="badge private">비공개</span> 해당 업체가 공개하지 않은 정보';
      b.insertBefore(l, b.firstChild);
    });
  }

  // ----- 초기화
  // 파비콘 (별도 파일 없이 SVG 데이터 URI)
  (function () {
    var l = document.createElement("link"); l.rel = "icon";
    l.href = "data:image/svg+xml," + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="16" cy="16" r="14" fill="#2d5bff"/><text x="16" y="21" font-size="14" font-family="sans-serif" font-weight="700" text-anchor="middle" fill="#fff">14</text></svg>');
    document.head.appendChild(l);
  })();

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(store.get("t14.theme"));
    renderHeader();
    applyLevel(store.get("t14.level") || "pro");
    renderWeekNav();
    renderToc();
    decorateCompare();
    // URL에 ?easy 가 있으면 쉬운 모드로 (발표 중 링크로 바로 전환하기 위함)
    if (/[?&]easy\b/.test(location.search)) { store.set("t14.level", "easy"); applyLevel("easy"); }
  });

  // 주차 페이지에서 쓸 작은 유틸
  window.T14 = {
    fmt: function (n, d) { return Number(n).toLocaleString("ko-KR", { maximumFractionDigits: d == null ? 1 : d }); },
    bytes: function (b) {
      var u = ["B", "KB", "MB", "GB", "TB"], i = 0;
      while (b >= 1024 && i < u.length - 1) { b /= 1024; i++; }
      return (i ? b.toFixed(b >= 100 ? 0 : 1) : b) + " " + u[i];
    },
    rand: function (seed) { // 결정적 난수 (발표 때 같은 결과를 재현하기 위함)
      var s = seed >>> 0 || 1;
      return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
    }
  };
})();
