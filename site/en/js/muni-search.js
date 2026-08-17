(function () {
  function norm(s) {
    s = (s || "").normalize("NFKC").trim().toLowerCase();
    return s.replace(/[ァ-ヶ]/g, function (ch) {
      return String.fromCharCode(ch.charCodeAt(0) - 0x60);
    }).replace(/[\s-]+/g, "");
  }

  function matches(m, word) {
    if (!word) return true;
    var fields = [
      m.name,
      m.kana,
      m.slug,
      window.MunicipalityNames ? MunicipalityNames.get(m.slug) : ""
    ];
    return fields.some(function (value) {
      return norm(value).indexOf(word) !== -1;
    });
  }

  function bindQuery(input, draw, shareBox) {
    var params = new URLSearchParams(location.search);
    var q = params.get("q");
    if (q) input.value = q;
    var copyBtn = shareBox ? shareBox.querySelector("button") : null;
    var copyNote = shareBox ? shareBox.querySelector("[data-note]") : null;

    function sync() {
      var value = (input.value || "").trim();
      var url = new URL(location.href);
      if (value) url.searchParams.set("q", value);
      else url.searchParams.delete("q");
      if (url.href !== location.href) history.replaceState(null, "", url.href);
      if (shareBox) shareBox.hidden = !value;
      if (copyNote) copyNote.textContent = "";
    }

    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var url = location.href;
        function done(message) {
          if (copyNote) copyNote.textContent = message;
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () {
            done("Copied. You can share this filtered list.");
          }, function () {
            done(url);
          });
        } else {
          done(url);
        }
      });
    }

    input.addEventListener("input", function () {
      draw();
      sync();
    });
    draw();
    sync();
  }

  window.MuniSearch = { norm: norm, matches: matches, bindQuery: bindQuery };
})();
