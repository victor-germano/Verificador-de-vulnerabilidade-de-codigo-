import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createProject, deleteProject, getProject, listProjects } from "@/features/projects/api";

export function useProjects() {
  return useQuery({ queryKey: ["projects"], queryFn: listProjects });
}

export function useProject(projectId: string | undefined) {
  return useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => getProject(projectId as string),
    enabled: Boolean(projectId),
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ name, description }: { name: string; description?: string }) =>
      createProject(name, description),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (projectId: string) => deleteProject(projectId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
