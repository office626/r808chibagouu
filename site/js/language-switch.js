(function () {
  var script = document.currentScript;
  if (!script) return;

  var siteRoot = new URL("../", script.src);
  var rootPath = siteRoot.pathname;
  var enRootPath = rootPath + "en/";
  var path = location.pathname;
  var isEnglish = path.indexOf(enRootPath) === 0;
  var relativePath = isEnglish
    ? path.slice(enRootPath.length)
    : path.indexOf(rootPath) === 0
      ? path.slice(rootPath.length)
      : "";

  if (!relativePath || relativePath === "en") relativePath = "index.html";

  function pageUrl(language) {
    var base = language === "en" ? enRootPath : rootPath;
    return location.origin + base + relativePath + location.search + location.hash;
  }

  function languageItem(language, label) {
    if ((language === "en") === isEnglish) {
      var current = document.createElement("span");
      current.lang = language;
      current.setAttribute("aria-current", "page");
      current.textContent = label;
      return current;
    }
    var link = document.createElement("a");
    link.lang = language;
    link.hreflang = language;
    link.href = pageUrl(language);
    link.textContent = label;
    return link;
  }

  var nav = document.createElement("nav");
  nav.className = "language-switch";
  nav.setAttribute("aria-label", isEnglish ? "Language selection" : "言語選択");
  nav.appendChild(languageItem("ja", "日本語"));
  nav.appendChild(languageItem("en", "English"));
  document.body.insertBefore(nav, document.body.firstChild);

  var pageNav = document.querySelector("header .nav");
  if (!pageNav) return;

  var openLabel = isEnglish ? "☰ Menu" : "☰ メニュー";
  var closeLabel = isEnglish ? "× Close" : "× 閉じる";
  var menuId = "site-menu";
  var button = document.createElement("button");
  button.type = "button";
  button.className = "menu-toggle";
  button.setAttribute("aria-controls", menuId);
  button.setAttribute("aria-expanded", "false");
  button.textContent = openLabel;

  pageNav.id = menuId;
  pageNav.classList.add("menu-panel");
  pageNav.setAttribute("aria-label", isEnglish ? "Other pages" : "他のページ");
  pageNav.hidden = true;
  pageNav.parentNode.insertBefore(button, pageNav);

  function setOpen(open) {
    pageNav.hidden = !open;
    button.setAttribute("aria-expanded", open ? "true" : "false");
    button.textContent = open ? closeLabel : openLabel;
  }

  button.addEventListener("click", function () {
    setOpen(button.getAttribute("aria-expanded") !== "true");
  });
  pageNav.addEventListener("click", function (event) {
    if (event.target.closest("a")) setOpen(false);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !pageNav.hidden) {
      setOpen(false);
      button.focus();
    }
  });
})();
