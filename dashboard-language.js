(() => {
  const STORAGE_KEY = "gta-dashboard-language";
  const root = document.documentElement;
  const buttons = Array.from(document.querySelectorAll("[data-set-language]"));

  function normalizeLanguage(value) {
    return value === "th" ? "th" : "en";
  }

  function setLanguage(value) {
    const language = normalizeLanguage(value);
    root.lang = language;
    root.setAttribute("data-ui-language", language);

    for (const button of buttons) {
      const isActive = button.getAttribute("data-set-language") === language;
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    }

    try {
      window.localStorage.setItem(STORAGE_KEY, language);
    } catch (_error) {
      // Best effort only.
    }
  }

  let initialLanguage = "en";
  try {
    initialLanguage = normalizeLanguage(window.localStorage.getItem(STORAGE_KEY));
  } catch (_error) {
    initialLanguage = "en";
  }

  for (const button of buttons) {
    button.addEventListener("click", () => {
      setLanguage(button.getAttribute("data-set-language"));
    });
  }

  setLanguage(initialLanguage);
})();
