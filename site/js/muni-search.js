// 市町村の読み検索。県民ホームと市町村一覧で共通に使う。
// カタカナ・全角英数はひらがな・半角に寄せ、名前・読み（kana）・slug の先頭に当てる。
(function () {
  function norm(s) {
    s = (s || "").normalize("NFKC").trim().toLowerCase();
    return s.replace(/[ァ-ヶ]/g, function (ch) {
      return String.fromCharCode(ch.charCodeAt(0) - 0x60);
    }).replace(/\s+/g, "");
  }
  function matches(m, word) {
    if (!word) return true;
    if (norm(m.name).indexOf(word) !== -1) return true;
    if (norm(m.kana).indexOf(word) !== -1) return true;
    if (m.slug && m.slug.indexOf(word) === 0) return true;
    return false;
  }
  // ?q= を検索欄に入れ、入力に合わせて URL を書き換える。
  // 「印西で絞った状態」の URL をそのまま共有できるようにするため。履歴は増やさない。
  function bindQuery(input, draw, shareBox) {
    var params = new URLSearchParams(location.search);
    var q = params.get("q");
    if (q) input.value = q;
    var copyBtn = shareBox ? shareBox.querySelector("button") : null;
    var copyNote = shareBox ? shareBox.querySelector("[data-note]") : null;
    function sync() {
      var v = (input.value || "").trim();
      var u = new URL(location.href);
      if (v) u.searchParams.set("q", v); else u.searchParams.delete("q");
      if (u.href !== location.href) history.replaceState(null, "", u.href);
      if (shareBox) shareBox.hidden = !v;
      if (copyNote) copyNote.textContent = "";
    }
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var url = location.href;
        function done(msg) { if (copyNote) copyNote.textContent = msg; }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () { done("コピーしました。LINE などで「" + input.value.trim() + "」の人に送れます。"); },
            function () { done(url); });
        } else {
          done(url);
        }
      });
    }
    input.addEventListener("input", function () { draw(); sync(); });
    draw();
    sync();
  }
  window.MuniSearch = { norm: norm, matches: matches, bindQuery: bindQuery };
})();
