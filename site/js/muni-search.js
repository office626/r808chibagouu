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
  window.MuniSearch = { norm: norm, matches: matches };
})();
