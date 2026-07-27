import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getScan, listProjectScans, scanGitRepository, uploadAndScan } from "@/features/scans/api";

export function useProjectScans(projectId: string | undefined) {
  return useQuery({
    queryKey: ["scans", "project", projectId],
    queryFn: () => listProjectScans(projectId as string),
    enabled: Boolean(projectId),
  });
}

export function useScan(scanId: string | undefined) {
  return useQuery({
    queryKey: ["scans", scanId],
    queryFn: () => getScan(scanId as string),
    enabled: Boolean(scanId),
  });
}

export function useUploadAndScan(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => uploadAndScan(projectId, file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["scans", "project", projectId] });
      void queryClient.invalidateQueries({ queryKey: ["findings"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useScanGitRepository(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (repositoryUrl: string) => scanGitRepository(projectId, repositoryUrl),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["scans", "project", projectId] });
      void queryClient.invalidateQueries({ queryKey: ["findings"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
