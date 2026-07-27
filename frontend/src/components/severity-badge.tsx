import { Badge } from "@/components/ui/badge";
import type { Severity } from "@/types/api";

const LABELS: Record<Severity, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  info: "Info",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return <Badge variant={severity}>{LABELS[severity]}</Badge>;
}
