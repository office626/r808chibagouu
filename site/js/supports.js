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
    updated: function (md) { return "Updated " + md; },
    updatedTitle: "The page text changed (detected automatically). Check the official page for what changed.",
    broken: "Could not open (auto check)",
    brokenTitle: "The page could not be fetched at the last automatic check. It may have moved.",
    archived: "archived copy"
  } : {
    checked: function (m, d) { return m + "/" + d + " 確認"; },
    deadline: "期限: ",
    sourceSuffix: "",
    official: "公式",
    updated: function (md) { return "更新 " + md; },
    updatedTitle: "ページの本文が変わったことを自動で検知しました。何が変わったかは公式ページで確認してください。",
    broken: "開けない（自動確認）",
    brokenTitle: "直近の自動確認でページを取得できませんでした。移動した可能性があります。",
    archived: "当時の内容（アーカイブ）"
  };
  var WATCH = null;            // site/data/watch.json の中身 / contents of watch.json
  var FRESH_MS = 72 * 3600 * 1000;
  function setWatch(w) { WATCH = w || null; }
  function md(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(iso || "");
    return m ? String(Number(m[2])) + "/" + String(Number(m[3])) + " " + m[4] + ":" + m[5] : "";
  }
  function isFresh(iso) {
    var t = Date.parse(iso || "");
    return !!t && (Date.now() - t) < FRESH_MS;
  }
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
    var w = WATCH && WATCH.by_url ? WATCH.by_url[item.url] : null;
    if (w && w.last_error) {
      li.appendChild(document.createTextNode(" "));
      var bb = badge("status-broken", T.broken);
      bb.title = T.brokenTitle;
      li.appendChild(bb);
      var au = w.archive_url || ("https://web.archive.org/web/*/" + item.url);
      li.appendChild(document.createTextNode(" "));
      var aa = document.createElement("a");
      aa.className = "report-link";
      aa.href = au;
      aa.target = "_blank";
      aa.rel = "noopener";
      aa.textContent = T.archived;
      li.appendChild(aa);
    } else if (w && w.last_changed && isFresh(w.last_changed)) {
      li.appendChild(document.createTextNode(" "));
      var ub = badge("status-updated", T.updated(md(w.last_changed)));
      ub.title = T.updatedTitle + ((w.added && w.added.length) ? "\n" + w.added.join("\n") : "");
      li.appendChild(ub);
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
  window.SupportsView = { renderItem: renderItem, renderList: renderList, latestChecked: latestChecked, setWatch: setWatch, md: md, isFresh: isFresh };
})();
