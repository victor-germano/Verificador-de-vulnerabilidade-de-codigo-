import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { SEVERITY_COLORS } from "@/lib/chart-colors";
import type { SeverityTrendPoint } from "@/types/api";

export function TrendLineChart({ data }: { data: SeverityTrendPoint[] }) {
  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
        Sem histórico suficiente ainda
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={256}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
        <YAxis tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: "var(--popover)",
            border: "1px solid var(--border)",
            borderRadius: "0.5rem",
            fontSize: "0.75rem",
          }}
        />
        <Legend wrapperStyle={{ fontSize: "0.75rem" }} />
        <Line type="monotone" dataKey="critical" stroke={SEVERITY_COLORS.critical} strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="high" stroke={SEVERITY_COLORS.high} strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="medium" stroke={SEVERITY_COLORS.medium} strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="low" stroke={SEVERITY_COLORS.low} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
