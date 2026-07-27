import { apiClient } from "@/lib/api-client";
import type { Scan } from "@/types/api";

export async function listProjectScans(projectId: string): Promise<Scan[]> {
  const { data } = await apiClient.get<Scan[]>(`/scans/project/${projectId}`);
  return data;
}

export async function getScan(scanId: string): Promise<Scan> {
  const { data } = await apiClient.get<Scan>(`/scans/${scanId}`);
  return data;
}

export async function uploadAndScan(projectId: string, file: File): Promise<Scan> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<Scan>(
    `/scans/upload?project_id=${projectId}`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return data;
}

export async function scanGitRepository(projectId: string, repositoryUrl: string): Promise<Scan> {
  const { data } = await apiClient.post<Scan>("/scans/git", {
    project_id: projectId,
    repository_url: repositoryUrl,
  });
  return data;
}

export function reportDownloadUrl(scanId: string, format: string): string {
  return `/api/v1/reports/${scanId}?format=${format}`;
}
