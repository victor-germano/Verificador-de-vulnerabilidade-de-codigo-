import { apiClient } from "@/lib/api-client";
import type { TokenResponse, User } from "@/types/api";

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/auth/login", { email, password });
  return data;
}

export async function register(email: string, password: string, fullName: string): Promise<User> {
  const { data } = await apiClient.post<User>("/auth/register", {
    email,
    password,
    full_name: fullName,
  });
  return data;
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}
