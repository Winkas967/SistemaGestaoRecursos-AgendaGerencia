const root = document.documentElement;
const toggleBtn = document.getElementById("themeToggle");
const iconSun = document.getElementById("iconSun");
const iconMoon = document.getElementById("iconMoon");
const label = document.getElementById("themeLabel");

function applyTheme(theme) {
    root.setAttribute("data-theme", theme);

    if (theme === "dark") {
        iconSun.style.display = "none";
        iconMoon.style.display = "block";
        label.textContent = "Modo claro";
    } else {
        iconSun.style.display = "block";
        iconMoon.style.display = "none";
        label.textContent = "Modo escuro";
    }

    localStorage.setItem("theme", theme);
}

const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
let currentTheme = savedTheme || (prefersDark ? "dark" : "light");

applyTheme(currentTheme);

window.addEventListener("load", () => {
    root.classList.remove("is-loading");
    root.classList.add("is-ready");
});

toggleBtn.addEventListener("click", () => {
    currentTheme = currentTheme === "light" ? "dark" : "light";
    applyTheme(currentTheme);
});
