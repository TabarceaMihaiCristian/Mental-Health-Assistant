export interface UserProfile {
  age_range: string | null;
  occupation: string | null;
  goals: string | null;
  preferred_activities: string[];
  timezone: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  profile?: UserProfile | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
}

export interface ForgotPasswordPayload {
  email: string;
}

export interface ForgotPasswordResponse {
  message: string;
  reset_token?: string | null;
}

export interface ResetPasswordPayload {
  token: string;
  password: string;
}

export interface PasswordResetResponse {
  message: string;
}
