// 市町村公式の支援リンク（supports.json）の共通描画。日本語版・英語版で共通。
// 種類バッジ・受付状態・確認日・期限を1行で出す。金額は出さない。
// Shared renderer for municipal official links (supports.json). Used by both the Japanese and English pages.
(function () {
  var EN = document.documentElement.lang === "en";
  var T = EN ? {
    checked: function (m, d) { return "checked " + m + "/" + d; },
    deadline: "Deadline: ",
    sourceSuffix: " (Japanese source title)",
    official: "Official site"
  } : {
    checked: function (m, d) { return m + "/" + d + " 確認"; },
    deadline: "期限: ",
    sourceSuffix: "",
    official: "公式"
  };
  function fmtDate(ymd) {
    if (!ymd) return "";
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd);
    if (!m) return ymd;
    return T.checked(String(Number(m[2])), String(Number(m[3])));
  }
  function badge(cls, text) {
    var s = document.createElement("span");
    s.className = "badge " + cls;
    s.textContent = text;
    return s;
  }
  // item: {kind, kind_label, kind_label_en, title, url, status, status_label, status_label_en, checked, deadline, note}
  function renderItem(item, muniName) {
    var li = document.createElement("li");
    li.className = "support-item kind-" + (item.kind || "support");
    var a = document.createElement("a");
    a.href = item.url;
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = item.title + T.sourceSuffix;
    li.appendChild(a);
    li.appendChild(document.createTextNode(" "));
    li.appendChild(badge("admin", (EN ? item.kind_label_en : item.kind_label) || T.official));
    if (item.status && item.status !== "unknown") {
      li.appendChild(document.createTextNode(" "));
      li.appendChild(badge("status-" + item.status, (EN ? item.status_label_en : item.status_label) || item.status));
    }
    var meta = [];
    if (item.deadline) meta.push(T.deadline + item.deadline);
    if (item.checked) meta.push(fmtDate(item.checked));
    if (item.note && !EN) meta.push(item.note);
    if (meta.length) {
      var s = document.createElement("span");
      s.className = "support-meta";
      s.textContent = meta.join(" / ");
      li.appendChild(document.createTextNode(" "));
      li.appendChild(s);
    }
    if (window.Report) {
      li.appendChild(document.createTextNode(" "));
      li.appendChild(Report.itemLink((muniName ? muniName + " / " : "") + item.title + " / " + item.url));
    }
    return li;
  }
  function renderList(ul, items, muniName) {
    ul.innerHTML = "";
    (items || []).forEach(function (it) { ul.appendChild(renderItem(it, muniName)); });
  }
  function latestChecked(items) {
    var dates = (items || []).map(function (it) { return it.checked; }).filter(Boolean).sort();
    return dates.length ? dates[dates.length - 1] : "";
  }
  window.SupportsView = { renderItem: renderItem, renderList: renderList, latestChecked: latestChecked };
})();
