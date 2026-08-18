import { ofetch, type FetchOptions } from "ofetch";
import { getAuthToken, removeAuthToken } from "@/shared/lib/authStorage";

const DEFAULT_BASE_API = "/api/v1/";

function resolveBaseURL(): string {
  const envBase = import.meta.env.VITE_BASE_API;
  if (typeof envBase === "string" && envBase.length > 0) {
    return envBase.endsWith("/") ? envBase : `${envBase}/`;
  }
  return DEFAULT_BASE_API;
}

const instance = ofetch.create({
  baseURL: resolveBaseURL(),
  onResponseError({ response }) {
    if (response.status === 401) {
      removeAuthToken();
      if (!window.location.hash.startsWith("#/login")) {
        window.location.hash = "#/login";
      }
    }
  },
});

// ofetch treats a leading "/" as site-root absolute and ignores baseURL.
function normalizeURL(url: string): string {
  if (/^https?:\/\//i.test(url) || url.startsWith("//")) return url;
  return url.replace(/^\/+/, "");
}

export function http<T = unknown>(
  url: string,
  options: FetchOptions<"json"> = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  return instance<T>(normalizeURL(url), {
    ...options,
    headers,
  }) as Promise<T>;
}
