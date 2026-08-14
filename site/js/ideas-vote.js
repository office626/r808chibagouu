(function () {
  var STORE = "ctzc-r808-feature-votes";
  var ideas = [];
  var mine = { voter: "", votes: {} };
  var serverCounts = {};
  var endpoint = "";
  var filter = "all";
  var sortBy = "votes";
  var busy = false;

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "v-" + Date.now() + "-" + Math.random().toString(16).slice(2);
  }

  function loadMine() {
    try {
      mine = JSON.parse(localStorage.getItem(STORE) || "{}");
    } catch (e) {
      mine = {};
    }
    if (!mine.votes) mine.votes = {};
    if (!mine.voter) mine.voter = uuid();
    saveMine();
  }

  function saveMine() {
    localStorage.setItem(STORE, JSON.stringify(mine));
  }

  function votedCount() {
    return Object.keys(mine.votes).filter(function (k) { return mine.votes[k]; }).length;
  }

  function countFor(id) {
    var n = serverCounts[id] || 0;
    if (!endpoint && mine.votes[id]) n = Math.max(n, 1);
    return n;
  }

  function normalizeEndpoint(raw) {
    var u = String(raw || "").trim();
    u = u.replace(/\/+$/, "");
    u = u.replace(/\/dev$/, "/exec");
    return u;
  }

  function api(action, idea) {
    if (!endpoint) {
      return Promise.resolve(null);
    }
    var sep = endpoint.indexOf("?") >= 0 ? "&" : "?";
    var url = endpoint + sep +
      "action=" + encodeURIComponent(action) +
      "&idea=" + encodeURIComponent(idea || "") +
      "&voter=" + encodeURIComponent(mine.voter);
    return fetch(url, { method: "GET", cache: "no-store", redirect: "follow" })
      .then(function (r) { return r.text(); })
      .then(function (text) {
        var data = JSON.parse(text);
        if (data && data.counts) serverCounts = data.counts;
        return data;
      });
  }

  function render() {
    var root = document.getElementById("ideas");
    var empty = document.getElementById("empty");
    var tally = document.getElementById("tally");
    var top = document.getElementById("top-pick");
    var rows = ideas.filter(function (it) {
      return filter === "all" || it.category === filter;
    });
    rows.sort(function (a, b) {
      if (sortBy === "votes") {
        var d = countFor(b.id) - countFor(a.id);
        if (d) return d;
        if (!!mine.votes[b.id] !== !!mine.votes[a.id]) return mine.votes[b.id] ? -1 : 1;
      }
      var order = { info: 0, feature: 1, action: 2 };
      return (order[a.category] || 9) - (order[b.category] || 9);
    });
    root.innerHTML = "";
    if (!rows.length) {
      empty.hidden = false;
      return;
    }
    empty.hidden = true;
    var max = 1;
    rows.forEach(function (it) {
      if (countFor(it.id) > max) max = countFor(it.id);
    });
    rows.forEach(function (it) {
      var n = countFor(it.id);
      var article = document.createElement("article");
      article.className = "idea" + (mine.votes[it.id] ? " idea-voted" : "");

      var head = document.createElement("div");
      head.className = "idea-head";
      var badge = document.createElement("span");
      badge.className = "badge " + (it.category === "info" ? "admin" : it.category === "feature" ? "pri" : "press");
      badge.textContent = it.category_label;
      var votes = document.createElement("span");
      votes.className = "idea-count";
      votes.textContent = n + " 票";
      head.appendChild(badge);
      head.appendChild(votes);

      var h3 = document.createElement("h3");
      h3.textContent = it.title;
      var p = document.createElement("p");
      p.textContent = it.summary;
      var who = document.createElement("p");
      who.className = "idea-for";
      who.textContent = "想定する利用者: " + it.for;

      var bar = document.createElement("div");
      bar.className = "idea-bar";
      var fill = document.createElement("span");
      fill.style.width = (n / max) * 100 + "%";
      bar.appendChild(fill);

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "vote-btn" + (mine.votes[it.id] ? " done" : "");
      btn.disabled = busy;
      btn.textContent = mine.votes[it.id] ? "投票を取り消す" : "必要だと思う";
      btn.setAttribute("aria-pressed", mine.votes[it.id] ? "true" : "false");
      btn.addEventListener("click", function () { toggle(it.id); });

      article.appendChild(head);
      article.appendChild(h3);
      article.appendChild(p);
      article.appendChild(who);
      article.appendChild(bar);
      article.appendChild(btn);
      root.appendChild(article);
    });

    var nMine = votedCount();
    var mode = endpoint
      ? "票は匿名IDで集計します。同じブラウザでは1案1票です。"
      : "票はこのブラウザに保存されます。全員分の合算は、運用シートの投票スクリプト公開後に有効です。";
    tally.textContent = (nMine ? "あなたは " + nMine + " 件に投票しています。" : "まだ投票していません。") + " " + mode;

    var ranked = ideas.slice().sort(function (a, b) { return countFor(b.id) - countFor(a.id); });
    if (ranked[0] && countFor(ranked[0].id) > 0) {
      top.hidden = false;
      top.textContent = "いま票が最も多い案: " + ranked[0].title + "（" + countFor(ranked[0].id) + " 票）";
    } else {
      top.hidden = true;
    }
  }

  function toggle(id) {
    if (busy) return;
    var next = !mine.votes[id];
    if (next) mine.votes[id] = new Date().toISOString();
    else delete mine.votes[id];
    saveMine();
    if (!endpoint) {
      render();
      return;
    }
    busy = true;
    render();
    api(next ? "vote" : "unvote", id)
      .catch(function () {})
      .then(function () {
        busy = false;
        render();
      });
  }

  function bindFilters() {
    document.querySelectorAll("[data-filter]").forEach(function (el) {
      el.addEventListener("click", function () {
        filter = el.getAttribute("data-filter");
        document.querySelectorAll("[data-filter]").forEach(function (c) {
          c.classList.toggle("on", c === el);
        });
        render();
      });
    });
    document.getElementById("sort").addEventListener("change", function (e) {
      sortBy = e.target.value;
      render();
    });
  }

  loadMine();
  bindFilters();
  Promise.all([
    fetch("../data/feature-ideas.json").then(function (r) { return r.json(); }),
    fetch("../data/vote-config.json").then(function (r) { return r.json(); }).catch(function () { return {}; })
  ]).then(function (pair) {
    ideas = (pair[0] && pair[0].ideas) || [];
    var note = document.getElementById("ideas-note");
    if (note && pair[0].note) note.textContent = pair[0].note;
    endpoint = normalizeEndpoint((pair[1] && pair[1].endpoint) || "");
    return endpoint ? api("list") : null;
  }).then(function () {
    render();
  }).catch(function () {
    document.getElementById("empty").hidden = false;
    document.getElementById("empty").textContent = "案の読み込みに失敗しました。";
  });
})();
