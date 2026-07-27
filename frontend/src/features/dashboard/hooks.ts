import { useQuery } from "@tanstack/react-query";

import {
  fetchDashboardSummary,
  fetchDashboardTrend,
  fetchTopFiles,
  fetchTopVulnerabilities,
} from "@/features/dashboard/api";

export function useDashboardSummary() {
  return useQuery({ queryKey: ["dashboard", "summary"], queryFn: fetchDashboardSummary });
}

export function useDashboardTrend(days = 30) {
  return useQuery({
    queryKey: ["dashboard", "trend", days],
    queryFn: () => fetchDashboardTrend(days),
  });
}

export function useTopVulnerabilities(limit = 5) {
  return useQuery({
    queryKey: ["dashboard", "top-vulnerabilities", limit],
    queryFn: () => fetchTopVulnerabilities(limit),
  });
}

export function useTopFiles(limit = 5) {
  return useQuery({
    queryKey: ["dashboard", "top-files", limit],
    queryFn: () => fetchTopFiles(limit),
  });
}
