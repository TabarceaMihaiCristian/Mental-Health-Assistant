function parseApiBaseUrl() {
  const fallback = "http://localhost:8000/api/v1";
  const rawValue = import.meta.env.VITE_API_BASE_URL?.trim() || fallback;

  try {
    return new URL(rawValue).toString().replace(/\/$/, "");
  } catch {
    throw new Error(`Invalid VITE_API_BASE_URL: ${rawValue}`);
  }
}

export const appConfig = {
  apiBaseUrl: parseApiBaseUrl(),
} as const;
