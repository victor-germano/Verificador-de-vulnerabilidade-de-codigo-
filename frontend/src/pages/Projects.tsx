import { zodResolver } from "@hookform/resolvers/zod";
import { FolderKanban, Plus } from "lucide-react";
import * as React from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";

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
import { useCreateProject, useProjects } from "@/features/projects/hooks";

const schema = z.object({
  name: z.string().min(1, "Informe o nome do projeto"),
  description: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

function CreateProjectDialog() {
  const [open, setOpen] = React.useState(false);
  const createProject = useCreateProject();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      await createProject.mutateAsync(values);
      toast.success(`Projeto "${values.name}" criado`);
      reset();
      setOpen(false);
    } catch {
      toast.error("Não foi possível criar o projeto.");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus /> Novo projeto
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Novo projeto</DialogTitle>
        </DialogHeader>
        <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="name">Nome</Label>
            <Input id="name" {...register("name")} />
            {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="description">Descrição (opcional)</Label>
            <Input id="description" {...register("description")} />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Criando…" : "Criar projeto"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function ProjectsPage() {
  const { data: projects, isLoading } = useProjects();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Projetos</h1>
          <p className="text-sm text-muted-foreground">Gerencie os projetos analisados</p>
        </div>
        <CreateProjectDialog />
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      )}

      {!isLoading && projects?.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-12 text-center">
            <FolderKanban className="size-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Nenhum projeto ainda. Crie o primeiro para começar a escanear código.
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects?.map((project) => (
          <Link key={project.id} to={`/projects/${project.id}`}>
            <Card className="h-full transition-colors hover:border-primary/50">
              <CardHeader>
                <CardTitle className="text-foreground">{project.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-2 text-sm text-muted-foreground">
                  {project.description || "Sem descrição"}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
