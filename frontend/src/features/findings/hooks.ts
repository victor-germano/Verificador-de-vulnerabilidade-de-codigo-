import { useQuery } from "@tanstack/react-query";

import { listFindings } from "@/features/findings/api";
import type { FindingFilters } from "@/types/api";

export function useFindings(filters: FindingFilters) {
  return useQuery({
    queryKey: ["findings", filters],
    queryFn: () => listFindings(filters),
    enabled: Boolean(filters.project_id),
  });
}
