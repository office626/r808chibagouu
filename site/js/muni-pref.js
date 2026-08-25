// 選んだ市町村をこの端末に覚えておく。
// トップの選択欄（#muni-select）で選び、ほかのページでは上部のバーから開き直せる。
// サーバーには何も送らない。localStorage が使えない環境でも、ページは普通に読める。
(function () {
  var script = document.currentScript;
  if (!script) return;

  var siteRoot = new URL("../", script.src);
  var rootPath = siteRoot.pathname;
  var isEnglish = location.pathname.indexOf(rootPath + "en/") === 0;
  var pageBase = rootPath + (isEnglish ? "en/" : "");
  var STORE = "ctzc_muni_v1";

  var T = isEnglish
    ? {
      label: "Selected municipality",
      open: "Open this municipality's page",
      change: "Change",
      choose: "Choose a municipality",
      go: function (name) { return "Open the page for " + name; }
    }
    : {
      label: "選択中の市町村",
      open: "この市町村のページ",
      change: "変える",
      choose: "市町村を選ぶ",
      go: function (name) { return name + "のページを開く"; }
    };

  function load() {
    try { return localStorage.getItem(STORE) || ""; } catch (e) { return ""; }
  }
  function save(slug) {
    try { localStorage.setItem(STORE, slug); } catch (e) { /* 保存できなくても動く */ }
  }
  function muniUrl(slug) {
    return pageBase + "resident/municipality.html?slug=" + encodeURIComponent(slug);
  }

  var select = document.getElementById("muni-select");
  var saved = load();
  if (!select && !saved) return;

  fetch(siteRoot + "data/municipalities.json")
    .then(function (r) { return r.json(); })
    .then(function (munis) {
      var known = {};
      munis.forEach(function (m) { known[m.slug] = m.name; });
      if (saved && !known[saved]) saved = "";
      if (select) setupSelect(munis, known);
      else if (saved) showBar(known[saved]);
    })
    .catch(function () { /* 読めなければ選択欄も バーも出さない */ });

  // トップの「市町村を選ぶ」欄
  function setupSelect(munis, known) {
    var go = document.getElementById("muni-go");
    var goLine = document.getElementById("muni-go-line");
    var blank = document.createElement("option");
    blank.value = "";
    blank.textContent = T.choose;
    select.appendChild(blank);
    munis.forEach(function (m) {
      var op = document.createElement("option");
      op.value = m.slug;
      op.textContent = m.name;
      select.appendChild(op);
    });
    function sync() {
      var slug = select.value;
      if (!go || !goLine) return;
      if (!slug) { goLine.hidden = true; return; }
      go.href = muniUrl(slug);
      go.textContent = T.go(known[slug]);
      goLine.hidden = false;
    }
    if (saved) select.value = saved;
    sync();
    select.addEventListener("change", function () {
      save(select.value);
      sync();
    });
  }

  // トップ以外のページの上部バー
  function showBar(name) {
    var header = document.querySelector("header");
    if (!header) return;
    var bar = document.createElement("div");
    bar.className = "muni-bar";
    var inner = document.createElement("div");
    inner.className = "muni-bar-inner";

    var label = document.createElement("span");
    label.className = "muni-bar-label";
    label.textContent = T.label;

    var nameEl = document.createElement("span");
    nameEl.className = "muni-bar-name";
    nameEl.textContent = name;

    var open = document.createElement("a");
    open.href = muniUrl(saved);
    open.textContent = T.open;

    var change = document.createElement("a");
    change.href = pageBase + "index.html#muni-select";
    change.textContent = T.change;

    inner.appendChild(label);
    inner.appendChild(nameEl);
    inner.appendChild(open);
    inner.appendChild(change);
    bar.appendChild(inner);
    header.parentNode.insertBefore(bar, header);
  }
})();
