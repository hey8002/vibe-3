const defaultApiBase = "/api";
const storageKey = "admin-superapp-api-base-url";

export function getApiBaseUrl(): string {
  const runtimeValue = window.localStorage.getItem(storageKey);
  if (runtimeValue && runtimeValue.trim()) {
    return runtimeValue.replace(/\/$/, "");
  }

  const value = import.meta.env.VITE_API_BASE_URL;
  return value && value.trim() ? value.replace(/\/$/, "") : defaultApiBase;
}

export function apiUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}

export function setApiBaseUrl(value: string): void {
  const normalized = value.trim().replace(/\/$/, "");
  if (!normalized) {
    window.localStorage.removeItem(storageKey);
    return;
  }
  window.localStorage.setItem(storageKey, normalized);
}

export function clearApiBaseUrl(): void {
  window.localStorage.removeItem(storageKey);
}
