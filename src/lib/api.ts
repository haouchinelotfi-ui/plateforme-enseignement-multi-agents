import { ApiError } from "./types";

// ============================================================================
// API Client — wrapper fetch vers le backend FastAPI (Render)
// ============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const APP_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("oupsii_token");
}

export function setToken(token: string) {
  if (typeof window !== "undefined") localStorage.setItem("oupsii_token", token);
}

export function clearToken() {
  if (typeof window !== "undefined") localStorage.removeItem("oupsii_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    // Include credentials for cookie-based flows if needed
    credentials: "include",
  });

  if (!res.ok) {
    let detail = `Erreur ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
    } catch {
      /* non-JSON error */
    }
    const err: ApiError = { detail, code: String(res.status) };
    throw err;
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ---------- Auth ----------

export const api = {
  baseURL: API_URL,
  appURL: APP_URL,

  async register(email: string, password: string) {
    const { access_token, user } = await request<{
      access_token: string;
      user: import("./types").User;
    }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setToken(access_token);
    return user;
  },

  async login(email: string, password: string) {
    const { access_token, user } = await request<{
      access_token: string;
      user: import("./types").User;
    }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setToken(access_token);
    return user;
  },

  async me() {
    return request<import("./types").User>("/api/auth/me");
  },

  logout() {
    clearToken();
  },

  // ---------- Quiz ----------

  async getQuiz() {
    return request<import("./types").QuizQuestion[]>("/api/quiz/questions");
  },

  async submitQuiz(answers: Record<string, number>) {
    return request<import("./types").QuizResult>("/api/quiz/submit", {
      method: "POST",
      body: JSON.stringify({ answers }),
    });
  },

  // ---------- Agents / Chat ----------

  async getAgents() {
    return request<import("./types").Agent[]>("/api/agents");
  },

  async chat(message: string, opts?: { agent_id?: string; session_id?: string; level_code?: string; subject_slug?: string }) {
    return request<import("./types").ChatResponse>("/api/agents/chat", {
      method: "POST",
      body: JSON.stringify({ message, ...opts }),
    });
  },

  async getHistory(session_id: string) {
    return request<import("./types").ChatMessage[]>(`/api/agents/history/${session_id}`);
  },

  // ---------- Billing ----------

  async createCheckoutSession(price_id: string) {
    return request<{ url: string }>("/api/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ price_id, success_url: `${APP_URL}/dashboard?billing=success`, cancel_url: `${APP_URL}/pricing?billing=cancel` }),
    });
  },

  async createPortalSession() {
    return request<{ url: string }>("/api/billing/portal");
  },

  // ---------- Feedback ----------

  async submitFeedback(usage_log_id: string, rating: number, comment?: string) {
    return request<{ ok: boolean }>("/api/feedback", {
      method: "POST",
      body: JSON.stringify({ usage_log_id, rating, comment }),
    });
  },
};
