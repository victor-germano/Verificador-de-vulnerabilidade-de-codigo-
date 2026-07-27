import * as React from "react";
import { useSearchParams } from "react-router-dom";

import { SeverityBadge } from "@/components/severity-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useFindings } from "@/features/findings/hooks";
import { useProjects } from "@/features/projects/hooks";
import type { Finding, Language, Severity } from "@/types/api";

const SEVERITIES: Severity[] = ["critical", "high", "medium", "low", "info"];
const LANGUAGES: Language[] = [
  "python",
  "javascript",
  "typescript",
  "java",
  "php",
  "go",
  "rust",
  "csharp",
];

function FindingDetailDialog({ finding, onClose }: { finding: Finding | null; onClose: () => void }) {
  return (
    <Dialog open={Boolean(finding)} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
        {finding && (
          <>
            <DialogHeader>
              <div className="flex items-center gap-2">
                <SeverityBadge severity={finding.severity} />
                <DialogTitle>{finding.rule_name}</DialogTitle>
              </div>
              <DialogDescription>
                {finding.file_path}:{finding.line_start}
                {finding.line_end !== finding.line_start ? `-${finding.line_end}` : ""} · {finding.rule_id}
              </DialogDescription>
            </DialogHeader>

            <div className="flex flex-wrap gap-1.5 text-xs">
              {finding.owasp && <Badge variant="secondary">{finding.owasp}</Badge>}
              {finding.cwe && <Badge variant="secondary">{finding.cwe}</Badge>}
              {finding.cvss != null && <Badge variant="secondary">CVSS {finding.cvss}</Badge>}
              <Badge variant="secondary">Confiança: {finding.confidence}</Badge>
            </div>

            <pre className="overflow-x-auto rounded-md bg-muted p-3 text-xs">
              {finding.code_snippet}
            </pre>

            <Section title="Descrição" text={finding.description} />
            <Section title="Explicação técnica" text={finding.explanation} />
            <Section title="Impacto" text={finding.impact} />
            <Section title="Recomendação" text={finding.recommendation} />

            <div>
              <p className="mb-1 text-sm font-medium">Exemplo seguro</p>
              <pre className="overflow-x-auto rounded-md bg-muted p-3 text-xs">
                {finding.secure_example}
              </pre>
            </div>

            {finding.references.length > 0 && (
              <div>
                <p className="mb-1 text-sm font-medium">Referências</p>
                <ul className="list-inside list-disc text-xs text-primary">
                  {finding.references.map((ref) => (
                    <li key={ref}>
                      <a href={ref} target="_blank" rel="noreferrer" className="hover:underline">
                        {ref}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

function Section({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <p className="mb-1 text-sm font-medium">{title}</p>
      <p className="text-sm text-muted-foreground">{text}</p>
    </div>
  );
}

export default function FindingsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { data: projects } = useProjects();
  const [selectedFinding, setSelectedFinding] = React.useState<Finding | null>(null);

  const projectId = searchParams.get("project_id") ?? "";
  const severity = (searchParams.get("severity") as Severity | null) ?? undefined;
  const language = (searchParams.get("language") as Language | null) ?? undefined;
  const filePath = searchParams.get("file_path") ?? "";

  React.useEffect(() => {
    if (!projectId && projects && projects.length > 0) {
      const next = new URLSearchParams(searchParams);
      next.set("project_id", projects[0].id);
      setSearchParams(next, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projects, projectId]);

  const updateParam = (key: string, value: string | undefined) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next, { replace: true });
  };

  const { data: findings, isLoading } = useFindings({
    project_id: projectId,
    severity,
    language,
    file_path: filePath || undefined,
  });

  const PAGE_SIZE = 20;
  const [page, setPage] = React.useState(1);

  React.useEffect(() => {
    setPage(1);
  }, [projectId, severity, language, filePath]);

  const totalPages = findings ? Math.max(1, Math.ceil(findings.length / PAGE_SIZE)) : 1;
  const pageStart = (page - 1) * PAGE_SIZE;
  const paginatedFindings = findings?.slice(pageStart, pageStart + PAGE_SIZE) ?? [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Vulnerabilidades</h1>
        <p className="text-sm text-muted-foreground">Filtre por projeto, severidade, linguagem e arquivo</p>
      </div>

      <Card>
        <CardContent className="flex flex-wrap items-end gap-3 pt-5">
          <div className="flex min-w-48 flex-col gap-1.5">
            <label className="text-xs font-medium text-muted-foreground">Projeto</label>
            <Select value={projectId} onValueChange={(v) => updateParam("project_id", v)}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione um projeto" />
              </SelectTrigger>
              <SelectContent>
                {projects?.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex min-w-36 flex-col gap-1.5">
            <label className="text-xs font-medium text-muted-foreground">Severidade</label>
            <Select
              value={severity ?? "all"}
              onValueChange={(v) => updateParam("severity", v === "all" ? undefined : v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                {SEVERITIES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex min-w-36 flex-col gap-1.5">
            <label className="text-xs font-medium text-muted-foreground">Linguagem</label>
            <Select
              value={language ?? "all"}
              onValueChange={(v) => updateParam("language", v === "all" ? undefined : v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                {LANGUAGES.map((l) => (
                  <SelectItem key={l} value={l}>
                    {l}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex min-w-48 flex-1 flex-col gap-1.5">
            <label className="text-xs font-medium text-muted-foreground">Arquivo</label>
            <Input
              placeholder="filtrar por caminho…"
              defaultValue={filePath}
              onBlur={(e) => updateParam("file_path", e.target.value || undefined)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-5">
          {isLoading && <Skeleton className="h-64" />}
          {!isLoading && findings?.length === 0 && (
            <p className="py-12 text-center text-sm text-muted-foreground">
              Nenhuma vulnerabilidade encontrada com esses filtros.
            </p>
          )}
          {!isLoading && findings && findings.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Severidade</TableHead>
                  <TableHead>Regra</TableHead>
                  <TableHead>Arquivo</TableHead>
                  <TableHead>Linguagem</TableHead>
                  <TableHead>CWE</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedFindings.map((finding) => (
                  <TableRow
                    key={finding.id}
                    className="cursor-pointer"
                    onClick={() => setSelectedFinding(finding)}
                  >
                    <TableCell>
                      <SeverityBadge severity={finding.severity} />
                    </TableCell>
                    <TableCell className="font-medium">{finding.rule_name}</TableCell>
                    <TableCell className="max-w-64 truncate font-mono text-xs text-muted-foreground">
                      {finding.file_path}:{finding.line_start}
                    </TableCell>
                    <TableCell className="text-muted-foreground">{finding.language}</TableCell>
                    <TableCell className="text-muted-foreground">{finding.cwe ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!isLoading && findings && findings.length > PAGE_SIZE && (
            <div className="mt-4 flex items-center justify-between text-sm text-muted-foreground">
              <span>
                Mostrando {pageStart + 1}–{Math.min(pageStart + PAGE_SIZE, findings.length)} de{" "}
                {findings.length}
              </span>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  Anterior
                </Button>
                <span>
                  Página {page} de {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                >
                  Próxima
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <FindingDetailDialog finding={selectedFinding} onClose={() => setSelectedFinding(null)} />
    </div>
  );
}
