// 市町村公式の支援リンク（supports.json）の共通描画。日本語版・英語版で共通。
// 種類バッジ・受付状態・確認日・期限を1行で出す。金額は出さない。
// Shared renderer for municipal official links (supports.json). Used by both the Japanese and English pages.
(function () {
  var EN = document.documentElement.lang === "en";
  var T = EN ? {
    checked: function (m, d) { return "checked " + m + "/" + d; },
    deadline: "Deadline: ",
    sourceSuffix: " (Japanese source title)",
    official: "Official site",
    issueTitle: function (name) { return "[" + name + "] Add or fix an official link"; },
    issueBody: function (name, slug) {
      return "Municipality: " + name + " (" + slug + ")\n" +
        "Kind (risai / support / waste / disinfect / water / housing / vc / hub): \n" +
        "Official page title: \n" +
        "URL: \n" +
        "Status (open / preparing / closed / unknown): \n" +
        "Deadline (only if stated officially): \n" +
        "Date checked: \n\n" +
        "You can also add one row to data/supports.csv.";
    }
  } : {
    checked: function (m, d) { return m + "/" + d + " 確認"; },
    deadline: "期限: ",
    sourceSuffix: "",
    official: "公式",
    issueTitle: function (name) { return "[" + name + "] 公式リンクの追加・修正"; },
    issueBody: function (name, slug) {
      return "対象市町村: " + name + " (" + slug + ")\n" +
        "種類（罹災証明／支援策／災害ごみ／消毒／断水／住まい／ボランティア／大雨情報まとめ）: \n" +
        "公式ページの見出し: \n" +
        "URL: \n" +
        "受付状態（受付中／準備中／終了／不明）: \n" +
        "期限（公式に書かれていれば）: \n" +
        "確認した日: \n\n" +
        "※ data/supports.csv に1行足すか、この Issue に書いてください。";
    }
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
  function renderItem(item) {
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
    return li;
  }
  function renderList(ul, items) {
    ul.innerHTML = "";
    (items || []).forEach(function (it) { ul.appendChild(renderItem(it)); });
  }
  function latestChecked(items) {
    var dates = (items || []).map(function (it) { return it.checked; }).filter(Boolean).sort();
    return dates.length ? dates[dates.length - 1] : "";
  }
  // 「情報を足す・直す」用の Issue リンク / prefilled GitHub issue link
  function issueLink(muniName, slug) {
    return "https://github.com/office626/r808chibagouu/issues/new?title=" +
      encodeURIComponent(T.issueTitle(muniName)) + "&body=" + encodeURIComponent(T.issueBody(muniName, slug));
  }
  window.SupportsView = { renderItem: renderItem, renderList: renderList, latestChecked: latestChecked, issueLink: issueLink };
})();
