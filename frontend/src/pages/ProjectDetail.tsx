import axios from "axios";
import { Download, GitBranch, ShieldAlert, Upload } from "lucide-react";
import * as React from "react";
import { Link, useParams } from "react-router-dom";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAuth } from "@/features/auth/auth-context";
import { CollaboratorsCard } from "@/features/collaborators/CollaboratorsCard";
import { useCollaborators } from "@/features/collaborators/hooks";
import { reportDownloadUrl } from "@/features/scans/api";
import {
  useProjectScans,
  useScanGitRepository,
  useUploadAndScan,
} from "@/features/scans/hooks";
import { useProject } from "@/features/projects/hooks";
import { cn } from "@/lib/utils";
import type { Scan, ScanStatus } from "@/types/api";

const STATUS_LABEL: Record<ScanStatus, string> = {
  pending: "Pendente",
  running: "Em execução",
  completed: "Concluído",
  failed: "Falhou",
};

const STATUS_CLASS: Record<ScanStatus, string> = {
  pending: "bg-muted text-muted-foreground",
  running: "bg-severity-low/15 text-severity-low",
  completed: "bg-severity-low/15 text-emerald-600 dark:text-emerald-400",
  failed: "bg-severity-critical/15 text-severity-critical",
};

function notifyScanResult(scan: Scan) {
  if (scan.status === "failed") {
    toast.error("O scan falhou", {
      description: scan.error_message ?? undefined,
    });
    return;
  }
  toast.success("Scan concluído", {
    description: `${scan.files_scanned} arquivo(s) analisado(s) · Security Score ${scan.security_score ?? "—"}/100`,
  });
}

function GitScanDialog({ projectId }: { projectId: string }) {
  const [open, setOpen] = React.useState(false);
  const [url, setUrl] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const scanGitRepository = useScanGitRepository(projectId);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      const scan = await scanGitRepository.mutateAsync(url);
      notifyScanResult(scan);
      setUrl("");
      setOpen(false);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(
          err.response?.data?.detail ??
            "Não foi possível clonar o repositório.",
        );
      } else {
        setError("Não foi possível clonar o repositório.");
      }
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <GitBranch /> Repositório Git
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Escanear repositório Git</DialogTitle>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="repository-url">
              URL do repositório (público, http/https)
            </Label>
            <Input
              id="repository-url"
              placeholder="https://github.com/org/repo.git"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-xs text-destructive">{error}</p>}
          <DialogFooter>
            <Button
              type="submit"
              disabled={scanGitRepository.isPending || !url}
            >
              {scanGitRepository.isPending
                ? "Clonando e analisando…"
                : "Escanear"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const { user } = useAuth();

  const { data: project } = useProject(projectId);
  const { data: scans, isLoading } = useProjectScans(projectId);
  const { data: collaborators } = useCollaborators(projectId);
  const uploadAndScan = useUploadAndScan(projectId ?? "");

  const isOwner = Boolean(project && user && project.owner_id === user.id);
  const myRole = collaborators?.find((c) => c.user_id === user?.id)?.role;
  const canEdit = isOwner || myRole === "editor";

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    try {
      const scan = await uploadAndScan.mutateAsync(file);
      notifyScanResult(scan);
    } catch {
      toast.error("Não foi possível enviar o arquivo para análise.");
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">
            {project?.name ?? "Projeto"}
          </h1>
          <p className="text-sm text-muted-foreground">
            {project?.description ||
              "Envie um arquivo, pasta (.zip) ou repositório Git para analisar"}
          </p>
        </div>
        {canEdit && (
          <div className="flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".py,.js,.ts,.jsx,.tsx,.java,.php,.go,.rs,.cs,.cpp,.c,.zip"
              onChange={handleFileChange}
            />
            {projectId && <GitScanDialog projectId={projectId} />}
            <Button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadAndScan.isPending}
            >
              <Upload /> {uploadAndScan.isPending ? "Analisando…" : "Novo scan"}
            </Button>
          </div>
        )}
      </div>

      {projectId && (
        <Link
          to={`/findings?project_id=${projectId}`}
          className="inline-flex w-fit items-center gap-1.5 text-sm font-medium text-primary hover:underline"
        >
          <ShieldAlert className="size-4" /> Ver todas as vulnerabilidades deste
          projeto
        </Link>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Histórico de scans</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <Skeleton className="h-32" />}
          {!isLoading && scans?.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Nenhum scan realizado ainda.
            </p>
          )}
          {!isLoading && scans && scans.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Alvo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Arquivos</TableHead>
                  <TableHead>Security Score</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead className="text-right">Relatório</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {scans.map((scan) => (
                  <TableRow key={scan.id}>
                    <TableCell className="max-w-56 truncate font-mono text-xs">
                      {scan.target_reference}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={cn(
                          "border-transparent",
                          STATUS_CLASS[scan.status],
                        )}
                      >
                        {STATUS_LABEL[scan.status]}
                      </Badge>
                      {scan.status === "failed" && scan.error_message && (
                        <p className="mt-1 max-w-56 truncate text-xs text-severity-critical">
                          {scan.error_message}
                        </p>
                      )}
                    </TableCell>
                    <TableCell>{scan.files_scanned}</TableCell>
                    <TableCell>{scan.security_score ?? "—"}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(scan.created_at).toLocaleString("pt-BR")}
                    </TableCell>
                    <TableCell className="text-right">
                      {scan.status === "completed" && (
                        <a
                          href={reportDownloadUrl(scan.id, "json")}
                          className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
                        >
                          <Download className="size-3.5" /> JSON
                        </a>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {project && <CollaboratorsCard project={project} />}
    </div>
  );
}
