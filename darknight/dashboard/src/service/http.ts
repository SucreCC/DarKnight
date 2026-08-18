import { FetchOptions, $fetch as ohMyFetch } from "ofetch";
import { getAuthToken } from "utils/authStorage";

const DEFAULT_BASE_API = "/api/v1/";

function resolveBaseURL(): string {
  const envBase = import.meta.env.VITE_BASE_API;
  if (typeof envBase === "string" && envBase.length > 0) {
    return envBase.endsWith("/") ? envBase : `${envBase}/`;
  }
  return DEFAULT_BASE_API;
}

export const $fetch = ohMyFetch.create({
  baseURL: resolveBaseURL(),
});

function normalizeRequestURL(url: string): string {
  if (/^https?:\/\//i.test(url) || url.startsWith("//")) {
    return url;
  }
  // ofetch treats "/path" as site-root absolute and ignores baseURL prefix.
  return url.replace(/^\/+/, "");
}

export const fetcher = <T = any>(
  url: string,
  ops: FetchOptions<"json"> = {}
) => {
  const token = getAuthToken();
  if (token) {
    ops["headers"] = {
      ...(ops?.headers || {}),
      Authorization: `Bearer ${getAuthToken()}`,
    };
  }
  return $fetch<T>(normalizeRequestURL(url), ops);
};

export const fetch = fetcher;
