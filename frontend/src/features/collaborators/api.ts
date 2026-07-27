import { apiClient } from "@/lib/api-client";
import type { Collaborator, ProjectRole } from "@/types/api";

export async function listCollaborators(
  projectId: string,
): Promise<Collaborator[]> {
  const { data } = await apiClient.get<Collaborator[]>(
    `/projects/${projectId}/collaborators`,
  );
  return data;
}

export async function addCollaborator(
  projectId: string,
  email: string,
  role: ProjectRole,
): Promise<Collaborator> {
  const { data } = await apiClient.post<Collaborator>(
    `/projects/${projectId}/collaborators`,
    {
      email,
      role,
    },
  );
  return data;
}

export async function updateCollaboratorRole(
  projectId: string,
  userId: string,
  role: ProjectRole,
): Promise<Collaborator> {
  const { data } = await apiClient.patch<Collaborator>(
    `/projects/${projectId}/collaborators/${userId}`,
    { role },
  );
  return data;
}

export async function removeCollaborator(
  projectId: string,
  userId: string,
): Promise<void> {
  await apiClient.delete(`/projects/${projectId}/collaborators/${userId}`);
}
