(function () {
  function pageUrl() {
    return location.href;
  }
  function pageText() {
    return document.title || "CTZC 千葉豪雨ポータル";
  }
  function enc(s) {
    return encodeURIComponent(s);
  }
  function hrefs() {
    var u = pageUrl();
    var t = pageText();
    return {
      line: "https://social-plugins.line.me/lineit/share?url=" + enc(u),
      facebook: "https://www.facebook.com/sharer/sharer.php?u=" + enc(u),
      x: "https://twitter.com/intent/tweet?url=" + enc(u) + "&text=" + enc(t)
    };
  }
  function btn(label, kind) {
    var a = document.createElement("a");
    a.className = "share-btn share-" + kind;
    a.textContent = label;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.addEventListener("click", function () {
      var h = hrefs();
      a.href = h[kind];
    });
    a.href = hrefs()[kind];
    return a;
  }
  function mount(root) {
    var label = document.createElement("p");
    label.className = "share-label";
    label.textContent = "このページを共有";
    var row = document.createElement("p");
    row.className = "share-btns";
    row.appendChild(btn("LINE", "line"));
    row.appendChild(btn("Facebook", "facebook"));
    row.appendChild(btn("X", "x"));
    var copy = document.createElement("button");
    copy.type = "button";
    copy.className = "share-btn share-copy";
    copy.textContent = "リンクをコピー";
    copy.addEventListener("click", function () {
      var url = pageUrl();
      function ok() {
        copy.textContent = "コピーしました";
        setTimeout(function () { copy.textContent = "リンクをコピー"; }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(ok).catch(function () {
          window.prompt("このURLをコピーしてください", url);
        });
      } else {
        window.prompt("このURLをコピーしてください", url);
      }
    });
    row.appendChild(copy);
    if (navigator.share) {
      var native = document.createElement("button");
      native.type = "button";
      native.className = "share-btn share-copy";
      native.textContent = "端末の共有";
      native.addEventListener("click", function () {
        navigator.share({ title: pageText(), url: pageUrl() }).catch(function () {});
      });
      row.appendChild(native);
    }
    var note = document.createElement("p");
    note.className = "meta";
    note.textContent = "Instagramなど、共有ボタンがないアプリには「リンクをコピー」を使ってください。申請窓口ではありません。";
    root.appendChild(label);
    root.appendChild(row);
    root.appendChild(note);
  }
  document.querySelectorAll("[data-share]").forEach(mount);
})();
