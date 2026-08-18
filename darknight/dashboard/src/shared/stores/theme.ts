import { defineStore } from "pinia";
import { ref } from "vue";

const THEME_KEY = "darknight-theme";
export type ThemeMode = "light" | "dark";

function detectTheme(): ThemeMode {
  const saved = localStorage.getItem(THEME_KEY) as ThemeMode | null;
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function applyTheme(mode: ThemeMode): void {
  const root = document.documentElement;
  if (mode === "dark") root.classList.add("dark");
  else root.classList.remove("dark");
}

export const useThemeStore = defineStore("theme", () => {
  const mode = ref<ThemeMode>(detectTheme());
  applyTheme(mode.value);

  function setMode(next: ThemeMode) {
    mode.value = next;
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  }

  function toggle() {
    setMode(mode.value === "dark" ? "light" : "dark");
  }

  return { mode, setMode, toggle };
});
