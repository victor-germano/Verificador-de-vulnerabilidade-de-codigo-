import { apiClient } from "@/lib/api-client";
import type { Project } from "@/types/api";

export async function listProjects(): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>("/projects");
  return data;
}

export async function getProject(projectId: string): Promise<Project> {
  const { data } = await apiClient.get<Project>(`/projects/${projectId}`);
  return data;
}

export async function createProject(name: string, description?: string): Promise<Project> {
  const { data } = await apiClient.post<Project>("/projects", { name, description });
  return data;
}

export async function deleteProject(projectId: string): Promise<void> {
  await apiClient.delete(`/projects/${projectId}`);
}
