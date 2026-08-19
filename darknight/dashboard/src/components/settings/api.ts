import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { http } from "@/shared/api/http";
import { getAuthToken } from "@/shared/lib/authStorage";

export type CoreInfo = {
  version: string | null;
  started: boolean | null;
  logs_websocket: string | null;
};

export const coreQueryKey = ["core"] as const;
export const coreConfigQueryKey = ["core", "config"] as const;

export function useCoreQuery() {
  return useQuery({
    queryKey: coreQueryKey,
    queryFn: () => http<CoreInfo>("/core"),
    refetchOnWindowFocus: false,
  });
}

export function useCoreConfigQuery() {
  return useQuery({
    queryKey: coreConfigQueryKey,
    queryFn: () => http<Record<string, unknown>>("/core/config"),
    refetchOnWindowFocus: false,
  });
}

export function useUpdateConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      http("/core/config", { method: "PUT", body }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: coreQueryKey });
      queryClient.invalidateQueries({ queryKey: coreConfigQueryKey });
    },
  });
}

export function useRestartCore() {
  return useMutation({
    mutationFn: () => http("/core/restart", { method: "POST" }),
  });
}

export function buildLogsWebsocketUrl(nodeId?: string): string | null {
  try {
    const base = import.meta.env.VITE_BASE_API || "/api/v1/";
    const url = new URL(
      base.startsWith("/") ? window.location.origin + base : base
    );
    const proto = url.protocol === "https:" ? "wss://" : "ws://";
    const path = `${url.host}${url.pathname}`.replace(/\/+$/, "");
    const logPath = nodeId ? `/node/${nodeId}/logs` : "/core/logs";
    return `${proto}${path}${logPath}?interval=1&token=${getAuthToken()}`;
  } catch {
    return null;
  }
}
