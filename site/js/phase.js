// 発災からの日数を数えて、時期別ページの「いま」の位置を自動で示す。
// 見出しに「（いま）」を書き込んでしまうと、日が経つほど実態とずれるため。
// JavaScript が動かない場合は印が付かないだけで、本文はそのまま読める。
(function () {
  var ONSET = Date.UTC(2026, 7, 13); // 令和8年8月13日
  var isEnglish = document.documentElement.lang === "en";
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-phase-from]"));
  if (!cards.length) return;

  var now = new Date();
  var today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  var days = Math.floor((today - ONSET) / 86400000);
  if (days < 0) return;

  var current = null;
  cards.forEach(function (card) {
    var from = parseInt(card.getAttribute("data-phase-from"), 10);
    var to = card.getAttribute("data-phase-to");
    var upper = to === "" || to === null ? Infinity : parseInt(to, 10);
    if (days >= from && days <= upper) current = card;
  });
  if (!current) return;

  var label = isEnglish ? "now" : "いま";
  var heading = current.querySelector("h2");
  if (heading) {
    var mark = document.createElement("span");
    mark.className = "phase-now";
    mark.textContent = label;
    heading.insertBefore(mark, heading.firstChild);
  }
  var toc = document.querySelector('.page-toc a[href="#' + current.id + '"]');
  if (toc) toc.classList.add("phase-now-link");

  var line = document.getElementById("phase-now");
  if (line) {
    var name = (heading ? heading.textContent : "").replace(label, "").split("：")[0].split(":")[0].trim();
    line.textContent = isEnglish
      ? "Day " + days + " since the disaster (13 August 2026). You are in the “" + name + "” period below."
      : "発災（8月13日）から" + days + "日目。下の「" + name + "」がいまの時期です。";
  }
})();
