import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { SEVERITY_COLORS } from "@/lib/chart-colors";
import type { Severity } from "@/types/api";

interface SeverityPieChartProps {
  counts: Record<Severity, number>;
}

const ORDER: Severity[] = ["critical", "high", "medium", "low", "info"];
const LABELS: Record<Severity, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  info: "Info",
};

export function SeverityPieChart({ counts }: SeverityPieChartProps) {
  const data = ORDER.map((severity) => ({
    name: LABELS[severity],
    value: counts[severity] ?? 0,
    severity,
  })).filter((entry) => entry.value > 0);

  if (data.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center text-sm text-muted-foreground">
        Nenhuma vulnerabilidade encontrada
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={224}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={56} outerRadius={84} paddingAngle={2}>
          {data.map((entry) => (
            <Cell key={entry.severity} fill={SEVERITY_COLORS[entry.severity]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: "var(--popover)",
            border: "1px solid var(--border)",
            borderRadius: "0.5rem",
            fontSize: "0.75rem",
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
