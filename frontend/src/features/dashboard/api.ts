import { apiClient } from "@/lib/api-client";
import type { DashboardSummary, SeverityTrendPoint, TopItem } from "@/types/api";

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await apiClient.get<DashboardSummary>("/dashboard/summary");
  return data;
}

export async function fetchDashboardTrend(days = 30): Promise<SeverityTrendPoint[]> {
  const { data } = await apiClient.get<SeverityTrendPoint[]>("/dashboard/trend", {
    params: { days },
  });
  return data;
}

export async function fetchTopVulnerabilities(limit = 5): Promise<TopItem[]> {
  const { data } = await apiClient.get<TopItem[]>("/dashboard/top-vulnerabilities", {
    params: { limit },
  });
  return data;
}

export async function fetchTopFiles(limit = 5): Promise<TopItem[]> {
  const { data } = await apiClient.get<TopItem[]>("/dashboard/top-files", { params: { limit } });
  return data;
}
