import { FileWarning, FolderKanban, ShieldCheck, Activity } from "lucide-react";

import { SeverityPieChart } from "@/components/charts/severity-pie-chart";
import { TopItemsBarChart } from "@/components/charts/top-items-bar-chart";
import { TrendLineChart } from "@/components/charts/trend-line-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useDashboardSummary,
  useDashboardTrend,
  useTopFiles,
  useTopVulnerabilities,
} from "@/features/dashboard/hooks";

function StatCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: React.ReactNode;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card>
      <CardContent className="flex items-center justify-between pt-5">
        <div>
          <p className="text-xs font-medium text-muted-foreground">{label}</p>
          <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
        </div>
        <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Icon className="size-4.5" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { data: summary, isLoading: summaryLoading } = useDashboardSummary();
  const { data: trend } = useDashboardTrend(30);
  const { data: topVulns } = useTopVulnerabilities(5);
  const { data: topFiles } = useTopFiles(5);

  if (summaryLoading || !summary) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Visão geral da segurança dos seus projetos</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Projetos" value={summary.total_projects} icon={FolderKanban} />
        <StatCard label="Scans realizados" value={summary.total_scans} icon={Activity} />
        <StatCard
          label="Security Score médio"
          value={summary.average_security_score ?? "—"}
          icon={ShieldCheck}
        />
        <StatCard label="Vulnerabilidades" value={summary.total_findings} icon={FileWarning} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Distribuição por severidade</CardTitle>
          </CardHeader>
          <CardContent>
            <SeverityPieChart
              counts={{
                critical: summary.critical_count,
                high: summary.high_count,
                medium: summary.medium_count,
                low: summary.low_count,
                info: summary.info_count,
              }}
            />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Tendência (últimos 30 dias)</CardTitle>
          </CardHeader>
          <CardContent>
            <TrendLineChart data={trend ?? []} />
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top vulnerabilidades</CardTitle>
          </CardHeader>
          <CardContent>
            <TopItemsBarChart items={topVulns ?? []} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top arquivos afetados</CardTitle>
          </CardHeader>
          <CardContent>
            <TopItemsBarChart items={topFiles ?? []} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
