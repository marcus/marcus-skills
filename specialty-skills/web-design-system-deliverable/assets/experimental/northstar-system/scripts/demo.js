const root = document.documentElement;
const storageKey = "northstar-design-system-theme";
const themeButton = document.querySelector("[data-theme-toggle]");
const currentPage = document.body.dataset.page;

function setTheme(theme) {
  root.dataset.theme = theme;
  localStorage.setItem(storageKey, theme);
  if (themeButton) {
    themeButton.textContent = theme === "dark" ? "Light mode" : "Dark mode";
  }
}

const storedTheme = localStorage.getItem(storageKey);
setTheme(storedTheme || "light");

document.querySelectorAll("[data-page-link]").forEach((link) => {
  if (link.dataset.pageLink === currentPage) {
    link.setAttribute("aria-current", "page");
  }
});

if (themeButton) {
  themeButton.addEventListener("click", () => {
    setTheme(root.dataset.theme === "dark" ? "light" : "dark");
  });
}
