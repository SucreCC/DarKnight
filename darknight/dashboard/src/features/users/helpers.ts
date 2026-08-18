import { formatBytes } from "@/shared/lib/format";
import { RESET_STRATEGIES, type DataLimitResetStrategy } from "./types";

export function usagePercentage(used: number, total: number | null): number {
  if (total === 0 || total === null) return 0;
  return Math.min((used / total) * 100, 100);
}

export function isUnlimited(total: number | null): boolean {
  return total === 0 || total === null;
}

export function usageTotalText(
  total: number | null,
  resetStrategy: DataLimitResetStrategy,
  translate: (key: string) => string
): string {
  if (isUnlimited(total)) return "∞";
  let text = formatBytes(total as number);
  if (resetStrategy !== "no_reset") {
    const entry = RESET_STRATEGIES.find((s) => s.value === resetStrategy);
    if (entry) text += ` ${translate(`userDialog.${entry.title}`)}`;
  }
  return text;
}

export function absoluteSubscriptionUrl(url: string): string {
  return url.startsWith("/") ? window.location.origin + url : url;
}
