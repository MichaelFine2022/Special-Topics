function calculate({ localStorageTheme, systemSettingDark }) {
    return localStorageTheme || (systemSettingDark.matches ? "dark" : "light");
}
  
function updateButton({ buttonEl, isDark }) {
    const newCta = isDark ? "Change to light theme" : "Change to dark theme";
    buttonEl.setAttribute("aria-label", newCta);
    buttonEl.innerText = newCta;
}
  
function updateTheme({ theme }) {
    document.documentElement.setAttribute("data-theme", theme);
}
  
const button = document.querySelector("[data-theme-toggle]");
const localStorageTheme = localStorage.getItem("theme");
const systemSettingDark = window.matchMedia("(prefers-color-scheme: dark)");
  
let currentThemeSetting = calculate({ localStorageTheme, systemSettingDark });
  
updateButton({ buttonEl: button, isDark: currentThemeSetting === "dark" });
updateTheme({ theme: currentThemeSetting });
  
button.addEventListener("click", () => {
    const newTheme = currentThemeSetting === "dark" ? "light" : "dark";
  
    localStorage.setItem("theme", newTheme);
    updateButton({ buttonEl: button, isDark: newTheme === "dark" });
    updateTheme({ theme: newTheme });
  
    currentThemeSetting = newTheme;
});
  
systemSettingDark.addEventListener("change", (event) => {
    if (!localStorage.getItem("theme")) {
      const newSystemTheme = event.matches ? "dark" : "light";
      updateTheme({ theme: newSystemTheme });
      updateButton({ buttonEl: button, isDark: newSystemTheme === "dark" });
      currentThemeSetting = newSystemTheme;
    }
});
  