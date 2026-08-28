const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/+$/, "");
const TOKEN_KEY = "supplier_price_intelligence_token";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export class NetworkError extends Error {}
export const getToken = () => sessionStorage.getItem(TOKEN_KEY);
export const setToken = (token: string) => sessionStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => sessionStorage.removeItem(TOKEN_KEY);

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(
      `${API_BASE_URL}/${path.replace(/^\/+/, "")}`,
      { ...options, headers },
    );
  } catch {
    throw new NetworkError("Unable to reach the API server.");
  }

  if (response.status === 401) { clearToken(); window.dispatchEvent(new Event("session-expired")); }
  if (!response.ok) {
    const body: { detail?: string | Array<{ msg?: string }> } = await response
      .json()
      .catch(() => ({}));
    const detail = Array.isArray(body.detail)
      ? body.detail.map((issue) => issue.msg).filter(Boolean).join(" ")
      : body.detail;
    throw new ApiError(
      response.status,
      detail || "The request could not be completed.",
    );
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
