// 「困りごとから探す」の自己チェック。
// チップで状況を選ぶと data-tags が重なるカードと行だけを表示する。選択は localStorage と URL の ?s= に残す。
// サーバーには何も送らない。
(function () {
  var isEnglish = document.documentElement.lang === "en";
  var STORE = "ctzc_situations_v1";
  var chips = Array.prototype.slice.call(document.querySelectorAll("[data-sit]"));
  var targets = Array.prototype.slice.call(document.querySelectorAll("[data-tags]"));
  var count = document.getElementById("sit-count");
  var clearBtn = document.getElementById("sit-clear");
  var printBtn = document.getElementById("sit-print");
  var linkBtn = document.getElementById("sit-link");
  var linkNote = document.getElementById("sit-link-note");
  var selected = {};

  function fromQuery() {
    var m = /[?&]s=([^&#]*)/.exec(location.search);
    if (!m) return null;
    var out = {};
    decodeURIComponent(m[1]).split(",").forEach(function (k) { if (k) out[k] = true; });
    return out;
  }
  function load() {
    var q = fromQuery();
    if (q) { selected = q; return; }
    try { selected = JSON.parse(localStorage.getItem(STORE) || "{}"); } catch (e) { selected = {}; }
  }
  function save() {
    try { localStorage.setItem(STORE, JSON.stringify(selected)); } catch (e) { /* 保存できなくても動く */ }
  }
  function keys() { return Object.keys(selected).filter(function (k) { return selected[k]; }); }
  function apply() {
    var on = keys();
    chips.forEach(function (c) {
      var isOn = !!selected[c.getAttribute("data-sit")];
      c.classList.toggle("on", isOn);
      c.setAttribute("aria-pressed", isOn ? "true" : "false");
    });
    var shown = 0;
    targets.forEach(function (el) {
      var tags = (el.getAttribute("data-tags") || "").split(/\s+/);
      var hit = on.length === 0 || tags.some(function (t) { return selected[t]; });
      el.hidden = !hit;
      if (hit) shown += 1;
    });
    // 見出しだけ残って中身がない節を隠す
    Array.prototype.slice.call(document.querySelectorAll("[data-section]")).forEach(function (sec) {
      var any = Array.prototype.slice.call(sec.querySelectorAll("[data-tags]")).some(function (el) { return !el.hidden; });
      sec.hidden = !any;
    });
    if (count) {
      count.textContent = on.length === 0
        ? (isEnglish
          ? "Showing all information. Choose one or more situations above to narrow the list."
          : "すべて表示しています。上のボタンで状況を選ぶと、該当するものだけになります。")
        : (isEnglish
          ? on.length + " situation(s) selected. Showing " + shown + " matching item(s)."
          : on.length + "件の状況を選択中。該当 " + shown + " 件を表示しています。");
    }
    if (clearBtn) clearBtn.hidden = on.length === 0;
    if (linkBtn) linkBtn.hidden = on.length === 0;
    if (linkNote) linkNote.textContent = "";
  }
  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      var k = c.getAttribute("data-sit");
      selected[k] = !selected[k];
      save();
      apply();
    });
  });
  if (clearBtn) clearBtn.addEventListener("click", function () { selected = {}; save(); apply(); });
  if (printBtn) printBtn.addEventListener("click", function () { window.print(); });
  if (linkBtn) linkBtn.addEventListener("click", function () {
    var url = location.origin + location.pathname + "?s=" + encodeURIComponent(keys().join(","));
    function done(msg) { if (linkNote) linkNote.textContent = msg; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () {
        done(isEnglish
          ? "Link copied. Save or send it to reopen the same selection later."
          : "リンクをコピーしました。LINE などで自分に送っておくと、あとで同じ表示を開けます。");
      },
        function () { done(url); });
    } else {
      done(url);
    }
  });
  load();
  apply();
})();
