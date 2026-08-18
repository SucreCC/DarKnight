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
  return $fetch<T>(url, ops);
};

export const fetch = fetcher;
