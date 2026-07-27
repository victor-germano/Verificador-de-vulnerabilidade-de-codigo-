import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  addCollaborator,
  listCollaborators,
  removeCollaborator,
  updateCollaboratorRole,
} from "@/features/collaborators/api";
import type { ProjectRole } from "@/types/api";

export function useCollaborators(projectId: string | undefined) {
  return useQuery({
    queryKey: ["collaborators", projectId],
    queryFn: () => listCollaborators(projectId as string),
    enabled: Boolean(projectId),
  });
}

export function useAddCollaborator(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ email, role }: { email: string; role: ProjectRole }) =>
      addCollaborator(projectId, email, role),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["collaborators", projectId],
      });
    },
  });
}

export function useUpdateCollaboratorRole(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: ProjectRole }) =>
      updateCollaboratorRole(projectId, userId, role),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["collaborators", projectId],
      });
    },
  });
}

export function useRemoveCollaborator(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => removeCollaborator(projectId, userId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["collaborators", projectId],
      });
    },
  });
}
