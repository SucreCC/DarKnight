import { createI18n } from "vue-i18n";
import en from "@/locales/en.json";
import zh from "@/locales/zh.json";
import ru from "@/locales/ru.json";
import fa from "@/locales/fa.json";

const LANG_KEY = "darknight-lang";

export const SUPPORTED_LOCALES = [
  { value: "en", label: "English" },
  { value: "zh", label: "中文" },
  { value: "ru", label: "Русский" },
  { value: "fa", label: "فارسی" },
] as const;

export type LocaleCode = (typeof SUPPORTED_LOCALES)[number]["value"];

function detectLocale(): LocaleCode {
  const saved = localStorage.getItem(LANG_KEY) as LocaleCode | null;
  if (saved && SUPPORTED_LOCALES.some((l) => l.value === saved)) return saved;
  const nav = navigator.language.split("-")[0];
  if (SUPPORTED_LOCALES.some((l) => l.value === nav)) return nav as LocaleCode;
  return "en";
}

export const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: "en",
  messages: { en, zh, ru, fa },
});

export function setLocale(locale: LocaleCode): void {
  i18n.global.locale.value = locale;
  localStorage.setItem(LANG_KEY, locale);
  document.documentElement.setAttribute("lang", locale);
  document.documentElement.setAttribute(
    "dir",
    locale === "fa" ? "rtl" : "ltr"
  );
}
