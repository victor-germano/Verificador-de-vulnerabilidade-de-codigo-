import { apiClient } from "@/lib/api-client";
import type { Finding, FindingFilters } from "@/types/api";

export async function listFindings(filters: FindingFilters): Promise<Finding[]> {
  const { data } = await apiClient.get<Finding[]>("/findings", { params: filters });
  return data;
}
