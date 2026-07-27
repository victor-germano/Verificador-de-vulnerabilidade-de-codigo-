import axios from "axios";
import { Trash2, UserPlus } from "lucide-react";
import * as React from "react";
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
import { useAuth } from "@/features/auth/auth-context";
import {
  useAddCollaborator,
  useCollaborators,
  useRemoveCollaborator,
  useUpdateCollaboratorRole,
} from "@/features/collaborators/hooks";
import type { Collaborator, Project, ProjectRole } from "@/types/api";

const ROLE_LABEL: Record<ProjectRole, string> = {
  editor: "Editor",
  viewer: "Leitor",
};

function extractErrorMessage(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err)) {
    return err.response?.data?.detail ?? fallback;
  }
  return fallback;
}

function AddCollaboratorDialog({ projectId }: { projectId: string }) {
  const [open, setOpen] = React.useState(false);
  const [email, setEmail] = React.useState("");
  const [role, setRole] = React.useState<ProjectRole>("viewer");
  const [error, setError] = React.useState<string | null>(null);
  const addCollaborator = useAddCollaborator(projectId);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await addCollaborator.mutateAsync({ email, role });
      toast.success("Colaborador adicionado");
      setEmail("");
      setRole("viewer");
      setOpen(false);
    } catch (err) {
      setError(
        extractErrorMessage(err, "Não foi possível adicionar o colaborador."),
      );
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <UserPlus /> Adicionar colaborador
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Adicionar colaborador</DialogTitle>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="collaborator-email">E-mail</Label>
            <Input
              id="collaborator-email"
              type="email"
              placeholder="pessoa@empresa.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="collaborator-role">Papel</Label>
            <Select
              value={role}
              onValueChange={(value) => setRole(value as ProjectRole)}
            >
              <SelectTrigger id="collaborator-role">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="viewer">Leitor</SelectItem>
                <SelectItem value="editor">Editor</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {error && <p className="text-xs text-destructive">{error}</p>}
          <DialogFooter>
            <Button
              type="submit"
              disabled={addCollaborator.isPending || !email}
            >
              {addCollaborator.isPending ? "Adicionando…" : "Adicionar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function CollaboratorRow({
  projectId,
  collaborator,
}: {
  projectId: string;
  collaborator: Collaborator;
}) {
  const updateRole = useUpdateCollaboratorRole(projectId);
  const removeCollaborator = useRemoveCollaborator(projectId);

  const handleRoleChange = async (role: ProjectRole) => {
    try {
      await updateRole.mutateAsync({ userId: collaborator.user_id, role });
      toast.success("Papel atualizado");
    } catch (err) {
      toast.error(
        extractErrorMessage(err, "Não foi possível atualizar o papel."),
      );
    }
  };

  const handleRemove = async () => {
    try {
      await removeCollaborator.mutateAsync(collaborator.user_id);
      toast.success("Colaborador removido");
    } catch (err) {
      toast.error(
        extractErrorMessage(err, "Não foi possível remover o colaborador."),
      );
    }
  };

  return (
    <TableRow>
      <TableCell>
        <div className="flex flex-col">
          <span className="font-medium">{collaborator.full_name}</span>
          <span className="text-xs text-muted-foreground">
            {collaborator.email}
          </span>
        </div>
      </TableCell>
      <TableCell>
        <Select
          value={collaborator.role}
          onValueChange={(value) => handleRoleChange(value as ProjectRole)}
        >
          <SelectTrigger className="h-8 w-32" disabled={updateRole.isPending}>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="viewer">Leitor</SelectItem>
            <SelectItem value="editor">Editor</SelectItem>
          </SelectContent>
        </Select>
      </TableCell>
      <TableCell className="text-right">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleRemove}
          disabled={removeCollaborator.isPending}
          aria-label="Remover colaborador"
        >
          <Trash2 className="size-4 text-destructive" />
        </Button>
      </TableCell>
    </TableRow>
  );
}

export function CollaboratorsCard({ project }: { project: Project }) {
  const { user } = useAuth();
  const { data: collaborators, isLoading } = useCollaborators(project.id);
  const isOwner = user?.id === project.owner_id;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3 space-y-0">
        <CardTitle>Colaboradores</CardTitle>
        {isOwner && <AddCollaboratorDialog projectId={project.id} />}
      </CardHeader>
      <CardContent>
        {isLoading && <Skeleton className="h-20" />}
        {!isLoading && collaborators?.length === 0 && (
          <p className="py-4 text-sm text-muted-foreground">
            Nenhum colaborador além do proprietário. Adicione pessoas para dar
            acesso a este projeto.
          </p>
        )}
        {!isLoading && collaborators && collaborators.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Pessoa</TableHead>
                <TableHead>Papel</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {collaborators.map((collaborator) =>
                isOwner ? (
                  <CollaboratorRow
                    key={collaborator.user_id}
                    projectId={project.id}
                    collaborator={collaborator}
                  />
                ) : (
                  <TableRow key={collaborator.user_id}>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-medium">
                          {collaborator.full_name}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {collaborator.email}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {ROLE_LABEL[collaborator.role]}
                      </Badge>
                    </TableCell>
                    <TableCell />
                  </TableRow>
                ),
              )}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
