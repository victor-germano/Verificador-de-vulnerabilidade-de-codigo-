import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { TopItem } from "@/types/api";

export function TopItemsBarChart({ items }: { items: TopItem[] }) {
  if (items.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center text-sm text-muted-foreground">
        Sem dados ainda
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={224}>
      <BarChart data={items} layout="vertical" margin={{ top: 4, right: 16, left: 4, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" allowDecimals={false} />
        <YAxis
          type="category"
          dataKey="label"
          width={140}
          tick={{ fontSize: 11 }}
          stroke="var(--muted-foreground)"
        />
        <Tooltip
          contentStyle={{
            background: "var(--popover)",
            border: "1px solid var(--border)",
            borderRadius: "0.5rem",
            fontSize: "0.75rem",
          }}
        />
        <Bar dataKey="count" fill="var(--primary)" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
