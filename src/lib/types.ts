// ============================================================================
// Types TypeScript — alignés sur le schéma PostgreSQL / backend FastAPI
// ============================================================================

export type Cycle = "CEM" | "LYCEE";

export interface Level {
  id: number;
  code: string;
  name: string;
  cycle: Cycle;
}

export interface Subject {
  id: number;
  slug: string;
  name: string;
}

export interface Agent {
  id: string;
  level_id: number;
  subject_id: number;
  agent_name: string;
  system_prompt: string;
  allowed_tools: string[];
  model_config: { model: string; temperature: number };
  is_active: boolean;
  level?: Level;
  subject?: Subject;
}

export type SubscriptionStatus =
  | "trialing"
  | "active"
  | "past_due"
  | "canceled"
  | "incomplete"
  | "trialing_expired";

export interface User {
  id: string;
  email: string;
  detected_level_id: number | null;
  detected_level?: Level | null;
  trial_starts_at: string;
  trial_ends_at: string;
  subscription_status: SubscriptionStatus;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  last_active_at: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  rating?: number | null;
}

export interface ChatRequest {
  agent_id?: string;
  session_id?: string;
  message: string;
  level_code?: string;
  subject_slug?: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  agent_id: string;
  agent_name: string;
  tokens_input: number;
  tokens_output: number;
  usage_log_id: string;
}

export interface QuizQuestion {
  id: string;
  subject_slug: string;
  question: string;
  options: string[];
  correct_index: number;
  level_hint: string;
}

export interface QuizSubmission {
  answers: Record<string, number>;
}

export interface QuizResult {
  detected_level_code: string;
  detected_level_name: string;
  score_by_subject: Record<string, { correct: number; total: number }>;
  recommendation: string;
}

export interface FeedbackRequest {
  usage_log_id: string;
  rating: number;
  comment?: string;
}

export interface PricingPlan {
  id: string;
  name: string;
  price: number;
  interval: "month" | "year";
  stripe_price_id: string;
  features: string[];
  highlighted?: boolean;
}

export interface ApiError {
  detail: string;
  code?: string;
}
